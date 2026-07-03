"""大纲面板组件 - 展示写作方法论的节点结构。"""
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QProgressBar, QFrame, QStackedWidget, QComboBox, QPushButton,
    QMenu,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QCursor

from core.methods.advisor import method_advisor
from core.methods.base import WritingMethod

from core.methods.registry import get_method, list_methods, PlotNode


def _resolve_method_id(method_id_or_name: str) -> str:
    """解析方法 ID，支持英文 ID 和中文名称。"""
    if not method_id_or_name:
        return None
    # 先尝试直接查 ID
    if get_method(method_id_or_name):
        return method_id_or_name
    # 再尝试按名称精确匹配
    for method in list_methods():
        if method.name == method_id_or_name or method.id == method_id_or_name:
            return method.id
    # 模糊匹配1：互相包含
    for method in list_methods():
        if method_id_or_name in method.name or method.name in method_id_or_name:
            return method.id
    # 模糊匹配2：关键字匹配（"三幕" -> "三幕结构"）
    keywords_map = {
        "三幕": "three-act",
        "英雄": "hero-journey",
        "故事圈": "story-circle",
        "七点": "seven-point",
        "皮克斯": "pixar-formula",
        "雪花": "snowflake",
        "自由": "freestyle",
    }
    for kw, mid in keywords_map.items():
        if kw in method_id_or_name:
            return mid
    return None


class OutlineNodeWidget(QFrame):
    """单个大纲节点组件。"""
    node_clicked = Signal(int)  # 发射被点击章节的 chapter_id

    def __init__(self, node: PlotNode, chapter_data: list[dict] = None, parent=None):
        """
        :param node: PlotNode 实例
        :param chapter_data: 与该节点关联的章节数据列表，每个元素为
                             {'id': int, 'number': int, 'title': str}
        """
        super().__init__(parent)
        self._node = node
        self._chapter_data = chapter_data or []
        self.setObjectName("outline_node")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        name_label = QLabel(self._node.name)
        name_font = QFont()
        name_font.setBold(True)
        name_font.setPointSize(11)
        name_label.setFont(name_font)
        name_label.setObjectName("node_name")
        header_layout.addWidget(name_label)

        header_layout.addStretch()

        self.range_label = QLabel(self._node.chapter_range)
        self.range_label.setObjectName("node_range")
        # 如果有关联章节，让标签可点击
        if self._chapter_data:
            self.range_label.setCursor(QCursor(Qt.PointingHandCursor))
            self.range_label.mousePressEvent = self._on_range_clicked
        header_layout.addWidget(self.range_label)

        layout.addLayout(header_layout)

        desc_label = QLabel(self._node.description)
        desc_label.setObjectName("node_description")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("node_progress")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        layout.addWidget(self.progress_bar)

    def _on_range_clicked(self, event):
        """章节范围标签点击事件。"""
        if not self._chapter_data:
            return
        if len(self._chapter_data) == 1:
            ch = self._chapter_data[0]
            self.node_clicked.emit(ch['id'])
        else:
            # 跨多章时显示下拉菜单让用户选择
            menu = QMenu(self)
            for ch in self._chapter_data:
                action = menu.addAction(f"第{ch['number']}章 {ch['title']}")
                action.setData(ch['id'])
            action = menu.exec(QCursor.pos())
            if action:
                self.node_clicked.emit(action.data())

    def set_progress(self, value: int):
        self.progress_bar.setValue(value)
        self.progress_bar.setTextVisible(value > 0)
        self.progress_bar.setFormat(f"{value}%")


