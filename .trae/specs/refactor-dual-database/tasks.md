# 双层数据库架构重构 - 实现计划

**注意**：这是一个横跨数据层、服务层、UI 层的大型重构，建议分批实施。

## [ ] Task 1: DatabaseManager 双引擎改造

- **Priority**: high
- **Depends On**: None
- **Description**:
  - `models/database.py`：
    - 拆为 `AppBase(DeclarativeBase)` 和 `ProjectBase(DeclarativeBase)`
    - `DatabaseManager` 持有 `_app_engine`（应用级）+ `_project_engine`（项目级，可 None）
    - `init_app_db(db_path)` — 创建应用引擎 + 创建 AppBase 所有表
    - `init_project_db(db_path)` — 创建项目引擎 + 创建 ProjectBase 所有表
    - `get_app_session()` → app session
    - `get_project_session()` → project session（需先 init_project_db）
    - `open_project(db_path)` → 先 close_project() + init_project_db()
    - `close_project()` → dispose project engine
    - `get_session()` 保留兼容别名 → 调用 get_app_session()
  - 保持所有 PRAGMA 设置不变
- **Verification**: 双引擎各自 create_all 表不冲突，get_app_session() / get_project_session() 返回正确 session

## [ ] Task 2: 应用级数据模型

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 将 `models/project.py` 精简为应用级 `Project` 元数据：
    - 字段：id, name(NOT NULL), path(UNIQUE NOT NULL), description, genre, writing_method, total_words, chapter_count, status, cover_image, created_at, updated_at, last_opened_at
    - 移除 `target_words`（设计文档无此字段）
  - 新建 `models/app/app_config.py` — app_config 表（设计文档 3.1 节）
  - 新建 `models/app/ai_provider.py` — ai_providers 表（设计文档 3.3 节）
    - 实际已有此表，更新字段匹配设计文档
  - 新建 `models/app/ai_conversation.py` — ai_conversations 表（设计文档 3.4 节）
  - 新建 `models/app/plugin.py` — plugins 表（设计文档 3.5 节）
  - 新建 `models/app/__init__.py` — 导出所有 app 模型
  - 更新 `models/__init__.py` — 导出 AppBase + 应用模型
- **Verification**: AppBase.metadata.create_all 创建 5 张表

## [ ] Task 3: 项目级数据模型

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 新建 `models/project/` 目录，全部使用 `ProjectBase`，**移除所有 project_id 字段**（项目 DB 中不需要）
  - `project_info.py` — 字段完全按设计文档 4.1 节：id, name, type, description, genre, target_audience, tone, themes(JSON), estimated_length, writing_method, hybrid_scheme(JSON), language, status, config_version, created_at, updated_at
  - `volume.py` — 从现有 `models/chapter.py` 中的 Volume 迁移，移除 project_id
  - `chapter.py` — 从现有迁移，移除 project_id，字段补全（subtitle, content_plain, char_count, paragraph_count, plot_stage, completed_at）
  - `character.py` — 从现有迁移，移除 project_id，字段补全（aliases→JSON, skills→JSON, possessions→JSON, secrets→JSON）
  - `character_state.py` — 新表（设计文档 4.5 节）
  - `character_appearance.py` — 从现有迁移，移除 project_id
  - `plot_node.py` — 从现有迁移，移除 project_id（需要兼容当前 plot_arcs 表，可能合并为 plot_nodes 带 plot_type）
  - `foreshadowing.py` — 新表（设计文档 4.8 节），实际当前是 plot_foreshadows，按文档重命名+补字段
  - `conflict.py` — 新表（设计文档 4.9 节）
  - `relationship.py` — 从现有迁移，移除 project_id，补全字段
  - `faction.py` — 从现有迁移，移除 project_id，补全字段
  - `faction_member.py` — 从现有迁移，移除 project_id
  - `relationship_history.py` — 从现有迁移，移除 project_id
  - `timeline_event.py` — 从现有迁移，移除 project_id，补全字段（duration, participants, related_plot_node_id）
  - `validation_rule.py` — 新表（设计文档 4.15 节）
  - `world_setting.py` — 从现有迁移，移除 project_id，补全字段
  - `writing_method_config.py` — 新表（设计文档 2.2 节提及）
  - `writing_statistic.py` — 新表（设计文档 4.17 节）
  - 新建 `models/project/__init__.py` — 导出所有项目模型
  - 更新 `models/__init__.py` — 导出 ProjectBase + 项目模型
- **Verification**: ProjectBase.metadata.create_all 创建 19 张表

## [ ] Task 4: project_info 服务

- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 新建 `services/project_info_service.py`，`project_info_service` 单例
  - `get(project_id)` → 读取 project_info
  - `update(project_id, **data)` → 更新字段
  - 所有操作使用 `db_manager.get_project_session()`
- **Verification**: 在项目中读取/写入 project_info 正常

## [ ] Task 5: 服务层改造

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 逐个修改以下服务，将其内部 `db_manager.get_session()` 改为 `db_manager.get_project_session()`：
    - `services/chapter_service.py`
    - `services/character_service.py`
    - `services/plot_service.py`
    - `services/relationship_service.py`
    - `services/timeline_service.py`
    - `services/world_service.py`
    - `services/consistency_service.py`
    - `services/export_service.py`
    - `services/import_service.py`
  - `services/project_service.py` 拆分：
    - 列表/元数据操作 → `get_app_session()`
    - 项目信息 → 调用 `project_info_service`
  - 每个服务修改后，模型引用更新为 `models/project/` 下对应模型
- **Verification**: 每个服务的基础 CRUD 操作读写项目级 DB 正常

## [ ] Task 6: 主窗口集成

- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - `ui/main_window.py`：
    - 打开项目时：调用 `db_manager.open_project(project_db_path)`
    - 关闭项目时：调用 `db_manager.close_project()`
    - `signal_bus.project_opened` 保持现有接口
    - `_close_project` 中先 close_project 再清空面板
  - 处理首次迁移兼容：如果 `.novel/project.db` 不存在，先提示迁移
- **Verification**: 打开项目→项目级 DB 加载正常，关闭项目→引擎释放正常

## [ ] Task 7: 数据迁移脚本

- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 创建 `scripts/migrate_to_dual_db.py`：
    1. 连接现有 `novel_writer.db`
    2. 遍历所有 project_id
    3. 每个项目创建 `.novel/project.db`（ProjectBase.metadata.create_all）
    4. 写入 project_info（从现有 projects 表字段映射）
    5. 逐表 SELECT * WHERE project_id=? → INSERT INTO 项目 DB（移除 project_id）
    6. 更新应用级 projects 表：删除项目级字段
    7. 提示完成
- **Verification**: 迁移后新项目 DB 数据完整，应用级 DB 项目列表正常

# Task Dependencies
- Task 1 → Task 2, Task 3
- Task 2, Task 3 → Task 4
- Task 1 → Task 5
- Task 5, Task 4 → Task 6
- Task 3 → Task 7

# 并行执行建议
- Task 2（应用模型）和 Task 3（项目模型）可并行
- Task 4（project_info 服务）依赖 Task 3，Task 5（服务改造）依赖 Task 1，两者无相互依赖可并行
