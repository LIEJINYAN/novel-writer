"""Anthropic 适配器。"""
from typing import Generator
from ..base import (
    BaseAIProvider, Message, AIConfig, AIResponse, TokenUsage,
    AIProviderError, AIConnectionError, AIAuthenticationError,
    AIRateLimitError, AIModelNotFoundError,
)


class AnthropicProvider(BaseAIProvider):
    """Anthropic (Claude) 适配器，使用 anthropic Python SDK。"""

    name = "anthropic"
    display_name = "Anthropic"
    default_api_base = "https://api.anthropic.com"
    default_models = ["claude-sonnet-4", "claude-haiku-3-5"]

    def _create_client(self, api_key: str, api_base: str):
        """创建 Anthropic 客户端。"""
        from anthropic import Anthropic
        return Anthropic(api_key=api_key, base_url=api_base or self.default_api_base)

    def _handle_error(self, error: Exception) -> AIProviderError:
        """将 Anthropic SDK 错误映射为自定义异常。"""
        error_msg = str(error)

        try:
            from anthropic import (
                AuthenticationError,
                APIError,
                APIConnectionError,
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
            if isinstance(error, APIError):
                return AIProviderError(f"API 错误: {error_msg}")
        except ImportError:
            pass

        return AIProviderError(f"AI 调用失败: {error_msg}")

    @staticmethod
    def _split_system_message(messages: list[Message]) -> tuple:
        """将 system 消息从 messages 列表中分离。"""
        system_prompt = None
        converted_messages = []
        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content
            else:
                converted_messages.append({"role": msg.role, "content": msg.content})
        return system_prompt, converted_messages

    def chat(self, messages: list[Message], config: AIConfig) -> AIResponse:
        """同步对话调用。"""
        client = self._create_client(config.api_key, config.api_base)
        system_prompt, converted_messages = self._split_system_message(messages)

        try:
            kwargs = {
                "model": config.model,
                "messages": converted_messages,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
            }
            if system_prompt:
                kwargs["system"] = system_prompt

            response = client.messages.create(**kwargs)

            # 提取所有文本块内容
            content = ""
            for block in response.content:
                if block.type == "text":
                    content += block.text

            # 解析 token 用量
            usage = TokenUsage(
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens,
            )

            return AIResponse(content=content, usage=usage, model=response.model)

        except Exception as e:
            raise self._handle_error(e)

    def chat_stream(self, messages: list[Message], config: AIConfig) -> Generator[str, None, None]:
        """流式对话调用。"""
        client = self._create_client(config.api_key, config.api_base)
        system_prompt, converted_messages = self._split_system_message(messages)

        try:
            kwargs = {
                "model": config.model,
                "messages": converted_messages,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "stream": True,
            }
            if system_prompt:
                kwargs["system"] = system_prompt

            stream = client.messages.create(**kwargs)

            for event in stream:
                if event.type == "content_block_delta" and event.delta.type == "text_delta":
                    yield event.delta.text

        except Exception as e:
            raise self._handle_error(e)

    def test_connection(self, api_key: str, api_base: str) -> bool:
        """测试连接。"""
        if not api_key:
            raise AIAuthenticationError("API Key 不能为空")

        try:
            client = self._create_client(api_key, api_base)
            # 调用 models.list 验证连接
            client.models.list(limit=1)
            return True
        except Exception as e:
            raise self._handle_error(e)

    def list_models(self, api_key: str, api_base: str) -> list[str]:
        """获取可用模型列表。"""
        if not api_key:
            raise AIAuthenticationError("API Key 不能为空")

        try:
            client = self._create_client(api_key, api_base)
            models_page = client.models.list()
            model_ids = [m.id for m in models_page.data]

            # 合并 default_models 和 API 返回的模型，保持顺序并去重
            seen = set()
            result = []
            for m in self.default_models + model_ids:
                if m not in seen:
                    seen.add(m)
                    result.append(m)
            return result
        except Exception:
            # API 调用失败时返回 default_models 作为兜底
            return list(self.default_models)
