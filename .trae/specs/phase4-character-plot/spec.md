# Phase 4 追踪系统 — 角色与情节

## Why

小说创作中角色和情节是最核心的追踪对象。目前项目可以编辑章节内容，但缺少对角色和情节节点的结构化管理和可视化。作者无法追踪角色出场、了解情节进展、管理伏笔。

## What Changes

| 改动 | 说明 |
|------|------|
| 角色数据模型 | Character 表扩展：性格/外貌/背景/弧线/状态/出场 |
| 情节数据模型 | PlotNode 表 + PlotArc 表：类型/状态/关联章节/伏笔 |
| 角色面板 | 侧边栏标签页，列表+搜索+筛选+角色卡片 |
| 角色详情对话框 | 编辑角色完整信息 |
| 情节面板 | 侧边栏标签页，节点列表+树状视图+状态标记 |
| 情节详情对话框 | 编辑节点信息、关联章节、伏笔管理 |

## Impact

- `models/` — Character/PlotNode/PlotArc/PlotForeshadow 数据模型
- `services/character_service.py` — 角色 CRUD 服务
- `services/plot_service.py` — 情节 CRUD 服务
- `ui/sidebar/character_panel.py` — 角色面板
- `ui/sidebar/plot_panel.py` — 情节面板
- `ui/dialogs/character_dialog.py` — 角色详情对话框
- `ui/dialogs/plot_dialog.py` — 情节详情对话框
- `ui/main_window.py` — 侧边栏添加"角色""情节"标签页
- `ui/styles/dark.qss` / `light.qss` — 新面板样式

## Requirements

### FR-1: 角色数据模型
- Character 表字段：id, project_id, name, aliases, gender, age, role_type(主角/配角/反派等), personality(性格标签), appearance(外貌描述), background(背景故事), arc(角色弧线), status(活跃/已故/失踪等), notes, created_at, updated_at, is_deleted(软删除)
- 出场记录字段：character_id, chapter_id, role(主要/次要/提及), context(出场描述)

### FR-2: 角色面板
- 侧边栏标签页"角色"
- 角色列表：显示头像图标 + 姓名 + 角色类型 + 出场章数
- 搜索框：按名称/别名搜索
- 筛选下拉：按角色类型/状态筛选
- 新建角色按钮 → 弹出角色详情对话框
- 点击角色 → 弹出详情对话框
- 右键菜单：编辑/删除

### FR-3: 角色详情对话框
- 基本信息：姓名、别名、性别、年龄
- 角色类型下拉
- 性格标签（多行文本，每个标签一行）
- 外貌描述（多行文本）
- 背景故事（多行文本）
- 角色弧线（多行文本）
- 状态下拉
- 备注（多行文本）
- 出场记录列表（只读，显示章节标题和角色）

### FR-4: 情节数据模型
- PlotArc 表：id, project_id, name, description, sort_order
- PlotNode 表：id, project_id, arc_id, title, description, status(计划中/进行中/已完成/已放弃), chapter_id(关联章节), importance(核心/重要/次要), notes
- PlotForeshadow 表：id, project_id, node_id(伏笔所属节点), description, target_node_id(揭示节点), status(已埋设/已揭示/已废弃)

### FR-5: 情节面板
- 侧边栏标签页"情节"
- 按弧线分组的节点树
- 节点状态标记（颜色点：计划中=灰，进行中=蓝，已完成=绿，已放弃=红）
- 搜索框
- 新建弧线/新建节点按钮
- 点击节点 → 弹出详情对话框

### FR-6: 情节详情对话框
- 基本信息：标题、描述
- 所属弧线下拉
- 状态下拉
- 关联章节下拉选择
- 重要性选择
- 伏笔列表（可新建/编辑/删除）
- 备注

## Out of Scope
- 角色出场频率分析图表
- 关系图谱可视化（5.3）
- 时间线视图（5.4）
- 一致性检查 AI 分析（5.5）
- 世界观设定管理（5.6）

## Acceptance Criteria

### AC-1
- 新建角色后出现在角色列表中
- 角色列表支持搜索和筛选
- 角色详情对话框可完整编辑所有字段

### AC-2
- 新建弧线和节点后出现在情节面板中
- 节点按弧线分组，状态颜色正确
- 节点可关联章节

### AC-3
- 角色面板和情节面板在侧边栏中作为独立标签页
- 暗色/亮色主题样式正确
