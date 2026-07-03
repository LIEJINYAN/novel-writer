# AI 提示词系统剩余项对齐 - 检查清单

- [x] Task 1: `ContextBuilder.build_writing_context()` 存在，返回包含 11 级上下文的 dict
- [x] Task 1: 前后文裁剪 `_trim_context()` 按优先级工作
- [x] Task 1: 前 3 章自动包含黄金开篇法则
- [x] Task 2: `core/ai/error_handler.py` 包含 5 个异常类（AIError/RateLimitError/AuthError/ModelNotAvailableError/ContextTooLongError）
- [x] Task 2: `with_retry` 异步装饰器可用，指数退避逻辑正确
- [x] Task 2: 现有 `AIProviderError` 层级不受影响
- [x] Task 3: `core/ai/audit_service.py` 包含 `AIAuditService` + 全局 `audit_service` 实例
- [x] Task 3: `audit_text()` 正确检测高频词、长段落、低单句成段比例
- [x] 应用启动正常，无导入错误
