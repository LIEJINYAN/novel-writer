"""项目管理服务 - 薄包装层，委托给 ProjectManager。"""
from typing import Optional, List
from PySide6.QtCore import QObject, Signal
from models import Project
from core.project import ProjectManager
from utils.signal_bus import signal_bus
from utils.logger import logger


class ProjectService(QObject):
    """项目服务 - 管理项目的 CRUD 操作（委托给 ProjectManager）。"""

    project_created = Signal(int)      # 项目创建 (project_id)
    project_opened = Signal(int)       # 项目打开 (project_id)
    project_closed = Signal()          # 项目关闭
    project_deleted = Signal(int)      # 项目删除 (project_id)
    project_updated = Signal(int)      # 项目更新 (project_id)

    def __init__(self, project_manager: Optional[ProjectManager] = None):
        super().__init__()
        self._current_project: Optional[Project] = None
        self._manager = project_manager or ProjectManager()

    @property
    def current_project(self) -> Optional[Project]:
        return self._current_project

    # ========== 项目 CRUD ==========

    def create_project(self, info: dict) -> Project:
        """创建新项目。"""
        project = self._manager.create_project(info)
        self._current_project = project
        self.project_created.emit(project.id)
        self.project_opened.emit(project.id)
        return project

    def open_project(self, project_id: int) -> Optional[Project]:
        """打开项目。"""
        project = self._manager.open_project(project_id)
        if project:
            self._current_project = project
            signal_bus.project_opened.emit(project.id)
            self.project_opened.emit(project.id)
        return project

    def get_project(self, project_id: int) -> Optional[Project]:
        """获取项目对象。"""
        return self._manager.get_project(project_id)

    def get_project_by_path(self, path: str) -> Optional[Project]:
        """通过路径查找项目。"""
        return self._manager.get_project_by_path(path)

    def delete_project(self, project_id: int) -> bool:
        """删除/归档项目。"""
        result = self._manager.delete_project(project_id)
        if result:
            self.project_deleted.emit(project_id)
        return result

    def list_projects(self) -> List[Project]:
        """获取所有活跃项目列表。"""
        return self._manager.list_projects()

    # ========== 回收站操作 ==========

    def list_archived_projects(self) -> List[Project]:
        """列出所有已归档的项目。"""
        return self._manager.list_archived_projects()

    def restore_project(self, project_id: int) -> bool:
        """恢复已归档的项目。"""
        return self._manager.restore_project(project_id)

    def hard_delete_project(self, project_id: int) -> bool:
        """彻底删除项目。"""
        return self._manager.hard_delete_project(project_id)

    def hard_delete_all_projects(self) -> int:
        """永久删除所有已归档的项目。"""
        return self._manager.hard_delete_all_projects()

    # ========== 统计 & 归档 ==========

    def get_project_stats(self, project_id: int) -> dict:
        """获取项目统计信息。"""
        return self._manager.get_project_stats(project_id)

    def archive_project(self, project_id: int) -> bool:
        """归档项目。"""
        return self._manager.archive_project(project_id)
