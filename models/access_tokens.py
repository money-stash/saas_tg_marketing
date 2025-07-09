from models.base import Base
from sqlalchemy import Column, Integer, String, Boolean


class AccessToken(Base):
    __tablename__ = "AccessTokens"

    id = Column(Integer, primary_key=True)
    key = Column(String)
    name = Column(String)
    user_id = Column(Integer, default=0)
