import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
import re
from urllib import request
from urllib.parse import urljoin

from bs4 import BeautifulSoup

import config
from repositories.task.niconico_notify_channel_config_repo import NiconicoNotifyChannelConfigRepository
from repositories.task.niconico_user_video_info_repo import NiconicoUserVideoInfoRepository
from repositories.task.niconico_video_send_log_repo import NiconicoVideoSendLogRepository


@dataclass
class NiconicoVideo:
	"""Niconico video data needed to notify Discord about an uploaded video."""

	user_id: int
	title: str
	link: str
	pub_date: str


class NiconicoUserVideoService:
	"""Check Niconico user videos through nvapi and notify Discord about new uploads."""

	JST = timezone(timedelta(hours=9))

	def __init__(self, bot, session_factory):
		"""Store dependencies and polling settings."""
		self.bot = bot
		self.session_factory = session_factory
		self.enabled = config.NICONICO_USER_VIDEO_ENABLED
		self.check_interval_seconds = 15 * 60

	async def run_forever(self):
		"""Poll Niconico user videos at quarter-hour clock boundaries."""
		if not self.enabled:
			print("Niconico user video notifier disabled.")
			return

		await self.bot.wait_until_ready()
		while not self.bot.is_closed():
			await asyncio.sleep(self.seconds_until_next_check())
			await self.check_once()

	def seconds_until_next_check(self):
		"""Return seconds until the next n:00/n:15/n:30/n:45 scheduled run."""
		now = datetime.now()
		elapsed = now.minute * 60 + now.second + now.microsecond / 1_000_000
		interval = max(1, self.check_interval_seconds)
		remainder = elapsed % interval
		if remainder == 0:
			return 0
		return interval - remainder

	async def check_once(self):
		"""Fetch latest videos for monitored users, record new rows, and notify."""
		try:
			await self.discover_latest_videos()
			await self.notify_unsent_videos()
		except Exception as e:
			print(f"[ERROR] Niconico user video check failed: {e}")

	async def discover_latest_videos(self):
		"""Record the latest uploaded video for each monitored user when it is new."""
		async with self.session_factory() as session:
			user_repo = NiconicoUserVideoInfoRepository(session)
			user_ids = await user_repo.list_enabled_user_ids()

		for user_id in user_ids:
			try:
				videos = await self.get_latest_videos(user_id)
			except Exception as e:
				print(f"[ERROR] Niconico user video fetch failed user_id={user_id}: {e}")
				continue

			if not videos:
				continue

			for video in videos:
				async with self.session_factory() as session:
					log_repo = NiconicoVideoSendLogRepository(session)
					if await log_repo.exists_link(video.link):
						continue
					await log_repo.insert({
						"user_id": video.user_id,
						"link": video.link,
						"title": video.title,
						"pub_date": video.pub_date,
						"send_flg": False,
					})
					print(f"Niconico video discovered user_id={video.user_id}: {video.title}")

	async def add_monitored_user(self, user_id: int):
		"""Add a Niconico user id to the monitored list."""
		async with self.session_factory() as session:
			repo = NiconicoUserVideoInfoRepository(session)
			await repo.add(user_id)

	async def disable_monitored_user(self, row_id: int):
		"""Disable a monitored Niconico user row by database id."""
		async with self.session_factory() as session:
			repo = NiconicoUserVideoInfoRepository(session)
			return await repo.disable(row_id)

	async def list_monitored_users(self):
		"""Return active monitored Niconico user rows."""
		async with self.session_factory() as session:
			repo = NiconicoUserVideoInfoRepository(session)
			return await repo.list_enabled()

	async def add_notify_config(self, guild_id: int, user_id: int, channel_id: int, mention: str = ""):
		"""Register a notification channel setting for one Niconico user."""
		async with self.session_factory() as session:
			repo = NiconicoNotifyChannelConfigRepository(session)
			await repo.insert({
				"user_id": user_id,
				"guild_id": guild_id,
				"channel_id": channel_id,
				"enabled": True,
				"mention": mention,
			})

	async def list_notify_configs(self, guild_id: int):
		"""Return Niconico notification settings for one Discord guild."""
		async with self.session_factory() as session:
			repo = NiconicoNotifyChannelConfigRepository(session)
			return await repo.list_by_guild(guild_id)

	async def set_notify_config_enabled(self, guild_id: int, config_id: int, enabled: bool):
		"""Enable or disable one Niconico notification setting."""
		async with self.session_factory() as session:
			repo = NiconicoNotifyChannelConfigRepository(session)
			return await repo.set_enabled(guild_id, config_id, enabled)

	async def notify_unsent_videos(self):
		"""Send all unsent discovered videos to configured notification channels."""
		async with self.session_factory() as session:
			log_repo = NiconicoVideoSendLogRepository(session)
			rows = await log_repo.list_unsent()

		for row in rows:
			notified = await self.notify_video(row)
			if notified:
				async with self.session_factory() as session:
					log_repo = NiconicoVideoSendLogRepository(session)
					await log_repo.mark_sent(row.id)

	async def notify_video(self, row):
		"""Notify every guild channel configured for Niconico user uploads."""
		notified = False
		body = self.build_notification(row)
		for guild in self.bot.guilds:
			async with self.session_factory() as session:
				repo = NiconicoNotifyChannelConfigRepository(session)
				configs = await repo.get_enabled_by_guild_and_user(guild.id, row.user_id)

			sent_channel_keys = set()
			for config_row in configs:
				channel_key = (config_row.channel_id, str(config_row.mention or ""))
				if channel_key in sent_channel_keys:
					continue
				sent_channel_keys.add(channel_key)

				channel = self.bot.get_channel(config_row.channel_id)
				if channel is None:
					print(
						"[WARN] Niconico notify channel not found: "
						f"guild={guild.id} channel={config_row.channel_id}"
					)
					continue

				message = self.build_mention(config_row.mention)
				if message:
					message += "\n"
				message += body

				try:
					await channel.send(message)
					notified = True
				except Exception as e:
					print(
						"[ERROR] Niconico notify failed "
						f"guild={guild.id} channel={config_row.channel_id}: {e}"
					)
		return notified

	async def get_latest_video(self, user_id: int):
		"""Download and parse the latest uploaded video item for a Niconico user."""
		videos = await self.get_latest_videos(user_id)
		return videos[0] if videos else None

	async def get_latest_videos(self, user_id: int):
		"""Download latest regular and short video items for a Niconico user."""
		return await asyncio.to_thread(self._get_latest_videos_sync, user_id)

	def _get_latest_video_sync(self, user_id: int):
		"""Blocking Niconico latest video lookup implementation."""
		return self._get_latest_video_from_api_sync(user_id)

	def _get_latest_videos_sync(self, user_id: int):
		"""Blocking Niconico latest video and shorts lookup implementation."""
		videos = []
		errors = []
		for fetcher in (
			self._get_latest_video_from_api_sync,
			self._get_latest_short_from_page_sync,
		):
			try:
				video = fetcher(user_id)
				if video:
					videos.append(video)
			except Exception as e:
				errors.append(e)
				print(f"[WARN] Niconico user video source failed user_id={user_id}: {e}")

		if not videos and errors:
			raise errors[-1]

		return sorted(videos, key=lambda item: self.pub_date_sort_key(item.pub_date), reverse=True)

	def _get_latest_video_from_api_sync(self, user_id: int):
		"""Blocking nvapi lookup for a user's latest uploaded video."""
		api_url = (
			f"https://nvapi.nicovideo.jp/v2/users/{user_id}/videos"
			"?sortKey=registeredAt&sortOrder=desc&pageSize=1&page=1"
		)
		req = request.Request(
			api_url,
			headers={
				"User-Agent": "discord_bot_v3",
				"X-Frontend-Id": "6",
				"X-Frontend-Version": "0",
			},
		)
		with request.urlopen(req, timeout=30) as response:
			payload = json.loads(response.read().decode("utf-8", errors="replace"))

		items = payload.get("data", {}).get("items", [])
		if not items:
			return None

		essential = items[0].get("essential", {})
		video_id = essential.get("id")
		title = essential.get("title")
		if not video_id or not title:
			return None

		return NiconicoVideo(
			user_id=int(user_id),
			title=title,
			link=f"https://www.nicovideo.jp/watch/{video_id}",
			pub_date=essential.get("registeredAt", ""),
		)

	def _get_latest_short_from_page_sync(self, user_id: int):
		"""Blocking lookup for a user's latest short video from the shorts page."""
		shorts_url = f"https://www.nicovideo.jp/user/{user_id}/shorts"
		req = request.Request(
			shorts_url,
			headers={
				"User-Agent": "discord_bot_v3",
				"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
			},
		)
		with request.urlopen(req, timeout=30) as response:
			html = response.read().decode("utf-8", errors="replace")

		candidates = self.extract_short_video_candidates(user_id, shorts_url, html)
		if not candidates:
			return None
		return max(candidates, key=lambda item: self.pub_date_sort_key(item.pub_date))

	def extract_short_video_candidates(self, user_id: int, page_url: str, html: str):
		"""Extract short video candidates from embedded JSON and page links."""
		candidates = {}
		soup = BeautifulSoup(html, "html.parser")

		for script in soup.find_all("script"):
			text = script.string or script.get_text() or ""
			text = text.strip()
			if not text:
				continue
			for payload in self.extract_json_payloads(text):
				for video in self.extract_videos_from_json(user_id, payload):
					candidates[video.link] = video

		for element in soup.find_all(attrs={"data-initial-data": True}):
			text = element.get("data-initial-data", "").strip()
			for payload in self.extract_json_payloads(text):
				for video in self.extract_videos_from_json(user_id, payload):
					candidates[video.link] = video

		for anchor in soup.find_all("a", href=True):
			href = anchor.get("href", "")
			video_id = self.extract_niconico_video_id(href)
			if not video_id:
				continue
			title = (anchor.get("title") or anchor.get_text(" ", strip=True) or video_id).strip()
			pub_date = self.find_nearby_datetime(anchor)
			link = urljoin(page_url, href)
			if "/watch/" not in link:
				link = f"https://www.nicovideo.jp/watch/{video_id}"
			candidates[link] = NiconicoVideo(
				user_id=int(user_id),
				title=title,
				link=link,
				pub_date=pub_date,
			)

		return list(candidates.values())

	def extract_json_payloads(self, text: str):
		"""Return JSON payloads found in one script block."""
		payloads = []
		try:
			payloads.append(json.loads(text))
			return payloads
		except json.JSONDecodeError:
			pass

		for match in re.finditer(r"\{.*?(?:sm|so|nm|ss)\d+.*?\}", text):
			try:
				payloads.append(json.loads(match.group(0)))
			except json.JSONDecodeError:
				continue
		return payloads

	def extract_videos_from_json(self, user_id: int, payload):
		"""Recursively extract Niconico video-like dictionaries from JSON data."""
		videos = []
		if isinstance(payload, dict):
			video_id = (
				payload.get("id")
				or payload.get("videoId")
				or payload.get("contentId")
				or payload.get("watchId")
			)
			if isinstance(video_id, str):
				video_id = self.extract_niconico_video_id(video_id)
			title = payload.get("title") or payload.get("name")
			pub_date = (
				payload.get("registeredAt")
				or payload.get("createdAt")
				or payload.get("publishedAt")
				or payload.get("uploadTime")
				or payload.get("datePublished")
			)
			if video_id and title:
				videos.append(NiconicoVideo(
					user_id=int(user_id),
					title=str(title),
					link=f"https://www.nicovideo.jp/watch/{video_id}",
					pub_date=str(pub_date or ""),
				))

			for value in payload.values():
				videos.extend(self.extract_videos_from_json(user_id, value))
		elif isinstance(payload, list):
			for item in payload:
				videos.extend(self.extract_videos_from_json(user_id, item))
		return videos

	def extract_niconico_video_id(self, value: str):
		"""Extract a Niconico video id from a URL or text."""
		match = re.search(r"(?:sm|so|nm|ss)\d+", value or "")
		return match.group(0) if match else ""

	def find_nearby_datetime(self, element):
		"""Find a datetime-like string near one anchor element."""
		for target in [element, *element.parents]:
			if target is None:
				continue
			time_tag = target.find("time") if hasattr(target, "find") else None
			if time_tag:
				value = time_tag.get("datetime") or time_tag.get_text(" ", strip=True)
				if value:
					return value
		return ""

	def pub_date_sort_key(self, value: str):
		"""Return a sortable datetime for a Niconico publication date."""
		text = str(value or "").strip()
		if not text:
			return datetime.min.replace(tzinfo=timezone.utc)
		try:
			normalized = text.replace("Z", "+00:00")
			parsed = datetime.fromisoformat(normalized)
			if parsed.tzinfo is None:
				parsed = parsed.replace(tzinfo=timezone.utc)
			return parsed
		except ValueError:
			return datetime.min.replace(tzinfo=timezone.utc)

	def build_notification(self, row):
		"""Build the Discord message body for a new Niconico video."""
		lines = [
			"\u30cb\u30b3\u30cb\u30b3\u52d5\u753b\u306b\u65b0\u3057\u3044\u52d5\u753b\u304c\u6295\u7a3f\u3055\u308c\u307e\u3057\u305f\u3002",
			# f"\u6295\u7a3f\u30e6\u30fc\u30b6\u30fcID: {row.user_id}",
			f"\u30bf\u30a4\u30c8\u30eb: {row.title}",
		]
		if row.pub_date:
			lines.append(f"\u6295\u7a3f\u6642\u9593: {self.format_pub_date_jst(row.pub_date)}")
		lines.append(row.link)
		return "\n".join(lines)

	def format_pub_date_jst(self, value: str):
		"""Format an API datetime as Japan time for Discord notifications."""
		text = str(value or "").strip()
		if not text:
			return ""
		try:
			normalized = text.replace("Z", "+00:00")
			parsed = datetime.fromisoformat(normalized)
			if parsed.tzinfo is None:
				parsed = parsed.replace(tzinfo=timezone.utc)
			return parsed.astimezone(self.JST).strftime("%Y/%m/%d %H:%M:%S")
		except ValueError:
			return text

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
