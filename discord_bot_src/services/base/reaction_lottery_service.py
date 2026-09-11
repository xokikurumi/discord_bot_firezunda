import random
import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo


class ReactionLotteryService:
	"""Parse lottery settings and select winners from Discord reaction users."""

	DEFAULT_REACTION = "🎉"
	DEFAULT_DURATION = timedelta(hours=1)
	MAX_DURATION = timedelta(days=7)
	JST = ZoneInfo("Asia/Tokyo")

	def parse_end_time(self, end_text: str):
		"""Parse a duration or absolute datetime and return a UTC aware datetime."""
		text = (end_text or "").strip()
		if not text:
			return self.now_utc() + self.DEFAULT_DURATION

		duration = self.parse_duration(text)
		if duration is not None:
			return self.validate_deadline(self.now_utc() + duration)

		deadline = self.parse_absolute_time(text)
		return self.validate_deadline(deadline)

	def parse_duration(self, text: str):
		"""Parse duration strings such as 30m, 2h, or 1d."""
		match = re.fullmatch(r"(\d+)\s*([smhd秒分時間日])", text.lower())
		if not match:
			return None

		amount = int(match.group(1))
		unit = match.group(2)
		if amount <= 0:
			raise ValueError("end must be in the future.")
		if unit in {"s", "秒"}:
			return timedelta(seconds=amount)
		if unit in {"m", "分"}:
			return timedelta(minutes=amount)
		if unit in {"h", "時間"}:
			return timedelta(hours=amount)
		return timedelta(days=amount)

	def parse_absolute_time(self, text: str):
		"""Parse absolute local datetimes."""
		normalized = text.replace("/", "-")
		formats = [
			"%Y-%m-%d %H:%M",
			"%Y-%m-%dT%H:%M",
			"%m-%d %H:%M",
		]
		for date_format in formats:
			try:
				parsed = datetime.strptime(normalized, date_format)
			except ValueError:
				continue
			if date_format == "%m-%d %H:%M":
				parsed = parsed.replace(year=datetime.now(self.JST).year)
			return parsed.replace(tzinfo=self.JST).astimezone(timezone.utc)

		raise ValueError("end must be a duration like 30m/2h/1d or datetime like 2026-08-10 21:00.")

	def validate_deadline(self, deadline):
		"""Validate a lottery deadline."""
		now = self.now_utc()
		if deadline <= now:
			raise ValueError("end must be in the future.")
		if deadline - now > self.MAX_DURATION:
			raise ValueError("end must be within 7 days.")
		return deadline

	def now_utc(self):
		"""Return current UTC time."""
		return datetime.now(timezone.utc)

	def seconds_until(self, deadline):
		"""Return seconds until a deadline."""
		return max(0, (deadline - self.now_utc()).total_seconds())

	def choose_winners(self, users, winner_count: int):
		"""Choose lottery winners from unique non-bot users."""
		candidates = []
		seen = set()
		for user in users:
			if getattr(user, "bot", False):
				continue
			if user.id in seen:
				continue
			seen.add(user.id)
			candidates.append(user)

		if winner_count <= 0:
			raise ValueError("winners must be 1 or more.")
		if not candidates:
			return []
		return random.sample(candidates, min(winner_count, len(candidates)))

	def format_deadline_timestamp(self, deadline):
		"""Return Discord timestamp markup for a deadline."""
		return f"<t:{int(deadline.timestamp())}:F>"
