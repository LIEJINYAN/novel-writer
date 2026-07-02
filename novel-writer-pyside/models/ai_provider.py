"""AI 提供商配置模型。"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from .database import Base

class AIProvider(Base):
    __tablename__ = "ai_providers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, comment="提供商标识")
    display_name = Column(String(100), comment="显示名称")
    api_key_encrypted = Column(String(1024), default="", comment="加密后的 API Key")
    api_base = Column(String(1024), comment="API 地址")
    default_model = Column(String(100), default="", comment="默认模型")
    temperature = Column(Float, default=0.8)
    max_tokens = Column(Integer, default=4096)
    is_enabled = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
