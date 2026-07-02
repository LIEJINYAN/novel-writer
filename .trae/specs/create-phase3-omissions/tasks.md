# Phase 3 遗漏项补全 - 实现计划

## 第一批：写作模板补充 + 重试机制（高优先级）

### [x] Task 1: 第二批写作模板（5 个）

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `core/ai/prompts/write_templates_v2.py`
  - 5 个模板：
    1. **ConstitutionTemplate** (`constitution`) — 设定生成
    2. **SpecifyTemplate** (`specify`) — 细纲生成
    3. **WorldExpandTemplate** (`world_expand`) — 世界观扩展
    4. **DialogueGenTemplate** (`dialogue_gen`) — 对话生成
    5. **TitleGenTemplate** (`title_gen`) — 标题生成
  - 注册到 PROMPT_REGISTRY，共 16 个模板
- **Acceptance Criteria**: AC-1

### [x] Task 2: 指数退避重试机制

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `core/ai/retry_middleware.py` — 装饰器 + RetrySignalEmitter
  - 修改 `core/ai/ai_worker.py` — run() 集成重试 + retry_signal 信号
  - 修改 `ui/main_window.py` — 连接 retry_signal 显示重试状态
  - 可重试/不可重试错误分类
- **Acceptance Criteria**: AC-2

---

## 第二批：方法转换 + AI 对话服务（中优先级）

### [x] Task 3: 方法转换器

- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 创建 `core/ai/writing_methods/method_converter.py` — convert_chapters / suggest_reassignment / get_conversion_summary
  - 修改 `ui/sidebar/outline_panel.py` — 添加"转换"按钮 + 转换对话框
- **Acceptance Criteria**: AC-3

### [x] Task 4: AI 对话服务

- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - 创建 `core/ai/chat_service.py` — 会话管理 + 历史管理 + 消息发送
  - 修改 `ui/sidebar/ai_chat_panel.py` — 使用 ChatService 替代 AIWorker + 新建会话按钮
- **Acceptance Criteria**: AC-4

# Task Dependencies
- Task 1（写作模板）：无依赖
- Task 2（重试机制）：无依赖，与 Task 1 可并行
- Task 3（方法转换）：无依赖，与 Task 1/2 可并行
- Task 4（对话服务）：依赖 Task 2（使用带重试的 AIWorker）
