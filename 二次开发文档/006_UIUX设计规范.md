# UI/UX 设计规范

## 1. 设计概述

### 1.1 设计理念

Novel Writer PySide6 版的 UI/UX 设计遵循以下核心原则：

1. **沉浸式写作**：界面不干扰创作，编辑区为核心焦点
2. **渐进式暴露**：复杂功能隐藏在子面板，按需展开
3. **上下文感知**：根据当前操作智能展示相关面板
4. **键盘优先**：所有操作支持快捷键，减少鼠标依赖
5. **响应式布局**：面板可拖拽、隐藏、自定义
6. **暗色优先**：长时间写作护眼，支持亮色切换

### 1.2 目标用户画像

| 用户类型 | 特征 | 核心需求 |
|---------|------|---------|
| 网文作者 | 日更需求、追求效率 | 快速续写、字数统计、章节管理 |
| 严肃文学作者 | 深度创作、结构严谨 | 大纲规划、角色追踪、一致性检查 |
| 新手作者 | 不熟悉创作方法论 | 向导式流程、方法推荐、写作提示 |
| AI 辅助用户 | 依赖 AI 生成内容 | AI 对话、续写、润色、多模型对比 |

---

## 2. 整体布局

### 2.1 主窗口布局

```
┌───────────────────────────────────────────────────────────┐
│  菜单栏 (File, Edit, View, Project, Writing, AI, Help)     │
├───────────────────────────────────────────────────────────┤
│  工具栏 (新建│打开│保存│撤销│重做│AI续写│润色│设置)        │
├──────┬──────────────────────────────────┬────────────────┤
│      │                                  │                │
│ 左   │                                  │   右侧栏       │
│ 侧   │       中央编辑器区域              │                │
│ 栏   │                                  │  [AI面板]      │
│      │   (富文本编辑器)                  │  [角色面板]    │
│ 项目 │                                  │  [大纲面板]    │
│ 树   │                                  │  [追踪面板]    │
│      │                                  │  [统计面板]    │
│      │                                  │                │
├──────┴──────────────────────────────────┴────────────────┤
│  状态栏 (字数│行数│项目名│保存状态│AI状态│光标位置)      │
└───────────────────────────────────────────────────────────┘
```

### 2.2 布局实现

```python
# ui/main_window.py
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QDockWidget
)
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Novel Writer")
        self.resize(1400, 900)
        self.setMinimumSize(1000, 600)
        
        self._init_central_widget()
        self._init_dock_widgets()
        self._init_menu()
        self._init_toolbar()
        self._init_statusbar()
        self._restore_layout()
    
    def _init_central_widget(self):
        """中央编辑器区域"""
        self.editor_tabs = EditorTabWidget(self)
        self.setCentralWidget(self.editor_tabs)
    
    def _init_dock_widgets(self):
        """初始化停靠面板"""
        # 左侧 - 项目树
        self.project_tree_dock = QDockWidget("项目", self)
        self.project_tree_dock.setWidget(ProjectTreeWidget(self))
        self.project_tree_dock.setFeatures(
            QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable
        )
        self.addDockWidget(Qt.LeftDockWidgetArea, self.project_tree_dock)
        
        # 右侧 - 多面板
        self.right_dock = QDockWidget("面板", self)
        self.right_panel = RightPanelWidget(self)
        self.right_dock.setWidget(self.right_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)
        
        # 底部 - AI 对话面板（可隐藏）
        self.ai_dock = QDockWidget("AI 对话", self)
        self.ai_dock.setWidget(AIChatWidget(self))
        self.addDockWidget(Qt.BottomDockWidgetArea, self.ai_dock)
        self.ai_dock.hide()  # 默认隐藏
```

### 2.3 面板尺寸建议

| 面板 | 默认宽度/高度 | 最小值 | 可隐藏 | 可拖拽 |
|------|-------------|--------|--------|--------|
| 左侧栏（项目树） | 250px | 180px | 是 | 是 |
| 中央编辑器 | 自适应 | 400px | 否 | 否 |
| 右侧栏（面板） | 320px | 240px | 是 | 是 |
| 底部 AI 面板 | 200px | 120px | 是 | 是 |
| 状态栏 | 28px | 28px | 否 | 否 |

