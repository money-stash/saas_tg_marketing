from models.base import Base
from sqlalchemy import Column, Integer, String, Boolean


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    role = Column(String, default="worker")
    status = Column(Boolean, default=True)
    key_id = Column(Integer, default=0)
    user_id = Column(Integer)
    date = Column(String)
