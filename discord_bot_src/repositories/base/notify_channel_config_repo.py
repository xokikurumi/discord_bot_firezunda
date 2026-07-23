from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.text.notify_channel_config import NotifyChannelConfig


class NotifyChannelConfigRepository:
	"""Database access for guild notification channel settings."""

	def __init__(self, session: AsyncSession):
		"""Store the active SQLAlchemy session."""
		self.session = session

	async def get_enabled_by_category(self, guild_id: int, category: str):
		"""Return enabled notification settings for a guild and category."""
		stmt = (
			select(NotifyChannelConfig)
			.where(
				NotifyChannelConfig.guild_id == guild_id,
				NotifyChannelConfig.category == category,
				NotifyChannelConfig.enabled.is_(True),
			)
			.order_by(NotifyChannelConfig.id.asc())
		)
		result = await self.session.execute(stmt)
		return result.scalars().all()

	async def insert(self, data: dict):
		"""Insert one notification channel setting."""
		stmt = insert(NotifyChannelConfig).values(**data)
		await self.session.execute(stmt)
		await self.session.commit()

	async def list_by_guild(self, guild_id: int):
		"""Return all notification settings for a guild."""
		stmt = (
			select(NotifyChannelConfig)
			.where(NotifyChannelConfig.guild_id == guild_id)
			.order_by(NotifyChannelConfig.id.asc())
		)
		result = await self.session.execute(stmt)
		return result.scalars().all()

	async def set_enabled(self, guild_id: int, config_id: int, enabled: bool):
		"""Enable or disable one notification setting in a guild."""
		stmt = (
			update(NotifyChannelConfig)
			.where(
				NotifyChannelConfig.id == config_id,
				NotifyChannelConfig.guild_id == guild_id,
			)
			.values(enabled=enabled)
		)
		result = await self.session.execute(stmt)
		await self.session.commit()
		return result.rowcount
