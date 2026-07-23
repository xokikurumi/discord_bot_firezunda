from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String, Text, func

from models.base import Base


class NiconicoInfoFilter(Base):
	"""ORM model for guild-scoped Niconico Info keyword filters."""

	__tablename__ = "niconico_info_filter"

	id = Column(Integer, primary_key=True, autoincrement=True)
	guild_id = Column(BigInteger, nullable=False, index=True)
	mode = Column(String(20), nullable=False, default="include", index=True)
	keyword = Column(Text, nullable=False)
	enabled = Column(Boolean, nullable=False, default=True, index=True)
	delete_flg = Column(Boolean, nullable=False, default=False, index=True)
	created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
