# Novel Writer 项目分析文档索引

> **项目版本**: v0.20.0  
> **最后更新**: 2026-07-02  
> **文档数量**: 15 份

---

## 文档列表

### 📋 基础文档

| 编号 | 文档名称 | 内容概述 |
|------|---------|---------|
| [000](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/000_INDEX.md) | **INDEX.md** | 本索引文档，链接所有分析文档 |
| [001](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/001_项目分析摘要.md) | **项目分析摘要** | 项目整体分析，技术栈、目录结构、核心模块识别 |

### 🏗️ 架构与设计

| 编号 | 文档名称 | 内容概述 |
|------|---------|---------|
| [002](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/002_ARCHITECTURE.md) | **ARCHITECTURE.md** | 核心功能模块、模块间调用关系、数据流程图、状态管理 |
| [003](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/003_DATABASE_SCHEMA.md) | **DATABASE_SCHEMA.md** | 文件系统数据存储结构、核心数据文件定义、数据迁移机制 |
| [004](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/004_API_REFERENCE.md) | **API_REFERENCE.md** | CLI 命令、AI 斜杠命令、插件命令、外部 API 接口 |

### 🤖 AI 相关

| 编号 | 文档名称 | 内容概述 |
|------|---------|---------|
| [005](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/005_AI_PROMPTS.md) | **AI_PROMPTS.md** | AI 模型配置、提示词模板分类、上下文管理、参数配置、错误处理 |

### 🚀 运维与部署

| 编号 | 文档名称 | 内容概述 |
|------|---------|---------|
| [006](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/006_SETUP.md) | **SETUP.md** | 系统要求、依赖安装、环境变量配置、启动命令、Docker 部署 |
| [007](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/007_CHANGELOG.md) | **CHANGELOG.md** | 版本变更历史，按 Keep a Changelog 格式组织 |

### 🔧 运维支持

| 编号 | 文档名称 | 内容概述 |
|------|---------|---------|
| [008](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/008_TROUBLESHOOTING.md) | **TROUBLESHOOTING.md** | 常见问题排查指南，启动失败、AI 调用、文件操作等问题 |
| [009](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/009_BACKUP.md) | **BACKUP.md** | 备份策略、备份命令、恢复步骤、云同步方案 |

### 🔒 安全

| 编号 | 文档名称 | 内容概述 |
|------|---------|---------|
| [010](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/010_SECURITY.md) | **SECURITY.md** | 安全风险评估、环境变量管理、API Key 轮换、安全工具推荐 |

### 📈 规划与测试

| 编号 | 文档名称 | 内容概述 |
|------|---------|---------|
| [011](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/011_ROADMAP.md) | **ROADMAP.md** | 短期/中期/长期规划、想法池、版本里程碑 |
| [012](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/012_TESTING.md) | **TESTING.md** | 手动测试清单、边界条件测试、回归测试、自动化测试计划 |

### 📜 许可证

| 编号 | 文档名称 | 内容概述 |
|------|---------|---------|
| [013](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/013_LICENSE_DEPENDENCIES.md) | **LICENSE_DEPENDENCIES.md** | 依赖许可证清单、风险评估、兼容性矩阵、重新生成方法 |

### 📝 代码规范

| 编号 | 文档名称 | 内容概述 |
|------|---------|---------|
| [014](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/014_CODESTYLE.md) | **CODESTYLE.md** | 代码风格指南、格式化工具配置、EditorConfig 配置、ESLint 规则 |

### 🔌 插件开发

| 编号 | 文档名称 | 内容概述 |
|------|---------|---------|
| [015](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/015_PLUGIN_DEV_GUIDE.md) | **PLUGIN_DEV_GUIDE.md** | 插件开发指南、目录结构、配置格式、命令文件编写、调试方法 |

---

## 项目核心信息

### 技术栈

- **语言**: TypeScript / JavaScript (ESM)
- **框架**: Commander.js (CLI)
- **存储**: 文件系统（JSON/YAML/Markdown）
- **AI 平台**: Claude Code, Cursor, Gemini CLI, Windsurf, Roo Code, GitHub Copilot, Qwen Code, OpenCode, Codex CLI, Kilo Code, Auggie CLI, CodeBuddy, Amazon Q Developer

### 核心功能

1. **七步方法论**: constitution → specify → clarify → plan → tasks → write → analyze
2. **追踪管理**: plot-check, timeline, relations, world-check, track
3. **专家模式**: 剧情结构专家、人物塑造专家等
4. **插件系统**: translate, authentic-voice, book-analysis, genre-knowledge, stardust-dreams

### 目录结构

```
novel-writer-2/
├── src/                    # 核心源代码
│   ├── cli.ts              # CLI 命令入口
│   ├── plugins/            # 插件管理器
│   └── utils/              # 工具函数
├── plugins/                # 内置插件
│   ├── stardust-dreams/    # 星尘织梦 AI 插件
│   ├── translate/          # 翻译插件
│   └── ...
├── templates/              # 命令模板
├── stories/                # 生成的小说章节
├── spec/                   # 规格和追踪数据
│   ├── tracking/           # 追踪数据
│   └── knowledge/          # 知识库
└── .specify/               # 项目配置和脚本
    ├── memory/             # 写作记忆
    ├── scripts/            # 脚本文件
    └── templates/          # 模板文件
```

---

## 快速导航

| 场景 | 推荐文档 |
|------|---------|
| 新开发人员上手 | [001](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/001_项目分析摘要.md), [002](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/002_ARCHITECTURE.md), [006](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/006_SETUP.md) |
| 了解 AI 交互逻辑 | [005](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/005_AI_PROMPTS.md) |
| 排查问题 | [008](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/008_TROUBLESHOOTING.md) |
| 备份数据 | [009](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/009_BACKUP.md) |
| 安全审计 | [010](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/010_SECURITY.md) |
| 规划开发 | [011](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/011_ROADMAP.md) |
| 测试验证 | [012](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/012_TESTING.md) |
| 许可证合规 | [013](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/013_LICENSE_DEPENDENCIES.md) |
| 代码规范 | [014](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/014_CODESTYLE.md) |
| 插件开发 | [015](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/软件分析文档/015_PLUGIN_DEV_GUIDE.md) |

---

## 更新记录

| 日期 | 变更内容 |
|------|---------|
| 2026-07-01 | 初始版本，创建 001-007 文档 |
| 2026-07-02 | 创建 008-013 文档，添加索引文档 |