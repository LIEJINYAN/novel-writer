# Plugin Development Guide

## Overview

Novel Writer 采用插件化架构，允许开发者扩展核心功能。插件系统支持：

- **命令扩展**：添加自定义 AI 斜杠命令
- **专家系统**：注册专业写作专家
- **模板系统**：提供预设写作模板
- **知识库**：扩展类型知识和写作规则
- **代码逻辑**：通过 JavaScript/TypeScript 实现复杂功能

## Plugin Structure

### Standard Directory Layout

```
plugins/
└── your-plugin-name/           # 插件目录（使用小写短横线命名）
    ├── config.yaml             # 必需：插件配置文件
    ├── README.md               # 推荐：插件说明文档
    ├── commands/               # 可选：Markdown 格式命令文件
    │   └── your-command.md
    ├── commands-gemini/        # 可选：Gemini TOML 格式命令文件
    │   └── your-command.toml
    ├── experts/                # 可选：专家模式文件
    │   └── your-expert.md
    ├── templates/              # 可选：模板文件（JSON/YAML/MD）
    │   └── template.json
    ├── memory/                 # 可选：写作记忆文件
    │   └── memory.md
    ├── knowledge/              # 可选：知识库文件
    │   └── knowledge.md
    ├── docs/                   # 可选：详细文档
    │   └── guide.md
    └── lib/                    # 可选：JavaScript/TypeScript 代码
        └── api-client.js
```

### Required Files

| 文件 | 说明 |
|------|------|
| `config.yaml` | 插件配置文件，必需 |
| `commands/` | 命令文件目录（至少包含一个命令文件） |

### Optional Files

| 目录 | 说明 |
|------|------|
| `commands-gemini/` | Gemini 专用 TOML 命令文件 |
| `experts/` | 专家模式文件 |
| `templates/` | 写作模板文件 |
| `memory/` | 写作记忆文件 |
| `knowledge/` | 类型知识库文件 |
| `docs/` | 插件详细文档 |
| `lib/` | JavaScript/TypeScript 业务逻辑代码 |
| `cache/` | 缓存目录（用于临时数据） |

## Configuration File (config.yaml)

### Basic Structure

```yaml
name: your-plugin-name
version: 1.0.0
description: 插件功能描述
type: feature  # feature | expert | workflow
displayName: 显示名称
author: 作者名称
homepage: https://your-website.com
```

### Fields Reference

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 插件内部名称，小写短横线分隔 |
| `version` | string | ✅ | 语义化版本号（SemVer） |
| `description` | string | ✅ | 插件功能描述 |
| `type` | string | ✅ | 插件类型：`feature`（功能型）、`expert`（专家型）、`workflow`（工作流型） |
| `displayName` | string | ❌ | 友好显示名称 |
| `author` | string | ❌ | 作者名称 |
| `homepage` | string | ❌ | 插件主页或文档链接 |
| `commands` | array | ❌ | 命令列表 |
| `experts` | array | ❌ | 专家列表 |
| `dependencies` | object | ❌ | 依赖配置 |
| `installation` | object | ❌ | 安装配置 |
| `api` | object | ❌ | API 配置（用于外部服务集成） |
| `security` | object | ❌ | 安全配置 |

### Commands Configuration

```yaml
commands:
  - id: command-id
    name: 命令名称
    description: 命令功能描述
    file: commands/command-file.md
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 命令唯一标识，决定斜杠命令名称（如 `/command-id`） |
| `name` | string | ❌ | 命令友好名称 |
| `description` | string | ✅ | 命令功能描述，显示在命令列表中 |
| `file` | string | ✅ | 命令文件路径（相对于插件根目录） |

### Experts Configuration

```yaml
experts:
  - id: expert-id
    name: 专家名称
    title: 专家头衔
    description: 专家描述
    file: experts/expert-file.md
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 专家唯一标识 |
| `name` | string | ❌ | 专家友好名称 |
| `title` | string | ✅ | 专家头衔（如"翻译专家"） |
| `description` | string | ✅ | 专家能力描述 |
| `file` | string | ✅ | 专家文件路径 |

### Dependencies Configuration

```yaml
dependencies:
  core: ">=0.5.0"
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `core` | string | 核心版本要求，使用语义化版本范围 |

### Installation Configuration

```yaml
installation:
  message: |
    ✅ 插件安装成功！

    可用命令：
    - /command-id - 功能说明

    专家模式：
    - 使用 /expert expert-id 激活专家
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `message` | string | 安装成功后显示的提示消息（支持多行文本） |

