"""角色数据模型。"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from models.database import ProjectBase


class Character(ProjectBase):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    aliases = Column(Text)
    role = Column(String(50), default="supporting")
    importance = Column(String(20), default="medium")
    gender = Column(String(20))
    age = Column(Integer)
    appearance = Column(Text)
    personality = Column(Text)
    background = Column(Text)
    motivation = Column(Text)
    skills = Column(Text)
    possessions = Column(Text)
    secrets = Column(Text)
    character_arc = Column(Text)
    avatar = Column(String(500))
    sort_order = Column(Integer, default=0)
    is_deleted = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        Index("idx_characters_role", "role"),
        Index("idx_characters_importance", "importance"),
    )
