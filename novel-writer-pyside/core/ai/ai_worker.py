"""AI 后台线程 Worker。"""
import random
from PySide6.QtCore import QThread, Signal
from typing import Generator
from .base import Message, AIConfig, AIProviderError
from .manager import ai_manager


class AIWorker(QThread):
    """AI 调用后台线程，支持流式输出和取消。"""

    # 信号
    chunk_received = Signal(str)    # 收到一个文本块
    finished_signal = Signal(str)   # 生成完成（参数为完整文本）
    error_signal = Signal(str)      # 生成出错（参数为错误消息）
    retry_signal = Signal(int, int, str)  # 重试通知 (attempt, max_retries, error_msg)

    def __init__(self, messages: list[Message], config: AIConfig, parent=None):
        super().__init__(parent)
        self._messages = messages
        self._config = config
        self._cancelled = False

    def run(self):
        """线程执行：调用 AI 流式接口，带自动重试。"""
        from .retry_middleware import is_retryable

        max_retries = 3
        base_delay = 1.0
        max_delay = 30.0

        for attempt in range(max_retries + 1):
            try:
                full_text = ""
                # 调用 AI 管理器的流式接口
                stream = ai_manager.chat_stream(self._messages, self._config)

                for chunk in stream:
                    if self._cancelled:
                        self.finished_signal.emit(full_text)
                        return
                    full_text += chunk
                    self.chunk_received.emit(chunk)

                # 成功完成
                self.finished_signal.emit(full_text)
                return

            except Exception as e:
                if self._cancelled:
                    return

                if not is_retryable(e) or attempt >= max_retries:
                    # 不可重试或重试耗尽
                    if isinstance(e, AIProviderError):
                        self.error_signal.emit(str(e))
                    else:
                        self.error_signal.emit(f"AI 调用失败: {e}")
                    return

                # 指数退避重试
                delay = min(max_delay, base_delay * (2 ** attempt))
                delay += random.uniform(0, 0.1)  # 抖动

                self.retry_signal.emit(attempt + 1, max_retries, str(e))
                self.msleep(int(delay * 1000))

    def cancel(self):
        """取消生成。"""
        self._cancelled = True