### API Configuration（可选）

用于集成外部服务的插件：

```yaml
api:
  endpoint: https://api.example.com
  version: v1
```

### Security Configuration（可选）

```yaml
security:
  encryption: AES-256-GCM
  tokenStorage: encrypted-local
  sessionTimeout: 900
  memoryOnly: true
```

## Command Files

### Markdown Format (Claude/Cursor/Windsurf/Roo Code)

命令文件使用 Markdown 格式，包含 YAML frontmatter：

```markdown
---
description: 命令功能描述
tags: [tag1, tag2]
category: 分类名称
---

# 命令标题

命令的详细说明和使用指南...

## 使用方法

说明如何使用此命令...

## 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| arg1 | string | 参数说明 |

## 示例

```
/command-id 参数值
```

## 输出格式

描述命令的输出格式...
```

### TOML Format (Gemini)

Gemini 使用 TOML 格式，可手动创建或由系统自动转换：

```toml
description = "命令功能描述"

prompt = """
# 命令标题

命令的详细说明...

用户输入：{{args}}
"""
```

### Auto-conversion

如果不提供 TOML 文件，系统会自动从 Markdown 转换：
1. 提取 YAML frontmatter 中的 `description`
2. 移除 frontmatter，保留正文内容
3. 添加 `用户输入：{{args}}` 作为参数占位符

## Expert Files

专家文件使用 Markdown 格式，定义专家的角色和能力：

```markdown
# 专家头衔

## 角色定义

详细描述专家的角色和背景...

## 核心能力

- 能力一
- 能力二
- 能力三

## 使用场景

描述何时应该调用此专家...

## 工作流程

专家的工作步骤和方法...

## 输出标准

描述专家输出的格式和质量要求...
```

## JavaScript Library（可选）

对于需要复杂逻辑的插件，可以在 `lib/` 目录中放置 JavaScript 代码。

### Example: API Client

```javascript
export class YourAPIClient {
  constructor() {
    this.baseUrl = process.env.YOUR_API_URL || 'https://api.example.com';
    this.apiKey = process.env.YOUR_API_KEY || null;
  }

  async request(endpoint, options = {}) {
    const url = new URL(endpoint, this.baseUrl);
    
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }

    return response.json();
  }
}
```

### Environment Variables

插件可以使用环境变量，建议在 `README.md` 中说明：

```
YOUR_API_URL - API 服务地址
YOUR_API_KEY - API 访问密钥
```

## Plugin Types

### Feature Type

提供特定功能的插件，如翻译、风格检测等。

**示例**：`translate`、`authentic-voice`

### Expert Type

提供专业写作指导的插件，专注于特定领域。

**示例**：`luyao-style`、`shizhangyu-style`

### Workflow Type

提供完整工作流程的插件，包含多个相关命令。

**示例**：`book-analysis`

## Development Workflow

### Step 1: Create Plugin Directory

```bash
mkdir -p plugins/your-plugin-name/{commands,experts}
cd plugins/your-plugin-name
```

### Step 2: Create config.yaml

```bash
touch config.yaml
```

### Step 3: Create Command Files

```bash
touch commands/your-command.md
```

### Step 4: Test Installation

在项目根目录运行：

```bash
# 使用开发模式测试
npm run dev -- plugins:add your-plugin-name

# 或使用构建后的版本
npm run build
novel plugins:add your-plugin-name
```

### Step 5: Verify Installation

```bash
npm run dev -- plugins:list
```

### Step 6: Debug Commands

1. 在 AI 助手中打开项目
2. 使用 `/command-id` 测试命令
3. 检查命令是否正确注入到 AI 目录

## Loading Mechanism

插件加载流程：

```
1. 扫描 plugins/ 目录
   ↓
2. 查找包含 config.yaml 的子目录
   ↓
3. 读取并验证配置文件
   ↓
4. 检查核心版本依赖
   ↓
5. 注入命令到 AI 平台目录
   ↓
6. 注册专家到 experts/plugins/ 目录
   ↓
7. 显示安装成功消息
```

### Supported AI Platforms

| 平台 | 命令目录 | 格式 |
|------|---------|------|
| Claude | `.claude/commands/` | Markdown (.md) |
| Cursor | `.cursor/commands/` | Markdown (.md) |
| Gemini | `.gemini/commands/` | TOML (.toml) |
| Windsurf | `.windsurf/workflows/` | Markdown (.md) |
| Roo Code | `.roo/commands/` | Markdown (.md) |

