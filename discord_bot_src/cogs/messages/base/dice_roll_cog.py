from discord.ext import commands


class DiceRollCog(commands.Cog):
	"""Discord Cog for automatic and command-based dice rolls."""

	def __init__(self, bot, dice_service):
		"""Keep references to the bot and dice service."""
		self.bot = bot
		self.service = dice_service
		print("DiceRollCog initialized.")

	@commands.hybrid_command(name="roll", aliases=["dice"])
	async def roll_command(self, ctx, *, expression: str):
		"""Roll a dice expression such as 1d100 or 2d6+3."""
		try:
			result = self.service.roll(expression)
		except Exception as e:
			await ctx.send(f"dice roll failed: {e}")
			return

		await ctx.send(result)

	@commands.Cog.listener()
	async def on_message(self, message):
		"""Roll messages that consist only of a dice expression."""
		if message.author.bot:
			return

		if not message.guild:
			return

		if not self.service.is_auto_roll(message.content):
			return

		try:
			result = self.service.roll(message.content)
		except Exception as e:
			await message.channel.send(f"dice roll failed: {e}")
			return

		await message.channel.send(result)
