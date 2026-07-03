# Tasks

## [x] Task 1: 填充 `core/writing/` 写作引擎
- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 创建 `core/writing/engine.py`：`WritingEngine` 类，包含章节/分卷 CRUD 核心逻辑
  - 从 `services/chapter_service.py` 提取：`create_volume`、`create_chapter`、`delete_chapter`、`rename_chapter`、`reorder_chapter` 等核心数据库操作
  - `services/chapter_service.py` 保留为薄包装层，委托给 `WritingEngine`
  - `core/writing/__init__.py` 导出 `WritingEngine`
- **Acceptance**: `WritingEngine` 类创建成功，章节/分卷管理功能正常

## [x] Task 2: 增强 `core/project/` 项目管理
- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 增强 `core/project/manager.py` 中的 `ProjectManager` 类
  - 从 `services/project_service.py` 提取：`create_project`、`open_project`、`delete_project`、`get_project` 等核心逻辑
  - `services/project_service.py` 保留为薄包装层，委托给 `ProjectManager`
  - `core/project/__init__.py` 导出 `ProjectManager`
- **Acceptance**: `ProjectManager` 包含项目 CRUD 核心逻辑，项目服务功能正常

## [x] Task 3: 配置管理对齐
- **Priority**: low
- **Depends On**: None
- **Description**:
  - 扩展 `app/config.py` 中的 `AppConfig` 类
  - 增加 `load()` 类方法：从 `config.json` 加载配置
  - 增加 `save()` 方法：持久化到 `config.json`
  - 增加 `update(**kwargs)` 方法：批量更新配置
  - 配置文件位置按平台区分（Windows: `%APPDATA%/NovelWriter/config.json`）
  - 保持与现有 `app_config_service`（DB 键值对）和 QSettings 的兼容
- **Acceptance**: `AppConfig.load()`、`save()`、`update()` 可用，配置可持久化

## [x] Task 4: `core/methods/` 路径对齐
- **Priority**: low
- **Depends On**: None
- **Description**:
  - 将 `core/ai/writing_methods/` 中的实现文件迁移至 `core/methods/`：
    - `base.py` → `base.py`（WritingMethod ABC）
    - `three_act.py`、`hero_journey.py`、`seven_point.py` → 对应文件
    - `advisor.py` → `advisor.py`（MethodAdvisor）
    - `method_converter.py` → `converter.py`
  - 在 `core/ai/writing_methods/` 中保留 stub 文件，`from core.methods import *` 实现向后兼容
  - 更新 `ui/sidebar/outline_panel.py` 和 `ui/dialogs/creation_wizard.py` 的导入路径
- **Acceptance**: 6 种写作方法可通过 `core.methods` 导入，旧导入路径保持兼容

# Task Dependencies
- 所有任务彼此独立，可并行执行
