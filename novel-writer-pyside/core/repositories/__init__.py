"""仓储层模块 - 提供统一的数据访问抽象。"""
from .base import BaseRepository
from .project_repository import ProjectRepository
from .chapter_repository import ChapterRepository, VolumeRepository
from .character_repository import CharacterRepository, ChapterAppearanceRepository
from .plot_repository import PlotArcRepository, PlotNodeRepository, PlotForeshadowRepository
from .ai_provider_repository import AIProviderRepository

__all__ = [
    "BaseRepository",
    "ProjectRepository",
    "ChapterRepository",
    "VolumeRepository",
    "CharacterRepository",
    "ChapterAppearanceRepository",
    "PlotArcRepository",
    "PlotNodeRepository",
    "PlotForeshadowRepository",
    "AIProviderRepository",
]
