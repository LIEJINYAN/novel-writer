from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Index

from models.database import AppBase


class Project(AppBase):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    path = Column(String(1024), unique=True, nullable=False)
    description = Column(Text)
    genre = Column(String(50))
    writing_method = Column(String(50), default="three-act")
    total_words = Column(Integer, default=0)
    chapter_count = Column(Integer, default=0)
    status = Column(String(20), default="active")
    cover_image = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    last_opened_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_projects_updated_at", "updated_at"),
        Index("idx_projects_status", "status"),
    )
