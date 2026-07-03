# 架构对齐 Phase 2 - 检查清单

- [x] Task 1: `core/writing/engine.py` 创建成功，章节管理核心逻辑提取
- [x] Task 1: `services/chapter_service.py` 改为委托调用，接口不变
- [x] Task 2: `core/project/manager.py` 增强，包含项目 CRUD 核心逻辑
- [x] Task 2: `services/project_service.py` 改为委托调用，接口不变
- [x] Task 3: `app/config.py` 的 `AppConfig` 包含 `load/save/update` 方法
- [x] Task 3: 配置文件 `config.json` 可正常读写
- [x] Task 4: 6 个方法类从 `core/ai/writing_methods/` 移至 `core/methods/`
- [x] Task 4: 旧导入路径向后兼容（stub 文件）
- [x] 应用启动正常，无导入错误
