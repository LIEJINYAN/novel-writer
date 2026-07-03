"""AI 分析服务 - 章节质量分析。"""
from typing import Optional
from core.ai.ai_worker import AIWorker
from core.ai.manager import ai_manager
from core.ai.prompt_templates.registry import get_template
from core.ai.base import Message


class AnalysisService:
    """章节分析服务。"""

    def __init__(self):
        self._worker: Optional[AIWorker] = None

    def analyze_chapter(self, content: str, genre: str = "") -> AIWorker:
        """分析章节内容质量。

        Args:
            content: 章节全文
            genre: 小说类型（玄幻、都市、言情等）

        Returns:
            AIWorker 实例
        """
        template = get_template("analyze")
        message_dicts = template.build_messages(content=content, genre=genre)
        messages = [Message(**m) for m in message_dicts]
        config = ai_manager._create_config_from_active()
        config.stream = True
        self._worker = AIWorker(messages, config)
        return self._worker

    @property
    def is_running(self) -> bool:
        return self._worker is not None and self._worker.isRunning()

    def cancel(self):
        if self._worker:
            self._worker.cancel()
            self._worker = None


# 全局实例
analysis_service = AnalysisService()
