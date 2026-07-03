# 导入导出功能 — 验证检查清单

## 依赖
- [x] `requirements.txt` 包含 `ebooklib` 和 `fpdf2`
- [x] 两个库已成功 `pip install`

## 从原版导入
- [x] `ImportService.detect_original_project()` 验证目录结构
- [x] `ImportService.import_original_project()` 完整导入（项目信息/章节/角色/情节）
- [x] 无效目录抛出 ValueError
- [x] 导入为原子事务，失败回滚

## 导出为原版格式
- [x] `ExportService.export_to_original()` 生成目录结构
- [x] `.specify/config.json` 字段正确
- [x] `stories/` 目录包含所有章节

## 全本导出 TXT
- [x] `ExportService.export_txt()` 生成包含所有章节的 .txt
- [x] `=== 第X章 ===` 分隔符
- [x] 章节顺序正确

## 全本导出 MD
- [x] `ExportService.export_md()` 生成 Markdown 文件
- [x] `## 第X章` 标题级别
- [x] 内容包裹 `<div class="chapter">`

## 全本导出 EPUB
- [x] `ExportService.export_epub()` 生成 .epub
- [x] 使用 ebooklib 库
- [x] 封面页 + TOC + 每章独立文档
- [x] zh-CN 语言设置

## 全本导出 PDF
- [x] `ExportService.export_pdf()` 生成 .pdf
- [x] 使用 fpdf2 库
- [x] CJK 字体自动检测
- [x] 书名页 + 分卷标题页

## 单章/分卷导出
- [x] 右键章节 → "导出为 TXT" / "导出为 MD"
- [x] 右键分卷 → "导出分卷为 TXT" / "导出分卷为 MD"
- [x] 调用导出的子集逻辑，内容正确

## 菜单集成
- [x] 文件菜单有"从原版导入..."
- [x] 导出菜单有 TXT/MD/EPUB/PDF/原版格式 7 项
- [x] EPUB/PDF 弹出设置对话框（书名/作者/字号）
- [x] 所有入口有 try/except 错误处理
