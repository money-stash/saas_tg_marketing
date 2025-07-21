from models.base import Base
from sqlalchemy import Column, Integer, String


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    date = Column(String)
    worker_id = Column(Integer)  # тот кто создал задание
    path = Column(String)  # путь к файлу отчета
    type = Column(String)  # тип отчета (например, "spammer", "parser")
