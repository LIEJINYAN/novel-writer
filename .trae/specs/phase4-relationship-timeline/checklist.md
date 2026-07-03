# Phase 4-A：关系追踪 + 时间线 - 检查清单

## 数据模型
- [x] Checkpoint 1.1: Relationship 表含 project_id / character_a_id / character_b_id / relationship_type / intensity / notes 字段
- [x] Checkpoint 1.2: RelationshipChange 表记录每次变化（前后对比）
- [x] Checkpoint 1.3: Faction 表含名称/描述/领导者/状态
- [x] Checkpoint 1.4: FactionMember 表关联派系和角色
- [x] Checkpoint 1.5: TimelineEvent 表含事件名称/故事内日期/关联章节/重要性
- [x] Checkpoint 1.6: 所有 `project_id` 使用 `ondelete="CASCADE"`，`chapters`/`characters` FK 合理使用 SET NULL
- [x] Checkpoint 1.7: 5 个模型均可从 `models` 包导入

## 关系服务
- [x] Checkpoint 2.1: `create_relationship` 创建并返回关系，自动生成 "新建" 类型变化记录
- [x] Checkpoint 2.2: `update_relationship` 修改后根据是否变化生成 "变化" 类型记录
- [x] Checkpoint 2.3: `get_relationship` 返回含变化历史
- [x] Checkpoint 2.4: `list_relationships` 支持按角色名搜索
- [x] Checkpoint 2.5: 派系 CRUD（create/update/delete/list_factions）完整可用
- [x] Checkpoint 2.6: 派系成员添加和移除功能正常

## 时间线服务
- [x] Checkpoint 3.1: 事件 CRUD（create/update/delete/batch_delete）完整可用
- [x] Checkpoint 3.2: `list_events` 按 sort_order 排序
- [x] Checkpoint 3.3: 事件可关联章节

## 关系对话框 + 派系对话框
- [x] Checkpoint 4.1: 关系对话框可选角色 A/B（仅项目角色，禁止 A=B）
- [x] Checkpoint 4.2: 强度滑动条 1-10，实时显示数值
- [x] Checkpoint 4.3: 变化历史只读列表正常显示
- [x] Checkpoint 4.4: 派系对话框可选择领导者、添加/移除成员
- [x] Checkpoint 4.5: 保存后数据写入数据库

## 关系面板
- [x] Checkpoint 5.1: 侧边栏"关系"标签页显示关系表和派系列表两个子标签页
- [x] Checkpoint 5.2: 关系表显示角色A/角色B/类型/强度
- [x] Checkpoint 5.3: 派系列表显示名称/领导者/成员数/状态
- [x] Checkpoint 5.4: 双击行打开对应编辑对话框
- [x] Checkpoint 5.5: 右键菜单编辑/删除
- [x] Checkpoint 5.6: 搜索框可按角色名筛选

## 时间线面板 + 对话框
- [x] Checkpoint 6.1: 事件列表按重要性颜色标记（核心=红/重要=蓝/次要=灰）
- [x] Checkpoint 6.2: 双击事件打开编辑对话框
- [x] Checkpoint 6.3: 右键菜单编辑/删除
- [x] Checkpoint 6.4: Shift 多选后批量删除
- [x] Checkpoint 6.5: 对话框可关联章节

## 主窗口集成 + QSS
- [x] Checkpoint 7.1: 侧边栏有"关系""时间线"标签页
- [x] Checkpoint 7.2: 打开/切换项目时面板自动刷新
- [x] Checkpoint 7.3: dark.qss / light.qss 包含关系和时间线面板样式
- [x] Checkpoint 7.4: 暗色/亮色主题下面板显示正常
