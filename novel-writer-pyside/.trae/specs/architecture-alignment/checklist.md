# 架构对齐设计文档 - 检查清单

- [x] Task 1: `services/editor_service.py` 创建成功，自动保存/撤销栈逻辑从 main_window 提取
- [x] Task 1: 自动保存和撤销栈配置功能正常
- [x] Task 2: `services/ai_service.py` 创建成功，作为 `core/ai/` 的 Facade
- [x] Task 2: AI 续写/润色/重写/对话通过 AIService 调用正常
- [x] Task 3: `core/tracking/` 包含 5 个追踪类文件
- [x] Task 3: 原 `services/` 接口不变（向后兼容）
- [x] Task 4: `core/plugins/base.py` 和 `core/plugins/manager.py` 创建成功
- [x] Task 4: 插件发现机制在应用启动时触发
- [x] 应用启动正常，无导入错误
