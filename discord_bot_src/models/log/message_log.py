from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    Text,
    Boolean,
    DateTime,
    Index
)

from models.base import Base, TimestampMixin, TablenameMixin


class MessageLog(Base, TimestampMixin, TablenameMixin):
    """ORM model for original Discord message logs."""

    __tablename__ = "message_log"
    # =========================
    # PK
    # =========================
    id = Column(Integer, primary_key=True, autoincrement=True)

    # =========================
    # Discord情報
    # =========================
    message_id = Column(BigInteger, nullable=False, unique=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    channel_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    bot_flg = Column(Boolean, nullable=False)

    # =========================
    # 内容
    # =========================
    content = Column(Text, nullable=True)
    message_created_at = Column(DateTime(timezone=True), nullable=True, index=True)

    # =========================
    # 補助情報
    # =========================
    has_attachments = Column(Boolean, default=False, nullable=False)
    has_embeds = Column(Boolean, default=False, nullable=False)
    has_stickers = Column(Boolean, default=False, nullable=False)
    stickers = Column(Text, nullable=True)

    # =========================
    # インデックス（重要）
    # =========================
    __table_args__ = (
        Index("idx_channel_created", "channel_id", "created_at"),
        Index("idx_user_created", "user_id", "created_at"),
        Index("idx_channel_message_created", "channel_id", "message_created_at"),
    )
