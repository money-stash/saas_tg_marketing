from models.base import Base
from sqlalchemy import Column, Integer, String, Boolean


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    date = Column(String)
    account_id = Column(Integer)
    path = Column(String)
    is_valid = Column(Boolean, default=True)
