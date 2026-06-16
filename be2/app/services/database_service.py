"""
Database Service
Handles database connections and session management
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)


def _build_database_url() -> str:
    """
    Resolve database URL:
    1. DATABASE_URL env var (PostgreSQL on production)
    2. SQLite fallback: /data/be2.db (Railway/Docker volume) or in-memory
    """
    url = os.getenv("DATABASE_URL", "").strip()
    if url:
        # SQLAlchemy async requires postgresql+asyncpg://
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    sqlite_path = os.getenv("SQLITE_PATH", "/data/be2.db")
    return f"sqlite+aiosqlite:///{sqlite_path}"


class DatabaseService:
    """Database service for async SQLAlchemy operations"""

    def __init__(self):
        self.engine = None
        self.session_factory = None
        self._initialize_engine()

    def _initialize_engine(self):
        database_url = _build_database_url()
        is_sqlite = "sqlite" in database_url

        connect_args = {"check_same_thread": False} if is_sqlite else {}

        self.engine = create_async_engine(
            database_url,
            echo=os.getenv("DEBUG", "false").lower() == "true",
            pool_pre_ping=not is_sqlite,
            connect_args=connect_args,
        )

        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info(f"Database engine initialized: {database_url.split('@')[-1] if '@' in database_url else database_url}")

    async def connect(self):
        try:
            async with self.engine.begin() as conn:
                from sqlalchemy import text
                await conn.execute(text("SELECT 1"))
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            raise

    async def disconnect(self):
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connection closed")

    async def get_session(self):
        if not self.session_factory:
            raise RuntimeError("Database not initialized")
        async with self.session_factory() as session:
            try:
                yield session
            except SQLAlchemyError:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def execute_query(self, query: str, values: dict = None):
        from sqlalchemy import text
        async with self.engine.begin() as conn:
            if values:
                result = await conn.execute(text(query), values)
            else:
                result = await conn.execute(text(query))
            return result

    async def fetch_all(self, query: str, values: dict = None):
        result = await self.execute_query(query, values)
        return [dict(row._mapping) for row in result.fetchall()]

    async def fetch_one(self, query: str, values: dict = None):
        result = await self.execute_query(query, values)
        row = result.fetchone()
        return dict(row._mapping) if row else None


database_service = DatabaseService()
