"""搜索替换面板组件（VSCode 风格浮动面板）。"""
import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QCompleter, QGraphicsDropShadowEffect, QFrame, QSizePolicy,
)
from PySide6.QtCore import Signal, Qt, QEvent, QStringListModel, QPoint, QTimer, QStandardPaths
from PySide6.QtGui import QColor, QCursor, QFont, QFontDatabase

# Codicon 图标码点（来自 VSCode codiconsLibrary.ts）
_ICON_CHEVRON_RIGHT = '\ueab6'
_ICON_CHEVRON_DOWN = '\ueab4'
_ICON_CASE_SENSITIVE = '\ueab1'
_ICON_REGEX = '\ueb38'
_ICON_SELECTION = '\ueb85'
_ICON_PRESERVE_CASE = '\ueb2e'
_ICON_WHOLE_WORD = '\ueb7e'
_ICON_REPLACE = '\ueb3d'
_ICON_REPLACE_ALL = '\ueb3c'
_ICON_ARROW_UP = '\ueaa1'
_ICON_ARROW_DOWN = '\uea9a'
_ICON_CLOSE = '\uea76'
_ICON_ARROW_LEFT = '\uea99'  # 反向查找

_codicon_font_id = None


def _load_codicon_font():
    """加载 Codicon 图标字体（仅加载一次）。"""
    global _codicon_font_id
    if _codicon_font_id is not None:
        return _codicon_font_id
    font_path = os.path.join(
        os.path.dirname(__file__), '..', '..', 'assets', 'fonts', 'codicon.ttf'
    )
    font_path = os.path.normpath(font_path)
    if os.path.exists(font_path):
        _codicon_font_id = QFontDatabase.addApplicationFont(font_path)
        if _codicon_font_id != -1:
            families = QFontDatabase.applicationFontFamilies(_codicon_font_id)
            if families:
                return _codicon_font_id
    return -1


def _codicon_font(size: int = 13) -> QFont:
    """获取 Codicon 字体。"""
    _load_codicon_font()
    return QFont("codicon", size)


