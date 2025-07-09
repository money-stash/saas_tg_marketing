from pytz import timezone
from datetime import datetime
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import secrets

from models.base import Base
from utils.logger import logger

from models.workers import Worker
from models.access_tokens import AccessToken

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

    async def create_worker(self, username: str, user_id: int):
        async with self.get_session() as session:
            now = datetime.now().strftime("%d-%m-%Y")
            user = Worker(username=username, user_id=user_id, date=now)
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

    ##########                          ##########
    ##########   AccessToken methods    ##########
    ##########                          ##########

    async def create_token(self, name: str, user_id: int = 0):
        async with self.get_session() as session:
            key = secrets.token_urlsafe(12)
            token = AccessToken(key=key, name=name, user_id=user_id)
            session.add(token)
            await session.commit()
            logger.info(f"Token created: {key} (name: {name})")

    async def get_all_tokens(self) -> list[AccessToken]:
        async with self.get_session() as session:
            result = await session.execute(select(AccessToken))
            return result.scalars().all()

    async def get_token_by_id(self, id: int) -> AccessToken | None:
        async with self.get_session() as session:
            result = await session.execute(
                select(AccessToken).where(AccessToken.id == id)
            )
            return result.scalar_one_or_none()

    async def delete_token(self, id: int):
        async with self.get_session() as session:
            await session.execute(delete(AccessToken).where(AccessToken.id == id))
            await session.commit()
            logger.info(f"Token {id} deleted")

    async def get_token_by_key(self, key: str) -> AccessToken | None:
        async with self.get_session() as session:
            result = await session.execute(
                select(AccessToken).where(AccessToken.key == key)
            )
            return result.scalar_one_or_none()

    async def bind_user_to_token(self, user_id: int, username: str, key: str):
        async with self.get_session() as session:
            token_result = await session.execute(
                select(AccessToken).where(AccessToken.key == key)
            )
            token = token_result.scalar_one_or_none()
            if not token:
                logger.warning(f"No token found for key: {key}")
                return False

            token.user_id = user_id

            worker_result = await session.execute(
                select(Worker).where(Worker.username == username)
            )
            worker = worker_result.scalar_one_or_none()
            if not worker:
                logger.warning(f"No worker found with username: {username}")
                return False

            worker.key_id = token.id

            await session.commit()
            logger.info(
                f"Token and worker updated for user_id: {user_id}, username: {username}"
            )
            return True


db = Database()
