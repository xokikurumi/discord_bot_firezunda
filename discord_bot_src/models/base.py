from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import Column, DateTime, func


# =========================
# Baseクラス
# =========================
class Base(DeclarativeBase):
	"""Declarative base class for all SQLAlchemy ORM models."""

	pass


# =========================
# 共通Mixin（全テーブル共通）
# =========================
class TimestampMixin:
	"""Mixin that adds a database-created timestamp to a model."""

	created_at = Column(
		DateTime(timezone=True),
		server_default=func.now(),
		nullable=False
	)

	# updated_at = Column(
	# 	DateTime(timezone=True),
	# 	server_default=func.now(),
	# 	onupdate=func.now(),
	# 	nullable=False
	# )


# =========================
# テーブル名自動生成Mixin
# =========================
class TablenameMixin:
	"""Mixin that derives a default table name from the class name."""

	@declared_attr.directive
	def __tablename__(cls):
		"""Return the lowercase class name as the table name."""
		return cls.__name__.lower()
