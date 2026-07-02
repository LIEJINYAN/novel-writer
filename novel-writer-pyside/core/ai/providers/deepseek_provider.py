"""DeepSeek 适配器，复用 OpenAI SDK（DeepSeek 兼容 OpenAI 接口）。"""
from .openai_provider import OpenAIProvider


class DeepSeekProvider(OpenAIProvider):
    """DeepSeek 适配器，继承 OpenAIProvider，覆盖配置。"""

    name = "deepseek"
    display_name = "DeepSeek"
    default_api_base = "https://api.deepseek.com/v1"
    default_models = ["deepseek-chat", "deepseek-reasoner"]
