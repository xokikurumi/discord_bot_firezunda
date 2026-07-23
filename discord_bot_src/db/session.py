from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import DB_URL

# =========================
# Engine（接続プール）
# =========================
engine = create_async_engine(
    DB_URL,
    echo=False,           # デバッグ時はTrue
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True    # 切断検知（重要）
)


# =========================
# Session Factory
# =========================
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# =========================
# セッション取得（推奨）
# =========================
async def get_session():
    """Yield an async database session for dependency-style callers."""
    async with AsyncSessionLocal() as session:
        yield session
