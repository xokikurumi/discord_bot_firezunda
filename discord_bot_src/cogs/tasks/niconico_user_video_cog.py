import asyncio

import discord
from discord.ext import commands


class NiconicoUserVideoCog(commands.Cog):
	"""Discord Cog that periodically checks Niconico user uploaded videos."""

	def __init__(self, bot, niconico_user_video_service):
		"""Keep references and task state for the Niconico notifier."""
		self.bot = bot
		self.service = niconico_user_video_service
		self.task = None
		print("NiconicoUserVideoCog initialized.")

	async def cog_load(self):
		"""Start the background upload checker when the Cog is loaded."""
		if self.task is None or self.task.done():
			self.task = asyncio.create_task(self.service.run_forever())

	async def cog_unload(self):
		"""Cancel the background upload checker when the Cog is unloaded."""
		if self.task:
			self.task.cancel()

	@commands.hybrid_command(name="niconico_user_video_check")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def niconico_user_video_check(self, ctx):
		"""Manually run the Niconico user upload check."""
		await ctx.send("Niconico user video check started.")
		await self.service.check_once()
		await ctx.send("Niconico user video check finished.")

	@commands.hybrid_group(name="niconico_user_video_user", invoke_without_command=True, fallback="help")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def niconico_user_video_user(self, ctx):
		"""Show usage for Niconico monitored user commands."""
		await ctx.send(
			"usage: !niconico_user_video_user add <user_id> | "
			"!niconico_user_video_user list | !niconico_user_video_user remove <id>"
		)

	@niconico_user_video_user.command(name="add")
	async def niconico_user_video_user_add(self, ctx, user_id: int):
		"""Add a Niconico user id to the monitored list."""
		await self.service.add_monitored_user(user_id)
		await ctx.send(f"Niconico monitored user added: user_id={user_id}")

	@niconico_user_video_user.command(name="list")
	async def niconico_user_video_user_list(self, ctx):
		"""List monitored Niconico user ids."""
		rows = await self.service.list_monitored_users()
		if not rows:
			await ctx.send("Niconico monitored users are not registered.")
			return

		lines = ["Niconico monitored users:"]
		for row in rows:
			lines.append(f"{row.id}: user_id={row.user_id}")
		await ctx.send("\n".join(lines))

	@niconico_user_video_user.command(name="remove")
	async def niconico_user_video_user_remove(self, ctx, row_id: int):
		"""Disable a monitored Niconico user row."""
		updated_count = await self.service.disable_monitored_user(row_id)
		if updated_count == 0:
			await ctx.send(f"Niconico monitored user not found: id={row_id}")
			return
		await ctx.send(f"Niconico monitored user removed: id={row_id}")

	@commands.hybrid_group(name="niconico_user_video_notify", invoke_without_command=True, fallback="help")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def niconico_user_video_notify(self, ctx):
		"""Show usage for per-user Niconico notification settings."""
		await ctx.send(
			"usage: !niconico_user_video_notify add <user_id> [#channel] [mention] | "
			"!niconico_user_video_notify list | "
			"!niconico_user_video_notify enable <id> | "
			"!niconico_user_video_notify disable <id>"
		)

	@niconico_user_video_notify.command(name="add")
	async def niconico_user_video_notify_add(
		self,
		ctx,
		user_id: int,
		channel: discord.TextChannel = None,
		mention: str = "",
	):
		"""Register a notification channel for one Niconico user."""
		target_channel = channel or ctx.channel
		mention = "" if mention.lower() in ("none", "なし", "no") else mention
		await self.service.add_notify_config(
			ctx.guild.id,
			user_id,
			target_channel.id,
			mention,
		)
		await ctx.send(
			f"Niconico notify config added: user_id={user_id}, "
			f"channel={target_channel.mention}, mention={mention or '-'}"
		)

	@niconico_user_video_notify.command(name="list")
	async def niconico_user_video_notify_list(self, ctx):
		"""List per-user Niconico notification channel settings."""
		rows = await self.service.list_notify_configs(ctx.guild.id)
		if not rows:
			await ctx.send("Niconico notify configs are not registered.")
			return

		lines = ["Niconico notify configs:"]
		for row in rows:
			channel = self.bot.get_channel(row.channel_id)
			channel_text = channel.mention if channel else str(row.channel_id)
			lines.append(
				f"{row.id}: user_id={row.user_id}, channel={channel_text}, "
				f"enabled={row.enabled}, mention={row.mention or '-'}"
			)

		message = ""
		for line in lines:
			if len(message) + len(line) + 1 > 1900:
				await ctx.send(message)
				message = ""
			message += line + "\n"
		if message:
			await ctx.send(message)

	@niconico_user_video_notify.command(name="enable")
	async def niconico_user_video_notify_enable(self, ctx, config_id: int):
		"""Enable one per-user Niconico notification setting."""
		updated_count = await self.service.set_notify_config_enabled(ctx.guild.id, config_id, True)
		if updated_count == 0:
			await ctx.send(f"Niconico notify config not found: id={config_id}")
			return
		await ctx.send(f"Niconico notify config enabled: id={config_id}")

	@niconico_user_video_notify.command(name="disable")
	async def niconico_user_video_notify_disable(self, ctx, config_id: int):
		"""Disable one per-user Niconico notification setting."""
		updated_count = await self.service.set_notify_config_enabled(ctx.guild.id, config_id, False)
		if updated_count == 0:
			await ctx.send(f"Niconico notify config not found: id={config_id}")
			return
		await ctx.send(f"Niconico notify config disabled: id={config_id}")

	@niconico_user_video_check.error
	async def niconico_user_video_check_error(self, ctx, error):
		"""Handle errors raised by the manual Niconico check command."""
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("administrator permission is required.")
			return
		await ctx.send(f"Niconico user video check failed: {error}")

	@niconico_user_video_user.error
	@niconico_user_video_user_add.error
	@niconico_user_video_user_list.error
	@niconico_user_video_user_remove.error
	async def niconico_user_video_user_error(self, ctx, error):
		"""Handle errors raised by Niconico monitored user commands."""
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("administrator permission is required.")
			return
		await ctx.send(f"Niconico monitored user command failed: {error}")

	@niconico_user_video_notify.error
	@niconico_user_video_notify_add.error
	@niconico_user_video_notify_list.error
	@niconico_user_video_notify_enable.error
	@niconico_user_video_notify_disable.error
	async def niconico_user_video_notify_error(self, ctx, error):
		"""Handle errors raised by Niconico notification setting commands."""
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("administrator permission is required.")
			return
		await ctx.send(f"Niconico notify config command failed: {error}")
