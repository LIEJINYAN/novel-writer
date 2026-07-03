# 数据库性能补全 & Alembic 激活 - 检查清单

- [x] Task 1: `init_app_db()` 和 `init_project_db()` 各含 5 个 PRAGMA 设置
- [x] Task 2: `alembic/env.py` 同时导出 AppBase 和 ProjectBase 的 metadata
- [x] Task 2: `alembic/versions/0001_initial_tables.py` 与当前双库 schema 一致
- [x] Task 2: `alembic upgrade head` 执行成功
- [x] Task 3: 应用启动正常，无报错
