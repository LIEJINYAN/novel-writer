# Chat 模式增加读取能力

## Why

Chat 模式只有纯文字对话，AI 无法读取章节内容、项目设定，用户讨论情节时需要手动粘贴。只需给 Chat 模式开放 read 类工具即可解决。

## Changes

| 文件 | 改动 |
|------|------|
| `core/ai/agent/agent_executor.py` | `execute()` 增加 `tool_categories` 参数，筛选工具描述 |
| `ui/sidebar/ai_panel.py` | Chat 模式也走 AgentExecutor，但只传 `tool_categories=["read"]` |

## 行为变化

| 模式 | 可用工具 | 用户说"帮我看看第三章" |
|------|---------|----------------------|
| Chat | read 类（read_chapter, analyze_chapter） | ✅ 读取并讨论 |
| Agent | read + edit 类 + 全部工具 | ✅ 读取 + 可执行续写/润色 |

## Requirements

### FR-1: AgentExecutor 支持工具筛选
- `execute(user_input, history, tool_categories=None)` 新增参数
- `tool_categories=None` 时使用全部工具（现有行为）
- `tool_categories=["read"]` 时只描述 read 类工具
- `tool_categories=["edit"]` 时只描述 edit 类工具

### FR-2: Chat 模式使用 AgentExecutor
- Chat 模式初始化时创建 AgentExecutor，传入 `tool_categories=["read"]`
- 用户消息走 AgentExecutor execute()
- AgentEvent 处理方式与 Agent 模式相同
- Chat 模式执行的工具结果只展示在消息区，不写入编辑器

## Out of Scope
- 联网搜索工具（search_web）暂未实现，后续添加
- 预览工具（preview）暂未实现
