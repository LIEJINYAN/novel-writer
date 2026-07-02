# License Dependencies Report

> **项目版本**: v0.20.0  
> **最后更新**: 2026-07-02  
> **生成方式**: 手动生成，基于 package.json 和公开开源许可证信息

---

## 1. 项目许可证

| 项目 | 许可证 | 说明 |
|------|--------|------|
| Novel Writer | **MIT** | 项目自身使用 MIT 许可证 |

---

## 2. 直接依赖许可证清单

### 2.1 运行时依赖 (dependencies)

| 序号 | 依赖名称 | 版本范围 | 许可证 | 许可证类型 | 风险等级 |
|------|---------|---------|--------|-----------|---------|
| 1 | `@commander-js/extra-typings` | ^12.0.0 | **MIT** | 宽松许可证 | 🟢 安全 |
| 2 | `chalk` | ^5.3.0 | **MIT** | 宽松许可证 | 🟢 安全 |
| 3 | `dotenv` | ^16.3.1 | **BSD-2-Clause** | 宽松许可证 | 🟢 安全 |
| 4 | `fs-extra` | ^11.2.0 | **MIT** | 宽松许可证 | 🟢 安全 |
| 5 | `glob` | ^10.3.10 | **ISC** | 宽松许可证（MIT 等效） | 🟢 安全 |
| 6 | `inquirer` | ^9.2.12 | **MIT** | 宽松许可证 | 🟢 安全 |
| 7 | `js-yaml` | ^4.1.0 | **MIT** | 宽松许可证 | 🟢 安全 |
| 8 | `ora` | ^8.0.1 | **MIT** | 宽松许可证 | 🟢 安全 |

### 2.2 开发依赖 (devDependencies)

| 序号 | 依赖名称 | 版本范围 | 许可证 | 许可证类型 | 风险等级 |
|------|---------|---------|--------|-----------|---------|
| 9 | `@types/fs-extra` | ^11.0.4 | **MIT** | 宽松许可证 | 🟢 安全 |
| 10 | `@types/inquirer` | ^9.0.9 | **MIT** | 宽松许可证 | 🟢 安全 |
| 11 | `@types/js-yaml` | ^4.0.9 | **MIT** | 宽松许可证 | 🟢 安全 |
| 12 | `@types/jsonfile` | ^6.1.4 | **MIT** | 宽松许可证 | 🟢 安全 |
| 13 | `@types/node` | ^20.10.0 | **MIT** | 宽松许可证 | 🟢 安全 |
| 14 | `@types/through` | ^0.0.33 | **MIT** | 宽松许可证 | 🟢 安全 |
| 15 | `tsx` | ^4.7.0 | **MIT** | 宽松许可证 | 🟢 安全 |
| 16 | `typescript` | ^5.3.3 | **Apache-2.0** | 宽松许可证（含专利授权） | 🟢 安全 |

---

## 3. 许可证类型说明

### 3.1 宽松许可证（Safe）

| 许可证 | 特点 | 兼容性 |
|--------|------|--------|
| **MIT** | 最宽松的开源许可证之一，允许几乎任何用途，只需保留版权声明 | 与所有许可证兼容，可用于商业软件 |
| **ISC** | 功能上与 MIT 等效，文本更简洁 | 与所有许可证兼容，可用于商业软件 |
| **BSD-2-Clause** | 宽松许可证，要求保留版权声明和许可证文本 | 与所有许可证兼容，可用于商业软件 |
| **Apache-2.0** | 宽松许可证，包含专利授权条款 | 与所有许可证兼容，可用于商业软件 |

### 3.2 传染性许可证（Viral）

> **本项目中不存在此类许可证依赖**

| 许可证 | 特点 | 兼容性 | 风险 |
|--------|------|--------|------|
| **GPL-2.0** | 强 copyleft，衍生作品必须同样使用 GPL-2.0 | 不兼容商业软件 | 🔴 高风险 |
| **GPL-3.0** | 强 copyleft，禁止 Tivoization | 不兼容商业软件 | 🔴 高风险 |
| **LGPL-2.1/3.0** | 弱 copyleft，只要求修改的库文件开源 | 部分兼容 | 🟡 中风险 |
| **AGPL-3.0** | 强 copyleft，网络服务也需开源 | 不兼容商业软件 | 🔴 高风险 |

---

## 4. 风险评估总结

### 4.1 许可证风险

```
┌─────────────────────────────────────────────────────────────┐
│ 许可证风险评估                                              │
├─────────────────────────────────────────────────────────────┤
│ 传染性许可证 (GPL/LGPL/AGPL):           0/16 = 0%          │
│ 宽松许可证 (MIT/ISC/BSD/Apache):       16/16 = 100%        │
│ 未知/无许可证:                          0/16 = 0%          │
├─────────────────────────────────────────────────────────────┤
│ 总体风险等级: 🟢 安全                                       │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 评估结论

✅ **所有直接依赖均使用宽松许可证**，无传染性许可证风险  
✅ **项目自身使用 MIT 许可证**，与所有依赖许可证兼容  
✅ **可安全用于商业软件**，无需担心许可证兼容性问题  

---

## 5. 许可证兼容性矩阵

| 依赖许可证 | MIT (项目) | Apache-2.0 | BSD-2-Clause | ISC |
|-----------|-----------|------------|--------------|-----|
| **MIT** | ✅ | ✅ | ✅ | ✅ |
| **ISC** | ✅ | ✅ | ✅ | ✅ |
| **BSD-2-Clause** | ✅ | ✅ | ✅ | ✅ |
| **Apache-2.0** | ✅ | ✅ | ✅ | ✅ |

---

## 6. 重新生成此清单

### 6.1 手动检查步骤

```bash
# 1. 查看 package.json 中的依赖
cat package.json | jq '.dependencies, .devDependencies'

# 2. 检查每个依赖的许可证（使用 npm view）
npm view chalk license
npm view dotenv license
npm view fs-extra license
npm view inquirer license
npm view js-yaml license
npm view ora license
npm view typescript license

# 3. 检查完整的许可证树（包括间接依赖）
npm ls --json | jq '.. | .license?' | sort | uniq
```

### 6.2 使用工具检查

```bash
# 安装 license-checker 工具
npm install -g license-checker

# 生成完整的许可证报告
license-checker --production --csv --out licenses.csv

# 或者使用更现代的工具
npx license-report --output=html --file=licenses.html
```

### 6.3 GitHub Actions 自动化检查（推荐）

在 `.github/workflows/license-check.yml` 中添加：

```yaml
name: License Check

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  license-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
      - run: npm install
      - run: npx license-checker --production --failOn GPL --failOn LGPL --failOn AGPL
```

---

## 7. 补充指令

> **请为每个依赖项从公开源查询许可证类型（若无法查询，标注'未知'）**

如需验证或更新许可证信息，可以运行以下命令：

```bash
# 批量查询所有依赖的许可证
npm list --depth=0 --json | jq -r '.dependencies | to_entries[] | "\(.key)@\(.value.version): \(.value.license)"'
```

---

## 8. 第三方服务许可证

本项目使用的外部 API 服务：

| 服务 | 许可证 | 说明 |
|------|--------|------|
| Stardust Dreams API | 专有 | 星尘织梦插件使用的外部 API，需单独授权 |

---

## 9. 更新记录

| 日期 | 变更内容 |
|------|---------|
| 2026-07-02 | 初始版本，基于 package.json v0.20.0 生成 |