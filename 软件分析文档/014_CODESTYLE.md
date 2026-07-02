# Code Style Guide

## Overview

本项目是一个 TypeScript/JavaScript CLI 工具，基于 ES Module 模块系统。通过分析现有代码，推荐以下代码规范。

## Recommended Tools

### Prettier
用于代码格式化，确保团队成员之间代码风格一致。

### ESLint
用于代码质量检查，捕获潜在的语法错误和代码规范问题。

### EditorConfig
用于统一不同编辑器之间的基础格式设置。

## EditorConfig Configuration

以下是推荐的 `.editorconfig` 配置：

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.{ts,js}]
indent_style = space
indent_size = 2
tab_width = 2

[*.{json,yaml,yml}]
indent_style = space
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[*.sh]
end_of_line = lf

[*.ps1]
end_of_line = crlf
```

## Prettier Configuration

在项目根目录创建 `.prettierrc`：

```json
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "all",
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "arrowParens": "always",
  "bracketSpacing": true,
  "jsxSingleQuote": false,
  "quoteProps": "as-needed"
}
```

### 配置说明

| 选项 | 值 | 说明 |
|------|-----|------|
| `semi` | `true` | 行尾添加分号 |
| `singleQuote` | `true` | 使用单引号 |
| `trailingComma` | `all` | 多行时添加尾随逗号 |
| `printWidth` | `100` | 行宽限制 |
| `tabWidth` | `2` | 缩进宽度 |
| `useTabs` | `false` | 使用空格缩进 |
| `arrowParens` | `always` | 箭头函数参数始终使用括号 |

## ESLint Configuration

在项目根目录创建 `.eslintrc.json`：

```json
{
  "env": {
    "node": true,
    "es2022": true
  },
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "prettier"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaVersion": "latest",
    "sourceType": "module"
  },
  "plugins": [
    "@typescript-eslint"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "@typescript-eslint/explicit-function-return-type": "off",
    "@typescript-eslint/explicit-module-boundary-types": "off",
    "@typescript-eslint/no-explicit-any": "warn"
  }
}
```

## Script Commands

在 `package.json` 中添加以下脚本：

```json
{
  "scripts": {
    "format": "prettier --write \"src/**/*.ts\" \"plugins/**/*.js\"",
    "format:check": "prettier --check \"src/**/*.ts\" \"plugins/**/*.js\"",
    "lint": "eslint \"src/**/*.ts\"",
    "lint:fix": "eslint \"src/**/*.ts\" --fix",
    "code:check": "npm run format:check && npm run lint"
  }
}
```

## How to Run

### 安装依赖

```bash
npm install --save-dev prettier eslint @typescript-eslint/eslint-plugin @typescript-eslint/parser eslint-config-prettier
```

### 一键格式化整个项目

```bash
npm run format
```

### 检查格式问题（不修改）

```bash
npm run format:check
```

### 运行代码检查

```bash
npm run lint
```

### 自动修复代码检查问题

```bash
npm run lint:fix
```

### 完整代码检查（格式化 + lint）

```bash
npm run code:check
```

## Code Style Rules

### 缩进
- 使用 **2 个空格**进行缩进
- 不使用 Tab 键

### 引号
- 字符串使用**单引号** `'`
- JSX 属性使用**双引号** `"`
- 模板字符串使用反引号 `` ` ``

### 分号
- **行尾添加分号**

### 命名规范
- **变量/函数**：`camelCase`
  ```typescript
  const projectPath = '/path/to/project';
  function getProjectInfo() {}
  ```

- **接口/类型/类**：`PascalCase`
  ```typescript
  interface ProjectInfo {}
  type ConfigOptions = {};
  class PluginManager {}
  ```

- **常量**：`UPPER_SNAKE_CASE`
  ```typescript
  const AI_CONFIGS = [];
  const MAX_RETRIES = 3;
  ```

- **私有属性/方法**：前缀 `_`
  ```typescript
  private _pluginsDir: string;
  private _loadConfig() {}
  ```

### 箭头函数
- 参数始终使用括号
  ```typescript
  // ✅ 正确
  const add = (a: number, b: number) => a + b;
  
  // ✅ 正确（即使只有一个参数）
  const double = (x: number) => x * 2;
  ```

### 尾随逗号
- 多行数组/对象/函数参数末尾添加尾随逗号
  ```typescript
  const config = {
    name: 'novel',
    type: 'novel',
    ai: 'claude',
  };
  
  const list = [
    'item1',
    'item2',
    'item3',
  ];
  ```

### 空行
- 函数之间空一行
- 类的方法之间空一行
- 逻辑块之间空一行

### 注释
- 函数/方法使用 JSDoc 风格注释
- 复杂逻辑添加单行注释
- 保持注释与代码同步

## Editor Setup

### VS Code

安装以下扩展：
- [Prettier - Code formatter](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode)
- [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint)
- [EditorConfig for VS Code](https://marketplace.visualstudio.com/items?itemName=EditorConfig.EditorConfig)

在 `.vscode/settings.json` 中配置：

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "[markdown]": {
    "editor.formatOnSave": false
  }
}
```

## CI/CD Integration

在 GitHub Actions 中添加代码风格检查：

```yaml
name: Code Style Check

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Use Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 18
      - run: npm ci
      - run: npm run code:check
```

## Migration Notes

现有代码存在一些风格不一致的地方，建议逐步迁移：

1. **分号**：`logger.ts` 和 `manager.ts` 缺少行尾分号，需添加
2. **引号**：`cli.ts` 和 `version.ts` 使用双引号，建议统一为单引号
3. **尾随逗号**：部分对象和数组缺少尾随逗号，建议添加

迁移时可以使用 `npm run format` 和 `npm run lint:fix` 自动修复大部分问题。
