# AI 提示词系统剩余项对齐 Spec

## Why

`004_AI提示词系统设计.md` 有 3 个模块在上一轮对齐中未覆盖：ContextBuilder 上下文构建器缺少 `build_writing_context()` 方法，错误处理用字符串匹配而非文档的异常层级，AI 内容审计服务完全缺失。

## What Changes

1. **ContextBuilder** `core/ai/context/context_builder.py` — 新增 `build_writing_context()` 方法，按文档 11 级优先级加载上下文
2. **error_handler.py** `core/ai/error_handler.py` — 新建，包含 `AIError`/`RateLimitError`/`AuthError`/`ModelNotAvailableError`/`ContextTooLongError` 异常类 + `with_retry` 装饰器
3. **audit_service.py** `core/ai/audit_service.py` — 新建，包含 `AIAuditService` 类（高频词检测、段落长度检查、单句成段比例）

## Impact
- Affected specs: `004_AI提示词系统设计.md` 第 4.1、7、8.2 节
- Affected code: `core/ai/context/context_builder.py`、`core/ai/error_handler.py`（新建）、`core/ai/audit_service.py`（新建）

## ADDED Requirements

### Requirement: ContextBuilder.build_writing_context
系统 SHALL 在 `ContextBuilder` 中提供 `build_writing_context()` 方法，按文档 4.1 节和 4.2 节优先级构建上下文。

#### Scenario: 构建完整写作上下文
- **WHEN** `build_writing_context(chapter_id, project_id)` 被调用
- **THEN** 返回包含 constitution/specification/creative_plan/tasks/character_state/relationships/plot_tracker/previous_summary 的 dict
- **AND** 前 3 章额外包含 golden_opening
- **AND** 超过 max_context_tokens 时自动裁剪

### Requirement: Error Handler 异常层级
系统 SHALL 在 `core/ai/error_handler.py` 中提供文档定义的异常类和重试机制。

#### Scenario: 异常类定义
- **WHEN** 调用 `AIError` / `RateLimitError` / `AuthError` / `ModelNotAvailableError` / `ContextTooLongError`
- **THEN** 各异常正确继承且可用

#### Scenario: with_retry 重试
- **WHEN** 被装饰的异步函数抛出 `RateLimitError`
- **THEN** 指数退避重试（base_delay=1.0, max_delay=60.0, max_retries=3）

### Requirement: AIAuditService
系统 SHALL 在 `core/ai/audit_service.py` 中提供 `AIAuditService` 类。

#### Scenario: AI 内容审计
- **WHEN** `audit_text(text)` 被调用
- **THEN** 返回含 `total_issues`、`issues` 列表、`ai_score` 的 dict
- **AND** 检测 AI 高频词（BANNED_WORDS）、段落长度超 150 字、单句成段比例低于 30%

## MODIFIED Requirements
- 保留现有 `AIProviderError` 层级（AIConnectionError 等）作为底层 Provider 异常，新增的 `AIError` 层作为上层服务异常

## REMOVED Requirements
无
