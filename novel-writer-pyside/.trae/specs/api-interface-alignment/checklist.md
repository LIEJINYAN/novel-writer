# 服务接口对齐 - 检查清单

- [x] Task 1: `AIService` 继承 `QObject`，包含 5 个 AI 信号
- [x] Task 2: `AIService` 包含 `create_constitution`/`create_specification`/`clarify_decisions`/`create_plan`/`generate_tasks` 5 个方法
- [x] Task 2: 七步方法内部使用 `prompt_templates` 模板
- [x] Task 3: `EditorService` 包含 `content_changed`/`word_count_changed`/`chapter_opened`/`chapter_closed` 4 个信号
- [x] Task 4: `ProjectService` 继承 `QObject`，包含 5 个项目信号
- [x] Task 5: `services/plugin_service.py` 包含 `PluginService` + 全局实例
- [x] Task 5: `PluginService` 包含 4 个信号和 7 个方法
- [x] 应用启动正常，无导入错误
