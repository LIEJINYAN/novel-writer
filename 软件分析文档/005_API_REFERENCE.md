# API_REFERENCE

## 1. 接口概述

> **重要说明**：本项目是一个 **CLI 工具 + AI 辅助创作系统**，**没有自建的 HTTP 服务器**，也**没有 REST API 路由**。项目的"接口"分为三个类别：

| 类别 | 说明 | 调用方式 |
|------|------|----------|
| **CLI 命令** | 终端命令，用于项目初始化、插件管理、升级 | 终端执行 `novel <command>` |
| **AI 斜杠命令** | AI 助手内部命令，用于小说创作 | AI 助手中输入 `/command` |
| **实时 API 调用** | stardust-dreams 插件调用的外部 API | HTTP 请求（仅该插件） |

---

## 2. CLI 命令

### 2.1 命令总览

| 命令 | 描述 | 参数 |
|------|------|------|
| `novel init` | 初始化新的小说项目 | `[name]`, `--here`, `--ai`, `--all`, `--method`, `--no-git`, `--with-experts`, `--plugins` |
| `novel check` | 检查系统环境和 AI 工具 | 无 |
| `novel plugins` | 显示插件管理帮助 | 无 |
| `novel plugins:list` | 列出已安装的插件 | 无 |
| `novel plugins:add` | 安装插件 | `<name>` |
| `novel plugins:remove` | 移除插件 | `<name>` |
| `novel upgrade` | 升级项目到最新版本 | `--ai`, `--all`, `-i`, `--commands`, `--scripts`, `--spec`, `--experts`, `--templates`, `--memory`, `-y`, `--no-backup`, `--dry-run` |

### 2.2 命令详细说明

#### `novel init` - 初始化项目

**功能**：创建新的小说项目目录结构，配置 AI 助手和写作方法

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `name` | string | 否 | - | 项目名称（使用 `--here` 时可选） |
| `--here` | flag | 否 | false | 在当前目录初始化 |
| `--ai <type>` | string | 否 | claude | AI 助手类型 |
| `--all` | flag | 否 | false | 为所有 AI 助手生成配置 |
| `--method <type>` | string | 否 | three-act | 写作方法 |
| `--no-git` | flag | 否 | false | 跳过 Git 初始化 |
| `--with-experts` | flag | 否 | false | 启用专家模式 |
| `--plugins <names>` | string | 否 | - | 预装插件（逗号分隔） |

**`--ai` 可选值**：
- `claude` - Claude Code
- `cursor` - Cursor
- `gemini` - Gemini CLI
- `windsurf` - Windsurf
- `roocode` - Roo Code
- `copilot` - GitHub Copilot
- `qwen` - Qwen Code
- `opencode` - OpenCode
- `codex` - Codex CLI
- `kilocode` - Kilo Code
- `auggie` - Auggie CLI
- `codebuddy` - CodeBuddy
- `q` - Amazon Q Developer

**`--method` 可选值**：
- `three-act` - 三幕结构
- `hero-journey` - 英雄之旅
- `story-circle` - 故事圈
- `seven-point` - 七点结构
- `pixar` - 皮克斯公式
- `snowflake` - 雪花十步

**示例**：

```bash
# 在当前目录初始化，使用默认设置
novel init --here

# 创建名为 my-story 的项目，指定 AI 和方法
novel init my-story --ai claude --method hero-journey

# 创建项目并安装翻译插件
novel init my-story --plugins translate,authentic-voice
```

**输出**：

```
╔═══════════════════════════════════════╗
║     📚  Novel Writer  📝              ║
║     AI 驱动的中文小说创作工具        ║
╚═══════════════════════════════════════╝

  v0.8.9

✓ 小说项目 "my-story" 创建成功！

接下来:
─────────────────────────────
  1. cd my-story - 进入项目目录
  2. 在 Claude Code 中打开项目
  3. 使用以下斜杠命令开始创作:

     📝 七步方法论:
     /constitution - 创建创作宪法，定义核心原则
     /specify      - 定义故事规格，明确要创造什么
     /clarify      - 澄清关键决策点，明确模糊之处
     /plan         - 制定技术方案，决定如何创作
     /tasks        - 分解执行任务，生成可执行清单
     /write        - AI 辅助写作章节内容
     /analyze      - 综合验证分析，确保质量一致

     📊 追踪管理命令:
     /plot-check  - 检查情节一致性
     /timeline    - 管理故事时间线
     /relations   - 追踪角色关系
     /world-check - 验证世界观设定
     /track       - 综合追踪与智能分析

推荐流程: constitution → specify → clarify → plan → tasks → write → analyze
```

