from sqlalchemy import desc, func, insert, select, update
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

	async def list_confirmed_evaluation_cases(self, guild_id=None, limit: int = 100):
		"""Return administrator-confirmed feedback rows for analysis evaluation."""
		if limit <= 0:
			return []

		conditions = [
			MessageAnalysisFeedback.review_status == "CONFIRMED",
			MessageAnalysisFeedback.corrected_result_json.is_not(None),
			MessageAnalysisFeedback.corrected_result_json != "",
			MessageLog.content.is_not(None),
			MessageLog.content != "",
		]
		if guild_id:
			conditions.append(MessageAnalysisFeedback.guild_id == guild_id)

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
			.where(*conditions)
			.order_by(desc(MessageAnalysisFeedback.created_at), desc(MessageAnalysisFeedback.id))
			.limit(limit)
		)
		result = await self.session.execute(stmt)
		return result.all()

	async def list_embedding_backfill_candidates(
		self,
		guild_id=None,
		limit: int = 100,
		force: bool = False,
		before_id: int = 0,
	):
		"""Return confirmed feedback rows that need embedding storage."""
		if limit <= 0:
			return []

		conditions = [
			MessageAnalysisFeedback.review_status == "CONFIRMED",
			MessageAnalysisFeedback.corrected_result_json.is_not(None),
			MessageAnalysisFeedback.corrected_result_json != "",
			MessageLog.content.is_not(None),
			MessageLog.content != "",
		]
		if guild_id:
			conditions.append(MessageAnalysisFeedback.guild_id == guild_id)
		if before_id:
			conditions.append(MessageAnalysisFeedback.id < before_id)
		if not force:
			conditions.append(MessageAnalysisFeedback.embedding_json.is_(None))

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
			.where(*conditions)
			.order_by(desc(MessageAnalysisFeedback.created_at), desc(MessageAnalysisFeedback.id))
			.limit(limit)
		)
		result = await self.session.execute(stmt)
		return result.all()

	async def update_embedding(
		self,
		feedback_id: int,
		embedding_model: str,
		embedding_text_hash: str,
		embedding_dim: int,
		embedding_json: str,
	):
		"""Store embedding data for one feedback row."""
		stmt = (
			update(MessageAnalysisFeedback)
			.where(MessageAnalysisFeedback.id == feedback_id)
			.values(
				embedding_model=embedding_model,
				embedding_text_hash=embedding_text_hash,
				embedding_dim=embedding_dim,
				embedding_json=embedding_json,
			)
		)
		await self.session.execute(stmt)
		await self.session.commit()

	async def find_latest_confirmed_by_content(self, guild_id: int, content: str):
		"""Return the latest confirmed feedback for the same guild and exact message text."""
		normalized_content = (content or "").strip()
		if not normalized_content:
			return None

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
				func.trim(MessageLog.content) == normalized_content,
			)
			.order_by(desc(MessageAnalysisFeedback.created_at), desc(MessageAnalysisFeedback.id))
			.limit(1)
		)
		result = await self.session.execute(stmt)
		return result.first()
