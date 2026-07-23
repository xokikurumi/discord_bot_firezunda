from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.ext.asyncio import AsyncSession

from models.text.discord_user import DiscordUser


class DiscordUserRepository:
	"""Database access for observed Discord user master rows."""

	def __init__(self, session: AsyncSession):
		"""Store the active SQLAlchemy session."""
		self.session = session

	async def upsert(self, data: dict):
		"""Insert or update one Discord user row."""
		stmt = mysql_insert(DiscordUser).values(**data)
		update_values = {
			"name": stmt.inserted.name,
			"display_name": stmt.inserted.display_name,
			"global_name": stmt.inserted.global_name,
			"discriminator": stmt.inserted.discriminator,
			"bot_flg": stmt.inserted.bot_flg,
			"avatar_url": stmt.inserted.avatar_url,
			"last_seen_at": stmt.inserted.last_seen_at,
		}
		await self.session.execute(stmt.on_duplicate_key_update(**update_values))
		await self.session.commit()
