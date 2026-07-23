from sqlalchemy import Column, DateTime, Float, Integer, String, UniqueConstraint

from models.base import Base, TimestampMixin


class GeoloniaAddress(Base, TimestampMixin):
	"""ORM model for Geolonia Japanese address representative points."""

	__tablename__ = "b_geolonia_address"

	id = Column(Integer, primary_key=True, autoincrement=True)
	prefecture = Column(String(50), nullable=False, index=True)
	municipality = Column(String(100), nullable=False, index=True)
	town = Column(String(150), nullable=False, index=True)
	lat = Column(Float, nullable=False)
	lng = Column(Float, nullable=False)
	source_updated_at = Column(DateTime(timezone=True), nullable=True)

	__table_args__ = (
		UniqueConstraint("prefecture", "municipality", "town", name="uq_geolonia_address"),
	)
