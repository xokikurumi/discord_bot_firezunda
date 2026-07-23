import asyncio
from datetime import datetime, timedelta, timezone
from io import BytesIO
import json
import math
from pathlib import Path
from urllib import request as urlrequest
from urllib.parse import quote

import aiohttp
import discord
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

import config
import constants
from repositories.base.geolonia_address_repo import GeoloniaAddressRepository
from repositories.base.jma_shindo_station_repo import JmaShindoStationRepository
from repositories.base.notify_channel_config_repo import NotifyChannelConfigRepository


class P2PQuakeService:
	"""Receive P2PQuake WebSocket events and notify configured Discord channels."""

	TARGET_CODES = {551, 552, 556}
	MAX_SEEN_IDS = 200
	DISCORD_MESSAGE_LIMIT = 1900
	PREFECTURE_COORDS = {
		"\u5317\u6d77\u9053": (43.06, 141.35),
		"\u9752\u68ee\u770c": (40.82, 140.74),
		"\u5ca9\u624b\u770c": (39.70, 141.15),
		"\u5bae\u57ce\u770c": (38.27, 140.87),
		"\u79cb\u7530\u770c": (39.72, 140.10),
		"\u5c71\u5f62\u770c": (38.24, 140.36),
		"\u798f\u5cf6\u770c": (37.75, 140.47),
		"\u8328\u57ce\u770c": (36.34, 140.45),
		"\u6803\u6728\u770c": (36.57, 139.88),
		"\u7fa4\u99ac\u770c": (36.39, 139.06),
		"\u57fc\u7389\u770c": (35.86, 139.65),
		"\u5343\u8449\u770c": (35.61, 140.12),
		"\u6771\u4eac\u90fd": (35.69, 139.69),
		"\u795e\u5948\u5ddd\u770c": (35.45, 139.64),
		"\u65b0\u6f5f\u770c": (37.90, 139.02),
		"\u5bcc\u5c71\u770c": (36.70, 137.21),
		"\u77f3\u5ddd\u770c": (36.59, 136.63),
		"\u798f\u4e95\u770c": (36.06, 136.22),
		"\u5c71\u68a8\u770c": (35.66, 138.57),
		"\u9577\u91ce\u770c": (36.65, 138.18),
		"\u5c90\u961c\u770c": (35.39, 136.72),
		"\u9759\u5ca1\u770c": (34.98, 138.38),
		"\u611b\u77e5\u770c": (35.18, 136.91),
		"\u4e09\u91cd\u770c": (34.73, 136.51),
		"\u6ecb\u8cc0\u770c": (35.00, 135.87),
		"\u4eac\u90fd\u5e9c": (35.02, 135.76),
		"\u5927\u962a\u5e9c": (34.69, 135.50),
		"\u5175\u5eab\u770c": (34.69, 135.18),
		"\u5948\u826f\u770c": (34.69, 135.83),
		"\u548c\u6b4c\u5c71\u770c": (34.23, 135.17),
		"\u9ce5\u53d6\u770c": (35.50, 134.24),
		"\u5cf6\u6839\u770c": (35.47, 133.05),
		"\u5ca1\u5c71\u770c": (34.66, 133.93),
		"\u5e83\u5cf6\u770c": (34.40, 132.46),
		"\u5c71\u53e3\u770c": (34.19, 131.47),
		"\u5fb3\u5cf6\u770c": (34.07, 134.56),
		"\u9999\u5ddd\u770c": (34.34, 134.04),
		"\u611b\u5a9b\u770c": (33.84, 132.77),
		"\u9ad8\u77e5\u770c": (33.56, 133.53),
		"\u798f\u5ca1\u770c": (33.61, 130.42),
		"\u4f50\u8cc0\u770c": (33.25, 130.30),
		"\u9577\u5d0e\u770c": (32.75, 129.87),
		"\u718a\u672c\u770c": (32.79, 130.74),
		"\u5927\u5206\u770c": (33.24, 131.61),
		"\u5bae\u5d0e\u770c": (31.91, 131.42),
		"\u9e7f\u5150\u5cf6\u770c": (31.56, 130.56),
		"\u6c96\u7e04\u770c": (26.21, 127.68),
	}
	SCALE_COLORS = {
		10: (173, 220, 115),
		20: (245, 223, 88),
		30: (245, 170, 65),
		40: (236, 110, 56),
		45: (224, 73, 50),
		50: (194, 47, 47),
		55: (139, 45, 128),
		60: (99, 36, 110),
		70: (68, 28, 87),
	}
	TSUNAMI_GRADE_COLORS = {
		"MajorWarning": (204, 24, 50),
		"Warning": (236, 112, 37),
		"Watch": (247, 203, 70),
		"Yoho": (113, 169, 221),
	}
	TSUNAMI_AREA_COORDS = {
		"\u5317\u6d77\u9053\u592a\u5e73\u6d0b\u6cbf\u5cb8\u6771\u90e8": (42.95, 144.00),
		"\u5317\u6d77\u9053\u592a\u5e73\u6d0b\u6cbf\u5cb8\u4e2d\u90e8": (42.45, 143.15),
		"\u5317\u6d77\u9053\u592a\u5e73\u6d0b\u6cbf\u5cb8\u897f\u90e8": (42.05, 141.15),
		"\u5317\u6d77\u9053\u65e5\u672c\u6d77\u6cbf\u5cb8\u5317\u90e8": (44.65, 141.80),
		"\u5317\u6d77\u9053\u65e5\u672c\u6d77\u6cbf\u5cb8\u5357\u90e8": (42.65, 140.25),
		"\u30aa\u30db\u30fc\u30c4\u30af\u6d77\u6cbf\u5cb8": (44.25, 143.60),
		"\u9752\u68ee\u770c\u65e5\u672c\u6d77\u6cbf\u5cb8": (40.80, 140.15),
		"\u9752\u68ee\u770c\u592a\u5e73\u6d0b\u6cbf\u5cb8": (40.65, 141.45),
		"\u9678\u5965\u6e7e": (41.00, 140.95),
		"\u5ca9\u624b\u770c": (39.45, 142.00),
		"\u5bae\u57ce\u770c": (38.35, 141.25),
		"\u798f\u5cf6\u770c": (37.55, 141.05),
		"\u8328\u57ce\u770c": (36.35, 140.80),
		"\u5343\u8449\u770c\u4e5d\u5341\u4e5d\u91cc\u30fb\u5916\u623f": (35.35, 140.45),
		"\u5343\u8449\u770c\u5185\u623f": (35.15, 139.85),
		"\u6771\u4eac\u6e7e\u5185\u6e7e": (35.55, 139.85),
		"\u4f0a\u8c46\u8af8\u5cf6": (34.35, 139.25),
		"\u5c0f\u7b20\u539f\u8af8\u5cf6": (27.10, 142.20),
		"\u76f8\u6a21\u6e7e\u30fb\u4e09\u6d66\u534a\u5cf6": (35.20, 139.45),
		"\u9759\u5ca1\u770c": (34.70, 138.35),
		"\u611b\u77e5\u770c\u5916\u6d77": (34.65, 137.15),
		"\u4f0a\u52e2\u30fb\u4e09\u6cb3\u6e7e": (34.65, 136.95),
		"\u4e09\u91cd\u770c\u5357\u90e8": (33.95, 136.20),
		"\u548c\u6b4c\u5c71\u770c": (33.85, 135.25),
		"\u5fb3\u5cf6\u770c": (33.85, 134.60),
		"\u9ad8\u77e5\u770c": (33.25, 133.45),
		"\u5bae\u5d0e\u770c": (31.85, 131.45),
		"\u9e7f\u5150\u5cf6\u770c\u6771\u90e8": (31.25, 131.05),
		"\u7a2e\u5b50\u5cf6\u30fb\u5c4b\u4e45\u5cf6\u5730\u65b9": (30.55, 130.95),
		"\u5944\u7f8e\u7fa4\u5cf6\u30fb\u30c8\u30ab\u30e9\u5217\u5cf6": (28.25, 129.35),
		"\u6c96\u7e04\u672c\u5cf6\u5730\u65b9": (26.35, 127.85),
		"\u5927\u6771\u5cf6\u5730\u65b9": (25.85, 131.25),
		"\u5bae\u53e4\u5cf6\u30fb\u516b\u91cd\u5c71\u5730\u65b9": (24.55, 124.30),
	}

	def __init__(self, bot, session_factory):
		"""Store dependencies and runtime state for the WebSocket worker."""
		self.bot = bot
		self.session_factory = session_factory
		self.ws_url = config.P2PQUAKE_WS_URL
		self.reconnect_delay = config.P2PQUAKE_RECONNECT_DELAY
		self.gsi_blank_tile_base_url = config.GSI_BLANK_TILE_BASE_URL.rstrip("/")
		self.gsi_tile_cache_dir = Path(config.GSI_TILE_CACHE_DIR)
		self.geolonia_api_base_url = config.GEOLONIA_JAPANESE_ADDRESSES_API_BASE_URL.rstrip("/")
		self.geolonia_municipality_cache = None
		self.geolonia_town_cache = {}
		self.geolonia_db_municipality_cache = {}
		self.geolonia_db_municipality_prefecture_cache = None
		self.geolonia_db_town_cache = {}
		self.geolonia_sync_lock = asyncio.Lock()
		self.jma_station_url = config.JMA_SHINDO_STATION_URL
		self.jma_station_cache = None
		self.jma_station_sync_lock = asyncio.Lock()
		self.enabled = config.P2PQUAKE_ENABLED
		self.min_notify_scale = config.P2PQUAKE_MIN_NOTIFY_SCALE
		self.image_font_path = config.P2PQUAKE_IMAGE_FONT_PATH
		self.seen_ids = []

	async def run_forever(self):
		"""Keep the P2PQuake WebSocket connected until the bot shuts down."""
		if not self.enabled:
			print("P2PQuake watcher disabled.")
			return

		await self.bot.wait_until_ready()
		jma_station_task = asyncio.create_task(self.run_jma_shindo_station_sync_forever())
		geolonia_address_task = asyncio.create_task(self.run_geolonia_address_sync_forever())
		try:
			while not self.bot.is_closed():
				try:
					await self.watch_once()
				except asyncio.CancelledError:
					raise
				except Exception as e:
					print(f"[ERROR] P2PQuake watcher error: {e}")

				await asyncio.sleep(self.reconnect_delay)
		finally:
			jma_station_task.cancel()
			geolonia_address_task.cancel()

	async def run_jma_shindo_station_sync_forever(self):
		"""Periodically refresh JMA seismic intensity stations into the database."""
		if not config.JMA_SHINDO_STATION_SYNC_ENABLED:
			print("JMA shindo station sync disabled.")
			return

		while not self.bot.is_closed():
			try:
				if await self.is_jma_shindo_station_sync_due():
					await self.sync_jma_shindo_stations()
			except asyncio.CancelledError:
				raise
			except Exception as e:
				print(f"[ERROR] JMA shindo station sync failed: {e}")

			await asyncio.sleep(config.JMA_SHINDO_STATION_SYNC_CHECK_INTERVAL_SECONDS)

	async def is_jma_shindo_station_sync_due(self):
		"""Return True when the cached JMA station data should be refreshed."""
		async with self.session_factory() as session:
			repo = JmaShindoStationRepository(session)
			last_synced_at = await repo.get_last_synced_at("jma_shindo_stations")

		if last_synced_at is None:
			return True
		if last_synced_at.tzinfo is None:
			last_synced_at = last_synced_at.replace(tzinfo=timezone.utc)
		return datetime.now(timezone.utc) - last_synced_at >= timedelta(days=config.JMA_SHINDO_STATION_SYNC_INTERVAL_DAYS)

	async def sync_jma_shindo_stations(self):
		"""Fetch JMA station table data and save it into the database."""
		async with self.jma_station_sync_lock:
			if not await self.is_jma_shindo_station_sync_due():
				return

			print("JMA shindo station sync started.")
			synced_at = datetime.now(timezone.utc)
			rows = await asyncio.to_thread(self.fetch_jma_shindo_station_rows, synced_at)
			async with self.session_factory() as session:
				repo = JmaShindoStationRepository(session)
				await repo.bulk_upsert_stations(rows)
				await repo.set_last_synced_at("jma_shindo_stations", synced_at)

			self.jma_station_cache = None
			print(f"JMA shindo station sync finished. rows={len(rows)}")

	def fetch_jma_shindo_station_rows(self, synced_at: datetime):
		"""Fetch and parse JMA seismic intensity station tables."""
		with urlrequest.urlopen(self.jma_station_url, timeout=30) as response:
			html = response.read().decode("utf-8", errors="replace")

		soup = BeautifulSoup(html, "html.parser")
		rows = []
		for table in soup.find_all("table"):
			table_rows = table.find_all("tr")
			if not table_rows:
				continue
			header = [cell.get_text(" ", strip=True) for cell in table_rows[0].find_all(["th", "td"])]
			if "震度観測点名称" not in header or "緯度(度)" not in header:
				continue

			for tr in table_rows[1:]:
				cells = [cell.get_text(" ", strip=True) for cell in tr.find_all(["th", "td"])]
				row = self.parse_jma_shindo_station_cells(cells, synced_at)
				if row:
					rows.append(row)
		return rows

	def parse_jma_shindo_station_cells(self, cells, synced_at: datetime):
		"""Convert one JMA station table row into a DB row."""
		if len(cells) < 8:
			return None

		latitude = self.degree_minute_to_decimal(cells[3], cells[4])
		longitude = self.degree_minute_to_decimal(cells[5], cells[6])
		if latitude is None or longitude is None:
			return None

		return {
			"region_name": cells[0],
			"station_name": cells[1],
			"address": cells[2],
			"lat": latitude,
			"lng": longitude,
			"observation_start": cells[7] if len(cells) > 7 else "",
			"observation_end": cells[8] if len(cells) > 8 else "",
			"source_updated_at": synced_at,
		}

	def degree_minute_to_decimal(self, degree, minute):
		"""Convert JMA degree/minute coordinate fields to decimal degrees."""
		degree_value = self.to_float(degree)
		minute_value = self.to_float(minute)
		if degree_value is None or minute_value is None:
			return None
		return degree_value + minute_value / 60.0

	async def run_geolonia_address_sync_forever(self):
		"""Periodically refresh Geolonia address data into the database."""
		if not config.GEOLONIA_ADDRESS_SYNC_ENABLED:
			print("Geolonia address sync disabled.")
			return

		while not self.bot.is_closed():
			try:
				if await self.is_geolonia_address_sync_due():
					await self.sync_geolonia_addresses()
			except asyncio.CancelledError:
				raise
			except Exception as e:
				print(f"[ERROR] Geolonia address sync failed: {e}")

			await asyncio.sleep(config.GEOLONIA_ADDRESS_SYNC_CHECK_INTERVAL_SECONDS)

	async def is_geolonia_address_sync_due(self):
		"""Return True when Geolonia data has not been synced for the latest scheduled date."""
		async with self.session_factory() as session:
			repo = GeoloniaAddressRepository(session)
			last_synced_at = await repo.get_last_synced_at("geolonia_japanese_addresses")

		if last_synced_at is None:
			return True
		if last_synced_at.tzinfo is None:
			last_synced_at = last_synced_at.replace(tzinfo=timezone.utc)
		return last_synced_at < self.latest_geolonia_scheduled_sync_at(datetime.now(timezone.utc))

	def latest_geolonia_scheduled_sync_at(self, now: datetime):
		"""Return the latest Geolonia scheduled sync date for January 1 or June 1."""
		if now.tzinfo is None:
			now = now.replace(tzinfo=timezone.utc)

		candidates = [
			datetime(now.year, 1, 1, tzinfo=timezone.utc),
			datetime(now.year, 6, 1, tzinfo=timezone.utc),
		]
		if now < candidates[0]:
			return datetime(now.year - 1, 6, 1, tzinfo=timezone.utc)
		if now < candidates[1]:
			return candidates[0]
		return candidates[1]

	async def sync_geolonia_addresses(self):
		"""Fetch Geolonia Japanese address data and save it into the database."""
		async with self.geolonia_sync_lock:
			if not await self.is_geolonia_address_sync_due():
				return

			print("Geolonia address sync started.")
			synced_at = datetime.now(timezone.utc)
			municipalities = await asyncio.to_thread(self.fetch_geolonia_municipality_source)
			total_count = 0

			for pref, municipality_names in municipalities.items():
				for municipality in municipality_names:
					rows = await asyncio.to_thread(
						self.build_geolonia_address_rows,
						pref,
						municipality,
						synced_at,
					)
					if not rows:
						continue
					async with self.session_factory() as session:
						repo = GeoloniaAddressRepository(session)
						await repo.bulk_upsert_addresses(rows)
					total_count += len(rows)

			async with self.session_factory() as session:
				repo = GeoloniaAddressRepository(session)
				await repo.set_last_synced_at("geolonia_japanese_addresses", synced_at)

			self.geolonia_db_municipality_cache.clear()
			self.geolonia_db_municipality_prefecture_cache = None
			self.geolonia_db_town_cache.clear()
			print(f"Geolonia address sync finished. rows={total_count}")

	def fetch_geolonia_municipality_source(self):
		"""Fetch Geolonia prefecture-to-municipality source data from the API."""
		return self.fetch_json(f"{self.geolonia_api_base_url}.json")

	def build_geolonia_address_rows(self, pref: str, municipality: str, synced_at: datetime):
		"""Fetch one municipality's town data and convert it into DB rows."""
		url = f"{self.geolonia_api_base_url}/{quote(pref)}/{quote(municipality)}.json"
		towns = self.fetch_json(url)
		rows = []
		for town in towns:
			lat = self.to_float(town.get("lat") or town.get("latitude"))
			lng = self.to_float(town.get("lng") or town.get("lon") or town.get("longitude"))
			town_name = town.get("town") or town.get("area") or town.get("name") or ""
			if lat is None or lng is None or not town_name:
				continue
			rows.append({
				"prefecture": town.get("prefecture") or town.get("pref") or pref,
				"municipality": town.get("city") or town.get("municipality") or municipality,
				"town": town_name,
				"lat": lat,
				"lng": lng,
				"source_updated_at": synced_at,
			})
		return rows

	async def watch_once(self):
		"""Open one WebSocket connection and process messages until it closes."""
		timeout = aiohttp.ClientTimeout(total=None, sock_connect=30, sock_read=None)
		async with aiohttp.ClientSession(timeout=timeout) as session:
			async with session.ws_connect(self.ws_url, heartbeat=30) as ws:
				print("P2PQuake WebSocket connected.")
				async for msg in ws:
					if msg.type == aiohttp.WSMsgType.TEXT:
						await self.handle_raw_message(msg.data)
					elif msg.type == aiohttp.WSMsgType.ERROR:
						raise ws.exception()

	async def handle_raw_message(self, raw_message: str):
		"""Parse a raw WebSocket message and notify when it is a target code."""
		data = json.loads(raw_message)
		code = int(data.get("code", 0))
		if code not in self.TARGET_CODES:
			return

		event_id = str(data.get("id") or data.get("_id") or "")
		if event_id and self.is_seen(event_id):
			return
		if event_id:
			self.mark_seen(event_id)

		if not self.should_notify_event(data):
			print(
				"P2PQuake event skipped by intensity threshold: "
				f"code={code} max_scale={self.extract_event_max_scale(data)} "
				f"threshold={self.min_notify_scale}"
			)
			return

		text = self.format_event(data)
		if text:
			await self.notify_discord(text, data)

	def is_seen(self, event_id: str):
		"""Return True when this WebSocket event id was already processed."""
		return event_id in self.seen_ids

	def mark_seen(self, event_id: str):
		"""Remember a processed event id for lightweight duplicate suppression."""
		self.seen_ids.append(event_id)
		if len(self.seen_ids) > self.MAX_SEEN_IDS:
			self.seen_ids = self.seen_ids[-self.MAX_SEEN_IDS:]

	async def notify_discord(self, body: str, data: dict):
		"""Send text immediately, then queue hypocenter image posts in the background."""
		image_targets = []
		for guild in self.bot.guilds:
			async with self.session_factory() as session:
				repo = NotifyChannelConfigRepository(session)
				configs = await repo.get_enabled_by_category(guild.id, constants.CONFIG_MENTION_QUAKE)

			for row in configs:
				channel = self.bot.get_channel(row.channel_id)
				if channel is None:
					print(f"[WARN] P2PQuake notify channel not found: guild={guild.id} channel={row.channel_id}")
					continue

				try:
					mention = self.build_mention(row.mention)
					for message in self.split_discord_messages(body, mention):
						await channel.send(message)
					image_targets.append(channel)
				except Exception as e:
					print(f"[ERROR] P2PQuake notify failed guild={guild.id} channel={row.channel_id}: {e}")

		if image_targets:
			code = int(data.get("code", 0))
			if code == 552 and self.has_tsunami_areas(data):
				asyncio.create_task(self.post_tsunami_image(data, image_targets))
			elif self.has_earthquake_image_data(data):
				asyncio.create_task(self.post_hypocenter_image(data, image_targets))

	def split_discord_messages(self, body: str, mention: str = ""):
		"""Split a Discord message body into chunks under the configured safety limit."""
		prefix = f"{mention}\n" if mention else ""
		limit = self.DISCORD_MESSAGE_LIMIT
		messages = []
		current = prefix

		for line in str(body or "").splitlines():
			line_parts = self.split_long_line(line, limit)
			for part in line_parts:
				separator = "\n" if current and not current.endswith("\n") else ""
				if len(current) + len(separator) + len(part) > limit:
					if current.strip():
						messages.append(current.rstrip("\n"))
					current = part
				else:
					current = f"{current}{separator}{part}"

		if current.strip():
			messages.append(current.rstrip("\n"))
		return messages or [prefix.rstrip("\n") or "-"]

	def split_long_line(self, line: str, limit: int):
		"""Split one line when it exceeds Discord's message chunk limit."""
		if len(line) <= limit:
			return [line]
		return [line[index:index + limit] for index in range(0, len(line), limit)]

	async def post_hypocenter_image(self, data: dict, channels):
		"""Generate the hypocenter image off the event loop and post only the image."""
		try:
			intensity_points = await self.extract_intensity_points_from_db(data)
			image_bytes = await asyncio.to_thread(self.generate_hypocenter_image, data, intensity_points)
			if not image_bytes:
				return

			for channel in channels:
				try:
					file = discord.File(BytesIO(image_bytes), filename="hypocenter.png")
					await channel.send(file=file)
				except Exception as e:
					print(f"[ERROR] P2PQuake hypocenter image send failed channel={channel.id}: {e}")
		except Exception as e:
			print(f"[ERROR] P2PQuake hypocenter image generation failed: {e}")

	async def post_tsunami_image(self, data: dict, channels):
		"""Generate the tsunami area image off the event loop and post only the image."""
		try:
			image_bytes = await asyncio.to_thread(self.generate_tsunami_image, data)
			if not image_bytes:
				return

			for channel in channels:
				try:
					file = discord.File(BytesIO(image_bytes), filename="tsunami.png")
					await channel.send(file=file)
				except Exception as e:
					print(f"[ERROR] P2PQuake tsunami image send failed channel={channel.id}: {e}")
		except Exception as e:
			print(f"[ERROR] P2PQuake tsunami image generation failed: {e}")

	async def add_notify_config(self, guild_id: int, category: str, channel_id: int, mention: str = ""):
		"""Register a notification channel setting."""
		async with self.session_factory() as session:
			repo = NotifyChannelConfigRepository(session)
			await repo.insert({
				"category": category,
				"guild_id": guild_id,
				"channel_id": channel_id,
				"enabled": True,
				"mention": mention,
			})

	async def list_notify_configs(self, guild_id: int):
		"""List notification channel settings for a guild."""
		async with self.session_factory() as session:
			repo = NotifyChannelConfigRepository(session)
			return await repo.list_by_guild(guild_id)

	async def set_notify_config_enabled(self, guild_id: int, config_id: int, enabled: bool):
		"""Enable or disable one notification channel setting."""
		async with self.session_factory() as session:
			repo = NotifyChannelConfigRepository(session)
			return await repo.set_enabled(guild_id, config_id, enabled)

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

	def format_event(self, data: dict):
		"""Dispatch P2PQuake event formatting by code."""
		code = int(data.get("code", 0))
		if code == 551:
			return self.format_earthquake(data)
		if code == 552:
			return self.format_tsunami(data)
		if code == 556:
			return self.format_eew_warning(data)
		return None

	def should_notify_event(self, data: dict):
		"""Return False for earthquake alerts below the configured intensity threshold."""
		code = int(data.get("code", 0))
		if code not in (551, 556):
			return True

		max_scale = self.extract_event_max_scale(data)
		if max_scale is None:
			return self.min_notify_scale <= 10
		return max_scale >= self.min_notify_scale

	def extract_event_max_scale(self, data: dict):
		"""Extract the maximum observed or predicted seismic intensity from an event."""
		earthquake = data.get("earthquake") or {}
		scales = [self.normalize_scale(earthquake.get("maxScale"))]

		for point in data.get("points") or []:
			scales.append(self.extract_point_max_scale(point))

		for area in data.get("areas") or []:
			scales.append(self.extract_point_max_scale(area))

		scales = [scale for scale in scales if scale is not None]
		if not scales:
			return None
		return max(scales)

	def extract_point_max_scale(self, point: dict):
		"""Extract the maximum scale from one observed or predicted intensity item."""
		scales = [
			self.normalize_scale(point.get("scale")),
			self.normalize_scale(point.get("scaleFrom")),
			self.normalize_scale(point.get("scaleTo")),
		]
		scales = [scale for scale in scales if scale is not None]
		if not scales:
			return None
		return max(scales)

	def has_hypocenter_location(self, data: dict):
		"""Return True when the event contains usable hypocenter coordinates."""
		return self.extract_hypocenter_location(data) is not None

	def has_earthquake_image_data(self, data: dict):
		"""Return True when an earthquake event has data worth rendering as an image."""
		return self.has_hypocenter_location(data) or bool(data.get("points") or data.get("areas"))

	def has_tsunami_areas(self, data: dict):
		"""Return True when the tsunami event has at least one drawable area."""
		return bool(self.extract_tsunami_area_points(data))

	def extract_hypocenter_location(self, data: dict):
		"""Extract latitude, longitude, and label from P2PQuake hypocenter data."""
		earthquake = data.get("earthquake") or {}
		hypocenter = earthquake.get("hypocenter") or {}
		latitude = self.to_float(hypocenter.get("latitude") or hypocenter.get("lat"))
		longitude = self.to_float(hypocenter.get("longitude") or hypocenter.get("lon") or hypocenter.get("lng"))
		if latitude is None or longitude is None:
			return None
		if not (20 <= latitude <= 46 and 122 <= longitude <= 154):
			return None
		return {
			"latitude": latitude,
			"longitude": longitude,
			"name": hypocenter.get("name") or "\u9707\u6e90\u5730",
			"magnitude": hypocenter.get("magnitude"),
			"depth": hypocenter.get("depth"),
			"time": earthquake.get("originTime") or earthquake.get("time") or data.get("time"),
			"max_scale": earthquake.get("maxScale"),
		}

	def to_float(self, value):
		"""Convert numeric API fields to float while tolerating missing values."""
		if value in (None, "", -1, "-1"):
			return None
		try:
			return float(value)
		except (TypeError, ValueError):
			return None

	def format_image_datetime(self, value):
		"""Format a datetime-like string with date and time on separate image lines."""
		if not value:
			return "-"
		text = str(value).strip()
		if "T" in text:
			date_part, time_part = text.split("T", 1)
			return f"{date_part}\n{time_part}"
		if " " in text:
			date_part, time_part = text.split(" ", 1)
			return f"{date_part}\n{time_part}"
		return text

	def generate_hypocenter_image(self, data: dict, intensity_points=None):
		"""Render a Japan-area hypocenter and intensity map as PNG bytes."""
		location = self.extract_hypocenter_location(data)

		width = 1080
		height = 760
		margin_left = 42
		margin_top = 54
		map_width = 790
		map_height = 540
		if intensity_points is None:
			intensity_points = self.extract_intensity_points(data)
		if not location and not intensity_points:
			return None
		render_context = self.build_gsi_render_context(location, intensity_points, map_width, map_height)

		image = Image.new("RGB", (width, height), (245, 248, 250))
		draw = ImageDraw.Draw(image)
		font_large = self.load_font(30)
		font_medium = self.load_font(22)
		font_small = self.load_font(17)

		map_image = self.build_gsi_base_map(render_context)
		image.paste(map_image, (margin_left, margin_top))
		draw.rectangle((margin_left, margin_top, margin_left + map_width, margin_top + map_height), outline=(120, 143, 158), width=2)
		self.draw_intensity_points(draw, intensity_points, render_context, margin_left, margin_top, font_small)

		title = "\u9707\u6e90\u4f4d\u7f6e\u3068\u5404\u5730\u306e\u9707\u5ea6" if location else "\u5404\u5730\u306e\u9707\u5ea6"
		draw.text((32, 18), title, font=font_large, fill=(24, 35, 43))
		info_x = margin_left + map_width + 28
		info_y = margin_top
		earthquake = data.get("earthquake") or {}
		hypocenter = earthquake.get("hypocenter") or {}
		info_lines = [
			("\u9707\u6e90\u5730", str(location["name"]) if location else str(hypocenter.get("name") or "-")),
			("\u767a\u751f\u6642\u523b", self.format_image_datetime(earthquake.get("originTime") or earthquake.get("time") or data.get("time"))),
			("\u7def\u5ea6", f'{location["latitude"]:.2f}' if location else "-"),
			("\u7d4c\u5ea6", f'{location["longitude"]:.2f}' if location else "-"),
			("\u898f\u6a21", f'M{hypocenter.get("magnitude") or "-"}'),
			("\u6df1\u3055", self.depth_text(hypocenter.get("depth"))),
			("\u6700\u5927\u9707\u5ea6", self.scale_text(earthquake.get("maxScale") or self.extract_event_max_scale(data))),
		]
		for label, value in info_lines:
			draw.text((info_x, info_y), label, font=font_small, fill=(86, 99, 110))
			value_y = info_y + 24
			draw.multiline_text((info_x, value_y), value, font=font_medium, fill=(24, 35, 43), spacing=4)
			value_box = draw.multiline_textbbox((info_x, value_y), value, font=font_medium, spacing=4)
			info_y += max(58, (value_box[3] - info_y) + 18)

		self.draw_intensity_legend(draw, info_x, info_y + 8, font_small)

		draw.text((32, height - 36), "P2P\u5730\u9707\u60c5\u5831\u306e\u9707\u6e90\u30fb\u9707\u5ea6\u30c7\u30fc\u30bf\u3092\u5143\u306b\u4f5c\u6210 / \u80cc\u666f: \u5730\u7406\u9662\u30bf\u30a4\u30eb / \u89b3\u6e2c\u70b9\u4f4d\u7f6e: \u6c17\u8c61\u5e81\u9707\u5ea6\u89b3\u6e2c\u70b9\u4e00\u89a7", font=font_small, fill=(98, 111, 121))
		if location:
			x, y = self.project_gsi_location(location["latitude"], location["longitude"], render_context, margin_left, margin_top)
			self.draw_hypocenter_marker(draw, x, y)
		output = BytesIO()
		image.save(output, format="PNG")
		return output.getvalue()

	def generate_tsunami_image(self, data: dict):
		"""Render a Japan-area tsunami warning map as PNG bytes."""
		area_points = self.extract_tsunami_area_points(data)
		if not area_points:
			return None

		width = 1080
		height = 760
		margin_left = 42
		margin_top = 54
		map_width = 790
		map_height = 540
		render_context = self.build_gsi_points_render_context(area_points, map_width, map_height)

		image = Image.new("RGB", (width, height), (245, 248, 250))
		draw = ImageDraw.Draw(image)
		font_large = self.load_font(30)
		font_medium = self.load_font(22)
		font_small = self.load_font(17)

		map_image = self.build_gsi_base_map(render_context)
		image.paste(map_image, (margin_left, margin_top))
		draw.rectangle((margin_left, margin_top, margin_left + map_width, margin_top + map_height), outline=(120, 143, 158), width=2)
		self.draw_tsunami_area_points(draw, area_points, render_context, margin_left, margin_top, font_small)

		title = "\u6d25\u6ce2\u60c5\u5831\u5bfe\u8c61\u533a\u57df"
		draw.text((32, 18), title, font=font_large, fill=(24, 35, 43))
		info_x = margin_left + map_width + 28
		info_y = margin_top
		info_lines = [
			("\u767a\u8868\u6642\u523b", self.format_image_datetime(self.issue_time(data))),
			("\u5bfe\u8c61\u533a\u57df\u6570", str(len(area_points))),
		]
		if data.get("cancelled"):
			info_lines.append(("\u72b6\u614b", "\u89e3\u9664"))

		for label, value in info_lines:
			draw.text((info_x, info_y), label, font=font_small, fill=(86, 99, 110))
			value_y = info_y + 24
			draw.multiline_text((info_x, value_y), value, font=font_medium, fill=(24, 35, 43), spacing=4)
			value_box = draw.multiline_textbbox((info_x, value_y), value, font=font_medium, spacing=4)
			info_y += max(58, (value_box[3] - info_y) + 18)

		self.draw_tsunami_legend(draw, info_x, info_y + 8, font_small)
		self.draw_tsunami_area_summary(draw, area_points, info_x, info_y + 158, font_small)

		draw.text((32, height - 36), "\u6d25\u6ce2\u4e88\u5831\u533a\u57df\u540d\u3092\u4ee3\u8868\u5ea7\u6a19\u306b\u5909\u63db\u3057\u3066\u8868\u793a / \u80cc\u666f: \u5730\u7406\u9662\u30bf\u30a4\u30eb", font=font_small, fill=(98, 111, 121))
		output = BytesIO()
		image.save(output, format="PNG")
		return output.getvalue()

	def build_gsi_points_render_context(self, points, map_width: int, map_height: int):
		"""Choose the highest GSI tile zoom that fits all given points."""
		for zoom in range(14, 4, -1):
			pixels = [
				self.latlon_to_global_pixel(point["latitude"], point["longitude"], zoom)
				for point in points
			]
			min_x = min(pixel[0] for pixel in pixels)
			max_x = max(pixel[0] for pixel in pixels)
			min_y = min(pixel[1] for pixel in pixels)
			max_y = max(pixel[1] for pixel in pixels)
			if max_x - min_x <= map_width - 120 and max_y - min_y <= map_height - 120:
				break
		else:
			zoom = 5
			pixels = [
				self.latlon_to_global_pixel(point["latitude"], point["longitude"], zoom)
				for point in points
			]
			min_x = min(pixel[0] for pixel in pixels)
			max_x = max(pixel[0] for pixel in pixels)
			min_y = min(pixel[1] for pixel in pixels)
			max_y = max(pixel[1] for pixel in pixels)

		if len(points) == 1:
			zoom = min(8, zoom)
			center_x, center_y = self.latlon_to_global_pixel(points[0]["latitude"], points[0]["longitude"], zoom)
		else:
			center_x = (min_x + max_x) / 2
			center_y = (min_y + max_y) / 2

		return {
			"zoom": zoom,
			"left_pixel": center_x - map_width / 2,
			"top_pixel": center_y - map_height / 2,
			"width": map_width,
			"height": map_height,
		}

	def build_gsi_render_context(self, location: dict, intensity_points, map_width: int, map_height: int):
		"""Choose the highest GSI tile zoom that fits the hypocenter and intensity points."""
		targets = list(intensity_points)
		if location:
			targets.append({
				"latitude": location["latitude"],
				"longitude": location["longitude"],
			})

		for zoom in range(14, 4, -1):
			pixels = [
				self.latlon_to_global_pixel(point["latitude"], point["longitude"], zoom)
				for point in targets
			]
			min_x = min(pixel[0] for pixel in pixels)
			max_x = max(pixel[0] for pixel in pixels)
			min_y = min(pixel[1] for pixel in pixels)
			max_y = max(pixel[1] for pixel in pixels)
			if max_x - min_x <= map_width - 120 and max_y - min_y <= map_height - 120:
				break
		else:
			zoom = 5
			pixels = [
				self.latlon_to_global_pixel(point["latitude"], point["longitude"], zoom)
				for point in targets
			]
			min_x = min(pixel[0] for pixel in pixels)
			max_x = max(pixel[0] for pixel in pixels)
			min_y = min(pixel[1] for pixel in pixels)
			max_y = max(pixel[1] for pixel in pixels)

		if len(targets) == 1:
			zoom = min(8, zoom)
			center_x, center_y = self.latlon_to_global_pixel(location["latitude"], location["longitude"], zoom)
		else:
			center_x = (min_x + max_x) / 2
			center_y = (min_y + max_y) / 2

		return {
			"zoom": zoom,
			"left_pixel": center_x - map_width / 2,
			"top_pixel": center_y - map_height / 2,
			"width": map_width,
			"height": map_height,
		}

	def build_gsi_base_map(self, context: dict):
		"""Download and stitch GSI blank tiles for the selected render context."""
		width = context["width"]
		height = context["height"]
		zoom = context["zoom"]
		left_pixel = context["left_pixel"]
		top_pixel = context["top_pixel"]
		tile_size = 256
		tile_min_x = math.floor(left_pixel / tile_size)
		tile_max_x = math.floor((left_pixel + width) / tile_size)
		tile_min_y = math.floor(top_pixel / tile_size)
		tile_max_y = math.floor((top_pixel + height) / tile_size)
		tile_count = 2 ** zoom
		map_image = Image.new("RGB", (width, height), (226, 239, 248))

		for tile_x in range(tile_min_x, tile_max_x + 1):
			for tile_y in range(tile_min_y, tile_max_y + 1):
				if tile_y < 0 or tile_y >= tile_count:
					continue
				tile = self.fetch_gsi_tile(zoom, tile_x % tile_count, tile_y)
				if tile is None:
					continue
				paste_x = int(tile_x * tile_size - left_pixel)
				paste_y = int(tile_y * tile_size - top_pixel)
				map_image.paste(tile, (paste_x, paste_y))

		return map_image

	def fetch_gsi_tile(self, zoom: int, tile_x: int, tile_y: int):
		"""Load one GSI blank tile from local cache or fetch and cache it."""
		cache_path = self.gsi_tile_cache_path(zoom, tile_x, tile_y)
		cached_tile = self.load_cached_gsi_tile(cache_path)
		if cached_tile is not None:
			return cached_tile

		url = f"{self.gsi_blank_tile_base_url}/{zoom}/{tile_x}/{tile_y}.png"
		try:
			with urlrequest.urlopen(url, timeout=10) as response:
				tile_bytes = response.read()
			self.save_gsi_tile_cache(cache_path, tile_bytes)
			return Image.open(BytesIO(tile_bytes)).convert("RGB")
		except Exception as e:
			print(f"[WARN] GSI tile fetch failed z={zoom} x={tile_x} y={tile_y}: {e}")
			return None

	def gsi_tile_cache_path(self, zoom: int, tile_x: int, tile_y: int):
		"""Return the local cache path for one GSI tile."""
		return self.gsi_tile_cache_dir / str(zoom) / str(tile_x) / f"{tile_y}.png"

	def load_cached_gsi_tile(self, cache_path: Path):
		"""Load a cached GSI tile when the local file exists and is readable."""
		if not cache_path.exists():
			return None
		try:
			return Image.open(cache_path).convert("RGB")
		except Exception as e:
			print(f"[WARN] GSI tile cache read failed path={cache_path}: {e}")
			return None

	def save_gsi_tile_cache(self, cache_path: Path, tile_bytes: bytes):
		"""Save a fetched GSI tile to the local cache."""
		try:
			cache_path.parent.mkdir(parents=True, exist_ok=True)
			cache_path.write_bytes(tile_bytes)
		except Exception as e:
			print(f"[WARN] GSI tile cache save failed path={cache_path}: {e}")

	def latlon_to_global_pixel(self, latitude: float, longitude: float, zoom: int):
		"""Convert latitude and longitude to Web Mercator global pixel coordinates."""
		siny = math.sin(math.radians(latitude))
		siny = min(max(siny, -0.9999), 0.9999)
		scale = 256 * (2 ** zoom)
		x = (longitude + 180.0) / 360.0 * scale
		y = (0.5 - math.log((1 + siny) / (1 - siny)) / (4 * math.pi)) * scale
		return x, y

	def project_gsi_location(self, latitude: float, longitude: float, context: dict, left: int, top: int):
		"""Project a location into the stitched GSI map rectangle."""
		x, y = self.latlon_to_global_pixel(latitude, longitude, context["zoom"])
		return left + x - context["left_pixel"], top + y - context["top_pixel"]

	def extract_intensity_points(self, data: dict):
		"""Extract observed or expected intensities for map rendering."""
		points = data.get("points") or data.get("areas") or []
		by_key = {}
		for point in points:
			scale = self.normalize_scale(point.get("scaleFrom") or point.get("scale"))
			if scale is None:
				continue

			latitude = self.to_float(point.get("latitude") or point.get("lat"))
			longitude = self.to_float(point.get("longitude") or point.get("lon") or point.get("lng"))
			name = self.point_name(point)
			pref = self.prefecture_from_name(name)
			has_point_coords = latitude is not None and longitude is not None
			resolved_by_geolonia = False
			if latitude is None or longitude is None:
				resolved = self.resolve_prefecture_location(name)
				if resolved:
					latitude, longitude, resolved_name = resolved
					name = resolved_name or name
					resolved_by_geolonia = True

			if latitude is None or longitude is None:
				continue

			key = name or f"{latitude:.2f},{longitude:.2f}"
			if not has_point_coords and not resolved_by_geolonia:
				key = pref or key
			current = by_key.get(key)
			if current is None or scale > current["scale"]:
				by_key[key] = {
					"name": name or pref or "-",
					"latitude": latitude,
					"longitude": longitude,
					"scale": scale,
				}

		return sorted(by_key.values(), key=lambda item: item["scale"], reverse=True)

	async def extract_intensity_points_from_db(self, data: dict):
		"""Extract intensity points and resolve missing coordinates from cached DB data."""
		points = data.get("points") or data.get("areas") or []
		by_key = {}
		for point in points:
			scale = self.normalize_scale(point.get("scaleFrom") or point.get("scale"))
			if scale is None:
				continue

			latitude = self.to_float(point.get("latitude") or point.get("lat"))
			longitude = self.to_float(point.get("longitude") or point.get("lon") or point.get("lng"))
			name = self.point_name(point)
			pref = self.prefecture_from_name(name)
			has_point_coords = latitude is not None and longitude is not None
			resolved_from_db = False
			if latitude is None or longitude is None:
				resolved = await self.resolve_jma_shindo_station_from_db(name)
				if resolved:
					latitude, longitude, resolved_name = resolved
					name = resolved_name or name
					resolved_from_db = True
				else:
					resolved = await self.resolve_observation_location_from_db(name)
					if resolved:
						latitude, longitude, resolved_name = resolved
						name = resolved_name or name
						resolved_from_db = True
					else:
						resolved = self.resolve_prefecture_location(name)
					if resolved:
						latitude, longitude, resolved_name = resolved
						name = resolved_name or name

			if latitude is None or longitude is None:
				continue

			key = name or f"{latitude:.2f},{longitude:.2f}"
			if not has_point_coords and not resolved_from_db:
				key = pref or key
			current = by_key.get(key)
			if current is None or scale > current["scale"]:
				by_key[key] = {
					"name": name or pref or "-",
					"latitude": latitude,
					"longitude": longitude,
					"scale": scale,
				}

		return sorted(by_key.values(), key=lambda item: item["scale"], reverse=True)

	async def resolve_jma_shindo_station_from_db(self, name: str):
		"""Resolve an observation label to coordinates using cached JMA station data."""
		stations = await self.get_jma_shindo_stations_from_db()
		normalized_name = self.normalize_observation_name(name)
		matches = [
			station for station in stations
			if station["normalized_name"] and (
				station["normalized_name"] in normalized_name
				or normalized_name in station["normalized_name"]
			)
		]
		if not matches:
			return None

		best = max(matches, key=lambda station: len(station["normalized_name"]))
		return best["lat"], best["lng"], best["station_name"]

	async def get_jma_shindo_stations_from_db(self):
		"""Load and cache active JMA station rows from the database."""
		if self.jma_station_cache is not None:
			return self.jma_station_cache

		async with self.session_factory() as session:
			repo = JmaShindoStationRepository(session)
			rows = await repo.list_active_stations()

		self.jma_station_cache = [
			{
				"station_name": row.station_name,
				"normalized_name": self.normalize_observation_name(row.station_name),
				"lat": row.lat,
				"lng": row.lng,
			}
			for row in rows
		]
		return self.jma_station_cache

	def normalize_observation_name(self, name: str):
		"""Normalize station labels for matching P2PQuake names to JMA names."""
		return (
			(name or "")
			.replace("（旧）", "")
			.replace("(旧)", "")
			.replace("（臨時）", "")
			.replace("(臨時)", "")
			.replace(" ", "")
			.replace("　", "")
		)

	def resolve_prefecture_location(self, name: str):
		"""Resolve a label to a prefecture representative point as a fallback."""
		pref = self.prefecture_from_name(name)
		if not pref:
			return None
		coords = self.PREFECTURE_COORDS.get(pref)
		if coords:
			return coords[0], coords[1], pref
		return None

	async def resolve_observation_location_from_db(self, name: str):
		"""Resolve an observation label to coordinates using cached DB address data."""
		pref = self.prefecture_from_name(name)
		municipality = ""
		if not pref:
			municipality = self.extract_municipality_name(name)
			pref = await self.find_prefecture_by_municipality_from_db(municipality)
			if not pref:
				return None

		if not municipality:
			municipality = await self.find_municipality_from_db(pref, name)
		if not municipality:
			return None

		town = await self.find_town_from_db(pref, municipality, name)
		if town:
			return town["lat"], town["lng"], f"{pref}{municipality}{town['town']}"

		center = await self.city_center_from_db(pref, municipality)
		if center:
			return center[0], center[1], f"{pref}{municipality}"
		return None

	async def find_prefecture_by_municipality_from_db(self, municipality: str):
		"""Find the prefecture for a municipality name when the observation label omits it."""
		if not municipality:
			return ""
		if self.geolonia_db_municipality_prefecture_cache is None:
			async with self.session_factory() as session:
				repo = GeoloniaAddressRepository(session)
				rows = await repo.list_municipality_prefectures()

			cache = {}
			for pref, name in rows:
				if not name:
					continue
				cache.setdefault(name, set()).add(pref)
			self.geolonia_db_municipality_prefecture_cache = cache

		prefs = self.geolonia_db_municipality_prefecture_cache.get(municipality) or set()
		if len(prefs) != 1:
			return ""
		return next(iter(prefs))

	async def find_municipality_from_db(self, pref: str, name: str):
		"""Find the longest cached municipality name contained in an observation label."""
		if pref not in self.geolonia_db_municipality_cache:
			async with self.session_factory() as session:
				repo = GeoloniaAddressRepository(session)
				self.geolonia_db_municipality_cache[pref] = await repo.list_municipalities(pref)

		municipality_name = self.extract_municipality_name(name)
		if municipality_name in self.geolonia_db_municipality_cache[pref]:
			return municipality_name

		matches = [
			municipality for municipality in self.geolonia_db_municipality_cache[pref]
			if municipality and municipality in name
		]
		if not matches:
			return ""
		return max(matches, key=len)

	def extract_municipality_name(self, name: str):
		"""Extract a municipality prefix from a longer address label."""
		normalized_name = self.normalize_observation_name(name)
		for pref in self.PREFECTURE_COORDS:
			if normalized_name.startswith(pref):
				normalized_name = normalized_name[len(pref):]
				break
		for suffix in ("\u5e02", "\u533a", "\u753a", "\u6751"):
			index = normalized_name.find(suffix)
			if index >= 0:
				return normalized_name[:index + len(suffix)]
		return ""

	async def find_town_from_db(self, pref: str, municipality: str, name: str):
		"""Find the most specific cached town name contained in an observation label."""
		towns = await self.get_towns_from_db(pref, municipality)
		matches = [
			town for town in towns
			if town.get("town") and town["town"] in name
		]
		if not matches:
			return None
		return max(matches, key=lambda town: len(town.get("town", "")))

	async def city_center_from_db(self, pref: str, municipality: str):
		"""Return a cached municipality representative point."""
		towns = await self.get_towns_from_db(pref, municipality)
		coords = [(town["lat"], town["lng"]) for town in towns]
		if not coords:
			return None
		return (
			sum(lat for lat, _ in coords) / len(coords),
			sum(lng for _, lng in coords) / len(coords),
		)

	async def get_towns_from_db(self, pref: str, municipality: str):
		"""Load and cache cached town-level rows from the database."""
		cache_key = (pref, municipality)
		if cache_key in self.geolonia_db_town_cache:
			return self.geolonia_db_town_cache[cache_key]

		async with self.session_factory() as session:
			repo = GeoloniaAddressRepository(session)
			rows = await repo.list_towns(pref, municipality)

		self.geolonia_db_town_cache[cache_key] = [
			{"town": row.town, "lat": row.lat, "lng": row.lng}
			for row in rows
		]
		return self.geolonia_db_town_cache[cache_key]

	def resolve_observation_location(self, name: str):
		"""Resolve an observation label to coordinates using Geolonia address data."""
		pref = self.prefecture_from_name(name)
		if not pref:
			return None

		municipality = self.find_municipality(pref, name)
		if not municipality:
			coords = self.PREFECTURE_COORDS.get(pref)
			if coords:
				return coords[0], coords[1], pref
			return None

		town = self.find_town(pref, municipality, name)
		if town:
			return town["lat"], town["lng"], f"{pref}{municipality}{town['town']}"

		center = self.city_center_from_geolonia(pref, municipality)
		if center:
			return center[0], center[1], f"{pref}{municipality}"

		coords = self.PREFECTURE_COORDS.get(pref)
		if coords:
			return coords[0], coords[1], pref
		return None

	def find_municipality(self, pref: str, name: str):
		"""Find the longest municipality name contained in an observation label."""
		municipalities = self.get_geolonia_municipalities().get(pref, [])
		matches = [municipality for municipality in municipalities if municipality in name]
		if not matches:
			return ""
		return max(matches, key=len)

	def find_town(self, pref: str, municipality: str, name: str):
		"""Find the most specific Geolonia town record contained in a label."""
		towns = self.get_geolonia_towns(pref, municipality)
		matches = [
			town for town in towns
			if town.get("town") and town["town"] in name
		]
		if not matches:
			return None
		return max(matches, key=lambda town: len(town.get("town", "")))

	def city_center_from_geolonia(self, pref: str, municipality: str):
		"""Return a municipality-level representative point from Geolonia town data."""
		towns = self.get_geolonia_towns(pref, municipality)
		coords = [
			(self.to_float(town.get("lat")), self.to_float(town.get("lng")))
			for town in towns
		]
		coords = [(lat, lng) for lat, lng in coords if lat is not None and lng is not None]
		if not coords:
			return None
		return (
			sum(lat for lat, _ in coords) / len(coords),
			sum(lng for _, lng in coords) / len(coords),
		)

	def get_geolonia_municipalities(self):
		"""Load and cache Geolonia prefecture-to-municipality data."""
		if self.geolonia_municipality_cache is not None:
			return self.geolonia_municipality_cache

		url = f"{self.geolonia_api_base_url}.json"
		try:
			self.geolonia_municipality_cache = self.fetch_json(url)
		except Exception as e:
			print(f"[WARN] Geolonia municipality fetch failed: {e}")
			self.geolonia_municipality_cache = {}
		return self.geolonia_municipality_cache

	def get_geolonia_towns(self, pref: str, municipality: str):
		"""Load and cache Geolonia town-level representative point data."""
		cache_key = (pref, municipality)
		if cache_key in self.geolonia_town_cache:
			return self.geolonia_town_cache[cache_key]

		url = f"{self.geolonia_api_base_url}/{quote(pref)}/{quote(municipality)}.json"
		try:
			self.geolonia_town_cache[cache_key] = self.fetch_json(url)
		except Exception as e:
			print(f"[WARN] Geolonia town fetch failed pref={pref} municipality={municipality}: {e}")
			self.geolonia_town_cache[cache_key] = []
		return self.geolonia_town_cache[cache_key]

	def fetch_json(self, url: str):
		"""Fetch a JSON document with a short timeout."""
		with urlrequest.urlopen(url, timeout=10) as response:
			return json.loads(response.read().decode("utf-8"))

	def point_name(self, point: dict):
		"""Return the most useful display name from an intensity point."""
		return point.get("addr") or point.get("name") or point.get("pref") or ""

	def extract_tsunami_area_points(self, data: dict):
		"""Extract drawable tsunami warning area points from a P2PQuake event."""
		points = []
		seen_names = set()
		for area in data.get("areas") or []:
			name = area.get("name") or area.get("pref") or area.get("area") or ""
			if not name or name in seen_names:
				continue
			location = self.resolve_tsunami_area_location(name)
			if location is None:
				print(f"[WARN] Tsunami area location not found: {name}")
				continue

			latitude, longitude, label = location
			points.append({
				"latitude": latitude,
				"longitude": longitude,
				"name": name,
				"label": label,
				"grade": area.get("grade"),
				"grade_text": self.tsunami_grade_text(area.get("grade")),
				"max_height": self.max_tsunami_height(area),
				"arrival_time": (area.get("firstHeight") or {}).get("arrivalTime")
				if isinstance(area.get("firstHeight"), dict) else "",
			})
			seen_names.add(name)
		return points

	def resolve_tsunami_area_location(self, name: str):
		"""Resolve a tsunami forecast area name to an approximate representative point."""
		if name in self.TSUNAMI_AREA_COORDS:
			lat, lng = self.TSUNAMI_AREA_COORDS[name]
			return lat, lng, name

		for area_name, coords in self.TSUNAMI_AREA_COORDS.items():
			if area_name in name or name in area_name:
				return coords[0], coords[1], area_name

		return self.resolve_prefecture_location(name)

	def prefecture_from_name(self, name: str):
		"""Find a prefecture name inside a P2PQuake point label."""
		for pref in self.PREFECTURE_COORDS:
			if name and pref in name:
				return pref
		return name if name in self.PREFECTURE_COORDS else ""

	def normalize_scale(self, scale):
		"""Normalize JMA intensity values to comparable integer codes."""
		if scale in (None, "", -1, "-1"):
			return None
		try:
			return int(scale)
		except (TypeError, ValueError):
			return None

	def draw_intensity_points(self, draw, points, context, left, top, font):
		"""Draw observed intensity points on the map."""
		for point in reversed(points):
			x, y = self.project_gsi_location(point["latitude"], point["longitude"], context, left, top)
			if not (
				left <= x <= left + context["width"]
				and top <= y <= top + context["height"]
			):
				continue

			color = self.SCALE_COLORS.get(point["scale"], (130, 130, 130))
			scale_label = self.scale_text(point["scale"])
			radius = 14 if point["scale"] < 45 else 17
			draw.ellipse((x - radius - 3, y - radius - 3, x + radius + 3, y + radius + 3), fill=(255, 255, 255), outline=(42, 55, 70), width=2)
			draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color, outline=(255, 255, 255), width=2)
			text_box = draw.textbbox((0, 0), scale_label, font=font)
			text_width = text_box[2] - text_box[0]
			text_height = text_box[3] - text_box[1]
			draw.text((x - text_width / 2, y - text_height / 2 - 1), scale_label, font=font, fill=(20, 24, 28))

	def draw_tsunami_area_points(self, draw, points, context, left, top, font):
		"""Draw tsunami warning area markers and short labels on the map."""
		for point in reversed(points):
			x, y = self.project_gsi_location(point["latitude"], point["longitude"], context, left, top)
			if not (
				left <= x <= left + context["width"]
				and top <= y <= top + context["height"]
			):
				continue

			color = self.tsunami_grade_color(point.get("grade"))
			radius = 18 if point.get("grade") == "MajorWarning" else 16 if point.get("grade") == "Warning" else 14
			draw.ellipse((x - radius - 5, y - radius - 5, x + radius + 5, y + radius + 5), fill=(255, 255, 255), outline=color, width=3)
			draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color, outline=(255, 255, 255), width=2)

			label = self.truncate_map_label(point.get("name") or "", 12)
			if label:
				label_x = x + radius + 8
				label_y = y - 17
				label_box = draw.textbbox((0, 0), label, font=font)
				label_width = label_box[2] - label_box[0]
				label_height = label_box[3] - label_box[1]
				if label_x + label_width + 12 > left + context["width"]:
					label_x = x - radius - label_width - 16
				if label_y < top:
					label_y = top + 3
				if label_y + label_height + 8 > top + context["height"]:
					label_y = top + context["height"] - label_height - 8
				draw.rounded_rectangle(
					(label_x - 5, label_y - 3, label_x + label_width + 5, label_y + label_height + 4),
					radius=4,
					fill=(255, 255, 255),
					outline=color,
					width=1,
				)
				draw.text((label_x, label_y), label, font=font, fill=(24, 35, 43))

	def truncate_map_label(self, text: str, max_chars: int = 10):
		"""Keep map station labels short enough to avoid covering nearby points."""
		text = (text or "").strip()
		if len(text) <= max_chars:
			return text
		return f"{text[:max_chars - 1]}…"

	def draw_hypocenter_marker(self, draw, x, y):
		"""Draw the hypocenter marker as a red cross symbol."""
		marker = "×"
		font = self.load_font(44)
		text_box = draw.textbbox((0, 0), marker, font=font, stroke_width=4)
		text_width = text_box[2] - text_box[0]
		text_height = text_box[3] - text_box[1]
		draw.text(
			(x - text_width / 2, y - text_height / 2),
			marker,
			font=font,
			fill=(220, 36, 31),
			stroke_width=4,
			stroke_fill=(255, 255, 255),
		)

	def draw_intensity_legend(self, draw, x, y, font):
		"""Draw the intensity color legend beside the map."""
		draw.text((x, y), "\u89b3\u6e2c\u5730\u70b9\u9707\u5ea6\u51e1\u4f8b", font=font, fill=(86, 99, 110))
		legend_items = [10, 20, 30, 40, 45, 50, 55, 60, 70]
		for index, scale in enumerate(legend_items):
			item_x = x + (index % 3) * 68
			item_y = y + 28 + (index // 3) * 34
			color = self.SCALE_COLORS.get(scale, (130, 130, 130))
			draw.ellipse((item_x, item_y, item_x + 24, item_y + 24), fill=color, outline=(255, 255, 255), width=2)
			draw.text((item_x + 30, item_y + 2), self.scale_text(scale), font=font, fill=(24, 35, 43))

	def draw_tsunami_legend(self, draw, x, y, font):
		"""Draw the tsunami warning grade color legend beside the map."""
		draw.text((x, y), "\u6d25\u6ce2\u51e1\u4f8b", font=font, fill=(86, 99, 110))
		for index, grade in enumerate(("MajorWarning", "Warning", "Watch", "Yoho")):
			item_x = x
			item_y = y + 28 + index * 32
			color = self.tsunami_grade_color(grade)
			draw.rounded_rectangle((item_x, item_y, item_x + 26, item_y + 22), radius=4, fill=color)
			draw.text((item_x + 36, item_y + 1), self.tsunami_grade_text(grade), font=font, fill=(24, 35, 43))

	def draw_tsunami_area_summary(self, draw, points, x, y, font):
		"""Draw a compact tsunami area summary beside the map."""
		draw.text((x, y), "\u5bfe\u8c61\u533a\u57df", font=font, fill=(86, 99, 110))
		for index, point in enumerate(points):
			item_y = y + 28 + index * 44
			color = self.tsunami_grade_color(point.get("grade"))
			draw.ellipse((x, item_y + 4, x + 16, item_y + 20), fill=color, outline=(255, 255, 255), width=1)
			name = self.truncate_map_label(point.get("name") or "", 10)
			height = point.get("max_height") or "-"
			draw.text((x + 24, item_y), name, font=font, fill=(24, 35, 43))
			draw.text((x + 24, item_y + 20), f"{point.get('grade_text') or '-'} / {height}", font=font, fill=(86, 99, 110))

	def tsunami_grade_color(self, grade):
		"""Return the display color for one tsunami warning grade."""
		return self.TSUNAMI_GRADE_COLORS.get(grade, (130, 130, 130))

	def load_font(self, size: int):
		"""Load a Japanese-capable font when available."""
		configured_path = getattr(self, "image_font_path", "")
		paths = []
		if configured_path:
			paths.append(configured_path)
		paths.extend((
			"/opt/discord/fonts/NotoSansCJKjp-Regular.otf",
			"/opt/discord/current/fonts/NotoSansCJKjp-Regular.otf",
			"/opt/discord/current/assets/fonts/NotoSansCJKjp-Regular.otf",
			"/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
			"/usr/share/fonts/opentype/noto/NotoSansCJKjp-Regular.otf",
			"/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc",
			"/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
			"/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
			"/usr/share/fonts/truetype/vlgothic/VL-Gothic-Regular.ttf",
			"/usr/share/fonts/ipa-gothic/ipag.ttf",
			"C:/Windows/Fonts/meiryo.ttc",
			"C:/Windows/Fonts/NotoSansJP-VF.ttf",
			"C:/Windows/Fonts/YuGothM.ttc",
			"C:/Windows/Fonts/msgothic.ttc",
		))
		for path in paths:
			try:
				return ImageFont.truetype(path, size)
			except OSError:
				if configured_path and path == configured_path:
					print(f"[WARN] configured image font cannot be loaded: {path}")
				continue
		print("[WARN] Japanese image font not found. Falling back to Pillow default font.")
		return ImageFont.load_default()

	def project_location(self, latitude, longitude, left, top, width, height, lon_min, lon_max, lat_min, lat_max):
		"""Project longitude and latitude into the map rectangle."""
		x = left + ((longitude - lon_min) / (lon_max - lon_min)) * width
		y = top + ((lat_max - latitude) / (lat_max - lat_min)) * height
		return x, y

	def draw_grid(self, draw, left, top, width, height, lon_min, lon_max, lat_min, lat_max, font):
		"""Draw longitude and latitude guide lines."""
		for lon in range(125, 155, 5):
			x, _ = self.project_location(lat_min, lon, left, top, width, height, lon_min, lon_max, lat_min, lat_max)
			draw.line((x, top, x, top + height), fill=(188, 207, 218), width=1)
			draw.text((x + 4, top + height - 24), f"{lon}E", font=font, fill=(91, 108, 120))
		for lat in range(20, 50, 5):
			_, y = self.project_location(lat, lon_min, left, top, width, height, lon_min, lon_max, lat_min, lat_max)
			draw.line((left, y, left + width, y), fill=(188, 207, 218), width=1)
			draw.text((left + 6, y + 4), f"{lat}N", font=font, fill=(91, 108, 120))

	def draw_japan_outline(self, draw, left, top, width, height, lon_min, lon_max, lat_min, lat_max):
		"""Draw a rough Japan outline for visual context."""
		islands = [
			[(141.0, 45.5), (144.0, 44.4), (145.6, 43.2), (144.5, 41.8), (142.0, 41.4), (140.2, 42.6), (140.0, 44.0), (141.0, 45.5)],
			[(140.0, 41.4), (141.5, 40.6), (141.0, 39.0), (142.0, 38.2), (141.2, 37.0), (140.4, 36.0), (140.9, 35.0), (139.6, 34.5), (138.2, 35.2), (137.0, 36.4), (136.0, 35.7), (135.0, 35.4), (134.2, 35.7), (133.0, 35.2), (132.4, 34.4), (133.6, 33.6), (134.8, 34.1), (135.8, 33.5), (136.8, 34.2), (137.8, 34.7), (138.8, 35.4), (139.8, 36.5), (140.0, 38.0), (139.8, 39.5), (140.0, 41.4)],
			[(132.0, 34.6), (133.8, 34.5), (134.8, 34.0), (134.2, 33.4), (132.8, 33.4), (132.0, 34.0), (132.0, 34.6)],
			[(130.2, 33.9), (131.8, 33.6), (132.0, 32.6), (131.0, 31.4), (130.0, 31.0), (129.6, 32.2), (130.2, 33.9)],
			[(127.6, 26.7), (128.3, 26.5), (128.2, 26.0), (127.5, 26.1), (127.6, 26.7)],
		]
		for island in islands:
			points = [
				self.project_location(lat, lon, left, top, width, height, lon_min, lon_max, lat_min, lat_max)
				for lon, lat in island
			]
			draw.polygon(points, fill=(208, 222, 196), outline=(70, 111, 82))

	def format_earthquake(self, data: dict):
		"""Format code 551 earthquake information."""
		earthquake = data.get("earthquake") or {}
		hypocenter = earthquake.get("hypocenter") or {}
		points = data.get("points") or []
		lines = [
			"\u3010\u5730\u9707\u60c5\u5831\u3011",
			f"\u767a\u8868\u6642\u523b: {self.issue_time(data)}",
			f"\u767a\u751f\u6642\u523b: {earthquake.get('time') or '-'}",
			f"\u9707\u6e90\u5730: {hypocenter.get('name') or '-'}",
			f"\u898f\u6a21: M{hypocenter.get('magnitude') or '-'} / \u6df1\u3055: {self.depth_text(hypocenter.get('depth'))}",
			f"\u6700\u5927\u9707\u5ea6: {self.scale_text(earthquake.get('maxScale'))}",
			f"\u6d25\u6ce2: {self.tsunami_text(earthquake.get('domesticTsunami'))}",
		]
		intensity_lines = self.format_points(points)
		if intensity_lines:
			lines.append("\u5404\u5730\u306e\u9707\u5ea6:")
			lines.extend(intensity_lines)
		return "\n".join(lines)

	def format_tsunami(self, data: dict):
		"""Format code 552 tsunami forecast or warning information."""
		areas = data.get("areas") or []
		lines = [
			"\u3010\u6d25\u6ce2\u4e88\u5831\u3011",
			f"\u767a\u8868\u6642\u523b: {self.issue_time(data)}",
		]
		if data.get("cancelled"):
			lines.append("\u6d25\u6ce2\u4e88\u5831\u306f\u89e3\u9664\u3055\u308c\u307e\u3057\u305f\u3002")

		for area in areas:
			first_height = area.get("firstHeight") if isinstance(area.get("firstHeight"), dict) else {}
			lines.append(
				f"- {area.get('name') or '-'}: {self.tsunami_grade_text(area.get('grade'))}"
				f" / \u5230\u9054\u4e88\u60f3: {first_height.get('arrivalTime') or '-'}"
				f" / \u6700\u5927: {self.max_tsunami_height(area)}"
			)
		return "\n".join(lines)

	def format_eew_warning(self, data: dict):
		"""Format code 556 emergency earthquake warning information."""
		earthquake = data.get("earthquake") or {}
		hypocenter = earthquake.get("hypocenter") or {}
		areas = data.get("areas") or []
		lines = [
			"\u3010\u7dca\u6025\u5730\u9707\u901f\u5831\uff08\u8b66\u5831\uff09\u3011",
			f"\u767a\u8868\u6642\u523b: {self.issue_time(data)}",
			f"\u767a\u751f\u6642\u523b: {earthquake.get('originTime') or earthquake.get('time') or '-'}",
			f"\u9707\u6e90\u5730: {hypocenter.get('name') or '-'}",
			f"\u898f\u6a21: M{hypocenter.get('magnitude') or '-'} / \u6df1\u3055: {self.depth_text(hypocenter.get('depth'))}",
			f"\u6700\u5927\u4e88\u6e2c\u9707\u5ea6: {self.scale_text(earthquake.get('maxScale'))}",
		]
		for area in areas:
			lines.append(f"- {area.get('name') or area.get('pref') or '-'}: {self.scale_text(area.get('scaleFrom') or area.get('scale'))}")
		return "\n".join(lines)

	def issue_time(self, data: dict):
		"""Extract issue time from common P2PQuake fields."""
		issue = data.get("issue") or {}
		return issue.get("time") or data.get("time") or "-"

	def format_points(self, points):
		"""Format observed intensity points, grouped as simple lines."""
		lines = []
		sorted_points = sorted(
			points,
			key=lambda point: self.extract_point_max_scale(point) or -1,
			reverse=True,
		)
		for point in sorted_points:
			scale = self.extract_point_max_scale(point)
			name = point.get("addr") or point.get("name") or point.get("pref") or "-"
			lines.append(f"- {name}: {self.scale_text(scale)}")
		return lines

	def depth_text(self, depth):
		"""Format hypocenter depth from P2PQuake numeric values."""
		if depth in (None, -1):
			return "-"
		if depth == 0:
			return "\u3054\u304f\u6d45\u3044"
		return f"{depth}km"

	def scale_text(self, scale):
		"""Convert JMA intensity codes to readable Japanese labels."""
		scale_map = {
			10: "1",
			20: "2",
			30: "3",
			40: "4",
			45: "5\u5f31",
			50: "5\u5f37",
			55: "6\u5f31",
			60: "6\u5f37",
			70: "7",
		}
		return scale_map.get(scale, str(scale) if scale is not None else "-")

	def tsunami_text(self, value):
		"""Format domestic tsunami status for earthquake information."""
		mapping = {
			"None": "\u306a\u3057",
			"Unknown": "\u4e0d\u660e",
			"Checking": "\u8abf\u67fb\u4e2d",
			"NonEffective": "\u82e5\u5e72\u306e\u6d77\u9762\u5909\u52d5",
			"Watch": "\u6d25\u6ce2\u6ce8\u610f\u5831",
			"Warning": "\u6d25\u6ce2\u8b66\u5831\u4ee5\u4e0a",
		}
		return mapping.get(value, str(value) if value else "-")

	def tsunami_grade_text(self, grade):
		"""Format tsunami warning grade values."""
		mapping = {
			"MajorWarning": "\u5927\u6d25\u6ce2\u8b66\u5831",
			"Warning": "\u6d25\u6ce2\u8b66\u5831",
			"Watch": "\u6d25\u6ce2\u6ce8\u610f\u5831",
			"Yoho": "\u6d25\u6ce2\u4e88\u5831",
		}
		return mapping.get(grade, str(grade) if grade else "-")

	def max_tsunami_height(self, area):
		"""Return a readable maximum tsunami height for one area."""
		max_height = area.get("maxHeight")
		if isinstance(max_height, dict):
			if max_height.get("description"):
				return max_height["description"]
			if max_height.get("value"):
				return f"{max_height['value']}m"
		return "-"
