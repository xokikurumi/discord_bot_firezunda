from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, String

from models.base import Base, TablenameMixin, TimestampMixin


class DiscordChannel(Base, TimestampMixin, TablenameMixin):
	"""ORM model for Discord channels observed by the bot."""

	__tablename__ = "discord_channel"

	id = Column(Integer, primary_key=True, autoincrement=True)
	guild_id = Column(BigInteger, nullable=False, index=True)
	channel_id = Column(BigInteger, nullable=False, index=True)
	name = Column(String(100), nullable=True)
	channel_type = Column(String(50), nullable=True)
	category_id = Column(BigInteger, nullable=True)
	parent_channel_id = Column(BigInteger, nullable=True)
	position = Column(Integer, nullable=True)
	last_seen_at = Column(DateTime(timezone=True), nullable=True)

	__table_args__ = (
		Index("uq_discord_channel_guild_channel", "guild_id", "channel_id", unique=True),
		Index("idx_discord_channel_last_seen", "guild_id", "last_seen_at"),
	)
