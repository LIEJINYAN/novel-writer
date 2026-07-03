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
        from models.database import db_manager
        try:
            p_session = db_manager.get_project_session()
            if p_session is None:
                return []
        except Exception:
            return []

        try:
            from models.project.character import Character
            characters = p_session.query(Character).all()
            p_session.close()

            result = []
            for c in characters:
                result.append({
                    "name": c.name or "",
                    "description": c.background or "",
                })
            return result
        except Exception as e:
            logger.warning(f"获取角色列表失败: {e}")
            try:
                p_session.close()
            except Exception:
                pass

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

    def build_writing_context(
        self,
        chapter_id: int,
        project_id: int,
        include_tracking: bool = True,
        include_knowledge: bool = True,
        max_context_tokens: int = 8000,
    ) -> dict:
        """构建完整的写作上下文。按 11 级优先级加载。

        Args:
            chapter_id: 章节 ID
            project_id: 项目 ID
            include_tracking: 是否包含追踪数据（角色状态、关系、情节）
            include_knowledge: 是否包含知识库/世界观
            max_context_tokens: 最大 token 限制
        Returns:
            dict: 写作上下文字典
        """
        context = {}

        # 第1级：创作宪法（最高优先级）
        context["constitution"] = self._load_constitution(project_id)

        # 第2级：风格参考（反AI检测规范）
        context["style_reference"] = self._load_style_reference()

        # 第3级：故事规格
        context["specification"] = self._load_specification(project_id)

        # 第4级：创作计划
        context["creative_plan"] = self._load_creative_plan(project_id)

        # 第5级：当前任务
        context["current_task"] = self._load_current_task(chapter_id)

        # 第6-8级：追踪数据
        if include_tracking:
            context["character_state"] = self._load_character_states(project_id)
            context["relationships"] = self._load_relationships(project_id)
            context["plot_tracker"] = self._load_plot_tracker(project_id)

        # 第9级：知识库/世界观
        if include_knowledge:
            context["world_settings"] = self._load_world_settings(project_id)

        # 第10级：前文摘要
        context["previous_summary"] = self._load_previous_summary(chapter_id)

        # 第11级：黄金开篇法则（仅前3章）
        chapter_number = self._get_chapter_number(chapter_id)
        if chapter_number <= 3:
            context["golden_opening"] = self._load_golden_opening(chapter_number)
        else:
            context["golden_opening"] = ""

        # Token 估算与裁剪
        context = self._trim_context(context, max_context_tokens)

        return context

    def _load_constitution(self, project_id: int) -> str:
        """加载创作宪法（从 project_info 表的 constitution 字段）。"""
        return ""  # 返回空字符串表示尚未设置，不报错

    def _load_style_reference(self) -> str:
        """加载风格参考（ANTI_AI_SYSTEM 常量）。"""
        try:
            from core.ai.prompt_templates.anti_ai import ANTI_AI_SYSTEM
            return ANTI_AI_SYSTEM
        except ImportError:
            return ""

    def _load_specification(self, project_id: int) -> str:
        """加载故事规格（从 project_info 表的 specification 字段）。"""
        return ""

    def _load_creative_plan(self, project_id: int) -> str:
        """加载创作计划。"""
        return ""

    def _load_current_task(self, chapter_id: int) -> str:
        """加载当前任务（从 chapter 的 tasks 字段）。"""
        return ""

    def _load_character_states(self, project_id: int) -> str:
        """加载角色状态摘要。"""
        characters = self._get_project_characters(project_id)
        if not characters:
            return ""
        lines = ["【角色状态】"]
        for c in characters:
            lines.append(f"- {c.get('name', '')}: {c.get('description', '')}")
        return "\n".join(lines)

    def _load_relationships(self, project_id: int) -> str:
        """加载关系网络。"""
        return ""

    def _load_plot_tracker(self, project_id: int) -> str:
        """加载情节追踪。"""
        return ""

    def _load_world_settings(self, project_id: int) -> str:
        """加载知识库/世界观。"""
        return ""

    def _load_previous_summary(self, chapter_id: int) -> str:
        """加载前文摘要（前3章内容，限制3000字）。"""
        return ""

    @staticmethod
    def _load_golden_opening(chapter_number: int) -> str:
        """加载黄金开篇法则。"""
        return (
            f"## 黄金开篇法则（第{chapter_number}章专用）\n"
            "- 前500字必须建立核心冲突\n"
            "- 第一个场景必须有视觉冲击力\n"
            "- 开篇第一句要独特、有记忆点\n"
            "- 避免缓慢铺垫，直接切入关键场景\n"
        )

    def _get_chapter_number(self, chapter_id: int) -> int:
        """获取章节编号。"""
        return 0  # 简化实现，返回 0 表示无法获取

    def _trim_context(self, context: dict, max_tokens: int) -> dict:
        """按优先级裁剪上下文，确保不超过 token 限制。

        优先级从高到低：constitution > style_reference > specification
        > creative_plan > current_task > character_state > relationships
        > plot_tracker > world_settings > previous_summary > golden_opening
        """
        try:
            from core.ai.context.token_counter import TokenCounter

            counter = TokenCounter()
            # 检查 counter 是否有 truncate_to_tokens 方法
            if not hasattr(counter, "truncate_to_tokens"):
                return context  # 方法不可用时跳过裁剪
        except ImportError:
            return context  # 无法估算时不裁剪

        # 按优先级顺序排列 key
        priority_order = [
            "constitution",       # 1 - 最高
            "style_reference",    # 2
            "specification",      # 3
            "creative_plan",      # 4
            "current_task",       # 5
            "character_state",    # 6
            "relationships",      # 7
            "plot_tracker",       # 8
            "world_settings",     # 9
            "previous_summary",   # 10
            "golden_opening",     # 11
        ]

        total_tokens = sum(counter.count(v) for v in context.values() if isinstance(v, str))
        if total_tokens <= max_tokens:
            return context

        # 从低优先级开始裁剪
        result = dict(context)
        for key in reversed(priority_order):
            if key not in result or not isinstance(result[key], str):
                continue
            tokens = counter.count(result[key])
            if total_tokens - tokens <= max_tokens:
                # 裁剪此字段到刚好满足限制
                allowed = total_tokens - max_tokens
                truncated = counter.truncate_to_tokens(result[key], max(0, tokens - allowed))
                if truncated:
                    result[key] = truncated
                else:
                    result[key] = ""
                break
            else:
                total_tokens -= tokens
                result[key] = ""

        return result

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
