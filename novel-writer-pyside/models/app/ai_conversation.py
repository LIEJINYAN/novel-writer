from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Index

from models.database import AppBase


class AIConversation(AppBase):
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, nullable=True)
    title = Column(String(200))
    conversation_type = Column(String(50), default="chat")
    provider_name = Column(String(50))
    model = Column(String(100))
    messages = Column(Text, nullable=False)
    total_tokens = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    __table_args__ = (
        Index("idx_ai_conversations_project_id", "project_id"),
        Index("idx_ai_conversations_updated_at", "updated_at"),
    )
