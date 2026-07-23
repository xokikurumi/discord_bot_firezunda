import asyncio
from dataclasses import dataclass
from datetime import date
import hashlib
import re
from typing import Optional
from urllib import request

from bs4 import BeautifulSoup

import config
import constants
from repositories.base.notify_channel_config_repo import NotifyChannelConfigRepository
from repositories.task.niconico_info_event_repo import NiconicoInfoEventRepository
from repositories.task.niconico_info_filter_repo import NiconicoInfoFilterRepository


@dataclass
class NiconicoInfoEventData:
	"""Scraped Niconico info/posting festival event data."""

	source_key: str
	title: str
	start_date: Optional[date]
	end_date: Optional[date]
	date_text: str
	explanation: str
	link: str
	organizer_user: str
	organizer_link: str
	categories: list[str]
	source_url: str


class NiconicoInfoService:
	"""Scrape Niconico posting festival info and notify Discord about new items."""

	SUMMARY_MAX_CHARS = 500
	DATE_RANGE_PATTERN = re.compile(
		r"(\d{4})年(\d{1,2})月(\d{1,2})日.*?(\d{4})年(\d{1,2})月(\d{1,2})日"
	)
	BLOG_POST_DATE_PATTERN = re.compile(r"\s+(\d{4}-\d{2}-\d{2})$")
	BLOG_NEWS_LINK_PATTERN = re.compile(r"^https://blog\.nicovideo\.jp/niconews/\d+/?$")

	def __init__(self, bot, session_factory):
		"""Store dependencies and polling settings."""
		self.bot = bot
		self.session_factory = session_factory
		self.enabled = config.NICONICO_INFO_ENABLED
		self.check_interval_seconds = config.NICONICO_INFO_CHECK_INTERVAL_SECONDS
		self.target_urls = config.NICONICO_INFO_TARGET_URLS

	async def run_forever(self):
		"""Poll Niconico info pages until the bot shuts down."""
		if not self.enabled:
			print("Niconico info notifier disabled.")
			return

		await self.bot.wait_until_ready()
		while not self.bot.is_closed():
			await self.check_once()
			await asyncio.sleep(self.check_interval_seconds)

	async def check_once(self):
		"""Scrape events, record new rows, and notify unsent rows."""
		try:
			await self.discover_events()
			await self.notify_unsent_events()
		except Exception as e:
			print(f"[ERROR] Niconico info check failed: {e}")

	async def discover_events(self):
		"""Fetch configured pages and record newly discovered events."""
		events = await self.fetch_events()
		for event in events:
			async with self.session_factory() as session:
				repo = NiconicoInfoEventRepository(session)
				if await repo.exists_source_key(event.source_key):
					continue
				await repo.insert({
					"source_key": event.source_key,
					"title": event.title,
					"start_date": event.start_date,
					"end_date": event.end_date,
					"date_text": event.date_text,
					"explanation": event.explanation,
					"link": event.link,
					"organizer_user": event.organizer_user,
					"organizer_link": event.organizer_link,
					"categories": ", ".join(event.categories),
					"source_url": event.source_url,
					"send_flg": False,
				})
				print(f"Niconico info discovered: {event.title}")

	async def fetch_events(self):
		"""Download and parse all configured Niconico info pages."""
		return await asyncio.to_thread(self._fetch_events_sync)

	def _fetch_events_sync(self):
		"""Blocking downloader and HTML parser for Niconico info pages."""
		events = []
		seen_keys = set()
		for url in self.target_urls:
			try:
				html = self.download_html(url)
			except Exception as e:
				print(f"[WARN] Niconico info fetch failed url={url}: {e}")
				continue
			for event in self.parse_events(html, url):
				if event.source_key in seen_keys:
					continue
				seen_keys.add(event.source_key)
				events.append(event)
		return events

	def download_html(self, url: str):
		"""Download one Niconico info HTML page."""
		req = request.Request(url, headers={"User-Agent": "discord_bot_v3"})
		with request.urlopen(req, timeout=30) as response:
			return response.read().decode("utf-8", errors="replace")

	def parse_events(self, html: str, source_url: str):
		"""Parse event cards from one Niconico info page."""
		soup = BeautifulSoup(html, "html.parser")
		blog_events = self.parse_blog_events(soup, source_url)
		if blog_events:
			return blog_events

		articles = soup.select("div.events-Content ul.sw-List li.list-Item")
		if not articles:
			articles = soup.select("li.list-Item")

		events = []
		for article in articles:
			title = self.text_or_empty(article.select_one("div.item-Info p.title, p.title"))
			if not title:
				continue

			date_text = self.text_or_empty(article.select_one("div.item-Info p.date, p.date"))
			start_date, end_date = self.parse_date_range(date_text)
			explanation = self.text_or_empty(article.select_one("div.item-Info p.text, p.text"))
			organizer = article.select_one("div.item-Info a.text-Link, a.text-Link")
			organizer_user = self.text_or_empty(organizer)
			organizer_link = organizer.get("href", "") if organizer else ""
			link = self.find_event_link(article)
			categories = [
				self.text_or_empty(category)
				for category in article.select("div.item-Info ul.category-List li, ul.category-List li")
				if self.text_or_empty(category)
			]

			events.append(NiconicoInfoEventData(
				source_key=self.build_source_key(title, start_date, end_date, link, organizer_link),
				title=title,
				start_date=start_date,
				end_date=end_date,
				date_text=date_text,
				explanation=explanation,
				link=link,
				organizer_user=organizer_user,
				organizer_link=organizer_link,
				categories=categories,
				source_url=source_url,
			))
		return events

	def parse_blog_events(self, soup, source_url: str):
		"""Parse Niconico Info blog category article links."""
		events = []
		seen_links = set()
		for article in soup.select("li.l-main-list2-item"):
			link_element = article.select_one("a[href]")
			if link_element is None:
				continue

			link = link_element.get("href", "").strip()
			if not self.BLOG_NEWS_LINK_PATTERN.match(link):
				continue
			if link in seen_links:
				continue
			seen_links.add(link)

			title, published_date = self.split_blog_title_and_date(self.text_or_empty(link_element))
			if not title:
				continue

			category = self.get_blog_category_name(soup)
			events.append(NiconicoInfoEventData(
				source_key=self.build_source_key(title, published_date, None, link, ""),
				title=title,
				start_date=published_date,
				end_date=None,
				date_text=published_date.isoformat() if published_date else "",
				explanation="",
				link=link,
				organizer_user="",
				organizer_link="",
				categories=[category] if category else [],
				source_url=source_url,
			))
		return events

	def split_blog_title_and_date(self, text: str):
		"""Split a blog list item into title text and published date."""
		match = self.BLOG_POST_DATE_PATTERN.search(text or "")
		if not match:
			return text, None

		title = text[:match.start()].strip()
		year, month, day = [int(value) for value in match.group(1).split("-")]
		return title, date(year, month, day)

	def get_blog_category_name(self, soup):
		"""Return the current blog category title when present."""
		candidates = [
			soup.select_one(".category-title"),
			soup.select_one("h1"),
			soup.select_one("h2"),
		]
		for candidate in candidates:
			text = self.text_or_empty(candidate)
			if text:
				return text
		return ""

	def find_event_link(self, article):
		"""Return the announcement video/page link from an event card."""
		links = article.select("div.item-Info ul.btn-List a.btn-Link, ul.btn-List a.btn-Link")
		for link in links:
			label = self.text_or_empty(link)
			if "告知動画" in label:
				return link.get("href", "")
		if links:
			return links[0].get("href", "")
		return ""

	def parse_date_range(self, date_text: str):
		"""Parse Japanese date range text into start and end dates."""
		match = self.DATE_RANGE_PATTERN.search(date_text or "")
		if not match:
			return None, None
		values = [int(value) for value in match.groups()]
		return (
			date(values[0], values[1], values[2]),
			date(values[3], values[4], values[5]),
		)

	def build_source_key(self, title: str, start_date, end_date, link: str, organizer_link: str):
		"""Build a stable duplicate key for one scraped event."""
		raw_key = "|".join([
			title or "",
			start_date.isoformat() if start_date else "",
			end_date.isoformat() if end_date else "",
			link or "",
			organizer_link or "",
		])
		return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

	def text_or_empty(self, element):
		"""Return normalized text from a BeautifulSoup element."""
		if element is None:
			return ""
		return " ".join(element.get_text(" ", strip=True).split())

	async def notify_unsent_events(self):
		"""Send all unsent discovered events to configured notification channels."""
		async with self.session_factory() as session:
			repo = NiconicoInfoEventRepository(session)
			rows = await repo.list_unsent()

		for row in rows:
			notified = await self.notify_event(row)
			if notified:
				async with self.session_factory() as session:
					repo = NiconicoInfoEventRepository(session)
					await repo.mark_sent(row.id)

	async def notify_event(self, row):
		"""Notify every guild channel configured for Niconico info events."""
		notified = False
		handled = False
		body = await self.build_notification(row)
		for guild in self.bot.guilds:
			async with self.session_factory() as session:
				notify_repo = NotifyChannelConfigRepository(session)
				filter_repo = NiconicoInfoFilterRepository(session)
				configs = await notify_repo.get_enabled_by_category(
					guild.id,
					constants.CONFIG_MENTION_NICONICO_INFO,
				)
				filters = await filter_repo.list_by_guild(guild.id, enabled_only=True)

			if not configs:
				continue

			handled = True
			if not self.matches_filters(row, filters):
				continue

			for config_row in configs:
				channel = self.bot.get_channel(config_row.channel_id)
				if channel is None:
					print(
						"[WARN] Niconico info notify channel not found: "
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
						"[ERROR] Niconico info notify failed "
						f"guild={guild.id} channel={config_row.channel_id}: {e}"
					)
		return notified or handled

	async def add_filter(self, guild_id: int, keyword: str, mode: str = "include"):
		"""Add a Niconico Info keyword filter for one guild."""
		mode = self.normalize_filter_mode(mode)
		async with self.session_factory() as session:
			repo = NiconicoInfoFilterRepository(session)
			await repo.insert({
				"guild_id": guild_id,
				"keyword": keyword,
				"mode": mode,
				"enabled": True,
				"delete_flg": False,
			})
		return mode

	async def list_filters(self, guild_id: int):
		"""Return Niconico Info filters for one guild."""
		async with self.session_factory() as session:
			repo = NiconicoInfoFilterRepository(session)
			return await repo.list_by_guild(guild_id)

	async def set_filter_enabled(self, guild_id: int, filter_id: int, enabled: bool):
		"""Enable or disable one Niconico Info filter."""
		async with self.session_factory() as session:
			repo = NiconicoInfoFilterRepository(session)
			return await repo.set_enabled(guild_id, filter_id, enabled)

	async def delete_filter(self, guild_id: int, filter_id: int):
		"""Delete one Niconico Info filter."""
		async with self.session_factory() as session:
			repo = NiconicoInfoFilterRepository(session)
			return await repo.delete(guild_id, filter_id)

	def matches_filters(self, row, filters):
		"""Return True when a Niconico Info row passes guild filters."""
		if not filters:
			return True

		text = self.filter_target_text(row)
		exclude_filters = [row_filter for row_filter in filters if row_filter.mode == "exclude"]
		for row_filter in exclude_filters:
			if self.filter_keyword_matches(text, row_filter.keyword):
				return False

		include_filters = [row_filter for row_filter in filters if row_filter.mode == "include"]
		if include_filters:
			return any(self.filter_keyword_matches(text, row_filter.keyword) for row_filter in include_filters)
		return True

	def filter_target_text(self, row):
		"""Build normalized text used for keyword filter matching."""
		parts = [
			row.title,
			row.date_text,
			row.explanation,
			row.link,
			row.organizer_user,
			row.organizer_link,
			row.categories,
			row.source_url,
		]
		return "\n".join(str(part or "") for part in parts).casefold()

	def filter_keyword_matches(self, text: str, keyword: str):
		"""Return True when one filter keyword is contained in target text."""
		return str(keyword or "").casefold() in text

	def normalize_filter_mode(self, mode: str):
		"""Normalize user-facing filter mode aliases."""
		normalized = str(mode or "include").strip().casefold()
		if normalized in ("exclude", "ng", "deny", "除外"):
			return "exclude"
		return "include"

	async def build_notification(self, row):
		"""Build the Discord message body for a Niconico info event."""
		link = row.link or row.organizer_link
		summary = await self.build_notification_summary(row)
		lines = [
			"ニコニコインフォに新しい情報が追加されました。",
			f"タイトル: {row.title}",
		]
		if row.date_text:
			lines.append(f"期間: {row.date_text}")
		elif row.start_date and row.end_date:
			lines.append(f"期間: {row.start_date:%Y/%m/%d} - {row.end_date:%Y/%m/%d}")
		if row.organizer_user:
			lines.append(f"主催: {row.organizer_user}")
		if row.categories:
			lines.append(f"カテゴリ: {row.categories}")
		if link:
			lines.append(link)
		if summary:
			lines.append(f"要約: {summary}")
		return "\n".join(lines)[:1900]

	async def build_notification_summary(self, row):
		"""Return an about-500-character summary for a notification row."""
		if row.explanation:
			return self.summarize_text(row.explanation)

		link = row.link or row.organizer_link
		if not link:
			return ""
		try:
			return await asyncio.to_thread(self.fetch_article_summary, link)
		except Exception as e:
			print(f"[WARN] Niconico info summary fetch failed link={link}: {e}")
			return ""

	def fetch_article_summary(self, link: str):
		"""Download an article page and return a compact text summary."""
		html = self.download_html(link)
		soup = BeautifulSoup(html, "html.parser")
		text = self.extract_article_text(soup)
		return self.summarize_text(text)

	def extract_article_text(self, soup):
		"""Extract the main readable text from a Niconico Info article page."""
		for tag in soup.select("script, style, noscript, header, footer, nav"):
			tag.decompose()

		selectors = [
			"article",
			".entry-content",
			".articleBody",
			".article-body",
			".post-content",
			".l-main",
			"main",
		]
		for selector in selectors:
			element = soup.select_one(selector)
			text = self.text_or_empty(element)
			if len(text) >= 80:
				return text
		return self.text_or_empty(soup.body or soup)

	def summarize_text(self, text: str):
		"""Compress text to roughly SUMMARY_MAX_CHARS characters."""
		text = self.normalize_summary_text(text)
		if len(text) <= self.SUMMARY_MAX_CHARS:
			return text
		return f"{text[:self.SUMMARY_MAX_CHARS].rstrip()}..."

	def normalize_summary_text(self, text: str):
		"""Normalize whitespace for Discord summary text."""
		text = re.sub(r"\s+", " ", str(text or "")).strip()
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
