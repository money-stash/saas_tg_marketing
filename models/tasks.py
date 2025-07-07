from models.base import Base
from sqlalchemy import Column, Integer, String, Boolean


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    task_type = Column(String)
    status = Column(Boolean)
    logs = Column(String)
