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
from models.sessions import Session
from models.reports import Report
from models.tasks import Task
from models.links import ChannelLink

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

    async def block_user(self, id: int):
        async with self.get_session() as session:
            await session.execute(
                update(Worker).where(Worker.id == id).values(status=False)
            )
            await session.commit()
            logger.info(f"Worker {id} blocked")

    async def block_user_by_username(self, username: str):
        async with self.get_session() as session:
            await session.execute(
                update(Worker).where(Worker.username == username).values(status=False)
            )
            await session.commit()
            logger.info(f"Worker with username '{username}' blocked")

    async def unblock_user(self, id: int):
        async with self.get_session() as session:
            await session.execute(
                update(Worker).where(Worker.id == id).values(status=True)
            )
            await session.commit()
            logger.info(f"Worker {id} unblocked")

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
            return key

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
            result = await session.execute(
                select(AccessToken).where(AccessToken.id == id)
            )
            token = result.scalar_one_or_none()
            if not token:
                logger.warning(f"Token {id} not found")
                return

            user_id = token.user_id

            worker_result = await session.execute(
                select(Worker).where(Worker.user_id == user_id)
            )
            worker = worker_result.scalar_one_or_none()
            if worker:
                worker.key_id = 0

            await session.delete(token)
            await session.commit()
            logger.info(f"Token {id} deleted and worker key_id reset if applicable")

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

    ##########                          ##########
    ##########      Session methods     ##########
    ##########                          ##########

    async def add_session(self, account_id: int, path: str, is_valid: bool = True):
        async with self.get_session() as session:
            now = datetime.now().strftime("%d-%m-%Y")
            new_session = Session(
                account_id=account_id, path=path, is_valid=is_valid, date=now
            )
            session.add(new_session)
            await session.commit()

    async def delete_session(self, session_id: int):
        async with self.get_session() as session:
            await session.execute(delete(Session).where(Session.id == session_id))
            await session.commit()

    async def get_all_sessions(self) -> list[Session]:
        async with self.get_session() as session:
            result = await session.execute(select(Session))
            return result.scalars().all()

    async def get_session_by_id(self, session_id: int) -> Session | None:
        async with self.get_session() as session:
            result = await session.execute(
                select(Session).where(Session.id == session_id)
            )
            return result.scalar_one_or_none()

    async def get_session_by_session_path(self, session_path: str) -> Session | None:
        async with self.get_session() as session:
            result = await session.execute(
                select(Session).where(Session.path == session_path)
            )
            return result.scalar_one_or_none()

    ##########                          ##########
    ##########     Report methods       ##########
    ##########                          ##########

    async def add_report(self, date: str, worker_id: int, path: str, type_: str):
        async with self.get_session() as session:
            report = Report(date=date, worker_id=worker_id, path=path, type=type_)
            session.add(report)
            await session.commit()
            logger.info(f"Report added: {path}")

    async def get_all_reports(self) -> list[Report]:
        async with self.get_session() as session:
            result = await session.execute(select(Report))
            return result.scalars().all()

    async def get_report_by_id(self, report_id: int) -> Report | None:
        async with self.get_session() as session:
            result = await session.execute(select(Report).where(Report.id == report_id))
            return result.scalar_one_or_none()

    ##########                          ##########
    ##########      Task methods        ##########
    ##########                          ##########

    async def add_task(
        self, task_type: str, status: bool = True, logs: str = ""
    ) -> int:
        async with self.get_session() as session:
            task = Task(task_type=task_type, status=status, logs=logs)
            session.add(task)
            await session.flush()
            await session.commit()
            logger.info(f"Task added: type={task_type}")
            return task.id

    async def delete_task(self, task_id: int):
        async with self.get_session() as session:
            await session.execute(delete(Task).where(Task.id == task_id))
            await session.commit()
            logger.info(f"Task deleted: id={task_id}")

    ##########                          ##########
    ##########    ChannelLink methods   ##########
    ##########                          ##########

    async def add_channel_link(self, link: str, spam_text: str, link_name: str = ""):
        async with self.get_session() as session:
            new_link = ChannelLink(link=link, spam_text=spam_text, link_name=link_name)
            session.add(new_link)
            await session.commit()
            logger.info(f"Channel link added: {link}")

    async def delete_channel_link_by_id(self, link_id: int):
        async with self.get_session() as session:
            await session.execute(delete(ChannelLink).where(ChannelLink.id == link_id))
            await session.commit()
            logger.info(f"Channel link deleted by ID: {link_id}")

    async def delete_channel_link_by_url(self, link: str):
        async with self.get_session() as session:
            await session.execute(delete(ChannelLink).where(ChannelLink.link == link))
            await session.commit()
            logger.info(f"Channel link deleted by URL: {link}")

    async def get_all_channel_links(self) -> list[ChannelLink]:
        async with self.get_session() as session:
            result = await session.execute(select(ChannelLink))
            return result.scalars().all()

    async def get_channel_link_by_id(self, link_id: int) -> ChannelLink | None:
        async with self.get_session() as session:
            result = await session.execute(
                select(ChannelLink).where(ChannelLink.id == link_id)
            )
            return result.scalar_one_or_none()

    async def update_channel_link_text(self, link_id: int, new_spam_text: str):
        async with self.get_session() as session:
            await session.execute(
                update(ChannelLink)
                .where(ChannelLink.id == link_id)
                .values(spam_text=new_spam_text)
            )
            await session.commit()
            logger.info(f"Channel link ID {link_id} updated with new spam_text")

    async def update_channel_link_status(self, link_id: int, status: bool):
        async with self.get_session() as session:
            await session.execute(
                update(ChannelLink)
                .where(ChannelLink.id == link_id)
                .values(active=status)
            )
            await session.commit()
            logger.info(
                f"Channel link ID {link_id} updated with new active status: {status}"
            )


db = Database()
