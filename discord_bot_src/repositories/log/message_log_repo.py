from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.mysql import insert as mysql_insert

from models.log.message_analysis_log import MessageAnalysisLog
from models.log.message_log import MessageLog


class MessageLogRepository:
    """Database access for stored message create logs."""

    def __init__(self, session: AsyncSession):
        """Store the active SQLAlchemy session."""
        self.session = session

    # =========================
    # 追加
    # =========================
    async def insert(self, data: dict):
        """Insert one realtime message log row."""
        # Realtime logging expects duplicates to surface as database errors.
        stmt = insert(MessageLog).values(**data)
        await self.session.execute(stmt)
        await self.session.commit()

    async def insert_ignore(self, data: dict):
        """Insert one message row while ignoring unique-key duplicates."""
        # Backfill should skip messages already present via the unique message_id.
        stmt = mysql_insert(MessageLog).values(**data).prefix_with("IGNORE")
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    # =========================
    # 取得（ID）
    # =========================
    async def get_by_message_id(self, message_id: int):
        """Return the message log row for a Discord message id."""
        # Used by raw edit recovery to find the original stored message body.
        stmt = select(MessageLog).where(
            MessageLog.message_id == message_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # =========================
    # 一覧取得（チャンネル）
    # =========================
    async def get_by_channel(self, channel_id: int, limit: int = 100):
        """Return recent message log rows for a Discord channel id."""
        # Return recent message logs for channel-scoped inspection.
        stmt = (
            select(MessageLog)
            .where(MessageLog.channel_id == channel_id)
            .order_by(MessageLog.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_recent_context(self, channel_id: int, exclude_message_id: int, limit: int = 10):
        """Return recent channel messages excluding the target message."""
        stmt = (
            select(MessageLog)
            .where(
                MessageLog.channel_id == channel_id,
                MessageLog.message_id != exclude_message_id,
            )
            .order_by(MessageLog.message_created_at.desc(), MessageLog.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(reversed(result.scalars().all()))

    async def list_unanalyzed_analysis_candidates(self, limit: int = 100, after_id: int = 0):
        """Return logged user messages that do not have an analysis result yet."""
        stmt = (
            select(MessageLog)
            .outerjoin(
                MessageAnalysisLog,
                MessageAnalysisLog.message_id == MessageLog.message_id,
            )
            .where(
                MessageLog.id > after_id,
                MessageAnalysisLog.id.is_(None),
                MessageLog.bot_flg.is_(False),
                MessageLog.content.is_not(None),
                MessageLog.content != "",
                MessageLog.content.not_like("!%"),
            )
            .order_by(MessageLog.id.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
