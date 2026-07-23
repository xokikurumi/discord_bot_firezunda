from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    Text,
    Boolean,
    Index
)

from models.base import Base, TimestampMixin, TablenameMixin


class MessageDeleteLog(Base, TimestampMixin, TablenameMixin):
    """ORM model for Discord message delete history."""

    __tablename__ = "message_delete_log"
    # =========================
    # PK
    # =========================
    id = Column(Integer, primary_key=True, autoincrement=True)

    # =========================
    # Discord情報
    # =========================
    message_id = Column(BigInteger, nullable=False, index=True)
    guild_id = Column(BigInteger, nullable=True, index=True)
    channel_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=True, index=True)

    # =========================
    # 蜀・ｮｹ
    # =========================
    content = Column(Text, nullable=True)
    bot_flg = Column(Boolean, nullable=True)
    has_attachments = Column(Boolean, nullable=True)
    has_embeds = Column(Boolean, nullable=True)

    # =========================
    # インデックス（重要）
    # =========================
    __table_args__ = (
        Index("idx_message_delete_message_created", "message_id", "created_at"),
        Index("idx_message_delete_channel_created", "channel_id", "created_at"),
        Index("idx_message_delete_user_created", "user_id", "created_at"),
    )
