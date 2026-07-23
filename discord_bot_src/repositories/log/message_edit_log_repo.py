from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.log.message_edit_log import MessageEditLog


class MessageEditLogRepository:
    """Database access for message edit history rows."""

    def __init__(self, session: AsyncSession):
        """Store the active SQLAlchemy session."""
        self.session = session

    # =========================
    # 追加
    # =========================
    async def insert(self, data: dict):
        """Insert one message edit history row."""
        stmt = insert(MessageEditLog).values(**data)
        await self.session.execute(stmt)
        await self.session.commit()

    # =========================
    # 取得（ID）
    # =========================
    async def get_by_message_id(self, message_id: int):
        """Return edit history rows for a Discord message id, newest first."""
        stmt = (
            select(MessageEditLog)
            .where(MessageEditLog.message_id == message_id)
            .order_by(MessageEditLog.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    # =========================
    # 一覧取得（チャンネル）
    # =========================
    async def get_by_channel(self, channel_id: int, limit: int = 100):
        """Return recent edit history rows for a Discord channel id."""
        stmt = (
            select(MessageEditLog)
            .where(MessageEditLog.channel_id == channel_id)
            .order_by(MessageEditLog.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
