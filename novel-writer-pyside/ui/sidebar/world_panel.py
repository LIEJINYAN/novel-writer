"""世界观面板。"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLineEdit, QComboBox, QMenu, QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from services.world_service import world_service
from utils.signal_bus import signal_bus
from ui.dialogs.world_dialog import WorldDialog


SETTING_TYPES = ["全部", "地点", "规则", "物品", "传说", "种族", "文化", "其他"]
IMPORTANCE_COLORS = {
    "核心": QColor("#E74C3C"),
    "重要": QColor("#3498DB"),
    "次要": QColor("#95A5A6"),
}


class WorldPanel(QWidget):
    """侧边栏世界观树形面板。"""

    project_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("world_panel")
        self._project_id = None
        self._init_ui()
        signal_bus.project_opened.connect(self._on_project_opened)
        signal_bus.project_closed.connect(self._on_project_closed)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # 顶部
        top_layout = QHBoxLayout()
        self._type_filter = QComboBox()
        self._type_filter.addItems(SETTING_TYPES)
        self._type_filter.currentTextChanged.connect(self._on_filter)
        top_layout.addWidget(self._type_filter)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("搜索...")
        self._search_input.textChanged.connect(self._on_filter)
        top_layout.addWidget(self._search_input)

        self._add_btn = QPushButton("+ 新建")
        self._add_btn.clicked.connect(self._on_add)
        top_layout.addWidget(self._add_btn)
        layout.addLayout(top_layout)

        # 树
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._on_context_menu)
        self._tree.itemDoubleClicked.connect(self._on_edit)
        layout.addWidget(self._tree)

    def _on_project_opened(self, project_id: int):
        self._project_id = project_id
        self._load_tree()

    def _on_project_closed(self):
        self._project_id = None
        self._tree.clear()

    def clear(self):
        self._project_id = None
        self._tree.clear()

    def _load_tree(self):
        """加载树形数据。"""
        self._tree.clear()
        if not self._project_id:
            return

        tree = world_service.get_tree(self._project_id)
        for root in tree:
            self._add_tree_node(None, root)

    def _add_tree_node(self, parent, node_data):
        """递归添加树节点。"""
        item = QTreeWidgetItem(parent if parent else self._tree)
        item.setText(0, f"[{node_data['setting_type']}] {node_data['name']}")
        item.setData(0, Qt.UserRole, node_data["id"])

        # 重要性着色
        color = IMPORTANCE_COLORS.get(node_data["importance"])
        if color:
            item.setForeground(0, color)

        for child in node_data.get("children", []):
            self._add_tree_node(item, child)

        if parent is None:
            self._tree.addTopLevelItem(item)
        item.setExpanded(True)

    def _on_filter(self):
        """筛选/搜索。"""
        if not self._project_id:
            return
        type_filter = self._type_filter.currentText()
        search = self._search_input.text().strip()

        if type_filter == "全部":
            type_filter = ""

        items = world_service.list(self._project_id,
                                    type_filter=type_filter,
                                    search=search)

        self._tree.clear()
        # 扁平显示搜索结果
        if search:
            for item in items:
                tree_item = QTreeWidgetItem(self._tree)
                tree_item.setText(0, f"[{item.setting_type}] {item.name}")
                tree_item.setData(0, Qt.UserRole, item.id)
                color = IMPORTANCE_COLORS.get(item.importance)
                if color:
                    tree_item.setForeground(0, color)
        else:
            tree = world_service.get_tree(self._project_id)
            for root in tree:
                self._add_tree_node(None, root)

    def _on_add(self):
        """新建条目。"""
        if not self._project_id:
            return
        parent_id = None
        current = self._tree.currentItem()
        if current:
            parent_id = current.data(0, Qt.UserRole)
        dialog = WorldDialog(self._project_id, parent_id=parent_id, parent=self)
        if dialog.exec():
            self._load_tree()

    def _on_edit(self, item):
        """编辑条目。"""
        if not self._project_id or not item:
            return
        setting_id = item.data(0, Qt.UserRole)
        if setting_id:
            dialog = WorldDialog(self._project_id, setting_id=setting_id, parent=self)
            if dialog.exec():
                self._load_tree()

    def _on_context_menu(self, pos):
        """右键菜单。"""
        item = self._tree.itemAt(pos)
        menu = QMenu(self)
        add_action = menu.addAction("新建子条目")
        if item:
            edit_action = menu.addAction("编辑")
            delete_action = menu.addAction("删除")

        action = menu.exec(self._tree.mapToGlobal(pos))

        if not item and action == add_action:
            self._on_add()
        elif item:
            setting_id = item.data(0, Qt.UserRole)
            if action == add_action:
                dialog = WorldDialog(self._project_id, parent_id=setting_id, parent=self)
                if dialog.exec():
                    self._load_tree()
            elif action == edit_action:
                self._on_edit(item)
            elif action == delete_action:
                reply = QMessageBox.question(
                    self, "确认删除", "确定删除这个条目？\n（子条目将取消关联）",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    world_service.delete(setting_id)
                    self._load_tree()
