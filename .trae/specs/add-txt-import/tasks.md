# Tasks

### [x] Task 1: 导入服务新增方法
- [x] `services/txt_import_service.py` 创建完成
  - [x] `import_chapter_from_file(file_path, chapter_id) -> Chapter` 
  - [x] `import_volume_from_dir(dir_path, volume_id) -> dict` 
  - [x] `import_full_book(file_path, project_id, volume_id) -> dict`
  - [x] `split_full_book(file_path) -> list[dict]` 分割逻辑
- [x] 全本分割逻辑：`## 第X章` / `=== 第X章 ===` / `\n\n\n`
- [x] 文件名自然排序

### [x] Task 2: 全本导入预览对话框
- [x] 创建 `ui/dialogs/import_preview_dialog.py`
  - [x] QDialog，左右栏布局
  - [x] 章节列表（标题 + 字数）
  - [x] 内容预览
  - [x] 目标分卷选择（已有 + 新建）
  - [x] 确认/取消按钮

### [x] Task 3: 单章导入菜单
- [x] 项目树章节右键菜单 → "从文件导入..."
- [x] 调用 `import_chapter_from_file`

### [x] Task 4: 分卷导入菜单
- [x] 项目树分卷右键菜单 → "从文件夹导入章节..."
- [x] 调用 `import_volume_from_dir`

### [x] Task 5: 全本导入菜单
- [x] 文件 → 导入 → 从 TXT/MD 导入...
- [x] 调用全本导入逻辑 + 预览对话框
