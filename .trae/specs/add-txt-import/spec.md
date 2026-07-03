# TXT/MD 导入功能 Spec

## Why
已实现全本/分卷/单章导出为 TXT/MD，但缺少反向操作——用户无法从外部 .txt 或 .md 文件导入内容到当前项目。

## What Changes
- **单章导入**: 右键编辑器标签页或章节节点 → 从文件导入，替换当前章节内容
- **分卷导入**: 右键分卷节点 → 从文件夹导入，按文件名排序批量创建章节
- **全本导入**: 文件 → 导入 → 从 TXT/MD 导入，自动按章节分割或用户指定分割方式

## Impact
- Affected specs: add-export-features
- Affected code: `services/import_service.py`（新增方法）, `services/chapter_service.py`, `ui/main_window.py`（菜单项/右键菜单）

## ADDED Requirements

### Requirement: 单章导入
The system SHALL import content from a single .txt or .md file into a chapter.

#### Scenario: 替换当前章节
- **WHEN** 用户右键编辑器标签页 → "从文件导入" 或 右键章节节点 → "从文件导入"
- **THEN** 弹出文件选择对话框，过滤 .txt/.md
- **THEN** 文件内容替换当前章节内容
- **THEN** 编辑器即时刷新，字数统计更新

### Requirement: 分卷导入
The system SHALL import multiple files from a directory into a volume as chapters.

#### Scenario: 从文件夹导入章节
- **WHEN** 用户右键分卷节点 → "从文件夹导入章节"
- **THEN** 弹出目录选择对话框
- **THEN** 递归搜索目录下所有 .txt/.md 文件，按文件名排序
- **THEN** 每个文件创建为一个新章节，文件名（不含扩展名）作为标题
- **THEN** 导入完成后弹出报告：成功 N 个，跳过 M 个

### Requirement: 全本导入
The system SHALL import a single TXT/MD file and split it into multiple chapters.

#### Scenario: 自动分割导入
- **WHEN** 用户点击"文件 → 导入 → 从 TXT/MD 导入"
- **THEN** 弹出文件选择对话框，过滤 .txt/.md
- **THEN** 系统自动检测分割方式：
  1. 优先按 `## 第X章` 或 `# 第X章` 分割
  2. 其次按 `=== 第X章 ===` 分割
  3. 最后按连续两个换行符 `\n\n\n` 分割
- **THEN** 弹出预览对话框，显示分割结果（每段预览 + 合并/拆分选项）
- **THEN** 确认后批量创建章节到新分卷

#### Scenario: 手动分割导入
- **WHEN** 自动分割结果不理想
- **THEN** 用户在预览对话框中可手动调整分割点
- **THEN** 确认后按用户指定的分割创建章节

## Out of Scope
- EPUB/PDF 导入（格式复杂，需解析）
- 格式转换（导入时自动移除 HTML/Markdown 标记）
- 章节合并导入（当前只支持分割导入）

## MODIFIED Requirements
无

## REMOVED Requirements
无
