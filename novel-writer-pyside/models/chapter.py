"""章节数据模型。"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class Volume(Base):
    __tablename__ = "volumes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False, comment="分卷名称")
    sort_order = Column(Integer, default=0, comment="排序")
    description = Column(Text, default="", comment="分卷描述")
    
    project = relationship("Project", backref="volumes")
    chapters = relationship("Chapter", backref="volume", order_by="Chapter.chapter_number")

class Chapter(Base):
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    volume_id = Column(Integer, ForeignKey("volumes.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    chapter_number = Column(Integer, default=1, comment="章节号")
    title = Column(String(255), nullable=False, comment="章节标题")
    content = Column(Text, default="", comment="章节内容")
    word_count = Column(Integer, default=0, comment="字数")
    status = Column(String(20), default="draft", comment="状态: draft/review/final")
    is_deleted = Column(Boolean, default=False, comment="软删除")
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    project = relationship("Project", backref="chapters")
