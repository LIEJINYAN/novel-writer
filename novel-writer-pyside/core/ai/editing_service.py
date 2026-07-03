"""AI 编辑服务 - 润色、重写。"""
from typing import Optional
from core.ai.ai_worker import AIWorker
from core.ai.manager import ai_manager
from core.ai.prompt_templates.registry import get_template
from core.ai.base import Message, AIProviderError


class EditingAIService:
    """AI 编辑服务。"""

    def __init__(self):
        self._worker: Optional[AIWorker] = None

    def polish(self, text: str, style: str = "简洁") -> AIWorker:
        """润色文本。

        Args:
            text: 用户选中的文本
            style: 润色风格（简洁/优美/正式/口语化）

        Returns:
            AIWorker 实例（已配置好信号）

        Raises:
            AIProviderError: 未配置 AI 提供商
        """
        provider = ai_manager.get_active_provider()
        if provider is None:
            raise AIProviderError("未配置 AI 提供商，请先在设置中配置")

        template = get_template("polish")
        if template is None:
            raise AIProviderError("找不到润色模板")

        messages_data = template.build_messages(text=text, style=style)
        messages = [Message(**m) for m in messages_data]
        config = ai_manager._create_config_from_active()
        config.stream = True

        self._worker = AIWorker(messages, config)
        return self._worker

    def rewrite(self, text: str, direction: str = "扩写") -> AIWorker:
        """重写文本。

        Args:
            text: 用户选中的文本
            direction: 改写方向（扩写/缩写/改视角/改人称）

        Returns:
            AIWorker 实例

        Raises:
            AIProviderError: 未配置 AI 提供商
        """
        provider = ai_manager.get_active_provider()
        if provider is None:
            raise AIProviderError("未配置 AI 提供商，请先在设置中配置")

        template = get_template("rewrite")
        if template is None:
            raise AIProviderError("找不到重写模板")

        messages_data = template.build_messages(text=text, direction=direction)
        messages = [Message(**m) for m in messages_data]
        config = ai_manager._create_config_from_active()
        config.stream = True

        self._worker = AIWorker(messages, config)
        return self._worker

    @property
    def is_running(self) -> bool:
        """是否正在生成。"""
        return self._worker is not None and self._worker.isRunning()

    def cancel(self):
        """取消当前生成。"""
        if self._worker:
            if self._worker.isRunning():
                self._worker.cancel()
            self._worker = None


# 全局实例
editing_service = EditingAIService()
