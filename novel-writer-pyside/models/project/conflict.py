"""冲突数据模型。"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from models.database import ProjectBase


class Conflict(ProjectBase):
    __tablename__ = "conflicts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    conflict_type = Column(String(50), default="person/person")
    status = Column(String(20), default="active")
    parties_involved = Column(Text)
    start_chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="SET NULL"))
    end_chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="SET NULL"))
    resolution = Column(Text)
    escalation_level = Column(Integer, default=1)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
