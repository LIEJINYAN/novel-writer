"""一致性检查服务 - 规则引擎 + AI 深度检查（委托至 ConsistencyChecker）。"""
from __future__ import annotations
from typing import Optional, Callable
from models import Chapter
from models.database import db_manager
from core.ai.ai_worker import AIWorker
from core.ai.manager import ai_manager
from core.ai.prompt_templates.registry import get_template
from core.ai.base import Message
from core.tracking.consistency_checker import ConsistencyChecker, CheckResult


class ConsistencyService:

    def __init__(self):
        self._checker = ConsistencyChecker(db_manager)

    def check_all(self, project_id: int) -> dict[str, list[dict]]:
        """执行所有一致性检查，按类别分组返回字典。

        返回格式:
        {
            'character_issues': [{'description': str, 'severity': str, 'suggestion': str}, ...],
            'relationship_issues': [...],
            'world_issues': [...],
        }
        """
        results = self._checker.check_all(project_id)
        grouped = {
            'character_issues': [],
            'relationship_issues': [],
            'world_issues': [],
        }
        for r in results:
            item = {
                'description': r.message,
                'severity': r.severity,
                'suggestion': r.detail,
            }
            if r.category == '角色':
                grouped['character_issues'].append(item)
            elif r.category == '关系':
                grouped['relationship_issues'].append(item)
            elif r.category == '世界观':
                grouped['world_issues'].append(item)
            elif r.category == '时间线':
                # 时间线问题归到角色分类下展示
                grouped['character_issues'].append(item)
        return grouped

    def run_rules(self, project_id: int) -> list[CheckResult]:
        """执行三类规则检查。"""
        return self._checker.run_rules(project_id)

    def run_ai_check(self, project_id: int,
                     on_chunk: Callable[[str], None],
                     on_done: Callable[[], None],
                     on_error: Callable[[str], None]) -> Optional[AIWorker]:
        """AI 深度一致性检查。"""
        session = db_manager.get_project_session()
        try:
            # 获取项目所有章节内容摘要
            chapters = session.query(Chapter).filter(
                Chapter.is_deleted == 0,
            ).order_by(Chapter.chapter_number).all()

            content_summary = "\n".join(
                f"第{c.chapter_number}章 {c.title}:\n{(c.content_plain or '')[:500]}"
                for c in chapters
            )

            if not content_summary.strip():
                on_error("项目中没有章节内容")
                return None

            template = get_template("consistency_check")
            message_dicts = template.build_messages(content=content_summary)
            messages = [Message(**m) for m in message_dicts]

            config = ai_manager._create_config_from_active()

            worker = AIWorker(messages, config)
            worker.chunk_received.connect(on_chunk)
            worker.finished.connect(on_done)
            worker.error_signal.connect(on_error)
            worker.start()
            return worker
        finally:
            session.close()


consistency_service = ConsistencyService()
