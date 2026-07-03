"""项目信息数据模型。"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from models.database import ProjectBase


class ProjectInfo(ProjectBase):
    __tablename__ = "project_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    type = Column(String(20), default="novel")
    description = Column(Text)
    genre = Column(String(50))
    target_audience = Column(String(50))
    tone = Column(String(50))
    themes = Column(Text)
    estimated_length = Column(Integer, default=0)
    writing_method = Column(String(50), default="three-act")
    hybrid_scheme = Column(Text)
    language = Column(String(20), default="zh-CN")
    status = Column(String(20), default="active")
    config_version = Column(String(20), default="1.0.0")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
