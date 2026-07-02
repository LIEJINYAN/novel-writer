# AI 面板双模式架构（Chat / Agent）— 实现计划

## 第一批：基础设施（高优先级）

### [x] Task 1: 工具注册中心

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `core/ai/agent/__init__.py`
  - 创建 `core/ai/agent/tool_registry.py`
  - `Tool` 数据类 + `ToolRegistry` 类 + 全局 `tool_registry`
- **Verification**: 注册/获取/描述/注销 全部通过

### [x] Task 2: 基础工具实现（5 个）

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `core/ai/agent/tools/` 包
  - 5 个工具：read_chapter, continue_write, polish_text, rewrite_text, analyze_chapter
  - 每个工具有完整 definition 和 handler
  - `register_all()` 批量注册
- **Verification**: 5 个工具全部注册到 tool_registry

### [x] Task 3: Agent 执行器

- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 创建 `core/ai/agent/agent_executor.py`
  - `AgentEvent` 事件类型 + `AgentExecutor` 类 + `AGENT_SYSTEM_PROMPT`
  - `execute()` yield 事件流（thinking/tool_call/tool_result/text/error/done）
  - `_parse_tool_calls()` 正则解析 LLM 输出
- **Verification**: 自然语言可触发工具调用，纯聊天不触发

---

## 第二批：UI 改造（高优先级）

### [x] Task 4: AI 面板双模式 UI

- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 重写 `ui/sidebar/ai_panel.py`
  - Chat/Agent 模式切换（QRadioButton）
  - Chat 模式使用 chat_service
  - Agent 模式使用 AgentExecutor
  - 工具卡片可视化
  - 所有信号接口保持不变
- **Verification**: 编译通过，main_window.py 无需修改

### [x] Task 5: Agent 模式自然语言到工具调用

- **Priority**: medium
- **Depends On**: Task 3, Task 4
- **Description**: 与 Task 3 合并实现

### [x] Task 6: QSS 主题适配

- **Priority**: low
- **Depends On**: Task 4
- **Description**:
  - 更新 dark.qss 和 light.qss
  - 模式切换按钮样式、工具卡片样式、状态指示器样式
- **Verification**: 6 个样式断言全部通过

# Task Dependencies
- Task 1（工具注册中心）→ Task 2（工具实现）
- Task 2 → Task 3（Agent 执行器）
- Task 3 → Task 4（AI 面板 UI）
- Task 3, Task 4 → Task 5（意图识别）
- Task 4 → Task 6（QSS 主题）
