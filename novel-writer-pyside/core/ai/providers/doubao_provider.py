"""豆包适配器 - 兼容 OpenAI API 格式。"""

from .openai_provider import OpenAIProvider


class DoubaoProvider(OpenAIProvider):
    """豆包 AI 提供商。"""

    name = "doubao"
    display_name = "豆包"
    default_api_base = "https://ark.cn-beijing.volces.com/api/v3"
    default_models = ["doubao-pro", "doubao-lite"]

    def __init__(self):
        super().__init__()
        self._api_base = self.default_api_base

    def _create_client(self, api_key, api_base=None):
        """创建 OpenAI 客户端，指向豆包的端点。"""
        from openai import OpenAI
        base = api_base or self.default_api_base
        return OpenAI(api_key=api_key, base_url=base)
