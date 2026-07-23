from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.log.message_delete_log import MessageDeleteLog


class MessageDeleteLogRepository:
	"""Database access for message delete history rows."""

	def __init__(self, session: AsyncSession):
		"""Store the active SQLAlchemy session."""
		self.session = session

	# =========================
	# 追加
	# =========================
	async def insert(self, data: dict):
		"""Insert one message delete history row."""
		stmt = insert(MessageDeleteLog).values(**data)
		await self.session.execute(stmt)
		await self.session.commit()

	# =========================
	# 取得（ID）
	# =========================
	async def get_by_message_id(self, message_id: int):
		"""Return delete history rows for a Discord message id, newest first."""
		stmt = (
			select(MessageDeleteLog)
			.where(MessageDeleteLog.message_id == message_id)
			.order_by(MessageDeleteLog.created_at.desc())
		)
		result = await self.session.execute(stmt)
		return result.scalars().all()

	# =========================
	# 荳隕ｧ蜿門ｾ暦ｼ医メ繝｣繝ｳ繝阪Ν・・
	# =========================
	async def get_by_channel(self, channel_id: int, limit: int = 100):
		"""Return recent delete history rows for a Discord channel id."""
		stmt = (
			select(MessageDeleteLog)
			.where(MessageDeleteLog.channel_id == channel_id)
			.order_by(MessageDeleteLog.created_at.desc())
			.limit(limit)
		)
		result = await self.session.execute(stmt)
		return result.scalars().all()
