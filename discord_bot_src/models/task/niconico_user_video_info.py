from sqlalchemy import BigInteger, Boolean, Column, Integer

from models.base import Base


class NiconicoUserVideoInfo(Base):
	"""ORM model for Niconico users monitored for uploaded videos."""

	__tablename__ = "b_m_niconico_video_infomation"

	id = Column(Integer, primary_key=True, autoincrement=True)
	user_id = Column(BigInteger, nullable=False, index=True)
	delete_flg = Column(Boolean, nullable=False, default=False, index=True)
