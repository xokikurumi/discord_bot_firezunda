import asyncio
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from urllib import request

import discord

import config
import constants
from repositories.base.notify_channel_config_repo import NotifyChannelConfigRepository
from repositories.task.ics_guild_event_config_repo import IcsGuildEventConfigRepository
from repositories.task.ics_guild_event_import_repo import IcsGuildEventImportRepository


JST = timezone(timedelta(hours=9))


@dataclass
class IcsEvent:
	"""Parsed VEVENT data needed to create a Discord scheduled event."""

	uid: str
	summary: str
	description: str
	location: str
	start_time: datetime
	end_time: datetime
	url: str


class IcsGuildEventService:
	"""Download an ICS feed and import future events into guild scheduled events."""

	def __init__(self, bot, session_factory):
		"""Store dependencies and import settings."""
		self.bot = bot
		self.session_factory = session_factory
		self.ics_url = config.ICS_GUILD_EVENT_URL
		self.enabled = config.ICS_GUILD_EVENT_ENABLED
		self.interval_months = config.ICS_GUILD_EVENT_INTERVAL_MONTHS
		self.last_run_key = None

	async def run_forever(self):
		"""Check periodically whether a month-start ICS import should run."""
		if not self.enabled:
			print("ICS guild event importer disabled.")
			return

		await self.bot.wait_until_ready()
		while not self.bot.is_closed():
			now = datetime.now(JST)
			if self.should_run(now):
				self.last_run_key = self.run_key(now)
				await self.import_all_guilds()

			await asyncio.sleep(config.ICS_GUILD_EVENT_CHECK_INTERVAL_SECONDS)

	def should_run(self, now: datetime):
		"""Return True on the first day of an interval month."""
		if now.day != 1:
			return False
		if (now.month - 1) % self.interval_months != 0:
			return False
		return self.last_run_key != self.run_key(now)

	def run_key(self, now: datetime):
		"""Return a unique key for a monthly import run."""
		return f"{now.year:04d}-{now.month:02d}"

	async def import_all_guilds(self):
		"""Download the ICS feed once and import it into opted-in joined guilds."""
		try:
			ics_text = await self.download_ics()
			events = self.parse_ics(ics_text)
			future_events = [event for event in events if event.end_time > datetime.now(JST)]
			for guild in await self.get_enabled_guilds():
				await self.import_guild_events(guild, future_events)
		except Exception as e:
			print(f"[ERROR] ICS guild event import failed: {e}")

	async def import_guild(self, guild):
		"""Download the ICS feed and import it into one opted-in guild."""
		if not await self.is_guild_enabled(guild.id):
			return False

		ics_text = await self.download_ics()
		events = self.parse_ics(ics_text)
		future_events = [event for event in events if event.end_time > datetime.now(JST)]
		await self.import_guild_events(guild, future_events)
		return True

	async def get_enabled_guilds(self):
		"""Return joined guild objects that have enabled ICS imports by command."""
		async with self.session_factory() as session:
			repo = IcsGuildEventConfigRepository(session)
			enabled_guild_ids = set(await repo.list_enabled_guild_ids())
		return [guild for guild in self.bot.guilds if guild.id in enabled_guild_ids]

	async def is_guild_enabled(self, guild_id: int):
		"""Return True when a guild has enabled ICS imports by command."""
		async with self.session_factory() as session:
			repo = IcsGuildEventConfigRepository(session)
			return await repo.is_enabled(guild_id)

	async def set_guild_enabled(self, guild_id: int, enabled: bool):
		"""Enable or disable ICS imports for a guild."""
		async with self.session_factory() as session:
			repo = IcsGuildEventConfigRepository(session)
			await repo.set_enabled(guild_id, enabled)

	async def download_ics(self):
		"""Download the ICS file into memory without keeping a local copy."""
		return await asyncio.to_thread(self._download_ics_sync)

	def _download_ics_sync(self):
		"""Blocking urllib implementation for ICS download."""
		with request.urlopen(self.ics_url, timeout=30) as response:
			return response.read().decode("utf-8", errors="replace")

	async def import_guild_events(self, guild, events):
		"""Create missing scheduled events for one guild."""
		existing_events = await guild.fetch_scheduled_events()
		existing_keys = {
			(self.normalize_name(event.name), event.start_time.astimezone(JST).date())
			for event in existing_events
			if event.start_time is not None
		}

		for event in events:
			if await self.is_imported(guild.id, event.uid):
				continue
			if (self.normalize_name(event.summary), event.start_time.date()) in existing_keys:
				continue

			created_event = await self.create_guild_event(guild, event)
			await self.record_import(guild.id, event, created_event.id)
			await self.notify_sales_event_created(guild, event, created_event)

	async def is_imported(self, guild_id: int, uid: str):
		"""Return True when the event UID has already been recorded for the guild."""
		async with self.session_factory() as session:
			repo = IcsGuildEventImportRepository(session)
			return await repo.exists(guild_id, uid)

	async def record_import(self, guild_id: int, event: IcsEvent, scheduled_event_id: int):
		"""Record a successful scheduled event creation."""
		async with self.session_factory() as session:
			repo = IcsGuildEventImportRepository(session)
			await repo.insert_ignore({
				"guild_id": guild_id,
				"ics_uid": event.uid,
				"source_url": self.ics_url,
				"scheduled_event_id": scheduled_event_id,
				"summary": event.summary,
				"start_time": event.start_time,
			})

	async def create_guild_event(self, guild, event: IcsEvent):
		"""Create one external Discord scheduled event."""
		return await guild.create_scheduled_event(
			name=event.summary[:100],
			start_time=event.start_time,
			end_time=event.end_time,
			entity_type=discord.EntityType.external,
			privacy_level=discord.PrivacyLevel.guild_only,
			location=(event.location or event.url or "TBD")[:100],
			description=self.build_description(event),
			reason="ICS scheduled event import",
		)

	async def notify_sales_event_created(self, guild, event: IcsEvent, scheduled_event):
		"""Notify configured SALES_EVENT channels that a scheduled event was added."""
		async with self.session_factory() as session:
			repo = NotifyChannelConfigRepository(session)
			configs = await repo.get_enabled_by_category(guild.id, constants.CONFIG_MENTION_SALES_EVENT)

		if not configs:
			return

		body = self.build_sales_event_notification(event, scheduled_event)
		for row in configs:
			channel = self.bot.get_channel(row.channel_id)
			if channel is None:
				print(f"[WARN] SALES_EVENT notify channel not found: guild={guild.id} channel={row.channel_id}")
				continue

			message = self.build_mention(row.mention)
			if message:
				message += "\n"
			message += body

			try:
				await channel.send(message)
			except Exception as e:
				print(f"[ERROR] SALES_EVENT notify failed guild={guild.id} channel={row.channel_id}: {e}")

	def build_sales_event_notification(self, event: IcsEvent, scheduled_event):
		"""Build the notification text for a newly created sales event."""
		lines = [
			"即売会イベントをサーバーイベントに追加しました。",
			f"イベント名: {event.summary}",
			f"開始日時: {event.start_time.astimezone(JST).strftime('%Y/%m/%d %H:%M')}",
			f"終了日時: {event.end_time.astimezone(JST).strftime('%Y/%m/%d %H:%M')}",
		]
		if event.location:
			lines.append(f"場所: {event.location}")
		if event.url:
			lines.append(f"URL: {event.url}")

		scheduled_event_url = getattr(scheduled_event, "url", None)
		if scheduled_event_url:
			lines.append(f"Discordイベント: {scheduled_event_url}")
		return "\n".join(lines)

	def build_mention(self, mention):
		"""Build a Discord mention string from database mention settings."""
		if not mention:
			return ""
		mention = str(mention).strip()
		if mention == "everyone":
			return "@everyone"
		if mention == "here":
			return "@here"
		if mention.startswith("<@"):
			return mention
		if mention.isdigit():
			return f"<@&{mention}>"
		return mention

	def build_description(self, event: IcsEvent):
		"""Build a Discord scheduled event description from ICS data."""
		parts = []
		if event.description:
			parts.append(event.description)
		if event.url:
			parts.append(f"URL: {event.url}")
		parts.append(f"ICS UID: {event.uid}")
		return "\n\n".join(parts)[:1000]

	def parse_ics(self, ics_text: str):
		"""Parse VEVENT blocks from an ICS document."""
		lines = self.unfold_ics_lines(ics_text)
		events = []
		current = None
		for line in lines:
			if line == "BEGIN:VEVENT":
				current = {}
				continue
			if line == "END:VEVENT":
				if current:
					event = self.build_event(current)
					if event:
						events.append(event)
				current = None
				continue
			if current is not None and ":" in line:
				name, value = line.split(":", 1)
				key = name.split(";", 1)[0].upper()
				current[key] = self.unescape_ics_value(value)
		return events

	def unfold_ics_lines(self, ics_text: str):
		"""Unfold folded ICS lines that start with a space or tab."""
		raw_lines = ics_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
		lines = []
		for line in raw_lines:
			if line.startswith((" ", "\t")) and lines:
				lines[-1] += line[1:]
			else:
				lines.append(line)
		return lines

	def build_event(self, data: dict):
		"""Convert parsed ICS fields into an IcsEvent object."""
		uid = data.get("UID")
		summary = data.get("SUMMARY")
		start = self.parse_ics_datetime(data.get("DTSTART"))
		if not uid or not summary or not start:
			return None

		end = self.parse_ics_datetime(data.get("DTEND"))
		if end is None or end <= start:
			end = start + timedelta(days=1)

		return IcsEvent(
			uid=uid,
			summary=summary,
			description=data.get("DESCRIPTION", ""),
			location=data.get("LOCATION", ""),
			start_time=start,
			end_time=end,
			url=data.get("URL", ""),
		)

	def parse_ics_datetime(self, value):
		"""Parse common ICS date and datetime values as JST-aware datetimes."""
		if not value:
			return None
		value = value.strip()
		if len(value) == 8:
			day = date.fromisoformat(f"{value[0:4]}-{value[4:6]}-{value[6:8]}")
			return datetime.combine(day, time.min, tzinfo=JST)
		if value.endswith("Z"):
			return datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc).astimezone(JST)
		return datetime.strptime(value, "%Y%m%dT%H%M%S").replace(tzinfo=JST)

	def unescape_ics_value(self, value: str):
		"""Unescape common ICS text escapes."""
		return (
			value.replace("\\n", "\n")
			.replace("\\N", "\n")
			.replace("\\,", ",")
			.replace("\\;", ";")
			.replace("\\\\", "\\")
		)

	def normalize_name(self, name: str):
		"""Normalize event names for duplicate checks."""
		return " ".join((name or "").split()).casefold()
