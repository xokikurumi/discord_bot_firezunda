from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String, Text, func

from models.base import Base


class NiconicoVideoSendLog(Base):
	"""ORM model for Niconico uploaded videos already discovered or notified."""

	__tablename__ = "b_niconico_video_send_log"

	id = Column(Integer, primary_key=True, autoincrement=True)
	user_id = Column(BigInteger, nullable=False, index=True)
	link = Column(Text, nullable=False)
	title = Column(Text, nullable=False)
	pub_date = Column(String(100), nullable=True)
	send_flg = Column(Boolean, nullable=False, default=False, index=True)
	delete_flg = Column(Boolean, nullable=False, default=False, index=True)
	created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
