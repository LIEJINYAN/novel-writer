# SETUP - 环境快速搭建指南

## 1. 系统要求

### 1.1 硬件要求
- **内存**：至少 4GB RAM（推荐 8GB+）
- **磁盘空间**：至少 500MB 可用空间

### 1.2 软件要求

| 软件 | 最低版本 | 推荐版本 | 说明 |
|------|---------|---------|------|
| **Node.js** | 18.0.0 | 20.x LTS | 核心运行环境 |
| **npm** | 8.0.0 | 10.x | 包管理器 |
| **Git** | 2.0.0 | 最新版 | 版本控制（可选但推荐） |

### 1.3 操作系统支持

| 操作系统 | 状态 | 说明 |
|---------|------|------|
| **Windows** | ✅ 支持 | PowerShell 5.x 或 PowerShell 7+ |
| **macOS** | ✅ 支持 | macOS 10.15+ |
| **Linux** | ✅ 支持 | Ubuntu 18.04+, CentOS 8+ |

### 1.4 AI 助手（必需）

项目本身不直接调用 AI API，需要配合以下 AI 助手使用：

| AI 助手 | 推荐度 | 配置格式 |
|---------|--------|---------|
| **Claude Code** | ⭐⭐⭐ | Markdown (完整 frontmatter) |
| **Cursor** | ⭐⭐⭐ | 纯 Markdown |
| **Gemini CLI** | ⭐⭐⭐ | TOML |
| **其他** | ⭐⭐ | Markdown |

---

## 2. 克隆仓库

```bash
# HTTPS
git clone https://github.com/wordflowlab/novel-writer.git
cd novel-writer

# SSH（如果配置了 SSH）
git clone git@github.com:wordflowlab/novel-writer.git
cd novel-writer
```

---

## 3. 安装依赖

### 3.1 标准安装（Linux/macOS）

```bash
npm install
```

### 3.2 Windows 安装（跳过不兼容的 prepare 脚本）

```powershell
npm install --ignore-scripts
```

> **说明**：默认的 `prepare` 脚本包含 `build:commands`，该脚本使用 `bash` 和 `set -euo pipefail`，在 Windows 上无法直接运行。

### 3.3 安装依赖后手动构建（Windows）

```powershell
# 构建 TypeScript 代码
npm run build

# 生成命令模板（Windows 用户请见下文替代方案）
# 注意：build:commands 使用 bash 脚本，Windows 需要 WSL 或 Git Bash
```

### 3.4 Windows 命令模板生成方案

**方案 A：使用 WSL（推荐）**

```powershell
# 进入 WSL
wsl

# 在 WSL 中执行
cd /mnt/i/AI写小说/AI小说软件开发/novel-writer-2
npm run build:commands
```

**方案 B：使用 Git Bash**

```bash
# 打开 Git Bash，进入项目目录
npm run build:commands
```

**方案 C：手动构建（最小化）**

如果只需要 CLI 功能（不生成命令模板）：

```powershell
npm run build
```

---

## 4. 环境变量配置

### 4.1 必需环境变量

| 变量名 | 说明 | 默认值 | 是否必需 |
|--------|------|--------|---------|
| `STARDUST_API_KEY` | 星尘织梦 API 密钥 | 无 | 否（仅 stardust-dreams 插件需要） |
| `STARDUST_API_URL` | 星尘织梦 API 地址 | `https://api.stardust-dreams.com` | 否 |

### 4.2 .env.example 模板

创建 `.env` 文件：

```env
# 星尘织梦 API 配置（可选）
STARDUST_API_KEY=your_api_key_here
STARDUST_API_URL=https://api.stardust-dreams.com

# 开发环境配置
NODE_ENV=development
```

### 4.3 加载环境变量

项目使用 `dotenv` 库自动加载 `.env` 文件：

```typescript
// src/cli.ts 中已集成
import dotenv from 'dotenv';
dotenv.config();
```

---

## 5. 数据库初始化

> **注意**：本项目是 CLI 工具，不使用传统数据库。所有数据存储在本地文件系统中（JSON/YAML/Markdown 文件）。

### 5.1 数据文件结构

```
项目目录/
├── .specify/
│   ├── config.json          # 项目配置
│   ├── memory/              # 创作记忆
│   │   └── constitution.md  # 创作宪法
│   └── scripts/             # 支持脚本
├── spec/
│   ├── tracking/            # 追踪数据
│   │   ├── plot-tracker.json
│   │   ├── character-state.json
│   │   └── relationships.json
│   ├── knowledge/           # 知识库
│   └── presets/             # 预设配置
└── stories/
    └── 001-故事名/
        ├── specification.md # 故事规格
        ├── creative-plan.md # 创作计划
        ├── tasks.md         # 任务清单
        └── content/         # 章节内容
```

### 5.2 初始化项目命令

```bash
# 创建新项目
node dist/cli.js init my-novel

# 指定 AI 平台
node dist/cli.js init my-novel --ai claude
node dist/cli.js init my-novel --ai gemini
node dist/cli.js init my-novel --ai cursor

# 在当前目录初始化
node dist/cli.js init --here
```

---

## 6. 启动开发服务器

> **注意**：本项目是 CLI 工具，没有前端或后端服务器。开发时直接运行 CLI 命令即可。

### 6.1 开发模式（热更新）

```bash
npm run dev
```

示例：

```bash
# 使用 tsx 运行开发模式
npm run dev -- init my-novel --ai claude
```

### 6.2 生产模式

```bash
# 构建项目
npm run build

# 运行 CLI
node dist/cli.js

# 查看帮助
node dist/cli.js --help

# 查看版本
node dist/cli.js --version
```