---

## 3. QSS 主题系统

### 3.1 主题架构

```
ui/styles/
├── dark.qss          # 暗色主题（默认）
├── light.qss         # 亮色主题
├── sepia.qss         # 护眼黄
├── variables.css     # 主题变量（颜色、字体、间距）
└── common.qss        # 通用样式（跨主题）
```

### 3.2 暗色主题色板

```css
/* ui/styles/variables.css */

/* 背景色 */
--bg-primary: #1e1e2e;        /* 主背景 */
--bg-secondary: #2a2a3c;      /* 次背景 */
--bg-tertiary: #33334d;       /* 三级背景 */
--bg-hover: #3a3a55;          /* 悬停背景 */
--bg-selected: #4a4a6a;       /* 选中背景 */

/* 文字色 */
--text-primary: #e0e0e8;     /* 主文字 */
--text-secondary: #a0a0b8;    /* 次文字 */
--text-muted: #6a6a85;        /* 弱化文字 */
--text-accent: #7c7cff;       /* 强调文字 */

/* 边框色 */
--border-color: #3a3a55;      /* 普通边框 */
--border-hover: #5a5a8a;     /* 悬停边框 */

/* 功能色 */
--color-success: #4caf50;     /* 成功 */
--color-warning: #ff9800;     /* 警告 */
--color-error: #f44336;       /* 错误 */
--color-info: #2196f3;        /* 信息 */

/* AI 专用色 */
--color-ai: #9c27b0;          /* AI 操作 */
--color-ai-bg: #2d1b3d;      /* AI 背景 */
--color-ai-text: #ce93d8;    /* AI 文字 */

/* 编辑器色 */
--editor-bg: #1a1a28;        /* 编辑器背景 */
--editor-text: #d4d4d8;      /* 编辑器文字 */
--editor-cursor: #7c7cff;    /* 光标色 */
--editor-selection: #4a4a6a;  /* 选中色 */
```

### 3.3 暗色主题 QSS

```css
/* ui/styles/dark.qss */

/* 全局 */
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #e0e0e8;
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
    font-size: 14px;
}

/* 菜单栏 */
QMenuBar {
    background-color: #2a2a3c;
    border-bottom: 1px solid #3a3a55;
    padding: 2px;
}
QMenuBar::item {
    padding: 4px 12px;
    border-radius: 4px;
}
QMenuBar::item:selected {
    background-color: #3a3a55;
}

/* 菜单 */
QMenu {
    background-color: #2a2a3c;
    border: 1px solid #3a3a55;
    border-radius: 6px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 24px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #4a4a6a;
}
QMenu::separator {
    height: 1px;
    background-color: #3a3a55;
    margin: 4px 8px;
}

/* 工具栏 */
QToolBar {
    background-color: #2a2a3c;
    border-bottom: 1px solid #3a3a55;
    padding: 4px;
    spacing: 4px;
}
QToolBar::separator {
    width: 1px;
    background-color: #3a3a55;
    margin: 0 4px;
}

/* 按钮 */
QPushButton {
    background-color: #33334d;
    border: 1px solid #3a3a55;
    border-radius: 6px;
    padding: 6px 16px;
    color: #e0e0e8;
}
QPushButton:hover {
    background-color: #3a3a55;
    border-color: #5a5a8a;
}
QPushButton:pressed {
    background-color: #2a2a3c;
}
QPushButton:disabled {
    color: #6a6a85;
    background-color: #2a2a3c;
}

/* 主按钮（AI 操作） */
QPushButton#aiButton {
    background-color: #4a2d5a;
    border-color: #6a3d7a;
    color: #ce93d8;
}
QPushButton#aiButton:hover {
    background-color: #5a3d6a;
}

/* 输入框 */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #1a1a28;
    border: 1px solid #3a3a55;
    border-radius: 6px;
    padding: 6px 8px;
    color: #d4d4d8;
    selection-background-color: #4a4a6a;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #7c7cff;
}

/* 编辑器特殊样式 */
QTextEdit#textEditor {
    background-color: #1a1a28;
    font-family: "Source Han Serif SC", "Noto Serif CJK SC", serif;
    font-size: 16px;
    line-height: 1.8;
    padding: 20px 40px;
    border: none;
}

/* 树形视图 */
QTreeView {
    background-color: #2a2a3c;
    border: 1px solid #3a3a55;
    border-radius: 6px;
}
QTreeView::item {
    padding: 4px 8px;
    border-radius: 4px;
}
QTreeView::item:hover {
    background-color: #3a3a55;
}
QTreeView::item:selected {
    background-color: #4a4a6a;
}

/* 标签页 */
QTabWidget::pane {
    border: 1px solid #3a3a55;
    border-radius: 6px;
    background-color: #1e1e2e;
}
QTabBar::tab {
    background-color: #2a2a3c;
    border: 1px solid #3a3a55;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 6px 16px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #1e1e2e;
    border-bottom: 2px solid #7c7cff;
}

/* 滚动条 */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #3a3a55;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #5a5a8a;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* 状态栏 */
QStatusBar {
    background-color: #2a2a3c;
    border-top: 1px solid #3a3a55;
    color: #a0a0b8;
    font-size: 12px;
}

/* 停靠面板 */
QDockWidget {
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
}
QDockWidget::title {
    background-color: #2a2a3c;
    padding: 4px 8px;
    border-bottom: 1px solid #3a3a55;
}

/* 对话框 */
QDialog {
    background-color: #1e1e2e;
}

/* 分组框 */
QGroupBox {
    border: 1px solid #3a3a55;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 12px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
}

/* 复选框 */
QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #3a3a55;
    border-radius: 3px;
    background-color: #1a1a28;
}
QCheckBox::indicator:checked {
    background-color: #7c7cff;
    border-color: #7c7cff;
}

/* 下拉框 */
QComboBox {
    background-color: #33334d;
    border: 1px solid #3a3a55;
    border-radius: 6px;
    padding: 4px 8px;
}
QComboBox:hover {
    border-color: #5a5a8a;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
```

