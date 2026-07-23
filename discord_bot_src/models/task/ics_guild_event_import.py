from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Text, UniqueConstraint

from models.base import Base, TimestampMixin


class IcsGuildEventImport(Base, TimestampMixin):
	"""ORM model for ICS events imported into Discord guild scheduled events."""

	__tablename__ = "ics_guild_event_import"

	id = Column(Integer, primary_key=True, autoincrement=True)
	guild_id = Column(BigInteger, nullable=False, index=True)
	ics_uid = Column(String(255), nullable=False)
	source_url = Column(Text, nullable=False)
	scheduled_event_id = Column(BigInteger, nullable=True)
	summary = Column(Text, nullable=True)
	start_time = Column(DateTime(timezone=True), nullable=False)

	__table_args__ = (
		UniqueConstraint("guild_id", "ics_uid", name="uq_ics_guild_event_import_guild_uid"),
	)
