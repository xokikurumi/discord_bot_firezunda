from sqlalchemy import BigInteger, Boolean, Column, Index, Integer, String, Text

from models.base import Base, TablenameMixin, TimestampMixin


class MessageAnalysisWhitelist(Base, TimestampMixin, TablenameMixin):
	"""ORM model for guild-scoped message analysis whitelist rules."""

	__tablename__ = "message_analysis_whitelist"

	id = Column(Integer, primary_key=True, autoincrement=True)
	guild_id = Column(BigInteger, nullable=False, index=True)
	rule_type = Column(String(30), nullable=False)
	pattern = Column(Text, nullable=False)
	created_by = Column(BigInteger, nullable=False, index=True)
	note = Column(Text, nullable=True)
	enabled = Column(Boolean, nullable=False, default=True)

	__table_args__ = (
		Index("idx_message_analysis_whitelist_guild_enabled", "guild_id", "enabled"),
		Index("idx_message_analysis_whitelist_type_created", "rule_type", "created_at"),
	)
