"""通义千问适配器 - 兼容 OpenAI API 格式。"""

from .openai_provider import OpenAIProvider


class TongyiProvider(OpenAIProvider):
    """通义千问 AI 提供商。"""

    name = "tongyi"
    display_name = "通义千问"
    default_api_base = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    default_models = ["qwen-max", "qwen-plus", "qwen-turbo"]

    def __init__(self):
        super().__init__()
        self._api_base = self.default_api_base

    def _create_client(self, api_key, api_base=None):
        """创建 OpenAI 客户端，指向通义千问的端点。"""
        from openai import OpenAI
        base = api_base or self.default_api_base
        return OpenAI(api_key=api_key, base_url=base)
