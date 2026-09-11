from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.log.message_analysis_whitelist import MessageAnalysisWhitelist


class MessageAnalysisWhitelistRepository:
	"""Database access for message analysis whitelist rules."""

	def __init__(self, session: AsyncSession):
		"""Store the active SQLAlchemy session."""
		self.session = session

	async def insert(self, data: dict):
		"""Insert one whitelist rule."""
		stmt = insert(MessageAnalysisWhitelist).values(**data)
		await self.session.execute(stmt)
		await self.session.commit()

	async def list_by_guild(self, guild_id: int, include_disabled: bool = False):
		"""Return whitelist rules for one guild."""
		conditions = [MessageAnalysisWhitelist.guild_id == guild_id]
		if not include_disabled:
			conditions.append(MessageAnalysisWhitelist.enabled.is_(True))
		stmt = (
			select(MessageAnalysisWhitelist)
			.where(*conditions)
			.order_by(MessageAnalysisWhitelist.id.asc())
		)
		result = await self.session.execute(stmt)
		return result.scalars().all()

	async def set_enabled(self, guild_id: int, rule_id: int, enabled: bool):
		"""Enable or disable one whitelist rule."""
		stmt = (
			update(MessageAnalysisWhitelist)
			.where(
				MessageAnalysisWhitelist.guild_id == guild_id,
				MessageAnalysisWhitelist.id == rule_id,
			)
			.values(enabled=enabled)
		)
		result = await self.session.execute(stmt)
		await self.session.commit()
		return result.rowcount
