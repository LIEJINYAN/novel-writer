# Phase 4-B：世界观设定 Spec

## Why

作者需要结构化地管理故事世界观——地点、规则、物品、传说等。当前软件没有任何"世界观"管理功能，这些信息散落在项目描述和章节备注中。树形层级结构可以清晰地表达地点包含关系（国家→城市→建筑）和设定关联。

## What Changes

| 改动 | 说明 |
|------|------|
| 世界观数据模型 | WorldSetting 表，支持树形层级（parent_id 自引用） |
| 世界观服务 | CRUD + 按类型筛选 + 树形结构查询 |
| 世界观面板 | 侧边栏"世界观"标签页，类型分组树 + 搜索/筛选 |
| 世界观对话框 | 名称、类型、描述、关联角色、重要性、排序 |

## Impact

- **新增** `models/world.py` — WorldSetting 数据模型
- **新增** `services/world_service.py` — CRUD + 树形查询
- **新增** `ui/sidebar/world_panel.py` — 世界观树形面板
- **新增** `ui/dialogs/world_dialog.py` — 世界观编辑对话框
- **修改** `models/__init__.py` — 导出新模型
- **修改** `ui/main_window.py` — 侧边栏添加"世界观"标签页
- **修改** `ui/styles/dark.qss` / `light.qss` — 新面板样式

所有模型使用 `ondelete="CASCADE"`，`project_id` 关联 `projects.id`。

## Requirements

### FR-1: 世界观数据模型

**WorldSetting 表**：
- id, project_id, setting_type(地点/规则/物品/传说/种族/文化/其他), name, description(支持Markdown), parent_id(→world_settings.id, SET NULL, 树形层级), importance(核心/重要/次要), tags(逗号分隔), sort_order, created_at, updated_at

#### 场景：创建世界观条目
- **WHEN** 用户在世界观面板点击"新建"
- **THEN** 弹出对话框，可选择类型、父节点、填写描述

#### 场景：树形层级
- **WHEN** 用户选择一个地点类型条目作为父节点
- **THEN** 子条目在树形视图中缩进显示

### FR-2: 世界观面板

- 侧边栏标签页"世界观"
- QTreeWidget 树形显示，按 setting_type 分组/着色
- 每个条目显示名称 + 重要性图标
- 搜索框：按名称/标签搜索
- 类型下拉筛选
- 新建按钮（弹对话框）
- 右键菜单：新建子条目/编辑/删除
- 双击编辑

### FR-3: 世界观对话框

- 名称
- 类型下拉（地点/规则/物品/传说/种族/文化/其他）
- 父节点下拉（仅显示同项目条目，可选"无"）
- 描述（QTextEdit，支持 Markdown）
- 重要性选择
- 标签（QLineEdit，逗号分隔）
- 保存验证：名称不能为空

## Out of Scope
- Markdown 渲染预览
- 设定关联关系图谱
- 设定冲突检测

## Acceptance Criteria

### AC-1
- 在"世界观"标签页可新建/编辑/删除条目
- 树形结构显示父子层级
- 按类型筛选和搜索正常

### AC-2
- 对话框可设置所有字段
- 父节点下拉只显示同项目条目

### AC-3
- 打开/切换项目时面板自动刷新
- 暗色/亮色主题正常
