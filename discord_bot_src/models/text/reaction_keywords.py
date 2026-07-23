from sqlalchemy import (
	Column,
	Integer,
	BigInteger,
	Text,
	Boolean,
	Index
)

from models.base import Base, TimestampMixin, TablenameMixin


class ReactionKeywords(Base, TimestampMixin, TablenameMixin):
	"""ORM model for guild-scoped reaction keyword rules."""

	__tablename__ = "b_reaction_keywords"
	# =========================
	# PK
	# =========================
	id = Column(Integer, primary_key=True, autoincrement=True)

	# =========================
	# Discord情報
	# =========================
	guild_id = Column(BigInteger, nullable=False, index=True)


	# =========================
	# 内容
	# =========================
	# content = Column(Text, nullable=True)
	enabled = Column(Boolean, nullable=False)
	keyword = Column(Text, nullable=False)
	reaction = Column(Text, nullable=True)
	reaction_id = Column(BigInteger, nullable=True)
	reaction_animation_flg = Column(Boolean, nullable=True)
	ng_word_flg = Column(Boolean, nullable=True)

	# =========================
	# 補助情報
	# =========================
	delete_flg = Column(Boolean, nullable=True)

	# =========================
	# インデックス（重要）
	# =========================
	# __table_args__ = (
	# 	Index("idx_channel_created", "channel_id", "created_at"),
	# 	Index("idx_user_created", "user_id", "created_at"),
	# )
