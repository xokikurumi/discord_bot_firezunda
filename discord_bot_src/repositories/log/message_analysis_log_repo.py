import asyncio

from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError

from models.log.message_analysis_log import MessageAnalysisLog


class MessageAnalysisLogRepository:
	"""Database access for Ollama message analysis logs."""

	def __init__(self, session: AsyncSession):
		"""Store the active SQLAlchemy session."""
		self.session = session

	async def insert_ignore(self, data: dict):
		"""Insert one analysis result while ignoring duplicate message ids."""
		stmt = mysql_insert(MessageAnalysisLog).values(**data).prefix_with("IGNORE")
		for attempt in range(3):
			try:
				result = await self.session.execute(stmt)
				await self.session.commit()
				return result.rowcount > 0
			except OperationalError as e:
				await self.session.rollback()
				if not self.is_retryable_lock_error(e) or attempt >= 2:
					raise
				await self.sleep_before_retry(attempt)
		return False

	async def get_by_message_id(self, message_id: int):
		"""Return one analysis result by Discord message id."""
		stmt = select(MessageAnalysisLog).where(MessageAnalysisLog.message_id == message_id)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none()

	def is_retryable_lock_error(self, error: OperationalError):
		"""Return True for transient MySQL lock errors."""
		code = getattr(error.orig, "args", [None])[0]
		return code in {1205, 1213}

	async def sleep_before_retry(self, attempt: int):
		"""Sleep briefly before retrying a transient database lock error."""
		await asyncio.sleep(0.5 * (attempt + 1))
