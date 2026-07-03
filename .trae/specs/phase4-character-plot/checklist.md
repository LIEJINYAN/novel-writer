# Phase 4 角色与情节 - 检查清单

## 数据模型
- [x] Checkpoint 1.1: Character 表包含所有字段（name/aliases/role_type/personality/appearance/background/arc/status 等）
- [x] Checkpoint 1.2: ChapterAppearance 表关联 character 和 chapter
- [x] Checkpoint 1.3: PlotArc 表包含 name/description/sort_order
- [x] Checkpoint 1.4: PlotNode 表包含 title/status/chapter_id/importance/arc_id
- [x] Checkpoint 1.5: PlotForeshadow 表含伏笔和揭示节点关联
- [x] Checkpoint 1.6: 所有模型可导入

## 角色服务
- [x] Checkpoint 2.1: create_character 创建并返回对象
- [x] Checkpoint 2.2: get/update/delete 角色完整可用
- [x] Checkpoint 2.3: list_characters 支持搜索和筛选
- [x] Checkpoint 2.4: add_appearance 记录出场
- [x] Checkpoint 2.5: get_appearances 返回出场列表

## 情节服务
- [x] Checkpoint 3.1: 弧线 CRUD 完整可用
- [x] Checkpoint 3.2: 节点 CRUD 完整可用
- [x] Checkpoint 3.3: 伏笔 CRUD 完整可用
- [x] Checkpoint 3.4: get_nodes_by_arc 按弧线分组
- [x] Checkpoint 3.5: get_nodes_by_status 按状态筛选

## 角色面板
- [x] Checkpoint 4.1: 侧边栏有"角色"标签页
- [x] Checkpoint 4.2: 角色列表显示姓名+类型+出场数
- [x] Checkpoint 4.3: 搜索和筛选可用
- [x] Checkpoint 4.4: 新建角色按钮弹出对话框
- [x] Checkpoint 4.5: 右键菜单编辑/删除

## 角色对话框
- [x] Checkpoint 5.1: 所有字段可编辑
- [x] Checkpoint 5.2: 出场记录列表只读展示
- [x] Checkpoint 5.3: 保存后角色数据更新

## 情节面板+对话框
- [x] Checkpoint 6.1: 侧边栏有"情节"标签页
- [x] Checkpoint 6.2: 节点按弧线分组展示
- [x] Checkpoint 6.3: 状态颜色标记正确
- [x] Checkpoint 6.4: 新建弧线/节点按钮可用
- [x] Checkpoint 6.5: 对话框编辑节点完整信息

## QSS
- [x] Checkpoint 7.1: 角色面板在暗色主题下正常
- [x] Checkpoint 7.2: 角色面板在亮色主题下正常
- [x] Checkpoint 7.3: 情节面板在两种主题下正常
