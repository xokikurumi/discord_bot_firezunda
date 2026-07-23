from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.task.ics_guild_event_config import IcsGuildEventConfig


class IcsGuildEventConfigRepository:
	"""Database access for guild opt-in settings for ICS event imports."""

	def __init__(self, session: AsyncSession):
		"""Store the active SQLAlchemy session."""
		self.session = session

	async def get_by_guild_id(self, guild_id: int):
		"""Return the ICS import config row for a guild, if it exists."""
		stmt = select(IcsGuildEventConfig).where(IcsGuildEventConfig.guild_id == guild_id)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none()

	async def is_enabled(self, guild_id: int):
		"""Return True when a guild has opted in to ICS scheduled event imports."""
		config = await self.get_by_guild_id(guild_id)
		return bool(config and config.enabled)

	async def set_enabled(self, guild_id: int, enabled: bool):
		"""Create or update the guild opt-in flag."""
		config = await self.get_by_guild_id(guild_id)
		if config:
			stmt = (
				update(IcsGuildEventConfig)
				.where(IcsGuildEventConfig.guild_id == guild_id)
				.values(enabled=enabled)
			)
			await self.session.execute(stmt)
		else:
			self.session.add(IcsGuildEventConfig(guild_id=guild_id, enabled=enabled))

		await self.session.commit()

	async def list_enabled_guild_ids(self):
		"""Return guild IDs that currently allow ICS scheduled event imports."""
		stmt = select(IcsGuildEventConfig.guild_id).where(IcsGuildEventConfig.enabled.is_(True))
		result = await self.session.execute(stmt)
		return list(result.scalars().all())
