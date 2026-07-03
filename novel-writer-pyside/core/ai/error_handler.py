"""AI 错误处理框架。

定义 AI 调用相关的上层服务异常类层级和自动重试机制。
与 core.ai.base 中的 AIProviderError（底层 Provider 异常）独立共存。
"""
import asyncio
from functools import wraps


class AIError(Exception):
    """AI 调用基础异常。"""
    pass


class RateLimitError(AIError):
    """速率限制异常。"""
    def __init__(self, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(f"请求过于频繁，请 {retry_after} 秒后重试")


class AuthError(AIError):
    """认证失败异常。"""
    pass


class ModelNotAvailableError(AIError):
    """模型不可用异常。"""
    pass


class ContextTooLongError(AIError):
    """上下文过长异常。"""
    pass


def with_retry(max_retries=3, base_delay=1.0, max_delay=60.0):
    """指数退避重试装饰器。

    Args:
        max_retries: 最大重试次数。
        base_delay: 基础延迟秒数。
        max_delay: 最大延迟秒数。
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except RateLimitError as e:
                    last_error = e
                    delay = min(e.retry_after, max_delay)
                    await asyncio.sleep(delay)
                except (ConnectionError, TimeoutError) as e:
                    last_error = e
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    await asyncio.sleep(delay)
                except AuthError:
                    raise  # 认证错误不重试
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
                    else:
                        raise
            raise last_error
        return wrapper
    return decorator


__all__ = [
    "AIError",
    "RateLimitError",
    "AuthError",
    "ModelNotAvailableError",
    "ContextTooLongError",
    "with_retry",
]
