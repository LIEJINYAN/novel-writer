"""Google Gemini 适配器。"""
from typing import Generator

from ..base import (
    BaseAIProvider, Message, AIConfig, AIResponse, TokenUsage,
    AIProviderError, AIConnectionError, AIAuthenticationError,
    AIRateLimitError, AIModelNotFoundError,
)


class GeminiProvider(BaseAIProvider):
    """Google Gemini 适配器，使用 google-generativeai SDK。"""

    name = "gemini"
    display_name = "Google Gemini"
    default_api_base = ""
    default_models = ["gemini-2.0-flash", "gemini-2.0-pro"]

    def _convert_messages(self, messages: list[Message]) -> list:
        """将 Message 列表转换为 Gemini contents 格式。

        Gemini 不支持独立的 system 参数，system 指令拼入第一个 user 消息开头。
        """
        contents = []
        system_text = ""
        for msg in messages:
            if msg.role == "system":
                system_text += msg.content + "\n"
            elif msg.role == "user":
                text = system_text + msg.content if system_text else msg.content
                contents.append({"role": "user", "parts": [text]})
                system_text = ""
            elif msg.role == "assistant":
                contents.append({"role": "model", "parts": [msg.content]})
        return contents

    def chat(self, messages: list[Message], config: AIConfig) -> AIResponse:
        """同步对话调用。"""
        import google.generativeai as genai

        genai.configure(api_key=config.api_key)

        # 转换消息格式
        contents = self._convert_messages(messages)

        try:
            model = genai.GenerativeModel(config.model)
            response = model.generate_content(contents)

            return AIResponse(
                content=response.text or "",
                usage=None,
                model=config.model,
            )

        except Exception as e:
            raise self._handle_error(e)

    def chat_stream(self, messages: list[Message], config: AIConfig) -> Generator[str, None, None]:
        """流式对话调用。"""
        import google.generativeai as genai

        genai.configure(api_key=config.api_key)

        # 转换消息格式
        contents = self._convert_messages(messages)

        try:
            model = genai.GenerativeModel(config.model)
            stream = model.generate_content(contents, stream=True)

            for chunk in stream:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            raise self._handle_error(e)

    def test_connection(self, api_key: str, api_base: str) -> bool:
        """测试连接是否可用。

        调用 genai.list_models() 验证 API Key 是否有效。
        """
        if not api_key:
            raise AIAuthenticationError("API Key 不能为空")

        import google.generativeai as genai

        genai.configure(api_key=api_key)

        try:
            genai.list_models()
            return True
        except Exception as e:
            raise self._handle_error(e)

    def list_models(self, api_key: str, api_base: str) -> list[str]:
        """获取可用模型列表。

        如果 API 调用失败，返回 default_models 作为兜底。
        """
        if not api_key:
            raise AIAuthenticationError("API Key 不能为空")

        import google.generativeai as genai

        genai.configure(api_key=api_key)

        try:
            models = genai.list_models()
            return [m.name.replace("models/", "") for m in models]
        except Exception:
            return list(self.default_models)

    def _handle_error(self, error: Exception) -> AIProviderError:
        """将 Google API 错误转换为自定义异常。"""
        error_msg = str(error)

        try:
            from google.api_core import exceptions as google_exceptions

            if isinstance(error, google_exceptions.PermissionDenied):
                return AIAuthenticationError(f"API Key 无效: {error_msg}")
            if isinstance(error, google_exceptions.NotFound):
                return AIModelNotFoundError(f"模型不存在: {error_msg}")
            if isinstance(error, google_exceptions.ResourceExhausted):
                return AIRateLimitError(f"请求频率超限: {error_msg}")
            if isinstance(error, google_exceptions.ServiceUnavailable):
                return AIConnectionError(f"服务暂不可用: {error_msg}")
            if isinstance(error, google_exceptions.GoogleAPICallError):
                return AIProviderError(f"Google API 调用失败: {error_msg}")
        except ImportError:
            pass

        return AIProviderError(f"AI 调用失败: {error_msg}")