## Best Practices

### Naming Conventions

- **插件名称**：小写，短横线分隔（`your-plugin-name`）
- **命令 ID**：小写，短横线分隔（`your-command`）
- **专家 ID**：小写，短横线分隔（`your-expert`）
- **文件名**：与命令/专家 ID 一致

### Configuration Tips

1. **必填字段**：确保 `name`、`version`、`description`、`type` 已填写
2. **命令描述**：清晰简洁，便于用户理解
3. **版本规范**：使用语义化版本（Major.Minor.Patch）

### Command Writing Tips

1. **清晰的结构**：使用标准 Markdown 结构
2. **参数说明**：明确列出所有参数及其用途
3. **示例代码**：提供完整的使用示例
4. **输出格式**：说明命令的预期输出

### Security Considerations

1. **敏感信息**：不要在代码或配置中硬编码密钥、密码等敏感信息
2. **环境变量**：使用环境变量管理敏感配置
3. **用户数据**：妥善处理用户数据，遵守隐私政策

## Debugging

### Logging

插件管理器提供日志输出：

```typescript
import { logger } from '../utils/logger.js';

logger.info('信息日志');
logger.success('成功日志');
logger.warn('警告日志');
logger.error('错误日志');
logger.debug('调试日志');
```

### Common Issues

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 插件未加载 | `config.yaml` 缺失或格式错误 | 检查配置文件 |
| 命令未注入 | 命令文件路径错误 | 检查 `file` 字段路径 |
| Gemini 命令不工作 | TOML 格式错误 | 检查 TOML 文件语法 |
| 依赖检查失败 | 核心版本不满足 | 更新核心版本或降低依赖要求 |

## Publishing

### Package Structure

确保插件目录包含：

- `config.yaml` - 必需配置
- `commands/` - 至少一个命令文件
- `README.md` - 插件说明文档
- 可选：`commands-gemini/`、`experts/`、`templates/`

### Distribution

目前插件通过以下方式分发：

1. **内置插件**：随项目源码一起发布
2. **本地安装**：从本地路径安装

> 远程插件仓库功能正在开发中...

## Example Plugin

### Complete Example

```yaml
# config.yaml
name: weather-plugin
version: 1.0.0
description: 天气查询插件 - 获取实时天气信息用于场景描写
type: feature
displayName: 天气助手
author: Novel Writer Team
homepage: https://github.com/wordflowlab/novel-writer

commands:
  - id: weather
    name: 查询天气
    description: 获取指定城市的实时天气信息
    file: commands/weather.md

experts:
  - id: weather-describer
    title: 天气描写专家
    description: 帮助用生动的语言描写天气场景
    file: experts/weather-describer.md

dependencies:
  core: ">=0.5.0"

installation:
  message: |
    ✅ 天气插件安装成功！

    可用命令：
    - /weather [城市] - 查询指定城市天气

    专家模式：
    - 使用 /expert weather-describer 获取天气描写指导

    环境变量：
    - OPENWEATHER_API_KEY - OpenWeatherMap API 密钥
```

### Command File Example

```markdown
---
description: 获取指定城市的实时天气信息
tags: [weather, scene]
category: 辅助工具
---

# 天气查询

获取指定城市的实时天气信息，帮助你在小说中描写真实的天气场景。

## 使用方法

```
/weather 北京
/weather 上海 --detailed
```

## 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| 城市 | string | 城市名称（中文或拼音） |
| --detailed | flag | 显示详细天气信息 |

## 返回内容

- 当前温度
- 天气状况（晴、多云、雨等）
- 风力和风向
- 湿度
- 天气描写建议

## 示例输出

```
🌤️ 北京天气
温度：25°C
天气：晴
风力：东北风 3级
湿度：45%

📝 写作建议：
阳光明媚的午后，微风拂面，正是适合户外场景描写的好天气...
```
```

## References

- [Plugin Manager](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/src/plugins/manager.ts) - 插件管理器源码
- [translate Plugin](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/plugins/translate) - 翻译插件示例
- [stardust-dreams Plugin](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/plugins/stardust-dreams) - 外部 API 集成示例
- [book-analysis Plugin](file:///i:/AI写小说/AI小说软件开发/novel-writer-2/plugins/book-analysis) - 工作流插件示例