### 3.4 主题切换

```python
# ui/styles/theme_manager.py
from PySide6.QtCore import QObject

class ThemeManager(QObject):
    """主题管理器"""
    
    THEMES = {
        "dark": "ui/styles/dark.qss",
        "light": "ui/styles/light.qss",
        "sepia": "ui/styles/sepia.qss",
    }
    
    def __init__(self, app):
        self.app = app
        self.current_theme = "dark"
    
    def apply_theme(self, theme_name: str):
        """应用主题"""
        if theme_name not in self.THEMES:
            return
        
        qss_path = self.THEMES[theme_name]
        with open(qss_path, "r", encoding="utf-8") as f:
            self.app.setStyleSheet(f.read())
        
        self.current_theme = theme_name
    
    def get_available_themes(self) -> list:
        return list(self.THEMES.keys())
```

---

## 4. 编辑器设计

### 4.1 编辑器组件

```python
# ui/editor/text_editor.py
from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import (
    QTextCharFormat, QFont, QColor, QSyntaxHighlighter,
    QTextFormat
)

class TextEditor(QTextEdit):
    """富文本编辑器"""
    
    content_changed = Signal()
    word_count_changed = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("textEditor")
        
        # 基本设置
        self.setAcceptRichText(True)
        self.setAutoFormatting(QTextEdit.AutoNone)
        
        # 字体设置
        font = QFont("Source Han Serif SC", 16)
        font.setStyleHint(QFont.Serif)
        self.setFont(font)
        
        # 行高
        self.setLineHeight(1.8)
        
        # 自动保存
        self._auto_save_timer = QTimer()
        self._auto_save_timer.setSingleShot(True)
        self._auto_save_timer.timeout.connect(self._auto_save)
        self.textChanged.connect(self._on_text_changed)
        
        # 字数
        self._word_count = 0
        
        # 快捷键
        self._setup_shortcuts()
    
    def _setup_shortcuts(self):
        """快捷键设置"""
        # Ctrl+B 加粗
        # Ctrl+I 斜体
        # Ctrl+Shift+1 一级标题
        # Ctrl+Shift+2 二级标题
        # Ctrl+Enter AI 续写
        # Ctrl+Shift+P AI 润色
        # Ctrl+S 保存
        # Ctrl+F 搜索
        # Ctrl+H 替换
        ...
    
    def _on_text_changed(self):
        """内容变更"""
        self.content_changed.emit()
        self._update_word_count()
        self._auto_save_timer.start(30000)  # 30秒后自动保存
    
    def _update_word_count(self):
        """更新字数"""
        text = self.toPlainText()
        # 中文字数统计：非空白字符数
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        total_chars = len(text.replace('\n', '').replace(' ', ''))
        self._word_count = chinese_chars
        self.word_count_changed.emit(self._word_count)
    
    def get_word_count(self) -> int:
        return self._word_count
    
    def get_char_count(self) -> int:
        return len(self.toPlainText())
    
    def get_paragraph_count(self) -> int:
        return self.document().blockCount()
    
    def insert_ai_text(self, text: str):
        """插入 AI 生成的文本（带打字机效果）"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
    
    def insert_ai_text_stream(self, text: str):
        """流式插入文本（逐字）"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.setTextCursor(cursor)
    
    def set_focus_mode(self, enabled: bool):
        """专注模式：仅高亮当前段落"""
        ...
```

