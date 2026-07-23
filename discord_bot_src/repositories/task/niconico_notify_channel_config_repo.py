from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.task.niconico_notify_channel_config import NiconicoNotifyChannelConfig


class NiconicoNotifyChannelConfigRepository:
	"""Database access for per-user Niconico notification settings."""

	def __init__(self, session: AsyncSession):
		"""Store the active SQLAlchemy session."""
		self.session = session

	async def get_enabled_by_guild_and_user(self, guild_id: int, user_id: int):
		"""Return enabled Niconico notification settings for one guild and user."""
		stmt = (
			select(NiconicoNotifyChannelConfig)
			.where(
				NiconicoNotifyChannelConfig.guild_id == guild_id,
				NiconicoNotifyChannelConfig.user_id == user_id,
				NiconicoNotifyChannelConfig.enabled.is_(True),
			)
			.order_by(NiconicoNotifyChannelConfig.id.asc())
		)
		result = await self.session.execute(stmt)
		return result.scalars().all()

	async def insert(self, data: dict):
		"""Insert one per-user Niconico notification setting."""
		stmt = insert(NiconicoNotifyChannelConfig).values(**data)
		await self.session.execute(stmt)
		await self.session.commit()

	async def list_by_guild(self, guild_id: int):
		"""Return all per-user Niconico notification settings for a guild."""
		stmt = (
			select(NiconicoNotifyChannelConfig)
			.where(NiconicoNotifyChannelConfig.guild_id == guild_id)
			.order_by(
				NiconicoNotifyChannelConfig.user_id.asc(),
				NiconicoNotifyChannelConfig.id.asc(),
			)
		)
		result = await self.session.execute(stmt)
		return result.scalars().all()

	async def set_enabled(self, guild_id: int, config_id: int, enabled: bool):
		"""Enable or disable one per-user Niconico notification setting."""
		stmt = (
			update(NiconicoNotifyChannelConfig)
			.where(
				NiconicoNotifyChannelConfig.id == config_id,
				NiconicoNotifyChannelConfig.guild_id == guild_id,
			)
			.values(enabled=enabled)
		)
		result = await self.session.execute(stmt)
		await self.session.commit()
		return result.rowcount
