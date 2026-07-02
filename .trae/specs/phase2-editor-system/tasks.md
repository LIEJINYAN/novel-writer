# Phase 2 编辑系统（第一批）- The Implementation Plan

## [x] Task 1: 章节编辑器组件（EditorWidget）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `ui/components/editor_widget.py`，封装 QPlainTextEdit 编辑器
  - 支持加载章节内容、获取当前内容
  - 内置字数统计方法（中文字数、段落数）
  - 内容变化信号（去抖动，避免每次按键都触发重计算）
  - 支持设置/获取修改状态（is_modified）
  - 编辑器字体设置（默认等宽字体，行高适中）
- **Acceptance Criteria Addressed**: AC-1, AC-9, AC-12
- **Test Requirements**:
  - `programmatic` TR-1.1: 模块可正常导入，EditorWidget 类可实例化
  - `programmatic` TR-1.2: set_content() 和 get_content() 正常工作
  - `programmatic` TR-1.3: count_words() 正确统计中文字数（排除空白）
  - `programmatic` TR-1.4: count_paragraphs() 正确统计段落数
  - `human-judgement` TR-1.5: 编辑器外观符合主题风格，字体舒适可读
- **Notes**: 使用 QPlainTextEdit 而非 QTextEdit，性能更优；字数统计去抖动 200ms

## [x] Task 2: 章节编辑服务（ChapterService）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `services/chapter_service.py`，封装章节和分卷的 CRUD 操作
  - 章节操作：create_chapter、update_chapter、delete_chapter（软删除）、get_chapter、rename_chapter
  - 分卷操作：create_volume、update_volume、delete_volume（软删除）、get_volume、rename_volume
  - 新建章节时自动计算章节号（当前分卷最大章节号 +1）
  - 操作完成后通过 signal_bus 发射对应信号
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5, AC-6, AC-7, AC-8
- **Test Requirements**:
  - `programmatic` TR-2.1: 模块可正常导入，ChapterService 类可实例化
  - `programmatic` TR-2.2: create_chapter() 在指定分卷下创建新章节，章节号自动递增
  - `programmatic` TR-2.3: update_chapter_content() 更新内容和字数
  - `programmatic` TR-2.4: delete_chapter() 软删除章节（is_deleted=True）
  - `programmatic` TR-2.5: create_volume() 创建新分卷，sort_order 自动递增
  - `programmatic` TR-2.6: delete_volume() 软删除分卷及其下所有章节
  - `programmatic` TR-2.7: 操作完成后发射对应信号
- **Notes**: 所有操作都使用 db_manager.get_session() 管理会话；软删除通过 is_deleted 字段

## [x] Task 3: 主窗口集成 - 章节打开与编辑
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - 项目树点击章节节点时，在中央 QTabWidget 中打开编辑器标签页
  - 标签页复用：如果章节已打开则切换到对应标签，不重复打开
  - 切换标签页时更新状态栏字数
  - 标签页标题显示章节名称，未保存时加 * 号
  - 初始化项目树的 itemClicked / itemDoubleClicked 信号连接
  - 保存菜单和 Ctrl+S 快捷键绑定到当前编辑的章节
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-11, AC-12, AC-13
- **Test Requirements**:
  - `programmatic` TR-3.1: 点击项目树章节节点能创建标签页
  - `programmatic` TR-3.2: 重复点击同一章节不重复创建标签页，而是切换到已有的
  - `programmatic` TR-3.3: 切换标签页时状态栏字数正确更新
  - `human-judgement` TR-3.4: 编辑内容后标签页显示 * 号，保存后消失
  - `human-judgement` TR-3.5: Ctrl+S 保存当前章节内容
- **Notes**: 用字典维护 chapter_id -> tab_index 的映射；保存动作先定位当前标签页对应的章节 ID

