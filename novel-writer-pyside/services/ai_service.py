"""AI 服务 - 作为 core/ai/ 子模块的统一 Facade 入口。"""
from typing import Optional, Generator

from PySide6.QtCore import QObject, Signal

from core.ai.manager import ai_manager
from core.ai.writing_service import writing_service
from core.ai.editing_service import editing_service
from core.ai.analysis_service import analysis_service
from core.ai.chat_service import chat_service
from core.ai.base import AIProviderError, Message
from core.ai.ai_worker import AIWorker


class AIService(QObject):
    """AI 服务 - 作为 core/ai/ 子模块的统一 Facade 入口。"""

    # 信号
    ai_started = Signal(str)              # AI 调用开始 (operation)
    ai_finished = Signal(str)             # AI 调用完成 (operation)
    ai_error = Signal(str, str)           # AI 错误 (error_type, message)
    ai_stream_chunk = Signal(str)         # 流式输出块 (text)
    ai_progress = Signal(int, int)        # 进度 (current, total)

    def __init__(self, parent=None):
        super().__init__(parent)
        # 内部引用 core/ai/ 模块的全局单例
        self._manager = ai_manager
        self._writing_service = writing_service
        self._editing_service = editing_service
        self._analysis_service = analysis_service
        self._chat_service = chat_service

    def init(self):
        """初始化 AI 管理器。"""
        self._manager.init()

    def continue_writing(self, chapter_id: int, project_id: int, max_tokens: int = 2000) -> AIWorker:
        """AI 续写。返回 AIWorker 实例。"""
        worker = self._writing_service.continue_write(chapter_id, project_id, max_tokens=max_tokens)
        worker.finished_signal.connect(lambda t: self.ai_finished.emit("continue_writing"))
        worker.error_signal.connect(lambda e: self.ai_error.emit("continue_writing", e))
        self.ai_started.emit("continue_writing")
        return worker

    def polish_text(self, text: str, style: str = "简洁") -> AIWorker:
        """AI 润色选中文本。返回 AIWorker 实例。"""
        worker = self._editing_service.polish(text, style)
        worker.finished_signal.connect(lambda t: self.ai_finished.emit("polish_text"))
        worker.error_signal.connect(lambda e: self.ai_error.emit("polish_text", e))
        self.ai_started.emit("polish_text")
        return worker

    def rewrite_text(self, text: str, style: str = "扩写") -> AIWorker:
        """AI 重写选中文本。返回 AIWorker 实例。"""
        worker = self._editing_service.rewrite(text, direction=style)
        worker.finished_signal.connect(lambda t: self.ai_finished.emit("rewrite_text"))
        worker.error_signal.connect(lambda e: self.ai_error.emit("rewrite_text", e))
        self.ai_started.emit("rewrite_text")
        return worker

    def analyze_chapter(self, content: str, context: str = "") -> AIWorker:
        """AI 分析章节。返回 AIWorker 实例。"""
        worker = self._analysis_service.analyze_chapter(content, genre=context)
        worker.finished_signal.connect(lambda t: self.ai_finished.emit("analyze_chapter"))
        worker.error_signal.connect(lambda e: self.ai_error.emit("analyze_chapter", e))
        self.ai_started.emit("analyze_chapter")
        return worker

    def list_providers(self) -> list:
        """获取可用 AI 提供商列表。"""
        return self._manager.list_providers()

    def set_active_provider(self, name: str) -> None:
        """切换当前 AI 提供商。"""
        self._manager.set_active_provider(name)

    def chat(self, messages: list, provider: str = None) -> Generator[str, None, None]:
        """AI 对话流式调用。

        Args:
            messages: Message 对象列表
            provider: 可选，指定提供商名称

        Yields:
            流式文本块
        """
        if provider and provider != self._manager._active_provider_name:
            self._manager.set_active_provider(provider)
        yield from self._manager.chat_stream(messages)

    def get_active_provider(self):
        """获取当前激活的提供商实例。"""
        return self._manager.get_active_provider()

    def create_constitution(self, genre: str = "", target_audience: str = "",
                            estimated_length: str = "", tone: str = "",
                            themes: str = "", user_input: str = "") -> "AIWorker":
        """创建创作宪法（七步法第1步）。
        
        使用 constitution 模板构建消息，返回 AIWorker 实例。
        """
        from core.ai.prompt_templates.registry import get_template
        from core.ai.ai_worker import AIWorker
        from core.ai.manager import ai_manager
        from core.ai.base import AIProviderError, Message

        provider = ai_manager.get_active_provider()
        if provider is None:
            raise AIProviderError("未配置 AI 提供商，请先在设置中配置")

        template = get_template("constitution")
        if template is None:
            raise AIProviderError("找不到创作宪法模板")

        messages_data = template.build_messages(
            genre=genre,
            target_audience=target_audience,
            estimated_length=estimated_length,
            tone=tone,
            themes=themes,
            user_input=user_input,
        )
        messages = [Message(**m) for m in messages_data]
        config = ai_manager._create_config_from_active()
        config.stream = True

        worker = AIWorker(messages, config)
        worker.finished_signal.connect(lambda t: self.ai_finished.emit("create_constitution"))
        worker.error_signal.connect(lambda e: self.ai_error.emit("create_constitution", e))
        self.ai_started.emit("create_constitution")
        return worker

    def create_specification(self, user_input: str = "", level: int = 1) -> "AIWorker":
        """创建故事规格（七步法第2步）。"""
        from core.ai.prompt_templates.registry import get_template
        from core.ai.ai_worker import AIWorker
        from core.ai.manager import ai_manager
        from core.ai.base import AIProviderError, Message

        provider = ai_manager.get_active_provider()
        if provider is None:
            raise AIProviderError("未配置 AI 提供商")

        template = get_template("specify")
        if template is None:
            raise AIProviderError("找不到故事规格模板")

        messages_data = template.build_messages(user_input=user_input, level=str(level))
        messages = [Message(**m) for m in messages_data]
        config = ai_manager._create_config_from_active()
        config.stream = True

        worker = AIWorker(messages, config)
        worker.finished_signal.connect(lambda t: self.ai_finished.emit("create_specification"))
        worker.error_signal.connect(lambda e: self.ai_error.emit("create_specification", e))
        self.ai_started.emit("create_specification")
        return worker

    def clarify_decisions(self, specification: str = "") -> "AIWorker":
        """澄清决策点（七步法第3步）。"""
        from core.ai.prompt_templates.registry import get_template
        from core.ai.ai_worker import AIWorker
        from core.ai.manager import ai_manager
        from core.ai.base import AIProviderError, Message

        provider = ai_manager.get_active_provider()
        if provider is None:
            raise AIProviderError("未配置 AI 提供商")

        template = get_template("clarify")
        if template is None:
            raise AIProviderError("找不到决策澄清模板")

        messages_data = template.build_messages(specification=specification)
        messages = [Message(**m) for m in messages_data]
        config = ai_manager._create_config_from_active()
        config.stream = True

        worker = AIWorker(messages, config)
        worker.finished_signal.connect(lambda t: self.ai_finished.emit("clarify_decisions"))
        worker.error_signal.connect(lambda e: self.ai_error.emit("clarify_decisions", e))
        self.ai_started.emit("clarify_decisions")
        return worker

    def create_plan(self, specification: str = "", constitution: str = "") -> "AIWorker":
        """制定创作计划（七步法第4步）。"""
        from core.ai.prompt_templates.registry import get_template
        from core.ai.ai_worker import AIWorker
        from core.ai.manager import ai_manager
        from core.ai.base import AIProviderError, Message

        provider = ai_manager.get_active_provider()
        if provider is None:
            raise AIProviderError("未配置 AI 提供商")

        template = get_template("plan")
        if template is None:
            raise AIProviderError("找不到创作计划模板")

        messages_data = template.build_messages(specification=specification, constitution=constitution)
        messages = [Message(**m) for m in messages_data]
        config = ai_manager._create_config_from_active()
        config.stream = True

        worker = AIWorker(messages, config)
        worker.finished_signal.connect(lambda t: self.ai_finished.emit("create_plan"))
        worker.error_signal.connect(lambda e: self.ai_error.emit("create_plan", e))
        self.ai_started.emit("create_plan")
        return worker

    def generate_tasks(self, plan: str = "") -> "AIWorker":
        """分解执行任务（七步法第5步）。"""
        from core.ai.prompt_templates.registry import get_template
        from core.ai.ai_worker import AIWorker
        from core.ai.manager import ai_manager
        from core.ai.base import AIProviderError, Message

        provider = ai_manager.get_active_provider()
        if provider is None:
            raise AIProviderError("未配置 AI 提供商")

        template = get_template("tasks")
        if template is None:
            raise AIProviderError("找不到任务分解模板")

        messages_data = template.build_messages(plan=plan)
        messages = [Message(**m) for m in messages_data]
        config = ai_manager._create_config_from_active()
        config.stream = True

        worker = AIWorker(messages, config)
        worker.finished_signal.connect(lambda t: self.ai_finished.emit("generate_tasks"))
        worker.error_signal.connect(lambda e: self.ai_error.emit("generate_tasks", e))
        self.ai_started.emit("generate_tasks")
        return worker
