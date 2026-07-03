# Tasks

## [x] Task 1: 补全 PRAGMA 配置
- **Priority**: high
- **Depends On**: None
- **Description**: 在 `models/database.py` 的 `init_app_db()` 和 `init_project_db()` 中各添加 `PRAGMA cache_size=-20000` 和 `PRAGMA temp_store=MEMORY`
- **Acceptance**: 启动时日志无报错，数据库连接设置 5 个 PRAGMA

## [x] Task 2: 重写 Alembic 迁移文件
- **Priority**: medium
- **Depends On**: None
- **Description**: 
  - 更新 `alembic/env.py` 同时捕获 AppBase 和 ProjectBase 的 metadata（使用 `target_metadata = [AppBase.metadata, ProjectBase.metadata]`）
  - 将 `alembic.ini` 中 URL 注释掉默认值，改为动态获取 db_path
  - 重写 `alembic/versions/0001_initial_tables.py` 以匹配当前双库架构 schema
  - 验证 `alembic upgrade head` 可正常执行
- **Acceptance**: `alembic upgrade head` 执行成功，数据库结构与模型一致

## [x] Task 3: 验证所有变更
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 验证应用启动正常，Alembic upgrade 通过
- **Acceptance**: `python app/main.py` 启动正常，无报错

# Task Dependencies
- [Task 3] depends on [Task 1]
