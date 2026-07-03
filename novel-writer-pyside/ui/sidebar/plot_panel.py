"""情节面板组件 - 管理小说情节弧线和节点。"""
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QBrush, QColor

from services.plot_service import plot_service
from utils.signal_bus import signal_bus
from models import PlotArc, PlotNode


class PlotPanel(QWidget):
    """情节面板 - 侧边栏情节管理标签页。"""

    plot_node_selected = Signal(int)
    plot_node_created = Signal(int)
    plot_node_deleted = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("plot_panel")
        self._project_id = None
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title_widget = QWidget()
        title_widget.setObjectName("plot_header")
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(16, 12, 16, 8)
        title_layout.setSpacing(2)

        self.title_label = QLabel("情节")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        self.title_label.setFont(title_font)
        self.title_label.setObjectName("plot_title")
        title_layout.addWidget(self.title_label)

        layout.addWidget(title_widget)

        filter_widget = QWidget()
        filter_widget.setObjectName("plot_filter")
        filter_layout = QVBoxLayout(filter_widget)
        filter_layout.setContentsMargins(16, 0, 16, 8)
        filter_layout.setSpacing(6)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索情节节点...")
        self.search_input.setObjectName("plot_search")
        filter_layout.addWidget(self.search_input)

        layout.addWidget(filter_widget)

        action_widget = QWidget()
        action_widget.setObjectName("plot_action")
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(16, 0, 16, 8)
        action_layout.setSpacing(8)

        self.add_arc_btn = QPushButton("新建弧线")
        self.add_arc_btn.setObjectName("plot_add_arc_btn")
        action_layout.addWidget(self.add_arc_btn)

        self.add_node_btn = QPushButton("新建节点")
        self.add_node_btn.setObjectName("plot_add_node_btn")
        action_layout.addWidget(self.add_node_btn)

        layout.addWidget(action_widget)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setObjectName("plot_tree")
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        layout.addWidget(self.tree_widget)

        self.empty_label = QLabel("暂无情节\n点击「新建弧线」开始规划")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #999; font-size: 13px;")
        self.empty_label.setContentsMargins(16, 40, 16, 40)
        self.empty_label.hide()
        layout.addWidget(self.empty_label)

    def _connect_signals(self):
        self.search_input.textChanged.connect(self._on_filter_changed)
        self.add_arc_btn.clicked.connect(self._on_add_arc)
        self.add_node_btn.clicked.connect(self._on_add_node)
        self.tree_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.tree_widget.customContextMenuRequested.connect(self._on_context_menu)

        signal_bus.project_opened.connect(self._on_project_opened)
        signal_bus.project_closed.connect(self._on_project_closed)

    def _on_project_opened(self, project_id: int):
        self._project_id = project_id
        self._refresh_tree()

    def _on_project_closed(self):
        self._project_id = None
        self._clear_tree()
        self.empty_label.show()

    def _on_filter_changed(self):
        self._refresh_tree()

    def _on_add_arc(self):
        if not self._project_id:
            return
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "新建弧线", "请输入弧线名称：")
        if not ok or not name.strip():
            return
        plot_service.create_arc(self._project_id, name.strip())
        self._refresh_tree()

    def _on_add_node(self):
        if not self._project_id:
            return
        from ui.dialogs.plot_dialog import PlotDialog
        dialog = PlotDialog(self._project_id, parent=self)
        if dialog.exec():
            node = dialog.get_node()
            if node:
                self.plot_node_created.emit(node.id)
                self._refresh_tree()

    def _on_item_double_clicked(self, item, column):
        data = item.data(0, Qt.UserRole)
        if isinstance(data, tuple) and data[0] == "node":
            node_id = data[1]
            self._edit_node(node_id)

    def _on_context_menu(self, pos):
        item = self.tree_widget.itemAt(pos)
        if not item:
            return

        data = item.data(0, Qt.UserRole)
        if not data:
            return

        menu = QMenu(self)

        if isinstance(data, tuple):
            if data[0] == "arc":
                arc_id = data[1]
                edit_action = menu.addAction("编辑弧线")
                edit_action.triggered.connect(lambda: self._edit_arc(arc_id))

                add_node_action = menu.addAction("在弧线中新建节点")
                add_node_action.triggered.connect(lambda: self._on_add_node_to_arc(arc_id))

                menu.addSeparator()

                delete_action = menu.addAction("删除弧线")
                delete_action.triggered.connect(lambda: self._delete_arc(arc_id))

            elif data[0] == "node":
                node_id = data[1]
                edit_action = menu.addAction("编辑节点")
                edit_action.triggered.connect(lambda: self._edit_node(node_id))

                menu.addSeparator()

                delete_action = menu.addAction("删除节点")
                delete_action.triggered.connect(lambda: self._delete_node(node_id))

        menu.exec(self.tree_widget.viewport().mapToGlobal(pos))

    def _on_add_node_to_arc(self, arc_id: int):
        if not self._project_id:
            return
        from ui.dialogs.plot_dialog import PlotDialog
        dialog = PlotDialog(self._project_id, arc_id=arc_id, parent=self)
        if dialog.exec():
            node = dialog.get_node()
            if node:
                self.plot_node_created.emit(node.id)
                self._refresh_tree()

    def _edit_arc(self, arc_id: int):
        arc = plot_service.get_arc(arc_id)
        if not arc:
            return
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "编辑弧线", "请输入弧线名称：", text=arc.name)
        if not ok or not name.strip():
            return
        plot_service.update_arc(arc_id, name=name.strip())
        self._refresh_tree()

    def _edit_node(self, node_id: int):
        from ui.dialogs.plot_dialog import PlotDialog
        dialog = PlotDialog(self._project_id, node_id=node_id, parent=self)
        if dialog.exec():
            self._refresh_tree()

    def _delete_arc(self, arc_id: int):
        arc = plot_service.get_arc(arc_id)
        if not arc:
            return

        reply = QMessageBox.warning(
            self, "确认删除",
            f"确定要删除弧线「{arc.name}」吗？\n该弧线及其下所有节点将被一并删除，此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        plot_service.delete_arc(arc_id)
        self._refresh_tree()

    def _delete_node(self, node_id: int):
        node = plot_service.get_node(node_id)
        if not node:
            return

        reply = QMessageBox.warning(
            self, "确认删除",
            f"确定要删除节点「{node.title}」吗？\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        plot_service.delete_node(node_id)
        self.plot_node_deleted.emit(node_id)
        self._refresh_tree()

    def _refresh_tree(self):
        if not self._project_id:
            return

        search = self.search_input.text().strip().lower()

        arcs = plot_service.list_arcs(self._project_id)

        self._clear_tree()

        has_items = False

        for arc in arcs:
            arc_item = QTreeWidgetItem([arc.name])
            arc_item.setData(0, Qt.UserRole, ("arc", arc.id))
            arc_item.setExpanded(True)

            nodes = plot_service.list_nodes(self._project_id, arc_id=arc.id)

            for node in nodes:
                if search and search not in node.title.lower():
                    continue

                has_items = True

                node_item = QTreeWidgetItem([node.title])
                node_item.setData(0, Qt.UserRole, ("node", node.id))

                status_color = self._get_status_color(node.status)
                node_item.setForeground(0, QBrush(QColor(status_color)))

                chapter_info = ""
                if node.chapter:
                    chapter_info = f" (第{node.chapter.chapter_number}章)"
                node_item.setText(0, f"{node.title}{chapter_info}")

                arc_item.addChild(node_item)

            self.tree_widget.addTopLevelItem(arc_item)
            has_items = True

        if not has_items:
            self.empty_label.show()
        else:
            self.empty_label.hide()

    def _clear_tree(self):
        self.tree_widget.clear()

    def _get_status_color(self, status: str) -> str:
        color_map = {
            "计划中": "#999999",
            "进行中": "#3498db",
            "已完成": "#27ae60",
            "已放弃": "#e74c3c",
        }
        return color_map.get(status, "#333333")

    def clear(self):
        self._project_id = None
        self._clear_tree()
        self.empty_label.show()
