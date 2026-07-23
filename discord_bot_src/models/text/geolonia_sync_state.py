from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint

from models.base import Base, TimestampMixin


class GeoloniaSyncState(Base, TimestampMixin):
	"""ORM model that stores periodic Geolonia address sync timestamps."""

	__tablename__ = "b_geolonia_sync_state"

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(100), nullable=False)
	last_synced_at = Column(DateTime(timezone=True), nullable=True)

	__table_args__ = (
		UniqueConstraint("name", name="uq_geolonia_sync_state_name"),
	)
