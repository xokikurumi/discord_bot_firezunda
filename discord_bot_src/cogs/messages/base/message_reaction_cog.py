from discord.ext import commands


class MessageReactionCog(commands.Cog):
	"""Discord Cog for reaction keyword commands and automatic reactions."""

	def __init__(self, bot, message_service):
		"""Keep references to the bot and reaction service."""
		self.bot = bot
		self.service = message_service
		print("MessageReactionCog initialized.")

	@commands.hybrid_group(name="reaction", invoke_without_command=True, fallback="help")
	@commands.guild_only()
	async def reaction_command(self, ctx):
		"""Show usage when the reaction command group is called without a subcommand."""
		await ctx.send(
			"usage: !reaction add <keyword> <reaction> [ng_word] | "
			"!reaction remove <keyword> | !reaction list | !reaction seed_syukka"
		)

	@reaction_command.command(name="add")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def reaction_add(self, ctx, keyword: str, reaction: str, ng_word: str = "false"):
		"""Register a keyword and its reaction for the current guild."""
		# Store either a Unicode emoji or a custom emoji mention for this guild.
		ng_word_flg = self.service.parse_bool(ng_word)
		reaction_data = self.service.parse_reaction(reaction)
		await self.service.add_keyword(ctx.guild.id, keyword, reaction, ng_word_flg)

		message = f"reaction keyword added: keyword={keyword}, reaction={reaction}, ng_word={ng_word_flg}"
		if reaction_data["reaction_id"] and self.bot.get_emoji(reaction_data["reaction_id"]) is None:
			message += "\nwarning: this custom emoji is not visible in the bot cache. It will be tried as an external emoji."

		await ctx.send(message)

	@reaction_command.command(name="remove")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def reaction_remove(self, ctx, keyword: str):
		"""Soft-delete a keyword rule for the current guild."""
		# Keep history by soft-deleting instead of removing rows from the table.
		deleted_count = await self.service.remove_keyword(ctx.guild.id, keyword)
		if deleted_count == 0:
			await ctx.send(f"reaction keyword not found: keyword={keyword}")
			return

		await ctx.send(f"reaction keyword removed: keyword={keyword}, count={deleted_count}")

	@reaction_command.command(name="list")
	@commands.guild_only()
	async def reaction_list(self, ctx):
		"""List reaction keyword rules registered for the current guild."""
		keywords = await self.service.list_keywords(ctx.guild.id)
		if not keywords:
			await ctx.send("reaction keywords are not registered.")
			return

		lines = []
		for keyword in keywords:
			reaction = keyword.reaction
			if keyword.reaction_id:
				prefix = "a" if keyword.reaction_animation_flg else ""
				reaction = f"<{prefix}:{keyword.reaction}:{keyword.reaction_id}>"

			ng_word = bool(keyword.ng_word_flg)
			enabled = bool(keyword.enabled)
			lines.append(
				f"{keyword.id}: keyword={keyword.keyword}, reaction={reaction}, "
				f"ng_word={ng_word}, enabled={enabled}"
			)

		message = "reaction keywords:\n"
		for line in lines:
			if len(message) + len(line) + 1 > 1900:
				await ctx.send(message)
				message = ""
			message += line + "\n"

		if message:
			await ctx.send(message)

	@reaction_command.command(name="check_emoji")
	@commands.guild_only()
	async def reaction_check_emoji(self, ctx, emoji: str):
		"""Check whether the bot can see and use a custom emoji."""
		# Helps diagnose Unknown Emoji errors for external custom emoji.
		status = self.service.check_emoji_status(ctx.channel, emoji)
		if status["emoji_id"] is None:
			await ctx.send("custom emoji mention or emoji id is required.")
			return

		lines = [
			f"emoji_id={status['emoji_id']}",
			f"bot_can_see_emoji={status['visible']}",
			f"add_reactions_permission={status['add_reactions']}",
			f"use_external_emojis_permission={status['use_external_emojis']}",
		]

		if status["emoji"] is not None:
			lines.append(f"emoji={status['emoji']}")
		else:
			lines.append(
				"emoji is not visible to this bot. The bot must be in the emoji source server, "
				"and this channel needs Use External Emojis permission."
			)

		await ctx.send("\n".join(lines))

	@reaction_command.command(name="seed_syukka")
	@commands.guild_only()
	@commands.has_guild_permissions(administrator=True)
	async def reaction_seed_syukka(self, ctx):
		"""Register the legacy syukka reaction preset for the current guild."""
		result = await self.service.add_syukka_preset(ctx.guild.id)
		lines = [
			"syukka reaction preset registered.",
			f"reaction={result['reaction']}",
			f"added={', '.join(result['added']) if result['added'] else '-'}",
			f"skipped={', '.join(result['skipped']) if result['skipped'] else '-'}",
		]
		await ctx.send("\n".join(lines))

	@reaction_add.error
	@reaction_remove.error
	@reaction_seed_syukka.error
	async def reaction_admin_error(self, ctx, error):
		"""Handle errors raised by administrator-only reaction commands."""
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("administrator permission is required.")
			return
		await ctx.send(f"reaction command failed: {error}")

	@commands.Cog.listener()
	async def on_message(self, message):
		"""Apply registered reaction rules to new user messages."""
		# =========================
		# 基本フィルタ
		# =========================
		if message.author.bot:
		    return

		if not message.guild:
			return  # DM除外（必要なら変更）

		# =========================
		# リアクション処理
		# =========================
		await self.service.reaction(message)
