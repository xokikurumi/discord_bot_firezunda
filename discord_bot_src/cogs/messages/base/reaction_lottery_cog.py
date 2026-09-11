import asyncio

import discord
from discord.ext import commands


class ReactionLotteryCog(commands.Cog):
	"""Discord Cog for reaction-based lotteries."""

	def __init__(self, bot, lottery_service):
		"""Keep references to the bot and lottery service."""
		self.bot = bot
		self.service = lottery_service
		self.tasks = {}
		print("ReactionLotteryCog initialized.")

	def cog_unload(self):
		"""Cancel active lottery tasks when the Cog is unloaded."""
		for task in self.tasks.values():
			task.cancel()
		self.tasks.clear()

	@commands.hybrid_group(name="lottery", invoke_without_command=True, fallback="help")
	@commands.guild_only()
	async def lottery_command(self, ctx):
		"""Show usage for lottery commands."""
		await ctx.send(
			"usage: !lottery start [end] [winners] [emoji] [title]\n"
			"example: !lottery start 30m 1 🎉 景品抽選\n"
			"example: !lottery start 2 \"2026-08-10 21:00\" イベント抽選\n"
			"usage: !lottery end <message_id>"
		)

	@lottery_command.command(name="start")
	@commands.guild_only()
	async def lottery_start(self, ctx, winners: str = "1", end: str = "1h", *, title: str = "抽選"):
		"""Start a reaction lottery that anyone can create."""
		try:
			winners, end, reaction_emoji, title = self.parse_start_options(winners, end, title)
			deadline = self.service.parse_end_time(end)
			if winners <= 0:
				raise ValueError("winners must be 1 or more.")
		except Exception as e:
			await ctx.send(f"lottery start failed: {e}")
			return

		embed = discord.Embed(
			title=f"{reaction_emoji} {title}",
			description=(
				f"{reaction_emoji} を押すと応募できます。\n"
				f"当選人数: {winners}\n"
				f"応募締切: {self.service.format_deadline_timestamp(deadline)}"
			),
			color=0xF5A623,
		)
		embed.set_footer(text=f"created by {ctx.author.display_name}")
		message = await ctx.send(embed=embed)
		await message.add_reaction(reaction_emoji)

		task = asyncio.create_task(self.finish_lottery_later(
			message.channel.id,
			message.id,
			winners,
			deadline,
			title,
			reaction_emoji,
		))
		self.tasks[message.id] = {
			"task": task,
			"channel_id": message.channel.id,
			"winners": winners,
			"title": title,
			"reaction_emoji": reaction_emoji,
			"creator_id": ctx.author.id,
		}

	@lottery_command.command(name="end")
	@commands.guild_only()
	async def lottery_end(self, ctx, message_id: int):
		"""End an active lottery early."""
		entry = self.tasks.pop(message_id, None)
		if entry is None:
			await ctx.send(f"active lottery not found: message_id={message_id}")
			return
		if not self.can_end_lottery(ctx, entry):
			await ctx.send("lottery end failed: only the creator or message managers can end it.")
			self.tasks[message_id] = entry
			return
		entry["task"].cancel()
		await self.finish_lottery(
			entry["channel_id"],
			message_id,
			entry["winners"],
			entry["title"],
			entry.get("reaction_emoji", self.service.DEFAULT_REACTION),
		)

	async def finish_lottery_later(
		self,
		channel_id: int,
		message_id: int,
		winners: int,
		deadline,
		title: str,
		reaction_emoji: str,
	):
		"""Wait until the deadline and finish the lottery."""
		try:
			await asyncio.sleep(self.service.seconds_until(deadline))
			await self.finish_lottery(channel_id, message_id, winners, title, reaction_emoji)
		except asyncio.CancelledError:
			raise
		except Exception as e:
			print(f"[ERROR] lottery finish failed message_id={message_id}: {e}")
		finally:
			self.tasks.pop(message_id, None)

	async def finish_lottery(
		self,
		channel_id: int,
		message_id: int,
		winners: int = 1,
		title: str = "抽選",
		reaction_emoji: str = None,
	):
		"""Fetch reaction users, choose winners, and post the result."""
		reaction_emoji = reaction_emoji or self.service.DEFAULT_REACTION
		channel = self.bot.get_channel(channel_id)
		if channel is None:
			channel = await self.bot.fetch_channel(channel_id)

		message = await channel.fetch_message(message_id)
		reaction = self.find_lottery_reaction(message, reaction_emoji)
		if reaction is None:
			await channel.send(f"lottery finished: {title}\n応募リアクションが見つかりませんでした。")
			return

		users = [user async for user in reaction.users()]
		winner_users = self.service.choose_winners(users, winners)
		if not winner_users:
			await channel.send(f"lottery finished: {title}\n応募者はいませんでした。")
			return

		mentions = ", ".join(user.mention for user in winner_users)
		await channel.send(
			f"lottery finished: {title}\n"
			f"当選者: {mentions}"
		)

	def parse_start_options(self, winners_text: str, end_text: str, title_text: str):
		"""Parse flexible prefix/slash lottery start arguments."""
		first = str(winners_text or "").strip()
		second = str(end_text or "").strip()
		title = (title_text or "").strip() or "抽選"

		if self.is_positive_int(first):
			winners = int(first)
			end = second or "1h"
		elif self.is_positive_int(second):
			winners = int(second)
			end = first or "1h"
		else:
			winners = 1
			end = first or second or "1h"
			if second and second != "1h":
				title = f"{second} {title}".strip()

		reaction_emoji, title = self.extract_reaction_from_title(title)
		return winners, end, reaction_emoji, title

	def is_positive_int(self, text: str):
		"""Return True when text is a positive integer."""
		return str(text or "").strip().isdigit() and int(str(text).strip()) > 0

	def extract_reaction_from_title(self, title: str):
		"""Extract an optional leading reaction emoji from the title text."""
		parts = (title or "").strip().split(maxsplit=1)
		if not parts:
			return self.service.DEFAULT_REACTION, "抽選"

		first = parts[0]
		if self.looks_like_reaction_emoji(first):
			return first, parts[1].strip() if len(parts) > 1 and parts[1].strip() else "抽選"
		return self.service.DEFAULT_REACTION, title.strip() or "抽選"

	def looks_like_reaction_emoji(self, text: str):
		"""Return True when text looks usable as a Discord reaction emoji."""
		token = (text or "").strip()
		if token.startswith(("<:", "<a:")) and token.endswith(">"):
			return True
		return bool(token) and not any(char.isalnum() for char in token)

	def find_lottery_reaction(self, message, reaction_emoji: str = None):
		"""Return the configured lottery reaction from a message."""
		reaction_emoji = reaction_emoji or self.service.DEFAULT_REACTION
		for reaction in message.reactions:
			if str(reaction.emoji) == reaction_emoji:
				return reaction
		return None

	def can_end_lottery(self, ctx, entry):
		"""Return True when a user may end a lottery early."""
		if ctx.author.id == entry.get("creator_id"):
			return True
		return bool(getattr(ctx.author.guild_permissions, "manage_messages", False))
