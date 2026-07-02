"""搜索替换面板组件。"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QCompleter,
)
from PySide6.QtCore import Signal, Qt, QEvent, QStringListModel


class SearchPanel(QWidget):
    search_text_changed = Signal(str)
    search_next = Signal()
    search_prev = Signal()
    replace = Signal(str, str)
    replace_all = Signal(str, str)
    close_panel = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("search_panel")
        self._replace_visible = False
        self._search_history = []  # 搜索历史列表，最多20条
        self._init_ui()
        self._init_completer()
        self._init_connections()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(2)

        search_row = QHBoxLayout()
        search_row.setSpacing(2)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("查找...")
        search_row.addWidget(self.search_input)

        self.match_label = QLabel("")
        self.match_label.setAlignment(Qt.AlignCenter)
        self.match_label.setMinimumWidth(80)
        search_row.addWidget(self.match_label)

        self.toggle_replace_btn = QPushButton("替换")
        self.toggle_replace_btn.setCheckable(True)
        self.toggle_replace_btn.setMaximumWidth(60)
        search_row.addWidget(self.toggle_replace_btn)

        self.prev_btn = QPushButton("↑")
        self.prev_btn.setMaximumWidth(30)
        search_row.addWidget(self.prev_btn)

        self.next_btn = QPushButton("↓")
        self.next_btn.setMaximumWidth(30)
        search_row.addWidget(self.next_btn)

        self.close_btn = QPushButton("✕")
        self.close_btn.setMaximumWidth(30)
        search_row.addWidget(self.close_btn)

        main_layout.addLayout(search_row)

        self.replace_widget = QWidget()
        replace_layout = QHBoxLayout(self.replace_widget)
        replace_layout.setContentsMargins(0, 0, 0, 0)
        replace_layout.setSpacing(2)

        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("替换为...")
        replace_layout.addWidget(self.replace_input)

        self.replace_btn = QPushButton("替换")
        self.replace_btn.setMaximumWidth(60)
        replace_layout.addWidget(self.replace_btn)

        self.replace_all_btn = QPushButton("全部替换")
        self.replace_all_btn.setMaximumWidth(80)
        replace_layout.addWidget(self.replace_all_btn)

        main_layout.addWidget(self.replace_widget)
        self.replace_widget.setVisible(False)

    def _init_completer(self):
        """初始化搜索历史自动补全。"""
        self._history_model = QStringListModel(self._search_history, self)
        self._completer = QCompleter(self._history_model, self)
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._completer.setMaxVisibleItems(10)
        self.search_input.setCompleter(self._completer)
        self._completer.activated.connect(self._on_history_activated)

    def _init_connections(self):
        self.search_input.textChanged.connect(self.search_text_changed.emit)
        self.prev_btn.clicked.connect(self.search_prev.emit)
        self.next_btn.clicked.connect(self.search_next.emit)
        self.close_btn.clicked.connect(self.close_panel.emit)
        self.toggle_replace_btn.toggled.connect(self.show_replace)
        self.replace_btn.clicked.connect(self._on_replace_clicked)
        self.replace_all_btn.clicked.connect(self._on_replace_all_clicked)
        # Esc 关闭面板
        self.search_input.installEventFilter(self)
        self.replace_input.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is self.search_input:
            if event.type() == QEvent.FocusIn:
                # 焦点进入时显示历史下拉
                if self._search_history:
                    self._completer.complete()
            elif event.type() == QEvent.KeyPress and event.key() == Qt.Key_Return:
                # 回车执行搜索时加入历史
                text = self.search_input.text().strip()
                if text:
                    self._add_to_history(text)
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            self.close_panel.emit()
            return True
        return super().eventFilter(obj, event)

    def _on_history_activated(self, text: str):
        """用户从历史下拉列表中选择搜索词。"""
        self._add_to_history(text)

    def _add_to_history(self, text: str):
        """添加搜索词到历史记录（去重，最多20条）。"""
        text = text.strip()
        if not text:
            return
        # 去重：如果已存在，移除旧位置
        if text in self._search_history:
            self._search_history.remove(text)
        # 插入到最前面（最近搜索）
        self._search_history.insert(0, text)
        # 限制最多20条
        if len(self._search_history) > 20:
            self._search_history.pop()
        # 更新 completer 模型
        self._history_model.setStringList(self._search_history)

    def _on_replace_clicked(self):
        search_text = self.search_input.text()
        replace_text = self.replace_input.text()
        self.replace.emit(search_text, replace_text)

    def _on_replace_all_clicked(self):
        search_text = self.search_input.text()
        replace_text = self.replace_input.text()
        self.replace_all.emit(search_text, replace_text)

    def set_search_text(self, text: str):
        self.search_input.setText(text)

    def set_match_count(self, current: int, total: int):
        if total == 0:
            self.match_label.setText("")
        else:
            self.match_label.setText(f"第 {current} 个，共 {total} 个")

    def show_replace(self, show: bool):
        self._replace_visible = show
        self.replace_widget.setVisible(show)
        self.toggle_replace_btn.setChecked(show)

    def clear(self):
        self.search_input.clear()
        self.replace_input.clear()
        self.match_label.setText("")

    def focus_search(self):
        self.search_input.setFocus()
        self.search_input.selectAll()