### 4.2 多标签页

```python
# ui/editor/editor_tabs.py
from PySide6.QtWidgets import QTabWidget, QToolButton

class EditorTabWidget(QTabWidget):
    """多标签页编辑器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        
        # 新建标签按钮
        self._setup_new_tab_button()
        
        self.tabCloseRequested.connect(self._on_close_tab)
        self.currentChanged.connect(self._on_tab_changed)
    
    def open_chapter(self, chapter_id: int, title: str, content: str):
        """打开章节"""
        # 检查是否已打开
        for i in range(self.count()):
            editor = self.widget(i)
            if hasattr(editor, 'chapter_id') and editor.chapter_id == chapter_id:
                self.setCurrentIndex(i)
                return
        
        # 新建标签
        editor = TextEditor(self)
        editor.chapter_id = chapter_id
        editor.setPlainText(content)
        
        index = self.addTab(editor, title)
        self.setCurrentIndex(index)
    
    def _on_close_tab(self, index: int):
        """关闭标签"""
        editor = self.widget(index)
        # 检查是否有未保存内容
        # ...
        self.removeTab(index)
```

---

## 5. 侧边栏面板设计

### 5.1 左侧 - 项目树

```python
# ui/sidebar/project_tree.py
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Qt, Signal

class ProjectTreeWidget(QTreeWidget):
    """项目树"""
    
    chapter_selected = Signal(int)       # 章节选中
    chapter_context_menu = Signal(int, str)  # 右键菜单 (chapter_id, action)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        self._setup_columns()
        self._setup_context_menu()
        
        self.itemDoubleClicked.connect(self._on_double_click)
        self.customContextMenuRequested.connect(self._on_context_menu)
    
    def load_project(self, project_id: int):
        """加载项目结构"""
        self.clear()
        
        # 分卷 → 章节 树形结构
        # 第1卷
        #   ├── 第1章：标题
        #   ├── 第2章：标题
        #   └── 第3章：标题
        # 未分卷
        #   ├── ...
        ...
    
    def _on_double_click(self, item, column):
        """双击打开章节"""
        if item.data(0, Qt.UserRole):
            chapter_id = item.data(0, Qt.UserRole)
            self.chapter_selected.emit(chapter_id)
    
    def _setup_context_menu(self):
        """右键菜单"""
        # 新建章节
        # 新建分卷
        # 重命名
        # 删除
        # 移动到分卷
        # 导出章节
        # 标记为完成
        ...
```

### 5.2 右侧 - 多面板容器

```python
# ui/sidebar/right_panel.py
from PySide6.QtWidgets import (
    QTabWidget, QWidget, QVBoxLayout
)

class RightPanelWidget(QTabWidget):
    """右侧面板容器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # AI 面板
        self.ai_panel = AIPanel(self)
        self.addTab(self.ai_panel, "AI")
        
        # 角色面板
        self.character_panel = CharacterPanel(self)
        self.addTab(self.character_panel, "角色")
        
        # 大纲面板
        self.outline_panel = OutlinePanel(self)
        self.addTab(self.outline_panel, "大纲")
        
        # 追踪面板
        self.tracking_panel = TrackingPanel(self)
        self.addTab(self.tracking_panel, "追踪")
        
        # 统计面板
        self.stats_panel = StatsPanel(self)
        self.addTab(self.stats_panel, "统计")
        
        self.setTabPosition(QTabWidget.North)
```

