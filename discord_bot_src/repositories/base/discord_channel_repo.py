from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.ext.asyncio import AsyncSession

from models.text.discord_channel import DiscordChannel


class DiscordChannelRepository:
	"""Database access for observed Discord channel master rows."""

	def __init__(self, session: AsyncSession):
		"""Store the active SQLAlchemy session."""
		self.session = session

	async def upsert(self, data: dict):
		"""Insert or update one Discord channel row."""
		stmt = mysql_insert(DiscordChannel).values(**data)
		update_values = {
			"name": stmt.inserted.name,
			"channel_type": stmt.inserted.channel_type,
			"category_id": stmt.inserted.category_id,
			"parent_channel_id": stmt.inserted.parent_channel_id,
			"position": stmt.inserted.position,
			"last_seen_at": stmt.inserted.last_seen_at,
		}
		await self.session.execute(stmt.on_duplicate_key_update(**update_values))
		await self.session.commit()
