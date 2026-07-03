# 导入导出功能 Spec

## Why
当前应用无法从原版 TypeScript 项目导入数据，也无法导出为可分享的格式（TXT/MD/EPUB/PDF）。用户无法迁移已有项目，也无法发布或备份作品。

## What Changes
- **从原版导入项目**: 解析原版目录结构（`.specify/config.json` + `stories/` + `spec/`），导入到当前 SQLite 数据库
- **导出为原版格式**: 将当前项目数据导出为与原版兼容的目录结构
- **全本导出 TXT/MD**: 合并所有章节，生成单个 .txt 或 .md 文件
- **全本导出 EPUB/PDF**: 生成电子书和 PDF 文件（含封面、目录）
- **单章/分卷导出**: 右键菜单导出单个章节或整卷为 .txt/.md

## Impact
- Affected specs: phase1-core, phase2-editor-system
- Affected code: `services/export_service.py`（新增）, `services/import_service.py`（新增）, `main_window.py`, `ui/dialogs/`（新增导出对话框）, `requirements.txt`（新增依赖）
- **BREAKING**: 无

## ADDED Requirements

### Requirement: 从原版导入项目
The system SHALL import projects from the original TypeScript v0.20.0 format.

#### Scenario: 导入原版项目
- **WHEN** 用户点击"文件 → 导入 → 从原版导入"
- **THEN** 弹出目录选择对话框，选择原版项目根目录
- **THEN** 系统解析 `.specify/config.json` 读取项目名称/类型/方法
- **THEN** 导入 `stories/` 目录下的章节文件为 Chapter 记录
- **THEN** 导入 `spec/tracking/` 下的角色/情节/关系数据
- **THEN** 导入完成后打开项目

#### Scenario: 导入失败
- **WHEN** 选择的目录不是有效的原版项目
- **THEN** 显示错误提示"所选目录不是有效的项目"
- **WHEN** 导入过程中发生文件读取错误
- **THEN** 显示错误详情并回滚已导入的数据

### Requirement: 导出为原版格式
The system SHALL export the current project to the original directory structure for backward compatibility.

#### Scenario: 导出为原版格式
- **WHEN** 用户点击"文件 → 导出 → 导出为原版格式"
- **THEN** 弹出目录选择对话框，选择导出目标目录
- **THEN** 生成 `.specify/config.json` + `stories/`（每章一个 .md） + `spec/tracking/` + `spec/knowledge/`
- **THEN** 导出完成后显示"导出完成"

### Requirement: 全本导出 TXT/MD
The system SHALL export the entire novel as a single TXT or MD file.

#### Scenario: 导出全本 TXT
- **WHEN** 用户点击"文件 → 导出 → 全本导出 TXT"
- **THEN** 弹出文件保存对话框，选择 .txt 路径
- **THEN** 按分卷/章节顺序合并所有内容，添加分隔标题
- **THEN** 生成文件并显示"导出完成"

#### Scenario: 导出全本 MD
- **WHEN** 用户点击"文件 → 导出 → 全本导出 Markdown"
- **THEN** 弹出文件保存对话框，选择 .md 路径
- **THEN** 按分卷/章节顺序合并，章节标题使用 `##` 级别
- **THEN** 生成文件并显示"导出完成"

### Requirement: 全本导出 EPUB/PDF
The system SHALL export the entire novel as EPUB or PDF with cover and table of contents.

#### Scenario: 导出 EPUB
- **WHEN** 用户点击"文件 → 导出 → 全本导出 EPUB"
- **THEN** 弹出导出设置对话框（填写书名、作者、封面图片可选）
- **THEN** 生成 EPUB 文件（含封面页、目录、各章节）
- **THEN** 生成完成后打开文件位置

#### Scenario: 导出 PDF
- **WHEN** 用户点击"文件 → 导出 → 全本导出 PDF"
- **THEN** 弹出导出设置对话框（书名、作者、字体大小、页边距）
- **THEN** 生成 PDF 文件
- **THEN** 生成完成后打开文件位置

### Requirement: 单章/分卷导出
The system SHALL export individual chapters or volumes as TXT/MD.

#### Scenario: 导出单章
- **WHEN** 用户在项目树右键章节 → "导出为 TXT" 或 "导出为 MD"
- **THEN** 弹出文件保存对话框
- **THEN** 只导出一个章节的内容

#### Scenario: 导出分卷
- **WHEN** 用户在项目树右键分卷 → "导出为 TXT" 或 "导出为 MD"
- **THEN** 弹出文件保存对话框
- **THEN** 合并该分卷下所有章节内容导出

## MODIFIED Requirements
无

## REMOVED Requirements
无
