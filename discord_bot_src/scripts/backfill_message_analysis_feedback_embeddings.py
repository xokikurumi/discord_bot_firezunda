import argparse
import asyncio
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))


def parse_args():
	"""Parse command line options for feedback embedding backfill."""
	parser = argparse.ArgumentParser(
		description="Create embeddings for confirmed message analysis feedback rows.",
	)
	parser.add_argument(
		"--env-file",
		default=os.getenv("DISCORD_BOT_ENV_FILE", "/opt/discord/env/discord-bot.env"),
		help="Environment file to load before DB/Ollama settings are imported.",
	)
	parser.add_argument("--guild-id", type=int, default=0, help="Limit backfill to one guild.")
	parser.add_argument("--limit", type=int, default=100, help="Maximum rows to process. Use 0 for all.")
	parser.add_argument("--batch-size", type=int, default=50, help="Rows to fetch per batch.")
	parser.add_argument("--sleep", type=float, default=0.0, help="Seconds to sleep between rows.")
	parser.add_argument("--force", action="store_true", help="Rebuild existing embeddings.")
	parser.add_argument("--dry-run", action="store_true", help="List target rows without calling Ollama.")
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


async def fetch_candidates(session_factory, repository_class, guild_id: int, limit: int, force: bool, before_id: int):
	"""Fetch feedback rows that should receive embeddings."""
	async with session_factory() as session:
		repo = repository_class(session)
		return await repo.list_embedding_backfill_candidates(guild_id or None, limit, force, before_id)


async def update_embedding(session_factory, repository_class, feedback_id: int, embedding_data: dict):
	"""Persist embedding columns for one feedback row."""
	async with session_factory() as session:
		repo = repository_class(session)
		await repo.update_embedding(
			feedback_id,
			embedding_data["embedding_model"],
			embedding_data["embedding_text_hash"],
			embedding_data["embedding_dim"],
			embedding_data["embedding_json"],
		)


async def run_backfill(args):
	"""Create embeddings for confirmed administrator feedback rows."""
	load_env_file(args.env_file)

	from db.session import AsyncSessionLocal, engine
	from repositories.log.message_analysis_feedback_repo import MessageAnalysisFeedbackRepository
	from services.base.messageWatcherService import MessageWatcherService

	service = MessageWatcherService(AsyncSessionLocal)
	processed = 0
	updated = 0
	skipped = 0
	failed = 0
	before_id = 0

	try:
		while args.limit <= 0 or processed < args.limit:
			batch_limit = args.batch_size
			if args.limit > 0:
				batch_limit = min(args.batch_size, args.limit - processed)
			rows = await fetch_candidates(
				AsyncSessionLocal,
				MessageAnalysisFeedbackRepository,
				args.guild_id,
				batch_limit,
				args.force,
				before_id,
			)
			if not rows:
				break

			for feedback, message_log, _analysis_log in rows:
				before_id = feedback.id
				processed += 1
				content = message_log.content or ""
				embedding_text = service.build_feedback_embedding_text(content, feedback.label, feedback.note or "")
				embedding_hash = service.embedding_text_hash(embedding_text)

				if not args.force and feedback.embedding_json and feedback.embedding_text_hash == embedding_hash:
					skipped += 1
					print(f"skipped id={feedback.id} message_id={feedback.message_id} reason=already_current")
					continue

				if args.dry_run:
					print(
						"candidate "
						f"id={feedback.id} message_id={feedback.message_id} "
						f"guild_id={feedback.guild_id} label={feedback.label}"
					)
					continue

				embedding_data = await service.build_feedback_embedding_data_limited(
					content,
					feedback.label,
					feedback.note or "",
					force=True,
				)
				if not embedding_data:
					failed += 1
					print(f"failed id={feedback.id} message_id={feedback.message_id}")
					continue

				await update_embedding(
					AsyncSessionLocal,
					MessageAnalysisFeedbackRepository,
					feedback.id,
					embedding_data,
				)
				updated += 1
				print(
					"updated "
					f"id={feedback.id} message_id={feedback.message_id} "
					f"model={embedding_data['embedding_model']} dim={embedding_data['embedding_dim']}"
				)

				if args.sleep > 0:
					await asyncio.sleep(args.sleep)
	finally:
		await engine.dispose()

	print(
		f"complete processed={processed} updated={updated} "
		f"skipped={skipped} failed={failed}"
	)


if __name__ == "__main__":
	asyncio.run(run_backfill(parse_args()))
