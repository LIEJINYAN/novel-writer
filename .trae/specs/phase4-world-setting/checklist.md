# Phase 4-B：世界观设定 - 检查清单

## 数据模型
- [x] Checkpoint 1.1: WorldSetting 表含 project_id / setting_type / name / description / parent_id / importance / tags / sort_order 字段
- [x] Checkpoint 1.2: parent_id 自引用 FK，使用 `ondelete="SET NULL"`
- [x] Checkpoint 1.3: project_id 使用 `ondelete="CASCADE"`
- [x] Checkpoint 1.4: 模型可从 `models` 包导入

## 世界观服务
- [x] Checkpoint 2.1: CRUD（create/get/update/delete）完整可用
- [x] Checkpoint 2.2: `list` 支持按类型筛选和名称搜索
- [x] Checkpoint 2.3: `get_tree` 返回正确的树形结构
- [x] Checkpoint 2.4: 删除条目时子节点 parent_id 设为 NULL

## 世界观对话框
- [x] Checkpoint 3.1: 对话框包含名称/类型/父节点/描述/重要性/标签字段
- [x] Checkpoint 3.2: 父节点下拉仅列出同项目条目，编辑时排除自身
- [x] Checkpoint 3.3: 保存验证：名称非空
- [x] Checkpoint 3.4: 保存后数据正确写入数据库

## 世界观面板
- [x] Checkpoint 4.1: 侧边栏"世界观"标签页存在
- [x] Checkpoint 4.2: QTreeWidget 树形显示，父子层级正确
- [x] Checkpoint 4.3: 按重要性颜色标记节点
- [x] Checkpoint 4.4: 双击节点打开编辑对话框
- [x] Checkpoint 4.5: 右键菜单包含"新建子条目/编辑/删除"
- [x] Checkpoint 4.6: 类型筛选和搜索功能正常
- [x] Checkpoint 4.7: 打开/关闭项目时面板自动刷新

## QSS 主题
- [x] Checkpoint 5.1: dark.qss 包含 world_panel 样式
- [x] Checkpoint 5.2: light.qss 包含 world_panel 样式
- [x] Checkpoint 5.3: 暗色/亮色主题下面板显示正常
