"""角色出场数据模型。"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship as rel, backref
from models.database import ProjectBase


class ChapterAppearance(ProjectBase):
    __tablename__ = "character_appearances"

    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    role_type = Column(String(20), default="minor")
    significance = Column(Text)
    scene_description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    character = rel("Character", backref=backref("appearances", cascade="all, delete-orphan"))
