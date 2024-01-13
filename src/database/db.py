from redis import Redis
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.messages import SESSION_NOT_CREATED, SOME_EXCEPTION_SESSION

from src.conf.config import config

import contextlib

SQLALCHEMY_DATABASE_URL = config.DB_URL

SessionLocal = sessionmaker

class DatabaseSessionManager:
    def __init__(self, url: str) -> None:
        self._engine: AsyncEngine = create_async_engine(SQLALCHEMY_DATABASE_URL)
        self._session_maker: async_sessionmaker = async_sessionmaker(autocommit=False, autoflush=False, bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncSession:
        if self._session_maker is None:
            raise Exception(SESSION_NOT_CREATED)

        session = self._session_maker()
        try:
            yield session
        except Exception as err:
            print(SOME_EXCEPTION_SESSION, err)
            await session.rollback()
        finally:
            await session.close()

sessionmanager = DatabaseSessionManager(SQLALCHEMY_DATABASE_URL)

# Dependency
async def get_db() -> AsyncSession:
    with sessionmanager.session() as session:
        yield session