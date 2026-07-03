# 双层数据库架构重构 Spec

## Why

当前是单库架构，所有数据在 `novel_writer.db`。设计文档规划的是**应用级 DB + 项目级 DB 双层架构**，每个项目在 `.novel/project.db` 中独立存储。回归此架构使项目迁移、备份、隔离更自然，也符合原版 Novel Writer 的项目目录结构。

## What Changes

- **BREAKING**: `DatabaseManager` 从单引擎改为双引擎（app + project）
- **BREAKING**: 所有项目级模型移到项目库，使用独立的 `ProjectBase`
- **BREAKING**: 所有项目级服务改用 `get_project_session()`
- **新增** `models/app/` 应用级模型：app_config, projects, ai_providers, ai_conversations, plugins（严格按设计文档 2.1 节）
- **新增** `models/project/` 项目级模型：project_info + 全部 16 张表（严格按设计文档 2.2 节 + 第 4 节）
- `projects` 表精简为元数据字段（设计文档 3.2 节）
- `project_info` 独立表（设计文档 4.1 节），字段完全按文档
- 提供迁移脚本，将现有单库数据拆分为 app + 各项目独立 db

## Impact

- **models/database.py** — `Base` → `AppBase` + `ProjectBase`，双引擎
- **models/project.py** — 拆为 `app/project.py`（精简为元数据）+ `project/project_info.py`（独立表）
- **所有服务** — 46 个方法需要改 session 获取方式
- **主窗口** — 打开/关闭项目时创建/销毁项目引擎
- **现有用户** — 提供一次性迁移，已有 `novel_writer.db` 中的数据拆分到各项目 db

## Requirements

### R-1: 应用级数据表（设计文档 2.1 / 3.x）

以下表在应用级 DB (novel_writer.db) 中，使用 `AppBase`：

**app_config**（3.1 节）：
- id, key(UNIQUE NOT NULL), value, created_at, updated_at

**projects**（3.2 节）：
- id, name(NOT NULL), path(UNIQUE NOT NULL), description, genre, writing_method, total_words, chapter_count, status, cover_image, created_at, updated_at, last_opened_at
- 索引：idx_projects_updated_at, idx_projects_status

**ai_providers**（3.3 节）：
- id, provider_name(UNIQUE NOT NULL), display_name(NOT NULL), api_key, api_base, default_model, is_enabled, is_default, config, created_at, updated_at
- 7 个提供商：openai / anthropic / google / deepseek / ollama / qwen / doubao

**ai_conversations**（3.4 节）：
- id, project_id, title, conversation_type, provider_name, model, messages(NOT NULL), total_tokens, created_at, updated_at
- 索引：idx_ai_conversations_project_id, idx_ai_conversations_updated_at

**plugins**（3.5 节）：
- id, plugin_name(UNIQUE NOT NULL), display_name(NOT NULL), version, description, author, path(NOT NULL), is_enabled, config, installed_at, updated_at

### R-2: 项目级数据表（设计文档 2.2 / 4.x）

以下表在项目级 DB (.novel/project.db) 中，使用 `ProjectBase`：

**project_info**（4.1 节）：
- id, name(NOT NULL), type('novel'), description, genre, target_audience, tone, themes(JSON 数组), estimated_length, writing_method('three-act'), hybrid_scheme(JSON), language('zh-CN'), status('active'), config_version('1.0.0'), created_at, updated_at

**volumes**（4.2 节）：
- id, volume_number(NOT NULL), title(NOT NULL), description, sort_order, is_complete(false), created_at, updated_at

**chapters**（4.3 节）：
- id, volume_id(FK), chapter_number(NOT NULL), title(NOT NULL), subtitle, content, content_plain, word_count, char_count, paragraph_count, summary, status('draft'), plot_stage, sort_order, is_deleted(false), created_at, updated_at, completed_at
- 外键：volume_id → volumes.id 级联删除
- 索引：idx_chapters_volume_id, idx_chapters_sort_order, idx_chapters_status, idx_chapters_is_deleted

**characters**（4.4 节）：
- id, name(NOT NULL), aliases(JSON), role, importance, gender, age, appearance, personality, background, motivation, skills(JSON), possessions(JSON), secrets(JSON), character_arc, avatar, sort_order, is_deleted(false), created_at, updated_at
- 索引：idx_characters_role, idx_characters_importance

**character_states**（4.5 节）：
- id, character_id(NOT NULL, FK→characters.id 级联删除), chapter_id(FK), is_alive(true), health_status, mental_state, location, position, current_phase, next_goal, status_snapshot(JSON), notes, created_at
- 索引：idx_character_states_character_id, idx_character_states_chapter_id

**character_appearances**（4.6 节）：
- id, character_id(NOT NULL, FK→characters.id 级联删除), chapter_id(NOT NULL, FK→chapters.id 级联删除), role_type, significance, scene_description, created_at
- UNIQUE(character_id, chapter_id)
- 索引：idx_character_appearances_character_id, idx_character_appearances_chapter_id

**plot_nodes**（4.7 节）：
- id, parent_id(FK→plot_nodes.id, 自引用), plot_type, name(NOT NULL), description, stage_key, status('pending'), start_chapter, end_chapter, sort_order, created_at, updated_at
- 索引：idx_plot_nodes_parent_id, idx_plot_nodes_plot_type, idx_plot_nodes_sort_order