---

#### `novel check` - 环境检查

**功能**：检查系统环境和已安装的 AI 工具

**参数**：无

**示例**：

```bash
novel check
```

**输出**：

```
检查系统环境...

✓ Node.js 已安装
✓ Git 已安装
✓ Claude CLI 已安装
✓ Cursor 已安装
⚠ Gemini CLI 未安装

环境检查通过！
```

---

#### `novel plugins:list` - 列出插件

**功能**：列出当前项目已安装的插件

**示例**：

```bash
novel plugins:list
```

**输出**：

```
📦 已安装的插件

项目: my-story
AI 配置: claude

  translate (v1.0.0)
    中英文翻译插件
    命令: /translate, /translate-chapter, /polish

  authentic-voice (v1.0.0)
    真实人声写作插件
    命令: /authentic-voice, /authenticity-audit
```

---

#### `novel plugins:add <name>` - 安装插件

**功能**：安装指定的插件

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 插件名称 |

**可用插件**：
- `translate` - 中英文翻译插件
- `authentic-voice` - 真实人声写作插件
- `book-analysis` - 拆书分析插件
- `genre-knowledge` - 类型知识库插件
- `luyao-style` - 路遥风格插件
- `shizhangyu-style` - 十章鱼风格插件
- `wangyu-style` - 忘语风格插件
- `stardust-dreams` - 星尘织梦API插件

**示例**：

```bash
novel plugins:add translate
```

---

#### `novel plugins:remove <name>` - 移除插件

**功能**：移除指定的插件

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 插件名称 |

**示例**：

```bash
novel plugins:remove translate
```

---

#### `novel upgrade` - 升级项目

**功能**：升级项目配置文件和命令到最新版本

**参数**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--ai <type>` | string | 所有已安装 | 指定要升级的 AI 配置 |
| `--all` | flag | false | 升级所有 AI 配置 |
| `-i, --interactive` | flag | false | 交互式选择更新内容 |
| `--commands` | flag | true | 更新命令文件 |
| `--scripts` | flag | true | 更新脚本文件 |
| `--spec` | flag | true | 更新写作规范和预设 |
| `--experts` | flag | false | 更新专家模式文件 |
| `--templates` | flag | false | 更新模板文件 |
| `--memory` | flag | false | 更新记忆文件 |
| `-y, --yes` | flag | false | 跳过确认提示 |
| `--no-backup` | flag | false | 跳过备份 |
| `--dry-run` | flag | false | 预览升级内容 |

**示例**：

```bash
# 升级所有内容（默认）
novel upgrade

# 仅更新命令文件
novel upgrade --commands

# 交互式选择更新内容
novel upgrade -i

# 预览升级内容，不实际修改
novel upgrade --dry-run
```

---

## 3. AI 斜杠命令

### 3.1 命令总览

> **说明**：斜杠命令在 AI 助手（如 Claude Code、Cursor、Gemini）内部使用，不是在终端中执行。

#### 核心方法论命令（七步法）

| 命令 | 描述 | 阶段 |
|------|------|------|
| `/constitution` | 创建创作宪法，定义核心原则 | 第一步 |
| `/specify` | 定义故事规格，明确要创造什么 | 第二步 |
| `/clarify` | 澄清关键决策点，明确模糊之处 | 第三步 |
| `/plan` | 制定技术方案，决定如何创作 | 第四步 |
| `/tasks` | 分解执行任务，生成可执行清单 | 第五步 |
| `/write` | AI 辅助写作章节内容 | 第六步 |
| `/analyze` | 综合验证分析，确保质量一致 | 第七步 |

#### 追踪管理命令

| 命令 | 描述 |
|------|------|
| `/track` | 综合追踪与智能分析 |
| `/track-init` | 初始化追踪文件 |
| `/plot-check` | 检查情节一致性 |
| `/timeline` | 管理故事时间线 |
| `/relations` | 追踪角色关系 |
| `/world-check` | 验证世界观设定 |
| `/checklist` | 检查清单 |

#### 专家模式命令

| 命令 | 描述 |
|------|------|
| `/expert` | 列出可用专家 |
| `/expert plot` | 剧情结构专家 |
| `/expert character` | 人物塑造专家 |
| `/expert style` | 风格把控专家 |
| `/expert world` | 世界观构建专家 |

### 3.2 命令详细说明

#### `/constitution` - 创作宪法

**功能**：定义小说的核心创作原则和风格指南

**输入**：自然语言描述作品特征

**输出**：创作宪法文档（Markdown）

**示例**：

```
/constitution 类型=奇幻，目标读者=成人，预计20万字，强调角色成长和世界观深度
```

**输出结构**：

```markdown
# 创作宪法

