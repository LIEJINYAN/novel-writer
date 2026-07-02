# Phase 3 遗漏项补全

## Why

Phase 3 核心功能已基本完成，但还有几处遗漏：写作模板不够完整（缺少设定生成、细纲生成等）、AI 调用没有错误重试机制、写作方法之间无法转换、AI 对话缺少独立的历史管理服务。这些虽不影响最小可用，但对完整开发体验是必要的补充。

## What Changes

- **新增 5 个写作模板**：constitution（设定生成）、specify（细纲生成）、world-expand（世界观扩展）、dialogue-gen（对话生成）、title-gen（标题生成）
- **新增重试机制**：指数退避重试装饰器/中间件，集成到 AIWorker
- **新增方法转换**：跨方法章节结构调整函数 + UI 入口
- **新增 AI 对话服务**：对话历史持久化、上下文管理、会话管理

## Impact

- 新文件：`core/ai/prompts/write_templates_v2.py`（第二批写作模板）
- 新文件：`core/ai/retry_middleware.py`（重试中间件）
- 新文件：`core/ai/writing_methods/method_converter.py`（方法转换器）
- 新文件：`core/ai/chat_service.py`（AI 对话服务）
- 修改 `core/ai/prompts/registry.py`：注册新模板
- 修改 `core/ai/ai_worker.py`：集成重试机制
- 修改 `ui/sidebar/outline_panel.py`：添加方法转换按钮
- 修改 `ui/sidebar/ai_chat_panel.py`：使用独立对话服务

## Requirements

### FR-1: 第二批写作模板
- ConstitutionTemplate：根据小说类型和主角生成完整的项目设定、世界观规则、力量体系
- SpecifyTemplate：根据章节序号和概要生成章节细纲（场景/冲突/关键对话）
- WorldExpandTemplate：针对现有设定扩展世界观细节（地理/政治/文化/经济）
- DialogueGenTemplate：根据角色性格和场景生成对话片段
- TitleGenTemplate：根据章节内容或项目设定生成吸引人的章节标题
- 所有模板注册到 PROMPT_REGISTRY，共 16 个模板

### FR-2: 指数退避重试
- `retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=30.0)` 装饰器
- 可配置重试次数和延迟策略
- 区分可重试错误（网络超时、速率限制）和不可重试错误（认证失败、模型不存在）
- 集成到 `AIWorker.run()` 中，对 API 调用包裹重试逻辑
- 在 AI 面板状态栏显示重试信息（"第 2/3 次重试..."）

### FR-3: 方法转换器
- `MethodConverter` 类：提供 `convert_chapters(chapters, from_method, to_method) -> dict` 方法
- 章节映射算法：将源方法的阶段比例映射到目标方法的阶段比例
- `suggest_reassignment(chapter, from_stage, to_stage) -> str`：为章节迁移提供建议
- 在 `ui/sidebar/outline_panel.py` 中添加"转换方法"按钮，弹出确认对话框

### FR-4: AI 对话服务
- `ChatService` 类管理对话会话
- `create_session() -> str` 创建新会话
- `send_message(session_id, content) -> Generator[str]` 发送消息并获取流式回复
- `get_history(session_id) -> list[Message]` 获取完整对话历史
- `clear_history(session_id)` 清空历史
- 会话上下文自动管理（裁剪、Token 计数），复用 `AIContextManager`
- 修改 `AIChatPanel` 使用 `ChatService` 而非直接调用 `AIWorker`

## Out of Scope
- Phase 4（角色/情节追踪系统）
- AI 对话历史持久化到数据库（仅内存缓存）
- 批量重写/批量转换

## Acceptance Criteria

### AC-1: 5 新模板
- 5 个模板均注册，`list_templates()` 返回 16 个模板
- 每个模板可正常渲染，输出格式正确

### AC-2: 重试机制
- 模拟网络超时错误，确认重试 3 次
- 模拟认证错误，确认不重试
- AI 面板显示重试状态

### AC-3: 方法转换
- 三幕式 → 英雄之旅的章节映射正确
- 转换后大纲结构可用
- 大纲面板有转换入口

### AC-4: 对话服务
- 创建会话后可连续对话
- 发送消息后返回流式回复
- 清空历史后会话重置
