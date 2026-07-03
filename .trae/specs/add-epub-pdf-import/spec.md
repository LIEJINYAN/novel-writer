# EPUB/PDF 全本导入功能 Spec

## Why

已有 TXT/MD 全本导入功能，但用户还可能拥有 EPUB 或 PDF 格式的小说文件（如从网上下载的电子书、出版书籍扫描件转文字等），需要支持直接导入这些格式，避免用户手动转换格式的麻烦。

## What Changes

- **新增 `services/epub_import_service.py`** — EPUB 格式解析与导入，复用现有全本导入流程
- **新增 `services/pdf_import_service.py`** — PDF 格式解析与导入，复用现有全本导入流程
- **修改 `services/txt_import_service.py`** — 抽取公共章节分割方法，供 EPUB/PDF 复用
- **修改 `ui/main_window.py`** — 文件菜单新增"从 EPUB 导入..."和"从 PDF 导入..."

## Dependencies

- EPUB: `ebooklib`（已在 requirements.txt 中）
- PDF: 需新增 `PyMuPDF>=1.24.0`（fitz 命名空间）

## Impact

- Affected specs: add-txt-import（扩展导入功能）
- Affected code:
  - `services/epub_import_service.py`（新建）
  - `services/pdf_import_service.py`（新建）
  - `services/txt_import_service.py`（抽取公共工具方法）
  - `ui/main_window.py`（菜单项）
  - `requirements.txt`（新增 PyMuPDF）

## ADDED Requirements

### Requirement: EPUB 全本导入

The system SHALL import a full book from an EPUB file and split it into chapters.

#### Scenario: 标准 EPUB 导入
- **WHEN** 用户点击"文件 → 导入 → 从 EPUB 导入..."
- **THEN** 弹出文件选择对话框，过滤 `.epub`
- **THEN** 系统使用 `ebooklib` 解析 EPUB 文件：
  1. 读取书的元数据（书名、作者）
  2. 按 Spine 顺序遍历文档项，保持原始章节顺序
  3. 对每个文档项，提取标题（优先从 TOC 获取 → 文件名回退）
  4. 清洗 HTML 内容，提取纯文本
  5. 过滤空内容章节
- **THEN** 复用 `ImportPreviewDialog` 显示分割预览
- **THEN** 确认后按全本导入流程创建章节到指定分卷

#### Scenario: 导航结构（NCX/TOC）缺失
- **WHEN** EPUB 文件没有可靠的 NCX/TOC 导航
- **THEN** 回退到按 Spine 顺序提取所有文档项，使用文件名作为章节标题
- **THEN** 仍然显示预览对话框供用户调整

### Requirement: PDF 全本导入

The system SHALL extract text from a PDF file and split it into chapters.

#### Scenario: PDF 文本导入
- **WHEN** 用户点击"文件 → 导入 → 从 PDF 导入..."
- **THEN** 弹出文件选择对话框，过滤 `.pdf`
- **THEN** 系统使用 PyMuPDF (fitz) 提取文本：
  1. 按页面顺序提取全部文本内容，每页末尾插入分页标记 `\f`
  2. 将全部文本拼接为一个大字符串
- **THEN** 复用 `TxtImportService.split_full_book()` 的章节分割逻辑（`第X章` 模式匹配 → 换行符兜底）
- **THEN** 复用 `ImportPreviewDialog` 显示分割预览
- **THEN** 确认后按全本导入流程创建章节到指定分卷

#### Scenario: PDF 扫描件（无文本层）
- **WHEN** PDF 文件为扫描件，提取的文本为空或极少（< 100 字符）
- **THEN** 弹出警告对话框："该 PDF 可能为扫描件，不包含可提取的文本内容。建议使用 OCR 工具（如 Adobe Acrobat、PaddleOCR）先转换为文本后再导入。"
- **THEN** 中止导入流程

### Requirement: 公共工具方法抽取

The system SHALL extract common text splitting logic into a shared utility for reuse across TXT/MD/PDF import.

- 将 `TxtImportService.split_full_book()` 和 `_build_segments()` 重构为独立的 `services/import_utils.py` 模块
- EPUB/PDF 导入服务也可调用这些分割方法

## Out of Scope

- PDF 扫描件 OCR 识别（需外部工具，非本软件职责）
- EPUB 转图片格式（EPUB 本身是 XHTML 文本，不需要转）
- PDF 保留布局（如段落缩进、分页信息等）
- 批量导入多个 EPUB/PDF

## MODIFIED Requirements

- `add-txt-import` spec 中的 `services/txt_import_service.py` 部分方法需要抽取为公共模块

## REMOVED Requirements

无