## 核心原则
- 真实性优先：角色行为必须符合性格设定
- 世界观一致性：魔法规则必须贯穿始终
- 节奏控制：每10章设置一个小高潮

## 风格指南
- 叙述视角：第三人称有限视角
- 语言风格：正式但生动，避免过于口语化
- 描写深度：注重心理描写和场景氛围

## 禁忌清单
- 避免突然的能力提升
- 避免角色行为前后矛盾
- 避免信息直接告知读者
```

---

#### `/specify` - 故事规格

**功能**：定义故事的核心要素和规格

**输出**：规格文档（specify.md）

---

#### `/clarify` - 决策澄清

**功能**：澄清故事中的关键决策点和模糊之处

**输出**：澄清报告和决策建议

---

#### `/plan` - 创作计划

**功能**：制定详细的创作技术方案

**输出**：计划文档（plan.md）

---

#### `/tasks` - 任务分解

**功能**：将创作任务分解为可执行的任务清单

**输出**：任务清单

---

#### `/write` - 章节写作

**功能**：AI 辅助写作章节内容

**参数**：

| 参数 | 说明 |
|------|------|
| `chapter` | 章节号（如：1, 2, 3） |
| `words` | 目标字数（默认：4000） |
| `continue` | 从上次中断处继续 |
| `style-check` | 检查风格一致性 |

**示例**：

```
/write chapter=1 words=5000 style-check
```

**输出**：章节内容（Markdown）

---

#### `/analyze` - 质量分析

**功能**：综合验证分析，确保内容质量和一致性

**输出**：分析报告和改进建议

---

#### `/track` - 综合追踪

**功能**：查看和分析所有追踪数据

**输出**：追踪数据汇总

---

#### `/plot-check` - 情节检查

**功能**：检查情节发展的一致性和逻辑性

**输出**：情节检查报告

---

#### `/timeline` - 时间线管理

**功能**：管理和查看故事时间线

**输出**：时间线视图

---

#### `/relations` - 关系追踪

**功能**：追踪角色间关系的发展

**输出**：关系图和变化历史

---

#### `/world-check` - 世界观验证

**功能**：验证世界观设定的一致性

**输出**：世界观检查报告

---

## 4. 插件命令

### 4.1 翻译插件（translate）

| 命令 | 描述 |
|------|------|
| `/translate` | 中英文翻译 |
| `/translate-chapter` | 翻译整个章节 |
| `/polish` | 英文润色 |

---

### 4.2 星尘织梦插件（stardust-dreams）

| 命令 | 描述 |
|------|------|
| `/stardust-auth` | 认证和登录 |
| `/stardust-session` | 管理会话 |
| `/stardust-list` | 列出可用表单 |
| `/stardust-use` | 使用指定表单的 Prompt |

---

### 4.3 拆书分析插件（book-analysis）

| 命令 | 描述 |
|------|------|
| `/book-analyze` | 分析书籍 |
| `/book-characters` | 分析人物 |
| `/book-formula` | 提取公式 |
| `/book-internalize` | 内化方法 |
| `/book-rhythm` | 分析节奏 |
| `/book-skeleton` | 提取骨架 |
| `/book-style` | 分析风格 |

---

### 4.4 类型知识库插件（genre-knowledge）

| 命令 | 描述 |
|------|------|
| `/clarify-enhance` | 增强澄清环节 |
| `/plan-enhance` | 增强计划环节 |
| `/write-enhance` | 增强写作环节 |

---

### 4.5 风格插件

#### 路遥风格（luyao-style）

| 命令 | 描述 |
|------|------|
| `/luyao-character` | 路遥式人物塑造 |
| `/luyao-dialogue` | 路遥式对话 |
| `/luyao-detail` | 路遥式细节描写 |
| `/luyao-style` | 路遥风格分析 |
| `/luyao-write` | 路遥风格写作 |

#### 十章鱼风格（shizhangyu-style）

| 命令 | 描述 |
|------|------|
| `/shizhangyu-character` | 人物分析 |
| `/shizhangyu-foreshadow` | 伏笔设计 |
| `/shizhangyu-plot` | 情节设计 |
| `/shizhangyu-style` | 风格分析 |
| `/shizhangyu-write` | 风格写作 |

#### 忘语风格（wangyu-style）

| 命令 | 描述 |
|------|------|
| `/wangyu-analyze` | 分析 |
| `/wangyu-enhance` | 增强 |
| `/wangyu-style` | 风格分析 |
| `/wangyu-write` | 风格写作 |

---

### 4.6 真实人声插件（authentic-voice）

| 命令 | 描述 |
|------|------|
| `/authentic-voice` | 真实人声写作 |
| `/authenticity-audit` | 真实性审计 |

---

## 5. 实时 API 调用

> **说明**：只有 stardust-dreams 插件会进行实时 HTTP API 调用，其他模块通过静态命令模板与 AI 助手交互。

### 5.1 API 基础信息

| 项目 | 值 |
|------|-----|
| **基础 URL** | `https://api.stardust-dreams.com`（可通过 `STARDUST_API_URL` 环境变量覆盖） |
| **认证方式** | API Key（通过 `STARDUST_API_KEY` 环境变量配置） |
| **内容类型** | `application/json` |

