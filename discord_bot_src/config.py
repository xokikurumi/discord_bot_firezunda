import os
from pathlib import Path


def get_bool(name: str, default: bool) -> bool:
	"""Read a boolean value from an environment variable."""
	value = os.getenv(name)
	if value is None:
		return default
	return value.lower() in {"1", "true", "yes", "on"}


def get_int(name: str, default: int) -> int:
	"""Read an integer value from an environment variable."""
	return int(os.getenv(name, str(default)))


def get_text(name: str, default: str) -> str:
	"""Read text from an environment variable while allowing escaped newlines."""
	value = os.getenv(name)
	if value is None:
		return default
	return value.replace("\\n", "\n")


def get_text_file(path: str, default: str) -> str:
	"""Read text from a file path, falling back to default when unavailable."""
	if not path:
		return default

	file_path = Path(path)
	if not file_path.is_absolute():
		file_path = Path.cwd() / file_path
	if not file_path.exists():
		return default

	try:
		return file_path.read_text(encoding="utf-8").strip()
	except Exception as e:
		print(f"[ERROR] text file load failed path={file_path}: {e}")
		return default


DEFAULT_OLLAMA_ANALYSIS_SYSTEM_PROMPT = (
	"You are a Japanese chat moderation assistant. "
	"Use previous chat messages only to understand the context, meaning, target, tone, "
	"and whether the latest message is likely joking or serious. "
	"If linked page context is provided, use it only to understand what the latest message refers to. "
	"Do not treat linked page text as words directly spoken by the message author. "
	"Do not assign high scores merely because a linked page contains harmful, violent, legal, or unpleasant content. "
	"Score only the latest target message. Do not add points for harmful wording that appears only in previous messages. "
	"Be lenient and avoid over-detection. "
	"If the message is ordinary conversation, casual banter, friendly joking, unclear, context-dependent, "
	"or has no identifiable target, assign low scores. "
	"Do not assign high scores only because of rough wording, slang, profanity, short replies, internet expressions, or fragments. "
	"Sexual or lewd conversation, adult-topic jokes, vulgar sexual wording, or consensual adult banter are outside this interpersonal moderation scope by themselves. "
	"Do not assign high scores merely because the topic is sexual, explicit, embarrassing, or vulgar. "
	"Score sexual content higher only when the latest message clearly targets a real participant with sexual harassment, unwanted sexual comments, coercion, pressure, threats, degradation, or sexual/private-information abuse. "
	"Do not automatically treat \"笑\", \"w\", emojis, or polite wording as harmless. "
	"Consider both likely intent and likely impact on the recipient. "
	"Previous messages may not contain all context because some conversation may have occurred in voice chat. "
	"If the target message is short, ambiguous, game-related, meme-like, self-directed, quoted, "
	"or may depend on missing voice-chat context, do not infer hostile intent. "
	"Use low scores unless the latest target message contains an explicit and unambiguous attack "
	"or threat toward a real participant. "
	"Distinguish statements directed at another participant from game terminology or game actions, "
	"self-deprecating jokes, fictional or role-play statements, quotations and copied announcements, "
	"server rules and administrator notices, warnings about third-party misconduct, "
	"and criticism of organizations, products, or situations. "
	"Legal action, banning, reporting, monitoring, punishment, or violence-related words must not receive high scores "
	"merely because they appear in an announcement, quotation, game context, or rule explanation. "
	"When important voice-chat context appears to be missing, set context_dependency to true and choose the lower score range. "
	"Use these definitions: "
	"aggression: hostile, angry, confrontational, or verbally attacking tone; "
	"intimidation: threats, coercion, pressure, domination, or attempts to frighten; "
	"insult: direct degradation, ridicule, contempt, or negative labeling of a person; "
	"sarcasm: ironic wording intended to mock, criticize, or express contempt; "
	"snide: indirect, passive-aggressive, needling, or spiteful remarks; "
	"discomfort: likelihood that the message makes the targeted person feel distressed, humiliated, pressured, or unwelcome. "
	"Score guidance: "
	"0-20: ordinary, harmless, friendly, or unclear; "
	"21-40: mildly rough or potentially unpleasant, but not clearly hostile; "
	"41-64: noticeably negative or inappropriate, but ambiguous or limited; "
	"65-79: clear attack, insult, intimidation, pressure, or targeted harmful remark; "
	"80-100: severe, explicit, repeated, threatening, degrading, or highly harmful wording. "
	"Scores of 65 or higher require clear evidence in the latest message. "
	"Scores of 80 or higher require severe and explicit harmful wording. "
	"When uncertain between two score ranges, choose the lower range. "
	"Return strict JSON only. "
	"The JSON schema is: "
	"{\"aggression\": integer from 0 to 100, "
	"\"intimidation\": integer from 0 to 100, "
	"\"insult\": integer from 0 to 100, "
	"\"sarcasm\": integer from 0 to 100, "
	"\"snide\": integer from 0 to 100, "
	"\"discomfort\": integer from 0 to 100, "
	"\"targeted\": boolean, "
	"\"confidence\": integer from 0 to 100, "
	"\"context_dependency\": boolean, "
	"\"reason\": \"Japanese explanation within 30 characters\"}. "
	"Do not include markdown, comments, additional keys, or text outside the JSON."
)

