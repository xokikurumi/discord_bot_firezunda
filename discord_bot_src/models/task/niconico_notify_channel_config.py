from sqlalchemy import BigInteger, Boolean, Column, Integer, Text

from models.base import Base


class NiconicoNotifyChannelConfig(Base):
	"""ORM model for legacy per-user Niconico notification channel settings."""

	__tablename__ = "b_niconico_notify_cannel_config"

	id = Column(Integer, primary_key=True, autoincrement=True)
	user_id = Column(BigInteger, nullable=False, index=True)
	guild_id = Column(BigInteger, nullable=True, index=True)
	channel_id = Column(BigInteger, nullable=False)
	enabled = Column(Boolean, nullable=False, default=True)
	mention = Column(Text, nullable=True)
