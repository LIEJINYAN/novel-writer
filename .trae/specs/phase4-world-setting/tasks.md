# Phase 4-B：世界观设定 - 实现计划

## [x] Task 1: 世界观数据模型

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `models/world.py`
  - `WorldSetting` 表：
    - id, project_id(FK→projects.id, CASCADE), setting_type(地点/规则/物品/传说/种族/文化/其他)
    - name(not null), description(Text), parent_id(FK→world_settings.id, SET NULL)
    - importance(核心/重要/次要), tags(Text, 逗号分隔), sort_order
    - created_at, updated_at
  - 自引用关系：`parent = rel("WorldSetting", remote_side=[id], backref="children")`
  - 更新 `models/__init__.py`
- **Verification**: `from models import WorldSetting` 成功

## [ ] Task 2: 世界观服务

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `services/world_service.py`，`world_service` 单例
  - `create(project_id, name, **data)` — 新建条目
  - `get(setting_id)` — 含子条目
  - `update(setting_id, **data)` — 更新
  - `delete(setting_id)` — 删除（子条目 parent_id 设为 NULL）
  - `list(project_id, type_filter="", search="")` — 按类型/名称搜索，按 sort_order 排序
  - `get_tree(project_id)` — 返回树形结构 [{"id":..., "name":..., "children": [...]}]
  - 遵循现有 `CharacterService` 模式
- **Verification**: 创建/编辑/删除条目正常，`get_tree` 返回正确树形结构

## [x] Task 3: 世界观对话框

- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 创建 `ui/dialogs/world_dialog.py`
  - `WorldDialog(QDialog)`：
    - 名称、类型下拉（含预设类型）
    - 父节点下拉（列出同项目条目，不含自身和子孙）
    - 描述（QTextEdit）
    - 重要性选择（QComboBox）
    - 标签（QLineEdit，placeholder="逗号分隔"）
    - 保存验证：名称非空
  - 编辑模式时加载已有数据、父节点排除自身
- **Verification**: 新建/编辑对话框打开正常，保存后数据正确

## [ ] Task 4: 世界观面板

- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 创建 `ui/sidebar/world_panel.py`
  - `WorldPanel(QWidget)`：
    - 顶部：类型筛选（QComboBox）+ 搜索框 + 新建按钮
    - 中间：QTreeWidget 树形显示
      - 每个节点：`[类型图标] 名称`，按重要性着色
      - 展开/折叠功能
    - 双击节点 → 打开 WorldDialog
    - 右键菜单：新建子条目/编辑/删除
    - 连接 `signal_bus.project_opened` / `project_closed`
    - `clear()` 方法
- **Verification**: 树形显示正常，右键菜单完整，双击编辑

## [x] Task 5: 主窗口集成 + QSS

- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 修改 `ui/main_window.py`：
    - 引入 `WorldPanel`
    - 侧边栏添加"世界观"标签页
    - close 时调用 `world_panel.clear()`
  - 修改 `ui/styles/dark.qss` / `light.qss`：
    - `QWidget#world_panel` 面板样式
    - 树节点重要性颜色
- **Verification**: 侧边栏显示"世界观"标签页，数据与当前项目绑定

# Task Dependencies
- Task 1 → Task 2 → Task 3 → Task 4 → Task 5

# 并行执行建议
- 各 Task 顺序依赖，不能并行
