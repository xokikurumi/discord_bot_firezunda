from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.task.niconico_info_event import NiconicoInfoEvent


class NiconicoInfoEventRepository:
	"""Database access for Niconico info/posting festival events."""

	def __init__(self, session: AsyncSession):
		"""Store the active SQLAlchemy session."""
		self.session = session

	async def exists_source_key(self, source_key: str):
		"""Return True when an event has already been discovered."""
		stmt = (
			select(NiconicoInfoEvent.id)
			.where(
				NiconicoInfoEvent.source_key == source_key,
				NiconicoInfoEvent.delete_flg.is_(False),
			)
			.limit(1)
		)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none() is not None

	async def insert(self, data: dict):
		"""Insert one newly discovered Niconico info event."""
		stmt = insert(NiconicoInfoEvent).values(**data)
		result = await self.session.execute(stmt)
		await self.session.commit()
		return result.inserted_primary_key[0]

	async def list_unsent(self, limit: int = 20):
		"""Return discovered events that have not been notified."""
		stmt = (
			select(NiconicoInfoEvent)
			.where(
				NiconicoInfoEvent.send_flg.is_(False),
				NiconicoInfoEvent.delete_flg.is_(False),
			)
			.order_by(NiconicoInfoEvent.id.asc())
			.limit(limit)
		)
		result = await self.session.execute(stmt)
		return result.scalars().all()

	async def mark_sent(self, row_id: int):
		"""Mark one event as notified."""
		stmt = (
			update(NiconicoInfoEvent)
			.where(NiconicoInfoEvent.id == row_id)
			.values(send_flg=True)
		)
		await self.session.execute(stmt)
		await self.session.commit()
