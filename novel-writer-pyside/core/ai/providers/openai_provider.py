"""OpenAI 适配器。"""
import httpx
from typing import Generator
from ..base import (
    BaseAIProvider, Message, AIConfig, AIResponse, TokenUsage,
    AIProviderError, AIConnectionError, AIAuthenticationError,
    AIRateLimitError, AIModelNotFoundError,
)


class OpenAIProvider(BaseAIProvider):
    """OpenAI 适配器，使用 openai Python SDK。"""

    name = "openai"
    display_name = "OpenAI"
    default_api_base = "https://api.openai.com/v1"
    default_models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]

    def _create_client(self, api_key: str, api_base: str):
        """创建 OpenAI 客户端。"""
        from openai import OpenAI
        return OpenAI(api_key=api_key, base_url=api_base or self.default_api_base)

    def chat(self, messages: list[Message], config: AIConfig) -> AIResponse:
        """同步对话调用。"""
        # 创建客户端
        client = self._create_client(config.api_key, config.api_base)

        # 构建 messages
        msg_list = [m.to_dict() for m in messages]

        try:
            response = client.chat.completions.create(
                model=config.model,
                messages=msg_list,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                stream=False,
            )

            # 解析响应
            content = response.choices[0].message.content or ""
            usage = TokenUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
            )
            return AIResponse(content=content, usage=usage, model=response.model)

        except Exception as e:
            raise self._handle_error(e)

    def chat_stream(self, messages: list[Message], config: AIConfig) -> Generator[str, None, None]:
        """流式对话调用。"""
        client = self._create_client(config.api_key, config.api_base)
        msg_list = [m.to_dict() for m in messages]

        try:
            stream = client.chat.completions.create(
                model=config.model,
                messages=msg_list,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                stream=True,
            )

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise self._handle_error(e)

    def test_connection(self, api_key: str, api_base: str) -> bool:
        """测试连接。"""
        if not api_key:
            raise AIAuthenticationError("API Key 不能为空")

        try:
            client = self._create_client(api_key, api_base)
            # 调用 models.list() 验证连接
            client.models.list()
            return True
        except Exception as e:
            raise self._handle_error(e)

    def list_models(self, api_key: str, api_base: str) -> list[str]:
        """获取可用模型列表。"""
        if not api_key:
            raise AIAuthenticationError("API Key 不能为空")

        try:
            client = self._create_client(api_key, api_base)
            models = client.models.list()
            return [m.id for m in models.data]
        except Exception as e:
            raise self._handle_error(e)

    def _handle_error(self, error: Exception) -> AIProviderError:
        """将 OpenAI SDK 错误转换为自定义异常。"""
        error_msg = str(error)

        # 导入 openai 异常类
        try:
            from openai import (
                APIConnectionError,
                AuthenticationError,
                RateLimitError,
                NotFoundError,
            )

            if isinstance(error, AuthenticationError):
                return AIAuthenticationError(f"API Key 无效: {error_msg}")
            if isinstance(error, APIConnectionError):
                return AIConnectionError(f"网络连接失败: {error_msg}")
            if isinstance(error, RateLimitError):
                return AIRateLimitError(f"请求频率超限: {error_msg}")
            if isinstance(error, NotFoundError):
                return AIModelNotFoundError(f"模型不存在: {error_msg}")
        except ImportError:
            pass

        return AIProviderError(f"AI 调用失败: {error_msg}")
