from discord.ext import commands

class VoiceCog(commands.Cog):
	"""Discord Cog for voice state logging."""

	def __init__(self, bot, Mservice):
		"""Keep references to the bot and voice status service."""
		self.bot = bot
		self.statusService = Mservice
		print("VoiceCog initialized.")

	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after):
		"""Persist each Discord voice state update."""
		try:
			await self.statusService.log_status(member, before, after)
		except Exception as e:
			# ログだけ吐いて落とさない
			print(f"[ERROR] on_voice_state_update: {e}")
