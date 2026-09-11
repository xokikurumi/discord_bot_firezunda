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
			"<correct|false_positive|false_negative|unsure> [note or corrected JSON]\n"
			"usage: !analysis whitelist add <text_exact|text_contains|user|channel> <pattern>\n"
			"usage: !analysis whitelist list [all]\n"
			"usage: !analysis whitelist enable|disable <id>"
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

	@analysis_command.group(name="whitelist", invoke_without_command=True)
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def analysis_whitelist(self, ctx):
		"""Show analysis whitelist command usage."""
		await ctx.send(
			"usage: !analysis whitelist add <text_exact|text_contains|user|channel> <pattern>\n"
			"usage: !analysis whitelist list [all]\n"
			"usage: !analysis whitelist enable|disable <id>"
		)

	@analysis_whitelist.command(name="add")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def analysis_whitelist_add(self, ctx, rule_type: str, *, pattern: str):
		"""Add an analysis whitelist rule."""
		try:
			normalized_type, normalized_pattern = await self.service.add_whitelist_rule(
				ctx.guild.id,
				ctx.author.id,
				rule_type,
				pattern,
			)
		except Exception as e:
			await ctx.send(f"analysis whitelist add failed: {e}")
			return

		await ctx.send(
			"analysis whitelist added: "
			f"type={normalized_type}, pattern={self.truncate_for_discord(normalized_pattern)}"
		)

	@analysis_whitelist.command(name="list")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def analysis_whitelist_list(self, ctx, include_disabled: str = ""):
		"""List analysis whitelist rules."""
		include_all = include_disabled.strip().lower() in {"all", "true", "disabled", "include_disabled"}
		rows = await self.service.list_whitelist_rules(ctx.guild.id, include_all)
		if not rows:
			await ctx.send("analysis whitelist rules are not registered.")
			return

		lines = ["analysis whitelist rules:"]
		for row in rows[:30]:
			status = "enabled" if row.enabled else "disabled"
			lines.append(
				f"- id={row.id} [{status}] type={row.rule_type} "
				f"pattern={self.truncate_for_discord(row.pattern)}"
			)
		if len(rows) > 30:
			lines.append(f"...and {len(rows) - 30} more")
		await ctx.send("\n".join(lines))

	@analysis_whitelist.command(name="enable")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def analysis_whitelist_enable(self, ctx, rule_id: int):
		"""Enable an analysis whitelist rule."""
		updated_count = await self.service.set_whitelist_rule_enabled(ctx.guild.id, rule_id, True)
		if updated_count == 0:
			await ctx.send(f"analysis whitelist rule not found: id={rule_id}")
			return
		await ctx.send(f"analysis whitelist enabled: id={rule_id}")

	@analysis_whitelist.command(name="disable")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def analysis_whitelist_disable(self, ctx, rule_id: int):
		"""Disable an analysis whitelist rule."""
		updated_count = await self.service.set_whitelist_rule_enabled(ctx.guild.id, rule_id, False)
		if updated_count == 0:
			await ctx.send(f"analysis whitelist rule not found: id={rule_id}")
			return
		await ctx.send(f"analysis whitelist disabled: id={rule_id}")

	@analysis_whitelist.error
	@analysis_whitelist_add.error
	@analysis_whitelist_list.error
	@analysis_whitelist_enable.error
	@analysis_whitelist_disable.error
	async def analysis_whitelist_error(self, ctx, error):
		"""Handle errors raised by administrator-only whitelist commands."""
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("administrator permission is required.")
			return
		await ctx.send(f"analysis whitelist command failed: {error}")

	def truncate_for_discord(self, text: str, max_chars: int = 120):
		"""Return compact text for command responses."""
		value = str(text or "").replace("\n", " ").strip()
		if len(value) <= max_chars:
			return value
		return value[:max_chars - 3] + "..."