### 5.3 AI 面板

```python
# ui/sidebar/ai_panel.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QComboBox, QSpinBox, QSlider, QLabel
)

class AIPanel(QWidget):
    """AI 面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # 模型选择
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("模型:"))
        self.model_combo = QComboBox()
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)
        
        # 温度滑块
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("温度:"))
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setRange(0, 200)
        self.temp_slider.setValue(70)
        self.temp_label = QLabel("0.7")
        temp_layout.addWidget(self.temp_slider)
        temp_layout.addWidget(self.temp_label)
        layout.addLayout(temp_layout)
        
        # 最大 token
        token_layout = QHBoxLayout()
        token_layout.addWidget(QLabel("最大输出:"))
        self.token_spin = QSpinBox()
        self.token_spin.setRange(100, 32000)
        self.token_spin.setValue(4000)
        token_layout.addWidget(self.token_spin)
        layout.addLayout(token_layout)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        self.continue_btn = QPushButton("续写")
        self.continue_btn.setObjectName("aiButton")
        self.polish_btn = QPushButton("润色")
        self.polish_btn.setObjectName("aiButton")
        self.dialogue_btn = QPushButton("对话")
        self.dialogue_btn.setObjectName("aiButton")
        btn_layout.addWidget(self.continue_btn)
        btn_layout.addWidget(self.polish_btn)
        btn_layout.addWidget(self.dialogue_btn)
        layout.addLayout(btn_layout)
        
        # 输出区域
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("AI 输出将显示在此处...")
        layout.addWidget(self.output_text)
        
        # 操作按钮
        action_layout = QHBoxLayout()
        self.insert_btn = QPushButton("插入到编辑器")
        self.copy_btn = QPushButton("复制")
        self.clear_btn = QPushButton("清空")
        action_layout.addWidget(self.insert_btn)
        action_layout.addWidget(self.copy_btn)
        action_layout.addWidget(self.clear_btn)
        layout.addLayout(action_layout)
```

### 5.4 角色面板

```python
# ui/sidebar/character_panel.py
class CharacterPanel(QWidget):
    """角色管理面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索角色...")
        layout.addWidget(self.search_input)
        
        # 角色列表
        self.character_list = QTreeWidget()
        self.character_list.setHeaderLabels(["姓名", "定位", "重要性"])
        layout.addWidget(self.character_list)
        
        # 添加/编辑按钮
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("添加角色")
        self.edit_btn = QPushButton("编辑")
        self.delete_btn = QPushButton("删除")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)
        
        # 角色详情（折叠展开）
        self.detail_group = QGroupBox("角色详情")
        # 姓名、性别、年龄、定位、外貌、性格、背景...
        ...
```

### 5.5 追踪面板

```python
# ui/sidebar/tracking_panel.py
class TrackingPanel(QWidget):
    """追踪面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # 追踪类型选择
        self.type_tabs = QTabWidget()
        
        # 情节追踪
        self.plot_tab = self._create_plot_tab()
        self.type_tabs.addTab(self.plot_tab, "情节")
        
        # 角色状态
        self.state_tab = self._create_state_tab()
        self.type_tabs.addTab(self.state_tab, "状态")
        
        # 关系图谱
        self.relation_tab = self._create_relation_tab()
        self.type_tabs.addTab(self.relation_tab, "关系")
        
        # 时间线
        self.timeline_tab = self._create_timeline_tab()
        self.type_tabs.addTab(self.timeline_tab, "时间线")
        
        layout.addWidget(self.type_tabs)
        
        # 一致性检查按钮
        self.check_btn = QPushButton("一致性检查")
        self.check_btn.setObjectName("aiButton")
        layout.addWidget(self.check_btn)
    
    def _create_plot_tab(self):
        """情节追踪标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 情节节点树
        self.plot_tree = QTreeWidget()
        self.plot_tree.setHeaderLabels(["节点", "状态", "阶段"])
        layout.addWidget(self.plot_tree)
        
        # 伏笔列表
        self.foreshadow_list = QListWidget()
        layout.addWidget(QLabel("伏笔:"))
        layout.addWidget(self.foreshadow_list)
        
        # 冲突列表
        self.conflict_list = QListWidget()
        layout.addWidget(QLabel("冲突:"))
        layout.addWidget(self.conflict_list)
        
        return tab
```

