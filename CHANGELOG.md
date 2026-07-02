# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- 新增 Trae 文档生成指南与完整项目分析文档

### Changed

- 在项目矩阵中添加 Article-Writer

---

## [0.20.0] - 2025-11-01

### Added

- **交互式启动界面**：全新的 CLI 启动体验，提供更友好的视觉反馈
- **命令前缀优化**：将命令前缀从 `novel.` 改为 `content.`，更直观地反映功能用途

### Changed

- 启动界面视觉设计优化，使用更清晰的图标和布局
- 命令命名规范调整，提高用户理解度

---

## [0.19.0] - 2025-10-25

### Added

- **Codex CLI 支持**：完整支持 OpenAI Codex CLI
  - 命令格式: `/novel-命令名` (例如: `/novel-write`)
  - 命令目录: `.codex/prompts/`
  - 使用 `novel-` 前缀避免命名冲突
  - 纯 Markdown 格式(无 YAML frontmatter)
  - 13 个核心命令全部支持
- **AI 平台命令对照文档**：`docs/ai-platform-commands.md` - 13 个 AI 平台的完整命令对照指南

### Changed

- 更新 `docs/why-codex-not-supported.md`，标题改为"Novel Writer 的 Codex CLI 支持"
- 更新 README 添加 Codex CLI 支持说明和命令格式示例

### Fixed

- 构建系统支持 Codex CLI 的命名空间格式

---

## [0.18.5] - 2025-10-24

### Fixed

