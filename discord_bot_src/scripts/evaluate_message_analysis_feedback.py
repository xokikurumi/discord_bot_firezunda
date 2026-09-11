import argparse
import asyncio
import json
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))


SCORE_KEYS = ("aggression", "intimidation", "insult", "sarcasm", "snide", "discomfort")


def parse_args():
	"""Parse command line options for administrator feedback evaluation."""
	parser = argparse.ArgumentParser(
		description="Evaluate current message analysis against confirmed administrator feedback.",
	)
	parser.add_argument(
		"--env-file",
		default=os.getenv("DISCORD_BOT_ENV_FILE", "/opt/discord/env/discord-bot.env"),
		help="Environment file to load before DB/Ollama settings are imported.",
	)
	parser.add_argument("--guild-id", type=int, default=0, help="Limit evaluation cases to one guild.")
	parser.add_argument("--limit", type=int, default=50, help="Maximum confirmed feedback cases to evaluate.")
	parser.add_argument("--no-rag", action="store_true", help="Disable feedback RAG during evaluation.")
	parser.add_argument("--url-context", action="store_true", help="Enable linked page fetching during evaluation.")
	parser.add_argument("--dry-run", action="store_true", help="List evaluation cases without calling Ollama.")
	parser.add_argument("--json", action="store_true", help="Print the final summary as JSON.")
	return parser.parse_args()


def load_env_file(env_file: str):
	"""Load KEY=VALUE lines before importing application config."""
	if not env_file:
		return

	path = Path(env_file)
	if not path.exists():
		return

	for raw_line in path.read_text(encoding="utf-8").splitlines():
		line = raw_line.strip()
		if not line or line.startswith("#"):
			continue
		if line.startswith("export "):
			line = line[len("export "):].strip()
		if "=" not in line:
			continue

		key, value = line.split("=", 1)
		key = key.strip()
		value = value.strip().strip("'\"").replace('\\"', '"')
		if key:
			os.environ.setdefault(key, value)


def alert_value(service, result: dict):
	"""Return whether a result would trigger a visible analysis reaction."""
	return service.should_react(result)


def score_mae(actual: dict, expected: dict):
	"""Return mean absolute score error for one evaluated case."""
	return sum(abs(actual[key] - expected[key]) for key in SCORE_KEYS) / len(SCORE_KEYS)


def max_score(result: dict):
	"""Return the highest moderation score in a normalized result."""
	return max(result[key] for key in SCORE_KEYS)


def empty_summary():
	"""Build the aggregate summary container."""
	return {
		"cases": 0,
		"analyzed": 0,
		"failed": 0,
		"alert_matches": 0,
		"targeted_matches": 0,
		"score_mae_total": 0.0,
		"max_score_error_total": 0.0,
		"labels": {},
	}


def add_label_count(summary: dict, label: str, key: str):
	"""Increment a nested label counter."""
	label_stats = summary["labels"].setdefault(label, {"cases": 0, "analyzed": 0, "failed": 0})
	label_stats[key] += 1


def finalize_summary(summary: dict):
	"""Add derived metrics to the aggregate summary."""
	analyzed = summary["analyzed"]
	if analyzed:
		summary["alert_accuracy"] = round(summary["alert_matches"] / analyzed, 4)
		summary["targeted_accuracy"] = round(summary["targeted_matches"] / analyzed, 4)
		summary["score_mae"] = round(summary["score_mae_total"] / analyzed, 2)
		summary["max_score_error"] = round(summary["max_score_error_total"] / analyzed, 2)
	else:
		summary["alert_accuracy"] = 0
		summary["targeted_accuracy"] = 0
		summary["score_mae"] = 0
		summary["max_score_error"] = 0
	return summary


async def fetch_cases(session_factory, repository_class, guild_id: int, limit: int):
	"""Load confirmed feedback rows for evaluation."""
	async with session_factory() as session:
		repo = repository_class(session)
		return await repo.list_confirmed_evaluation_cases(guild_id or None, limit)


async def run_evaluation(args):
	"""Run evaluation against administrator-confirmed feedback cases."""
	load_env_file(args.env_file)

	from db.session import AsyncSessionLocal, engine
	from repositories.log.message_analysis_feedback_repo import MessageAnalysisFeedbackRepository
	from services.base.messageWatcherService import MessageWatcherService

	service = MessageWatcherService(AsyncSessionLocal)
	service.url_context_enabled = bool(args.url_context)

	rows = await fetch_cases(
		AsyncSessionLocal,
		MessageAnalysisFeedbackRepository,
		args.guild_id,
		args.limit,
	)
	summary = empty_summary()

	try:
		for feedback, message_log, _analysis_log in rows:
			label = feedback.label or "unknown"
			summary["cases"] += 1
			add_label_count(summary, label, "cases")

			expected = service.parse_corrected_result_json(feedback.corrected_result_json)
			if not expected:
				summary["failed"] += 1
				add_label_count(summary, label, "failed")
				print(f"failed case_id={feedback.id} message_id={feedback.message_id} reason=invalid_expected")
				continue

			content = message_log.content or ""
			if args.dry_run:
				print(f"case case_id={feedback.id} message_id={feedback.message_id} label={label}")
				continue

			actual = await service.analyze_message(
				content,
				[],
				message_log.guild_id,
				use_exact_feedback=False,
				use_feedback_rag=not args.no_rag,
				excluded_feedback_message_id=feedback.message_id,
			)
			if actual is None:
				summary["failed"] += 1
				add_label_count(summary, label, "failed")
				print(f"failed case_id={feedback.id} message_id={feedback.message_id} reason=analysis_failed")
				continue

			summary["analyzed"] += 1
			add_label_count(summary, label, "analyzed")
			if alert_value(service, actual) == alert_value(service, expected):
				summary["alert_matches"] += 1
			if actual["targeted"] == expected["targeted"]:
				summary["targeted_matches"] += 1
			summary["score_mae_total"] += score_mae(actual, expected)
			summary["max_score_error_total"] += abs(max_score(actual) - max_score(expected))

			print(
				"evaluated "
				f"case_id={feedback.id} message_id={feedback.message_id} label={label} "
				f"mae={score_mae(actual, expected):.2f} "
				f"expected_alert={alert_value(service, expected)} actual_alert={alert_value(service, actual)} "
				f"expected_max={max_score(expected)} actual_max={max_score(actual)}"
			)
	finally:
		await engine.dispose()

	summary = finalize_summary(summary)
	if args.json:
		print(json.dumps(summary, ensure_ascii=False, indent=2))
	else:
		print(
			"summary "
			f"cases={summary['cases']} analyzed={summary['analyzed']} failed={summary['failed']} "
			f"alert_accuracy={summary['alert_accuracy']} targeted_accuracy={summary['targeted_accuracy']} "
			f"score_mae={summary['score_mae']} max_score_error={summary['max_score_error']}"
		)


if __name__ == "__main__":
	asyncio.run(run_evaluation(parse_args()))
