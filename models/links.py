from models.base import Base
from sqlalchemy import Column, Integer, String, Boolean


class ChannelLink(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True)
    link = Column(String, nullable=False)
    link_name = Column(String, nullable=False)
    active = Column(Boolean, default=False)
    spam_text = Column(String, nullable=False)
