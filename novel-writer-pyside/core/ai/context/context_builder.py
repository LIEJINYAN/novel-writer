"""上下文构建器 - 从数据库加载章节、角色、项目信息并构建 AI 友好的上下文。"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ContextBuilder:
    """上下文构建器。"""

    def __init__(self):
        self._db = None  # 延迟初始化

    def _get_db(self):
        """获取数据库会话。"""
        if self._db is not None:
            try:
                self._db.close()
            except Exception:
                pass
            self._db = None

        try:
            from models import db_manager
            self._db = db_manager.get_session()
        except (ImportError, Exception) as e:
            logger.warning(f"无法获取数据库会话: {e}")
            return None
        return self._db

    def _get_project_info(self, project_id: int) -> dict:
        """获取项目信息。"""
        db = self._get_db()
        if db is None:
            return {"name": "", "genre": "", "description": ""}

        try:
            # 尝试不同的模型导入路径
            project = None
            try:
                from models import Project
                project = db.query(Project).filter(Project.id == project_id).first()
            except (ImportError, AttributeError):
                pass

            if project is None:
                try:
                    from app.models import Project
                    project = db.query(Project).filter(Project.id == project_id).first()
                except (ImportError, AttributeError):
                    pass

            if project is None:
                try:
                    from app.database.models import Project
                    project = db.query(Project).filter(Project.id == project_id).first()
                except (ImportError, AttributeError):
                    pass

            if project:
                return {
                    "name": getattr(project, 'name', '') or '',
                    "genre": getattr(project, 'genre', '') or '',
                    "description": getattr(project, 'description', '') or '',
                }
        except Exception as e:
            logger.warning(f"获取项目信息失败: {e}")

        return {"name": "", "genre": "", "description": ""}

    def _get_chapter_content(self, chapter_id: int) -> str:
        """获取章节内容。"""
        db = self._get_db()
        if db is None:
            return ""

        try:
            chapter = None
            try:
                from models import Chapter
                chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
            except (ImportError, AttributeError):
                pass

            if chapter is None:
                try:
                    from app.models import Chapter
                    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
                except (ImportError, AttributeError):
                    pass

            if chapter is None:
                try:
                    from app.database.models import Chapter
                    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
                except (ImportError, AttributeError):
                    pass

            if chapter:
                return getattr(chapter, 'content', '') or ''
        except Exception as e:
            logger.warning(f"获取章节内容失败: {e}")

        return ""

    def _get_chapter_title(self, chapter_id: int) -> str:
        """获取章节标题。"""
        db = self._get_db()
        if db is None:
            return ""

        try:
            chapter = None
            try:
                from models import Chapter
                chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
            except (ImportError, AttributeError):
                pass

            if chapter is None:
                try:
                    from app.models import Chapter
                    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
                except (ImportError, AttributeError):
                    pass

            if chapter is None:
                try:
                    from app.database.models import Chapter
                    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
                except (ImportError, AttributeError):
                    pass

            if chapter:
                return getattr(chapter, 'title', '') or ''
        except Exception as e:
            logger.warning(f"获取章节标题失败: {e}")

        return ""

    def _get_project_characters(self, project_id: int) -> list[dict]:
        """获取项目角色列表。"""
        db = self._get_db()
        if db is None:
            return []

        try:
            characters = []
            # 尝试不同的模型导入路径
            try:
                from models import Character
                characters = db.query(Character).filter(Character.project_id == project_id).all()
            except (ImportError, AttributeError):
                pass

            if not characters:
                try:
                    from app.models import Character
                    characters = db.query(Character).filter(Character.project_id == project_id).all()
                except (ImportError, AttributeError):
                    pass

            if not characters:
                try:
                    from app.database.models import Character
                    characters = db.query(Character).filter(Character.project_id == project_id).all()
                except (ImportError, AttributeError):
                    pass

            if not characters:
                return []

            result = []
            for c in characters:
                result.append({
                    "name": getattr(c, 'name', '') or '',
                    "description": getattr(c, 'description', '') or '',
                })
            return result
        except Exception as e:
            logger.warning(f"获取角色列表失败: {e}")

        return []

    def build_chapter_context(self, chapter_id: int, project_id: int) -> str:
        """构建章节上下文。包含章节内容、项目信息和角色信息。

        Args:
            chapter_id: 章节 ID
            project_id: 项目 ID
        Returns:
            str: 格式化的上下文文本
        """
        project = self._get_project_info(project_id)
        title = self._get_chapter_title(chapter_id)
        content = self._get_chapter_content(chapter_id)
        characters = self._get_project_characters(project_id)

        parts = []
        parts.append(f"【项目信息】\n项目名称：{project['name']}\n类型：{project['genre']}\n简介：{project['description']}\n")

        if characters:
            char_lines = []
            for c in characters:
                char_lines.append(f"- {c['name']}: {c['description']}")
            parts.append(f"【角色列表】\n" + "\n".join(char_lines) + "\n")

        if title:
            parts.append(f"【当前章节】\n标题：{title}\n")

        if content:
            parts.append(f"【章节内容】\n{content}\n")

        return "\n".join(parts)

    def build_project_context(self, project_id: int) -> str:
        """构建项目级上下文。

        Args:
            project_id: 项目 ID
        Returns:
            str: 项目上下文
        """
        project = self._get_project_info(project_id)
        characters = self._get_project_characters(project_id)

        parts = []
        parts.append(f"项目名称：{project['name']}")
        parts.append(f"类型：{project['genre']}")
        parts.append(f"简介：{project['description']}")

        if characters:
            parts.append(f"\n角色列表：")
            for c in characters:
                parts.append(f"- {c['name']}: {c['description']}")

        return "\n".join(parts)

    def build_analysis_context(self, chapter_id: int, project_id: int) -> str:
        """构建分析专用上下文（章节内容+项目信息，不含角色详情）。

        Args:
            chapter_id: 章节 ID
            project_id: 项目 ID
        Returns:
            str: 分析上下文
        """
        project = self._get_project_info(project_id)
        title = self._get_chapter_title(chapter_id)
        content = self._get_chapter_content(chapter_id)

        parts = []
        parts.append(f"项目信息：{project['name']} | {project['genre']}")
        if title:
            parts.append(f"章节：{title}")
        if content:
            parts.append(f"\n{content}")

        return "\n".join(parts)

    def close(self):
        """关闭数据库会话。"""
        if self._db is not None:
            try:
                self._db.close()
            except Exception:
                pass
            self._db = None

    def __del__(self):
        self.close()


# 全局实例
context_builder = ContextBuilder()
