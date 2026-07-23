from datetime import datetime

from sqlalchemy import distinct, func, select
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.ext.asyncio import AsyncSession

from models.text.geolonia_address import GeoloniaAddress
from models.text.geolonia_sync_state import GeoloniaSyncState


class GeoloniaAddressRepository:
	"""Database access for cached Geolonia Japanese address data."""

	def __init__(self, session: AsyncSession):
		"""Store the active SQLAlchemy session."""
		self.session = session

	async def bulk_upsert_addresses(self, rows: list[dict], batch_size: int = 1000):
		"""Insert or update Geolonia address rows in batches."""
		for index in range(0, len(rows), batch_size):
			batch = rows[index:index + batch_size]
			if not batch:
				continue
			stmt = mysql_insert(GeoloniaAddress).values(batch)
			stmt = stmt.on_duplicate_key_update(
				lat=stmt.inserted.lat,
				lng=stmt.inserted.lng,
				source_updated_at=stmt.inserted.source_updated_at,
			)
			await self.session.execute(stmt)
			await self.session.commit()

	async def list_municipalities(self, prefecture: str):
		"""Return municipality names stored for one prefecture."""
		stmt = (
			select(distinct(GeoloniaAddress.municipality))
			.where(GeoloniaAddress.prefecture == prefecture)
			.order_by(GeoloniaAddress.municipality.asc())
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())

	async def list_municipality_prefectures(self):
		"""Return stored prefecture and municipality pairs."""
		stmt = (
			select(GeoloniaAddress.prefecture, GeoloniaAddress.municipality)
			.distinct()
			.order_by(GeoloniaAddress.municipality.asc(), GeoloniaAddress.prefecture.asc())
		)
		result = await self.session.execute(stmt)
		return list(result.all())

	async def list_towns(self, prefecture: str, municipality: str):
		"""Return town-level rows for one municipality."""
		stmt = (
			select(GeoloniaAddress)
			.where(
				GeoloniaAddress.prefecture == prefecture,
				GeoloniaAddress.municipality == municipality,
			)
			.order_by(GeoloniaAddress.town.asc())
		)
		result = await self.session.execute(stmt)
		return list(result.scalars().all())

	async def city_center(self, prefecture: str, municipality: str):
		"""Return the average representative point for one municipality."""
		stmt = (
			select(func.avg(GeoloniaAddress.lat), func.avg(GeoloniaAddress.lng))
			.where(
				GeoloniaAddress.prefecture == prefecture,
				GeoloniaAddress.municipality == municipality,
			)
		)
		result = await self.session.execute(stmt)
		lat, lng = result.one()
		if lat is None or lng is None:
			return None
		return float(lat), float(lng)

	async def get_last_synced_at(self, name: str):
		"""Return the last sync timestamp for a named sync job."""
		stmt = select(GeoloniaSyncState.last_synced_at).where(GeoloniaSyncState.name == name)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none()

	async def set_last_synced_at(self, name: str, synced_at: datetime):
		"""Upsert the last sync timestamp for a named sync job."""
		stmt = mysql_insert(GeoloniaSyncState).values(name=name, last_synced_at=synced_at)
		stmt = stmt.on_duplicate_key_update(last_synced_at=stmt.inserted.last_synced_at)
		await self.session.execute(stmt)
		await self.session.commit()
