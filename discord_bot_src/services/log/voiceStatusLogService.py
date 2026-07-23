from repositories.log.voice_channel_status_log_repo import VoiceChannelStatusRepository

class VoiceChannelStatusService:
	"""Persist voice channel state transitions."""

	def __init__(self, session_factory):
		"""Store the database session factory used for voice logs."""
		self.session_factory = session_factory

	async def log_status(self, member, before, after):
		"""Persist before/after voice state details for one member."""
		async with self.session_factory() as session:

			repo = VoiceChannelStatusRepository(session)
			await repo.insert({
				"before_guild_id": 0 if before.channel == None else before.channel.guild.id,
				"after_guild_id": 0 if after.channel == None else after.channel.guild.id,
				
				"user_id": member.id,

				"before_channel_id": 0 if before.channel == None else before.channel.id,
				"after_channel_id": 0 if after.channel == None else after.channel.id,

				"before_mute": before.self_mute,
				"after_mute": after.self_mute,

				"before_deaf": before.self_deaf,
				"after_deaf": after.self_deaf,

				"before_video": before.self_video,
				"after_video": after.self_video,

				"before_stream": before.self_stream,
				"after_stream": after.self_stream,
			})