**foreshadowings**（4.8 节）：
- id, content(NOT NULL), importance('medium'), planted_chapter_id(FK→chapters.id), planted_description, reveal_chapter_id(FK→chapters.id), reveal_description, status('active'), hints(JSON), related_characters(JSON), notes, created_at, updated_at
- 索引：idx_foreshadowings_status, idx_foreshadowings_importance

**conflicts**（4.9 节）：
- id, title(NOT NULL), description, conflict_type('person/person'), status('active'), parties_involved(JSON), start_chapter_id(FK→chapters.id), end_chapter_id(FK→chapters.id), resolution, escalation_level(1), sort_order, created_at, updated_at

**relationships**（4.10 节）：
- id, character_a_id(NOT NULL, FK→characters.id 级联删除), character_b_id(NOT NULL, FK→characters.id 级联删除), relationship_type('neutral'), description, initial_relation('陌生人'), current_relation('陌生人'), trajectory('stable'), intensity(5), key_events(JSON), notes, created_at, updated_at
- UNIQUE(character_a_id, character_b_id)

**factions**（4.11 节）：
- id, name(NOT NULL), description, leader_id(FK→characters.id SET NULL), goals(JSON), allied_with(JSON), opposed_to(JSON), status('active'), sort_order, created_at, updated_at

**faction_members**（4.12 节）：
- id, faction_id(NOT NULL, FK→factions.id 级联删除), character_id(NOT NULL, FK→characters.id 级联删除), role_in_faction, join_reason, joined_chapter_id(FK→chapters.id), is_core_member(false), sort_order, created_at
- UNIQUE(faction_id, character_id)

**relationship_history**（4.13 节）：
- id, relationship_id(NOT NULL, FK→relationships.id 级联删除), chapter_id(FK→chapters.id), change_type('change'), old_relation, new_relation, description, impact('medium'), created_at

**timeline_events**（4.14 节）：
- id, event_name(NOT NULL), description, story_date, chapter_id(FK→chapters.id), location, duration, participants(JSON), related_plot_node_id(FK→plot_nodes.id), importance('medium'), sort_order, created_at, updated_at
- 索引：idx_timeline_events_chapter_id, idx_timeline_events_sort_order

**validation_rules**（4.15 节）：
- id, rule_name(UNIQUE NOT NULL), category('character'), is_enabled(true), checks(JSON), config(JSON), severity('warning'), auto_fix_enabled(false), confidence_threshold(0.9), created_at, updated_at

**world_settings**（4.16 节）：
- id, setting_type('location'), name(NOT NULL), description, parent_id(FK→world_settings.id 自引用), importance('medium'), tags(JSON), related_characters(JSON), sort_order, created_at, updated_at

**writing_method_config**（设计文档 2.2 节，原文未详述）：
- id, project_id, method_name(NOT NULL), stage_config(JSON), scene_templates(JSON), created_at, updated_at

**writing_statistics**（4.17 节）：
- id, date(UNIQUE NOT NULL), words_written(0), words_deleted(0), net_words(0), time_spent(0), chapters_started(0), sessions(0), created_at, updated_at
- 索引：idx_writing_statistics_date

### R-3: 双层引擎

- `DatabaseManager` 维护两个引擎：`_app_engine` / `_project_engine`
- `init_app_db(db_path)` — 初始化应用级 DB，创建 AppBase 所有表
- `init_project_db(db_path)` — 初始化项目级 DB，创建 ProjectBase 所有表
- `get_app_session()` — 返回应用级 session
- `get_project_session()` — 返回当前打开项目的 session（需先调用 init_project_db）
- `close_project()` — dispose 项目引擎
- 两个引擎各自独立的 session_factory

### R-4: 服务层改造

- 所有操作项目数据的服务：
  - 方法签名不变，内部 `db_manager.get_session()` → `db_manager.get_project_session()`
  - 涉及：project_service, chapter_service, character_service, plot_service, relationship_service, timeline_service, world_service, consistency_service, export_service, import_service
- 操作应用级数据的服务（project_service 的列表/元数据）继续使用 `get_app_session()`

### R-5: 数据迁移脚本

提供 `scripts/migrate_to_dual_db.py`：
1. 读取现有 `novel_writer.db`
2. 按 project_id 分组，每个项目导出为 `.novel/project.db`
3. `project_info` 从现有 `projects` 表迁移
4. 各关联表 WHERE project_id = ? 导出
5. 更新 `projects` 表：删除项目级字段，保留元数据

## Out of Scope
- 原版 Novel Writer 文件格式的导入导出保持不变
- 不涉及 UI 层改动（服务接口不变，面板无需改）
- 暂不实现 app_config 的设置 UI

## Acceptance Criteria

### AC-1
- 新建项目：应用级 DB 写入 `projects`，项目级 DB 写入 `project_info` + 空表
- 打开项目：从项目级 DB 加载数据，各面板正常显示

### AC-2
- 所有项目级操作（CRUD 章节/角色/情节/关系/时间线/世界观）读写项目级 DB
- 所有应用级操作（项目列表、AI 配置）读写应用级 DB

### AC-3
- 迁移脚本跑完后，新旧数据一致
- 删除项目：删除项目目录 = 完整删除