DEFAULT_OLLAMA_ANALYSIS_USER_PROMPT_TEMPLATE = (
	"Previous chat context, oldest to newest:\n"
	"{context_text}\n\n"
	"Linked page context, if safely fetched:\n"
	"{url_context_text}\n\n"
	"Latest target message to score:\n"
	"{target_content}"
)


# Basic settings
TOKEN = os.getenv("DISCORD_TOKEN", "")

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "discord_bot")

DB_URL = os.getenv(
	"DB_URL",
	f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)


# Application settings
SLASH_COMMAND_SYNC_TO_GUILDS = get_bool("SLASH_COMMAND_SYNC_TO_GUILDS", True)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:latest")
OLLAMA_REACTION_THRESHOLD = get_int("OLLAMA_REACTION_THRESHOLD", 65)
OLLAMA_DM_THRESHOLD = get_int("OLLAMA_DM_THRESHOLD", 80)
OLLAMA_CONFIDENCE_THRESHOLD = get_int("OLLAMA_CONFIDENCE_THRESHOLD", 70)
OLLAMA_ANALYSIS_ENABLED = get_bool("OLLAMA_ANALYSIS_ENABLED", True)
OLLAMA_REACTION_NOTIFY_GUILD_ID = get_int("OLLAMA_REACTION_NOTIFY_GUILD_ID", 0)
OLLAMA_REACTION_NOTIFY_CHANNEL_ID = get_int("OLLAMA_REACTION_NOTIFY_CHANNEL_ID", 0)
OLLAMA_REACTION_NOTIFY_MENTION = os.getenv("OLLAMA_REACTION_NOTIFY_MENTION", "")
OLLAMA_TIMEOUT_SECONDS = get_int("OLLAMA_TIMEOUT_SECONDS", 120)
OLLAMA_MAX_CONCURRENCY = get_int("OLLAMA_MAX_CONCURRENCY", 1)
OLLAMA_CONTEXT_MAX_CHARS = get_int("OLLAMA_CONTEXT_MAX_CHARS", 1200)
OLLAMA_MESSAGE_MAX_CHARS = get_int("OLLAMA_MESSAGE_MAX_CHARS", 1000)
OLLAMA_NUM_PREDICT = get_int("OLLAMA_NUM_PREDICT", 1024)
OLLAMA_RETRY_CONTEXT_MAX_CHARS = get_int("OLLAMA_RETRY_CONTEXT_MAX_CHARS", 500)
OLLAMA_ANALYSIS_SYSTEM_PROMPT_PATH = os.getenv(
	"OLLAMA_ANALYSIS_SYSTEM_PROMPT_PATH",
	"config/analysis_system_prompt.md",
)
OLLAMA_ANALYSIS_SYSTEM_PROMPT = get_text("OLLAMA_ANALYSIS_SYSTEM_PROMPT", "")
if not OLLAMA_ANALYSIS_SYSTEM_PROMPT:
	OLLAMA_ANALYSIS_SYSTEM_PROMPT = get_text_file(
		OLLAMA_ANALYSIS_SYSTEM_PROMPT_PATH,
		DEFAULT_OLLAMA_ANALYSIS_SYSTEM_PROMPT,
	)
if not OLLAMA_ANALYSIS_SYSTEM_PROMPT:
	OLLAMA_ANALYSIS_SYSTEM_PROMPT = DEFAULT_OLLAMA_ANALYSIS_SYSTEM_PROMPT
