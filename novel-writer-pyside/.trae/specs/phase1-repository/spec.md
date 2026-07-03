# Phase 1 仓储模式实现 - 产品需求文档

## Overview
- **Summary**: 实现基于 SQLAlchemy 的仓储模式（Repository Pattern），提供统一的数据访问层抽象，将数据访问逻辑从服务层解耦。
- **Purpose**: 遵循 DDD（领域驱动设计）原则，降低服务层与具体 ORM 实现的耦合度，提高代码可测试性和可维护性。
- **Target Users**: 开发者（作为内部基础设施组件）

## Goals
- 实现通用的 BaseRepository 基类，封装常见的 CRUD 操作
- 为现有模型（Project、Chapter、Character、PlotArc、PlotNode、PlotForeshadow、AIProvider）创建具体仓储实现
- 保持向后兼容性，服务层可平滑迁移到仓储模式

## Non-Goals (Out of Scope)
- 不修改现有服务层的公共 API 接口
- 不改变现有数据库表结构
- 不实现单元测试（测试属于 Phase 5）

## Background & Context
- 项目当前使用服务层（services/）直接操作数据库会话
- SQLAlchemy 已集成，Base 类已定义
- 现有服务层代码分散，缺少统一的数据访问抽象

## Functional Requirements
- **FR-1**: BaseRepository 提供通用 CRUD 方法（get、list、create、update、delete）
- **FR-2**: BaseRepository 支持过滤、排序、分页查询
- **FR-3**: 为每个业务模型创建具体仓储类
- **FR-4**: 仓储层与服务层解耦，服务层可通过仓储访问数据

## Non-Functional Requirements
- **NFR-1**: 仓储层必须线程安全（使用独立会话）
- **NFR-2**: 查询性能不低于现有直接 SQLAlchemy 查询方式
- **NFR-3**: 代码符合项目现有风格（PEP 8）

## Constraints
- **Technical**: Python 3.11+, SQLAlchemy 2.x, PySide6
- **Dependencies**: 依赖 models/database.py 中的 db_manager

## Assumptions
- 所有业务模型已继承 Base 类
- db_manager 提供的 get_session() 方法可用
- 现有服务层代码结构稳定

## Acceptance Criteria

### AC-1: BaseRepository 基类实现
- **Given**: 项目已初始化，数据库连接可用
- **When**: 创建继承 BaseRepository 的具体仓储类
- **Then**: 仓储类自动获得 get、list、create、update、delete 方法
- **Verification**: `programmatic`

### AC-2: 过滤和排序功能
- **Given**: BaseRepository 已实现
- **When**: 调用 list 方法时传入过滤条件和排序字段
- **Then**: 返回符合条件的排序后结果列表
- **Verification**: `programmatic`

### AC-3: 具体仓储创建
- **Given**: BaseRepository 已实现
- **When**: 为每个业务模型创建具体仓储类
- **Then**: 所有模型都有对应的仓储实现，可正常使用
- **Verification**: `programmatic`

### AC-4: 模块导入验证
- **Given**: 仓储模块已创建
- **When**: 尝试导入仓储模块
- **Then**: 导入成功，无语法错误
- **Verification**: `programmatic`

## Open Questions (已评估）
- [x] **是否需要为服务层添加可选的仓储依赖注入？** → 暂不实现。当前仓储层作为可选基础组件存在，服务层仍直接操作 db_manager。当出现明确的多实现需求或单元测试需求时再引入 DI。
