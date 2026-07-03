"""势力数据模型。"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from models.database import ProjectBase


class Faction(ProjectBase):
    __tablename__ = "factions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    leader_id = Column(Integer, ForeignKey("characters.id", ondelete="SET NULL"))
    goals = Column(Text)
    allied_with = Column(Text)
    opposed_to = Column(Text)
    status = Column(String(20), default="active")
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
