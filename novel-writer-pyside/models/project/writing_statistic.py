"""写作统计数据模型。"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime
from models.database import ProjectBase


class WritingStatistic(ProjectBase):
    __tablename__ = "writing_statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, unique=True, nullable=False)
    words_written = Column(Integer, default=0)
    words_deleted = Column(Integer, default=0)
    net_words = Column(Integer, default=0)
    time_spent = Column(Integer, default=0)
    chapters_started = Column(Integer, default=0)
    chapters_finished = Column(Integer, default=0)
    sessions = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
