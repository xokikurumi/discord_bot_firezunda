import re

import d20


class DiceRollService:
	"""Detect and roll dice expressions with the d20 parser."""

	def __init__(self, enabled=True):
		"""Store whether automatic dice rolling is enabled."""
		self.enabled = enabled
		self.auto_roll_pattern = re.compile(
			r"""
			^
			(?=.{1,120}$)
			(?=.*\d\s*d\s*\d)
			[0-9dDkKhHlL+\-*/%().,\s]+
			$
			""",
			re.VERBOSE,
		)

	def is_auto_roll(self, content: str):
		"""Return True when a whole message looks like a dice expression."""
		if not self.enabled:
			return False
		if not content:
			return False

		content = content.strip()
		if content.startswith(("!", "/", "\\")):
			return False

		return self.auto_roll_pattern.fullmatch(content) is not None

	def roll(self, expression: str):
		"""Roll one dice expression and return the printable d20 result."""
		expression = (expression or "").strip()
		if not expression:
			raise ValueError("dice expression is empty.")

		return str(d20.roll(expression))