class ResizeSash(QWidget):
    """左侧垂直拖拽条，用于调整搜索面板宽度。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("resize_sash")
        self.setFixedWidth(4)
        self.setCursor(Qt.SizeHorCursor)
        self._dragging = False
        self._start_x = 0
        self._start_width = 0

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._start_x = event.globalPosition().x()
            self._start_width = self.parent().width()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging and self.parent():
            dx = self._start_x - event.globalPosition().x()
            new_width = int(self._start_width + dx)
            new_width = max(280, min(800, new_width))
            self.parent().setFixedWidth(new_width)
            if hasattr(self.parent(), 'width_changed'):
                self.parent().width_changed.emit(new_width)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)


class SearchHistoryManager:
    """搜索/替换历史持久化管理器。"""

    _HISTORY_FILE = "search_history.json"

    @classmethod
    def _get_path(cls) -> str:
        data_dir = os.path.join(
            QStandardPaths.writableLocation(QStandardPaths.AppDataLocation),
            "novel-writer"
        )
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, cls._HISTORY_FILE)

    @classmethod
    def load(cls) -> tuple[list[str], list[str]]:
        try:
            with open(cls._get_path(), "r", encoding="utf-8") as f:
                data = json.load(f)
            search = data.get("search", [])
            replace = data.get("replace", [])
            return search[:20], replace[:20]
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return [], []

    @classmethod
    def save(cls, search_history: list[str], replace_history: list[str]):
        try:
            with open(cls._get_path(), "w", encoding="utf-8") as f:
                json.dump({"search": search_history[:20], "replace": replace_history[:20]}, f, ensure_ascii=False)
        except OSError:
            pass


class SearchPanel(QWidget):
    search_text_changed = Signal(str)
    search_next = Signal()
    search_prev = Signal()
    replace = Signal(str, str)
    replace_all = Signal(str, str)
    close_panel = Signal()
    search_options_changed = Signal()
    replace_toggled = Signal(bool)
    width_changed = Signal(int)
    in_selection_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("search_panel")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedWidth(420)
        self._replace_visible = False
        self._search_history = []
        self._replace_history = []
        self._case_sensitive = False
        self._use_regex = False
        self._in_selection = False
        self._preserve_case = False
        self._whole_word = False
        self._search_backward = False
        # 从持久化文件加载历史
        self._search_history, self._replace_history = SearchHistoryManager.load()
        self._init_ui()
        self._init_buttons()
        self._init_shadow()
        self._init_completer()
        self._init_connections()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 最外层水平布局：左侧 sash + 右侧内容
        outer = QHBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        self._resize_sash = ResizeSash(self)
        outer.addWidget(self._resize_sash, 0)

        # 右侧内容容器
        content = QWidget()
        content.setObjectName("panel_content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 两个输入行共享同一布局（VSCode 风格：find-part / replace-part 同级同边距）
        control_rows = QVBoxLayout()
        control_rows.setContentsMargins(17, 6, 25, 6)  # left=17(toggle), right=25(close), top/bottom=背景留白
        control_rows.setSpacing(0)

        # === 搜索行 ===
        find_row = QHBoxLayout()
        find_row.setContentsMargins(4, 4, 4, 4)
        find_row.setSpacing(3)

        # 搜索框容器（VSCode 风格：输入框 100% 宽度，controls absolute 叠加在右侧）
        self._search_container = QFrame()
        self._search_container.setObjectName("search_input_container")
        search_inner = QHBoxLayout(self._search_container)
        search_inner.setContentsMargins(6, 0, 2, 0)
        search_inner.setSpacing(0)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("search_input_inner")
        self.search_input.setPlaceholderText("查找")
        self.search_input.setFrame(False)
        search_inner.addWidget(self.search_input, 1)

        find_row.addWidget(self._search_container, 1)

        self.match_label = QLabel("")
        self.match_label.setObjectName("match_label_inline")
        self.match_label.setAlignment(Qt.AlignCenter)
        self.match_label.setMinimumWidth(40)  # MAX_MATCHES_COUNT_WIDTH
        find_row.addWidget(self.match_label, 0)

        # controls 按钮（VSCode 风格：absolute 叠在输入框右侧）
        self.case_btn = QPushButton(_ICON_CASE_SENSITIVE)
        self.case_btn.setObjectName("option_btn")
        self.case_btn.setFont(_codicon_font(13))
        self.case_btn.setCheckable(True)
        self.case_btn.setFixedSize(20, 20)
        self.case_btn.setToolTip("区分大小写")
        self.case_btn.setParent(self._search_container)
        self.case_btn.show()

        self.regex_btn = QPushButton(_ICON_REGEX)
        self.regex_btn.setObjectName("option_btn")
        self.regex_btn.setFont(_codicon_font(13))
        self.regex_btn.setCheckable(True)
        self.regex_btn.setFixedSize(20, 20)
        self.regex_btn.setToolTip("使用正则表达式")
        self.regex_btn.setParent(self._search_container)
        self.regex_btn.show()

        self.whole_word_btn = QPushButton(_ICON_WHOLE_WORD)
        self.whole_word_btn.setObjectName("option_btn")
        self.whole_word_btn.setFont(_codicon_font(13))
        self.whole_word_btn.setCheckable(True)
        self.whole_word_btn.setFixedSize(20, 20)
        self.whole_word_btn.setToolTip("全词匹配")
        self.whole_word_btn.setParent(self._search_container)
        self.whole_word_btn.show()

        # 反向查找按钮
        self.backward_btn = QPushButton(_ICON_ARROW_LEFT)
        self.backward_btn.setObjectName("option_btn")
        self.backward_btn.setFont(_codicon_font(13))
        self.backward_btn.setCheckable(True)
        self.backward_btn.setFixedSize(20, 20)
        self.backward_btn.setToolTip("反向查找")
        self.backward_btn.setParent(self._search_container)
        self.backward_btn.show()

        # 导航按钮
        self.prev_btn = QPushButton(_ICON_ARROW_UP)
        self.prev_btn.setObjectName("nav_btn")
        self.prev_btn.setFont(_codicon_font(13))
        self.prev_btn.setFixedSize(20, 20)
        self.prev_btn.setToolTip("上一个 (Shift+Enter)")
        find_row.addWidget(self.prev_btn)

        self.next_btn = QPushButton(_ICON_ARROW_DOWN)
        self.next_btn.setObjectName("nav_btn")
        self.next_btn.setFont(_codicon_font(13))
        self.next_btn.setFixedSize(20, 20)
        self.next_btn.setToolTip("下一个 (Enter)")
        find_row.addWidget(self.next_btn)

        # 在选区内查找
        self.selection_btn = QPushButton(_ICON_SELECTION)
        self.selection_btn.setObjectName("option_btn")
        self.selection_btn.setFont(_codicon_font(13))
        self.selection_btn.setCheckable(True)
        self.selection_btn.setFixedSize(20, 20)
        self.selection_btn.setToolTip("在选区内查找")
        self.selection_btn.setEnabled(False)
        find_row.addWidget(self.selection_btn)

        control_rows.addLayout(find_row)

        # === 替换行（可展开） ===
        self.replace_widget = QWidget()
        self._replace_layout = QHBoxLayout(self.replace_widget)
        self._replace_layout.setContentsMargins(4, 4, 4, 4)
        self._replace_layout.setSpacing(3)

        # 替换框容器（VSCode 风格：输入框 100%，controls absolute）
        self._replace_container = QFrame()
        self._replace_container.setObjectName("search_input_container")
        replace_inner = QHBoxLayout(self._replace_container)
        replace_inner.setContentsMargins(6, 0, 2, 0)
        replace_inner.setSpacing(0)

        self.replace_input = QLineEdit()
        self.replace_input.setObjectName("replace_input_inner")
        self.replace_input.setPlaceholderText("替换为")
        self.replace_input.setFrame(False)
        replace_inner.addWidget(self.replace_input, 1)

        self._replace_layout.addWidget(self._replace_container, 1)
        self._replace_layout.setStretch(0, 1)

        self.preserve_case_btn = QPushButton(_ICON_PRESERVE_CASE)
        self.preserve_case_btn.setObjectName("option_btn")
        self.preserve_case_btn.setFont(_codicon_font(13))
        self.preserve_case_btn.setCheckable(True)
        self.preserve_case_btn.setFixedSize(24, 20)
        self.preserve_case_btn.setToolTip("保持大小写 (Preserve Case)")
        self.preserve_case_btn.setParent(self._replace_container)
        self.preserve_case_btn.show()

        self.replace_btn = QPushButton(_ICON_REPLACE)
        self.replace_btn.setObjectName("replace_btn")
        self.replace_btn.setFont(_codicon_font(13))
        self.replace_btn.setFixedSize(24, 22)
        self.replace_btn.setToolTip("替换")
        self._replace_layout.addWidget(self.replace_btn)

        self.replace_all_btn = QPushButton(_ICON_REPLACE_ALL)
        self.replace_all_btn.setObjectName("replace_btn")
        self.replace_all_btn.setFont(_codicon_font(13))
        self.replace_all_btn.setFixedSize(24, 22)
        self.replace_all_btn.setToolTip("全部替换")
        self._replace_layout.addWidget(self.replace_all_btn)

        # VSCode：右侧 stretch  spacer 吸收多余空间，容器/按钮紧贴左侧
        self._replace_layout.addStretch(0)

        control_rows.addWidget(self.replace_widget)
        self.replace_widget.setVisible(False)

        content_layout.addLayout(control_rows, 1)
        outer.addWidget(content, 1)
        main_layout.addLayout(outer, 1)

    def _init_buttons(self):
        """初始化绝对定位的 toggle 和 close 按钮（VSCode 风格）。"""
        # 展开替换按钮
        self.toggle_replace_btn = QPushButton(_ICON_CHEVRON_RIGHT)
        self.toggle_replace_btn.setObjectName("toggle_replace_btn")
        self.toggle_replace_btn.setFont(_codicon_font(13))
        self.toggle_replace_btn.setCheckable(True)
        self.toggle_replace_btn.setToolTip("展开替换")
        self.toggle_replace_btn.setParent(self)
        self.toggle_replace_btn.show()

        # 关闭按钮
        self.close_btn = QPushButton(_ICON_CLOSE)
        self.close_btn.setObjectName("close_btn")
        self.close_btn.setFont(_codicon_font(13))
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setToolTip("关闭 (Esc)")
        self.close_btn.setParent(self)
        self.close_btn.show()

        self._position_buttons()
        self._position_controls()

    def _position_buttons(self):
        """根据面板当前尺寸定位 toggle 和 close 按钮。"""
        ph = self._get_panel_height()
        sash_w = self._resize_sash.width()
        # toggle 按钮：左侧垂直占满（VSCode 的 left:0; top:0; height:-webkit-fill-available）
        self.toggle_replace_btn.setGeometry(sash_w, 0, 18, ph)
        # close 按钮：右上角（VSCode 的 right:4px; top:5px）
        pw = self.width()
        self.close_btn.move(pw - self.close_btn.width() - 4, 5)

    def _get_panel_height(self):
        """根据实际内容计算面板高度（替代硬编码）。"""
        tb = 6 + 8  # control_rows top + bottom margin
        find_h = 4 + self._search_container.sizeHint().height() + 4  # find_row margins(4,4) + container
        if self._replace_visible and self.replace_widget.isVisible():
            rep_h = 4 + self._replace_container.sizeHint().height() + 4
            return tb + find_h + rep_h
        return tb + find_h

    def _position_controls(self):
        """定位容器内叠加的控制按钮（VSCode 的 position: absolute; right: 2px; top: 3px）。"""
        # 搜索容器 controls：case/wholeWord/backward/regex（VSCode 第 963-989 行顺序）
        cw = self._search_container.width()
        ch = self._search_container.height()
        x = cw - 2  # right edge
        btns = []
        if self.case_btn.isVisibleTo(self._search_container):
            btns.append(self.case_btn)
        if self.whole_word_btn.isVisibleTo(self._search_container):
            btns.append(self.whole_word_btn)
        if self.backward_btn.isVisibleTo(self._search_container):
            btns.append(self.backward_btn)
        if self.regex_btn.isVisibleTo(self._search_container):
            btns.append(self.regex_btn)
        for btn in reversed(btns):
            x -= btn.width()
            btn.move(x, max(0, (ch - btn.height()) // 2))
            x -= 2  # spacing

        # 替换容器 controls：preserve_case
        rw = self._replace_container.width()
        rh = self._replace_container.height()
        pc_visible = self.preserve_case_btn.isVisibleTo(self._replace_container)
        if pc_visible:
            self.preserve_case_btn.move(
                rw - self.preserve_case_btn.width() - 2,
                max(0, (rh - self.preserve_case_btn.height()) // 2)
            )

        # 更新输入框 textMargins（VSCode 的 updateInputBoxPadding）
        btn_w = sum(b.width() for b in btns) + len(btns) * 2 if btns else 0
        self.search_input.setTextMargins(0, 0, btn_w, 0)
        pc_w = self.preserve_case_btn.width() + 2 if pc_visible else 0
        self.replace_input.setTextMargins(0, 0, pc_w, 0)

    def _init_shadow(self):
        """添加阴影效果，使搜索面板看起来浮在编辑器上方。"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 6)
        self.setGraphicsEffect(shadow)

    def _init_completer(self):
        """初始化搜索历史和替换历史自动补全。"""
        self._search_history_model = QStringListModel(self._search_history, self)
        self._search_completer = QCompleter(self._search_history_model, self)
        self._search_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._search_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._search_completer.setMaxVisibleItems(10)
        self.search_input.setCompleter(self._search_completer)
        self._search_completer.activated.connect(self._on_search_history_activated)

        self._replace_history_model = QStringListModel(self._replace_history, self)
        self._replace_completer = QCompleter(self._replace_history_model, self)
        self._replace_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._replace_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._replace_completer.setMaxVisibleItems(10)
        self.replace_input.setCompleter(self._replace_completer)
        self._replace_completer.activated.connect(self._on_replace_history_activated)

    def _init_connections(self):
        self.search_input.textChanged.connect(self.search_text_changed.emit)
        self.prev_btn.clicked.connect(self.search_prev.emit)
        self.next_btn.clicked.connect(self.search_next.emit)
        self.close_btn.clicked.connect(self.close_panel.emit)
        self.toggle_replace_btn.toggled.connect(self.show_replace)
        self.replace_btn.clicked.connect(self._on_replace_clicked)
        self.replace_all_btn.clicked.connect(self._on_replace_all_clicked)
        self.case_btn.toggled.connect(self._on_options_changed)
        self.regex_btn.toggled.connect(self._on_options_changed)
        self.whole_word_btn.toggled.connect(self._on_options_changed)
        self.selection_btn.toggled.connect(self._on_selection_changed)
        self.preserve_case_btn.toggled.connect(self._on_preserve_case_changed)
        self.backward_btn.toggled.connect(self._on_backward_changed)
        # Esc 关闭面板
        self.search_input.installEventFilter(self)
        self.replace_input.installEventFilter(self)
        # 回车触发替换操作
        self.replace_input.returnPressed.connect(self._on_replace_clicked)

    def _on_options_changed(self):
        """大小写/正则/全词匹配切换时触发重新搜索。"""
        self._case_sensitive = self.case_btn.isChecked()
        self._use_regex = self.regex_btn.isChecked()
        self._whole_word = self.whole_word_btn.isChecked()
        self.search_options_changed.emit()

    def _on_selection_changed(self, checked: bool):
        """选区查找切换时触发重新搜索。"""
        self._in_selection = checked
        self.in_selection_changed.emit(checked)
        self.search_options_changed.emit()

    def set_selection_available(self, available: bool):
        """设置选区按钮是否可用。"""
        self.selection_btn.setEnabled(available)
        if not available:
            self.selection_btn.setChecked(False)

    def _on_preserve_case_changed(self, checked: bool):
        """Preserve Case 切换处理。"""
        self._preserve_case = checked

    def _on_backward_changed(self, checked: bool):
        """反向查找切换。"""
        self._search_backward = checked
        self.search_options_changed.emit()

    @property
    def search_backward(self):
        return self._search_backward

    @property
    def in_selection(self):
        return self._in_selection

    @property
    def preserve_case(self):
        return self._preserve_case

    @property
    def case_sensitive(self):
        return self._case_sensitive

    @property
    def use_regex(self):
        return self._use_regex

    @property
    def whole_word(self):
        return self._whole_word

    @property
    def replace_visible(self):
        return self._replace_visible

    def eventFilter(self, obj, event):
        if obj is self.search_input:
            container = self.search_input.parentWidget()
            if event.type() == QEvent.FocusIn:
                if container:
                    container.setProperty("focused", True)
                    container.style().unpolish(container)
                    container.style().polish(container)
                if not self.search_input.text():
                    self.search_input.setPlaceholderText("查找（使用 ↑↓ 查看历史记录）")
            elif event.type() == QEvent.FocusOut:
                if container:
                    container.setProperty("focused", False)
                    container.style().unpolish(container)
                    container.style().polish(container)
                self.search_input.setPlaceholderText("查找")
            elif event.type() == QEvent.KeyPress:
                key = event.key()
                if key == Qt.Key_Return:
                    text = self.search_input.text().strip()
                    if text:
                        self._add_search_history(text)
                    if event.modifiers() & Qt.ShiftModifier:
                        self.search_prev.emit()
                    else:
                        self.search_next.emit()
                    return True
                elif key == Qt.Key_Up:
                    self._cycle_search_history(-1)
                    return True
                elif key == Qt.Key_Down:
                    self._cycle_search_history(1)
                    return True
        elif obj is self.replace_input:
            if event.type() == QEvent.FocusIn:
                container = self.replace_input.parentWidget()
                if container:
                    container.setProperty("focused", True)
                    container.style().unpolish(container)
                    container.style().polish(container)
                if not self.replace_input.text():
                    self.replace_input.setPlaceholderText("替换为（使用 ↑↓ 查看历史记录）")
            elif event.type() == QEvent.FocusOut:
                container = self.replace_input.parentWidget()
                if container:
                    container.setProperty("focused", False)
                    container.style().unpolish(container)
                    container.style().polish(container)
                self.replace_input.setPlaceholderText("替换为")
            elif event.type() == QEvent.KeyPress:
                key = event.key()
                if key == Qt.Key_Up:
                    self._cycle_replace_history(-1)
                    return True
                elif key == Qt.Key_Down:
                    self._cycle_replace_history(1)
                    return True
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            self.close_panel.emit()
            return True
        return super().eventFilter(obj, event)

    def _cycle_search_history(self, direction: int):
        """↑/↓ 浏览搜索历史（VSCode 风格）。"""
        if not self._search_history:
            return
        current = self.search_input.text()
        if current in self._search_history:
            idx = self._search_history.index(current)
            new_idx = idx - direction
            if 0 <= new_idx < len(self._search_history):
                self.search_input.setText(self._search_history[new_idx])
            elif direction == -1 and new_idx < 0:
                self.search_input.setText(self._search_history[-1])
            elif direction == 1 and new_idx >= len(self._search_history):
                self.search_input.setText("")
        else:
            if direction == -1:
                self.search_input.setText(self._search_history[0])
            else:
                self.search_input.setText("")

    def _cycle_replace_history(self, direction: int):
        """↑/↓ 浏览替换历史。"""
        if not self._replace_history:
            return
        current = self.replace_input.text()
        if current in self._replace_history:
            idx = self._replace_history.index(current)
            new_idx = idx - direction
            if 0 <= new_idx < len(self._replace_history):
                self.replace_input.setText(self._replace_history[new_idx])
            elif direction == -1 and new_idx < 0:
                self.replace_input.setText(self._replace_history[-1])
            elif direction == 1 and new_idx >= len(self._replace_history):
                self.replace_input.setText("")
        else:
            if direction == -1:
                self.replace_input.setText(self._replace_history[0])
            else:
                self.replace_input.setText("")

    def _on_search_history_activated(self, text: str):
        self._add_search_history(text)

    def _on_replace_history_activated(self, text: str):
        self._add_replace_history(text)

    def _add_search_history(self, text: str):
        text = text.strip()
        if not text:
            return
        if text in self._search_history:
            self._search_history.remove(text)
        self._search_history.insert(0, text)
        if len(self._search_history) > 20:
            self._search_history.pop()
        self._search_history_model.setStringList(self._search_history)
        SearchHistoryManager.save(self._search_history, self._replace_history)

    def _add_replace_history(self, text: str):
        text = text.strip()
        if not text:
            return
        if text in self._replace_history:
            self._replace_history.remove(text)
        self._replace_history.insert(0, text)
        if len(self._replace_history) > 20:
            self._replace_history.pop()
        self._replace_history_model.setStringList(self._replace_history)
        SearchHistoryManager.save(self._search_history, self._replace_history)

    def _on_replace_clicked(self):
        search_text = self.search_input.text()
        replace_text = self.replace_input.text()
        self._add_search_history(search_text)
        self._add_replace_history(replace_text)
        self.replace.emit(search_text, replace_text)

    def _on_replace_all_clicked(self):
        search_text = self.search_input.text()
        replace_text = self.replace_input.text()
        self._add_search_history(search_text)
        self._add_replace_history(replace_text)
        self.replace_all.emit(search_text, replace_text)

    def set_search_text(self, text: str):
        self.search_input.setText(text)

    def set_match_count(self, current: int, total: int):
        if total == 0:
            self.match_label.setText("无结果")
            self.match_label.setStyleSheet("color: #f7768e;")
        else:
            self.match_label.setText(f"{current}/{total}")
            self.match_label.setStyleSheet("")

    def show_replace(self, show: bool):
        self._replace_visible = show
        self.toggle_replace_btn.setText(_ICON_CHEVRON_RIGHT if not show else _ICON_CHEVRON_DOWN)
        self.toggle_replace_btn.setChecked(show)
        if show:
            self.replace_widget.setVisible(True)
            self.updateGeometry()
            self._replace_layout.activate()
            self._sync_replace_width()
        else:
            self.replace_widget.setVisible(False)
        self._position_controls()
        self.replace_toggled.emit(show)

    def _sync_replace_width(self):
        """VSCode 风格：替换容器宽度 = 搜索容器宽度。"""
        if self._replace_visible:
            w = self._search_container.width()
            self._replace_container.setFixedWidth(w)
            self._replace_layout.setStretch(0, 0)  # 容器不拉伸
            self._replace_layout.setStretch(3, 1)  # spacer 吸收剩余空间
        else:
            self._replace_container.setFixedWidth(16777215)
            self._replace_layout.setStretch(0, 1)  # 容器拉伸填充
            self._replace_layout.setStretch(3, 0)  # spacer 不拉伸
        self._position_controls()

    def clear(self):
        self.search_input.clear()
        self.replace_input.clear()
        self.match_label.setText("")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_buttons()
        self._position_controls()
        if self._replace_visible and self.replace_widget.isVisible():
            self._sync_replace_width()
        self._update_responsive_layout(event.size().width())

    def _update_responsive_layout(self, width: int):
        """根据宽度响应式调整可见元素（VSCode 风格优先级）。"""
        changed = False
        if width < 300:
            self.selection_btn.setVisible(False)
            self.whole_word_btn.setVisible(False)
            self.regex_btn.setVisible(False)
            self.case_btn.setVisible(False)
            self.backward_btn.setVisible(False)
            self.prev_btn.setVisible(False)
            self.next_btn.setVisible(False)
            self.close_btn.setVisible(True)
            changed = True
        elif width < 330:
            self.selection_btn.setVisible(False)
            self.whole_word_btn.setVisible(False)
            self.regex_btn.setVisible(False)
            self.case_btn.setVisible(False)
            self.backward_btn.setVisible(False)
            self.prev_btn.setVisible(True)
            self.next_btn.setVisible(True)
            self.close_btn.setVisible(True)
            changed = True
        elif width < 360:
            self.selection_btn.setVisible(False)
            self.whole_word_btn.setVisible(False)
            self.regex_btn.setVisible(False)
            self.case_btn.setVisible(True)
            self.backward_btn.setVisible(True)
            self.prev_btn.setVisible(True)
            self.next_btn.setVisible(True)
            self.close_btn.setVisible(True)
            changed = True
        elif width < 400:
            self.selection_btn.setVisible(True)
            self.whole_word_btn.setVisible(False)
            self.regex_btn.setVisible(False)
            self.case_btn.setVisible(True)
            self.backward_btn.setVisible(True)
            self.prev_btn.setVisible(True)
            self.next_btn.setVisible(True)
            self.close_btn.setVisible(True)
            changed = True
        else:
            self.selection_btn.setVisible(True)
            self.whole_word_btn.setVisible(True)
            self.regex_btn.setVisible(True)
            self.case_btn.setVisible(True)
            self.backward_btn.setVisible(True)
            self.prev_btn.setVisible(True)
            self.next_btn.setVisible(True)
            self.close_btn.setVisible(True)
            changed = True
        if changed:
            self._position_controls()

    def focus_search(self):
        self.search_input.setFocus()
        self.search_input.selectAll()
        if not self.search_input.text():
            self.set_match_count(0, 0)
