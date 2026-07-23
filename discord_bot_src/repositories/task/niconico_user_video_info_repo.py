from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.task.niconico_user_video_info import NiconicoUserVideoInfo


class NiconicoUserVideoInfoRepository:
	"""Database access for monitored Niconico user ids."""

	def __init__(self, session: AsyncSession):
		"""Store the active SQLAlchemy session."""
		self.session = session

	async def list_enabled_user_ids(self):
		"""Return Niconico user ids that should be checked."""
		stmt = (
			select(NiconicoUserVideoInfo.user_id)
			.where(NiconicoUserVideoInfo.delete_flg.is_(False))
			.order_by(NiconicoUserVideoInfo.id.asc())
		)
		result = await self.session.execute(stmt)
		return result.scalars().all()

	async def add(self, user_id: int):
		"""Add one monitored Niconico user id."""
		stmt = insert(NiconicoUserVideoInfo).values(user_id=user_id, delete_flg=False)
		await self.session.execute(stmt)
		await self.session.commit()

	async def disable(self, row_id: int):
		"""Soft-delete one monitored Niconico user row."""
		stmt = (
			update(NiconicoUserVideoInfo)
			.where(NiconicoUserVideoInfo.id == row_id)
			.values(delete_flg=True)
		)
		result = await self.session.execute(stmt)
		await self.session.commit()
		return result.rowcount

	async def list_enabled(self):
		"""Return active monitored Niconico user rows."""
		stmt = (
			select(NiconicoUserVideoInfo)
			.where(NiconicoUserVideoInfo.delete_flg.is_(False))
			.order_by(NiconicoUserVideoInfo.id.asc())
		)
		result = await self.session.execute(stmt)
		return result.scalars().all()
