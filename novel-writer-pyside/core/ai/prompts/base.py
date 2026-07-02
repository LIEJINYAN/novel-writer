"""提示词模板基类。"""
from abc import ABC, abstractmethod
from typing import Any

from jinja2 import Template


class PromptTemplate(ABC):
    """提示词模板基类，所有模板必须实现 render 方法。"""

    @abstractmethod
    def render(self, context: dict[str, Any]) -> list:
        """渲染模板，返回 Message 列表。

        Args:
            context: 模板变量字典

        Returns:
            list: 消息列表（通常包含 system 和 user 消息）。
            当前返回 dict 列表 ``[{"role": "system", "content": "..."}]``，
            待 ``core/ai/base.py`` 的 Message 类创建后可平滑适配。
        """
        pass

    def _render_template(self, template_str: str, context: dict) -> str:
        """使用 Jinja2 渲染模板字符串。"""
        template = Template(template_str)
        return template.render(**context)
