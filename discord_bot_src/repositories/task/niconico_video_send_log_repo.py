from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.task.niconico_video_send_log import NiconicoVideoSendLog


class NiconicoVideoSendLogRepository:
	"""Database access for Niconico video discovery and notification logs."""

	def __init__(self, session: AsyncSession):
		"""Store the active SQLAlchemy session."""
		self.session = session

	async def exists_link(self, link: str):
		"""Return True when the video link has already been recorded."""
		stmt = (
			select(NiconicoVideoSendLog.id)
			.where(
				NiconicoVideoSendLog.link == link,
				NiconicoVideoSendLog.delete_flg.is_(False),
			)
			.limit(1)
		)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none() is not None

	async def insert(self, data: dict):
		"""Insert one newly discovered Niconico video log row."""
		stmt = insert(NiconicoVideoSendLog).values(**data)
		result = await self.session.execute(stmt)
		await self.session.commit()
		return result.inserted_primary_key[0]

	async def list_unsent(self, limit: int = 20):
		"""Return discovered Niconico video rows that have not been notified."""
		stmt = (
			select(NiconicoVideoSendLog)
			.where(
				NiconicoVideoSendLog.send_flg.is_(False),
				NiconicoVideoSendLog.delete_flg.is_(False),
			)
			.order_by(NiconicoVideoSendLog.id.asc())
			.limit(limit)
		)
		result = await self.session.execute(stmt)
		return result.scalars().all()

	async def mark_sent(self, row_id: int):
		"""Mark a Niconico video row as notified."""
		stmt = (
			update(NiconicoVideoSendLog)
			.where(NiconicoVideoSendLog.id == row_id)
			.values(send_flg=True)
		)
		await self.session.execute(stmt)
		await self.session.commit()