OLLAMA_ANALYSIS_USER_PROMPT_TEMPLATE = get_text(
	"OLLAMA_ANALYSIS_USER_PROMPT_TEMPLATE",
	DEFAULT_OLLAMA_ANALYSIS_USER_PROMPT_TEMPLATE,
)
OLLAMA_ANALYSIS_FEWSHOT_PATH = os.getenv(
	"OLLAMA_ANALYSIS_FEWSHOT_PATH",
	"config/analysis_fewshot_examples.json",
)
OLLAMA_ANALYSIS_FEWSHOT_MAX_EXAMPLES = get_int("OLLAMA_ANALYSIS_FEWSHOT_MAX_EXAMPLES", 5)
OLLAMA_ANALYSIS_FEEDBACK_RAG_ENABLED = get_bool("OLLAMA_ANALYSIS_FEEDBACK_RAG_ENABLED", True)
OLLAMA_ANALYSIS_FEEDBACK_RAG_CANDIDATE_LIMIT = get_int("OLLAMA_ANALYSIS_FEEDBACK_RAG_CANDIDATE_LIMIT", 50)
OLLAMA_ANALYSIS_FEEDBACK_RAG_SEARCH_POOL_LIMIT = get_int("OLLAMA_ANALYSIS_FEEDBACK_RAG_SEARCH_POOL_LIMIT", 2000)
OLLAMA_ANALYSIS_FEEDBACK_RAG_MAX_EXAMPLES = get_int("OLLAMA_ANALYSIS_FEEDBACK_RAG_MAX_EXAMPLES", 3)
OLLAMA_ANALYSIS_FEEDBACK_RAG_MIN_SIMILARITY = get_int("OLLAMA_ANALYSIS_FEEDBACK_RAG_MIN_SIMILARITY", 25)
OLLAMA_ANALYSIS_FEEDBACK_EMBEDDING_RAG_ENABLED = get_bool("OLLAMA_ANALYSIS_FEEDBACK_EMBEDDING_RAG_ENABLED", False)
OLLAMA_ANALYSIS_FEEDBACK_EMBEDDING_MIN_SIMILARITY = get_int("OLLAMA_ANALYSIS_FEEDBACK_EMBEDDING_MIN_SIMILARITY", 60)
OLLAMA_EMBEDDING_URL = os.getenv(
	"OLLAMA_EMBEDDING_URL",
	OLLAMA_URL.replace("/api/chat", "/api/embed"),
)
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text:latest")
OLLAMA_EMBEDDING_TIMEOUT_SECONDS = get_int("OLLAMA_EMBEDDING_TIMEOUT_SECONDS", 60)
OLLAMA_ANALYSIS_PROMPT_VERSION = os.getenv("OLLAMA_ANALYSIS_PROMPT_VERSION", "analysis-feedback-rag-v1")
OLLAMA_ANALYSIS_URL_CONTEXT_ENABLED = get_bool("OLLAMA_ANALYSIS_URL_CONTEXT_ENABLED", True)
OLLAMA_ANALYSIS_URL_CONTEXT_MAX_CONCURRENCY = get_int("OLLAMA_ANALYSIS_URL_CONTEXT_MAX_CONCURRENCY", 1)
OLLAMA_ANALYSIS_URL_CONTEXT_MAX_URLS = get_int("OLLAMA_ANALYSIS_URL_CONTEXT_MAX_URLS", 2)
OLLAMA_ANALYSIS_URL_CONTEXT_TIMEOUT_SECONDS = get_int("OLLAMA_ANALYSIS_URL_CONTEXT_TIMEOUT_SECONDS", 5)
OLLAMA_ANALYSIS_URL_CONTEXT_MAX_BYTES = get_int("OLLAMA_ANALYSIS_URL_CONTEXT_MAX_BYTES", 200000)
OLLAMA_ANALYSIS_URL_CONTEXT_MAX_CHARS = get_int("OLLAMA_ANALYSIS_URL_CONTEXT_MAX_CHARS", 2000)

