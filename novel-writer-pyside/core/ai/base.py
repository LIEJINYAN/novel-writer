"""AI Provider 抽象层。

定义 AI 调用所需的核心数据结构、异常类层级以及提供商抽象基类。
纯 Python 实现，不依赖任何第三方库。
"""
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Generator, Optional


@dataclass
class Message:
    """AI 对话消息。"""
    role: str  # "system" | "user" | "assistant"
    content: str

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}


@dataclass
class AIConfig:
    """AI 调用配置。"""
    model: str = ""
    temperature: float = 0.8
    max_tokens: int = 4096
    stream: bool = False
    api_key: str = ""
    api_base: str = ""


@dataclass
class TokenUsage:
    """Token 使用量。"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class AIResponse:
    """AI 响应。"""
    content: str = ""
    usage: TokenUsage = field(default_factory=TokenUsage)
    model: str = ""


class AIProviderError(Exception):
    """AI 提供商基础异常。"""
    pass


class AIConnectionError(AIProviderError):
    """连接错误（网络不通、服务未启动等）。"""
    pass


class AIAuthenticationError(AIProviderError):
    """认证错误（API Key 无效）。"""
    pass


class AIRateLimitError(AIProviderError):
    """速率限制错误。"""
    pass


class AIModelNotFoundError(AIProviderError):
    """模型不存在错误。"""
    pass


class BaseAIProvider(ABC):
    """AI 提供商抽象基类。"""

    # 提供商信息（子类覆盖）
    name: str = ""
    display_name: str = ""
    default_api_base: str = ""
    default_models: list[str] = []

    @abstractmethod
    def chat(self, messages: list[Message], config: AIConfig) -> AIResponse:
        """同步对话调用。"""
        pass

    @abstractmethod
    def chat_stream(self, messages: list[Message], config: AIConfig) -> Generator[str, None, None]:
        """流式对话调用，逐个 yield 文本 chunk。"""
        pass

    @abstractmethod
    def test_connection(self, api_key: str, api_base: str) -> bool:
        """测试连接是否可用。"""
        pass

    @abstractmethod
    def list_models(self, api_key: str, api_base: str) -> list[str]:
        """获取可用模型列表。"""
        pass
