"""关系历史数据模型。"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from models.database import ProjectBase


class RelationshipHistory(ProjectBase):
    __tablename__ = "relationship_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    relationship_id = Column(Integer, ForeignKey("relationships.id", ondelete="CASCADE"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="SET NULL"))
    change_type = Column(String(20), default="change")
    old_relation = Column(String(100))
    new_relation = Column(String(100))
    description = Column(Text)
    impact = Column(String(20), default="medium")
    created_at = Column(DateTime, default=datetime.now)
