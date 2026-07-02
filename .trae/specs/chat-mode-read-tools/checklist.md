# Chat 模式增加读取能力 - 检查清单

- [x] Checkpoint 1.1: `execute()` 接受 `tool_categories` 参数
- [x] Checkpoint 1.2: `tool_categories=["read"]` 时只描述 read 类工具
- [x] Checkpoint 1.3: `tool_categories=["edit"]` 时只描述 edit 类工具
- [x] Checkpoint 1.4: `tool_categories=None` 时描述全部工具（向后兼容）
- [x] Checkpoint 2.1: Chat 模式使用 AgentExecutor 而非 chat_service
- [x] Checkpoint 2.2: Chat 模式调用 "读取第三章" 成功读取并展示
- [x] Checkpoint 2.3: Chat 模式不可调用 edit 类工具
- [x] Checkpoint 2.4: Agent 模式仍可使用全部工具
