"""依赖注入容器实现。

提供简单的仓储依赖注入支持，服务层可选择性使用仓储而非直接操作 db_manager。

用法：
    container = ServiceContainer()
    chapter_service = ChapterService(repo=container.chapter_repo)
"""

from typing import Optional
from core.repositories import (
    BaseRepository,
    ChapterRepository,
    VolumeRepository,
    CharacterRepository,
    PlotNodeRepository,
    AIProviderRepository,
)


class ContainerError(Exception):
    """容器相关错误。"""


class ServiceContainer:
    """服务容器 - 管理仓储实例的创建和注入。"""

    def __init__(self):
        self._repos: dict[str, BaseRepository] = {}

    @property
    def chapter_repo(self) -> ChapterRepository:
        return self._get_or_create("chapter", ChapterRepository)

    @property
    def volume_repo(self) -> VolumeRepository:
        return self._get_or_create("volume", VolumeRepository)

    @property
    def character_repo(self) -> CharacterRepository:
        return self._get_or_create("character", CharacterRepository)

    @property
    def plot_node_repo(self) -> PlotNodeRepository:
        return self._get_or_create("plot_node", PlotNodeRepository)

    @property
    def ai_provider_repo(self) -> AIProviderRepository:
        return self._get_or_create("ai_provider", AIProviderRepository)

    def register(self, name: str, repo: BaseRepository) -> None:
        """手动注册仓储实例。"""
        self._repos[name] = repo

    def get(self, name: str) -> Optional[BaseRepository]:
        """获取已注册的仓储。"""
        return self._repos.get(name)

    def _get_or_create(self, name: str, repo_class: type) -> BaseRepository:
        if name not in self._repos:
            self._repos[name] = repo_class()
        return self._repos[name]


# 全局默认容器
default_container = ServiceContainer()
