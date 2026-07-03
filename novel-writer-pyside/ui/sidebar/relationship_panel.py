"""关系与派系面板。"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QHeaderView, QMenu,
    QAbstractItemView, QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from services.relationship_service import relationship_service
from utils.signal_bus import signal_bus
from ui.dialogs.relationship_dialog import RelationshipDialog
from ui.dialogs.faction_dialog import FactionDialog


class RelationshipPanel(QWidget):
    """侧边栏关系与派系列表。"""

    project_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("relationship_panel")
        self._project_id = None
        self._init_ui()
        signal_bus.project_opened.connect(self._on_project_opened)
        signal_bus.project_closed.connect(self._on_project_closed)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # 搜索
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("搜索角色关系...")
        self._search_input.textChanged.connect(self._on_search)
        layout.addWidget(self._search_input)

        # 按钮
        btn_layout = QHBoxLayout()
        self._add_rel_btn = QPushButton("+ 新建关系")
        self._add_rel_btn.clicked.connect(self._on_add_relationship)
        self._add_fac_btn = QPushButton("+ 新建派系")
        self._add_fac_btn.clicked.connect(self._on_add_faction)
        btn_layout.addWidget(self._add_rel_btn)
        btn_layout.addWidget(self._add_fac_btn)
        layout.addLayout(btn_layout)

        # 标签页
        self._tab_widget = QTabWidget()

        # 关系表标签页
        self._rel_table = QTableWidget()
        self._rel_table.setColumnCount(4)
        self._rel_table.setHorizontalHeaderLabels(["角色 A", "角色 B", "类型", "强度"])
        self._rel_table.horizontalHeader().setStretchLastSection(True)
        self._rel_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._rel_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._rel_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self._rel_table.customContextMenuRequested.connect(self._on_rel_context_menu)
        self._rel_table.itemDoubleClicked.connect(self._on_edit_relationship)
        self._tab_widget.addTab(self._rel_table, "关系")

        # 派系列表标签页
        self._fac_table = QTableWidget()
        self._fac_table.setColumnCount(4)
        self._fac_table.setHorizontalHeaderLabels(["派系名", "领导者", "成员数", "状态"])
        self._fac_table.horizontalHeader().setStretchLastSection(True)
        self._fac_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._fac_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._fac_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self._fac_table.customContextMenuRequested.connect(self._on_fac_context_menu)
        self._fac_table.itemDoubleClicked.connect(self._on_edit_faction)
        self._tab_widget.addTab(self._fac_table, "派系")

        layout.addWidget(self._tab_widget)

    def _on_project_opened(self, project_id: int):
        """信号：项目打开。"""
        self._project_id = project_id
        self._load_data()

    def _on_project_closed(self):
        """信号：项目关闭。"""
        self._project_id = None
        self._rel_table.setRowCount(0)
        self._fac_table.setRowCount(0)

    def clear(self):
        """清空面板数据（兼容 main_window 直接调用）。"""
        self._project_id = None
        self._rel_table.setRowCount(0)
        self._fac_table.setRowCount(0)

    def _load_data(self):
        """加载所有数据。"""
        self._load_relationships()
        self._load_factions()

    def _load_relationships(self, search: str = ""):
        """加载关系列表。"""
        self._rel_table.setRowCount(0)
        if not self._project_id:
            return
        rels = relationship_service.list(self._project_id, search=search)
        self._rel_table.setRowCount(len(rels))
        for row, r in enumerate(rels):
            self._rel_table.setItem(row, 0, QTableWidgetItem(r["character_a_name"]))
            self._rel_table.setItem(row, 1, QTableWidgetItem(r["character_b_name"]))
            self._rel_table.setItem(row, 2, QTableWidgetItem(r["relationship_type"]))
            self._rel_table.setItem(row, 3, QTableWidgetItem(str(r["intensity"])))
            self._rel_table.item(row, 0).setData(256, r["id"])

    def _load_factions(self):
        """加载派系列表。"""
        self._fac_table.setRowCount(0)
        if not self._project_id:
            return
        facs = relationship_service.list_factions(self._project_id)
        self._fac_table.setRowCount(len(facs))
        for row, f in enumerate(facs):
            self._fac_table.setItem(row, 0, QTableWidgetItem(f["name"]))
            self._fac_table.setItem(row, 1, QTableWidgetItem(f["leader_name"]))
            self._fac_table.setItem(row, 2, QTableWidgetItem(str(f["member_count"])))
            self._fac_table.setItem(row, 3, QTableWidgetItem(f["status"]))
            self._fac_table.item(row, 0).setData(256, f["id"])

    def _on_search(self, text: str):
        """搜索关系。"""
        self._load_relationships(search=text.strip())

    # ---- 关系操作 ----

    def _on_add_relationship(self):
        """新建关系。"""
        if not self._project_id:
            return
        dialog = RelationshipDialog(self._project_id, parent=self)
        if dialog.exec():
            self._load_relationships(search=self._search_input.text().strip())

    def _on_edit_relationship(self, item):
        """编辑关系。"""
        if not self._project_id or not item:
            return
        rel_id = item.data(256)
        if rel_id:
            dialog = RelationshipDialog(self._project_id, relationship_id=rel_id, parent=self)
            if dialog.exec():
                self._load_relationships(search=self._search_input.text().strip())

    def _on_rel_context_menu(self, pos):
        """关系右键菜单。"""
        item = self._rel_table.itemAt(pos)
        if not item:
            return
        rel_id = item.data(256)
        menu = QMenu(self)
        edit_action = menu.addAction("编辑")
        delete_action = menu.addAction("删除")
        action = menu.exec(self._rel_table.mapToGlobal(pos))

        if action == edit_action:
            dialog = RelationshipDialog(self._project_id, relationship_id=rel_id, parent=self)
            if dialog.exec():
                self._load_relationships(search=self._search_input.text().strip())
        elif action == delete_action:
            reply = QMessageBox.question(
                self, "确认删除", "确定删除这个关系？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                relationship_service.delete(rel_id)
                self._load_relationships(search=self._search_input.text().strip())

    # ---- 派系操作 ----

    def _on_add_faction(self):
        """新建派系。"""
        if not self._project_id:
            return
        dialog = FactionDialog(self._project_id, parent=self)
        if dialog.exec():
            self._load_factions()

    def _on_edit_faction(self, item):
        """编辑派系。"""
        if not self._project_id or not item:
            return
        fac_id = item.data(256)
        if fac_id:
            dialog = FactionDialog(self._project_id, faction_id=fac_id, parent=self)
            if dialog.exec():
                self._load_factions()

    def _on_fac_context_menu(self, pos):
        """派系右键菜单。"""
        item = self._fac_table.itemAt(pos)
        if not item:
            return
        fac_id = item.data(256)
        menu = QMenu(self)
        edit_action = menu.addAction("编辑")
        delete_action = menu.addAction("删除")
        action = menu.exec(self._fac_table.mapToGlobal(pos))

        if action == edit_action:
            dialog = FactionDialog(self._project_id, faction_id=fac_id, parent=self)
            if dialog.exec():
                self._load_factions()
        elif action == delete_action:
            reply = QMessageBox.question(
                self, "确认删除", "确定删除这个派系？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                relationship_service.delete_faction(fac_id)
                self._load_factions()
