from sqlalchemy import BigInteger, Boolean, Column, DateTime, Index, Integer, String

from models.base import Base, TablenameMixin, TimestampMixin


class DiscordUser(Base, TimestampMixin, TablenameMixin):
	"""ORM model for Discord users observed by the bot."""

	__tablename__ = "discord_user"

	id = Column(Integer, primary_key=True, autoincrement=True)
	guild_id = Column(BigInteger, nullable=False, index=True)
	user_id = Column(BigInteger, nullable=False, index=True)
	name = Column(String(100), nullable=True)
	display_name = Column(String(100), nullable=True)
	global_name = Column(String(100), nullable=True)
	discriminator = Column(String(10), nullable=True)
	bot_flg = Column(Boolean, nullable=False, default=False)
	avatar_url = Column(String(500), nullable=True)
	last_seen_at = Column(DateTime(timezone=True), nullable=True)

	__table_args__ = (
		Index("uq_discord_user_guild_user", "guild_id", "user_id", unique=True),
		Index("idx_discord_user_last_seen", "guild_id", "last_seen_at"),
	)
