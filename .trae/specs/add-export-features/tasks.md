# Tasks

### [x] Task 1: 添加导出相关依赖
- [x] 在 `requirements.txt` 添加 `ebooklib>=0.18`（EPUB）、`fpdf2>=2.7`（PDF）
- [x] `pip install` 验证安装成功

### [x] Task 2: 创建导入服务（从原版导入）
- [x] 创建 `services/import_service.py`
  - [x] `detect_original_project(path) -> bool` 验证目录结构
  - [x] `import_original_project(path) -> Project` 导入完整项目
  - [x] 解析 `.specify/config.json` → 创建 Project
  - [x] 解析 `stories/*.md` → 创建 Volume + Chapter
  - [x] 解析 `spec/tracking/` 下的角色/情节数据
- [x] 菜单项：文件 → 导入 → 从原版导入
- [x] 错误处理和回滚

### [x] Task 3: 创建导出为原版格式服务
- [x] `services/export_service.py` 中添加 `export_to_original(project, target_path)`
  - [x] 生成 `.specify/config.json`
  - [x] 生成 `stories/*.md`（每章一个文件）
  - [x] 生成 `spec/tracking/` 数据文件
- [x] 菜单项：文件 → 导出 → 导出为原版格式

### [x] Task 4: 实现 TXT/MD 导出（可并行）
- [x] `services/export_service.py` 中添加 `export_txt(project, file_path)`
- [x] `services/export_service.py` 中添加 `export_md(project, file_path)`
- [x] 按分卷/章节顺序合并内容
- [x] TXT 使用 `=== 第X章 ===` 分隔，MD 使用 `##` 标题
- [x] 菜单项：文件 → 导出 → 全本导出 TXT / 全本导出 Markdown

### [x] Task 5: 实现 EPUB 导出
- [x] `services/export_service.py` 中添加 `export_epub(project, file_path, settings)`
  - [x] 生成封面页（书名+作者）
  - [x] 生成目录页（分卷+章节树）
  - [x] 每章作为一个 HTML 文档
  - [x] 设置元数据（标题、作者、语言 zh-CN）
- [x] 导出设置对话框（书名、作者）

### [x] Task 6: 实现 PDF 导出
- [x] `services/export_service.py` 中添加 `export_pdf(project, file_path, settings)`
  - [x] 设置中文字体
  - [x] 生成封面页
  - [x] 生成目录
  - [x] 每章内容分页
- [x] 导出设置对话框（书名、作者、字体大小、页边距）

### [x] Task 7: 实现单章/分卷导出菜单
- [x] 项目树右键菜单：章节节点 → "导出为 TXT" / "导出为 MD"
- [x] 项目树右键菜单：分卷节点 → "导出分卷为 TXT" / "导出分卷为 MD"
- [x] 调用 TXT/MD 导出逻辑的子集

# Task Dependencies
全部完成。
