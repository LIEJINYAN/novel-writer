"""伏笔数据模型。"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from models.database import ProjectBase


class Foreshadowing(ProjectBase):
    __tablename__ = "foreshadowings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    importance = Column(String(20), default="medium")
    planted_chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="SET NULL"))
    planted_description = Column(Text)
    reveal_chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="SET NULL"))
    reveal_description = Column(Text)
    status = Column(String(20), default="active")
    hints = Column(Text)
    related_characters = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
