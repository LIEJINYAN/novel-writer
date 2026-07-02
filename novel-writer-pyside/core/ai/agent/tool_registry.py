"""工具注册中心 - 管理所有 Agent 可用工具。"""

from dataclasses import dataclass, field
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class Tool:
    """工具定义。"""
    name: str                      # 工具名称，如 "continue_write"
    description: str               # 自然语言描述，供 LLM 理解用途
    handler: Callable              # 执行函数，接收 **kwargs 返回 dict
    parameters: dict = field(default_factory=dict)  # JSON Schema 参数定义
    category: str = "edit"         # 分类: read/edit/system/network
    icon: str = "🔧"               # UI 图标


class ToolRegistry:
    """工具注册中心。"""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        """注册工具。"""
        self._tools[tool.name] = tool
        logger.info(f"注册工具: {tool.name} ({tool.category})")

    def unregister(self, name: str):
        """注销工具。"""
        self._tools.pop(name, None)
        logger.info(f"注销工具: {name}")

    def get(self, name: str) -> Optional[Tool]:
        """获取工具。"""
        return self._tools.get(name)

    def list(self, category: Optional[str] = None) -> list[Tool]:
        """列出工具，可选按分类筛选。"""
        tools = list(self._tools.values())
        if category:
            tools = [t for t in tools if t.category == category]
        return tools

    def get_descriptions(self) -> str:
        """生成 LLM system prompt 用的工具描述文本。"""
        lines = []
        for tool in self._tools.values():
            params_desc = ""
            if tool.parameters:
                props = tool.parameters.get("properties", {})
                required = tool.parameters.get("required", [])
                param_lines = []
                for name, schema in props.items():
                    req = "（必填）" if name in required else "（可选）"
                    param_lines.append(f"      {name}: {schema.get('description', '')} {req}")
                if param_lines:
                    params_desc = "\n" + "\n".join(param_lines)

            lines.append(f"- {tool.icon} `{tool.name}`: {tool.description}{params_desc}")

        return "\n".join(lines)

    @property
    def count(self) -> int:
        return len(self._tools)


# 全局实例
tool_registry = ToolRegistry()
