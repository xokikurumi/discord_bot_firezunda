from sqlalchemy import BigInteger, Boolean, Column, Index, Integer, String, Text

from models.base import Base, TablenameMixin, TimestampMixin


class MessageAnalysisLog(Base, TimestampMixin, TablenameMixin):
	"""ORM model for Ollama message analysis results."""

	__tablename__ = "message_analysis_log"

	id = Column(Integer, primary_key=True, autoincrement=True)
	message_id = Column(BigInteger, nullable=False, unique=True)
	guild_id = Column(BigInteger, nullable=False, index=True)
	channel_id = Column(BigInteger, nullable=False, index=True)
	user_id = Column(BigInteger, nullable=False, index=True)

	model = Column(String(100), nullable=False)
	aggression = Column(Integer, nullable=False, default=0)
	intimidation = Column(Integer, nullable=False, default=0)
	insult = Column(Integer, nullable=False, default=0)
	sarcasm = Column(Integer, nullable=False, default=0)
	snide = Column(Integer, nullable=False, default=0)
	discomfort = Column(Integer, nullable=False, default=0)
	max_score = Column(Integer, nullable=False, default=0)
	targeted = Column(Boolean, nullable=False, default=True)
	confidence = Column(Integer, nullable=False, default=100)
	context_dependency = Column(Boolean, nullable=False, default=False)
	reason = Column(Text, nullable=True)
	raw_result = Column(Text, nullable=True)
	prompt_version = Column(String(100), nullable=True)
	prompt_hash = Column(String(64), nullable=True)
	retrieved_rag_cases = Column(Text, nullable=True)

	should_react = Column(Boolean, nullable=False, default=False)
	should_notify = Column(Boolean, nullable=False, default=False)

	__table_args__ = (
		Index("idx_message_analysis_channel_created", "channel_id", "created_at"),
		Index("idx_message_analysis_user_created", "user_id", "created_at"),
		Index("idx_message_analysis_max_score", "max_score", "created_at"),
	)
