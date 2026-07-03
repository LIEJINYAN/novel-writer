"""关系数据模型。"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from models.database import ProjectBase


class Relationship(ProjectBase):
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, autoincrement=True)
    character_a_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    character_b_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    relationship_type = Column(String(50), default="neutral")
    description = Column(Text)
    initial_relation = Column(String(100), default="陌生人")
    current_relation = Column(String(100), default="陌生人")
    trajectory = Column(String(20), default="stable")
    intensity = Column(Integer, default=5)
    key_events = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        UniqueConstraint("character_a_id", "character_b_id"),
    )
