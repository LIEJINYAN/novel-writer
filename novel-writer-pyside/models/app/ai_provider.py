from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime

from models.database import AppBase


class AIProvider(AppBase):
    __tablename__ = "ai_providers"

    id = Column(Integer, primary_key=True)
    provider_name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    api_key_encrypted = Column("api_key", Text, nullable=True)
    api_base = Column(String(500), nullable=True)
    default_model = Column(String(100), nullable=True)
    is_enabled = Column(Integer, default=1)
    is_default = Column(Integer, default=0)
    config = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
