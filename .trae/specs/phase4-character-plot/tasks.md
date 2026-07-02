# Phase 4 角色与情节 - 实现计划

### [ ] Task 1: 数据模型

- **Priority**: high
- **Depends On**: None
- **Description**:
  在现有 models 中添加角色和情节相关的数据模型：
  - `models/character.py` — Character 表（name, aliases, gender, age, role_type, personality, appearance, background, arc, status, notes）+ ChapterAppearance 表
  - `models/plot.py` — PlotArc 表 + PlotNode 表 + PlotForeshadow 表
  - `models/__init__.py` — 导出新模型
  - Alembic 迁移脚本或自动创建表
- **Verification**: `python -c "from models.character import Character; from models.plot import PlotNode; print('模型导入成功')"`

### [ ] Task 2: 角色服务

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  创建 `services/character_service.py`：
  - `create_character(project_id, data)` → Character
  - `get_character(id)` → Character
  - `update_character(id, data)` → Character
  - `delete_character(id)` → bool
  - `list_characters(project_id, search=None, role_type=None, status=None)` → list[Character]
  - `add_appearance(character_id, chapter_id, role, context)` → ChapterAppearance
  - `get_appearances(character_id)` → list[ChapterAppearance]
  - `get_character_count(project_id)` → int
- **Verification**: 单元测试通过

### [ ] Task 3: 情节服务

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  创建 `services/plot_service.py`：
  - 弧线 CRUD：create_arc / get_arc / update_arc / delete_arc / list_arcs
  - 节点 CRUD：create_node / get_node / update_node / delete_node / list_nodes
  - 伏笔 CRUD：create_foreshadow / get_foreshadow / update_foreshadow / delete_foreshadow / list_foreshadows
  - `get_nodes_by_arc(arc_id)` → list[PlotNode]
  - `get_nodes_by_status(project_id, status)` → list[PlotNode]
- **Verification**: 单元测试通过

### [ ] Task 4: 角色面板

- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  创建 `ui/sidebar/character_panel.py`：
  - CharacterPanel(QWidget) 类
  - 标题 + 搜索框 + 筛选下拉 + 新建按钮
  - QListWidget 展示角色列表（自定义 item widget 显示头像图标+姓名+类型+出场数）
  - 点击 item → 弹出 CharacterDialog
  - 右键菜单：编辑/删除
  - 信号：character_selected, character_created, character_deleted
  注册到 main_window.py 侧边栏标签页
- **Verification**: 应用启动后侧边栏显示"角色"标签页

### [ ] Task 5: 角色详情对话框

- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  创建 `ui/dialogs/character_dialog.py`：
  - CharacterDialog(QDialog) 类
  - 布局：基本信息区域（姓名/别名/性别/年龄）+ 角色类型下拉 + 性格标签文本区域 + 外貌描述 + 背景故事 + 角色弧线 + 状态下拉 + 备注 + 出场记录列表（只读）
  - 确定/取消按钮
  - 加载/保存逻辑调用 character_service
- **Verification**: 对话框可打开、编辑、保存

### [ ] Task 6: 情节面板 + 详情对话框

- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  创建 `ui/sidebar/plot_panel.py`：
  - PlotPanel(QWidget) 类
  - 标题 + 搜索框 + 新建弧线/节点按钮
  - QTreeWidget 按弧线分组展示节点（状态颜色点 + 标题 + 关联章节）
  - 双击节点 → 弹出 PlotDialog
  创建 `ui/dialogs/plot_dialog.py`：
  - 基本信息 + 弧线下拉 + 状态下拉 + 章节下拉 + 重要性 + 伏笔列表 + 备注
  注册到 main_window.py 侧边栏标签页
- **Verification**: 侧边栏显示"情节"标签页，可管理节点

### [ ] Task 7: QSS 主题

- **Priority**: low
- **Depends On**: Task 4, Task 6
- **Description**:
  更新 dark.qss 和 light.qss：
  - 角色列表项样式
  - 情节树节点状态颜色
  - 对话框内表单样式
- **Verification**: 角色/情节面板在两种主题下可读

# Task Dependencies
- Task 1（数据模型）→ Task 2（角色服务） + Task 3（情节服务）
- Task 2 → Task 4（角色面板） + Task 5（角色对话框）
- Task 3 → Task 6（情节面板+对话框）
- Task 4, Task 6 → Task 7（QSS）
