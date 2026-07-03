"""依赖注入容器 - 提供可选的仓储依赖注入支持。"""
from .container import ServiceContainer, ContainerError

__all__ = ["ServiceContainer", "ContainerError"]
