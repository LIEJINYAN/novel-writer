from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean

from models.database import AppBase


class Plugin(AppBase):
    __tablename__ = "plugins"

    id = Column(Integer, primary_key=True)
    plugin_name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    version = Column(String(50))
    description = Column(Text)
    author = Column(String(100))
    path = Column(String(500), nullable=False)
    is_enabled = Column(Boolean, default=True)
    config = Column(Text)
    installed_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
