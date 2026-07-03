# 数据库性能补全 & Alembic 激活 Spec

## Why

`003_数据库设计.md` 中规划了 3 项尚未实现的内容：两个 PRAGMA 性能配置和 Alembic 迁移管线，补齐以对齐设计文档。

## What Changes

1. 在 `init_app_db` 和 `init_project_db` 中加入 `PRAGMA cache_size=-20000` 和 `PRAGMA temp_store=MEMORY`
2. 激活 Alembic 迁移管线：更新 `alembic/env.py` 同时支持 AppBase 和 ProjectBase，重写过时的 `0001_initial_tables.py` 以匹配当前双库 schema

## Impact
- Affected specs: 003_数据库设计.md 第 7.2、8.1 节
- Affected code: `models/database.py`, `alembic/env.py`, `alembic/versions/0001_initial_tables.py`

## ADDED Requirements

### Requirement: PRAGMA 补全
系统 SHALL 在初始化应用级和项目级数据库时设置 `cache_size=-20000`（20MB 缓存）和 `temp_store=MEMORY`（临时表放内存）。

#### Scenario: 初始化时生效
- **WHEN** `init_app_db()` 或 `init_project_db()` 被调用
- **THEN** 对应数据库连接执行了 5 个 PRAGMA（journal_mode、busy_timeout、foreign_keys、cache_size、temp_store）

### Requirement: Alembic 激活
系统 SHALL 提供可用的 Alembic 迁移管线，支持自动生成迁移脚本。

#### Scenario: alembic upgrade head
- **WHEN** 执行 `alembic upgrade head`
- **THEN** 迁移成功，数据库 schema 与当前模型一致
- **AND** 项目级 DB 与应用级 DB 的变更均纳入版本管理

## MODIFIED Requirements
### Requirement: 现有 PRAGMA 配置
`init_app_db` 和 `init_project_db` 各增加 2 行 PRAGMA 设置。

### Requirement: Alembic 配置
`alembic/env.py` 改为同时加载 AppBase 和 ProjectBase 的 metadata，`0001_initial_tables.py` 重写为当前双库架构。
