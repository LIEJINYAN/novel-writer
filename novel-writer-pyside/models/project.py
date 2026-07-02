"""项目数据模型。"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SAEnum
from .database import Base

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, comment="项目名称")
    path = Column(String(1024), nullable=True, comment="项目路径")
    genre = Column(String(50), default="", comment="小说类型")
    writing_method = Column(String(50), default="three-act", comment="写作方法")
    status = Column(String(20), default="active", comment="状态: active/archived")
    description = Column(Text, default="", comment="项目简介")
    target_words = Column(Integer, default=0, comment="目标字数")
    cover_image = Column(String(1024), nullable=True, comment="封面路径")
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"