### 5.2 端点列表

| HTTP 方法 | 路径 | 功能 | 文件 |
|-----------|------|------|------|
| POST | `/api/trpc/form.getSession` | 获取会话信息 | [api-client.js](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/plugins/stardust-dreams/lib/api-client.js) |
| POST | `/api/trpc/form.getPrompt` | 获取加密 Prompt | [api-client.js](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/plugins/stardust-dreams/lib/api-client.js) |

### 5.3 端点详细说明

#### POST /api/trpc/form.getSession

**功能**：获取会话信息

**请求体**：

```json
{
  "json": {
    "sessionId": "string"
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `json.sessionId` | string | 是 | 会话 ID |

**成功响应**（200）：

```json
{
  "result": {
    "data": {
      "success": true,
      "data": {
        "sessionId": "session_abc123",
        "formId": "form_xyz789",
        "formName": "小说创作表单",
        "createdAt": "2024-01-01T10:00:00Z"
      }
    }
  }
}
```

**失败响应**（400/404）：

```json
{
  "result": {
    "data": {
      "success": false,
      "error": "会话不存在或已过期"
    }
  }
}
```

---

#### POST /api/trpc/form.getPrompt

**功能**：获取加密的 Prompt（核心功能）

**请求体**：

```json
{
  "json": {
    "sessionId": "string",
    "apiKey": "string"
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `json.sessionId` | string | 是 | 会话 ID |
| `json.apiKey` | string | 是 | API Key |

**成功响应**（200）：

```json
{
  "result": {
    "data": {
      "success": true,
      "data": {
        "sessionId": "session_abc123",
        "formId": "form_xyz789",
        "formName": "小说创作表单",
        "parameters": {},
        "encryptedPrompt": "base64_encoded_string",
        "iv": "base64_encoded_iv",
        "authTag": "base64_encoded_auth_tag",
        "sessionKey": "base64_encoded_key",
        "expiresAt": "2024-01-01T11:00:00Z"
      }
    }
  }
}
```

**响应字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `sessionId` | string | 会话 ID |
| `formId` | string | 表单 ID |
| `formName` | string | 表单名称 |
| `parameters` | object | 表单参数 |
| `encryptedPrompt` | string | AES-256-GCM 加密的 Prompt |
| `iv` | string | 初始化向量（base64） |
| `authTag` | string | 认证标签（base64） |
| `sessionKey` | string | 解密密钥（base64） |
| `expiresAt` | string | 过期时间（ISO 8601） |

**失败响应**（400/401/404）：

```json
{
  "result": {
    "data": {
      "success": false,
      "error": "无法获取会话的加密 Prompt"
    }
  }
}
```

---

### 5.4 错误处理

**速率限制**（429）：

```json
{
  "error": "请求过于频繁，请 60 秒后重试"
}
```

**网络错误**：

```json
{
  "error": "网络请求失败: [详细错误信息]"
}
```

---

## 6. 认证方式

### 6.1 CLI 认证

> **说明**：CLI 工具本身不需要认证，但某些插件需要。

### 6.2 stardust-dreams 插件认证

**环境变量**：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `STARDUST_API_URL` | API 地址 | `https://api.stardust-dreams.com` |
| `STARDUST_API_KEY` | API Key | 无（必须配置） |

**配置方式**：

```bash
# 方式1：环境变量
export STARDUST_API_KEY="your_api_key_here"

# 方式2：.env 文件
echo "STARDUST_API_KEY=your_api_key_here" > .env
```

**安全机制**：
- API Key 通过 HTTPS 请求体传输
- 加密 Prompt 使用 AES-256-GCM 加密
- 解密密钥仅在内存中使用，不持久化存储
- 认证信息加密存储在 `~/.novel/stardust/` 目录

---

## 7. 错误码

### 7.1 CLI 错误码

| 码 | 说明 |
|----|------|
| 0 | 成功 |
| 1 | 一般错误 |

### 7.2 HTTP 错误码

| 码 | 说明 | 处理建议 |
|----|------|----------|
| 400 | 参数错误 | 检查请求参数 |
| 401 | 认证失败 | 验证 API Key |
| 404 | 资源不存在 | 验证会话 ID |
| 429 | 速率限制 | 等待后重试 |
| 500 | 服务器错误 | 联系支持 |

---

## 8. 执行流程示例

### 8.1 完整创作流程

```
用户终端执行：
    novel init my-story --ai claude --method hero-journey
        ↓
项目创建成功，进入项目目录
        ↓
用户在 Claude Code 中打开项目
        ↓
AI 助手内部执行斜杠命令：
    /constitution → 创建创作宪法
    /specify → 定义故事规格
    /clarify → 澄清关键决策
    /plan → 制定创作计划
    /tasks → 分解任务清单
    /write chapter=1 → 写作第一章
    /analyze → 质量分析
        ↓
所有数据保存到本地文件：
    .specify/config.json
    spec/tracking/plot-tracker.json
    spec/tracking/character-state.json
    stories/chapter-1.md
```

### 8.2 stardust-dreams 插件调用流程

```
用户在 AI 助手中执行：
    /stardust-use session_abc123
        ↓
插件执行 API 调用：
    POST /api/trpc/form.getSession
        ↓
    POST /api/trpc/form.getPrompt
        ↓
获取加密数据并解密：
    AES-256-GCM 解密
        ↓
将解密后的 Prompt 注入 AI 对话
        ↓
AI 使用 Prompt 进行创作
        ↓
更新追踪文件
```

---

## 9. 总结

| 接口类型 | 数量 | 调用方式 | 认证 |
|----------|------|----------|------|
| CLI 命令 | 7 | 终端 `novel <command>` | 无需 |
| AI 斜杠命令 | 14 | AI 助手 `/command` | 无需 |
| 插件命令 | 25+ | AI 助手 `/command` | 部分需要 |
| 实时 API | 2 | HTTP POST | API Key |

**核心设计特点**：
1. **无自建服务器**：所有交互通过 CLI 和 AI 助手进行
2. **静态命令模板**：AI 命令通过 Markdown/TOML 文件定义，无需运行时 API
3. **插件化扩展**：插件可添加新的命令和 API 调用
4. **文件优先**：所有数据存储在本地文件中