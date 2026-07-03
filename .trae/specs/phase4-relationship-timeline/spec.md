# Phase 4-A：关系追踪 + 时间线 Spec

## Why

当前软件支持角色和情节管理，但缺少**角色关系**和**时间线**追踪。作者无法记录角色之间如何关联、关系如何随剧情演变，也无法整理故事内的时间线事件。这两者互相关联——关系变化本身就是时间线的一部分。

## What Changes

| 改动 | 说明 |
|------|------|
| 关系/派系数据模型 | Relationship / Faction / FactionMember 表 |
| 关系变化数据模型 | RelationshipChange 表（跟踪每次变化） |
| 时间线数据模型 | TimelineEvent 表（事件名称、描述、故事内日期、关联章节） |
| 关系服务 | 关系和派系 CRUD + 变化历史记录 |
| 时间线服务 | 事件 CRUD + 按时间线排序 |
| 关系面板 | 侧边栏标签页，关系列表 + 派系列表，搜索筛选 |
| 时间线面板 | 侧边栏标签页，事件列表 + 按重要性颜色标记 |
| 关系对话框 | 编辑两个角色间的关系、类型、强度、备注 |
| 派系对话框 | 编辑派系名称、描述、领导者（从角色选） |
| 时间线对话框 | 事件名称、描述、故事内日期、关联章节、重要性选择 |
| 主窗口集成 | 侧边栏添加"关系""时间线"标签页 + QSS 主题 |

## Impact

- **新增** `models/relationship.py` — 4 个数据模型
- **新增** `models/timeline.py` — 1 个数据模型
- **新增** `services/relationship_service.py` — 关系和派系 CRUD
- **新增** `services/timeline_service.py` — 时间线 CRUD
- **新增** `ui/sidebar/relationship_panel.py` — 关系+派系列表面板
- **新增** `ui/sidebar/timeline_panel.py` — 时间线面板
- **新增** `ui/dialogs/relationship_dialog.py` — 关系编辑对话框
- **新增** `ui/dialogs/faction_dialog.py` — 派系编辑对话框
- **新增** `ui/dialogs/timeline_event_dialog.py` — 时间线事件对话框
- **修改** `ui/main_window.py` — 侧边栏添加"关系""时间线"标签页
- **修改** `ui/styles/dark.qss` / `light.qss` — 新面板样式

所有模型均使用 `ondelete="CASCADE"`，`project_id` 关联 `projects.id`，遵循现有项目删除级联策略。

## Requirements

### FR-1: 关系数据模型

**Relationship 表**：
- id, project_id, character_a_id, character_b_id, relationship_type(盟友/敌对/恋人/家人/师徒/中立/其他), description, current_relation(关系状态标签), intensity(1-10), notes

**RelationshipChange 表**（关联关系变化历史）：
- id, relationship_id, chapter_id(触发章节), change_type(新建/变化/结束), old_relation, new_relation, description, created_at

**Faction 表**：
- id, project_id, name, description, leader_id(→characters.id), goals(JSON), status(活跃/休眠/解散)

**FactionMember 表**（多对多关联）：
- id, faction_id, character_id, role_in_faction, is_core_member, sort_order

#### 场景：编辑角色关系
- **WHEN** 用户在关系面板选择两个角色
- **THEN** 可设置关系类型、强度、备注

#### 场景：关系变化自动记录
- **WHEN** 用户修改已有关系
- **THEN** 自动在 RelationshipChange 中记录变化前和变化后的值

### FR-2: 时间线数据模型

**TimelineEvent 表**：
- id, project_id, event_name, description, story_date(故事内日期/时间点), chapter_id(关联章节), location, importance(核心/重要/次要), sort_order(时间排序)

#### 场景：添加时间线事件
- **WHEN** 用户打开时间线面板
- **THEN** 可添加新事件，填写名称、描述、故事内日期、关联章节、重要性

### FR-3: 关系面板

- 侧边栏标签页"关系"
- 两个子标签页：**关系表**、**派系列表**
- 关系列表：显示双方角色名 + 关系类型 + 强度(图标)
- 派系列表：显示派系名 + 领导者名 + 成员数
- 搜索框：按角色名搜索
- 新建关系/新建派系按钮

### FR-4: 关系对话框

- 角色 A / 角色 B 下拉选择（仅列出当前项目角色）
- 关系类型下拉
- 关系状态标签（自定义文本）
- 强度滑动条 (1-10)
- 关系描述（多行文本）
- 变化历史列表（只读，按时间倒序）

### FR-5: 派系对话框

- 派系名称
- 描述（多行文本）
- 领导者下拉（从角色中选）
- 目标（文本框，每行一条）
- 状态下拉
- 成员列表 + 添加/移除按钮

### FR-6: 时间线面板

- 侧边栏标签页"时间线"
- 事件列表，按重要性颜色标记（核心=红/实心、重要=蓝、次要=灰）
- 搜索框
- 按住 shift 多选删除
- 新建事件按钮

### FR-7: 时间线事件对话框

- 事件名称
- 描述（多行文本）
- 故事内日期（文本，支持"第3年春"这类自定义格式）
- 地点（文本）
- 关联章节下拉
- 重要性选择

## Out of Scope
- 关系图谱可视化（QGraphicsView 关系网络图）
- 时间轴可视化（滚动时间轴视图）
- 关系变化时间线图表

## Acceptance Criteria

### AC-1
- 在"关系"标签页可新建/编辑/删除关系
- 关系列表显示双方角色名和类型
- 派系列表显示名称和成员数

### AC-2
- 编辑已有关系时自动记录变化到历史
- 关系变化历史可查看

### AC-3
- 在"时间线"标签页可新建/编辑/删除事件
- 事件按重要性颜色标记
- 事件可关联章节
