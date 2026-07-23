from sqlalchemy import insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.text.reaction_keywords import ReactionKeywords


class ReactionKeyworkdsRepository:
	"""Database access for guild-scoped reaction keyword rules."""

	def __init__(self, session: AsyncSession):
		"""Store the active SQLAlchemy session."""
		self.session = session

	# =========================
	# 追加
	# =========================
	async def insert(self, data: dict):
		"""Insert a new reaction keyword row."""
		# Store a reaction rule for one guild.
		stmt = insert(ReactionKeywords).values(**data)
		await self.session.execute(stmt)
		await self.session.commit()

	async def soft_delete(self, guild_id: int, keyword: str):
		"""Mark matching keyword rows as deleted and disabled."""
		# Preserve rule history while preventing future matches.
		stmt = (
			update(ReactionKeywords)
			.where(
				ReactionKeywords.guild_id == guild_id,
				ReactionKeywords.keyword == keyword,
				ReactionKeywords.delete_flg.isnot(True)
			)
			.values(delete_flg=True, enabled=False)
		)
		result = await self.session.execute(stmt)
		await self.session.commit()
		return result.rowcount

	async def list_by_guild(self, guild_id: int):
		"""Return non-deleted keyword rows for one guild."""
		# Show rules that still belong to the current guild and are not deleted.
		stmt = (
			select(ReactionKeywords)
			.where(
				ReactionKeywords.guild_id == guild_id,
				ReactionKeywords.delete_flg.isnot(True)
			)
			.order_by(ReactionKeywords.id.asc())
		)
		result = await self.session.execute(stmt)
		return result.scalars().all()

	# =========================
	# 取得（ID）
	# =========================
	async def getReactions(self, guild_id: int, ng_word_flg: bool):
		"""Return enabled keyword rules for reaction matching."""
		# NULL ng_word_flg is treated as a normal reaction for older rows.
		conditions = [
			ReactionKeywords.enabled.is_(True),
			ReactionKeywords.delete_flg.isnot(True),
			ReactionKeywords.guild_id == guild_id,
		]
		if ng_word_flg:
			conditions.append(ReactionKeywords.ng_word_flg.is_(True))
		else:
			conditions.append(
				or_(
					ReactionKeywords.ng_word_flg.is_(False),
					ReactionKeywords.ng_word_flg.is_(None),
				)
			)

		stmt = select(ReactionKeywords).where(*conditions)
		result = await self.session.execute(stmt)
		return result.scalars().all()
