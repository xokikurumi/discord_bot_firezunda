import asyncio

import discord
from discord.ext import commands

import constants


class P2PQuakeCog(commands.Cog):
	"""Discord Cog that runs the P2PQuake WebSocket watcher."""

	def __init__(self, bot, p2pquake_service):
		"""Keep references and task state for the watcher."""
		self.bot = bot
		self.service = p2pquake_service
		self.task = None
		self.restart_task = None
		self.unloading = False
		print("P2PQuakeCog initialized.")

	async def cog_load(self):
		"""Start the background WebSocket watcher when the Cog is loaded."""
		self.unloading = False
		self.start_watcher()

	async def cog_unload(self):
		"""Cancel the background WebSocket watcher when the Cog is unloaded."""
		self.unloading = True
		if self.restart_task:
			self.restart_task.cancel()
		if self.task:
			self.task.cancel()

	def start_watcher(self):
		"""Start the watcher task when it is not already running."""
		if self.task is not None and not self.task.done():
			return
		self.task = asyncio.create_task(self.service.run_forever())
		self.task.add_done_callback(self.handle_watcher_done)

	def handle_watcher_done(self, task):
		"""Restart the watcher if its task stops unexpectedly."""
		if self.unloading or self.bot.is_closed() or task.cancelled():
			return

		try:
			exception = task.exception()
		except asyncio.CancelledError:
			return

		if exception:
			print(f"[ERROR] P2PQuake watcher task stopped: {exception}")
		else:
			print("[WARN] P2PQuake watcher task stopped unexpectedly.")

		if self.restart_task is None or self.restart_task.done():
			self.restart_task = asyncio.create_task(self.restart_watcher())

	async def restart_watcher(self):
		"""Restart the watcher task after a short delay."""
		await asyncio.sleep(self.service.reconnect_delay)
		if self.unloading or self.bot.is_closed():
			return
		print("Restarting P2PQuake watcher task.")
		self.start_watcher()

	@commands.hybrid_group(name="notify_config", invoke_without_command=True, fallback="help")
	@commands.guild_only()
	async def notify_config(self, ctx):
		"""Show usage for notification setting commands."""
		await ctx.send(
			"usage: !notify_config add [#channel] [mention] [category] | "
			"!notify_config list | !notify_config category list | "
			"!notify_config enable <id> | !notify_config disable <id>"
		)

	@notify_config.group(name="category", invoke_without_command=True, fallback="help")
	@commands.guild_only()
	async def notify_config_category(self, ctx):
		"""Show usage for notification category commands."""
		await ctx.send("usage: !notify_config category list")

	@notify_config_category.command(name="list")
	@commands.guild_only()
	async def notify_config_category_list(self, ctx):
		"""List available notification categories."""
		lines = ["notify config categories:"]
		for category, description in constants.NOTIFY_CONFIG_CATEGORIES:
			lines.append(f"- {category}: {description}")
		await ctx.send("\n".join(lines))

	@notify_config.command(name="add")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def notify_config_add(
		self,
		ctx,
		channel: str = "",
		mention: str = "",
		category: str = constants.CONFIG_MENTION_QUAKE,
	):
		"""Register a notification channel setting for the current guild."""
		target_channel, mention, category = self.parse_notify_config_add_args(
			ctx,
			channel,
			mention,
			category,
		)

		await self.service.add_notify_config(
			ctx.guild.id,
			category,
			target_channel.id,
			mention,
		)

		await ctx.send(
			f"notify config added: category={category}, "
			f"channel={target_channel.mention}, mention={mention or '-'}"
		)

	def parse_notify_config_add_args(self, ctx, channel_text: str = "", mention: str = "", category: str = ""):
		"""Parse notify_config add arguments for both prefix and slash command usage."""
		category_values = {name for name, _description in constants.NOTIFY_CONFIG_CATEGORIES}
		tokens = [str(value or "").strip() for value in (channel_text, mention, category) if str(value or "").strip()]
		target_channel = ctx.channel
		mention_text = ""
		category_text = constants.CONFIG_MENTION_QUAKE

		if tokens:
			channel_candidate = self.resolve_text_channel(ctx, tokens[0])
			if channel_candidate:
				target_channel = channel_candidate
				tokens = tokens[1:]

		for token in tokens:
			normalized = token.upper()
			if normalized in category_values:
				category_text = normalized
			elif token.lower() not in ("none", "\u306a\u3057", "no"):
				mention_text = token

		return target_channel, mention_text, category_text

	def resolve_text_channel(self, ctx, text: str):
		"""Resolve a text channel from a mention, id, name, or converter result."""
		if isinstance(text, discord.TextChannel):
			return text
		value = str(text or "").strip()
		if not value:
			return None

		channel_id = None
		if value.startswith("<#") and value.endswith(">"):
			channel_id_text = value[2:-1]
			if channel_id_text.isdecimal():
				channel_id = int(channel_id_text)
		elif value.isdecimal():
			channel_id = int(value)

		if channel_id:
			channel = ctx.guild.get_channel(channel_id)
			if isinstance(channel, discord.TextChannel):
				return channel

		value = value.lstrip("#")
		return discord.utils.get(ctx.guild.text_channels, name=value)

	@notify_config.command(name="list")
	@commands.guild_only()
	async def notify_config_list(self, ctx):
		"""List notification channel settings for the current guild."""
		rows = await self.service.list_notify_configs(ctx.guild.id)
		if not rows:
			await ctx.send("notify configs are not registered.")
			return

		lines = ["notify configs:"]
		for row in rows:
			channel = self.bot.get_channel(row.channel_id)
			channel_text = channel.mention if channel else str(row.channel_id)
			lines.append(
				f"{row.id}: category={row.category}, channel={channel_text}, "
				f"mention={row.mention or '-'}, enabled={bool(row.enabled)}"
			)

		message = ""
		for line in lines:
			if len(message) + len(line) + 1 > 1900:
				await ctx.send(message)
				message = ""
			message += line + "\n"

		if message:
			await ctx.send(message)

	@notify_config.command(name="enable")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def notify_config_enable(self, ctx, config_id: int):
		"""Enable one notification channel setting."""
		updated_count = await self.service.set_notify_config_enabled(ctx.guild.id, config_id, True)
		if updated_count == 0:
			await ctx.send(f"notify config not found: id={config_id}")
			return
		await ctx.send(f"notify config enabled: id={config_id}")

	@notify_config.command(name="disable")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def notify_config_disable(self, ctx, config_id: int):
		"""Disable one notification channel setting."""
		updated_count = await self.service.set_notify_config_enabled(ctx.guild.id, config_id, False)
		if updated_count == 0:
			await ctx.send(f"notify config not found: id={config_id}")
			return
		await ctx.send(f"notify config disabled: id={config_id}")

	@notify_config_add.error
	@notify_config_enable.error
	@notify_config_disable.error
	async def notify_config_admin_error(self, ctx, error):
		"""Handle errors raised by administrator-only notify config commands."""
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("administrator permission is required.")
			return
		await ctx.send(f"notify config command failed: {error}")
