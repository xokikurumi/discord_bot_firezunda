from discord.ext import commands


class AnalysisCog(commands.Cog):
	"""Discord Cog for message analysis maintenance commands."""

	def __init__(self, bot, watcher_service):
		"""Keep references to the bot and watcher service."""
		self.bot = bot
		self.service = watcher_service
		print("AnalysisCog initialized.")

	@commands.hybrid_group(name="analysis", invoke_without_command=True, fallback="help")
	@commands.guild_only()
	async def analysis_command(self, ctx):
		"""Show usage when the analysis command group is called without a subcommand."""
		await ctx.send(
			"usage: !analysis feedback <message_id> "
			"<correct|false_positive|false_negative|unsure> [note or corrected JSON]"
		)

	@analysis_command.command(name="feedback")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def analysis_feedback(self, ctx, message_id: str, label: str, *, note: str = ""):
		"""Register administrator feedback for a stored analysis result."""
		message_id_text = message_id.strip()
		if not message_id_text.isdecimal():
			await ctx.send("message_id must be a Discord message id.")
			return

		message_id_value = int(message_id_text)
		try:
			normalized_label = await self.service.add_feedback(
				ctx.guild.id,
				ctx.author.id,
				message_id_value,
				label,
				note,
			)
		except Exception as e:
			await ctx.send(f"analysis feedback failed: {e}")
			return

		await ctx.send(
			f"analysis feedback added: message_id={message_id_value}, label={normalized_label}"
		)

	@analysis_feedback.error
	async def analysis_feedback_error(self, ctx, error):
		"""Handle errors raised by administrator-only analysis commands."""
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("administrator permission is required.")
			return
		await ctx.send(f"analysis feedback failed: {error}")
