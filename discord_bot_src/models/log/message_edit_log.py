from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    Text,
    Boolean,
    Index
)

from models.base import Base, TimestampMixin, TablenameMixin


class MessageEditLog(Base, TimestampMixin, TablenameMixin):
    """ORM model for Discord message edit history."""

    __tablename__ = "message_edit_log"
    # =========================
    # PK
    # =========================
    id = Column(Integer, primary_key=True, autoincrement=True)

    # =========================
    # Discord情報
    # =========================
    message_id = Column(BigInteger, nullable=False, index=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    channel_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)

    # =========================
    # 内容
    # =========================
    before_content = Column(Text, nullable=True)
    after_content = Column(Text, nullable=True)

    # =========================
    # インデックス（重要）
    # =========================
    __table_args__ = (
        Index("idx_message_edit_message_created", "message_id", "created_at"),
        Index("idx_message_edit_channel_created", "channel_id", "created_at"),
        Index("idx_message_edit_user_created", "user_id", "created_at"),
    )
