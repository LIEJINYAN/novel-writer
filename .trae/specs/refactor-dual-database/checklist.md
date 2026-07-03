# 双层数据库架构重构 - 检查清单

## DatabaseManager 双引擎
- [ ] Checkpoint 1.1: AppBase / ProjectBase 两个 DeclarativeBase 独立
- [ ] Checkpoint 1.2: `init_app_db` 创建应用引擎，`init_project_db` 创建项目引擎
- [ ] Checkpoint 1.3: `get_app_session` / `get_project_session` 返回独立的 session
- [ ] Checkpoint 1.4: `open_project` / `close_project` 正确管理项目引擎生命周期
- [ ] Checkpoint 1.5: `get_session()` 保留为 `get_app_session()` 别名

## 应用级模型
- [ ] Checkpoint 2.1: projects 表精简为元数据（设计文档 3.2 节）
- [ ] Checkpoint 2.2: app_config 表（设计文档 3.1 节）
- [ ] Checkpoint 2.3: ai_providers 表（设计文档 3.3 节）
- [ ] Checkpoint 2.4: ai_conversations 表（设计文档 3.4 节）
- [ ] Checkpoint 2.5: plugins 表（设计文档 3.5 节）
- [ ] Checkpoint 2.6: AppBase.metadata.create_all 创建 5 张表

## 项目级模型
- [ ] Checkpoint 3.1: project_info 表（设计文档 4.1 节）
- [ ] Checkpoint 3.2: volumes 表（设计文档 4.2 节）
- [ ] Checkpoint 3.3: chapters 表（设计文档 4.3 节）
- [ ] Checkpoint 3.4: characters 表（设计文档 4.4 节）
- [ ] Checkpoint 3.5: character_states 表（设计文档 4.5 节）
- [ ] Checkpoint 3.6: character_appearances 表（设计文档 4.6 节）
- [ ] Checkpoint 3.7: plot_nodes 表（设计文档 4.7 节）
- [ ] Checkpoint 3.8: foreshadowings 表（设计文档 4.8 节）
- [ ] Checkpoint 3.9: conflicts 表（设计文档 4.9 节）
- [ ] Checkpoint 3.10: relationships 表（设计文档 4.10 节）
- [ ] Checkpoint 3.11: factions 表（设计文档 4.11 节）
- [ ] Checkpoint 3.12: faction_members 表（设计文档 4.12 节）
- [ ] Checkpoint 3.13: relationship_history 表（设计文档 4.13 节）
- [ ] Checkpoint 3.14: timeline_events 表（设计文档 4.14 节）
- [ ] Checkpoint 3.15: validation_rules 表（设计文档 4.15 节）
- [ ] Checkpoint 3.16: world_settings 表（设计文档 4.16 节）
- [ ] Checkpoint 3.17: writing_method_config 简表
- [ ] Checkpoint 3.18: writing_statistics 表（设计文档 4.17 节）
- [ ] Checkpoint 3.19: 所有模型无 project_id 字段，使用 ProjectBase
- [ ] Checkpoint 3.20: ProjectBase.metadata.create_all 创建 19 张表

## project_info 服务
- [ ] Checkpoint 4.1: get / update 正常读写 project_info 表
- [ ] Checkpoint 4.2: 使用 get_project_session()

## 服务层改造
- [ ] Checkpoint 5.1: chapter_service 所有方法改用 get_project_session()
- [ ] Checkpoint 5.2: character_service 所有方法改用 get_project_session()
- [ ] Checkpoint 5.3: plot_service 所有方法改用 get_project_session()
- [ ] Checkpoint 5.4: relationship_service 所有方法改用 get_project_session()
- [ ] Checkpoint 5.5: timeline_service 所有方法改用 get_project_session()
- [ ] Checkpoint 5.6: world_service 所有方法改用 get_project_session()
- [ ] Checkpoint 5.7: consistency_service 所有方法改用 get_project_session()
- [ ] Checkpoint 5.8: export_service / import_service 改用 get_project_session()
- [ ] Checkpoint 5.9: project_service 拆分应用级和项目级操作

## 主窗口集成
- [ ] Checkpoint 6.1: 打开项目时调用 db_manager.open_project()
- [ ] Checkpoint 6.2: 关闭项目时调用 db_manager.close_project()
- [ ] Checkpoint 6.3: signal_bus.project_opened 接口不变
- [ ] Checkpoint 6.4: 应用启动/关闭正常

## 数据迁移
- [ ] Checkpoint 7.1: 迁移脚本遍历所有项目
- [ ] Checkpoint 7.2: 每个项目正确导出 project_info
- [ ] Checkpoint 7.3: 每个项目正确导出所有关联表
- [ ] Checkpoint 7.4: 应用级 projects 表更新为元数据
- [ ] Checkpoint 7.5: 迁移后新旧数据一致