## [x] Task 4: 项目树右键菜单完善（章节/分卷操作）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 项目节点右键菜单：新建分卷
  - 分卷节点右键菜单：新建章节、重命名分卷、删除分卷
  - 章节节点右键菜单：重命名章节、删除章节
  - 所有操作前有确认对话框（删除操作必确认，重命名可直接输入）
  - 操作完成后自动刷新项目树
  - 删除章节后如果有打开的标签页，自动关闭该标签页
  - 删除分卷后关闭其下所有已打开的章节标签页
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5, AC-6, AC-7, AC-8
- **Test Requirements**:
  - `human-judgement` TR-4.1: 三种节点的右键菜单选项正确
  - `human-judgement` TR-4.2: 新建章节后自动打开新章节编辑器
  - `human-judgement` TR-4.3: 重命名后项目树和标签页同步更新
  - `programmatic` TR-4.4: 删除章节后数据库中 is_deleted=True
  - `programmatic` TR-4.5: 删除分卷后分卷和其下章节都标记为已删除
- **Notes**: 使用 QInputDialog 做重命名输入；删除用 QMessageBox.warning 确认

## [x] Task 5: 实时字数统计
- **Priority**: medium
- **Depends On**: Task 1, Task 3
- **Description**:
  - 编辑器内容变化时实时统计中文字数和段落数
  - 状态栏显示格式："字数：1,234 | 段落：12"
  - 使用去抖动（200ms）避免每次按键都重算
  - 切换标签页时更新为当前章节的统计
  - 关闭项目时清空字数显示
- **Acceptance Criteria Addressed**: AC-9, AC-2
- **Test Requirements**:
  - `programmatic` TR-5.1: 字数统计函数正确处理中英文混合文本
  - `programmatic` TR-5.2: 段落数统计正确（空行不计入）
  - `human-judgement` TR-5.3: 输入时状态栏字数流畅更新，无明显卡顿
- **Notes**: 中文字数统计逻辑：统计所有非空白字符数（中文+英文+数字+标点），与主流写作软件一致

## [x] Task 6: 自动保存功能
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**:
  - 使用 QTimer 实现自动保存，默认间隔 30 秒
  - 仅在内容有修改时才执行保存
  - 保存成功后清除修改标记，状态栏短暂显示"已自动保存"
  - 切换标签页、关闭标签页、关闭项目时触发即时保存
  - 自动保存不弹对话框，静默执行
- **Acceptance Criteria Addressed**: AC-10, AC-13
- **Test Requirements**:
  - `programmatic` TR-6.1: 修改内容后等待超过间隔时间，数据库内容已更新
  - `programmatic` TR-6.2: 未修改内容时不会触发数据库写入
  - `human-judgement` TR-6.3: 状态栏短暂显示保存提示
  - `human-judgement` TR-6.4: 自动保存后标签页 * 号消失
- **Notes**: 保存操作应在主线程执行（SQLite 写入很快），不阻塞 UI；可考虑用 QTimer.singleShot 延迟保存

## [x] Task 7: 标签页关闭确认
- **Priority**: medium
- **Depends On**: Task 3, Task 6
- **Description**:
  - 关闭有未保存修改的标签页时，弹出确认对话框
  - 对话框选项：保存、不保存、取消
  - 保存：保存内容后关闭标签页
  - 不保存：直接关闭标签页，丢弃修改
  - 取消：中止关闭操作
  - 关闭项目时，检查所有打开的标签页，逐一确认或批量保存
- **Acceptance Criteria Addressed**: AC-14
- **Test Requirements**:
  - `human-judgement` TR-7.1: 未修改的标签页直接关闭，无提示
  - `human-judgement` TR-7.2: 已修改的标签页关闭时弹出三按钮对话框
  - `human-judgement` TR-7.3: 选择"取消"后标签页不关闭
- **Notes**: 重写 QTabWidget 的 tabCloseRequested 处理逻辑；关闭项目时遍历所有标签页检查

## [x] Task 8: QSS 主题适配
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 暗色主题：QPlainTextEdit 背景色、文字色、选中文本色、光标色
  - 亮色主题：同上
  - 编辑器内边距、行高视觉调优
  - 标签页样式微调（未保存标记的颜色）
  - 确保所有新组件在两个主题下都正常显示
- **Acceptance Criteria Addressed**: AC-15
- **Test Requirements**:
  - `human-judgement` TR-8.1: 暗色主题下编辑器视觉舒适，对比度足够
  - `human-judgement` TR-8.2: 亮色主题下编辑器视觉舒适
  - `human-judgement` TR-8.3: 切换主题时编辑器即时更新样式
- **Notes**: 参考现有 dark.qss 和 light.qss 的命名约定；QPlainTextEdit 的 objectName 可用 editor_widget
