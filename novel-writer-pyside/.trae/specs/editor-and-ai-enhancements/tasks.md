# 编辑器增强 & AI 功能完善 - 实现计划

## 依赖关系

```
Task 1 (行号) ──┐
Task 2 (撤销/重做) ─┤
Task 3 (自动保存配置) ─┤
Task 4 (续写字数) ─────┤
Task 5 (API Key加密) ──┤
Task 6 (搜索历史) ─────┤
Task 7 (拖拽排序确认) ──┤
Task 8 (大纲跳转) ─────┘  (全部互不依赖，可并行)
```

**所有 8 个任务互不依赖，可并行执行，但需要逐个提交以保持代码质量。**

## [x] Task 1: 编辑器行号显示
- **优先级**: high
- **依赖**: 无
- **描述**:
  - 在 `editor_widget.py` 中添加行号区域（LineNumberArea）
  - 重写 `lineNumberAreaPaintEvent` 绘制行号
  - 当前行高亮
  - 更新 QSS 主题（亮色/暗色）以适配行号区域样式
- **验收标准**: AC-1
- **测试要求**:
  - `programmatic` TR-1.1: `EditorWidget` 实例化后左侧显示行号区域
  - `programmatic` TR-1.2: 输入多行文本后行号与行数一致
  - `human-judgment` TR-1.3: 行号区域视觉风格与主题一致
- **注意事项**: 参考 PySide6 `QPlainTextEdit` + `QWidget` 行号区域的经典实现（覆盖 `resizeEvent`）

## [x] Task 2: 撤销/重做历史栈管理
- **优先级**: high
- **依赖**: 无
- **描述**:
  - 撤销/重做已由 QPlainTextEdit 原生支持，主要工作是：
    - 在设置对话框中添加"撤销栈深度"配置项（默认 100，最大 500）
    - 在主窗口或编辑器中应用该配置（`editor.setMaximumBlockCount` 间接限制）
    - 考虑到 QPlainTextEdit 原生 UNDO/REDO 已满足需求且稳定，本任务聚焦"可配置栈深度"的 UI 和设置持久化
- **验收标准**: AC-2
- **测试要求**:
  - `programmatic` TR-2.1: 修改栈深度配置后保存并重启，设置保持
  - `human-judgment` TR-2.2: 设置对话框中显示撤销栈深度输入
- **注意事项**: QPlainTextEdit 原生不支持自定义 UNDO 栈深度，改用 QUndoStack 包装或接受原生行为 + 文档长度限制

## [x] Task 3: 自动保存间隔可在设置面板配置
- **优先级**: high
- **依赖**: 无
- **描述**:
  - 在 `ai_settings_dialog.py` 中或新建的设置对话框中添加"自动保存间隔"输入
  - 类型：QSpinBox，单位：秒，范围 10~300
  - 配置保存到 `AppConfig` 或 `QSettings`
  - 主窗口读取配置后更新 `_autosave_timer` 间隔
- **验收标准**: AC-3
- **测试要求**:
  - `programmatic` TR-3.1: 保存间隔配置到数据库或 QSettings
  - `programmatic` TR-3.2: 修改间隔后自动保存定时器立即更新
- **注意事项**: 需要 `main_window.py` 中的 `_autosave_timer` 支持动态更新间隔

## [x] Task 4: 续写字数选择
- **优先级**: medium
- **依赖**: 无
- **描述**:
  - 在 `ai_panel.py` 的续写区域添加字数选择控件（QComboBox 或 QSpinBox）
  - 选项：500 / 1000 / 1500 / 2000（默认）/ 自定义
  - 选择的值传递到 `WritingAIService` 作为 `max_tokens` 参数
  - `continue_write` 信号携带字数参数
- **验收标准**: AC-4
- **测试要求**:
  - `human-judgment` TR-4.1: AI 面板续写区域显示字数选择控件
  - `programmatic` TR-4.2: 选择字数后调用 AI 续写接口的 max_tokens 参数正确
- **注意事项**: 需要修改 `continue_write_requested` 信号签名以携带字数参数

## [x] Task 5: API Key 加密升级为 cryptography
- **优先级**: medium
- **依赖**: 无
- **描述**:
  - 安装 `cryptography` 包
  - 重写 `utils/crypto.py`：使用 `cryptography.fernet.Fernet` 替代异或
  - Fernet key 生成逻辑：机器码 + 固定盐值 → SHA256 → base64 url-safe
  - 旧格式兼容：检测密文是否为 base64 解码后的异或格式，自动重新加密保存
- **验收标准**: AC-5
- **测试要求**:
  - `programmatic` TR-5.1: 新加密的 API Key 可正常解密还原
  - `programmatic` TR-5.2: 旧格式密文可自动迁移到新格式
  - `programmatic` TR-5.3: `cryptography` 在 requirements.txt 中列出
- **注意事项**: 向后兼容非常重要，不能导致已有 API Key 丢失

## [x] Task 6: 搜索历史记录
- **优先级**: medium
- **依赖**: 无
- **描述**:
  - 在 `SearchPanel` 中添加搜索历史列表（QCompleter 或 QListWidget 弹出）
  - 每次搜索时将关键词加入历史（最多 20 条，去重）
  - 搜索框聚焦时显示历史下拉
  - 键盘上下键选择历史项
- **验收标准**: AC-6
- **测试要求**:
  - `human-judgment` TR-6.1: 搜索历史下拉显示最近搜索词
  - `programmatic` TR-6.2: 历史记录不超过 20 条，重复词去重
- **注意事项**: 使用 `QCompleter` + 自定义 model 实现最简洁

## [x] Task 7: 拖拽排序确认提示与撤销
- **优先级**: low
- **依赖**: 无
- **描述**:
  - 在 `_on_tree_rows_moved` / `_reorder_from_tree` 之后增加非阻塞提示条
  - 提示条样式：半透明浮动栏，位于底部，5 秒自动消失
  - 提示条包含"撤销"按钮
  - 点击撤销：恢复拖拽前的排序快照
  - 实现方式：保存排序前的完整章节顺序快照，撤销时回写数据库并刷新树
- **验收标准**: AC-7
- **测试要求**:
  - `human-judgment` TR-7.1: 拖拽后显示提示条，5 秒消失
  - `human-judgment` TR-7.2: 点击撤销后恢复原排序
- **注意事项**: 使用 QTimer 控制提示条显示时间

## [x] Task 8: 大纲面板点击跳转章节
- **优先级**: medium
- **依赖**: 无
- **描述**:
  - 在 `OutlineNodeWidget` 的章节范围标签上添加点击事件
  - 点击后发射信号，携带章节范围信息
  - `OutlinePanel` 转发信号到主窗口
  - 主窗口接收信号后跳转到对应章节编辑器
  - 如果跨多章，展开一个简单的下拉菜单让用户选择
- **验收标准**: AC-8
- **测试要求**:
  - `human-judgment` TR-8.1: 点击大纲节点的章节范围标签，编辑器跳转到对应章节
- **注意事项**: 需要 OutlinePanel 新增一个信号 `navigate_to_chapter(int)`，主窗口连接该信号

## 项目设置任务

## [x] Task 0: 项目设置
- **优先级**: high
- **依赖**: 无
- **描述**:
  - 添加 `cryptography` 到 `requirements.txt`
- **测试要求**:
  - `programmatic` TR-0.1: `pip install cryptography` 安装成功
