import asyncio

from discord.ext import commands


class CommunicationTrendCog(commands.Cog):
	"""Discord Cog that runs semiannual communication trend analysis."""

	def __init__(self, bot, communication_trend_service):
		"""Keep references and task state for the analyzer."""
		self.bot = bot
		self.service = communication_trend_service
		self.task = None
		print("CommunicationTrendCog initialized.")

	async def cog_load(self):
		"""Start the background analyzer when the Cog is loaded."""
		if self.task is None or self.task.done():
			self.task = asyncio.create_task(self.service.run_forever())

	async def cog_unload(self):
		"""Cancel the background analyzer when the Cog is unloaded."""
		if self.task:
			self.task.cancel()

	@commands.hybrid_command(name="communication_trend_analyze")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def communication_trend_analyze(self, ctx):
		"""Manually analyze the latest completed half-year period."""
		await self.send_internal_status(ctx, "communication trend analysis started.")
		period = await self.service.analyze_previous_period(ctx.guild.id)
		await self.send_internal_status(ctx, f"communication trend analysis finished: period={period.key}")

	async def send_internal_status(self, ctx, message: str):
		"""Send a non-public or short-lived status message without exposing results."""
		if getattr(ctx, "interaction", None) is not None:
			await ctx.send(message, ephemeral=True)
			return
		await ctx.send(message, delete_after=10)

	@communication_trend_analyze.error
	async def communication_trend_analyze_error(self, ctx, error):
		"""Handle errors raised by the manual trend analysis command."""
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("administrator permission is required.")
			return
		await ctx.send(f"communication trend analysis failed: {error}")
