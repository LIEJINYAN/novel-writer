"""指数退避重试中间件。"""

import time
import random
import logging
import functools
from typing import Type, Tuple

logger = logging.getLogger(__name__)

# 可重试的错误类型
RETRYABLE_ERRORS = ("AIConnectionError", "AIRateLimitError", "TimeoutError")

# 不可重试的错误类型
NON_RETRYABLE_ERRORS = ("AIAuthenticationError", "AIModelNotFoundError", "AIConfigError")


def is_retryable(error: Exception) -> bool:
    """判断错误是否可重试。"""
    error_name = type(error).__name__
    if error_name in NON_RETRYABLE_ERRORS:
        return False
    if error_name in RETRYABLE_ERRORS:
        return True
    # 网络相关错误
    if isinstance(error, (ConnectionError, TimeoutError)):
        return True
    return False


class RetryContext:
    """重试上下文，记录重试信息。"""

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.attempt = 0
        self.last_error: Exception | None = None

    @property
    def is_exhausted(self) -> bool:
        return self.attempt >= self.max_retries

    @property
    def remaining(self) -> int:
        return max(0, self.max_retries - self.attempt)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    on_retry=None,
):
    """指数退避重试装饰器。
    
    Args:
        max_retries: 最大重试次数
        base_delay: 基础延迟（秒）
        max_delay: 最大延迟（秒）
        on_retry: 重试回调，签名 (attempt, max_retries, error) -> None
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            context = RetryContext(max_retries)

            for attempt in range(max_retries + 1):
                context.attempt = attempt
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if not is_retryable(e):
                        logger.warning(f"不可重试错误: {type(e).__name__}: {e}")
                        raise
                    
                    if attempt < max_retries:
                        delay = min(max_delay, base_delay * (2 ** attempt))
                        delay += random.uniform(0, 0.1)  # 抖动
                        
                        logger.info(
                            f"第 {attempt + 1}/{max_retries} 次重试 "
                            f"({type(e).__name__}: {e}) "
                            f"等待 {delay:.1f}s"
                        )
                        
                        if on_retry:
                            on_retry(attempt + 1, max_retries, e)
                        
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"重试耗尽 ({max_retries} 次), "
                            f"最后错误: {type(e).__name__}: {e}"
                        )
                        raise
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


class RetrySignalEmitter:
    """重试信号发射器 - 用于 AIWorker 的非装饰器方式集成。"""

    def __init__(self, max_retries=3, base_delay=1.0, max_delay=30.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.retry_callback = None  # 外部设置：def on_retry(attempt, max_retries, error)

    def execute(self, func, *args, **kwargs):
        """执行函数，自动重试。"""
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if not is_retryable(e):
                    raise

                if attempt < self.max_retries:
                    delay = min(self.max_delay, self.base_delay * (2 ** attempt))
                    delay += random.uniform(0, 0.1)

                    if self.retry_callback:
                        self.retry_callback(attempt + 1, self.max_retries, str(e))

                    time.sleep(delay)
                else:
                    raise

        raise last_error  # 不会执行到这里，满足类型检查