---

## 6. 对话框设计

### 6.1 新建项目对话框

```python
# ui/dialogs/new_project_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QTextEdit, QSpinBox, QDialogButtonBox,
    QFileDialog, QLabel
)

class NewProjectDialog(QDialog):
    """新建项目对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新建项目")
        self.setFixedSize(500, 600)
        
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # 项目名称
        form = QFormLayout()
        self.name_input = QLineEdit()
        form.addRow("项目名称:", self.name_input)
        
        # 项目路径
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.browse_btn = QPushButton("浏览...")
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)
        form.addRow("项目路径:", path_layout)
        
        # 小说类型
        self.genre_combo = QComboBox()
        self.genre_combo.addItems([
            "玄幻", "仙侠", "都市", "科幻", "历史",
            "悬疑", "言情", "武侠", "游戏", "其他"
        ])
        form.addRow("小说类型:", self.genre_combo)
        
        # 写作方法
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "三幕式 (three-act)",
            "英雄之旅 (hero-journey)",
            "故事圈 (story-circle)",
            "七点结构 (seven-point)",
            "皮克斯公式 (pixar)",
            "雪花法 (snowflake)",
        ])
        form.addRow("写作方法:", self.method_combo)
        
        # 预计字数
        self.word_count_spin = QSpinBox()
        self.word_count_spin.setRange(10000, 5000000)
        self.word_count_spin.setValue(200000)
        self.word_count_spin.setSingleStep(10000)
        form.addRow("预计字数:", self.word_count_spin)
        
        layout.addLayout(form)
        
        # 简介
        layout.addWidget(QLabel("项目简介:"))
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(100)
        layout.addWidget(self.desc_input)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
```

### 6.2 AI 设置对话框

```python
# ui/dialogs/ai_settings_dialog.py
class AISettingsDialog(QDialog):
    """AI 设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI 设置")
        self.setFixedSize(600, 500)
        
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # 提供商选择
        provider_group = QGroupBox("AI 提供商")
        provider_layout = QVBoxLayout(provider_group)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems([
            "OpenAI", "Anthropic Claude", "Google Gemini",
            "DeepSeek", "Ollama (本地)", "通义千问", "豆包"
        ])
        provider_layout.addWidget(self.provider_combo)
        
        # API Key
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        provider_layout.addWidget(QLabel("API Key:"))
        provider_layout.addWidget(self.api_key_input)
        
        # API Base (可选)
        self.api_base_input = QLineEdit()
        self.api_base_input.setPlaceholderText("自定义 API 地址（可选）")
        provider_layout.addWidget(QLabel("API 地址:"))
        provider_layout.addWidget(self.api_base_input)
        
        # 测试连接
        self.test_btn = QPushButton("测试连接")
        provider_layout.addWidget(self.test_btn)
        
        layout.addWidget(provider_group)
        
        # 参数设置
        params_group = QGroupBox("生成参数")
        params_layout = QFormLayout(params_group)
        
        # 模型选择
        self.model_combo = QComboBox()
        params_layout.addRow("模型:", self.model_combo)
        
        # 温度
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setRange(0, 200)
        self.temp_slider.setValue(70)
        params_layout.addRow("温度:", self.temp_slider)
        
        # Max Tokens
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 128000)
        self.max_tokens_spin.setValue(4000)
        params_layout.addRow("最大输出:", self.max_tokens_spin)
        
        layout.addWidget(params_group)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
```

---

## 7. 菜单设计

### 7.1 完整菜单结构

