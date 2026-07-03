from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime

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
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
