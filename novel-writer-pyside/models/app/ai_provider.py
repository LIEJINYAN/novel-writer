from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean

from models.database import AppBase


class AIProvider(AppBase):
    __tablename__ = "ai_providers"

    id = Column(Integer, primary_key=True)
    provider_name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    api_key_encrypted = Column("api_key", Text, nullable=True)
    api_base = Column(String(500), nullable=True)
    default_model = Column(String(100), nullable=True)
    temperature = Column(Float, default=0.8)
    max_tokens = Column(Integer, default=4096)
    is_enabled = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    config = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
