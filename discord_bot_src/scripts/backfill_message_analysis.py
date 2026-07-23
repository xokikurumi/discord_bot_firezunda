import argparse
import asyncio
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))


def parse_args():
	"""Parse command line options for message analysis backfill."""
	parser = argparse.ArgumentParser(
		description="Analyze stored message logs without Discord reactions or notifications.",
	)
	parser.add_argument(
		"--env-file",
		default=os.getenv("DISCORD_BOT_ENV_FILE", "/opt/discord/env/discord-bot.env"),
		help="Environment file to load before DB/Ollama settings are imported.",
	)
	parser.add_argument("--limit", type=int, default=100, help="Maximum messages to analyze. Use 0 for all.")
	parser.add_argument("--batch-size", type=int, default=20, help="Messages to fetch per batch.")
	parser.add_argument("--start-id", type=int, default=0, help="Start after message_log.id.")
	parser.add_argument("--sleep", type=float, default=0.0, help="Seconds to sleep between messages.")
	parser.add_argument("--dry-run", action="store_true", help="List candidates without analyzing.")
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


async def fetch_candidates(session_factory, message_log_repository, limit: int, after_id: int):
	"""Fetch stored messages that do not have analysis rows yet."""
	async with session_factory() as session:
		repo = message_log_repository(session)
		return await repo.list_unanalyzed_analysis_candidates(limit, after_id)


async def run_backfill(args):
	"""Run analysis backfill for stored Discord message logs."""
	load_env_file(args.env_file)

	from db.session import AsyncSessionLocal, engine
	from repositories.log.message_log_repo import MessageLogRepository
	from services.base.messageWatcherService import MessageWatcherService

	service = MessageWatcherService(AsyncSessionLocal)
	after_id = args.start_id
	processed = 0
	analyzed = 0
	skipped = 0

	try:
		while args.limit <= 0 or processed < args.limit:
			batch_limit = args.batch_size
			if args.limit > 0:
				batch_limit = min(args.batch_size, args.limit - processed)
			candidates = await fetch_candidates(
				AsyncSessionLocal,
				MessageLogRepository,
				batch_limit,
				after_id,
			)
			if not candidates:
				break

			for message_log in candidates:
				after_id = max(after_id, message_log.id)
				processed += 1

				if args.dry_run:
					print(
						"candidate "
						f"id={message_log.id} message_id={message_log.message_id} "
						f"guild_id={message_log.guild_id} channel_id={message_log.channel_id}"
					)
					continue

				try:
					if await service.analyze_logged_message(message_log):
						analyzed += 1
						print(f"analyzed id={message_log.id} message_id={message_log.message_id}")
					else:
						skipped += 1
						print(f"skipped id={message_log.id} message_id={message_log.message_id}")
				except Exception as e:
					skipped += 1
					print(
						"skipped "
						f"id={message_log.id} message_id={message_log.message_id} "
						f"error={e}"
					)

				if args.sleep > 0:
					await asyncio.sleep(args.sleep)
	finally:
		await engine.dispose()

	print(
		f"complete processed={processed} analyzed={analyzed} "
		f"skipped={skipped} last_id={after_id}"
	)


if __name__ == "__main__":
	asyncio.run(run_backfill(parse_args()))
