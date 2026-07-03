# Tasks

### [ ] Task 1: 公共工具方法抽取
- [ ] 创建 `services/import_utils.py`
  - [ ] 将 `split_full_book(file_path) -> list[dict]` 从 `TxtImportService` 抽取为独立函数
  - [ ] 将 `_build_segments(content, matches) -> list[dict]` 抽取为独立函数
  - [ ] 将 `natural_sort_key(s) -> list` 抽取为独立函数
- [ ] 更新 `services/txt_import_service.py` 改为调用 `import_utils.py` 中的公共函数
- [ ] 验证 TXT/MD 导入功能不受影响

### [ ] Task 2: EPUB 导入服务
- [ ] 创建 `services/epub_import_service.py`
  - [ ] `import_epub_full_book(file_path, project_id, volume_id=None, target_name=None) -> dict`
  - [ ] 使用 `ebooklib` 解析 EPUB
  - [ ] 按 Spine 顺序提取章节文档
  - [ ] 从 NCX/TOC 提取章节标题，失败则回退到文件名
  - [ ] 清洗 HTML → 纯文本（移除标签、处理换行）
  - [ ] 过滤空章节
  - [ ] 复用 `ImportPreviewDialog` 预览 + `import_full_book` 导入流程

### [ ] Task 3: PDF 导入服务
- [ ] 创建 `services/pdf_import_service.py`
  - [ ] `import_pdf_full_book(file_path, project_id, volume_id=None, target_name=None) -> dict`
  - [ ] 使用 `PyMuPDF`（fitz）提取文本
  - [ ] 按页提取，分页标记 `\f` 插入
  - [ ] 调用 `import_utils.split_full_book()` 分割章节
  - [ ] 扫描件检测（提取文本 < 100 字符时警告）
  - [ ] 复用 `ImportPreviewDialog` 预览 + `import_full_book` 导入流程

### [ ] Task 4: 菜单集成
- [ ] 修改 `ui/main_window.py`
  - [ ] 文件菜单新增 "导入" 子菜单
  - [ ] "从 EPUB 导入..." 选项 → `_on_import_epub` handler
  - [ ] "从 PDF 导入..." 选项 → `_on_import_pdf` handler
  - [ ] "从 TXT/MD 导入..." 保持现有不变
  - [ ] 三个导入选项按顺序排列在"导入"子菜单中

### [ ] Task 5: 依赖安装
- [ ] 修改 `requirements.txt`，新增 `PyMuPDF>=1.24.0`
- [ ] 验证 `ebooklib` 已在 requirements.txt 中
- [ ] 运行 `pip install -r requirements.txt` 安装依赖

### [ ] Task 6: 交互测试
- [ ] 准备测试用 EPUB 文件（标准结构 + 无 TOC 两种）
- [ ] 准备测试用 PDF 文件（文本层 PDF + 扫描件两种）
- [ ] 执行全流程测试：
  - [ ] EPUB 标准结构导入 → 章节正确分割
  - [ ] EPUB 无 TOC 导入 → 文件名回退
  - [ ] PDF 文本导入 → 章节按 `第X章` 分割
  - [ ] PDF 扫描件 → 弹出警告
  - [ ] 预览对话框可正常显示和确认
  - [ ] 导入后章节内容和字数正确
