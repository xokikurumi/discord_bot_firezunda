import asyncio
import hashlib
import ipaddress
import json
import re
import socket
import unicodedata
from pathlib import Path
from urllib import parse, request
from urllib.error import HTTPError, URLError

from bs4 import BeautifulSoup

import config
from repositories.log.message_analysis_feedback_repo import MessageAnalysisFeedbackRepository
from repositories.log.message_analysis_log_repo import MessageAnalysisLogRepository
from repositories.log.message_analysis_whitelist_repo import MessageAnalysisWhitelistRepository
from repositories.log.message_log_repo import MessageLogRepository


class MessageWatcherService:
	"""Analyze Discord messages with Ollama and notify authors when scores are high."""

	def __init__(self, session_factory, bot=None):
		"""Load Ollama connection settings and moderation threshold from config."""
		self.session_factory = session_factory
		self.bot = bot
		self.ollama_url = config.OLLAMA_URL
		self.ollama_model = config.OLLAMA_MODEL
		self.reaction_threshold = config.OLLAMA_REACTION_THRESHOLD
		self.dm_threshold = config.OLLAMA_DM_THRESHOLD
		self.confidence_threshold = config.OLLAMA_CONFIDENCE_THRESHOLD
		self.reaction_notify_guild_id = config.OLLAMA_REACTION_NOTIFY_GUILD_ID
		self.reaction_notify_channel_id = config.OLLAMA_REACTION_NOTIFY_CHANNEL_ID
		self.reaction_notify_mention = config.OLLAMA_REACTION_NOTIFY_MENTION
		self.enabled = config.OLLAMA_ANALYSIS_ENABLED
		self.timeout_seconds = config.OLLAMA_TIMEOUT_SECONDS
		self.context_max_chars = config.OLLAMA_CONTEXT_MAX_CHARS
		self.message_max_chars = config.OLLAMA_MESSAGE_MAX_CHARS
		self.num_predict = config.OLLAMA_NUM_PREDICT
		self.retry_context_max_chars = config.OLLAMA_RETRY_CONTEXT_MAX_CHARS
		self.analysis_system_prompt = config.OLLAMA_ANALYSIS_SYSTEM_PROMPT
		self.analysis_user_prompt_template = config.OLLAMA_ANALYSIS_USER_PROMPT_TEMPLATE
		self.analysis_prompt_version = config.OLLAMA_ANALYSIS_PROMPT_VERSION
		self.feedback_rag_enabled = config.OLLAMA_ANALYSIS_FEEDBACK_RAG_ENABLED
		self.feedback_rag_candidate_limit = config.OLLAMA_ANALYSIS_FEEDBACK_RAG_CANDIDATE_LIMIT
		self.feedback_rag_search_pool_limit = config.OLLAMA_ANALYSIS_FEEDBACK_RAG_SEARCH_POOL_LIMIT
		self.feedback_rag_max_examples = config.OLLAMA_ANALYSIS_FEEDBACK_RAG_MAX_EXAMPLES
		self.feedback_rag_min_similarity = config.OLLAMA_ANALYSIS_FEEDBACK_RAG_MIN_SIMILARITY
		self.feedback_embedding_rag_enabled = config.OLLAMA_ANALYSIS_FEEDBACK_EMBEDDING_RAG_ENABLED
		self.feedback_embedding_min_similarity = config.OLLAMA_ANALYSIS_FEEDBACK_EMBEDDING_MIN_SIMILARITY
		self.embedding_url = config.OLLAMA_EMBEDDING_URL
		self.embedding_model = config.OLLAMA_EMBEDDING_MODEL
		self.embedding_timeout_seconds = config.OLLAMA_EMBEDDING_TIMEOUT_SECONDS
		self.url_context_enabled = config.OLLAMA_ANALYSIS_URL_CONTEXT_ENABLED
		self.url_context_max_concurrency = config.OLLAMA_ANALYSIS_URL_CONTEXT_MAX_CONCURRENCY
		self.url_context_max_urls = config.OLLAMA_ANALYSIS_URL_CONTEXT_MAX_URLS
		self.url_context_timeout_seconds = config.OLLAMA_ANALYSIS_URL_CONTEXT_TIMEOUT_SECONDS
		self.url_context_max_bytes = config.OLLAMA_ANALYSIS_URL_CONTEXT_MAX_BYTES
		self.url_context_max_chars = config.OLLAMA_ANALYSIS_URL_CONTEXT_MAX_CHARS
		self.fewshot_examples = self.load_fewshot_examples(
			config.OLLAMA_ANALYSIS_FEWSHOT_PATH,
			config.OLLAMA_ANALYSIS_FEWSHOT_MAX_EXAMPLES,
		)
		self.semaphore = asyncio.Semaphore(config.OLLAMA_MAX_CONCURRENCY)
		self.url_context_semaphore = asyncio.Semaphore(max(1, self.url_context_max_concurrency))
		self.context_limit = 10

	async def watch(self, message):
		"""Analyze one Discord message and optionally DM the author."""
		# Skip command-like posts and disabled analysis before calling Ollama.
		if not self.enabled:
			return None

		if not message.content or message.content.startswith("!"):
			return None

		if await self.is_analysis_whitelisted(
			message.guild.id,
			message.channel.id,
			message.author.id,
			message.content,
		):
			return None

		context_messages = await self.get_context_messages(message)
		result = await self.analyze_message(message.content, context_messages, message.guild.id)
		if result is None:
			return None

		should_react = self.should_react(result)
		should_notify = self.should_notify(result)
		await self.save_analysis_result(message, result, should_react, should_notify)

		if should_react:
			await self.add_detection_reaction(message)
			await self.notify_reaction_channel(message, result)

		if should_notify:
			await self.notify_author(message, result)

		return result

	async def save_analysis_result(self, message, result: dict, should_react: bool, should_notify: bool):
		"""Persist one Ollama analysis result for later inspection."""
		await self.save_analysis_result_data(
			message.id,
			message.guild.id,
			message.channel.id,
			message.author.id,
			result,
			should_react,
			should_notify,
		)

	async def save_analysis_result_data(
		self,
		message_id: int,
		guild_id: int,
		channel_id: int,
		user_id: int,
		result: dict,
		should_react: bool,
		should_notify: bool,
	):
		"""Persist one analysis result from either Discord events or stored logs."""
		async with self.session_factory() as session:
			repo = MessageAnalysisLogRepository(session)
			await repo.insert_ignore({
				"message_id": message_id,
				"guild_id": guild_id,
				"channel_id": channel_id,
				"user_id": user_id,
				"model": self.ollama_model,
				"aggression": result["aggression"],
				"intimidation": result["intimidation"],
				"insult": result["insult"],
				"sarcasm": result["sarcasm"],
				"snide": result["snide"],
				"discomfort": result["discomfort"],
				"max_score": self.max_score(result),
				"targeted": result["targeted"],
				"confidence": result["confidence"],
				"context_dependency": result["context_dependency"],
				"reason": result.get("reason"),
				"raw_result": json.dumps(result, ensure_ascii=False),
				"prompt_version": result.get("prompt_version"),
				"prompt_hash": result.get("prompt_hash"),
				"retrieved_rag_cases": json.dumps(
					result.get("retrieved_rag_cases", []),
					ensure_ascii=False,
				),
				"should_react": should_react,
				"should_notify": should_notify,
			})

	async def analyze_logged_message(self, message_log):
		"""Analyze a stored message without reactions or user notifications."""
		if not self.enabled:
			return False

		if message_log.bot_flg:
			return False

		if not message_log.content or message_log.content.startswith("!"):
			return False

		if await self.is_analysis_whitelisted(
			message_log.guild_id,
			message_log.channel_id,
			message_log.user_id,
			message_log.content,
		):
			return False

		context_messages = await self.get_context_messages_for_log(message_log)
		result = await self.analyze_message(message_log.content, context_messages, message_log.guild_id)
		if result is None:
			return False

		await self.save_analysis_result_data(
			message_log.message_id,
			message_log.guild_id,
			message_log.channel_id,
			message_log.user_id,
			result,
			False,
			False,
		)
		return True

	async def get_context_messages(self, message):
		"""Load the previous channel messages used as conversation context."""
		async with self.session_factory() as session:
			repo = MessageLogRepository(session)
			return await repo.get_recent_context(
				message.channel.id,
				message.id,
				self.context_limit,
			)

	async def get_context_messages_for_log(self, message_log):
		"""Load previous stored channel messages for a logged target message."""
		async with self.session_factory() as session:
			repo = MessageLogRepository(session)
			return await repo.get_recent_context(
				message_log.channel_id,
				message_log.message_id,
				self.context_limit,
			)

	async def add_feedback(self, guild_id: int, reviewer_id: int, message_id: int, label: str, note: str = ""):
		"""Store administrator feedback for an analysis result."""
		normalized_label = self.normalize_feedback_label(label)
		async with self.session_factory() as session:
			message_repo = MessageLogRepository(session)
			message_log = await message_repo.get_by_message_id(message_id)
			if message_log and message_log.guild_id != guild_id:
				raise ValueError("message_id belongs to a different guild.")

			analysis_repo = MessageAnalysisLogRepository(session)
			analysis_log = await analysis_repo.get_by_message_id(message_id)
			corrected_result = self.build_corrected_feedback_result(
				normalized_label,
				analysis_log,
				note,
			)
			embedding_data = {}
			if corrected_result and message_log:
				embedding_data = await self.build_feedback_embedding_data_limited(
					message_log.content or "",
					normalized_label,
					note,
				)
			repo = MessageAnalysisFeedbackRepository(session)
			await repo.insert({
				"message_id": message_id,
				"guild_id": guild_id,
				"channel_id": message_log.channel_id if message_log else None,
				"user_id": message_log.user_id if message_log else None,
				"reviewer_id": reviewer_id,
				"label": normalized_label,
				"review_status": "CONFIRMED" if corrected_result else "PENDING",
				"corrected_result_json": json.dumps(corrected_result, ensure_ascii=False) if corrected_result else None,
				"note": note.strip() or None,
				**embedding_data,
			})
		return normalized_label

	async def add_whitelist_rule(
		self,
		guild_id: int,
		created_by: int,
		rule_type: str,
		pattern: str,
		note: str = "",
	):
		"""Add one guild-scoped analysis whitelist rule."""
		normalized_type = self.normalize_whitelist_rule_type(rule_type)
		normalized_pattern = self.normalize_whitelist_pattern(normalized_type, pattern)
		async with self.session_factory() as session:
			repo = MessageAnalysisWhitelistRepository(session)
			await repo.insert({
				"guild_id": guild_id,
				"rule_type": normalized_type,
				"pattern": normalized_pattern,
				"created_by": created_by,
				"note": note.strip() or None,
				"enabled": True,
			})
		return normalized_type, normalized_pattern

	async def list_whitelist_rules(self, guild_id: int, include_disabled: bool = False):
		"""Return whitelist rules for command display."""
		async with self.session_factory() as session:
			repo = MessageAnalysisWhitelistRepository(session)
			return await repo.list_by_guild(guild_id, include_disabled)

	async def set_whitelist_rule_enabled(self, guild_id: int, rule_id: int, enabled: bool):
		"""Enable or disable one whitelist rule."""
		async with self.session_factory() as session:
			repo = MessageAnalysisWhitelistRepository(session)
			return await repo.set_enabled(guild_id, rule_id, enabled)

	async def is_analysis_whitelisted(self, guild_id: int, channel_id: int, user_id: int, content: str):
		"""Return True when a message matches an enabled analysis whitelist rule."""
		if not guild_id:
			return False
		async with self.session_factory() as session:
			repo = MessageAnalysisWhitelistRepository(session)
			rules = await repo.list_by_guild(guild_id)

		normalized_content = self.normalize_whitelist_text(content)
		for rule in rules:
			if self.matches_whitelist_rule(rule, channel_id, user_id, normalized_content):
				return True
		return False

	def matches_whitelist_rule(self, rule, channel_id: int, user_id: int, normalized_content: str):
		"""Return True when one whitelist rule matches the target message."""
		rule_type = rule.rule_type
		pattern = str(rule.pattern or "").strip()
		if rule_type == "text_exact":
			return normalized_content == self.normalize_whitelist_text(pattern)
		if rule_type == "text_contains":
			return self.normalize_whitelist_text(pattern) in normalized_content
		if rule_type == "user":
			return str(user_id) == pattern
		if rule_type == "channel":
			return str(channel_id) == pattern
		return False

	def normalize_whitelist_rule_type(self, rule_type: str):
		"""Normalize supported whitelist rule type aliases."""
		aliases = {
			"exact": "text_exact",
			"text": "text_exact",
			"text_exact": "text_exact",
			"contains": "text_contains",
			"text_contains": "text_contains",
			"keyword": "text_contains",
			"user": "user",
			"user_id": "user",
			"channel": "channel",
			"channel_id": "channel",
		}
		normalized = aliases.get((rule_type or "").strip().lower())
		if normalized is None:
			raise ValueError("rule_type must be one of: text_exact, text_contains, user, channel")
		return normalized

	def normalize_whitelist_pattern(self, rule_type: str, pattern: str):
		"""Validate and normalize a whitelist pattern."""
		normalized = str(pattern or "").strip()
		if not normalized:
			raise ValueError("pattern must not be empty.")
		if rule_type in {"user", "channel"}:
			normalized = self.extract_discord_id(normalized)
			if not normalized:
				raise ValueError("user/channel whitelist pattern must contain a Discord id.")
		return normalized

	def normalize_whitelist_text(self, text: str):
		"""Normalize message text before whitelist matching."""
		return re.sub(r"\s+", " ", text or "").strip()

	def extract_discord_id(self, value: str):
		"""Extract a Discord snowflake from raw text or mention syntax."""
		match = re.search(r"\d{15,25}", value or "")
		return match.group(0) if match else ""

	def normalize_feedback_label(self, label: str):
		"""Normalize supported feedback labels and common aliases."""
		aliases = {
			"ok": "correct",
			"correct": "correct",
			"true": "correct",
			"正しい": "correct",
			"fp": "false_positive",
			"false_positive": "false_positive",
			"誤検知": "false_positive",
			"fn": "false_negative",
			"false_negative": "false_negative",
			"見逃し": "false_negative",
			"unsure": "unsure",
			"unknown": "unsure",
			"不明": "unsure",
		}
		normalized = aliases.get(label.strip().lower())
		if normalized is None:
			raise ValueError("label must be one of: correct, false_positive, false_negative, unsure")
		return normalized

	def build_corrected_feedback_result(self, label: str, analysis_log, note: str = ""):
		"""Build administrator-corrected scores when the current command provides enough information."""
		note_result = self.extract_corrected_result_from_note(note)
		if note_result:
			return note_result

		if label == "correct" and analysis_log is not None:
			return self.result_from_analysis_log(analysis_log)

		if label == "false_positive":
			return {
				"aggression": 0,
				"intimidation": 0,
				"insult": 0,
				"sarcasm": 0,
				"snide": 0,
				"discomfort": 5,
				"targeted": False,
				"confidence": 90,
				"context_dependency": True,
				"reason": "管理者過検出",
			}

		return None

	def extract_corrected_result_from_note(self, note: str):
		"""Parse an optional corrected JSON object embedded in administrator notes."""
		if not note or "{" not in note:
			return None
		json_text = self.extract_first_json_object(note)
		if not json_text:
			return None
		try:
			return self.normalize_result(json.loads(json_text))
		except (json.JSONDecodeError, TypeError, ValueError):
			return None

	def result_from_analysis_log(self, analysis_log):
		"""Convert a stored analysis row into the JSON result schema."""
		return {
			"aggression": analysis_log.aggression,
			"intimidation": analysis_log.intimidation,
			"insult": analysis_log.insult,
			"sarcasm": analysis_log.sarcasm,
			"snide": analysis_log.snide,
			"discomfort": analysis_log.discomfort,
			"targeted": analysis_log.targeted,
			"confidence": analysis_log.confidence,
			"context_dependency": analysis_log.context_dependency,
			"reason": analysis_log.reason or "",
		}

	async def analyze_message(
		self,
		content: str,
		context_messages=None,
		guild_id=None,
		use_exact_feedback: bool = True,
		use_feedback_rag: bool = True,
		excluded_feedback_message_id=None,
	):
		"""Run moderation analysis for message text and return normalized scores."""
		# urllib is blocking, so run the Ollama request outside the event loop.
		try:
			if use_exact_feedback:
				exact_feedback_result = await self.retrieve_exact_feedback_result(content, guild_id)
				if exact_feedback_result:
					return exact_feedback_result

			feedback_examples = []
			if use_feedback_rag:
				feedback_examples = await self.retrieve_feedback_rag_examples(
					content,
					context_messages or [],
					guild_id,
					excluded_feedback_message_id,
				)
			url_context_text = await self.build_url_context_text_limited(content)
			async with self.semaphore:
				return await asyncio.to_thread(
					self._request_ollama,
					content,
					context_messages or [],
					feedback_examples,
					url_context_text,
				)
		except HTTPError as e:
			error_body = e.read().decode("utf-8", errors="replace")
			print(f"[ERROR] ollama analysis failed: HTTP {e.code}: {error_body}")
			return None
		except (URLError, TimeoutError, json.JSONDecodeError, KeyError, ValueError) as e:
			print(f"[ERROR] ollama analysis failed: {e}")
			return None

	def _request_ollama(self, content: str, context_messages, feedback_examples=None, url_context_text=""):
		"""Send a blocking chat request to Ollama and parse its JSON response."""
		# Ask Ollama for strict JSON so the caller can score messages deterministically.
		try:
			return self._request_ollama_once(
				content,
				context_messages,
				self.context_max_chars,
				feedback_examples or [],
				url_context_text,
				self.num_predict,
			)
		except ValueError as e:
			if not self.should_retry_ollama_response(e):
				raise
			print("[INFO] ollama response was truncated or invalid; retrying with shorter context and larger output limit.")
			try:
				return self._request_ollama_once(
					content,
					context_messages,
					self.retry_context_max_chars,
					feedback_examples or [],
					self.truncate_text(url_context_text, self.retry_context_max_chars),
					self.retry_num_predict(),
				)
			except ValueError as retry_error:
				if not self.should_retry_ollama_response(retry_error):
					raise
				print("[INFO] ollama retry failed; retrying with minimal analysis prompt.")
				return self._request_ollama_minimal(content)

	def retry_num_predict(self):
		"""Return the retry output limit while preserving Ollama special values."""
		if self.num_predict <= 0:
			return self.num_predict
		return max(self.num_predict * 2, 1024)

	def minimal_retry_num_predict(self):
		"""Return a bounded output limit for the final minimal JSON retry."""
		if self.num_predict <= 0:
			return 1024
		return max(512, min(self.num_predict, 1024))

	def _request_ollama_minimal(self, content: str):
		"""Send a final small prompt when normal analysis prompts do not terminate."""
		target_content = self.truncate_text(content, min(self.message_max_chars, 500))
		messages = [
			{
				"role": "system",
				"content": config.DEFAULT_OLLAMA_ANALYSIS_SYSTEM_PROMPT,
			},
			{
				"role": "user",
				"content": (
					"Score only this latest target message.\n"
					"Return strict JSON only.\n\n"
					f"Latest target message to score:\n{target_content}"
				),
			},
		]
		result = self._request_ollama_messages(messages, self.minimal_retry_num_predict())
		result["prompt_version"] = f"{self.analysis_prompt_version}-minimal-retry"
		result["prompt_hash"] = self.prompt_hash(messages)
		result["retrieved_rag_cases"] = []
		return result

	def _request_ollama_once(
		self,
		content: str,
		context_messages,
		context_max_chars: int,
		feedback_examples,
		url_context_text: str,
		num_predict: int,
	):
		"""Send one blocking Ollama request and parse the moderation JSON."""
		context_text = self.build_context_text(context_messages, context_max_chars)
		target_content = self.truncate_text(content, self.message_max_chars)
		messages = [
			{
				"role": "system",
				"content": self.analysis_system_prompt,
			},
			*self.build_fewshot_messages(),
			*self.build_feedback_rag_messages(feedback_examples),
			{
				"role": "user",
				"content": self.build_analysis_user_prompt(
					context_text,
					target_content,
					url_context_text,
				),
			},
		]
		payload = {
			"model": self.ollama_model,
			"stream": False,
			"format": "json",
			"options": {
				"temperature": 0,
				"num_predict": num_predict,
			},
			"messages": messages,
		}
		result = self._request_ollama_payload(payload)
		result["prompt_version"] = self.analysis_prompt_version
		result["prompt_hash"] = self.prompt_hash(messages)
		result["retrieved_rag_cases"] = self.rag_case_references(feedback_examples)
		return result

	async def retrieve_exact_feedback_result(self, content: str, guild_id):
		"""Return an administrator-confirmed result for the same guild and exact text."""
		if not guild_id:
			return None

		try:
			async with self.session_factory() as session:
				repo = MessageAnalysisFeedbackRepository(session)
				row = await repo.find_latest_confirmed_by_content(guild_id, content)
		except Exception as e:
			print(f"[ERROR] analysis exact feedback load failed: {e}")
			return None

		if not row:
			return None

		feedback, _message_log, _analysis_log = row
		result = self.parse_corrected_result_json(feedback.corrected_result_json)
		if not result:
			return None

		result["prompt_version"] = f"{self.analysis_prompt_version}-exact-feedback"
		result["prompt_hash"] = ""
		result["retrieved_rag_cases"] = [{
			"case_id": feedback.id,
			"similarity": 100,
			"label": feedback.label,
			"match": "exact",
		}]
		return result

	def _request_ollama_messages(self, messages, num_predict: int):
		"""Send prepared Ollama chat messages and parse the moderation JSON."""
		payload = {
			"model": self.ollama_model,
			"stream": False,
			"format": "json",
			"options": {
				"temperature": 0,
				"num_predict": num_predict,
			},
			"messages": messages,
		}
		return self._request_ollama_payload(payload)

	def _request_ollama_payload(self, payload: dict):
		"""Send one blocking Ollama request payload and parse the moderation JSON."""
		data = json.dumps(payload).encode("utf-8")
		req = request.Request(
			self.ollama_url,
			data=data,
			headers={"Content-Type": "application/json"},
			method="POST",
		)

		with request.urlopen(req, timeout=self.timeout_seconds) as response:
			raw_body = response.read().decode("utf-8", errors="replace")
			if not raw_body.strip():
				raise ValueError("Ollama returned an empty HTTP response body")
			body = json.loads(raw_body)

		content = self.extract_ollama_message_content(body)
		if body.get("done_reason") == "length":
			raise ValueError("Ollama response reached length limit")
		analysis = self.parse_analysis_json(content)
		return self.normalize_result(analysis)

	async def retrieve_feedback_rag_examples(
		self,
		content: str,
		context_messages,
		guild_id,
		excluded_message_id=None,
	):
		"""Retrieve similar administrator feedback examples for the target message."""
		if not self.feedback_rag_enabled or not guild_id:
			return []
		if self.feedback_rag_candidate_limit <= 0 or self.feedback_rag_max_examples <= 0:
			return []

		try:
			async with self.session_factory() as session:
				repo = MessageAnalysisFeedbackRepository(session)
				rows = await repo.list_recent_rag_candidates(
					guild_id,
					self.feedback_rag_pool_limit(),
				)
		except Exception as e:
			print(f"[ERROR] analysis feedback RAG load failed: {e}")
			return []

		query_text = self.build_rag_search_text(content, context_messages)
		query_content = self.normalize_rag_text(content)
		query_embedding = None
		if any(getattr(feedback, "embedding_json", None) for feedback, _message_log, _analysis_log in rows):
			query_embedding = self.feedback_query_embedding(query_text)
		examples = []
		for feedback, message_log, analysis_log in rows:
			if excluded_message_id is not None and feedback.message_id == excluded_message_id:
				continue
			similarity = self.feedback_case_similarity(
				query_text,
				query_content,
				query_embedding,
				feedback,
				message_log,
			)
			if similarity < self.feedback_rag_min_similarity:
				continue
			corrected_result = self.parse_corrected_result_json(feedback.corrected_result_json)
			if not corrected_result:
				continue
			examples.append({
				"case_id": feedback.id,
				"similarity": similarity,
				"content": self.truncate_text((message_log.content or "").replace("\n", " "), 240),
				"label": feedback.label,
				"note": self.truncate_text((feedback.note or "").replace("\n", " "), 160),
				"corrected_result": corrected_result,
				"previous_analysis": self.format_analysis_scores(analysis_log),
			})

		examples.sort(key=lambda item: item["similarity"], reverse=True)
		return examples[:self.feedback_rag_max_examples]

	def feedback_rag_pool_limit(self):
		"""Return the number of confirmed feedback rows to scan for RAG similarity."""
		return max(
			self.feedback_rag_candidate_limit,
			self.feedback_rag_search_pool_limit,
			self.feedback_rag_max_examples,
		)

	def should_retry_ollama_response(self, error: ValueError):
		"""Return True when a failed Ollama response may succeed with a shorter retry."""
		message = str(error)
		return (
			"empty message content: length" in message
			or "response reached length limit" in message
			or "Ollama returned non-JSON content: {" in message
		)

	def load_fewshot_examples(self, path: str, max_examples: int):
		"""Load fixed few-shot moderation examples from a JSON file."""
		if not path or max_examples <= 0:
			return []

		file_path = Path(path)
		if not file_path.is_absolute():
			file_path = Path.cwd() / file_path
		if not file_path.exists():
			return []

		try:
			raw_examples = json.loads(file_path.read_text(encoding="utf-8"))
		except Exception as e:
			print(f"[ERROR] analysis few-shot file load failed path={file_path}: {e}")
			return []

		if not isinstance(raw_examples, list):
			print(f"[ERROR] analysis few-shot file must contain a JSON array: path={file_path}")
			return []

		examples = []
		for raw_example in raw_examples:
			example = self.normalize_fewshot_example(raw_example)
			if example:
				examples.append(example)
			if len(examples) >= max_examples:
				break
		return examples

	def normalize_fewshot_example(self, raw_example):
		"""Normalize one fixed few-shot example row."""
		if not isinstance(raw_example, dict):
			return None

		input_text = str(raw_example.get("input") or raw_example.get("message") or "").strip()
		output = raw_example.get("output") or raw_example.get("judgment")
		if not input_text or not isinstance(output, dict):
			return None

		normalized_output = self.normalize_result(output)
		return {
			"name": str(raw_example.get("name") or "").strip(),
			"context": str(raw_example.get("context") or "").strip(),
			"input": input_text,
			"output": normalized_output,
			"note": str(raw_example.get("note") or "").strip(),
		}

	def build_fewshot_messages(self):
		"""Build chat messages that show fixed administrator-confirmed examples."""
		if not self.fewshot_examples:
			return []

		messages = [
			{
				"role": "user",
				"content": (
					"Below are administrator-confirmed moderation examples. "
					"Use them as reference examples, not as rules to copy blindly. "
					"Prioritize the current target message and its context."
				),
			}
		]
		for index, example in enumerate(self.fewshot_examples, start=1):
			messages.append({
				"role": "user",
				"content": self.format_fewshot_input(index, example),
			})
			messages.append({
				"role": "assistant",
				"content": json.dumps(example["output"], ensure_ascii=False),
			})
		return messages

	def format_fewshot_input(self, index: int, example: dict):
		"""Format one fixed few-shot example input."""
		lines = [f"Example {index}"]
		if example["name"]:
			lines.append(f"Name: {example['name']}")
		if example["context"]:
			lines.append(f"Context: {example['context']}")
		lines.append("Latest target message to score:")
		lines.append(example["input"])
		if example["note"]:
			lines.append(f"Administrator note: {example['note']}")
		return "\n".join(lines)

	def build_feedback_rag_messages(self, examples):
		"""Build a dynamic prompt section from similar administrator feedback."""
		if not examples:
			return []

		messages = [{
			"role": "user",
			"content": (
				"Below are administrator-confirmed examples retrieved for the latest target message. "
				"Treat each assistant response as the corrected output for that past case. "
				"Use these examples as dynamic few-shot calibration, not as rules to copy blindly."
			),
		}]
		for index, example in enumerate(examples, start=1):
			lines = [
				f"Administrator-confirmed retrieved example {index}",
				f"Similarity: {example['similarity']}",
				"Context:",
				self.feedback_example_context(example),
				"Target message:",
				example["content"],
			]
			if example["note"]:
				lines.append(f"Administrator note: {example['note']}")
			if example["previous_analysis"]:
				lines.append(f"Previous model analysis before feedback: {example['previous_analysis']}")
			messages.append({
				"role": "user",
				"content": "\n".join(lines).strip(),
			})
			messages.append({
				"role": "assistant",
				"content": json.dumps(example["corrected_result"], ensure_ascii=False),
			})

		return messages

	def feedback_example_context(self, example: dict):
		"""Return a short context line for one retrieved feedback example."""
		label_context = {
			"correct": "管理者が過去判定を適切と確認した事例。",
			"false_positive": "管理者が過検出と判断し、低スコアへ補正した事例。",
			"false_negative": "管理者が見逃しと判断し、補正結果を登録した事例。",
			"unsure": "管理者が境界または不明と判断し、補正結果を登録した事例。",
		}
		return label_context.get(example["label"], "管理者確認済みの補正事例。")

	def build_rag_search_text(self, content: str, context_messages):
		"""Build retrieval text from target message and pre-analysis context."""
		lines = [
			"対象メッセージ:",
			self.normalize_rag_text(content),
		]
		if context_messages:
			lines.append("直前会話:")
			for message in context_messages[-5:]:
				message_content = (message.content or "").replace("\n", " ")
				lines.append(self.normalize_rag_text(message_content))
		if len((content or "").strip()) <= 12:
			lines.append("補足: 短文")
		return "\n".join(lines)

	def build_feedback_case_search_text(self, feedback, message_log):
		"""Build searchable text for one administrator-confirmed feedback case."""
		lines = [
			"対象メッセージ:",
			self.normalize_rag_text(message_log.content),
			"管理者判断:",
			feedback.label,
		]
		if feedback.note:
			lines.extend(["補足:", self.normalize_rag_text(feedback.note)])
		return "\n".join(lines)

	def parse_corrected_result_json(self, content: str):
		"""Parse a stored administrator-corrected moderation result."""
		if not content:
			return None
		try:
			return self.normalize_result(json.loads(content))
		except (json.JSONDecodeError, TypeError, ValueError):
			return None

	def rag_case_references(self, examples):
		"""Return compact RAG references for audit storage."""
		return [
			{
				"case_id": example["case_id"],
				"similarity": example["similarity"],
				"label": example["label"],
			}
			for example in examples
		]

	def prompt_hash(self, messages):
		"""Return a stable hash of the prompt messages sent to the model."""
		prompt_text = json.dumps(messages, ensure_ascii=False, sort_keys=True)
		return hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()

	def format_analysis_scores(self, analysis_log):
		"""Format a compact previous analysis summary for feedback RAG."""
		if analysis_log is None:
			return ""
		return (
			f"aggression={analysis_log.aggression}, "
			f"intimidation={analysis_log.intimidation}, "
			f"insult={analysis_log.insult}, "
			f"sarcasm={analysis_log.sarcasm}, "
			f"snide={analysis_log.snide}, "
			f"discomfort={analysis_log.discomfort}, "
			f"targeted={analysis_log.targeted}, "
			f"confidence={analysis_log.confidence}, "
			f"context_dependency={analysis_log.context_dependency}, "
			f"reason={self.truncate_text(analysis_log.reason or '-', 80)}"
		)

	def text_similarity(self, left: str, right: str):
		"""Return a lightweight lexical similarity score from 0 to 100."""
		left_tokens = self.text_features(left)
		right_tokens = self.text_features(right)
		if not left_tokens or not right_tokens:
			return 0
		overlap = len(left_tokens & right_tokens)
		return int(round((overlap / min(len(left_tokens), len(right_tokens))) * 100))

	def feedback_case_similarity(self, query_text: str, query_content: str, query_embedding, feedback, message_log):
		"""Score one feedback case using target text, context, and administrator metadata."""
		case_content = self.normalize_rag_text(message_log.content)
		content_similarity = self.text_similarity(query_content, case_content)
		context_similarity = self.text_similarity(query_text, self.build_feedback_case_search_text(feedback, message_log))
		note_similarity = self.text_similarity(query_content, feedback.note or "")
		embedding_similarity = self.feedback_embedding_similarity(query_embedding, feedback)
		score = max(
			content_similarity,
			int(round(context_similarity * 0.85)),
			int(round(note_similarity * 0.75)),
			embedding_similarity,
		)

		if query_content and query_content == case_content:
			score = 100
		elif query_content and case_content and (query_content in case_content or case_content in query_content):
			score = max(score, 88)
		if len(query_content) <= 12 and content_similarity >= 60:
			score = max(score, min(100, content_similarity + 15))
		if feedback.label in {"false_positive", "false_negative", "unsure"} and note_similarity >= 45:
			score = max(score, min(100, note_similarity + 10))
		return max(0, min(100, score))

	def feedback_query_embedding(self, query_text: str):
		"""Return an embedding vector for a RAG query when embedding RAG is enabled."""
		if not self.feedback_embedding_rag_enabled:
			return None
		try:
			return self.request_embedding(query_text)
		except Exception as e:
			print(f"[ERROR] analysis feedback embedding query failed: {e}")
			return None

	def feedback_embedding_similarity(self, query_embedding, feedback):
		"""Return cosine similarity between query and stored feedback embeddings as 0-100."""
		if query_embedding is None or not getattr(feedback, "embedding_json", None):
			return 0
		if feedback.embedding_model and feedback.embedding_model != self.embedding_model:
			return 0

		try:
			case_embedding = json.loads(feedback.embedding_json)
		except (TypeError, json.JSONDecodeError):
			return 0

		similarity = self.cosine_similarity(query_embedding, case_embedding)
		score = int(round(similarity * 100))
		if score < self.feedback_embedding_min_similarity:
			return 0
		return max(0, min(100, score))

	async def build_feedback_embedding_data_limited(self, content: str, label: str, note: str = "", force: bool = False):
		"""Build feedback embedding columns without blocking the event loop."""
		if not force and not self.feedback_embedding_rag_enabled:
			return {}
		try:
			return await asyncio.to_thread(self.build_feedback_embedding_data, content, label, note)
		except Exception as e:
			print(f"[ERROR] analysis feedback embedding build failed: {e}")
			return {}

	def build_feedback_embedding_data(self, content: str, label: str, note: str = ""):
		"""Build database columns for one administrator feedback embedding."""
		embedding_text = self.build_feedback_embedding_text(content, label, note)
		embedding = self.request_embedding(embedding_text)
		return {
			"embedding_model": self.embedding_model,
			"embedding_text_hash": self.embedding_text_hash(embedding_text),
			"embedding_dim": len(embedding),
			"embedding_json": json.dumps(embedding, separators=(",", ":")),
		}

	def build_feedback_embedding_text(self, content: str, label: str, note: str = ""):
		"""Build text used to embed one administrator-confirmed feedback case."""
		lines = [
			"target:",
			self.normalize_rag_text(content),
			"label:",
			label or "",
		]
		if note:
			lines.extend(["note:", self.normalize_rag_text(note)])
		return "\n".join(lines).strip()

	def embedding_text_hash(self, text: str):
		"""Return a stable hash for the embedded text."""
		return hashlib.sha256((text or "").encode("utf-8")).hexdigest()

	def request_embedding(self, text: str):
		"""Request one embedding vector from Ollama."""
		payload = {
			"model": self.embedding_model,
			"prompt": text or "",
		}
		data = json.dumps(payload).encode("utf-8")
		req = request.Request(
			self.embedding_url,
			data=data,
			headers={"Content-Type": "application/json"},
			method="POST",
		)

		with request.urlopen(req, timeout=self.embedding_timeout_seconds) as response:
			raw_body = response.read().decode("utf-8", errors="replace")
			if not raw_body.strip():
				raise ValueError("Ollama embedding returned an empty HTTP response body")
			body = json.loads(raw_body)

		embedding = body.get("embedding")
		if embedding is None and isinstance(body.get("embeddings"), list) and body["embeddings"]:
			embedding = body["embeddings"][0]
		if not isinstance(embedding, list) or not embedding:
			raise ValueError("Ollama embedding response did not contain an embedding vector")
		return [float(value) for value in embedding]

	def cosine_similarity(self, left, right):
		"""Return cosine similarity for two vectors."""
		if not left or not right or len(left) != len(right):
			return 0.0
		dot = 0.0
		left_norm = 0.0
		right_norm = 0.0
		for left_value, right_value in zip(left, right):
			dot += left_value * right_value
			left_norm += left_value * left_value
			right_norm += right_value * right_value
		if left_norm <= 0 or right_norm <= 0:
			return 0.0
		return dot / ((left_norm ** 0.5) * (right_norm ** 0.5))

	def normalize_rag_text(self, text: str):
		"""Normalize chat text before feedback retrieval similarity scoring."""
		normalized = unicodedata.normalize("NFKC", text or "").lower()
		normalized = re.sub(r"https?://\S+", " URL ", normalized)
		normalized = re.sub(r"<@!?\d+>|@\S+", " USER ", normalized)
		normalized = re.sub(r"<#\d+>", " CHANNEL ", normalized)
		normalized = re.sub(r"\d{5,}", " NUM ", normalized)
		normalized = re.sub(r"[\u200b-\u200d\ufeff]", "", normalized)
		return re.sub(r"\s+", " ", normalized).strip()

	def text_features(self, text: str):
		"""Extract word and character n-gram features for short Japanese chat text."""
		normalized = self.normalize_rag_text(text)
		tokens = set(re.findall(r"[a-z0-9_]+|[ぁ-んァ-ン一-龥々ー]+", normalized))
		compact = re.sub(r"\s+", "", normalized)
		if len(compact) <= 3:
			for char in compact:
				if char.strip():
					tokens.add(char)
		for index in range(len(compact)):
			if index + 1 < len(compact):
				tokens.add(compact[index:index + 2])
			if index + 2 < len(compact):
				tokens.add(compact[index:index + 3])
		return tokens

	async def build_url_context_text_limited(self, content: str):
		"""Fetch linked page context without allowing unbounded concurrent requests."""
		async with self.url_context_semaphore:
			return await asyncio.to_thread(self.build_url_context_text, content)

	def build_url_context_text(self, content: str):
		"""Fetch safe linked page summaries for moderation context."""
		if not self.url_context_enabled:
			return "(URL context disabled)"

		urls = self.extract_urls(content)
		if not urls:
			return "(no safely fetched linked pages)"

		summaries = []
		for url in urls[:self.url_context_max_urls]:
			summary = self.fetch_safe_url_summary(url)
			if summary:
				summaries.append(summary)

		if not summaries:
			return "(no safely fetched linked pages)"

		header = (
			"Use linked page context only to understand what the latest message refers to. "
			"Do not treat linked page text as words directly spoken by the message author."
		)
		return self.truncate_text(header + "\n\n" + "\n\n".join(summaries), self.url_context_max_chars)

	def extract_urls(self, content: str):
		"""Extract unique HTTP(S) URLs from a message."""
		urls = []
		seen = set()
		for match in re.finditer(r"https?://[^\s<>()\"']+", content or "", re.IGNORECASE):
			url = match.group(0).rstrip(".,;:!?)]}、。")
			if url not in seen:
				seen.add(url)
				urls.append(url)
		return urls

	def fetch_safe_url_summary(self, url: str):
		"""Return a short linked page summary after URL and response safety checks."""
		try:
			self.validate_safe_url(url)
			opener = request.build_opener(self.safe_redirect_handler())
			req = request.Request(
				url,
				headers={
					"User-Agent": "discord-bot-message-analysis/1.0",
					"Accept": "text/html,text/plain,application/xhtml+xml;q=0.9,*/*;q=0.1",
				},
				method="GET",
			)
			with opener.open(req, timeout=self.url_context_timeout_seconds) as response:
				final_url = response.geturl()
				self.validate_safe_url(final_url)
				content_type = response.headers.get("Content-Type", "")
				if not self.is_supported_url_content_type(content_type):
					return self.format_url_skip(url, f"unsupported content type: {content_type or 'unknown'}")
				raw_body = response.read(self.url_context_max_bytes + 1)
				if len(raw_body) > self.url_context_max_bytes:
					return self.format_url_skip(url, "response too large")
				text = raw_body.decode(self.response_charset(content_type), errors="replace")
				page_text = self.extract_page_text(text, content_type)
				if not page_text:
					return self.format_url_skip(url, "no readable text")
				return self.format_url_summary(final_url, content_type, page_text)
		except Exception as e:
			return self.format_url_skip(url, str(e))

	def safe_redirect_handler(self):
		"""Build a redirect handler that rejects unsafe redirect targets."""
		service = self

		class SafeRedirectHandler(request.HTTPRedirectHandler):
			def redirect_request(self, req, fp, code, msg, headers, newurl):
				service.validate_safe_url(newurl)
				return super().redirect_request(req, fp, code, msg, headers, newurl)

		return SafeRedirectHandler

	def validate_safe_url(self, url: str):
		"""Raise ValueError when a URL is unsafe for server-side fetching."""
		parsed = parse.urlparse(url)
		if parsed.scheme.lower() not in {"http", "https"}:
			raise ValueError("unsupported URL scheme")
		if parsed.username or parsed.password:
			raise ValueError("URL userinfo is not allowed")
		if not parsed.hostname:
			raise ValueError("URL host is missing")
		if parsed.port and parsed.port not in {80, 443}:
			raise ValueError("URL port is not allowed")

		host = parsed.hostname.strip().rstrip(".")
		if host.lower() in {"localhost", "localhost.localdomain"}:
			raise ValueError("localhost is not allowed")

		try:
			ipaddress.ip_address(host)
			addresses = {host}
		except ValueError:
			addresses = self.resolve_host_addresses(host)

		if not addresses:
			raise ValueError("host did not resolve")

		for address in addresses:
			if not self.is_public_ip_address(address):
				raise ValueError(f"unsafe host address: {address}")

	def resolve_host_addresses(self, host: str):
		"""Resolve a hostname and return all address strings."""
		try:
			results = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
		except socket.gaierror as e:
			raise ValueError(f"host resolution failed: {e}") from e
		return {result[4][0] for result in results}

	def is_public_ip_address(self, address: str):
		"""Return True when an IP address is safe for outbound page fetching."""
		ip = ipaddress.ip_address(address)
		return ip.is_global and not ip.is_multicast

	def is_supported_url_content_type(self, content_type: str):
		"""Return True when a response content type can be summarized as text."""
		media_type = (content_type or "").split(";", 1)[0].strip().lower()
		return media_type in {"text/html", "text/plain", "application/xhtml+xml", ""}

	def response_charset(self, content_type: str):
		"""Extract response charset from a Content-Type header."""
		for part in (content_type or "").split(";"):
			name, _, value = part.strip().partition("=")
			if name.lower() == "charset" and value:
				return value.strip("\"'")
		return "utf-8"

	def extract_page_text(self, content: str, content_type: str):
		"""Extract readable text from HTML or plain text."""
		media_type = (content_type or "").split(";", 1)[0].strip().lower()
		if media_type == "text/plain":
			return self.compact_text(content)

		soup = BeautifulSoup(content, "html.parser")
		for element in soup(["script", "style", "noscript", "template", "svg"]):
			element.decompose()

		parts = []
		if soup.title and soup.title.string:
			parts.append(f"Title: {soup.title.string}")

		description = soup.find("meta", attrs={"name": "description"})
		if description and description.get("content"):
			parts.append(f"Description: {description.get('content')}")

		body_source = soup.body or soup
		body_text = body_source.get_text(" ", strip=True)
		if body_text:
			parts.append(body_text)
		return self.compact_text("\n".join(parts))

	def compact_text(self, text: str):
		"""Normalize whitespace for prompt-friendly linked page context."""
		return re.sub(r"\s+", " ", text or "").strip()

	def format_url_summary(self, url: str, content_type: str, page_text: str):
		"""Format one linked page summary for the analysis prompt."""
		return (
			"Linked page:\n"
			f"URL: {url}\n"
			f"Content-Type: {content_type or 'unknown'}\n"
			"Safely fetched text excerpt:\n"
			f"{self.truncate_text(page_text, self.url_context_max_chars)}"
		)

	def format_url_skip(self, url: str, reason: str):
		"""Format a skipped URL notice for the analysis prompt."""
		return (
			"Linked page:\n"
			f"URL: {url}\n"
			f"Fetch skipped: {self.truncate_text(reason, 120)}"
		)

	def build_analysis_user_prompt(self, context_text: str, target_content: str, url_context_text: str = ""):
		"""Build the user prompt from the configured template."""
		template = self.analysis_user_prompt_template
		url_context = url_context_text or "(no safely fetched linked pages)"
		if "{url_context_text}" not in template:
			template = (
				template
				+ "\n\nLinked page context, if safely fetched:\n{url_context_text}"
			)
		try:
			return template.format(
				context_text=context_text,
				target_content=target_content,
				url_context_text=url_context,
			)
		except (KeyError, ValueError) as e:
			print(f"[ERROR] invalid OLLAMA_ANALYSIS_USER_PROMPT_TEMPLATE: {e}")
			return config.DEFAULT_OLLAMA_ANALYSIS_USER_PROMPT_TEMPLATE.format(
				context_text=context_text,
				target_content=target_content,
				url_context_text=url_context,
			)

	def extract_ollama_message_content(self, body: dict):
		"""Extract the assistant content from an Ollama chat response."""
		content = ((body.get("message") or {}).get("content") or "").strip()
		if not content:
			done_reason = body.get("done_reason") or body.get("error") or "unknown"
			raise ValueError(f"Ollama returned empty message content: {done_reason}")
		return content

	def parse_analysis_json(self, content: str):
		"""Parse Ollama JSON output while tolerating extra surrounding text."""
		cleaned = self.strip_code_fence(content.strip())
		try:
			return json.loads(cleaned)
		except json.JSONDecodeError:
			json_text = self.extract_first_json_object(cleaned)
			if json_text:
				return json.loads(json_text)
			preview = cleaned[:200].replace("\n", "\\n")
			raise ValueError(f"Ollama returned non-JSON content: {preview}")

	def strip_code_fence(self, content: str):
		"""Remove a Markdown code fence if the model returned one."""
		if not content.startswith("```"):
			return content
		lines = content.splitlines()
		if len(lines) >= 2 and lines[-1].strip() == "```":
			return "\n".join(lines[1:-1]).strip()
		return content

	def extract_first_json_object(self, content: str):
		"""Return the first balanced JSON object embedded in a text response."""
		start = content.find("{")
		if start < 0:
			return ""

		depth = 0
		in_string = False
		escape = False
		for index in range(start, len(content)):
			char = content[index]
			if escape:
				escape = False
				continue
			if char == "\\":
				escape = True
				continue
			if char == '"':
				in_string = not in_string
				continue
			if in_string:
				continue
			if char == "{":
				depth += 1
			elif char == "}":
				depth -= 1
				if depth == 0:
					return content[start:index + 1]
		return ""

	def build_context_text(self, context_messages, max_chars=None):
		"""Format previous messages for Ollama while keeping the target separate."""
		if not context_messages:
			return "(no previous messages)"

		lines = []
		for message in context_messages:
			content = (message.content or "").replace("\n", " ")
			lines.append(f"user:{message.user_id}: {content}")
		return self.truncate_text("\n".join(lines), max_chars or self.context_max_chars)

	def truncate_text(self, text: str, max_chars: int):
		"""Limit prompt text so slow models are less likely to time out."""
		if len(text) <= max_chars:
			return text
		return text[-max_chars:]

	def normalize_result(self, analysis: dict):
		"""Convert model output into bounded integer moderation scores."""
		# Clamp each score defensively because model output is not fully trusted.
		result = {}
		for key in ("aggression", "intimidation", "insult", "sarcasm", "snide", "discomfort"):
			score = int(analysis.get(key, 0))
			result[key] = max(0, min(100, score))

		result["targeted"] = self.normalize_bool(analysis.get("targeted"), True)
		result["confidence"] = max(0, min(100, int(analysis.get("confidence", 100))))
		result["context_dependency"] = self.normalize_bool(analysis.get("context_dependency"), False)
		result["reason"] = str(analysis.get("reason", "")).strip()
		return result

	def normalize_bool(self, value, default: bool):
		"""Convert common model boolean outputs into a bool."""
		if isinstance(value, bool):
			return value
		if value is None:
			return default
		if isinstance(value, (int, float)):
			return bool(value)
		if isinstance(value, str):
			normalized = value.strip().lower()
			if normalized in {"true", "1", "yes", "y", "on"}:
				return True
			if normalized in {"false", "0", "no", "n", "off"}:
				return False
		return default

	def max_score(self, result: dict):
		"""Return the highest moderation score in an analysis result."""
		return max(
			result["aggression"],
			result["intimidation"],
			result["insult"],
			result["sarcasm"],
			result["snide"],
			result["discomfort"],
		)

	def notification_score(self, result: dict):
		"""Return the highest score used for reaction and DM decisions."""
		return max(
			result["aggression"],
			result["intimidation"],
			result["insult"],
			result["discomfort"],
		)

	def should_react(self, result: dict):
		"""Return True when a notification-relevant score reaches the reaction threshold."""
		return self.should_alert(result, self.reaction_threshold)

	def should_notify(self, result: dict):
		"""Return True when a notification-relevant score reaches the DM threshold."""
		return self.should_alert(result, self.dm_threshold)

	def should_alert(self, result: dict, threshold: int):
		"""Return True when a score should create a visible moderation alert."""
		if self.notification_score(result) < threshold:
			return False
		if result["confidence"] < self.confidence_threshold:
			return False
		if result["targeted"]:
			return True
		return result["intimidation"] >= 80

	async def add_detection_reaction(self, message):
		"""Add a marker reaction to a message detected by Ollama analysis."""
		try:
			await message.add_reaction("\u2716")
		except Exception as e:
			print(f"[ERROR] discomfort reaction failed message_id={message.id}: {e}")

	async def notify_reaction_channel(self, message, result: dict):
		"""Notify the configured channel when a message reaches the reaction threshold."""
		if self.bot is None or not self.reaction_notify_channel_id:
			return

		channel = self.bot.get_channel(self.reaction_notify_channel_id)
		if channel is None:
			try:
				channel = await self.bot.fetch_channel(self.reaction_notify_channel_id)
			except Exception as e:
				print(f"[ERROR] analysis reaction notify channel fetch failed: {e}")
				return

		target_guild = getattr(channel, "guild", None)
		if self.reaction_notify_guild_id and getattr(target_guild, "id", None) != self.reaction_notify_guild_id:
			print(
				"[ERROR] analysis reaction notify channel guild mismatch: "
				f"configured_guild={self.reaction_notify_guild_id} "
				f"channel_guild={getattr(target_guild, 'id', None)}"
			)
			return

		body = self.build_reaction_notify_message(message, result)
		try:
			await channel.send(body)
		except Exception as e:
			print(f"[ERROR] analysis reaction notify failed message_id={message.id}: {e}")

	def build_reaction_notify_message(self, message, result: dict):
		"""Build the notification body sent to the configured moderation channel."""
		mention = self.reaction_notify_mention.strip()
		prefix = f"{mention}\n" if mention else ""
		content = (message.content or "").replace("\n", " ")
		content = self.truncate_text(content, 500)
		return (
			f"{prefix}"
			"analysis reaction threshold reached.\n"
			f"server: {message.guild.name} ({message.guild.id})\n"
			f"channel: #{message.channel.name} ({message.channel.id})\n"
			f"user: {message.author} ({message.author.id})\n"
			f"message: {message.jump_url}\n"
			f"score: notification={self.notification_score(result)}, max={self.max_score(result)}\n"
			f"targeted={result['targeted']}, confidence={result['confidence']}, "
			f"context_dependency={result['context_dependency']}\n"
			"scores: "
			f"aggression={result['aggression']}, "
			f"intimidation={result['intimidation']}, "
			f"insult={result['insult']}, "
			f"sarcasm={result['sarcasm']}, "
			f"snide={result['snide']}, "
			f"discomfort={result['discomfort']}\n"
			f"reason: {result.get('reason') or '-'}\n"
			f"content: {content}"
		)

	async def notify_author(self, message, result: dict):
		"""Send the moderation notice to the message author by DM."""
		# DM failures are expected when users block DMs, so log and keep the bot alive.
		try:
			await message.author.send(self.build_dm_message(message, result))
		except Exception as e:
			print(f"[ERROR] discomfort dm failed message_id={message.id}: {e}")

	def build_dm_message(self, message, result: dict):
		"""Build the Japanese DM body shown when a message is detected."""
		return (
			"投稿内容が他のユーザーに不快感を与える可能性があるため検出されました。\n"
			f"サーバー: {message.guild.name}\n"
			f"チャンネル: #{message.channel.name}\n"
			f"メッセージ: {message.jump_url}\n\n"
			"スコア(0-100):\n"
			f"- 攻撃性: {result['aggression']}\n"
			f"- 威圧感: {result['intimidation']}\n"
			f"- 侮辱: {result['insult']}\n"
			f"- 皮肉: {result['sarcasm']}\n"
			f"- 嫌味: {result['snide']}\n"
			f"- 相手が不快になる可能性: {result['discomfort']}\n\n"
			f"理由: {result['reason'] or '理由は取得できませんでした。'}"
		)
