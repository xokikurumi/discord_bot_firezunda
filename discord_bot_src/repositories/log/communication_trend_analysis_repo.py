from sqlalchemy import and_, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.log.communication_trend_analysis import CommunicationTrendAnalysis


class CommunicationTrendAnalysisRepository:
	"""Database access for communication trend analysis reports."""

	def __init__(self, session: AsyncSession):
		"""Store the active SQLAlchemy session."""
		self.session = session

	async def exists(self, period_key: str, scope_type: str, guild_id: int, user_id=None):
		"""Return True when a report already exists for the period and scope."""
		return await self.get(period_key, scope_type, guild_id, user_id) is not None

	async def get(self, period_key: str, scope_type: str, guild_id: int, user_id=None):
		"""Return one report for the period and scope."""
		conditions = [
			CommunicationTrendAnalysis.period_key == period_key,
			CommunicationTrendAnalysis.scope_type == scope_type,
			CommunicationTrendAnalysis.guild_id == guild_id,
		]
		if user_id is None:
			conditions.append(CommunicationTrendAnalysis.user_id.is_(None))
		else:
			conditions.append(CommunicationTrendAnalysis.user_id == user_id)

		stmt = (
			select(CommunicationTrendAnalysis)
			.where(and_(*conditions))
			.order_by(CommunicationTrendAnalysis.id.asc())
			.limit(1)
		)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none()

	async def insert(self, data: dict):
		"""Insert one communication trend report."""
		stmt = insert(CommunicationTrendAnalysis).values(**data)
		await self.session.execute(stmt)
		await self.session.commit()

	async def upsert_by_scope(self, data: dict):
		"""Update an existing report for the scope or insert a new one."""
		existing = await self.get(
			data["period_key"],
			data["scope_type"],
			data["guild_id"],
			data.get("user_id"),
		)
		if existing is None:
			await self.insert(data)
			return

		stmt = (
			update(CommunicationTrendAnalysis)
			.where(CommunicationTrendAnalysis.id == existing.id)
			.values(**data)
		)
		await self.session.execute(stmt)
		await self.session.commit()
