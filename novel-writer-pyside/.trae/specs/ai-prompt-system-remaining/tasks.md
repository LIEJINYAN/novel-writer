# Tasks

## [x] Task 1: 扩展 ContextBuilder.build_writing_context
- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 在 `core/ai/context/context_builder.py` 中新增 `build_writing_context(chapter_id, project_id, include_tracking=True, include_knowledge=True, max_context_tokens=8000)` 方法
  - 按文档 4.2 节 11 级优先级加载上下文
  - 保留现有方法不变
- **Acceptance**: `build_writing_context(1, 1)` 返回完整 11 级上下文字典

## [x] Task 2: 创建 core/ai/error_handler.py
- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 新建 `core/ai/error_handler.py`，包含 5 个异常类和 `with_retry` 装饰器
  - 与现有 `AIProviderError` 层级独立共存
- **Acceptance**: 5 个异常类 + `with_retry` 导入正常，基类不受影响

## [x] Task 3: 创建 core/ai/audit_service.py
- **Priority**: low
- **Depends On**: None
- **Description**:
  - 新建 `core/ai/audit_service.py`，包含 `AIAuditService` 类 + 全局实例
  - 高频词检测、段落长度、单句成段比例三项审计
- **Acceptance**: `audit_text("弥漫着...")` 返回 `total_issues > 0`

# Task Dependencies
- 所有任务独立，可并行执行
