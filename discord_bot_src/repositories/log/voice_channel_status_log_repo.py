from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.log.voice_channel_status_log import VoiceChannelStatus


class VoiceChannelStatusRepository:
    """Database access for voice channel status log rows."""

    def __init__(self, session: AsyncSession):
        """Store the active SQLAlchemy session."""
        self.session = session

    # =========================
    # 追加
    # =========================
    async def insert(self, data: dict):
        """Insert one voice state transition row."""
        stmt = insert(VoiceChannelStatus).values(**data)
        await self.session.execute(stmt)
        await self.session.commit()

    # =========================
    # 取得（ID）
    # =========================
    async def get_by_message_id(self, message_id: int):
        """Return one voice log row by message id if available."""
        stmt = select(VoiceChannelStatus).where(
            VoiceChannelStatus.message_id == message_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # =========================
    # 一覧取得（チャンネル）
    # =========================
    async def get_by_channel(self, channel_id: int, limit: int = 100):
        """Return recent voice log rows for a channel id if available."""
        stmt = (
            select(VoiceChannelStatus)
            .where(VoiceChannelStatus.channel_id == channel_id)
            .order_by(VoiceChannelStatus.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
