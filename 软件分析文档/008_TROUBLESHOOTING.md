# Troubleshooting Guide

> **注意**：本项目是一个 CLI 工具，不涉及传统服务器、数据库连接等问题。以下部分内容为通用模板，标注为 `[通用模板]` 的内容需要根据实际情况补充。

---

## 1. 启动失败类

### 1.1 项目初始化失败

**错误现象**：运行 `novel init` 命令后出现错误

**可能原因**：

| 原因 | 检查步骤 | 解决方案 |
|------|---------|---------|
| 项目目录已存在 | 检查目标目录是否已存在 | 删除目录或使用其他名称 |
| 未提供项目名称 | 检查命令是否包含项目名称 | 添加项目名称或使用 `--here` 参数 |
| 权限不足 | 检查当前用户对目标目录的写入权限 | 使用管理员权限运行或更改目录权限 |
| 构建产物缺失 | 检查 `dist/` 目录是否存在 | 运行 `npm run build` 和 `npm run build:commands` |

**代码中的错误处理**（[cli.ts](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/src/cli.ts#L170-L598)）：

```typescript
try {
  // 检查项目目录是否已存在
  if (await fs.pathExists(projectPath)) {
    spinner.fail(`项目目录 "${name}" 已存在`);
    process.exit(1);
  }
  
  // 检查构建产物
  const sourceDir = path.join(packageRoot, sourceMap[ai]);
  if (!await fs.pathExists(sourceDir)) {
    console.log(chalk.yellow(`警告: ${ai} 构建产物未找到，请运行 npm run build:commands`));
  }
} catch (error) {
  spinner.fail(chalk.red('项目初始化失败'));
  console.error(error);
  process.exit(1);
}
```

**排查命令**：

```bash
# 检查构建产物是否存在
ls dist/

# 重新构建
npm run build
npm run build:commands
```

### 1.2 依赖安装失败

**错误现象**：运行 `npm install` 时出现错误

**可能原因**：

| 原因 | 检查步骤 | 解决方案 |
|------|---------|---------|
| Node.js 版本不兼容 | 运行 `node --version` | 升级 Node.js 到 18.0.0+ |
| npm 版本问题 | 运行 `npm --version` | 更新 npm 到最新版本 |
| 网络问题 | 检查网络连接 | 使用代理或切换 npm 镜像 |
| Windows prepare 脚本失败 | 查看错误信息中是否包含 `set -euo pipefail` | 使用 `npm install --ignore-scripts` |
| 权限不足（Linux/macOS） | 查看错误信息中的权限错误 | 使用 `sudo npm install` |

**代码中的版本检查**（[cli.ts](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/src/cli.ts#L608-L637)）：

```typescript
const checks = [
  { name: 'Node.js', command: 'node --version', installed: false },
  // ...
];

checks.forEach(check => {
  try {
    execSync(check.command, { stdio: 'ignore' });
    check.installed = true;
    console.log(chalk.green('✓') + ` ${check.name} 已安装`);
  } catch {
    console.log(chalk.yellow('⚠') + ` ${check.name} 未安装`);
  }
});
```

**排查命令**：

```bash
# 检查 Node.js 版本
node --version

# 检查 npm 版本
npm --version

# 使用淘宝镜像
npm install --registry=https://registry.npmmirror.com

# Windows 跳过 prepare 脚本
npm install --ignore-scripts
```

### 1.3 Node/Python 版本不兼容

**错误现象**：运行 CLI 命令时出现版本相关错误

**可能原因**：

| 原因 | 检查步骤 | 解决方案 |
|------|---------|---------|
| Node.js 版本过低 | `node --version` | 升级到 18.0.0+ |
| ESM 模块不支持 | 查看错误信息 | Node.js 18+ 原生支持 ESM |
| Python 缺失（node-gyp） | 查看安装日志 | 安装 Python 3.6+ |

**package.json 中的版本要求**（[package.json](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/package.json#L54)）：

```json
{
  "engines": {
    "node": ">=18.0.0"
  }
}
```

**排查命令**：

```bash
# 检查 Node.js 版本
node --version

# 检查 Python 是否安装（仅用于某些原生模块）
python --version || python3 --version
```

### 1.4 环境变量缺失

**错误现象**：运行某些功能时出现 API Key 或配置错误

**可能原因**：

| 原因 | 检查步骤 | 解决方案 |
|------|---------|---------|
| STARDUST_API_KEY 缺失 | 检查 `.env` 文件或环境变量 | 设置环境变量 |
| STARDUST_API_URL 缺失 | 检查环境变量 | 使用默认值或设置自定义 URL |

**代码中的环境变量读取**（[api-client.js](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/plugins/stardust-dreams/lib/api-client.js#L8-L14)）：

```javascript
const API_BASE = process.env.STARDUST_API_URL || 'https://api.stardust-dreams.com';

export class StardustAPIClient {
  constructor() {
    this.baseUrl = API_BASE;
    this.apiKey = process.env.STARDUST_API_KEY || null;
  }
}
```

**排查命令**：

```bash
# 检查环境变量（Linux/macOS）
echo $STARDUST_API_KEY

# 检查环境变量（Windows PowerShell）
$env:STARDUST_API_KEY

# 设置环境变量（Linux/macOS）
export STARDUST_API_KEY=your_key_here

# 设置环境变量（Windows PowerShell）
$env:STARDUST_API_KEY="your_key_here"

# 创建 .env 文件
cat > .env << 'EOF'
STARDUST_API_KEY=your_key_here
STARDUST_API_URL=https://api.stardust-dreams.com
EOF
```

---

## 2. AI 调用类

### 2.1 API Key 无效或过期

**错误现象**：使用 stardust-dreams 插件时出现认证错误

**可能原因**：

| 原因 | 检查步骤 | 解决方案 |
|------|---------|---------|
| API Key 格式错误 | 检查 API Key 是否正确复制 | 重新复制正确的 API Key |
| API Key 已过期 | 联系服务提供商 | 申请新的 API Key |
| API Key 未设置 | 检查环境变量或配置文件 | 设置 `STARDUST_API_KEY` 环境变量 |

**代码中的错误处理**（[api-client.js](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/plugins/stardust-dreams/lib/api-client.js#L59-L61)）：

```javascript
if (!response?.result?.data?.success) {
  throw new Error(`无法获取会话 ${sessionId} 的加密 Prompt`);
}
```

**排查命令**：

```bash
# 验证 API Key 是否设置
echo $STARDUST_API_KEY

# 检查 API Key 长度（通常至少 32 字符）
echo ${#STARDUST_API_KEY}

# 尝试手动测试 API
curl -X POST https://api.stardust-dreams.com/api/trpc/form.getSession \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "test"}'
```

### 2.2 请求超时

**错误现象**：API 请求长时间无响应或超时

**可能原因**：

| 原因 | 检查步骤 | 解决方案 |
|------|---------|---------|
| 网络连接问题 | 检查网络连接和代理设置 | 检查网络或使用代理 |
| 服务器负载过高 | 等待一段时间后重试 | 稍后重试或联系服务提供商 |
| 请求超时时间过短 | [通用模板] 检查超时配置 | 增加超时时间 |

**代码中的错误处理**（[api-client.js](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/plugins/stardust-dreams/lib/api-client.js#L99-L116)）：

```javascript
try {
  const response = await fetch(url, fetchOptions);
  const data = await response.json();
  return data;
} catch (error) {
  if (error instanceof Error) {
    throw error;
  }
  throw new Error(`网络请求失败: ${error}`);
}
```

**排查命令**：

```bash
# 测试网络连接
ping api.stardust-dreams.com

# 测试 API 响应时间
curl -w "Response time: %{time_total}s\n" -o /dev/null -s https://api.stardust-dreams.com

# 检查代理设置
echo $HTTP_PROXY
echo $HTTPS_PROXY
```

### 2.3 配额不足

**错误现象**：收到 429 错误或类似的配额限制提示

**可能原因**：

| 原因 | 检查步骤 | 解决方案 |
|------|---------|---------|
| API 调用次数超限 | 检查响应中的 `Retry-After` 头 | 等待后重试 |
| 带宽/流量超限 | 查看服务提供商的配额信息 | 升级套餐或等待配额重置 |

**代码中的速率限制处理**（[api-client.js](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/plugins/stardust-dreams/lib/api-client.js#L104-L107)）：

```javascript
if (response.status === 429) {
  const retryAfter = response.headers.get('Retry-After');
  throw new Error(`请求过于频繁，请 ${retryAfter || '60'} 秒后重试`);
}
```

**排查命令**：

```bash
# 查看是否收到 429 错误
curl -v https://api.stardust-dreams.com/api/trpc/form.getSession

# 检查 Retry-After 头
curl -I https://api.stardust-dreams.com/api/trpc/form.getSession
```

### 2.4 返回内容被过滤

**错误现象**：AI 返回的内容不完整或被截断

**可能原因**：

| 原因 | 检查步骤 | 解决方案 |
|------|---------|---------|
| AI 助手内容限制 | 检查 AI 助手的输出限制 | 减少单次请求的内容量 |
| 提示词过长 | 检查提示词模板的长度 | 优化提示词，使用更简洁的指令 |
| 敏感内容过滤 | 检查内容是否包含敏感词汇 | 修改内容或调整提示词 |

**排查方法**：

1. 检查提示词模板的长度
2. 尝试缩短请求内容
3. 在 AI 助手中直接测试提示词

---

## 3. 数据库类

> **注意**：本项目不使用传统数据库，所有数据存储在本地文件系统中（JSON/YAML/Markdown 文件）。以下内容针对文件系统操作可能出现的问题。

### 3.1 文件读取失败

**错误现象**：AI 命令无法读取项目文件或配置

**可能原因**：

| 原因 | 检查步骤 | 解决方案 |
|------|---------|---------|
| 文件路径错误 | 检查文件是否存在于正确路径 | 确认文件路径或重新初始化项目 |
| 文件权限不足 | 检查文件的读写权限 | 修改文件权限 |
| 文件编码问题 | 检查文件编码格式 | 确保使用 UTF-8 编码 |

**代码中的文件读取**（[project.ts](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/src/utils/project.ts#L70-L83)）：

```typescript
try {
  const configContent = await fs.readFile(configPath, 'utf-8');
  const config = JSON.parse(configContent);
  return config;
} catch (error) {
  return null;
}
```

**排查命令**：

```bash
# 检查文件是否存在
ls -la .specify/config.json

# 检查文件权限
stat .specify/config.json

# 检查文件编码
file -I .specify/config.json
```

### 3.2 文件写入失败

**错误现象**：AI 命令无法保存内容到文件

**可能原因**：

| 原因 | 检查步骤 | 解决方案 |
|------|---------|---------|
| 目录不存在 | 检查目标目录是否存在 | 创建目录或重新初始化项目 |
| 磁盘空间不足 | 检查磁盘可用空间 | 清理磁盘空间 |
| 权限不足 | 检查目录的写入权限 | 修改目录权限 |

**代码中的错误处理**（[cli.ts](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/src/cli.ts#L594-L598)）：

```typescript
} catch (error) {
  spinner.fail(chalk.red('项目初始化失败'));
  console.error(error);
  process.exit(1);
}
```

**排查命令**：

```bash
# 检查磁盘空间
df -h  # Linux/macOS
dir C:\  # Windows

# 检查目录权限
ls -la stories/

# 尝试手动创建文件
echo "test" > stories/test.txt
```

### 3.3 JSON 解析错误

**错误现象**：配置文件或追踪文件无法解析

**可能原因**：

| 原因 | 检查步骤 | 解决方案 |
|------|---------|---------|
| JSON 格式错误 | 检查文件内容是否符合 JSON 规范 | 修复 JSON 语法错误 |
| 文件被损坏 | 检查文件内容是否完整 | 从备份恢复或重新创建文件 |
| 编码问题 | 检查文件是否使用正确编码 | 使用 UTF-8 重新保存文件 |

**排查命令**：

```bash
# 使用 Python 验证 JSON 格式
python -m json.tool .specify/config.json

# 使用 Node.js 验证 JSON 格式
node -e "JSON.parse(require('fs').readFileSync('.specify/config.json', 'utf-8'))"

# 检查文件内容
cat .specify/config.json
```

---

## 4. 插件类

### 4.1 插件安装失败

**错误现象**：运行 `novel plugins:add` 时出现错误

**可能原因**：

| 原因 | 检查步骤 | 解决方案 |
|------|---------|---------|
| 插件名称错误 | 检查插件名称是否正确 | 使用 `novel plugins` 查看可用插件 |
| 插件不存在 | 检查 `plugins/` 目录中是否有该插件 | 使用正确的插件名称 |
| 配置文件缺失 | 检查插件目录中是否有 `config.yaml` | 确认插件完整性 |
| 非项目目录 | 检查当前目录是否是有效的项目 | 使用 `novel init` 创建项目 |

**代码中的错误处理**（[cli.ts](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/src/cli.ts#L729-L737)）：

```typescript
if (!await fs.pathExists(builtinPluginPath)) {
  console.log(chalk.red(`❌ 插件 ${name} 未找到\n`));
  console.log(chalk.gray('可用插件:'));
  console.log(chalk.gray('  - translate (翻译出海插件)'));
  console.log(chalk.gray('  - authentic-voice (真实人声插件)'));
  console.log(chalk.gray('  - book-analysis (拆书分析插件)'));
  console.log(chalk.gray('  - genre-knowledge (类型知识库插件)'));
  process.exit(1);
}
```

**排查命令**：

```bash
# 查看可用插件
novel plugins

# 检查插件目录
ls plugins/

# 检查插件配置
cat plugins/translate/config.yaml
```

### 4.2 插件命令不生效

**错误现象**：安装插件后，AI 助手中无法使用插件命令

**可能原因**：

| 原因 | 检查步骤 | 解决方案 |
|------|---------|---------|
| 命令未注入 | 检查 AI 命令目录中是否有插件命令 | 重新安装插件 |
| AI 配置未检测 | 检查项目是否安装了对应的 AI 配置 | 使用 `novel init --ai <type>` 初始化 |
| 命令格式错误 | 检查命令文件格式是否正确 | 确认文件是 `.md` 或 `.toml` 格式 |

**代码中的命令注入**（[manager.ts](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/src/plugins/manager.ts#L222-L297)）：

```typescript
if (supportedAIs.claude) {
  const destPath = path.join(this.commandsDirs.claude, `${cmd.id}.md`)
  await fs.copy(sourcePath, destPath)
}
```

**排查命令**：

```bash
# 检查 Claude 命令目录
ls .claude/commands/

# 检查 Gemini 命令目录
ls .gemini/commands/

# 检查插件是否已安装
novel plugins:list
```

---

## 5. 环境检查命令

### 5.1 使用 `novel check` 检查环境

```bash
novel check
```

**输出示例**：

```
检查系统环境...

✓ Node.js 已安装
✓ Git 已安装
⚠ Claude CLI 未安装
⚠ Cursor 未安装
⚠ Gemini CLI 未安装

警告: 未检测到 AI 助手工具
请安装以下任一工具:
  • Claude: https://claude.ai
  • Cursor: https://cursor.sh
  • Gemini: https://gemini.google.com
```

---

## 6. 日志和调试

### 6.1 启用调试模式

```bash
# 设置 DEBUG 环境变量
export DEBUG=true  # Linux/macOS
$env:DEBUG="true"  # Windows PowerShell

# 运行命令
novel init my-novel
```

### 6.2 查看日志输出

项目使用统一的日志模块（[logger.ts](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/src/utils/logger.ts)）：

```typescript
export const logger = {
  info: (message: string, ...args: any[]) => {
    console.log(chalk.blue('ℹ'), message, ...args)
  },
  success: (message: string, ...args: any[]) => {
    console.log(chalk.green('✓'), message, ...args)
  },
  warn: (message: string, ...args: any[]) => {
    console.log(chalk.yellow('⚠'), message, ...args)
  },
  error: (message: string, ...args: any[]) => {
    console.error(chalk.red('✗'), message, ...args)
  },
  debug: (message: string, ...args: any[]) => {
    if (process.env.DEBUG) {
      console.log(chalk.gray('⚙'), message, ...args)
    }
  }
}
```

---

## 7. 常见问题速查表

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `项目目录 "xxx" 已存在` | 目标目录已存在 | 使用其他名称或删除目录 |
| `请提供项目名称或使用 --here 参数` | 未提供项目名称 | 添加名称或使用 `--here` |
| `当前目录不是 novel-writer 项目` | 不在项目目录中 | 使用 `novel init` 创建项目 |
| `插件 xxx 未找到` | 插件名称错误 | 使用正确的插件名称 |
| `构建产物未找到` | 未运行构建命令 | 运行 `npm run build:commands` |
| `Git 初始化失败` | Git 未安装或配置问题 | 安装 Git 或使用 `--no-git` |
| `请求过于频繁` | API 速率限制 | 等待后重试 |

---

## 8. 获取帮助

### 8.1 查看命令帮助

```bash
novel --help
novel init --help
novel plugins --help
novel upgrade --help
```

### 8.2 查看文档

```bash
# 查看安装指南
cat docs/installation.md

# 查看升级指南
cat docs/upgrade-guide.md

# 查看工作流程
cat docs/workflow.md
```

### 8.3 报告问题

如果遇到无法解决的问题，请提供以下信息：

1. 完整的错误信息
2. 操作系统和版本
3. Node.js 版本（`node --version`）
4. npm 版本（`npm --version`）
5. 执行的命令和参数
6. 项目目录结构（`ls -la`）

提交到 GitHub Issues：https://github.com/wordflowlab/novel-writer/issues