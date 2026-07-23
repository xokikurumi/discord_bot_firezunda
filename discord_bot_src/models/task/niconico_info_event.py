from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text, func

from models.base import Base


class NiconicoInfoEvent(Base):
	"""ORM model for Niconico info/posting festival events."""

	__tablename__ = "niconico_info_event"

	id = Column(Integer, primary_key=True, autoincrement=True)
	source_key = Column(String(255), nullable=False, unique=True, index=True)
	title = Column(Text, nullable=False)
	start_date = Column(Date, nullable=True)
	end_date = Column(Date, nullable=True)
	date_text = Column(Text, nullable=True)
	explanation = Column(Text, nullable=True)
	link = Column(Text, nullable=True)
	organizer_user = Column(Text, nullable=True)
	organizer_link = Column(Text, nullable=True)
	categories = Column(Text, nullable=True)
	source_url = Column(Text, nullable=True)
	send_flg = Column(Boolean, nullable=False, default=False, index=True)
	delete_flg = Column(Boolean, nullable=False, default=False, index=True)
	created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