class OutlinePanel(QWidget):
    """大纲面板 - 展示写作方法论的节点结构。"""

    method_changed = Signal(str)  # 写作方法变更信号
    navigate_to_chapter = Signal(int)  # 导航到指定章节

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("outline_panel")
        self._current_method_id = None
        self._node_widgets = {}
        self._current_method: Optional[WritingMethod] = None
        self._method_combo: Optional[QComboBox] = None
        self._stage_widgets: list[QWidget] = []
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        title_widget = QWidget()
        title_widget.setObjectName("outline_header")
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(16, 12, 16, 8)
        title_layout.setSpacing(2)

        self.title_label = QLabel("大纲")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        self.title_label.setFont(title_font)
        self.title_label.setObjectName("outline_title")
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_layout.addWidget(self.title_label)

        main_layout.addWidget(title_widget)

        # 写作方法选择器
        selector_widget = QWidget()
        selector_widget.setObjectName("method_selector")
        selector_layout = QHBoxLayout(selector_widget)
        selector_layout.setContentsMargins(16, 4, 16, 4)
        selector_layout.setSpacing(8)

        combo_label = QLabel("写作方法:")
        self._method_combo = QComboBox()
        self._method_combo.addItem("无")
        self._method_names = list(method_advisor.list_methods())
        for name in self._method_names:
            self._method_combo.addItem(name)
        self._method_combo.currentTextChanged.connect(self._on_method_changed)
        selector_layout.addWidget(combo_label)
        selector_layout.addWidget(self._method_combo, 1)

        self._convert_btn = QPushButton("转换")
        self._convert_btn.setObjectName("convert_method_btn")
        self._convert_btn.setMaximumWidth(50)
        self._convert_btn.clicked.connect(self._on_convert_method)
        self._convert_btn.setEnabled(False)
        selector_layout.addWidget(self._convert_btn)

        main_layout.addWidget(selector_widget)

        # 阶段指示器容器
        self._stages_container = QWidget()
        self._stages_container.setObjectName("outline_stages")
        self._stages_layout = QHBoxLayout(self._stages_container)
        self._stages_layout.setContentsMargins(16, 0, 16, 8)
        self._stages_layout.setSpacing(4)
        self._stages_container.setVisible(False)
        main_layout.addWidget(self._stages_container)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("outline_stack")

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setObjectName("outline_scroll")

        self.scroll_content = QWidget()
        self.nodes_layout = QVBoxLayout(self.scroll_content)
        self.nodes_layout.setContentsMargins(16, 8, 16, 16)
        self.nodes_layout.setSpacing(8)

        self.scroll_area.setWidget(self.scroll_content)
        self.stacked_widget.addWidget(self.scroll_area)

        self.empty_label = QLabel("未选择方法")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setContentsMargins(16, 40, 16, 40)
        self.empty_label.setObjectName("outline_empty")
        self.stacked_widget.addWidget(self.empty_label)

        self.stacked_widget.setCurrentWidget(self.empty_label)
        main_layout.addWidget(self.stacked_widget)

    def _clear_nodes(self):
        while self.nodes_layout.count() > 0:
            item = self.nodes_layout.takeAt(0)
            if item and item.widget():
                w = item.widget()
                w.setParent(None)
                w.deleteLater()
        self._node_widgets.clear()

    def load_method(self, method_id: str, node_chapters: dict[str, list[dict]] = None):
        """
        加载写作方法及其节点。

        :param method_id: 方法 ID
        :param node_chapters: 可选的节点-章节映射，格式为
                              {node_name: [{'id': int, 'number': int, 'title': str}, ...]}
        """
        if not method_id:
            self.clear()
            return

        resolved_id = _resolve_method_id(method_id)
        if not resolved_id:
            self.clear()
            return

        method = get_method(resolved_id)
        if not method:
            self.clear()
            return

        self._current_method_id = method_id
        self._clear_nodes()

        self.title_label.setText(method.name)
        self.stacked_widget.setCurrentWidget(self.scroll_area)

        for node in method.plot_nodes:
            ch_data = (node_chapters or {}).get(node.name, [])
            node_widget = OutlineNodeWidget(node, chapter_data=ch_data)
            node_widget.node_clicked.connect(self._on_node_chapter_clicked)
            self._node_widgets[node.name] = node_widget
            self.nodes_layout.addWidget(node_widget)

        self.nodes_layout.addStretch()

    def _on_node_chapter_clicked(self, chapter_id: int):
        """OutlineNodeWidget 的章节被点击时转发信号。"""
        self.navigate_to_chapter.emit(chapter_id)

    def set_progress(self, node_progress: dict):
        for node_name, progress in node_progress.items():
            if node_name in self._node_widgets:
                self._node_widgets[node_name].set_progress(progress)

    def clear(self):
        self._current_method_id = None
        self._current_method = None
        self.title_label.setText("大纲")
        self.stacked_widget.setCurrentWidget(self.empty_label)
        self._clear_nodes()
        self._clear_stages()
        if self._method_combo:
            self._method_combo.blockSignals(True)
            self._method_combo.setCurrentIndex(0)
            self._method_combo.blockSignals(False)

    def _on_method_changed(self, method_name: str):
        """写作方法变更。"""
        if not method_name or method_name == "无":
            self._current_method = None
        else:
            self._current_method = method_advisor.get_method(method_name)

        # 清除旧的阶段显示
        self._clear_stages()

        if self._current_method:
            # 显示方法阶段
            self._show_stages(self._current_method)

        # 启用/禁用转换按钮
        self._convert_btn.setEnabled(method_name != "无" and len(self._method_names) > 1)

        # 发射信号通知
        self.method_changed.emit(method_name)

    def _clear_stages(self):
        """清除阶段显示。"""
        for w in self._stage_widgets:
            w.deleteLater()
        self._stage_widgets.clear()
        if self._stages_container:
            self._stages_container.setVisible(False)

    def _show_stages(self, method: WritingMethod):
        """显示方法阶段。"""
        for stage in method.stages:
            stage_frame = QFrame()
            stage_frame.setObjectName("stage_indicator")
            stage_frame.setFixedHeight(24)
            stage_frame.setStyleSheet(
                f"QFrame#stage_indicator {{ background-color: {stage.color}; border-radius: 4px; }}"
            )

            stage_layout = QHBoxLayout(stage_frame)
            stage_layout.setContentsMargins(8, 2, 8, 2)

            stage_label = QLabel(stage.name)
            stage_label.setStyleSheet("color: white; font-size: 11px;")
            stage_layout.addWidget(stage_label)

            self._stages_layout.addWidget(stage_frame)
            self._stage_widgets.append(stage_frame)

        self._stages_container.setVisible(True)

    def get_current_method(self) -> Optional[str]:
        """获取当前选中的方法名称。"""
        return self._method_combo.currentText() if self._method_combo else "无"

    def set_method(self, method_name: str):
        """设置写作方法（通过方法名称选择）。"""
        if self._method_combo:
            idx = self._method_combo.findText(method_name)
            if idx >= 0:
                self._method_combo.setCurrentIndex(idx)

    def _get_all_chapters(self) -> list[dict]:
        """从大纲树获取所有章节。"""
        chapters = []
        # 如果有章节树控件，尝试从树中获取
        tree = getattr(self, '_tree', None)
        if tree:
            root = tree.invisibleRootItem()
            for i in range(root.childCount()):
                item = root.child(i)
                chapters.append({'title': item.text(0) or f'第{i+1}章'})
        # 如果 tree 不可用，返回默认示例
        if not chapters:
            for i in range(10):
                chapters.append({'title': f'第{i+1}章'})
        return chapters

    def _apply_method_conversion(self, method_name: str, mapping: dict):
        """应用方法转换。"""
        # 设置方法选择器
        self._method_combo.blockSignals(True)
        self._method_combo.setCurrentText(method_name)
        self._method_combo.blockSignals(False)
        # 触发更新阶段显示
        self._current_method = method_advisor.get_method(method_name)
        self._clear_stages()
        if self._current_method:
            self._show_stages(self._current_method)

    def _on_convert_method(self):
        """弹出转换对话框。"""
        from PySide6.QtWidgets import QMessageBox, QComboBox, QVBoxLayout, QLabel, QDialog, QDialogButtonBox
        from core.methods.converter import method_converter

        # 获取当前方法和章节
        current = self._method_combo.currentText()
        chapters = self._get_all_chapters()
        if not chapters or current == "无":
            return

        # 选择目标方法
        dialog = QDialog(self)
        dialog.setWindowTitle("转换写作方法")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"从「{current}」转换为："))
        combo = QComboBox()
        for name in self._method_names:
            if name != current:
                combo.addItem(name)
        layout.addWidget(combo)

        # 预览
        preview = QLabel()
        preview.setWordWrap(True)
        layout.addWidget(preview)

        def on_target_changed(target):
            summary = method_converter.get_conversion_summary(chapters, current, target)
            preview.setText(summary)

        combo.currentTextChanged.connect(on_target_changed)
        if combo.count() > 0:
            on_target_changed(combo.currentText())

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec():
            target = combo.currentText()
            # 应用转换
            mapping = method_converter.convert_chapters(chapters, current, target)
            # 更新大纲面板的阶段分配
            self._apply_method_conversion(target, mapping)
            # 切换方法选择
            self._method_combo.blockSignals(True)
            self._method_combo.setCurrentText(target)
            self._method_combo.blockSignals(False)
