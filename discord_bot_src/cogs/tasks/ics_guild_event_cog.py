import asyncio

from discord.ext import commands


class IcsGuildEventCog(commands.Cog):
	"""Discord Cog that periodically imports ICS events into guild events."""

	def __init__(self, bot, ics_guild_event_service):
		"""Keep references and task state for the ICS importer."""
		self.bot = bot
		self.service = ics_guild_event_service
		self.task = None
		print("IcsGuildEventCog initialized.")

	async def cog_load(self):
		"""Start the background import checker when the Cog is loaded."""
		if self.task is None or self.task.done():
			self.task = asyncio.create_task(self.service.run_forever())

	async def cog_unload(self):
		"""Cancel the background import checker when the Cog is unloaded."""
		if self.task:
			self.task.cancel()

	@commands.hybrid_command(name="ics_event_sync")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def ics_event_sync(self, ctx):
		"""Manually run the ICS guild event import for the current enabled guild."""
		if not await self.service.is_guild_enabled(ctx.guild.id):
			await ctx.send("ICS guild event import is disabled for this server. Run !ics_event_enable first.")
			return

		await ctx.send("ICS guild event import started.")
		await self.service.import_guild(ctx.guild)
		await ctx.send("ICS guild event import finished.")

	@commands.hybrid_command(name="ics_event_enable")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def ics_event_enable(self, ctx):
		"""Enable ICS guild scheduled event imports for the current guild."""
		await self.service.set_guild_enabled(ctx.guild.id, True)
		await ctx.send("ICS guild event import enabled for this server.")

	@commands.hybrid_command(name="ics_event_disable")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def ics_event_disable(self, ctx):
		"""Disable ICS guild scheduled event imports for the current guild."""
		await self.service.set_guild_enabled(ctx.guild.id, False)
		await ctx.send("ICS guild event import disabled for this server.")

	@commands.hybrid_command(name="ics_event_status")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def ics_event_status(self, ctx):
		"""Show whether ICS guild scheduled event imports are enabled."""
		enabled = await self.service.is_guild_enabled(ctx.guild.id)
		status = "enabled" if enabled else "disabled"
		await ctx.send(f"ICS guild event import is {status} for this server.")

	@ics_event_sync.error
	async def ics_event_sync_error(self, ctx, error):
		"""Handle errors raised by the manual ICS import command."""
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("administrator permission is required.")
			return
		await ctx.send(f"ICS guild event import failed: {error}")

	@ics_event_enable.error
	@ics_event_disable.error
	@ics_event_status.error
	async def ics_event_config_error(self, ctx, error):
		"""Handle errors raised by ICS import configuration commands."""
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("administrator permission is required.")
			return
		await ctx.send(f"ICS guild event config command failed: {error}")
