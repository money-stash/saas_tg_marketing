from pytz import timezone
from datetime import datetime
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from models.base import Base
from utils.logger import logger

from models.workers import Worker

from config import DB_PATH


class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()

        return cls._instance

    def _init(self):
        self.database_url = f"sqlite+aiosqlite:///{DB_PATH}"
        self.engine = create_async_engine(self.database_url, echo=False)
        self.async_session = async_sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    async def init_models(self):
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            logger.info("Database initialized")

        except Exception as e:
            logger.error(f"Error initializing DB: {e}")

    def get_session(self) -> AsyncSession:
        return self.async_session()

    ##########                          ##########
    ##########      Worker methods      ##########
    ##########                          ##########

    async def create_worker(self, username: str):
        async with self.get_session() as session:
            user = Worker(
                username=username,
            )
            session.add(user)
            await session.commit()

            logger.info(f"Worker {username} created")

    async def get_users(self) -> list[Worker]:
        async with self.get_session() as session:
            result = await session.execute(select(Worker))
            return result.scalars().all()

    async def get_user(self, id: int) -> Worker | None:
        async with self.get_session() as session:
            result = await session.execute(select(Worker).where(Worker.id == id))
            return result.scalar_one_or_none()

    async def updated_username(self, id: int, username: str):
        async with self.get_session() as session:
            await session.execute(
                update(Worker).where(Worker.id == id).values(username=username)
            )
            await session.commit()

            logger.info(f"Worker {id}(username) updated")

    async def delete_user(self, id: int):
        async with self.get_session() as session:
            await session.execute(delete(Worker).where(Worker.id == id))
            await session.commit()


db = Database()
