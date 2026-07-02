# Phase 3 遗漏项补全 - 验证检查清单

## 第一批：写作模板补充 + 重试机制

### 第二批写作模板
- [x] Checkpoint 1.1: `ConstitutionTemplate` 注册为 `constitution`，含 `{{ genre }}` `{{ protagonist }}` `{{ keywords }}` 变量
- [x] Checkpoint 1.2: `SpecifyTemplate` 注册为 `specify`，含 `{{ chapter_num }}` `{{ summary }}` `{{ method_name }}` 变量
- [x] Checkpoint 1.3: `WorldExpandTemplate` 注册为 `world_expand`，含 `{{ existing_setting }}` `{{ aspect }}` 变量
- [x] Checkpoint 1.4: `DialogueGenTemplate` 注册为 `dialogue_gen`，含 `{{ character_a }}` `{{ character_b }}` `{{ setting }}` `{{ mood }}` 变量
- [x] Checkpoint 1.5: `TitleGenTemplate` 注册为 `title_gen`，含 `{{ content }}` `{{ style }}` 变量
- [x] Checkpoint 1.6: 5 个模板注册到 PROMPT_REGISTRY，`list_templates()` 返回 16 个

### 指数退避重试
- [x] Checkpoint 2.1: `retry_with_backoff()` 装饰器接受 max_retries/base_delay/max_delay 参数
- [x] Checkpoint 2.2: 可重试错误（AIConnectionError, AIRateLimitError）触发重试
- [x] Checkpoint 2.3: 不可重试错误（AIAuthenticationError, AIModelNotFoundError）不触发重试
- [x] Checkpoint 2.4: 重试间隔按指数退避计算（base * 2^attempt）
- [x] Checkpoint 2.5: `AIWorker` 集成了重试机制，`run()` 方法包裹重试
- [x] Checkpoint 2.6: 重试时发射 `retry_signal(attempt, max_retries)` 信号
- [x] Checkpoint 2.7: AI 面板状态栏显示重试状态

---

## 第二批：方法转换 + AI 对话服务

### 方法转换器
- [x] Checkpoint 3.1: `MethodConverter.convert_chapters()` 正确映射章节到目标方法阶段
- [x] Checkpoint 3.2: 三幕式 → 英雄之旅的 20 章映射结果正确
- [x] Checkpoint 3.3: `suggest_reassignment()` 返回可读的迁移建议
- [x] Checkpoint 3.4: `get_conversion_summary()` 生成转换摘要
- [x] Checkpoint 3.5: 大纲面板有"转换方法"按钮
- [x] Checkpoint 3.6: 点击按钮弹出转换预览对话框

### AI 对话服务
- [x] Checkpoint 4.1: `ChatService.create_session()` 返回非空 session_id
- [x] Checkpoint 4.2: `ChatService.send_message()` 返回流式 Generator
- [x] Checkpoint 4.3: 多次发送消息后历史保留正确
- [x] Checkpoint 4.4: 历史超过 `max_history` 时自动裁剪
- [x] Checkpoint 4.5: `get_history()` 返回完整会话历史
- [x] Checkpoint 4.6: `clear_history()` 清空会话历史
- [x] Checkpoint 4.7: `delete_session()` 删除会话
- [x] Checkpoint 4.8: `AIChatPanel` 使用 `ChatService` 而非直接 `AIWorker`
- [x] Checkpoint 4.9: AI 对话面板有"新建会话"按钮
