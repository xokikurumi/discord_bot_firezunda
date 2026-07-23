import re
import unicodedata

import discord

from repositories.base.reaction_keywords_repo import ReactionKeyworkdsRepository


class MessageReactionService:
	"""Manage keyword-based reaction rules and apply them to new messages."""

	SYUKKA_REACTION = "<:syukka:1026820219039133696>"
	SYUKKA_PRESET_RULES = [
		("なの", SYUKKA_REACTION, False),
		("<:nano:1017766944180551690>", SYUKKA_REACTION, False),
		("なのだ", SYUKKA_REACTION, True),
		("なのです", SYUKKA_REACTION, True),
	]

	def __init__(self, session_factory, bot=None):
		"""Store database session factory and optional bot reference for emoji lookup."""
		self.session_factory = session_factory
		self.bot = bot
		print("MessageReactionService initialized.")

	def normalize_text(self, text: str) -> str:
		"""Normalize text so keyword matching is more tolerant of common variants."""
		# Normalize user input and keywords before substring matching.
		if text is None:
			return ""

		text = unicodedata.normalize("NFKC", text)
		text = "".join(
			chr(ord(c) - 0x60) if "\u30a1" <= c <= "\u30f3" else c
			for c in text
		)
		text = text.replace("\u30fc", "")
		text = re.sub(r"(.)\1+", r"\1", text)
		return text.casefold()

	def parse_bool(self, value) -> bool:
		"""Parse command input into a boolean flag."""
		# Accept short truthy words for command arguments such as "ng" or "yes".
		if isinstance(value, bool):
			return value
		return str(value).lower() in ("1", "true", "yes", "y", "on", "ng")

	def parse_reaction(self, reaction: str):
		"""Parse a Unicode emoji or custom emoji mention into database fields."""
		# Store custom emoji as name/id/animated so it can be reconstructed later.
		custom_emoji = re.fullmatch(r"<(a?):([A-Za-z0-9_]+):([0-9]+)>", reaction)
		if not custom_emoji:
			return {
				"reaction": reaction,
				"reaction_id": None,
				"reaction_animation_flg": False,
			}

		return {
			"reaction": custom_emoji.group(2),
			"reaction_id": int(custom_emoji.group(3)),
			"reaction_animation_flg": custom_emoji.group(1) == "a",
		}

	def parse_emoji_id(self, emoji: str):
		"""Extract a custom emoji id from a mention or raw numeric id."""
		custom_emoji = re.fullmatch(r"<a?:[A-Za-z0-9_]+:([0-9]+)>", emoji)
		if custom_emoji:
			return int(custom_emoji.group(1))

		if str(emoji).isdigit():
			return int(emoji)

		return None

	def check_emoji_status(self, channel, emoji: str):
		"""Return bot visibility and channel permission details for a custom emoji."""
		# This backs the diagnostic command for external custom emoji issues.
		emoji_id = self.parse_emoji_id(emoji)
		permissions = channel.permissions_for(channel.guild.me)
		status = {
			"emoji_id": emoji_id,
			"add_reactions": permissions.add_reactions,
			"use_external_emojis": getattr(permissions, "use_external_emojis", True),
			"visible": False,
			"emoji": None,
		}

		if emoji_id and self.bot:
			found = self.bot.get_emoji(emoji_id)
			status["visible"] = found is not None
			status["emoji"] = found

		return status

	def format_custom_emoji(self, keyword):
		"""Rebuild a custom emoji mention from a stored reaction keyword row."""
		prefix = "a" if keyword.reaction_animation_flg else ""
		return f"<{prefix}:{keyword.reaction}:{keyword.reaction_id}>"

	async def add_keyword(self, guild_id: int, keyword: str, reaction: str, ng_word: bool = False):
		"""Register a reaction or NG keyword rule for one guild."""
		reaction_data = self.parse_reaction(reaction)
		async with self.session_factory() as session:
			repo = ReactionKeyworkdsRepository(session)
			await repo.insert({
				"guild_id": guild_id,
				"enabled": True,
				"keyword": keyword,
				"reaction": reaction_data["reaction"],
				"reaction_id": reaction_data["reaction_id"],
				"reaction_animation_flg": reaction_data["reaction_animation_flg"],
				"ng_word_flg": ng_word,
				"delete_flg": False,
			})

	async def add_syukka_preset(self, guild_id: int):
		"""Register the legacy syukka reaction rules for one guild."""
		added = []
		skipped = []
		async with self.session_factory() as session:
			repo = ReactionKeyworkdsRepository(session)
			current_keywords = await repo.list_by_guild(guild_id)
			existing = {
				(self.normalize_text(row.keyword), bool(row.ng_word_flg))
				for row in current_keywords
			}

			for keyword, reaction, ng_word in self.SYUKKA_PRESET_RULES:
				key = (self.normalize_text(keyword), ng_word)
				if key in existing:
					skipped.append(keyword)
					continue

				reaction_data = self.parse_reaction(reaction)
				await repo.insert({
					"guild_id": guild_id,
					"enabled": True,
					"keyword": keyword,
					"reaction": reaction_data["reaction"],
					"reaction_id": reaction_data["reaction_id"],
					"reaction_animation_flg": reaction_data["reaction_animation_flg"],
					"ng_word_flg": ng_word,
					"delete_flg": False,
				})
				existing.add(key)
				added.append(keyword)

		return {
			"added": added,
			"skipped": skipped,
			"reaction": self.SYUKKA_REACTION,
		}

	async def remove_keyword(self, guild_id: int, keyword: str):
		"""Soft-delete matching keyword rules for one guild."""
		async with self.session_factory() as session:
			repo = ReactionKeyworkdsRepository(session)
			return await repo.soft_delete(guild_id, keyword)

	async def list_keywords(self, guild_id: int):
		"""List non-deleted reaction keyword rules for one guild."""
		async with self.session_factory() as session:
			repo = ReactionKeyworkdsRepository(session)
			return await repo.list_by_guild(guild_id)

	async def add_registered_reaction(self, message, keyword):
		"""Add the configured reaction for a matched keyword to a message."""
		# Prefer cached emoji objects, then fall back to Discord's external emoji string.
		if not keyword.reaction_id:
			await message.add_reaction(keyword.reaction)
			return

		permissions = message.channel.permissions_for(message.guild.me)
		if not permissions.add_reactions:
			print(f"[ERROR] add_reaction keyword_id={keyword.id}: missing Add Reactions permission")
			return

		if not getattr(permissions, "use_external_emojis", True):
			print(f"[ERROR] add_reaction keyword_id={keyword.id}: missing Use External Emojis permission")
			return

		emoji = self.bot.get_emoji(int(keyword.reaction_id)) if self.bot else None
		if emoji is not None:
			await message.add_reaction(emoji)
			return

		try:
			await message.add_reaction(self.format_custom_emoji(keyword))
		except discord.HTTPException as e:
			if getattr(e, "code", None) == 10014:
				print(
					f"[ERROR] add_reaction keyword_id={keyword.id}: unknown emoji. "
					"Check that the bot can access the emoji source server and has Use External Emojis permission. "
					f"emoji={self.format_custom_emoji(keyword)} original={e}"
				)
				return
			raise

	async def reaction(self, message):
		"""Apply keyword rules to a new Discord message."""
		# NG keywords suppress all reactions; normal keywords add their configured reactions.
		content = self.normalize_text(message.content)
		if not content:
			return

		async with self.session_factory() as session:
			repo = ReactionKeyworkdsRepository(session)
			try:
				ng_keywords = await repo.getReactions(message.guild.id, True)
				ok_keywords = await repo.getReactions(message.guild.id, False)

				for keyword in ng_keywords:
					if self.normalize_text(keyword.keyword) in content:
						return

				for keyword in ok_keywords:
					if self.normalize_text(keyword.keyword) not in content:
						continue

					try:
						await self.add_registered_reaction(message, keyword)
					except Exception as e:
						print(f"[ERROR] add_reaction keyword_id={keyword.id}: {e}")
			except Exception as e:
				print(f"[ERROR] reaction: {e}")
