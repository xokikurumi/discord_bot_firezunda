from sqlalchemy import BigInteger, Boolean, Column, Integer, String, Text

from models.base import Base


class NotifyChannelConfig(Base):
	"""ORM model for guild notification channel settings."""

	__tablename__ = "b_notify_cannel_config"

	id = Column(Integer, primary_key=True, autoincrement=True)
	category = Column(String(50), nullable=False, index=True)
	guild_id = Column(BigInteger, nullable=True, index=True)
	channel_id = Column(BigInteger, nullable=False)
	enabled = Column(Boolean, nullable=False, default=True)
	mention = Column(Text, nullable=True)
