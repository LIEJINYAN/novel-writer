# 架构对齐设计文档 Spec

## Why

`002_系统架构设计.md` 规划的架构与实际代码存在多处结构性偏离：3 个声明模块缺失、追踪系统层级错位、插件系统未实现。对齐以降低新开发者的理解成本，确保文档作为真实架构参考。

## What Changes

1. 创建 `services/editor_service.py`，从 `ui/main_window.py` 提取编辑器状态/自动保存/撤销逻辑
2. 创建 `services/ai_service.py`，作为 `core/ai/` 子模块的 Facade 入口
3. 将追踪逻辑从 `services/plot_service.py`、`character_service.py`、`relationship_service.py`、`timeline_service.py`、`consistency_service.py` 统一迁入 `core/tracking/`
4. 实现插件系统 `core/plugins/` 的 `PluginBase` 基类和 `PluginManager` 管理器骨架

**不在此范围**（实现细节差异，不影响架构理解）：
- AI 同步/异步（QThread 与文档 async 之差异）
- 编辑器组件类名（`EditorWidget` vs `TextEditor`）
- 单库/双库（实际双库正确）
- AppConfig 存储方式（QSettings 与文档 config.json 之差异）

## Impact
- Affected specs: 002_系统架构设计.md 第 3.1 节模块总览、第 4 节调用关系
- Affected code: `services/`、`core/tracking/`、`core/plugins/`、`ui/main_window.py`

## ADDED Requirements

### Requirement: EditorService 编辑器服务
系统 SHALL 提供 `EditorService` 类封装编辑器状态管理。

#### Scenario: 提取自动保存逻辑
- **WHEN** 自动保存触发
- **THEN** `EditorService` 接管保存流程，`main_window` 不再直接操作保存定时器

#### Scenario: 提取撤销栈配置
- **WHEN** 设置中修改撤销栈深度
- **THEN** `EditorService` 统一管理所有编辑器的撤销栈参数

### Requirement: AIService AI 服务入口
系统 SHALL 提供 `AIService` 类作为 AI 功能的统一入口。

#### Scenario: 统一调用入口
- **WHEN** UI 层需要调用 AI 续写/润色/重写
- **THEN** 通过 `AIService` 的方法调用，而非直接引用 `core/ai/` 子模块

### Requirement: Tracking 追踪系统迁入 core/
系统 SHALL 将 plot/character/relationship/timeline/consistency 追踪逻辑从 `services/` 迁入 `core/tracking/`。

#### Scenario: 追踪类存在
- **WHEN** 开发者查看 `core/tracking/` 目录
- **THEN** 看到 `PlotTracker`、`CharacterTracker`、`RelationshipTracker`、`TimelineManager`、`ConsistencyChecker` 5 个类文件

### Requirement: Plugin 插件系统骨架
系统 SHALL 提供 `PluginBase` 抽象基类和 `PluginManager` 管理器。

#### Scenario: 插件加载
- **WHEN** 应用启动
- **THEN** `PluginManager` 扫描插件目录并加载有效插件
- **AND** 插件可注册到定义的 7 个扩展点

## MODIFIED Requirements
### Requirement: 现有服务类调整
`services/plot_service.py`、`character_service.py`、`relationship_service.py`、`timeline_service.py`、`consistency_service.py` 中的业务逻辑拆分为两层：`services/` 保留服务层包装，`core/tracking/` 保留核心追踪逻辑。

## REMOVED Requirements
### Requirement: 旧的编辑器状态管理
**Reason**: 逻辑从 `main_window.py` 提取到 `EditorService`
**Migration**: `main_window.py` 中与编辑器状态相关的代码转移到 `services/editor_service.py`
