from sqlalchemy import (
	Column,
	Integer,
	BigInteger,
	Text,
	Boolean,
	Index
)

from models.base import Base, TimestampMixin, TablenameMixin


class VoiceChannelStatus(Base, TimestampMixin, TablenameMixin):
	"""ORM model for Discord voice state transition logs."""

	__tablename__ = "voice_status_log"
	# =========================
	# PK
	# =========================
	id = Column(Integer, primary_key=True, autoincrement=True)


	# =========================
	# Discord情報
	# =========================
	before_guild_id = Column(BigInteger, nullable=False, index=True)
	after_guild_id = Column(BigInteger, nullable=False, index=True)
	user_id = Column(BigInteger, nullable=False, index=True)

	# =========================
	# 内容
	# =========================
	before_channel_id = Column(BigInteger, index=True)
	after_channel_id = Column(BigInteger, index=True)

	before_mute = Column(Boolean, index=True)
	after_mute = Column(Boolean, index=True)

	before_deaf = Column(Boolean, index=True)
	after_deaf = Column(Boolean, index=True)

	before_video = Column(Boolean, index=True)
	after_video = Column(Boolean, index=True)

	before_stream = Column(Boolean, index=True)
	after_stream = Column(Boolean, index=True)
	# =========================
	# 補助情報
	# =========================

	# =========================
	# インデックス（重要）
	# =========================
	__table_args__ = (
		Index("idx_before_channel_created", "before_channel_id", "created_at"),
		Index("idx_after_channel_created", "after_channel_id", "created_at"),
		Index("idx_user_created", "user_id", "created_at"),
	)
