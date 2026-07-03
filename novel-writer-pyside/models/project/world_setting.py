"""世界观设定数据模型。"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from models.database import ProjectBase


class WorldSetting(ProjectBase):
    __tablename__ = "world_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    setting_type = Column(String(50), default="location")
    name = Column(String(200), nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("world_settings.id", ondelete="SET NULL"))
    importance = Column(String(20), default="medium")
    tags = Column(Text)
    related_characters = Column(Text)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
