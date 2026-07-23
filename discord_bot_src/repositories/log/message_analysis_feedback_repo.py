from sqlalchemy import desc, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.log.message_analysis_feedback import MessageAnalysisFeedback
from models.log.message_analysis_log import MessageAnalysisLog
from models.log.message_log import MessageLog


class MessageAnalysisFeedbackRepository:
	"""Database access for administrator feedback on message analysis."""

	def __init__(self, session: AsyncSession):
		"""Store the active SQLAlchemy session."""
		self.session = session

	async def insert(self, data: dict):
		"""Insert one feedback row."""
		stmt = insert(MessageAnalysisFeedback).values(**data)
		await self.session.execute(stmt)
		await self.session.commit()

	async def list_recent_rag_candidates(self, guild_id: int, limit: int):
		"""Return recent feedback rows with original message and analysis data."""
		if limit <= 0:
			return []

		stmt = (
			select(MessageAnalysisFeedback, MessageLog, MessageAnalysisLog)
			.join(
				MessageLog,
				MessageLog.message_id == MessageAnalysisFeedback.message_id,
			)
			.outerjoin(
				MessageAnalysisLog,
				MessageAnalysisLog.message_id == MessageAnalysisFeedback.message_id,
			)
			.where(
				MessageAnalysisFeedback.guild_id == guild_id,
				MessageAnalysisFeedback.review_status == "CONFIRMED",
				MessageAnalysisFeedback.corrected_result_json.is_not(None),
				MessageAnalysisFeedback.corrected_result_json != "",
				MessageLog.content.is_not(None),
				MessageLog.content != "",
			)
			.order_by(desc(MessageAnalysisFeedback.created_at), desc(MessageAnalysisFeedback.id))
			.limit(limit)
		)
		result = await self.session.execute(stmt)
		return result.all()
