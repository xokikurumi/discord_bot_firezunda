import asyncio

from sqlalchemy import text

from db.session import engine
from models.base import Base


# =========================
# テーブル作成
# =========================
async def init_db():
    """Create all ORM tables that do not already exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# =========================
# テーブル削除（開発用）
# =========================
async def drop_db():
    """Drop all ORM tables; intended for development use only."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# =========================
# 再作成（開発用）
# =========================
async def reset_db():
    """Drop and recreate all ORM tables for a clean development database."""
    await drop_db()
    await init_db()


# =========================
# 接続確認
# =========================
async def check_connection():
    """Run a minimal SELECT to confirm database connectivity."""
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print("DB Connection OK:", result.scalar())


# =========================
# 単体実行用
# =========================
if __name__ == "__main__":
	async def main():
		"""Run a simple database connectivity and initialization check."""
		await check_connection()
		await init_db()
		
		# DBの接続を閉じる
		await engine.dispose()


	# 単体実行処理
	asyncio.run(main())
