from sqlalchemy import BigInteger, Column, Index, Integer, String, Text

from models.base import Base, TablenameMixin, TimestampMixin


class MessageAnalysisFeedback(Base, TimestampMixin, TablenameMixin):
	"""ORM model for administrator feedback on message analysis results."""

	__tablename__ = "message_analysis_feedback"

	id = Column(Integer, primary_key=True, autoincrement=True)
	message_id = Column(BigInteger, nullable=False, index=True)
	guild_id = Column(BigInteger, nullable=False, index=True)
	channel_id = Column(BigInteger, nullable=True)
	user_id = Column(BigInteger, nullable=True)
	reviewer_id = Column(BigInteger, nullable=False, index=True)
	label = Column(String(30), nullable=False)
	review_status = Column(String(30), nullable=False, default="CONFIRMED")
	corrected_result_json = Column(Text, nullable=True)
	note = Column(Text, nullable=True)

	__table_args__ = (
		Index("idx_message_analysis_feedback_message_created", "message_id", "created_at"),
		Index("idx_message_analysis_feedback_label_created", "label", "created_at"),
		Index("idx_message_analysis_feedback_status_created", "review_status", "created_at"),
	)
