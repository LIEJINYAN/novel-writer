# Checklist

## 功能完整性

### EPUB 导入
- [ ] EPUB 标准结构可正确解析并导入
- [ ] 章节标题从 NCX/TOC 正确提取
- [ ] NCX/TOC 缺失时正确回退到文件名
- [ ] HTML 标签被正确清洗，仅保留纯文本
- [ ] 空章节被过滤

### PDF 导入
- [ ] 文本层 PDF 可正确提取文本并导入
- [ ] 章节分割复用 TXT 逻辑（`第X章` 模式匹配）
- [ ] 扫描件 PDF 检测正确弹出警告
- [ ] 分页标记 `\f` 正确处理

### 公共工具方法
- [ ] `import_utils.py` 包含 `split_full_book`、`_build_segments`、`natural_sort_key`
- [ ] `TxtImportService` 已改为调用公共方法
- [ ] 现有 TXT/MD 导入功能不受影响（回归测试）

### 菜单集成
- [ ] 文件菜单下有 "导入" 子菜单
- [ ] 子菜单包含三个选项：TXT/MD、EPUB、PDF 导入
- [ ] 每个选项触发对应的文件选择对话框
- [ ] 文件选择对话框正确过滤对应格式

### 依赖
- [ ] `PyMuPDF>=1.24.0` 已加入 requirements.txt
- [ ] `ebooklib` 已在 requirements.txt 中
- [ ] `pip install` 成功安装所有依赖

## 用户流程
- [ ] 用户可不借助外部工具直接导入 EPUB 小说
- [ ] 用户可将文本类 PDF 小说直接导入
- [ ] 用户收到扫描件 PDF 的明确提示
- [ ] 导入前后项目数据一致性（字数、章节数正确）