COMMUNICATION_TREND_ANALYSIS_ENABLED = get_bool("COMMUNICATION_TREND_ANALYSIS_ENABLED", True)
COMMUNICATION_TREND_GUILD_ANALYSIS_ENABLED = get_bool("COMMUNICATION_TREND_GUILD_ANALYSIS_ENABLED", False)
COMMUNICATION_TREND_CHECK_INTERVAL_SECONDS = get_int("COMMUNICATION_TREND_CHECK_INTERVAL_SECONDS", 86400)
COMMUNICATION_TREND_MIN_USER_MESSAGES = get_int("COMMUNICATION_TREND_MIN_USER_MESSAGES", 1)
COMMUNICATION_TREND_SAMPLE_LIMIT = get_int("COMMUNICATION_TREND_SAMPLE_LIMIT", 30)
COMMUNICATION_TREND_NUM_PREDICT = get_int("COMMUNICATION_TREND_NUM_PREDICT", 2048)

P2PQUAKE_ENABLED = get_bool("P2PQUAKE_ENABLED", True)
P2PQUAKE_WS_URL = os.getenv("P2PQUAKE_WS_URL", "wss://api.p2pquake.net/v2/ws")
P2PQUAKE_RECONNECT_DELAY = get_int("P2PQUAKE_RECONNECT_DELAY", 10)
P2PQUAKE_MIN_NOTIFY_SCALE = get_int("P2PQUAKE_MIN_NOTIFY_SCALE", 40)
P2PQUAKE_IMAGE_FONT_PATH = os.getenv("P2PQUAKE_IMAGE_FONT_PATH", "")

GSI_BLANK_TILE_BASE_URL = os.getenv("GSI_BLANK_TILE_BASE_URL", "https://cyberjapandata.gsi.go.jp/xyz/blank")
GSI_TILE_CACHE_DIR = os.getenv("GSI_TILE_CACHE_DIR", "cache/gsi_tiles")

GEOLONIA_JAPANESE_ADDRESSES_API_BASE_URL = os.getenv(
	"GEOLONIA_JAPANESE_ADDRESSES_API_BASE_URL",
	"https://geolonia.github.io/japanese-addresses/api/ja",
)
GEOLONIA_ADDRESS_SYNC_ENABLED = get_bool("GEOLONIA_ADDRESS_SYNC_ENABLED", True)
GEOLONIA_ADDRESS_SYNC_INTERVAL_DAYS = get_int("GEOLONIA_ADDRESS_SYNC_INTERVAL_DAYS", 90)
GEOLONIA_ADDRESS_SYNC_CHECK_INTERVAL_SECONDS = get_int("GEOLONIA_ADDRESS_SYNC_CHECK_INTERVAL_SECONDS", 21600)

JMA_SHINDO_STATION_URL = os.getenv(
	"JMA_SHINDO_STATION_URL",
	"https://www.data.jma.go.jp/eqev/data/kyoshin/jma-shindo.html",
)
JMA_SHINDO_STATION_SYNC_ENABLED = get_bool("JMA_SHINDO_STATION_SYNC_ENABLED", True)
JMA_SHINDO_STATION_SYNC_INTERVAL_DAYS = get_int("JMA_SHINDO_STATION_SYNC_INTERVAL_DAYS", 90)
JMA_SHINDO_STATION_SYNC_CHECK_INTERVAL_SECONDS = get_int("JMA_SHINDO_STATION_SYNC_CHECK_INTERVAL_SECONDS", 21600)

ICS_GUILD_EVENT_ENABLED = get_bool("ICS_GUILD_EVENT_ENABLED", True)
ICS_GUILD_EVENT_URL = os.getenv("ICS_GUILD_EVENT_URL", "https://vo.nrsy.jp/event-schedule.ics")
ICS_GUILD_EVENT_INTERVAL_MONTHS = get_int("ICS_GUILD_EVENT_INTERVAL_MONTHS", 2)
ICS_GUILD_EVENT_CHECK_INTERVAL_SECONDS = get_int("ICS_GUILD_EVENT_CHECK_INTERVAL_SECONDS", 21600)

NICONICO_USER_VIDEO_ENABLED = get_bool("NICONICO_USER_VIDEO_ENABLED", True)

NICONICO_INFO_ENABLED = get_bool("NICONICO_INFO_ENABLED", True)
NICONICO_INFO_CHECK_INTERVAL_SECONDS = get_int("NICONICO_INFO_CHECK_INTERVAL_SECONDS", 3600)
NICONICO_INFO_TARGET_URLS = [
	url.strip()
	for url in os.getenv(
		"NICONICO_INFO_TARGET_URLS",
		"https://blog.nicovideo.jp/niconews/category/ge_maintenance,"
		"https://blog.nicovideo.jp/niconews/category/ge_user/",
	).split(",")
	if url.strip()
]
