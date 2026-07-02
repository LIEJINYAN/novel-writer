"""角色数据模型。"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .database import Base


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(100), nullable=False)
    aliases = Column(Text, default="")       # 别名，逗号分隔
    gender = Column(String(20), default="")
    age = Column(String(50), default="")
    role_type = Column(String(50), default="")
    personality = Column(Text, default="")   # 性格标签
    appearance = Column(Text, default="")    # 外貌描述
    background = Column(Text, default="")    # 背景故事
    arc = Column(Text, default="")           # 角色弧线
    status = Column(String(50), default="活跃")
    notes = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_deleted = Column(Integer, default=0)

    project = relationship("Project", backref="characters")
    appearances = relationship("ChapterAppearance", back_populates="character",
                               cascade="all, delete-orphan")


class ChapterAppearance(Base):
    __tablename__ = "chapter_appearances"

    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    role = Column(String(50), default="次要")  # 主要/次要/提及
    context = Column(Text, default="")        # 出场描述

    character = relationship("Character", back_populates="appearances")
    chapter = relationship("Chapter")
