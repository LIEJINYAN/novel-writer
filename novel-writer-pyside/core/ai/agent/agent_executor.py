"""Agent 执行器 - 自然语言到工具调用的核心引擎。"""

import re
import json
import logging
from dataclasses import dataclass, field
from typing import Generator, Optional

from core.ai.agent.tool_registry import tool_registry

logger = logging.getLogger(__name__)


@dataclass
class AgentEvent:
    """Agent 执行过程中的事件。"""
    event_type: str  # thinking | tool_call | tool_result | text | error | done
    data: any = None


# Agent system prompt 模板
AGENT_SYSTEM_PROMPT = """你是小说写作助手。你可以使用以下工具来帮助用户完成创作任务：

{tool_descriptions}

## 使用规则
1. 当用户要求执行具体操作时，调用对应的工具
2. 工具调用格式：tool_name(param1="value1", param2="value2")
3. 一个回复中可以调用多个工具
4. 调用工具后，根据工具结果显示最终回复
5. 如果用户只是聊天讨论，直接回复即可，不需要调用工具
6. 如果用户没有明确指定参数，根据上下文合理推断"""


class AgentExecutor:
    """Agent 执行器。"""

    def __init__(self, provider, config):
        self._provider = provider
        self._config = config
        # 确保工具已注册
        from core.ai.agent.tools import register_all
        register_all()

    def execute(self, user_input: str, history: Optional[list] = None,
                tool_categories: Optional[list[str]] = None) -> Generator[AgentEvent, None, None]:
        """执行用户输入。

        Args:
            user_input: 用户自然语言输入
            history: 可选的对话历史（Message 对象列表）
            tool_categories: 可用的工具分类列表，如 ["read"]。None=全部工具
        Yields:
            AgentEvent 事件
        """
        from core.ai.base import Message

        yield AgentEvent("thinking", {"input": user_input})

        # 筛选工具描述
        if tool_categories:
            tool_lines = []
            for cat in tool_categories:
                tools = tool_registry.list(category=cat)
                for t in tools:
                    params_desc = ""
                    if t.parameters:
                        props = t.parameters.get("properties", {})
                        required = t.parameters.get("required", [])
                        param_lines = []
                        for name, schema in props.items():
                            req = "（必填）" if name in required else "（可选）"
                            param_lines.append(f"      {name}: {schema.get('description', '')} {req}")
                        if param_lines:
                            params_desc = "\n" + "\n".join(param_lines)
                    tool_lines.append(f"- {t.icon} `{t.name}`: {t.description}{params_desc}")
            tool_desc = "\n".join(tool_lines)
        else:
            tool_desc = tool_registry.get_descriptions()

        # 1. 构造消息列表
        messages = [Message(role="system", content=AGENT_SYSTEM_PROMPT.format(
            tool_descriptions=tool_desc
        ))]

        # 添加历史消息
        if history:
            messages.extend(history)

        # 添加当前用户输入
        messages.append(Message(role="user", content=user_input))

        # 2. 调用 LLM 获取回复
        full_response = ""
        try:
            for chunk in self._provider.chat_stream(messages, self._config):
                full_response += chunk
                yield AgentEvent("text", chunk)
        except Exception as e:
            yield AgentEvent("error", str(e))
            yield AgentEvent("done", None)
            return

        # 3. 解析工具调用
        tool_calls = self._parse_tool_calls(full_response)

        if not tool_calls:
            # 没有工具调用，纯文本回复
            yield AgentEvent("done", None)
            return

        # 4. 执行每个工具调用
        for tool_name, params in tool_calls:
            yield AgentEvent("tool_call", {"name": tool_name, "params": params})

            tool = tool_registry.get(tool_name)
            if not tool:
                result = {"success": False, "message": f"未知工具: {tool_name}", "data": None}
            else:
                try:
                    result = tool.handler(**params)
                except Exception as e:
                    result = {"success": False, "message": str(e), "data": None}

            yield AgentEvent("tool_result", {
                "name": tool_name,
                "success": result.get("success", False),
                "message": result.get("message", ""),
                "data": result.get("data"),
            })

            # 将工具结果加入消息供后续 LLM 调用
            result_text = json.dumps(result, ensure_ascii=False)
            messages.append(Message(role="user", content=f"工具 {tool_name} 返回结果：\n{result_text}"))

        # 5. 如果有工具调用，让 LLM 根据结果生成最终回复
        if tool_calls:
            yield AgentEvent("thinking", {"phase": "summary"})
            try:
                for chunk in self._provider.chat_stream(messages, self._config):
                    yield AgentEvent("text", chunk)
            except Exception as e:
                yield AgentEvent("error", str(e))

        yield AgentEvent("done", None)

    def _parse_tool_calls(self, text: str) -> list[tuple[str, dict]]:
        """从 LLM 回复文本中解析工具调用。

        格式: tool_name(param1="value1", param2=123)
        """
        results = []
        # 匹配 tool_name(key="value", key=number) 格式
        pattern = r'(\w+)\s*\(([^)]*)\)'
        for match in re.finditer(pattern, text):
            tool_name = match.group(1)
            params_str = match.group(2)

            # 检查是否是已注册的工具
            if not tool_registry.get(tool_name):
                continue

            # 解析参数
            params = {}
            # 匹配 key="value" | key=123 | key=3.14 | key=true | key=value
            param_pattern = r'(\w+)\s*=\s*"([^"]*)"|(\w+)\s*=\s*(\d+\.?\d*)|(\w+)\s*=\s*(true|false)|(\w+)\s*=\s*(\w+)'
            for pm in re.finditer(param_pattern, params_str):
                if pm.group(1) and pm.group(2):
                    key, val = pm.group(1), pm.group(2)
                elif pm.group(3) and pm.group(4):
                    key = pm.group(3)
                    raw = pm.group(4)
                    val = float(raw) if "." in raw else int(raw)
                elif pm.group(5) and pm.group(6):
                    key = pm.group(5)
                    val = pm.group(6).lower() == "true"
                else:
                    key, val = pm.group(7), pm.group(8)
                params[key] = val

            results.append((tool_name, params))

        return results
