from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.task.niconico_info_filter import NiconicoInfoFilter


class NiconicoInfoFilterRepository:
	"""Database access for Niconico Info keyword filters."""

	def __init__(self, session: AsyncSession):
		"""Store the active SQLAlchemy session."""
		self.session = session

	async def insert(self, data: dict):
		"""Insert one filter row."""
		stmt = insert(NiconicoInfoFilter).values(**data)
		await self.session.execute(stmt)
		await self.session.commit()

	async def list_by_guild(self, guild_id: int, enabled_only: bool = False):
		"""Return Niconico Info filters for a guild."""
		stmt = (
			select(NiconicoInfoFilter)
			.where(
				NiconicoInfoFilter.guild_id == guild_id,
				NiconicoInfoFilter.delete_flg.is_(False),
			)
			.order_by(NiconicoInfoFilter.id.asc())
		)
		if enabled_only:
			stmt = stmt.where(NiconicoInfoFilter.enabled.is_(True))
		result = await self.session.execute(stmt)
		return result.scalars().all()

	async def set_enabled(self, guild_id: int, filter_id: int, enabled: bool):
		"""Enable or disable one filter row."""
		stmt = (
			update(NiconicoInfoFilter)
			.where(
				NiconicoInfoFilter.id == filter_id,
				NiconicoInfoFilter.guild_id == guild_id,
				NiconicoInfoFilter.delete_flg.is_(False),
			)
			.values(enabled=enabled)
		)
		result = await self.session.execute(stmt)
		await self.session.commit()
		return result.rowcount

	async def delete(self, guild_id: int, filter_id: int):
		"""Soft-delete one filter row."""
		stmt = (
			update(NiconicoInfoFilter)
			.where(
				NiconicoInfoFilter.id == filter_id,
				NiconicoInfoFilter.guild_id == guild_id,
				NiconicoInfoFilter.delete_flg.is_(False),
			)
			.values(delete_flg=True, enabled=False)
		)
		result = await self.session.execute(stmt)
		await self.session.commit()
		return result.rowcount
