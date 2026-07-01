# PROJECT OVERVIEW

## 1. 项目名称和简介

### 项目名称
**Novel Writer**

### 一句话简介
AI 驱动的中文小说创作工具 —— 基于结构化工作流的智能写作助手，支持多 AI 平台集成和多种写作方法论。

---

## 2. 完整技术栈清单

### 核心技术

| 分类 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 语言 | TypeScript | ^5.3.3 | 核心开发语言，类型安全 |
| 运行时 | Node.js | >=18.0.0 | 执行环境 |
| 包管理 | npm | - | 依赖管理工具 |

### CLI 框架

| 分类 | 技术 | 版本 | 说明 |
|------|------|------|------|
| CLI框架 | Commander.js | ^12.0.0 | 命令行界面框架 |
| 交互式UI | Inquirer.js | ^9.2.12 | 交互式选择组件 |
| 终端美化 | chalk | ^5.3.0 | 彩色终端输出 |
| 终端动画 | ora | ^8.0.1 | Loading 动画效果 |

### 文件与配置处理

| 分类 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 文件操作 | fs-extra | ^11.2.0 | 增强版文件系统操作 |
| YAML解析 | js-yaml | ^4.1.0 | YAML 配置文件解析 |
| 环境变量 | dotenv | ^16.3.1 | 环境变量管理 |
| 路径匹配 | glob | ^10.3.10 | 文件路径匹配 |

### 开发工具

| 分类 | 技术 | 版本 | 说明 |
|------|------|------|------|
| TypeScript运行 | tsx | ^4.7.0 | TypeScript 即时编译运行 |
| 构建工具 | tsc | ^5.3.3 | TypeScript 编译器 |

### AI 平台支持

| 平台 | 命令格式 | 说明 |
|------|----------|------|
| Claude Code | Markdown | Anthropic 旗下 AI 助手 |
| Cursor | Markdown | VS Code 原生 AI 编辑器 |
| Gemini CLI | TOML | Google 旗下 AI 助手 |
| Windsurf | Markdown | AI 工作流平台 |
| Roo Code | Markdown | AI 编程助手 |
| GitHub Copilot | prompt.md | GitHub AI 助手 |
| Qwen Code | TOML | 阿里通义千问 |
| OpenCode | Markdown | 字节跳动 AI 助手 |
| Codex CLI | Markdown | Codex 命令行工具 |
| Kilo Code | Markdown | AI 编程助手 |
| Auggie CLI | Markdown | AI 开发助手 |
| CodeBuddy | Markdown | AI 编程助手 |
| Amazon Q | Markdown | AWS AI 助手 |

### 不适用项

> **重要说明**：本项目是纯 CLI 工具，以下技术栈**不适用**：

| 分类 | 状态 | 说明 |
|------|------|------|
| 前端框架 | 不适用 | 无 Web 前端界面 |
| 后端框架 | 不适用 | 无 HTTP 服务器 |
| 数据库 | 不适用 | 数据以 JSON/YAML 文件形式存储 |
| ORM | 不适用 | 无数据库操作 |
| 对象存储 | 不适用 | 无文件上传存储需求 |

---

## 3. 项目目录树

```
novel-writer-2/
├── .github/                    # GitHub 配置
│   └── copilot-instructions.md # Copilot 指令配置
├── docs/                       # 项目文档
│   ├── prd/                    # 产品需求文档
│   ├── tech/                   # 技术文档
│   └── writing/                # 写作指南
├── experts/                    # 内置专家系统
│   └── core/                   # 核心专家（角色/情节/风格/世界观）
├── memory/                     # 记忆文件（写作宪法、个人文风）
├── plugins/                    # 插件目录（8个内置插件）
│   ├── authentic-voice/        # 真实人声写作插件
│   ├── book-analysis/          # 拆书分析插件
│   ├── genre-knowledge/        # 类型知识库插件
│   ├── luyao-style/            # 路遥风格插件
│   ├── shizhangyu-style/       # 十章鱼风格插件
│   ├── stardust-dreams/        # 星尘织梦API插件（唯一实时API调用）
│   ├── translate/              # 翻译出海插件
│   └── wangyu-style/           # 忘语风格插件
├── scripts/                    # 核心脚本（Bash + PowerShell）
│   ├── bash/                   # Linux/macOS 脚本
│   ├── build/                  # 构建脚本
│   └── powershell/             # Windows 脚本
├── spec/                       # 写作规范与预设
│   ├── checklists/             # 检查清单
│   ├── knowledge/              # 知识库（反AI检测、文风指南等）
│   ├── presets/                # 写作方法预设模板
│   └── tracking/               # 追踪数据模板
├── src/                        # TypeScript 源码
│   ├── plugins/                # 插件管理模块
│   │   └── manager.ts          # 插件管理器
│   ├── utils/                  # 工具函数
│   │   ├── interactive.ts      # 交互式选择工具
│   │   ├── logger.ts           # 日志工具
│   │   └── project.ts          # 项目管理工具
│   ├── ai-interface.ts         # AI 接口层（智能推荐、方法转换）
│   ├── cli.ts                  # CLI 入口（所有命令定义）
│   ├── hybrid-method.ts        # 混合方法支持（多方法组合）
│   ├── method-advisor.ts       # 方法推荐系统（评分算法）
│   ├── method-converter.ts     # 方法转换工具（结构映射）
│   └── version.ts              # 版本管理（统一版本号）
├── stories/                    # 示例故事
├── templates/                  # 模板文件（命令、知识库、追踪）
├── package.json                # 项目配置
├── tsconfig.json               # TypeScript 配置
└── bun.lock                    # Bun 锁定文件
```