- **Gemini 宪法保存路径错误 (#6)**：统一所有命令模板文件中的路径引用，全部使用完整路径 `.specify/memory/constitution.md`
  - 修改 `templates/commands/constitution.md` 中 3 处路径引用
  - 修改 `templates/commands/specify.md` 中 1 处路径引用
  - 修改 `templates/commands/plan.md` 中 1 处路径引用
  - 修改 `templates/commands/write.md` 中 3 处路径引用
  - 重新构建所有平台的命令文件

---

## [0.18.4] - 2025-10-15

### Fixed

- **宪法文件命名统一**：统一宪法文件命名为 `constitution.md`
  - 重命名源文件: `memory/writing-constitution.md` → `memory/constitution.md`
  - 修改所有 Bash 脚本中的文件路径引用 (6个文件)
  - 修改所有 PowerShell 脚本中的文件路径引用 (5+个文件)
  - 修改所有命令模板中的文件引用
- **脚本路径重复问题**：修复构建系统中的 `rewrite_paths()` 函数重复添加 `.specify/` 前缀的问题

---

## [0.18.3] - 2025-10-15

### Added

- **插件安装系统标准化**：genre-knowledge 插件统一使用 `novel plugins:add` 命令安装
  - 新增 `plugins/genre-knowledge/config.yaml` 配置文件
  - 插件元数据完整定义(name, version, description, type, dependencies)

### Changed

- 更新 `plugins/genre-knowledge/README.md`，修改安装方法为标准化命令
- 更新 CLI 可用插件列表，添加 genre-knowledge

---

## [0.18.2] - 2025-10-15

### Added

- **补全插件命令文件**：genre-knowledge 插件的 `commands/` 目录添加 3 个增强命令文件
  - `commands/clarify-enhance.md` - clarify 命令的类型知识增强提示词
  - `commands/plan-enhance.md` - plan 命令的动态类型知识加载提示词
  - `commands/write-enhance.md` - write 命令的类型风格应用提示词

---

## [0.18.1] - 2025-10-15

### Changed

- **类型知识插件化**：将 `spec/knowledge/genres/` 的5个类型知识文件迁移到 `plugins/genre-knowledge/knowledge/genres/`
  - `fantasy.md` - 奇幻/玄幻类型指导
  - `scifi.md` - 科幻类型指导
  - `romance.md` - 言情类型指导
  - `mystery.md` - 悬疑推理类型指导
  - `shuangwen.md` - 爽文类型指导
- **核心命令优化**：移除核心命令对插件的硬编码依赖，添加 `plugins/**` 通配符权限

### Removed

- 删除 `spec/knowledge/genres/` 目录（已迁移至插件）

---

## [0.18.0] - 2025-10-14

### Added

- **四维特征分析框架**：增强创作分析能力
- **反AI检测增强**：优化去AI味写作规范

---

## [0.17.3] - 2025-10-13

### Added

- **核心命令增强**：优化多个核心命令的提示词模板
- **book-analysis 风格内化**：新增书籍分析和风格内化功能

---

## [0.17.2] - 2025-10-13

### Fixed

- **修复新项目缺失文件**：确保初始化项目时包含所有必要的预设文件和反AI检测文件
- **增强 upgrade 命令**：支持所有 13 个 AI 平台的灵活升级

---

## [0.17.1] - 2025-10-12

### Fixed

- **修复 expert 命令缺失核心专家文件**：补全专家模式所需的核心文件

---

## [0.17.0] - 2025-10-12

### Fixed

- **修复 expert 命令构建警告**：解决构建时的警告信息
- **优化反AI检测规范**：改进反AI检测写作规则

---

## [0.16.5] - 2025-10-11

### Added

- **增强 upgrade 命令**：支持所有 13 个 AI 平台的灵活升级

---

## [0.16.4] - 2025-10-11

### Added

- **创作强化指令**：补偿编程工具低温度限制，通过强化提示词模拟高温效果
  - 情感表达增强
  - 对话自然化
  - 场景生动化
  - 冲突张力提升
  - 节奏变化优化

---

## [0.16.3] - 2025-10-11

### Added

- **改进小说分段格式规范**：优化章节分段和格式规则

### Fixed

- **修复脚本错误**：解决多个脚本中的语法和逻辑错误

---

## [0.16.2] - 2025-10-10

### Fixed

- **修复脚本中的宪法文件名引用**：统一脚本中对宪法文件的引用路径

---

## [0.16.1] - 2025-10-10

### Fixed

- **修复 CLI 可执行权限问题**：确保 CLI 命令具有正确的执行权限

---

## [0.16.0] - 2025-10-10

### Added

- **checklist 系统统一化**：整合检查清单功能，提供标准化的质量检查流程

### Changed

- **项目清理**：移除冗余文件和代码，优化项目结构

---

## [0.15.0] - 2025-10-11

### Changed

- **多平台命令格式优化**：根据每个 AI 平台的实际支持情况生成正确的命令文件格式
  - 纯 Markdown（无 frontmatter）：Cursor, GitHub Copilot, Codex CLI, Auggie CLI, CodeBuddy, Amazon Q Developer
  - 最小 frontmatter（只 description）：OpenCode
  - 部分 frontmatter（description + argument-hint）：Roo Code, Windsurf, Kilo Code
  - 完整 frontmatter（所有字段）：Claude Code
  - TOML 格式（description + prompt）：Gemini CLI, Qwen Code

---

## [0.14.2] - 2025-10-10

### Fixed

- **中文字数统计问题**：修复 `wc -w` 对中文字数统计极不准确的问题
  - 新增 `count_chinese_words()` 函数，准确性提升 12+ 倍
  - 排除 Markdown 标记、代码块、空格、标点符号
  - 只统计实际文字内容

### Added

- **字数统计函数**（`scripts/bash/common.sh`）
  - `count_chinese_words()` - 准确的中文字数统计
  - `show_word_count_info()` - 显示友好的字数验证信息
- **新增文档**：`docs/word-count-guide.md` - 完整的字数统计使用说明

---

## [0.14.0] - 2025-10-09

### Added

- **Roo Code 斜杠命令支持**：`novel init` 与 `novel upgrade` 现在支持生成 `.roo/commands` 目录
- **插件系统集成**：插件命令注入流程同步扩展至 Roo Code

---

## [0.13.7] - 2025-10-06

### Fixed

- **插件命令文件命名优化**：修复插件安装后命令文件名过于复杂的问题
  - 移除不必要的 `plugin-{pluginName}-` 前缀
  - 插件命令文件名简化

---

## [0.13.6] - 2025-10-06

### Fixed

- **CLI 帮助文本更新**：修复 `novel init` 初始化后显示的帮助文本
  - 更新核心命令列表为正确的七步方法论命令
  - 移除已废弃的旧命令
  - 更新推荐流程

---

## [0.13.0] - 2025-10-05

### Added

- **增强插件系统项目检测**：改进插件安装和检测机制
- **用户体验提升**：优化 CLI 交互和提示信息

---

## [0.12.2] - 2025-10-04

### Added

- **Claude Code 增强层**：为 Claude Code 用户提供专属增强版本命令
  - 增强的 Frontmatter 字段（argument-hint, allowed-tools, model, disable-model-invocation）
  - 动态上下文加载，支持内联 bash 执行
  - 11 个增强命令（P0: analyze, write, clarify; P1: track, specify, plan; P2: tasks, plot-check, timeline, relations, world-check）

---

## [0.12.1] - 2025-10-01

### Added

- **智能双模式 analyze**：根据创作阶段自动选择分析类型
  - 框架一致性分析（章节数 < 3）
  - 内容质量分析（章节数 ≥ 3）
  - 支持 `--type` 参数手动指定模式

---

## [0.12.0] - 2025-09-30

### Added

- **多线索管理系统**：通过增强现有命令模板实现完整的多线索管理能力
  - specification.md 新增第五章:线索管理规格（线索定义表、线索节奏规划、线索交汇点规划、伏笔管理表、线索修改决策矩阵）
  - creative-plan.md 增强（添加"活跃线索"和"交汇点"列）
  - tasks.md 增强（每个写作任务增加线索相关字段）
  - plot-tracker.json 增强（自动从 specification.md 读取线索数据）

---

## [0.11.0] - 2025-09-30

### Added

- **SDD方法论实战指南**：新增 `docs/writing/practical-guide.md`（约10000字）
  - 基于《重返1984》小说的完整SDD实战案例
  - 详细讲解SDD的分层递归应用
  - 提供4个完整场景的实际输入提示词示例
- **可视化图表**：新增3个SVG图表辅助理解（sdd-levels.svg, sdd-flow.svg, prompt-structure.svg）

---

## [0.10.5] - 2025-09-30

### Fixed

- **common.sh 缺少函数**：添加 `get_active_story()` 函数，修复脚本执行错误

---

## [0.10.4] - 2025-09-30

### Fixed

- **七步方法论脚本缺失**：补全 Bash 脚本支持
  - 创建 `plan-story.sh` - 创作计划脚本
  - 创建 `tasks-story.sh` - 任务分解脚本
  - 复制其他必要脚本

---

## [0.10.3] - 2025-09-30

### Removed

- **移除旧格式兼容**：完全移除对旧 `story.md` 格式的支持
  - 所有脚本现在只支持新格式 `specification.md`

### Changed

- 更新所有脚本和命令模板使用新格式

---

## [0.10.2] - 2025-09-30

### Fixed

- **命令模板缺失**：补全七步方法论命令模板
  - 添加 `/constitution` - 创作宪法命令
  - 添加 `/specify` - 故事规格命令
  - 添加 `/plan` - 创作计划命令
  - 添加 `/tasks` - 任务分解命令
  - 添加 `/analyze` - 综合验证命令

---

## [0.10.1] - 2025-09-30

### Changed

- **脚本体系重构**：统一管理 Bash 和 PowerShell 脚本至 `.specify/scripts/`
- **命令同步更新**：完善 Claude Code 和 Gemini 命令模板
- **追踪系统增强**：新增 `/track-init` 命令，完善进度追踪和验证规则
- **命令优化**：更新 `/clarify`、`/expert`、`/write`、`/relations` 等命令

### Removed

- 删除冗余命令：`/story`、`/style`、`/outline`、`/chapters`

---

## [0.10.0] - 2025-09-29

### Added

- **七步方法论体系**：引入完整的规格驱动开发（SDD）创作流程
  - `/constitution` - 创作宪法，定义最高层级的创作原则
  - `/specify` - 故事规格，像 PRD 一样定义故事需求
  - `/clarify` - 澄清决策，通过交互式问答明确关键点
  - `/plan` - 创作计划，制定技术实现方案
  - `/tasks` - 任务分解，生成可执行的任务清单
  - `/write` - 章节写作（重构以适配新流程）
  - `/analyze` - 综合验证，全方位质量检查

### Changed

- **系统重构**：跨平台同步（PowerShell 脚本和 Gemini TOML 命令完全同步）
- **文档体系升级**：创建 `METHODOLOGY.md` 和 `MIGRATION.md`

### Removed

- 删除冗余命令：`/story`、`/style`、`/outline`、`/chapters`、`/method`

---

## [0.9.0] - 2025-09-29

### Added

- **`/clarify` 命令**：交互式澄清故事大纲中的关键决策点
- **结构化创作流程**：story → clarify → outline
- **智能问答**：AI 识别模糊点，通过5个精准问题明确创作方向

---

## [0.8.4] - 2025-09-26

### Added

- **Authentic Voice 真实人声插件**：提升原创度与自然度
  - `/authentic-voice` 真实人声创作模式
  - `/authenticity-audit` 人味自查与行级改写建议
  - 专家 `authentic-editor`：更细致的人声编辑
- **离线文本自查脚本**：`scripts/bash/text-audit.sh`

---

## [0.8.3] - 2025-09-25

### Added

- **完整插件 Gemini 支持**：所有插件都支持 Gemini CLI
  - translate 插件：3 个 TOML 命令
  - book-analysis 插件：6 个 TOML 命令
  - 作者风格插件：13 个 TOML 命令
  - stardust-dreams 插件：4 个 TOML 命令

---

## [0.8.2] - 2025-09-25

### Added

- **Google Gemini CLI 支持**：完整的 Gemini CLI 斜杠命令集成
  - 新增 13 个 TOML 格式的命令定义
  - 支持命名空间命令
  - 插件系统同时支持 Markdown 和 TOML 双格式

---

## [0.7.0] - 2025-01-24

### Added

- **外部AI建议整合功能**：支持整合来自Gemini、ChatGPT等AI工具的分析建议
  - 扩展 `/style` 命令，新增 `refine` 模式
  - 支持JSON和Markdown两种建议格式
  - 自动分类处理建议（风格/角色/情节/世界观/对话）

---

## [0.6.2] - 2025-09-24

### Changed

- **ESM 模块支持**：项目全面迁移到 ESM（ECMAScript Modules）
  - 添加 `"type": "module"` 配置
  - 更新所有导入语句为 ESM 格式

---

## [0.6.1] - 2025-09-24

### Fixed

- **依赖问题**：修复 `js-yaml` 模块缺失导致的运行错误

---

## [0.6.0] - 2025-09-24

### Added

- **角色一致性验证系统**：解决AI生成内容中的角色名称错误问题
  - 新增 `validation-rules.json` 验证规则文件
  - `/write` 命令增强：写作前提醒、写作后验证
  - `/track --check` 深度验证模式
  - `/track --fix` 自动修复模式

---

## [0.5.6] - 2025-09-23

### Added

- **写作风格插件**：新增三个写作风格插件
  - `luyao-style` - 路遥风格写作插件
  - `shizhangyu-style` - 施章渝风格写作插件
  - `wangyu-style` - 王毓风格写作插件

---

## [0.4.3] - 2025-09-21

### Changed

- **默认版本号更新**：将 version.ts 中的默认版本号从 0.4.1 更新为 0.4.2

---

## [0.4.2] - 2025-09-21

### Changed

- **统一版本管理**：实现自动从 package.json 读取版本号的模块
- **知识库模板系统**：将硬编码的知识库文件改为模板文件系统

---

## [0.4.0] - 2025-09-21

### Added

- **情节追踪系统** (`/plot-check`)：追踪情节节点、伏笔和冲突发展
- **时间线管理** (`/timeline`)：维护故事时间轴，确保时间逻辑一致
- **关系矩阵** (`/relations`)：管理角色关系和派系动态
- **世界观检查** (`/world-check`)：验证设定一致性，避免矛盾
- **综合追踪** (`/track`)：全方位查看创作状态
- **spec目录结构**：新增 `spec/tracking` 和 `spec/knowledge` 目录

---

## [0.3.7] - 2025-09-20

### Added

- **时间获取指导**：在命令模板中添加提示，指导 AI 使用 `date` 命令获取系统日期

### Changed

- **灵活的卷册管理**：章节现在会自动从 outline.md 解析卷册结构
- **动态章节数量**：支持从 outline.md 读取总章节数

### Fixed

- **日期生成错误**：修复了 AI 生成错误日期的问题

---

## [0.3.6] - 2025-01-20

### Fixed

- **目录命名问题**：修复了故事目录生成时名称为 `001-` 的问题
- **章节组织结构**：修复了章节按卷册结构生成的功能

---

## [0.3.5] - 2025-01-20

### Fixed

- **修复配置文件格式问题**：保留了命令文件中完整的 frontmatter 和 scripts 部分

---

## [0.3.4] - 之前版本

### Added

- 初始版本发布
- 支持 Claude、Cursor、Gemini、Windsurf、Roo Code 多种 AI 助手
- 提供了完整的小说创作工作流命令