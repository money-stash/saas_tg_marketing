from models.base import Base
from sqlalchemy import Column, Integer, String, Boolean


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    path = Column(String)
    worker_id = Column(Integer)
    is_valid = Column(Boolean, default=True)
