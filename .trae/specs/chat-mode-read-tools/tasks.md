# Chat 模式增加读取能力 - 实现计划

### [x] Task 1: AgentExecutor 增加 tool_categories 筛选

- **Priority**: high
- **Depends On**: None
- **Description**:
  修改 `core/ai/agent/agent_executor.py`：
  - `execute()` 增加 `tool_categories: list[str] | None = None` 参数
- **Verification**: 筛选分类工具生效

### [x] Task 2: Chat 模式改用 AgentExecutor（read 工具）

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  修改 `ui/sidebar/ai_panel.py`：
  - `_send_chat()` 使用 AgentExecutor 并传入 `tool_categories=["read"]`
  - 移除对 `chat_service` 的直接依赖
- **Verification**: Chat 模式可调用 read 工具
