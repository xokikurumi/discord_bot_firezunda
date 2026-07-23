import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
from urllib import request
from urllib.error import HTTPError, URLError

from sqlalchemy import text

import config
from repositories.log.communication_trend_analysis_repo import CommunicationTrendAnalysisRepository


JST = timezone(timedelta(hours=9))


@dataclass
class TrendPeriod:
	"""A completed semiannual analysis period."""

	key: str
	start: datetime
	end: datetime


class CommunicationTrendService:
	"""Create semiannual guild and user communication trend reports."""

	def __init__(self, bot, session_factory):
		"""Load runtime settings used by the semiannual analysis task."""
		self.bot = bot
		self.session_factory = session_factory
		self.enabled = config.COMMUNICATION_TREND_ANALYSIS_ENABLED
		self.guild_analysis_enabled = config.COMMUNICATION_TREND_GUILD_ANALYSIS_ENABLED
		self.check_interval_seconds = config.COMMUNICATION_TREND_CHECK_INTERVAL_SECONDS
		self.min_user_messages = config.COMMUNICATION_TREND_MIN_USER_MESSAGES
		self.sample_limit = config.COMMUNICATION_TREND_SAMPLE_LIMIT
		self.num_predict = config.COMMUNICATION_TREND_NUM_PREDICT
		self.ollama_url = config.OLLAMA_URL
		self.ollama_model = config.OLLAMA_MODEL
		self.ollama_timeout_seconds = config.OLLAMA_TIMEOUT_SECONDS
		self.last_run_key = None

	async def run_forever(self):
		"""Run the trend analyzer periodically and skip already processed periods."""
		if not self.enabled:
			print("Communication trend analyzer disabled.")
			return

		await self.bot.wait_until_ready()
		while not self.bot.is_closed():
			try:
				period = self.scheduled_analysis_period(datetime.now(JST))
				if period is not None and self.last_run_key != period.key:
					await self.analyze_period(period)
					self.last_run_key = period.key
			except Exception as e:
				print(f"[ERROR] Communication trend analysis failed: {e}")

			await asyncio.sleep(self.check_interval_seconds)

	async def analyze_previous_period(self, guild_id=None):
		"""Analyze the latest completed scheduled period."""
		period = self.latest_completed_scheduled_period(datetime.now(JST))
		await self.analyze_period(period, guild_id)
		return period

	def scheduled_analysis_period(self, now: datetime):
		"""Return the period to analyze on January 1 or June 1 JST."""
		now = now.astimezone(JST)
		if now.month == 1 and now.day == 1:
			return self.build_period(now.year - 1, 6, now.year, 1)
		if now.month == 6 and now.day == 1:
			return self.build_period(now.year, 1, now.year, 6)
		return None

	def latest_completed_scheduled_period(self, now: datetime):
		"""Return the latest period that would have been analyzed by schedule."""
		now = now.astimezone(JST)
		if (now.month, now.day) >= (6, 1):
			return self.build_period(now.year, 1, now.year, 6)
		return self.build_period(now.year - 1, 6, now.year, 1)

	def build_period(self, start_year: int, start_month: int, end_year: int, end_month: int):
		"""Build a trend period using JST calendar boundaries converted to UTC."""
		start_jst = datetime(start_year, start_month, 1, tzinfo=JST)
		end_jst = datetime(end_year, end_month, 1, tzinfo=JST)
		key = f"{start_year:04d}-{start_month:02d}_to_{end_year:04d}-{end_month:02d}"
		return TrendPeriod(
			key=key,
			start=start_jst.astimezone(timezone.utc),
			end=end_jst.astimezone(timezone.utc),
		)

	async def analyze_period(self, period: TrendPeriod, guild_id=None):
		"""Create missing guild and user reports for one period."""
		guild_ids = [guild_id] if guild_id is not None else await self.list_guild_ids(period)
		for guild_id in guild_ids:
			if self.guild_analysis_enabled:
				await self.analyze_guild(period, guild_id)
			user_ids = await self.list_user_ids(period, guild_id)
			for user_id in user_ids:
				await self.analyze_user(period, guild_id, user_id)

	async def list_guild_ids(self, period: TrendPeriod):
		"""Return guild ids that have message logs in the period."""
		async with self.session_factory() as session:
			result = await session.execute(
				text(
					"""
					SELECT DISTINCT guild_id
					FROM message_log
					WHERE bot_flg = FALSE
					  AND message_created_at >= :start
					  AND message_created_at < :end
					ORDER BY guild_id
					"""
				),
				{"start": period.start, "end": period.end},
			)
			return result.scalars().all()

	async def list_user_ids(self, period: TrendPeriod, guild_id: int):
		"""Return active user ids in a guild for the period."""
		async with self.session_factory() as session:
			result = await session.execute(
				text(
					"""
					SELECT user_id
					FROM message_log
					WHERE guild_id = :guild_id
					  AND user_id IS NOT NULL
					  AND bot_flg = FALSE
					  AND message_created_at >= :start
					  AND message_created_at < :end
					GROUP BY user_id
					HAVING COUNT(*) >= :min_user_messages
					ORDER BY COUNT(*) DESC
					"""
				),
				{
					"guild_id": guild_id,
					"start": period.start,
					"end": period.end,
					"min_user_messages": self.min_user_messages,
				},
			)
			return result.scalars().all()

	async def analyze_guild(self, period: TrendPeriod, guild_id: int):
		"""Create one guild-level communication trend report if missing."""
		async with self.session_factory() as session:
			repo = CommunicationTrendAnalysisRepository(session)
			existing = await repo.get(period.key, "guild", guild_id)
			if existing and existing.summary != "Ollama analysis failed.":
				return

		metrics = await self.collect_metrics(period, guild_id)
		if metrics["message_count"] == 0:
			return

		report = await self.request_report("guild", period, metrics)
		await self.save_report(period, "guild", guild_id, None, metrics, report)

	async def analyze_user(self, period: TrendPeriod, guild_id: int, user_id: int):
		"""Create one user-level communication trend report if missing."""
		async with self.session_factory() as session:
			repo = CommunicationTrendAnalysisRepository(session)
			existing = await repo.get(period.key, "user", guild_id, user_id)
			if existing and existing.summary != "Ollama analysis failed.":
				return

		metrics = await self.collect_metrics(period, guild_id, user_id)
		if metrics["message_count"] < self.min_user_messages:
			return

		report = await self.request_report("user", period, metrics)
		await self.save_report(period, "user", guild_id, user_id, metrics, report)

	async def collect_metrics(self, period: TrendPeriod, guild_id: int, user_id=None):
		"""Collect message, edit, delete, analysis, and sample data for one scope."""
		params = {"guild_id": guild_id, "start": period.start, "end": period.end}
		user_filter = ""
		if user_id is not None:
			params["user_id"] = user_id
			user_filter = "AND user_id = :user_id"

		async with self.session_factory() as session:
			counts = await session.execute(
				text(
					f"""
					SELECT
						COUNT(*) AS message_count,
						COUNT(DISTINCT user_id) AS active_user_count,
						SUM(CASE WHEN has_attachments THEN 1 ELSE 0 END) AS attachment_count,
						SUM(CASE WHEN has_embeds THEN 1 ELSE 0 END) AS embed_count,
						SUM(CASE WHEN has_stickers THEN 1 ELSE 0 END) AS sticker_count
					FROM message_log
					WHERE guild_id = :guild_id
					  AND bot_flg = FALSE
					  AND message_created_at >= :start
					  AND message_created_at < :end
					  {user_filter}
					"""
				),
				params,
			)
			count_row = counts.mappings().first() or {}

			edit_count = await self.count_rows(session, "message_edit_log", params, user_filter)
			delete_count = await self.count_rows(session, "message_delete_log", params, user_filter)
			analysis = await session.execute(
				text(
					f"""
					SELECT
						COUNT(*) AS analysis_count,
						AVG(max_score) AS max_score_avg,
						AVG(aggression) AS aggression_avg,
						AVG(intimidation) AS intimidation_avg,
						AVG(insult) AS insult_avg,
						AVG(sarcasm) AS sarcasm_avg,
						AVG(snide) AS snide_avg,
						AVG(discomfort) AS discomfort_avg,
						SUM(CASE WHEN should_react THEN 1 ELSE 0 END) AS reacted_count,
						SUM(CASE WHEN should_notify THEN 1 ELSE 0 END) AS notified_count
					FROM message_analysis_log
					WHERE guild_id = :guild_id
					  AND created_at >= :start
					  AND created_at < :end
					  {user_filter}
					"""
				),
				params,
			)
			analysis_row = analysis.mappings().first() or {}
			samples = await self.collect_samples(session, params, user_filter)

		metrics = {
			"guild_id": guild_id,
			"user_id": user_id,
			"message_count": int(count_row.get("message_count") or 0),
			"active_user_count": int(count_row.get("active_user_count") or 0),
			"attachment_count": int(count_row.get("attachment_count") or 0),
			"embed_count": int(count_row.get("embed_count") or 0),
			"sticker_count": int(count_row.get("sticker_count") or 0),
			"edit_count": int(edit_count or 0),
			"delete_count": int(delete_count or 0),
			"analysis_count": int(analysis_row.get("analysis_count") or 0),
			"max_score_avg": int(round(analysis_row.get("max_score_avg") or 0)),
			"analysis_averages": {
				"aggression": round(float(analysis_row.get("aggression_avg") or 0), 1),
				"intimidation": round(float(analysis_row.get("intimidation_avg") or 0), 1),
				"insult": round(float(analysis_row.get("insult_avg") or 0), 1),
				"sarcasm": round(float(analysis_row.get("sarcasm_avg") or 0), 1),
				"snide": round(float(analysis_row.get("snide_avg") or 0), 1),
				"discomfort": round(float(analysis_row.get("discomfort_avg") or 0), 1),
			},
			"reacted_count": int(analysis_row.get("reacted_count") or 0),
			"notified_count": int(analysis_row.get("notified_count") or 0),
			"samples": samples,
		}
		return metrics

	async def count_rows(self, session, table_name: str, params: dict, user_filter: str):
		"""Count rows in an event log table for the current scope."""
		result = await session.execute(
			text(
				f"""
				SELECT COUNT(*)
				FROM {table_name}
				WHERE guild_id = :guild_id
				  AND created_at >= :start
				  AND created_at < :end
				  {user_filter}
				"""
			),
			params,
		)
		return result.scalar() or 0

	async def collect_samples(self, session, params: dict, user_filter: str):
		"""Collect representative message samples for trend analysis."""
		result = await session.execute(
			text(
				f"""
				SELECT content
				FROM message_log
				WHERE guild_id = :guild_id
				  AND bot_flg = FALSE
				  AND content IS NOT NULL
				  AND content <> ''
				  AND message_created_at >= :start
				  AND message_created_at < :end
				  {user_filter}
				ORDER BY message_created_at DESC
				LIMIT :sample_limit
				"""
			),
			{**params, "sample_limit": self.sample_limit},
		)
		return [self.truncate_text(row[0].replace("\n", " "), 200) for row in result.fetchall()]

	async def request_report(self, scope_type: str, period: TrendPeriod, metrics: dict):
		"""Ask Ollama to turn metrics and samples into a Japanese trend report."""
		try:
			return await asyncio.to_thread(self._request_report_sync, scope_type, period, metrics)
		except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, ValueError) as e:
			print(f"[ERROR] Communication trend Ollama request failed: {e}")
			return {
				"summary": "Ollama analysis failed.",
				"tendencies": "",
				"risks": "",
				"recommendations": "",
				"error": str(e),
			}

	def _request_report_sync(self, scope_type: str, period: TrendPeriod, metrics: dict):
		"""Blocking Ollama request implementation."""
		try:
			return self._request_report_once(scope_type, period, metrics)
		except ValueError as e:
			if "empty report content" not in str(e):
				raise
			retry_metrics = dict(metrics)
			retry_metrics["samples"] = retry_metrics.get("samples", [])[:5]
			return self._request_report_once(scope_type, period, retry_metrics)

	def _request_report_once(self, scope_type: str, period: TrendPeriod, metrics: dict):
		"""Send one blocking Ollama report request."""
		payload = {
			"model": self.ollama_model,
			"stream": False,
			"format": "json",
			"options": {"temperature": 0, "num_predict": self.num_predict},
			"messages": [
				{
					"role": "system",
					"content": (
						"You analyze Discord communication tendencies. "
						"Return strict JSON in Japanese with keys: summary, tendencies, risks, recommendations. "
						"Be careful not to diagnose personality or health. Focus on observable communication style, "
						"server operations, friction signals, and practical improvements."
					),
				},
				{
					"role": "user",
					"content": json.dumps(
						{
							"scope_type": scope_type,
							"period_key": period.key,
							"period_start": period.start.isoformat(),
							"period_end": period.end.isoformat(),
							"metrics": metrics,
						},
						ensure_ascii=False,
					),
				},
			],
		}
		data = json.dumps(payload).encode("utf-8")
		req = request.Request(
			self.ollama_url,
			data=data,
			headers={"Content-Type": "application/json"},
			method="POST",
		)
		with request.urlopen(req, timeout=self.ollama_timeout_seconds) as response:
			body = json.loads(response.read().decode("utf-8", errors="replace"))

		content = ((body.get("message") or {}).get("content") or "").strip()
		if not content:
			done_reason = body.get("done_reason") or body.get("error") or "unknown"
			raise ValueError(f"Ollama returned empty report content: {done_reason}")
		return self.parse_json_object(content)

	def parse_json_object(self, content: str):
		"""Parse a JSON object, tolerating simple code fences or extra text."""
		content = content.strip()
		if content.startswith("```"):
			lines = content.splitlines()
			if len(lines) >= 2 and lines[-1].strip() == "```":
				content = "\n".join(lines[1:-1]).strip()
		try:
			return json.loads(content)
		except json.JSONDecodeError:
			start = content.find("{")
			end = content.rfind("}")
			if start >= 0 and end > start:
				return json.loads(content[start:end + 1])
			raise

	async def save_report(self, period: TrendPeriod, scope_type: str, guild_id: int, user_id, metrics: dict, report: dict):
		"""Persist one generated communication trend report."""
		async with self.session_factory() as session:
			repo = CommunicationTrendAnalysisRepository(session)
			await repo.upsert_by_scope({
				"period_key": period.key,
				"period_start": period.start,
				"period_end": period.end,
				"scope_type": scope_type,
				"guild_id": guild_id,
				"user_id": user_id,
				"model": self.ollama_model,
				"message_count": metrics["message_count"],
				"edit_count": metrics["edit_count"],
				"delete_count": metrics["delete_count"],
				"analysis_count": metrics["analysis_count"],
				"max_score_avg": metrics["max_score_avg"],
				"metrics": json.dumps(metrics, ensure_ascii=False),
				"summary": self.format_report_field(report.get("summary")),
				"tendencies": self.format_report_field(report.get("tendencies")),
				"risks": self.format_report_field(report.get("risks")),
				"recommendations": self.format_report_field(report.get("recommendations")),
				"raw_result": json.dumps(report, ensure_ascii=False),
			})

	def format_report_field(self, value):
		"""Convert Ollama report fields into text for database storage."""
		if value is None:
			return None
		if isinstance(value, str):
			return value
		if isinstance(value, list):
			return "\n".join(str(item) for item in value)
		if isinstance(value, dict):
			return json.dumps(value, ensure_ascii=False)
		return str(value)

	def truncate_text(self, text_value: str, max_chars: int):
		"""Return text truncated to a maximum number of characters."""
		if len(text_value) <= max_chars:
			return text_value
		return text_value[:max_chars] + "..."
