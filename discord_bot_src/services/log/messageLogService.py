import json
import os
from pathlib import Path
from repositories.base.discord_channel_repo import DiscordChannelRepository
from repositories.base.discord_user_repo import DiscordUserRepository
from repositories.log.message_log_repo import MessageLogRepository
from repositories.log.message_edit_log_repo import MessageEditLogRepository
from repositories.log.message_delete_log_repo import MessageDeleteLogRepository

BASE_PATH = Path(os.getenv("MESSAGE_FILE_BASE_PATH", "files"))

class MessageLogService:
	"""Persist message lifecycle events and historical message imports."""

	def __init__(self, session_factory):
		"""Store the database session factory used by each log operation."""
		self.session_factory = session_factory

	async def log_create(self, message):
		"""Persist a newly created message and save its attachments locally."""
		# Realtime message logging also stores attachments under guild/channel/message.
		async with self.session_factory() as session:
			row = 0
			filedir = BASE_PATH / str(message.guild.id) / str(message.channel.id) / str(message.id)

			filedir.mkdir(parents=True, exist_ok=True)
			for i, attachment in enumerate(message.attachments):
				ext = Path(attachment.filename).suffix
				file_path = filedir / f"{i}{ext}"
				await attachment.save(file_path)
			await self.upsert_message_master_rows(session, message)
			repo = MessageLogRepository(session)
			await repo.insert({
				"message_id": message.id,
				"guild_id": message.guild.id,
				"channel_id": message.channel.id,
				"user_id": message.author.id,
				"content": message.content,
				"message_created_at": message.created_at,
				"bot_flg": message.author.bot,
				"has_attachments": 1 if len(message.attachments) > 0 else 0,
				"has_embeds": 1 if len(message.embeds) > 0 else 0,
				"has_stickers": len(getattr(message, "stickers", [])) > 0,
				"stickers": self.serialize_stickers(getattr(message, "stickers", [])),
			})

	async def log_history_message(self, message):
		"""Persist a historical message while ignoring duplicates."""
		# Backfill uses INSERT IGNORE so already logged messages do not stop the import.
		async with self.session_factory() as session:
			await self.upsert_message_master_rows(session, message)
			repo = MessageLogRepository(session)
			return await repo.insert_ignore({
				"message_id": message.id,
				"guild_id": message.guild.id,
				"channel_id": message.channel.id,
				"user_id": message.author.id,
				"content": message.content,
				"message_created_at": message.created_at,
				"bot_flg": message.author.bot,
				"has_attachments": len(message.attachments) > 0,
				"has_embeds": len(message.embeds) > 0,
				"has_stickers": len(getattr(message, "stickers", [])) > 0,
				"stickers": self.serialize_stickers(getattr(message, "stickers", [])),
			})

	async def upsert_message_master_rows(self, session, message):
		"""Store the latest observed user and channel attributes for a message."""
		user_repo = DiscordUserRepository(session)
		channel_repo = DiscordChannelRepository(session)
		await user_repo.upsert(self.build_user_data(message))
		await channel_repo.upsert(self.build_channel_data(message))

	def build_user_data(self, message):
		"""Build user master data from a Discord message author."""
		author = message.author
		avatar = getattr(author, "display_avatar", None) or getattr(author, "avatar", None)
		return {
			"guild_id": message.guild.id,
			"user_id": author.id,
			"name": getattr(author, "name", None),
			"display_name": getattr(author, "display_name", None),
			"global_name": getattr(author, "global_name", None),
			"discriminator": getattr(author, "discriminator", None),
			"bot_flg": bool(getattr(author, "bot", False)),
			"avatar_url": str(avatar.url) if avatar else None,
			"last_seen_at": message.created_at,
		}

	def build_channel_data(self, message):
		"""Build channel master data from a Discord message channel."""
		channel = message.channel
		parent = getattr(channel, "parent", None)
		return {
			"guild_id": message.guild.id,
			"channel_id": channel.id,
			"name": getattr(channel, "name", None),
			"channel_type": str(getattr(channel, "type", "")) or None,
			"category_id": getattr(channel, "category_id", None),
			"parent_channel_id": getattr(parent, "id", None),
			"position": getattr(channel, "position", None),
			"last_seen_at": message.created_at,
		}

	def serialize_stickers(self, stickers):
		"""Serialize Discord sticker items for storage in message_log."""
		if not stickers:
			return None

		rows = []
		for sticker in stickers:
			rows.append({
				"id": getattr(sticker, "id", None),
				"name": getattr(sticker, "name", None),
				"format": str(getattr(sticker, "format", "")) or None,
				"url": getattr(sticker, "url", None),
			})
		return json.dumps(rows, ensure_ascii=False)

	async def log_edit(self, before, after):
		"""Persist an edit event with cached before and after message bodies."""
		# Cached edit events contain both before and after message bodies.
		async with self.session_factory() as session:
			repo = MessageEditLogRepository(session)
			await repo.insert({
				"message_id": before.id,
				"guild_id": before.guild.id,
				"channel_id": before.channel.id,
				"user_id": before.author.id,
				"before_content": before.content,
				"after_content": after.content
			})

	async def log_raw_edit(self, message):
		"""Persist an uncached edit event using stored logs for the previous body."""
		# Raw edit events lack the old body, so recover it from our latest stored log.
		async with self.session_factory() as session:
			message_repo = MessageLogRepository(session)
			edit_repo = MessageEditLogRepository(session)

			edit_logs = await edit_repo.get_by_message_id(message.id)
			if edit_logs:
				before_content = edit_logs[0].after_content
			else:
				message_log = await message_repo.get_by_message_id(message.id)
				before_content = message_log.content if message_log else None

			await edit_repo.insert({
				"message_id": message.id,
				"guild_id": message.guild.id,
				"channel_id": message.channel.id,
				"user_id": message.author.id,
				"before_content": before_content,
				"after_content": message.content
			})

	async def log_delete(self, message):
		"""Persist a cached delete event with available message details."""
		# Cached delete events still contain message details, so preserve them here.
		async with self.session_factory() as session:
			repo = MessageDeleteLogRepository(session)
			await repo.insert({
				"message_id": message.id,
				"guild_id": message.guild.id if message.guild else None,
				"channel_id": message.channel.id,
				"user_id": message.author.id,
				"content": message.content,
				"bot_flg": message.author.bot,
				"has_attachments": len(message.attachments) > 0,
				"has_embeds": len(message.embeds) > 0
			})

	async def log_raw_delete(self, payload):
		"""Persist an uncached delete event using only raw payload identifiers."""
		# Raw delete for uncached messages only provides ids; content is unavailable.
		async with self.session_factory() as session:
			repo = MessageDeleteLogRepository(session)
			await repo.insert({
				"message_id": payload.message_id,
				"guild_id": payload.guild_id,
				"channel_id": payload.channel_id,
				"user_id": None,
				"content": None,
				"bot_flg": None,
				"has_attachments": None,
				"has_embeds": None
			})
