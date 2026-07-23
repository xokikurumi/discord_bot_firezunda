from discord.ext import commands


class MessageCog(commands.Cog):
	"""Discord Cog for message create, edit, delete, and backfill logging."""

	def __init__(self, bot, message_service):
		"""Keep references to the bot and message log service."""
		self.bot = bot
		self.service = message_service
		print("MessageCog initialized.")

	@commands.hybrid_command(name="backfill_message_logs")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def backfill_message_logs(self, ctx, limit: int = 0):
		"""Import historical messages from all text channels in the current guild."""
		# Admin-only command to import historical messages without duplicating existing rows.
		history_limit = None if limit <= 0 else limit
		inserted_count = 0
		skipped_count = 0
		scanned_count = 0
		failed_channels = []

		await ctx.send("message log backfill started.")

		for channel in ctx.guild.text_channels:
			permissions = channel.permissions_for(ctx.guild.me)
			if not permissions.view_channel or not permissions.read_message_history:
				failed_channels.append(f"{channel.name}: missing permission")
				continue

			try:
				async for message in channel.history(limit=history_limit, oldest_first=True):
					scanned_count += 1
					inserted = await self.service.log_history_message(message)
					if inserted:
						inserted_count += 1
					else:
						skipped_count += 1

					if scanned_count % 500 == 0:
						await ctx.send(
							f"backfill progress: scanned={scanned_count}, "
							f"inserted={inserted_count}, skipped={skipped_count}"
						)
			except Exception as e:
				failed_channels.append(f"{channel.name}: {e}")

		summary = (
			"message log backfill complete.\n"
			f"scanned={scanned_count}, inserted={inserted_count}, skipped={skipped_count}, "
			f"failed_channels={len(failed_channels)}"
		)
		if failed_channels:
			summary += "\n" + "\n".join(failed_channels[:10])
			if len(failed_channels) > 10:
				summary += f"\n... and {len(failed_channels) - 10} more"

		await ctx.send(summary)

	@backfill_message_logs.error
	async def backfill_message_logs_error(self, ctx, error):
		"""Handle errors raised by the message backfill command."""
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("administrator permission is required.")
			return
		if isinstance(error, commands.NoPrivateMessage):
			await ctx.send("this command can only be used in a server.")
			return
		await ctx.send(f"backfill failed: {error}")

	@commands.Cog.listener()
	async def on_message(self, message):
		"""Persist newly created guild messages."""
		if not message.guild:
			return

		try:
			await self.service.log_create(message)
		except Exception as e:
			print(f"[ERROR] on_message: {e}")

	@commands.Cog.listener()
	async def on_message_edit(self, before, after):
		"""Persist edits for messages that are available in the local cache."""
		if not before.guild:
			return

		try:
			await self.service.log_edit(before, after)
		except Exception as e:
			print(f"[ERROR] on_message_edit: {e}")

	@commands.Cog.listener()
	async def on_raw_message_edit(self, payload):
		"""Persist edits for uncached messages using the current fetched body."""
		# If discord.py has the message cached, on_message_edit already records it.
		if getattr(payload, "cached_message", None) is not None:
			return

		channel = self.bot.get_channel(payload.channel_id)
		if channel is None:
			return

		message = await channel.fetch_message(payload.message_id)

		try:
			await self.service.log_raw_edit(message)
		except Exception as e:
			print(f"[ERROR] on_raw_message_edit: {e}")

	@commands.Cog.listener()
	async def on_message_delete(self, message):
		"""Persist deletes for messages that are available in the local cache."""
		if not message.guild:
			return

		try:
			await self.service.log_delete(message)
		except Exception as e:
			print(f"[ERROR] on_message_delete: {e}")

	@commands.Cog.listener()
	async def on_raw_message_delete(self, payload):
		"""Persist delete events for uncached messages using ids from the payload."""
		# Cached deletes are handled by on_message_delete with full message details.
		if payload.cached_message is not None:
			return

		if payload.guild_id is None:
			return

		try:
			await self.service.log_raw_delete(payload)
		except Exception as e:
			print(f"[ERROR] on_raw_message_delete: {e}")
