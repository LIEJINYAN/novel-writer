# Tasks

## [x] Task 1: 创建 EditorService
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建 `services/editor_service.py`
  - 从 `ui/main_window.py` 提取：自动保存逻辑、撤销栈深度管理、编辑器打开/关闭追踪
  - 保留 `main_window` 的 UI 事件处理和信号连接
- **Acceptance**: 自动保存和撤销栈配置功能正常，`main_window` 不再直接操作保存定时器逻辑

## [x] Task 2: 创建 AIService
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建 `services/ai_service.py`，作为 `core/ai/` 的 Facade
  - 暴露方法：`continue_writing()`、`polish_text()`、`rewrite_text()`、`chat()`
  - UI 层通过此服务调用 AI，不直接引用 `core/ai/` 子模块
- **Acceptance**: AI 续写/润色/重写/对话功能通过 `AIService` 正常调用

## [x] Task 3: 迁移追踪系统至 core/tracking/
- **Priority**: medium
- **Depends On**: Task 1, Task 2
- **Description**: 
  - 创建 `core/tracking/plot_tracker.py`（从 `services/plot_service.py` 提取核心逻辑）
  - 创建 `core/tracking/character_tracker.py`（从 `services/character_service.py` 提取核心逻辑）
  - 创建 `core/tracking/relationship_tracker.py`（从 `services/relationship_service.py` 提取核心逻辑）
  - 创建 `core/tracking/timeline_manager.py`（从 `services/timeline_service.py` 提取核心逻辑）
  - 创建 `core/tracking/consistency_checker.py`（从 `services/consistency_service.py` 提取核心逻辑）
  - `services/` 层保留为薄包装层，将核心逻辑委托给 `core/tracking/` 中的类
- **Acceptance**: 所有追踪功能通过 `core/tracking/` 中的类可用，原 `services/` 接口保持不变

## [x] Task 4: 实现插件系统骨架
- **Priority**: low
- **Depends On**: None
- **Description**: 
  - 在 `core/plugins/` 中创建 `base.py`（`PluginBase` 抽象基类）
  - 在 `core/plugins/` 中创建 `manager.py`（`PluginManager`）
  - 支持 7 个扩展点：`ui_menu`、`ui_sidebar`、`ai_provider`、`writing_method`、`export_format`、`tracker`、`command`
  - 应用启动时 `main.py` 调用 `plugin_manager.discover_plugins()`
- **Acceptance**: `PluginBase` 和 `PluginManager` 导入正常，插件发现机制可用

# Task Dependencies
- [Task 3] depends on [Task 1], [Task 2] (避免同一批文件重复冲突)
