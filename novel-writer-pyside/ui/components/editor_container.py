"""编辑器容器组件，搜索面板浮动在编辑器右上角（VSCode 风格）。"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QSplitter
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QPoint, Property
from PySide6.QtGui import QTextCursor
from ui.components.editor_widget import EditorWidget
from ui.components.search_panel import SearchPanel


class EditorContainer(QWidget):
    search_result_clicked = Signal(int)
    content_changed = Signal()
    ai_continue_requested = Signal()
    ai_polish_requested = Signal()
    ai_rewrite_requested = Signal()
    ai_analyze_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._panel_visible = False
        self._anim_offset = -32  # initial, updated on first show
        self._cached_x = 0
        self._cached_width = 420
        self._cached_height = 32
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._editor = EditorWidget()
        layout.addWidget(self._editor, 1)

        self._editor.content_changed.connect(self.content_changed.emit)
        self._editor.ai_continue_requested.connect(self.ai_continue_requested.emit)
        self._editor.ai_polish_requested.connect(self.ai_polish_requested.emit)
        self._editor.ai_rewrite_requested.connect(self.ai_rewrite_requested.emit)
        self._editor.ai_analyze_requested.connect(self.ai_analyze_requested.emit)

        self._search_panel = SearchPanel(self)
        self._search_panel.setVisible(False)

        self._search_results = QListWidget()
        self._search_results.setObjectName("search_results")
        self._search_results.setVisible(False)
        self._search_results.setMaximumHeight(160)
        self._search_results.itemClicked.connect(self._on_result_clicked)
        layout.addWidget(self._search_results, 0)

        self._anim = QPropertyAnimation(self, b"animOffset", self)
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.Linear)

        self._search_panel.replace_toggled.connect(self._on_replace_toggled)

    def _on_replace_toggled(self, shown: bool):
        """替换栏展开/收起时更新面板位置和 view zone。"""
        if self._search_panel.isVisible() and self._anim_offset >= 0:
            self._position_search_panel()
        self._update_view_zone()

    def _on_result_clicked(self, item):
        index = item.data(Qt.UserRole)
        if index is not None:
            self.search_result_clicked.emit(index)

    def _get_panel_height(self):
        return self._search_panel._get_panel_height()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._search_panel.isVisible():
            self._position_search_panel()

    def _position_search_panel(self):
        """计算并更新面板位置（缓存 x/width/height，动画时只更新 y）。"""
        panel_width = self._search_panel.width()
        panel_height = self._get_panel_height()
        viewport = self._editor.viewport()
        viewport_top_right = viewport.mapTo(self, QPoint(viewport.width(), 0))
        x = viewport_top_right.x() - panel_width - 8
        y = viewport_top_right.y() + 4 + self._anim_offset
        self._cached_x = x
        self._cached_width = panel_width
        self._cached_height = panel_height
        self._search_panel.setGeometry(x, y, panel_width, panel_height)
        if self._anim_offset >= 0:
            self._update_view_zone()

    def _update_view_zone(self):
        """VSCode 的 IViewZone 效果：编辑器顶部添加空间。"""
        h = self._get_panel_height() if self._search_panel.isVisible() and self._anim_offset >= 0 else 0
        # 只设置 viewport 顶部边距 = 面板高度，推开编辑器内容
        self._editor.viewport().setContentsMargins(0, h, 0, 0)

    @Property(float)
    def animOffset(self):
        return self._anim_offset

    @animOffset.setter
    def animOffset(self, value):
        self._anim_offset = value
        if self._search_panel.isVisible():
            viewport = self._editor.viewport()
            y = viewport.mapTo(self, QPoint(0, 0)).y() + 4 + value
            self._search_panel.move(self._cached_x, y)
            # VSCode 不做 view zone 渐变：_showViewZone / _removeViewZone 都是立即执行
            # 面板移动靠 CSS transition (GPU)，view zone 独立管理

    @property
    def editor(self):
        return self._editor

    @property
    def search_panel(self):
        return self._search_panel

    @property
    def search_results(self):
        return self._search_results

    # ---- EditorWidget 代理方法，兼容旧的调用方式 ----

    def is_modified(self) -> bool:
        return self._editor.is_modified()

    def set_modified(self, modified: bool):
        self._editor.set_modified(modified)

    def get_content(self) -> str:
        return self._editor.get_content()

    def set_content(self, text: str):
        self._editor.set_content(text)

    def count_words(self) -> int:
        return self._editor.count_words()

    def count_paragraphs(self) -> int:
        return self._editor.count_paragraphs()

    def document(self):
        return self._editor.document()

    def textCursor(self):
        return self._editor.textCursor()

    def setTextCursor(self, cursor):
        self._editor.setTextCursor(cursor)

    def setExtraSelections(self, selections):
        self._editor.setExtraSelections(selections)

    def ensureCursorVisible(self):
        self._editor.ensureCursorVisible()

    def viewport(self):
        return self._editor.viewport()

    def toPlainText(self) -> str:
        return self._editor.toPlainText()

    def setPlainText(self, text: str):
        self._editor.setPlainText(text)

    @property
    def _modified(self) -> bool:
        return self._editor._modified

    @_modified.setter
    def _modified(self, value: bool):
        self._editor._modified = value

    def show_search(self):
        self._panel_visible = True
        self._search_panel.setVisible(True)
        self._search_panel.raise_()
        # VSCode 风格：view zone 立即添加，面板靠动画滑入
        self._editor.viewport().setContentsMargins(0, self._get_panel_height(), 0, 0)
        # 动画期间禁用阴影
        shadow = self._search_panel.graphicsEffect()
        if shadow:
            shadow.setEnabled(False)
        # 初始定位：面板在编辑区上方（隐藏状态）
        self._anim_offset = -self._get_panel_height()
        self._position_search_panel()
        # 展开动画（清除旧连接防堆积）
        self._anim.stop()
        try:
            self._anim.finished.disconnect()
        except (TypeError, RuntimeError):
            pass
        self._anim.finished.connect(self._on_show_anim_finished)
        self._anim.setStartValue(-self._get_panel_height())
        self._anim.setEndValue(0)
        self._anim.start()

    def _on_show_anim_finished(self):
        try:
            self._anim.finished.disconnect(self._on_show_anim_finished)
        except (TypeError, RuntimeError):
            pass
        self._anim_offset = 0
        self._position_search_panel()
        self._search_panel.focus_search()
        # 恢复阴影
        shadow = self._search_panel.graphicsEffect()
        if shadow:
            shadow.setEnabled(True)

    def hide_search(self):
        self._panel_visible = False
        shadow = self._search_panel.graphicsEffect()
        if shadow:
            shadow.setEnabled(False)
        # VSCode 风格：_removeViewZone 立即执行，不渐变
        self._editor.viewport().setContentsMargins(0, 0, 0, 0)
        self._anim.stop()
        # 确保缓存高度最新（用于动画中的 view zone 渐变）
        self._cached_height = self._get_panel_height()
        try:
            self._anim.finished.disconnect()
        except (TypeError, RuntimeError):
            pass
        self._anim.finished.connect(self._on_hide_anim_finished)
        self._anim.setStartValue(0)
        start_offset = -self._get_panel_height()
        self._anim.setEndValue(start_offset)
        self._anim.start()
        self._search_results.setVisible(False)
        self._search_results.clear()

    def _on_hide_anim_finished(self):
        self._search_panel.setVisible(False)
        # view zone 已在动画中渐变至 0
        try:
            self._anim.finished.disconnect(self._on_hide_anim_finished)
        except (TypeError, RuntimeError):
            pass
        shadow = self._search_panel.graphicsEffect()
        if shadow:
            shadow.setEnabled(True)

    def update_search_results(self, matches, editor):
        self._search_results.clear()
        if not matches:
            self._search_results.setVisible(False)
            return

        self._search_results.setVisible(True)
        doc = editor.document()

        # 按行号分组
        line_groups = {}
        for i, (start, end) in enumerate(matches):
            block = doc.findBlock(start)
            if not block.isValid():
                continue
            line_number = block.blockNumber() + 1
            line_text = block.text()
            if line_number not in line_groups:
                line_groups[line_number] = []
            # 计算匹配词在行内的位置，用于显示上下文
            col = start - block.position()
            line_groups[line_number].append((i, start, end, col, line_text))

        for line_number in sorted(line_groups.keys()):
            group = line_groups[line_number]
            line_text = group[0][4].strip()
            preview = line_text[:100] if len(line_text) > 100 else line_text

            # 首个结果作为分组 header（可点击跳转到该行第一个匹配）
            first = group[0]
            header_text = f"行 {line_number}: {preview}"
            header_item = QListWidgetItem(header_text)
            header_item.setData(Qt.UserRole, first[0])
            header_item.setToolTip(f"行 {line_number} — {len(group)} 个匹配")
            font = header_item.font()
            font.setBold(True)
            header_item.setFont(font)
            self._search_results.addItem(header_item)

            # 行内多个匹配项作为子项
            if len(group) > 1:
                for idx, start, end, col, text in group:
                    # 显示匹配词附近的上下文
                    ctx_start = max(0, col - 10)
                    ctx_end = min(len(text), col + (end - start) + 10)
                    context = text[ctx_start:ctx_end].strip()
                    sub_text = f"  └ 第 {col+1} 列: …{context}…"
                    sub_item = QListWidgetItem(sub_text)
                    sub_item.setData(Qt.UserRole, idx)
                    sub_item.setToolTip(f"位置 {start}-{end}")
                    self._search_results.addItem(sub_item)

    def clear_search_results(self):
        self._search_results.clear()
        self._search_results.setVisible(False)
