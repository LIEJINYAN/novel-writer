"""提示词模板基类。"""
from dataclasses import dataclass, field
from typing import List, Dict

from core.ai.base import AIConfig


@dataclass
class PromptTemplate:
    """提示词模板基类"""

    name: str  # 模板名称
    description: str  # 模板描述
    system_prompt: str = ""  # 系统提示词
    user_prompt_template: str = ""  # 用户提示词模板（支持变量）
    default_config: AIConfig = field(default_factory=AIConfig)

    def render(self, **kwargs) -> str:
        """渲染模板，替换 {variable_name} 变量"""
        result = self.user_prompt_template
        for key, value in kwargs.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result

    def build_messages(self, **kwargs) -> List[Dict[str, str]]:
        """构建消息列表，返回 [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]"""
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": self.render(**kwargs)})
        return messages
