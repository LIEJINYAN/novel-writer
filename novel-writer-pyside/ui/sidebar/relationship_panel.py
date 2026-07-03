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

# 延迟导入：RelationScene 使用的 Qt 图形类
from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtCore import QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QFont


class RelationScene(QGraphicsScene):
    """关系图谱场景。"""
    def __init__(self, relations: list, parent=None):
        super().__init__(parent)
        self._nodes = {}  # character_name -> (cx, cy, ellipse_item)
        self._lines = []  # QGraphicsLineItem list
        self._load_data(relations)

    def _load_data(self, relations):
        self.clear()
        self._nodes.clear()
        # 收集所有角色
        chars = set()
        for rel in relations:
            chars.add(rel.get('character_a_name', ''))
            chars.add(rel.get('character_b_name', ''))

        # 布局节点（环形）
        from math import cos, sin, pi
        center = QPointF(300, 300)
        radius = 200
        angle_step = 2 * pi / max(len(chars), 1)
        for i, c in enumerate(chars):
            angle = i * angle_step - pi / 2
            x = center.x() + radius * cos(angle) - 30
            y = center.y() + radius * sin(angle) - 15
            item = self.addEllipse(x, y, 60, 30, QPen(QColor("#7c7cff"), 2), QBrush(QColor("#3a3a6a")))
            text = self.addSimpleText(c, QFont("Microsoft YaHei", 10))
            text.setPos(x + 30 - text.boundingRect().width() / 2, y + 7)
            self._nodes[c] = (x + 30, y + 15, item)

        # 绘制连线
        for rel in relations:
            a = rel.get('character_a_name', '')
            b = rel.get('character_b_name', '')
            rel_type = rel.get('relationship_type', '')
            if a in self._nodes and b in self._nodes and a != b:
                x1, y1, _ = self._nodes[a]
                x2, y2, _ = self._nodes[b]
                line = self.addLine(x1, y1, x2, y2, QPen(QColor("#8b5cf6"), 2))
                self._lines.append(line)
                # 关系类型标签（中点）
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                label = self.addSimpleText(rel_type, QFont("Microsoft YaHei", 8))
                label.setPos(mx - label.boundingRect().width() / 2, my - 10)


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

        # 关系图谱标签页
        from PySide6.QtWidgets import QGraphicsView
        from PySide6.QtGui import QPainter
        self._graphics_view = QGraphicsView()
        self._graphics_view.setRenderHint(QPainter.Antialiasing)
        self._graphics_view.setDragMode(QGraphicsView.ScrollHandDrag)
        self._graphics_view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self._scene = RelationScene([])
        self._graphics_view.setScene(self._scene)
        self._tab_widget.addTab(self._graphics_view, "关系")

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
        self._scene = RelationScene([])
        self._graphics_view.setScene(self._scene)
        self._fac_table.setRowCount(0)

    def clear(self):
        """清空面板数据（兼容 main_window 直接调用）。"""
        self._project_id = None
        self._scene = RelationScene([])
        self._graphics_view.setScene(self._scene)
        self._fac_table.setRowCount(0)

    def _load_data(self):
        """加载所有数据。"""
        self._load_relationships()
        self._load_factions()

    def _load_relationships(self, search: str = ""):
        """加载关系图谱。"""
        if not self._project_id:
            self._scene = RelationScene([])
            self._graphics_view.setScene(self._scene)
            return
        rels = relationship_service.list(self._project_id, search=search)
        self._scene = RelationScene(rels)
        self._graphics_view.setScene(self._scene)

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