```
文件 (File)
├── 新建项目...          Ctrl+N
├── 打开项目...          Ctrl+O
├── 最近打开
│   ├── 项目A
│   └── 项目B
├── 保存                Ctrl+S
├── 全部保存            Ctrl+Shift+S
├── 导出
│   ├── 导出为 TXT
│   ├── 导出为 Markdown
│   ├── 导出为 EPUB
│   └── 导出为 PDF
├── 从原版导入...
├── 备份项目...
├── 恢复项目...
├── 升级项目...
└── 退出                Ctrl+Q

编辑 (Edit)
├── 撤销                Ctrl+Z
├── 重做                Ctrl+Y
├── 剪切                Ctrl+X
├── 复制                Ctrl+C
├── 粘贴                Ctrl+V
├── 全选                Ctrl+A
├── 搜索...             Ctrl+F
├── 替换...             Ctrl+H
└── 格式
    ├── 加粗             Ctrl+B
    ├── 斜体             Ctrl+I
    ├── 一级标题         Ctrl+Shift+1
    ├── 二级标题         Ctrl+Shift+2
    └── 清除格式

视图 (View)
├── 专注模式            F11
├── 切换左侧栏          Ctrl+Shift+L
├── 切换右侧栏          Ctrl+Shift+R
├── 切换底部面板        Ctrl+Shift+B
├── 主题
│   ├── 暗色 (默认)
│   ├── 亮色
│   └── 护眼黄
├── 字体大小
│   ├── 放大            Ctrl++
│   ├── 缩小            Ctrl+-
│   └── 重置            Ctrl+0
└── 全屏                F12

项目 (Project)
├── 项目设置...
├── 章节管理...
├── 分卷管理...
├── 项目统计...
└── 写作方法
    ├── 三幕式
    ├── 英雄之旅
    ├── 故事圈
    ├── 七点结构
    ├── 皮克斯公式
    ├── 雪花法
    └── 方法推荐...

写作 (Writing)
├── 创作宪法...          (七步法第1步)
├── 故事规格...          (七步法第2步)
├── 决策澄清...          (七步法第3步)
├── 创作计划...          (七步法第4步)
├── 任务分解...          (七步法第5步)
├── AI 续写             Ctrl+Enter  (七步法第6步)
├── 质量分析...                       (七步法第7步)
├── ─────────────
├── 生成对话...
├── 生成大纲...
└── AI 审计...

AI
├── AI 对话面板          Ctrl+Shift+A
├── 切换提供商
│   ├── OpenAI
│   ├── Claude
│   ├── Gemini
│   ├── DeepSeek
│   └── Ollama (本地)
├── 切换模型
│   ├── gpt-4o
│   ├── claude-sonnet-4-5
│   └── ...
├── AI 设置...
└── ─────────────
├── 专家模式
│   ├── 剧情结构专家
│   ├── 人物塑造专家
│   ├── 世界观构建专家
│   └── 风格把控专家

追踪 (Tracking)
├── 综合追踪面板
├── 情节检查...
├── 时间线管理...
├── 关系图谱...
├── 世界观验证...
├── 一致性检查...
└── 验证规则设置...

工具 (Tools)
├── 插件管理...
├── 选项/设置...
└── 环境检查...

帮助 (Help)
├── 使用文档
├── 快捷键参考          Ctrl+/
├── 检查更新...
├── 关于
└── 反馈
```

---

## 8. 快捷键设计

### 8.1 全局快捷键

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| `Ctrl+N` | 新建项目 | |
| `Ctrl+O` | 打开项目 | |
| `Ctrl+S` | 保存当前章节 | |
| `Ctrl+Shift+S` | 全部保存 | |
| `Ctrl+W` | 关闭标签页 | |
| `Ctrl+Q` | 退出 | |
| `F11` | 专注模式 | 隐藏所有面板 |
| `F12` | 全屏 | |

### 8.2 编辑器快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Z` | 撤销 |
| `Ctrl+Y` | 重做 |
| `Ctrl+B` | 加粗 |
| `Ctrl+I` | 斜体 |
| `Ctrl+Shift+1` | 一级标题 |
| `Ctrl+Shift+2` | 二级标题 |
| `Ctrl+F` | 搜索 |
| `Ctrl+H` | 替换 |
| `Ctrl++` | 放大字体 |
| `Ctrl+-` | 缩小字体 |
| `Ctrl+0` | 重置字体 |

### 8.3 AI 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Enter` | AI 续写 |
| `Ctrl+Shift+P` | AI 润色 |
| `Ctrl+Shift+A` | 打开 AI 对话面板 |
| `Ctrl+Shift+D` | 生成对话 |
| `Ctrl+Shift+O` | 生成大纲 |
| `Ctrl+Shift+E` | 专家模式 |

