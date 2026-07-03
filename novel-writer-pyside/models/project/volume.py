"""分卷数据模型。"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from models.database import ProjectBase


class Volume(ProjectBase):
    __tablename__ = "volumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    volume_number = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    sort_order = Column(Integer, default=0)
    is_complete = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
