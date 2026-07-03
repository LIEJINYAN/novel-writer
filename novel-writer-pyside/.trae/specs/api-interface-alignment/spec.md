# 服务接口对齐 Spec

## Why

`005_API接口设计.md` 定义了服务层接口合同（77+ 个接口），但实际代码存在多处偏离：AIService 缺少 QObject 信号和七步方法、EditorService 和 ProjectService 信号不全、PluginService 缺失、TrackingService 分散为 5 个独立服务。

## What Changes

1. AIService 改为继承 QObject，新增 `ai_started`/`ai_finished`/`ai_error`/`ai_stream_chunk`/`ai_progress` 信号
2. AIService 新增七步方法：`create_constitution()`/`create_specification()`/`create_plan()`/`generate_tasks()`/`clarify_decisions()`（委托 prompt_templates 模板）
3. EditorService 补充缺失的信号
4. ProjectService 改为 QObject，补充信号
5. 创建 `services/plugin_service.py` 作为 PluginManager 的 Qt 包装层
6. 文档中的统一 `TrackingService` 保持实际为 5 个独立服务，更新 signal_bus 信号覆盖

## Impact
- Affected specs: `005_API接口设计.md` 第 2-10 节
- Affected code: `services/ai_service.py`、`services/editor_service.py`、`services/project_service.py`、`services/plugin_service.py`（新建）、`utils/signal_bus.py`

## ADDED Requirements

### Requirement: AIService QObject + 信号
系统 SHALL 使 AIService 继承 QObject 并发射文档定义的 AI 信号。

#### Scenario: AI 操作信号
- **WHEN** AI 续写开始
- **THEN** `ai_started.emit("continue_writing")`
- **WHEN** AI 续写完成
- **THEN** `ai_finished.emit("continue_writing")`
- **WHEN** AI 调用出错
- **THEN** `ai_error.emit(error_type, message)`

### Requirement: AIService 七步方法
系统 SHALL 在 AIService 上提供 5 个新方法：`create_constitution()`、`create_specification()`、`clarify_decisions()`、`create_plan()`、`generate_tasks()`，内部委托给 prompt_templates 的对应模板。

#### Scenario: 创作宪法调用
- **WHEN** `create_constitution(genre, target_audience, tone)` 被调用
- **THEN** 返回 AIWorker 实例，使用 constitution 模板构建消息

### Requirement: PluginService 插件服务
系统 SHALL 创建 `services/plugin_service.py` 作为 PluginManager 的 Qt 包装层。

#### Scenario: 插件管理
- **WHEN** UI 层需要列出插件
- **THEN** 通过 `PluginService.list_plugins()` 调用

## MODIFIED Requirements
### Requirement: EditorService 信号
补充 `content_changed`、`word_count_changed`、`chapter_opened`、`chapter_closed` 信号。

### Requirement: ProjectService 信号
改为 QObject，新增 `project_created`、`project_opened`、`project_closed`、`project_deleted`、`project_updated` 信号。

## REMOVED Requirements
无