### 8.4 面板切换快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Shift+L` | 切换左侧栏 |
| `Ctrl+Shift+R` | 切换右侧栏 |
| `Ctrl+Shift+B` | 切换底部面板 |
| `Ctrl+Shift+T` | 切换追踪面板 |
| `Ctrl+Shift+C` | 切换角色面板 |

---

## 9. 交互模式

### 9.1 AI 续写交互流程

```
用户在编辑器中定位光标
    ↓
按 Ctrl+Enter 或点击「续写」按钮
    ↓
编辑器底部出现 AI 状态栏（流式输出中...）
    ↓
AI 生成的文本逐字插入到光标位置（打字机效果）
    ↓
同时用户可以随时按 Esc 中断
    ↓
生成完成后：
    ├── 按 Enter 确认（保存到数据库）
    ├── 按 Esc 撤销（回退文本）
    └── 继续编辑（自动保留）
```

### 9.2 AI 润色交互流程

```
用户选中文本
    ↓
按 Ctrl+Shift+P 或右键 → AI 润色
    ↓
弹出润色选项（风格选择）
    ↓
AI 处理中（显示进度）
    ↓
弹出差分对比窗口
    ├── 原文（左）vs 润色后（右）
    ├── 差异高亮
    ├── 接受 / 拒绝 / 部分接受
    └── 继续润色
```

### 9.3 专注模式

```
用户按 F11
    ↓
隐藏所有面板（菜单、工具栏、侧边栏）
    ↓
编辑器全屏，仅保留状态栏
    ↓
当前段落高亮，其他段落降低不透明度（可选）
    ↓
再按 F11 退出
```

### 9.4 状态栏实时信息

```
状态栏布局：
[字数: 3,245] [行数: 156] [段落: 45] | [项目: 我的小说] | [● 已保存] | [AI: GPT-4o] | [Ln 45, Col 12]
```

---

## 10. 响应式与可访问性

### 10.1 响应式策略

| 窗口宽度 | 布局策略 |
|---------|---------|
| ≥ 1400px | 全布局（左右侧栏 + 编辑器 + 底部面板） |
| 1000-1399px | 左右侧栏可收窄 |
| 800-999px | 自动隐藏一个侧栏 |
| < 800px | 仅显示编辑器，侧栏改为浮层 |

### 10.2 字体策略

| 用途 | 字体 | 大小 |
|------|------|------|
| 编辑器正文 | Source Han Serif SC (思源宋体) | 16px |
| 界面文字 | Microsoft YaHei UI | 14px |
| 代码/等宽 | JetBrains Mono / Consolas | 13px |
| 标题 | Microsoft YaHei UI Bold | 16-20px |

### 10.3 可访问性

1. **高对比度模式**：主题色对比度 ≥ 4.5:1
2. **键盘导航**：所有操作可通过键盘完成
3. **焦点指示器**：清晰的焦点边框
4. **快捷键提示**：菜单中显示快捷键
5. **状态反馈**：所有操作有视觉/文字反馈
6. **错误提示**：友好的错误消息，不使用技术术语

---

## 11. 图标系统

### 11.1 图标规范

使用 Qt 内置图标 + 自定义 SVG 图标。

| 图标用途 | 来源 | 大小 |
|---------|------|------|
| 文件操作 | Qt StandardIcon | 16x16 / 24x24 |
| 编辑操作 | Qt StandardIcon | 16x16 / 24x24 |
| AI 操作 | 自定义 SVG | 24x24 |
| 追踪操作 | 自定义 SVG | 16x16 |
| 状态指示 | 自定义 SVG | 12x12 |

### 11.2 自定义图标

```
ui/icons/
├── ai_continue.svg     # AI 续写
├── ai_polish.svg       # AI 润色
├── ai_dialogue.svg     # AI 对话
├── track_plot.svg      # 情节追踪
├── track_character.svg # 角色追踪
├── track_relation.svg  # 关系追踪
├── track_timeline.svg  # 时间线
├── status_saved.svg    # 已保存
├── status_saving.svg   # 保存中
└── status_unsaved.svg  # 未保存
```
