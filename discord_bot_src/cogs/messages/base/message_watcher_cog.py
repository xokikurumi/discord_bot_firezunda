import asyncio

from discord.ext import commands


class MessageWatcherCog(commands.Cog):
	"""Discord Cog that forwards user messages to the watcher service."""

	def __init__(self, bot, watcher_service):
		"""Keep references to the bot and watcher service."""
		self.bot = bot
		self.service = watcher_service
		print("MessageWatcherCog initialized.")

	@commands.Cog.listener()
	async def on_message(self, message):
		"""Handle new messages and trigger Ollama-based discomfort analysis."""
		# Analyze only server messages written by users.
		if message.author.bot:
			return

		if not message.guild:
			return

		asyncio.create_task(self.run_watch(message))

	async def run_watch(self, message):
		"""Run message analysis in the background without breaking message events."""
		try:
			await self.service.watch(message)
		except Exception as e:
			print(f"[ERROR] message watcher task failed message_id={message.id}: {e}")
