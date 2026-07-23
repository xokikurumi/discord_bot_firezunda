import asyncio

import discord
from discord.ext import commands

from config import DB_HOST, TOKEN
from db.session import AsyncSessionLocal, engine
from db.schema_migrations import run_schema_migrations
from models.base import Base
from cogs.messages.logs.message_cog import MessageCog
from cogs.messages.logs.voice_cog import VoiceCog
from cogs.disaster.p2pquake_cog import P2PQuakeCog
from cogs.tasks.ics_guild_event_cog import IcsGuildEventCog
from cogs.tasks.communication_trend_cog import CommunicationTrendCog
from cogs.tasks.niconico_info_cog import NiconicoInfoCog
from cogs.tasks.niconico_user_video_cog import NiconicoUserVideoCog
from cogs.messages.base.message_reaction_cog import MessageReactionCog
from cogs.messages.base.message_watcher_cog import MessageWatcherCog
from cogs.messages.base.analysis_cog import AnalysisCog
from cogs.messages.base.dice_roll_cog import DiceRollCog
from services.log.messageLogService import MessageLogService
from services.log.voiceStatusLogService import VoiceChannelStatusService
from services.base.message_reaction_service import MessageReactionService
from services.base.messageWatcherService import MessageWatcherService
from services.base.dice_roll_service import DiceRollService
from services.base.p2pquake_service import P2PQuakeService
from services.task.ics_guild_event_service import IcsGuildEventService
from services.task.communication_trend_service import CommunicationTrendService
from services.task.niconico_info_service import NiconicoInfoService
from services.task.niconico_user_video_service import NiconicoUserVideoService


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.moderation = True
intents.reactions = True
intents.messages = True
intents.voice_states = True

bot = commands.Bot(
	command_prefix="!",
	intents=intents,
	max_messages=10000,
)


async def init_db():
	"""Create missing tables and apply small compatibility migrations."""
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)
		await run_schema_migrations(conn)
	print("DB initialized.")


class Container:
	"""Factory for application services shared by Cogs."""

	def __init__(self):
		"""Store common dependencies used to build service instances."""
		self.session_factory = AsyncSessionLocal

	def create_message_service(self):
		"""Create the message logging service."""
		return MessageLogService(self.session_factory)

	def create_voice_status_service(self):
		"""Create the voice status logging service."""
		return VoiceChannelStatusService(self.session_factory)

	def create_message_reaction_service(self):
		"""Create the reaction keyword service with bot emoji access."""
		return MessageReactionService(self.session_factory, bot)

	def create_message_watcher_service(self):
		"""Create the Ollama-backed message watcher service."""
		return MessageWatcherService(self.session_factory, bot)

	def create_dice_roll_service(self):
		"""Create the dice roll service."""
		return DiceRollService()

	def create_p2pquake_service(self):
		"""Create the P2PQuake WebSocket notification service."""
		return P2PQuakeService(bot, self.session_factory)

	def create_ics_guild_event_service(self):
		"""Create the ICS guild scheduled event import service."""
		return IcsGuildEventService(bot, self.session_factory)

	def create_communication_trend_service(self):
		"""Create the semiannual communication trend analysis service."""
		return CommunicationTrendService(bot, self.session_factory)

	def create_niconico_user_video_service(self):
		"""Create the Niconico user uploaded video notification service."""
		return NiconicoUserVideoService(bot, self.session_factory)

	def create_niconico_info_service(self):
		"""Create the Niconico info/posting festival notification service."""
		return NiconicoInfoService(bot, self.session_factory)


container = Container()
slash_commands_synced = False


async def sync_slash_commands():
	"""Sync application commands globally and optionally per guild."""
	synced_commands = await bot.tree.sync()
	print(f"Slash commands synced globally: {len(synced_commands)}")

	try:
		from config import SLASH_COMMAND_SYNC_TO_GUILDS
	except ImportError:
		SLASH_COMMAND_SYNC_TO_GUILDS = True

	if not SLASH_COMMAND_SYNC_TO_GUILDS:
		return

	for guild in bot.guilds:
		try:
			bot.tree.copy_global_to(guild=guild)
			guild_commands = await bot.tree.sync(guild=guild)
			print(f"Slash commands synced guild={guild.id}: {len(guild_commands)}")
		except Exception as e:
			print(f"[ERROR] Guild slash command sync failed guild={guild.id}: {e}")


@bot.event
async def on_ready():
	"""Log when the Discord bot is ready."""
	global slash_commands_synced
	if not slash_commands_synced:
		try:
			await sync_slash_commands()
			slash_commands_synced = True
		except Exception as e:
			print(f"[ERROR] Slash command sync failed: {e}")
	print(f"Bot ready: {bot.user} (ID: {bot.user.id})")


async def setup_cogs():
	"""Create services and register all Discord Cogs."""
	print("Cog initialize.")
	message_service = container.create_message_service()
	voice_service = container.create_voice_status_service()
	reaction_service = container.create_message_reaction_service()
	watcher_service = container.create_message_watcher_service()
	dice_roll_service = container.create_dice_roll_service()
	p2pquake_service = container.create_p2pquake_service()
	ics_guild_event_service = container.create_ics_guild_event_service()
	communication_trend_service = container.create_communication_trend_service()
	niconico_user_video_service = container.create_niconico_user_video_service()
	niconico_info_service = container.create_niconico_info_service()

	await bot.add_cog(MessageCog(bot, message_service))
	await bot.add_cog(VoiceCog(bot, voice_service))
	await bot.add_cog(MessageReactionCog(bot, reaction_service))
	await bot.add_cog(MessageWatcherCog(bot, watcher_service))
	await bot.add_cog(AnalysisCog(bot, watcher_service))
	await bot.add_cog(DiceRollCog(bot, dice_roll_service))
	await bot.add_cog(P2PQuakeCog(bot, p2pquake_service))
	await bot.add_cog(IcsGuildEventCog(bot, ics_guild_event_service))
	await bot.add_cog(CommunicationTrendCog(bot, communication_trend_service))
	await bot.add_cog(NiconicoUserVideoCog(bot, niconico_user_video_service))
	await bot.add_cog(NiconicoInfoCog(bot, niconico_info_service))
	print("Cog initialize complete.")


async def close_resources():
	"""Dispose shared async database resources."""
	await engine.dispose()


async def main():
	"""Initialize resources and start the Discord bot."""
	if not TOKEN:
		raise RuntimeError("DISCORD_TOKEN is not set.")
	if DB_HOST.strip().lower() == "localohst":
		raise RuntimeError("DB_HOST is set to 'localohst'. Did you mean 'localhost'?")

	try:
		await init_db()
		await setup_cogs()

		print("Bot starting.")
		await bot.start(TOKEN)
	finally:
		await close_resources()


if __name__ == "__main__":
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		print("Bot stopped.")
