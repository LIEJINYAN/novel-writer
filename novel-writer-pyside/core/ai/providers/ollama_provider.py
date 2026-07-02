"""Ollama 适配器，通过 httpx 调用本地 REST API。"""
import json
import httpx
from typing import Generator
from ..base import (
    BaseAIProvider, Message, AIConfig, AIResponse, TokenUsage,
    AIProviderError, AIConnectionError, AIAuthenticationError,
)


class OllamaProvider(BaseAIProvider):
    """Ollama 本地模型适配器。"""

    name = "ollama"
    display_name = "Ollama"
    default_api_base = "http://localhost:11434"
    default_models = ["llama3", "qwen2", "phi3"]

    def chat(self, messages: list[Message], config: AIConfig) -> AIResponse:
        """同步对话调用。"""
        api_base = config.api_base or self.default_api_base
        url = f"{api_base.rstrip('/')}/api/chat"

        # 构建 Ollama 格式的请求
        payload = {
            "model": config.model,
            "messages": [m.to_dict() for m in messages],
            "stream": False,
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_tokens,
            },
        }

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()

            data = response.json()
            content = data.get("message", {}).get("content", "")

            # Ollama 返回的 usage
            eval_count = data.get("eval_count", 0)
            prompt_eval_count = data.get("prompt_eval_count", 0)
            usage = TokenUsage(
                prompt_tokens=prompt_eval_count,
                completion_tokens=eval_count,
                total_tokens=prompt_eval_count + eval_count,
            )

            return AIResponse(content=content, usage=usage, model=config.model)

        except httpx.ConnectError:
            raise AIConnectionError(f"无法连接到 Ollama 服务（{api_base}），请确认 Ollama 已启动")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                from ..base import AIModelNotFoundError
                raise AIModelNotFoundError(f"模型 '{config.model}' 不存在，请先拉取模型")
            raise AIProviderError(f"Ollama API 错误: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise AIProviderError(f"Ollama 调用失败: {e}")

    def chat_stream(self, messages: list[Message], config: AIConfig) -> Generator[str, None, None]:
        """流式对话调用，逐行解析 ndjson。"""
        api_base = config.api_base or self.default_api_base
        url = f"{api_base.rstrip('/')}/api/chat"

        payload = {
            "model": config.model,
            "messages": [m.to_dict() for m in messages],
            "stream": True,
            "options": {
                "temperature": config.temperature,
                "num_predict": config.max_tokens,
            },
        }

        try:
            with httpx.Client(timeout=120.0) as client:
                with client.stream("POST", url, json=payload) as response:
                    response.raise_for_status()
                    # Ollama 流式返回 ndjson（每行一个 JSON）
                    for line in response.iter_lines():
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            content = data.get("message", {}).get("content", "")
                            if content:
                                yield content
                            # 检查是否结束
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue

        except httpx.ConnectError:
            raise AIConnectionError(f"无法连接到 Ollama 服务（{api_base}），请确认 Ollama 已启动")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                from ..base import AIModelNotFoundError
                raise AIModelNotFoundError(f"模型 '{config.model}' 不存在")
            raise AIProviderError(f"Ollama API 错误: {e.response.status_code}")
        except Exception as e:
            raise AIProviderError(f"Ollama 流式调用失败: {e}")

    def test_connection(self, api_key: str, api_base: str) -> bool:
        """测试连接，GET /api/tags 验证服务是否可用。"""
        # Ollama 不需要 API Key
        base = api_base or self.default_api_base
        url = f"{base.rstrip('/')}/api/tags"

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url)
                response.raise_for_status()
            return True
        except httpx.ConnectError:
            raise AIConnectionError(f"无法连接到 Ollama 服务（{base}），请确认 Ollama 已启动")
        except httpx.HTTPStatusError as e:
            raise AIProviderError(f"Ollama 连接错误: {e.response.status_code}")
        except Exception as e:
            raise AIConnectionError(f"Ollama 连接失败: {e}")

    def list_models(self, api_key: str, api_base: str) -> list[str]:
        """获取本地已安装模型列表，GET /api/tags。"""
        base = api_base or self.default_api_base
        url = f"{base.rstrip('/')}/api/tags"

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url)
                response.raise_for_status()

            data = response.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            # 过滤空名称
            return [m for m in models if m]
        except httpx.ConnectError:
            raise AIConnectionError(f"无法连接到 Ollama 服务（{base}），请确认 Ollama 已启动")
        except Exception as e:
            raise AIProviderError(f"获取模型列表失败: {e}")
