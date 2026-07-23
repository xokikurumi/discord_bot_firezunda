from sqlalchemy import Column, DateTime, Float, Integer, String, Text, UniqueConstraint

from models.base import Base, TimestampMixin


class JmaShindoStation(Base, TimestampMixin):
	"""ORM model for JMA seismic intensity observation stations."""

	__tablename__ = "b_jma_shindo_station"

	id = Column(Integer, primary_key=True, autoincrement=True)
	region_name = Column(String(100), nullable=False, index=True)
	station_name = Column(String(150), nullable=False, index=True)
	address = Column(Text, nullable=True)
	lat = Column(Float, nullable=False)
	lng = Column(Float, nullable=False)
	observation_start = Column(String(20), nullable=True)
	observation_end = Column(String(20), nullable=True, index=True)
	source_updated_at = Column(DateTime(timezone=True), nullable=True)

	__table_args__ = (
		UniqueConstraint("station_name", "lat", "lng", name="uq_jma_shindo_station_name_lat_lng"),
	)
