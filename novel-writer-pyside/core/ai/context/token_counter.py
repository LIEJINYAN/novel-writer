"""Token 计数器 - 支持多种模型族的 Token 计数。"""

import logging

logger = logging.getLogger(__name__)

# 模型族到编码器的映射
MODEL_FAMILIES = {
    "gpt-4": "cl100k_base",
    "gpt-3.5": "cl100k_base",
    "gpt-4o": "o200k_base",
    "claude": "cl100k_base",
    "gemini": "cl100k_base",
    "deepseek": "cl100k_base",
    "qwen": "qwen2",
}


class TokenCounter:
    """Token 计数器。"""

    def __init__(self):
        self._encoders = {}
        self._has_tiktoken = False
        self._init_tiktoken()

    def _init_tiktoken(self):
        try:
            import tiktoken

            self._has_tiktoken = True
            logger.info("tiktoken 加载成功")
        except ImportError:
            logger.warning("tiktoken 未安装，将使用估算模式")

    def _get_encoder(self, model_family: str):
        """获取或缓存编码器。"""
        if not self._has_tiktoken:
            return None
        import tiktoken

        encoding_name = MODEL_FAMILIES.get(model_family, "cl100k_base")
        if encoding_name not in self._encoders:
            try:
                self._encoders[encoding_name] = tiktoken.get_encoding(encoding_name)
            except Exception:
                logger.warning(f"无法加载编码器 {encoding_name}，回退到 cl100k_base")
                self._encoders[encoding_name] = tiktoken.get_encoding("cl100k_base")
        return self._encoders[encoding_name]

    def count(self, text: str, model: str = "gpt-4") -> int:
        """计算文本的 token 数。

        Args:
            text: 输入文本
            model: 模型名称（用于选择编码器）
        Returns:
            int: token 数量
        """
        if not text:
            return 0

        # 确定模型族
        model_family = self._infer_family(model)

        if self._has_tiktoken:
            encoder = self._get_encoder(model_family)
            if encoder:
                try:
                    return len(encoder.encode(text))
                except Exception as e:
                    logger.warning(f"tiktoken 编码失败: {e}，回退到估算")

        # 估算模式：中文约 2 token/字，英文约 0.3 token/字
        return self._estimate(text)

    def _infer_family(self, model: str) -> str:
        """从模型名称推断模型族。"""
        model_lower = model.lower()
        if "gpt-4o" in model_lower:
            return "gpt-4o"
        elif "gpt-4" in model_lower or "gpt4" in model_lower:
            return "gpt-4"
        elif "gpt-3.5" in model_lower or "gpt-3" in model_lower:
            return "gpt-3.5"
        elif "claude" in model_lower:
            return "claude"
        elif "gemini" in model_lower:
            return "gemini"
        elif "deepseek" in model_lower:
            return "deepseek"
        elif "qwen" in model_lower:
            return "qwen"
        return "gpt-4"

    def _estimate(self, text: str) -> int:
        """估算 token 数（无 tiktoken 时使用）。"""
        # 中文字符（包括中文标点）约 2 token/字
        # 英文字符约 0.25 token/字 (1 token ≈ 4 chars)
        chinese_chars = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        other_chars = len(text) - chinese_chars
        return chinese_chars * 2 + int(other_chars * 0.25) + 1

    def count_messages(self, messages: list, model: str = "gpt-4") -> int:
        """计算消息列表的 token 数。

        Args:
            messages: Message 对象列表或 dict 列表（需有 content 字段）
            model: 模型名称
        Returns:
            int: token 总数
        """
        total = 0
        for msg in messages:
            content = ""
            if hasattr(msg, "content"):
                content = msg.content or ""
            elif isinstance(msg, dict):
                content = msg.get("content", "") or ""
            total += self.count(content, model)
            # 加上消息格式开销（约 4 token/消息）
            total += 4
        # 加上回复开销（约 2 token）
        total += 2
        return total

    def get_model_max_tokens(self, model: str) -> int:
        """获取模型的最大上下文长度。"""
        model_lower = model.lower()
        limits = {
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-4o": 128000,
            "gpt-3.5-turbo": 16384,
            "claude-sonnet-4": 200000,
            "claude-haiku-3-5": 200000,
            "gemini-2.0-flash": 1048576,
            "gemini-2.0-pro": 2097152,
            "deepseek-chat": 65536,
            "qwen-max": 32768,
            "qwen-plus": 131072,
        }
        for key, limit in limits.items():
            if key in model_lower:
                return limit
        return 8192  # 默认


# 全局实例
token_counter = TokenCounter()