### 6.3 全局安装（推荐）

```bash
# 构建并安装
npm run build
npm install -g .

# 直接使用 novel 命令
novel --help
novel init my-novel
novel check
```

---

## 7. Docker 部署

> **注意**：项目当前没有 Dockerfile。以下是参考配置。

### 7.1 Dockerfile（参考）

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --ignore-scripts

COPY . .
RUN npm run build

# 全局安装
RUN npm install -g .

# 设置工作目录为项目目录
WORKDIR /workspace

CMD ["novel", "--help"]
```

### 7.2 docker-compose.yml（参考）

```yaml
version: '3.8'

services:
  novel-writer:
    build: .
    volumes:
      - ./projects:/workspace
    working_dir: /workspace
    command: novel --help
```

### 7.3 构建和运行（参考）

```bash
# 构建镜像
docker build -t novel-writer .

# 运行容器
docker run -it --rm -v "$(pwd)/projects:/workspace" novel-writer

# 使用 CLI 命令
docker run -it --rm -v "$(pwd)/projects:/workspace" novel-writer novel init my-novel
```

---

## 8. 完整安装脚本

### 8.1 Linux/macOS 一键安装

```bash
#!/bin/bash

# 1. 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js >= 18.0.0"
    exit 1
fi

# 2. 检查版本
node_version=$(node --version | sed 's/v//')
if [ "$(printf '%s\n' "18.0.0" "$node_version" | sort -V | head -n1)" != "18.0.0" ]; then
    echo "❌ Node.js 版本太低，需要 >= 18.0.0，当前版本: $node_version"
    exit 1
fi

# 3. 克隆仓库
git clone https://github.com/wordflowlab/novel-writer.git
cd novel-writer

# 4. 安装依赖
echo "📦 安装依赖..."
npm install

# 5. 构建项目
echo "🔨 构建项目..."
npm run build

# 6. 全局安装
echo "🚀 全局安装..."
npm install -g .

# 7. 验证
echo "✅ 安装完成！"
novel --version
novel --help
```

### 8.2 Windows PowerShell 一键安装

```powershell
# 1. 检查 Node.js
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Error "Node.js 未安装，请先安装 Node.js >= 18.0.0"
    exit 1
}

# 2. 检查版本
$nodeVersion = (node --version).Trim().Replace('v', '')
if ([version]$nodeVersion -lt [version]"18.0.0") {
    Write-Error "Node.js 版本太低，需要 >= 18.0.0，当前版本: $nodeVersion"
    exit 1
}

# 3. 克隆仓库
git clone https://github.com/wordflowlab/novel-writer.git
cd novel-writer

# 4. 安装依赖（跳过 prepare 脚本）
Write-Host "📦 安装依赖..."
npm install --ignore-scripts

# 5. 构建项目
Write-Host "🔨 构建项目..."
npm run build

# 6. 全局安装
Write-Host "🚀 全局安装..."
npm install -g .

# 7. 验证
Write-Host "✅ 安装完成！"
novel --version
novel --help
```

---

## 9. 常见问题

### 9.1 npm install 失败

**问题**：`prepare` 脚本在 Windows 上失败

**解决方案**：

```powershell
npm install --ignore-scripts
npm run build
```

### 9.2 命令模板生成失败

**问题**：`build:commands` 使用 bash 脚本

**解决方案**：使用 WSL 或 Git Bash 执行

### 9.3 权限错误（Linux/macOS）

**问题**：全局安装时权限不足

**解决方案**：

```bash
sudo npm install -g .
```

### 9.4 命令找不到

**问题**：`novel` 命令不在 PATH 中

**解决方案**：

```bash
# 查看 npm 全局路径
npm config get prefix

# 添加到 PATH（临时）
export PATH="$PATH:$(npm config get prefix)/bin"

# 添加到 PATH（永久，根据 shell 类型）
# Bash
echo 'export PATH="$PATH:$(npm config get prefix)/bin"' >> ~/.bashrc

# Zsh
echo 'export PATH="$PATH:$(npm config get prefix)/bin"' >> ~/.zshrc
```

### 9.5 PowerShell 执行策略错误

**问题**：Windows PowerShell 禁止运行脚本

**解决方案**：

```powershell
# 以管理员身份运行 PowerShell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 10. 快速验证清单

完成安装后，执行以下命令验证：

```bash
# 1. 检查版本
novel --version          # 应显示 v0.20.0 或更高

# 2. 检查帮助
novel --help             # 应显示 CLI 帮助信息

# 3. 检查环境
novel check              # 应显示环境检查结果

# 4. 创建测试项目
novel init test-project --ai claude --no-git

# 5. 进入项目目录
cd test-project

# 6. 验证项目结构
ls -la                   # 应包含 .specify/, spec/, stories/ 等目录
```

---

## 11. 技术栈总结

| 组件 | 技术 | 版本 |
|------|------|------|
| 运行时 | Node.js | >= 18.0.0 |
| 包管理 | npm | 8.x+ |
| 语言 | TypeScript | 5.3.x |
| CLI 框架 | Commander.js | 12.x |
| 格式化 | chalk | 5.x |
| 文件操作 | fs-extra | 11.x |
| YAML 解析 | js-yaml | 4.x |
| 进度条 | ora | 8.x |
| 交互式输入 | inquirer | 9.x |
| 命令模板 | Markdown/TOML | - |

---

## 12. 资源链接

- **项目仓库**：https://github.com/wordflowlab/novel-writer
- **安装指南**：[docs/installation.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/docs/installation.md)
- **工作流程**：[docs/workflow.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/docs/workflow.md)
- **命令详解**：[docs/commands.md](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/docs/commands.md)