import asyncio

from discord.ext import commands


class NiconicoInfoCog(commands.Cog):
	"""Discord Cog that periodically checks Niconico info/posting festival pages."""

	def __init__(self, bot, niconico_info_service):
		"""Keep references and task state for the Niconico info notifier."""
		self.bot = bot
		self.service = niconico_info_service
		self.task = None
		print("NiconicoInfoCog initialized.")

	async def cog_load(self):
		"""Start the background Niconico info checker when the Cog is loaded."""
		if self.task is None or self.task.done():
			self.task = asyncio.create_task(self.service.run_forever())

	async def cog_unload(self):
		"""Cancel the background checker when the Cog is unloaded."""
		if self.task:
			self.task.cancel()

	@commands.hybrid_command(name="niconico_info_check")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def niconico_info_check(self, ctx):
		"""Manually run the Niconico info check."""
		await ctx.send("Niconico info check started.")
		await self.service.check_once()
		await ctx.send("Niconico info check finished.")

	@commands.hybrid_group(name="niconico_info_filter", invoke_without_command=True, fallback="help")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def niconico_info_filter(self, ctx):
		"""Show usage for Niconico Info filter commands."""
		await ctx.send(
			"usage: !niconico_info_filter add <keyword> [include|exclude] | "
			"!niconico_info_filter list | "
			"!niconico_info_filter enable <id> | "
			"!niconico_info_filter disable <id> | "
			"!niconico_info_filter remove <id>"
		)

	@niconico_info_filter.command(name="add")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def niconico_info_filter_add(self, ctx, keyword: str, mode: str = "include"):
		"""Add a Niconico Info keyword filter."""
		normalized_mode = await self.service.add_filter(ctx.guild.id, keyword, mode)
		await ctx.send(f"Niconico info filter added: mode={normalized_mode}, keyword={keyword}")

	@niconico_info_filter.command(name="list")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def niconico_info_filter_list(self, ctx):
		"""List Niconico Info keyword filters."""
		rows = await self.service.list_filters(ctx.guild.id)
		if not rows:
			await ctx.send("Niconico info filters are not registered.")
			return

		lines = ["Niconico info filters:"]
		for row in rows:
			lines.append(
				f"{row.id}: mode={row.mode}, enabled={bool(row.enabled)}, keyword={row.keyword}"
			)

		message = ""
		for line in lines:
			if len(message) + len(line) + 1 > 1900:
				await ctx.send(message)
				message = ""
			message += line + "\n"
		if message:
			await ctx.send(message)

	@niconico_info_filter.command(name="enable")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def niconico_info_filter_enable(self, ctx, filter_id: int):
		"""Enable one Niconico Info keyword filter."""
		updated_count = await self.service.set_filter_enabled(ctx.guild.id, filter_id, True)
		if updated_count == 0:
			await ctx.send(f"Niconico info filter not found: id={filter_id}")
			return
		await ctx.send(f"Niconico info filter enabled: id={filter_id}")

	@niconico_info_filter.command(name="disable")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def niconico_info_filter_disable(self, ctx, filter_id: int):
		"""Disable one Niconico Info keyword filter."""
		updated_count = await self.service.set_filter_enabled(ctx.guild.id, filter_id, False)
		if updated_count == 0:
			await ctx.send(f"Niconico info filter not found: id={filter_id}")
			return
		await ctx.send(f"Niconico info filter disabled: id={filter_id}")

	@niconico_info_filter.command(name="remove")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def niconico_info_filter_remove(self, ctx, filter_id: int):
		"""Remove one Niconico Info keyword filter."""
		updated_count = await self.service.delete_filter(ctx.guild.id, filter_id)
		if updated_count == 0:
			await ctx.send(f"Niconico info filter not found: id={filter_id}")
			return
		await ctx.send(f"Niconico info filter removed: id={filter_id}")

	@niconico_info_check.error
	async def niconico_info_check_error(self, ctx, error):
		"""Handle errors raised by the manual Niconico info check command."""
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("administrator permission is required.")
			return
		await ctx.send(f"Niconico info check failed: {error}")

	@niconico_info_filter.error
	@niconico_info_filter_add.error
	@niconico_info_filter_list.error
	@niconico_info_filter_enable.error
	@niconico_info_filter_disable.error
	@niconico_info_filter_remove.error
	async def niconico_info_filter_error(self, ctx, error):
		"""Handle errors raised by Niconico Info filter commands."""
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("administrator permission is required.")
			return
		await ctx.send(f"Niconico info filter command failed: {error}")
