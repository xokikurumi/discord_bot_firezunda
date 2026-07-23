from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.ext.asyncio import AsyncSession

from models.text.jma_shindo_station import JmaShindoStation
from models.text.jma_sync_state import JmaSyncState


class JmaShindoStationRepository:
	"""Database access for cached JMA seismic intensity observation stations."""

	def __init__(self, session: AsyncSession):
		"""Store the active SQLAlchemy session."""
		self.session = session

	async def bulk_upsert_stations(self, rows: list[dict], batch_size: int = 1000):
		"""Insert or update JMA station rows in batches."""
		for index in range(0, len(rows), batch_size):
			batch = rows[index:index + batch_size]
			if not batch:
				continue
			stmt = mysql_insert(JmaShindoStation).values(batch)
			stmt = stmt.on_duplicate_key_update(
				region_name=stmt.inserted.region_name,
				address=stmt.inserted.address,
				observation_start=stmt.inserted.observation_start,
				observation_end=stmt.inserted.observation_end,
				source_updated_at=stmt.inserted.source_updated_at,
			)
			await self.session.execute(stmt)
			await self.session.commit()

	async def list_active_stations(self):
		"""Return active JMA stations used for observation label matching."""
		stmt = (
			select(JmaShindoStation)
			.where(
				(JmaShindoStation.observation_end.is_(None))
				| (JmaShindoStation.observation_end == "")
			)
			.order_by(JmaShindoStation.station_name.asc())
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())

	async def get_last_synced_at(self, name: str):
		"""Return the last sync timestamp for a named sync job."""
		stmt = select(JmaSyncState.last_synced_at).where(JmaSyncState.name == name)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none()

	async def set_last_synced_at(self, name: str, synced_at: datetime):
		"""Upsert the last sync timestamp for a named sync job."""
		stmt = mysql_insert(JmaSyncState).values(name=name, last_synced_at=synced_at)
		stmt = stmt.on_duplicate_key_update(last_synced_at=stmt.inserted.last_synced_at)
		await self.session.execute(stmt)
		await self.session.commit()