---

## 4. 如何启动项目

### 4.1 环境要求

- Node.js >= 18.0.0
- npm 或 bun
- Git（可选，用于版本控制）

### 4.2 安装依赖

```bash
# 标准安装（Linux/macOS）
npm install

# Windows 安装（需跳过 prepare 脚本，因为 build:commands 是 bash 脚本）
npm install --ignore-scripts
```

### 4.3 构建项目

```bash
# 编译 TypeScript（所有平台通用）
npx tsc

# 生成 AI 命令文件（仅 Linux/macOS，Windows 不支持）
npm run build:commands
```

### 4.4 运行 CLI

```bash
# 开发模式（使用 tsx 实时编译）
npm run dev -- --help

# 生产模式（使用编译后的 JavaScript）
node dist/cli.js --help

# 创建新小说项目
node dist/cli.js init my-story

# 检查环境
node dist/cli.js check
```

### 4.5 Windows 注意事项

> **重要提示**：`build:commands` 脚本是 bash 脚本，在 Windows 环境下会失败（`set -euo pipefail` 不被 PowerShell 支持）。
>
> **解决方案**：
> 1. 使用 `npm install --ignore-scripts` 跳过 prepare 脚本
> 2. 使用 `npx tsc` 单独编译 TypeScript
> 3. 如需生成 AI 命令文件，可使用 WSL（Windows Subsystem for Linux）或 Git Bash

### 4.6 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `STARDUST_API_URL` | 星尘织梦 API 地址 | `https://api.stardust-dreams.com` |
| `STARDUST_API_KEY` | 星尘织梦 API Key | 无（需用户配置） |
| `DEBUG` | 开启调试模式 | 无（设置后显示 debug 日志） |

---

## 5. 项目依赖的外部服务

### 5.1 实时 API 服务（仅 stardust-dreams 插件）

| 服务 | API 端点 | 用途 | 文件 |
|------|----------|------|------|
| 星尘织梦 | `/api/trpc/form.getSession` | 获取会话信息 | `plugins/stardust-dreams/lib/api-client.js` |
| 星尘织梦 | `/api/trpc/form.getPrompt` | 获取加密 Prompt | `plugins/stardust-dreams/lib/api-client.js` |

### 5.2 AI 助手平台（运行时依赖）

> **说明**：以下 AI 平台不是通过 API 调用，而是通过**静态命令模板**集成。用户需要在本地安装对应的 AI 助手工具，然后在 AI 助手内部使用 `/xxx` 斜杠命令。

| 平台 | 工具名称 | 安装方式 |
|------|----------|----------|
| Claude Code | claude | `npm install -g @anthropic-ai/claude` |
| Cursor | cursor | 下载安装包：https://cursor.sh |
| Gemini CLI | gemini | `npm install -g @google/gemini-cli` |
| GitHub Copilot | VS Code 插件 | VS Code 扩展商店安装 |

### 5.3 文件存储

| 类型 | 说明 |
|------|------|
| 本地文件系统 | 所有数据（故事、追踪、配置）均以 JSON/YAML/Markdown 文件形式存储在本地 |
| 用户主目录 | 认证信息加密存储在 `~/.novel/stardust/` 目录（仅 stardust-dreams 插件） |

### 5.4 网络依赖

| 依赖 | 用途 |
|------|------|
| 互联网连接 | 安装 npm 依赖、下载 AI 助手工具、stardust-dreams 插件调用远程 API |
| Git | 项目初始化时可选初始化 Git 仓库 |

---

## 6. 架构说明

### 6.1 核心工作流程

```
用户启动 → CLI命令 → 项目初始化 → AI助手打开项目 → 斜杠命令创作 → 脚本执行 → 追踪更新 → 质量审计
```

### 6.2 两种 AI 集成模式

| 模式 | 说明 | 示例 |
|------|------|------|
| **静态命令模板** | 通过命令文件（Markdown/TOML）定义指令，由 AI 助手解析执行 | `/write`、`/plan` 等斜杠命令 |
| **实时 API 调用** | 通过 HTTP 请求获取加密 Prompt，在内存中解密使用 | stardust-dreams 插件 |

### 6.3 无数据库设计

项目采用**文件优先**的存储策略：
- 所有数据以 JSON/YAML/Markdown 格式存储
- 无需数据库服务，开箱即用
- 便于版本控制和备份
- 适合单机创作场景