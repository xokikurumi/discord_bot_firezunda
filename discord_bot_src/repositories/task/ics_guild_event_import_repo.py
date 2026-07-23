from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.mysql import insert as mysql_insert

from models.task.ics_guild_event_import import IcsGuildEventImport


class IcsGuildEventImportRepository:
	"""Database access for imported ICS guild scheduled events."""

	def __init__(self, session: AsyncSession):
		"""Store the active SQLAlchemy session."""
		self.session = session

	async def exists(self, guild_id: int, ics_uid: str):
		"""Return True when an ICS UID has already been imported for a guild."""
		stmt = select(IcsGuildEventImport.id).where(
			IcsGuildEventImport.guild_id == guild_id,
			IcsGuildEventImport.ics_uid == ics_uid,
		)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none() is not None

	async def insert_ignore(self, data: dict):
		"""Insert an imported event row while ignoring duplicate guild/UID pairs."""
		stmt = mysql_insert(IcsGuildEventImport).values(**data).prefix_with("IGNORE")
		result = await self.session.execute(stmt)
		await self.session.commit()
		return result.rowcount > 0
