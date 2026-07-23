from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, String, Text

from models.base import Base, TablenameMixin, TimestampMixin


class CommunicationTrendAnalysis(Base, TimestampMixin, TablenameMixin):
	"""ORM model for semiannual communication trend analysis reports."""

	__tablename__ = "communication_trend_analysis"

	id = Column(Integer, primary_key=True, autoincrement=True)
	period_key = Column(String(20), nullable=False, index=True)
	period_start = Column(DateTime(timezone=True), nullable=False)
	period_end = Column(DateTime(timezone=True), nullable=False)
	scope_type = Column(String(20), nullable=False, index=True)
	guild_id = Column(BigInteger, nullable=False, index=True)
	user_id = Column(BigInteger, nullable=True, index=True)
	model = Column(String(100), nullable=False)

	message_count = Column(Integer, nullable=False, default=0)
	edit_count = Column(Integer, nullable=False, default=0)
	delete_count = Column(Integer, nullable=False, default=0)
	analysis_count = Column(Integer, nullable=False, default=0)
	max_score_avg = Column(Integer, nullable=False, default=0)
	metrics = Column(Text, nullable=True)

	summary = Column(Text, nullable=True)
	tendencies = Column(Text, nullable=True)
	risks = Column(Text, nullable=True)
	recommendations = Column(Text, nullable=True)
	raw_result = Column(Text, nullable=True)

	__table_args__ = (
		Index("idx_comm_trend_period_scope", "period_key", "scope_type", "guild_id", "user_id"),
		Index("idx_comm_trend_guild_created", "guild_id", "created_at"),
		Index("idx_comm_trend_user_created", "user_id", "created_at"),
	)
