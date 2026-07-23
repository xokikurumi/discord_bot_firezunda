from sqlalchemy import BigInteger, Boolean, Column, Integer, UniqueConstraint

from models.base import Base, TimestampMixin


class IcsGuildEventConfig(Base, TimestampMixin):
	"""ORM model for guilds that opted in to ICS scheduled event imports."""

	__tablename__ = "ics_guild_event_config"

	id = Column(Integer, primary_key=True, autoincrement=True)
	guild_id = Column(BigInteger, nullable=False, index=True)
	enabled = Column(Boolean, nullable=False, default=False, server_default="0")

	__table_args__ = (
		UniqueConstraint("guild_id", name="uq_ics_guild_event_config_guild_id"),
	)
