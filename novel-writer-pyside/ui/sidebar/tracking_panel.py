"""综合追踪面板 - 世界观等追踪信息的标签页容器。"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QTreeWidget, QTreeWidgetItem, QPushButton, QLineEdit,
    QMessageBox, QHeaderView, QAbstractItemView,
)
from PySide6.QtCore import Qt, Signal
from utils.signal_bus import signal_bus
from core.tracking.world import world_tracker


class TrackingPanel(QWidget):
    """综合追踪面板 - 包含世界观等追踪标签页。"""

    project_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tracking_panel")
        self._project_id = None
        self._init_ui()
        signal_bus.project_opened.connect(self._on_project_opened)
        signal_bus.project_closed.connect(self._on_project_closed)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self._tab_widget = QTabWidget()

        # ---- 世界观标签页 ----
        self._init_world_tab()
        self._tab_widget.addTab(self._world_tab, "世界观")

        layout.addWidget(self._tab_widget)

    def _init_world_tab(self):
        """初始化世界观标签页。"""
        self._world_tab = QWidget()
        world_layout = QVBoxLayout(self._world_tab)

        # 工具栏
        world_toolbar = QHBoxLayout()
        self._world_add_btn = QPushButton("新增")
        self._world_edit_btn = QPushButton("编辑")
        self._world_del_btn = QPushButton("删除")
        self._world_add_btn.clicked.connect(self._on_world_add)
        self._world_edit_btn.clicked.connect(self._on_world_edit)
        self._world_del_btn.clicked.connect(self._on_world_delete)
        world_toolbar.addWidget(self._world_add_btn)
        world_toolbar.addWidget(self._world_edit_btn)
        world_toolbar.addWidget(self._world_del_btn)
        world_toolbar.addStretch()
        self._world_search = QLineEdit()
        self._world_search.setPlaceholderText("搜索设定...")
        self._world_search.textChanged.connect(self._on_world_search)
        world_toolbar.addWidget(self._world_search)
        world_layout.addLayout(world_toolbar)

        # 树形视图：分类 | 条目
        self._world_tree = QTreeWidget()
        self._world_tree.setHeaderLabels(["名称", "类型", "描述"])
        self._world_tree.setAlternatingRowColors(True)
        self._world_tree.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._world_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._world_tree.setRootIsDecorated(True)
        self._world_tree.itemDoubleClicked.connect(self._on_world_edit)
        # 列宽
        self._world_tree.header().setStretchLastSection(True)
        self._world_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._world_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        world_layout.addWidget(self._world_tree, 1)

    # ========== 信号处理 ==========

    def _on_project_opened(self, project_id: int):
        """项目打开时加载数据。"""
        self._project_id = project_id
        self._load_world_tree()

    def _on_project_closed(self):
        """项目关闭时清空数据。"""
        self._project_id = None
        self._world_tree.clear()

    def clear(self):
        """清空面板数据。"""
        self._project_id = None
        self._world_tree.clear()

    # ========== 世界观数据加载 ==========

    def _load_world_tree(self, keyword: str = ""):
        """加载世界观树形数据。"""
        self._world_tree.clear()
        if not self._project_id:
            return

        if keyword:
            tree_data = world_tracker.search(self._project_id, keyword)
        else:
            tree_data = world_tracker.get_tree(self._project_id)

        for cat_group in tree_data:
            self._add_category_node(cat_group)

    def _add_category_node(self, cat_group: dict):
        """添加一个分类节点及其子条目。"""
        category = cat_group["category"]
        items = cat_group.get("items", [])

        if not items:
            return

        # 创建分类节点
        cat_item = QTreeWidgetItem(self._world_tree)
        cat_item.setText(0, category)
        cat_item.setText(1, "")
        cat_item.setText(2, "")
        cat_item.setFlags(cat_item.flags() & ~Qt.ItemIsSelectable)
        # 分类节点用加粗
        font = cat_item.font(0)
        font.setBold(True)
        cat_item.setFont(0, font)

        for entry in items:
            self._add_entry_node(cat_item, entry)

        cat_item.setExpanded(True)
        self._world_tree.addTopLevelItem(cat_item)

    def _add_entry_node(self, parent: QTreeWidgetItem, entry: dict):
        """递归添加条目及其子节点。"""
        item = QTreeWidgetItem(parent)
        item.setText(0, entry.get("name", ""))
        item.setText(1, entry.get("type", ""))
        item.setText(2, entry.get("description", ""))
        item.setData(0, Qt.UserRole, entry.get("id"))
        item.setToolTip(2, entry.get("description", ""))

        # 子条目
        for child in entry.get("children", []):
            self._add_entry_node(item, child)

    # ========== 世界观操作 ==========

    def _on_world_search(self, text: str):
        """搜索世界观条目。"""
        self._load_world_tree(keyword=text.strip())

    def _on_world_add(self):
        """新增条目占位。"""
        if not self._project_id:
            return
        QMessageBox.information(self, "新增设定", "新增设定功能将在后续版本实现。\n请使用侧边栏「世界观」面板进行完整操作。")

    def _on_world_edit(self):
        """编辑条目占位。"""
        if not self._project_id:
            return
        current = self._world_tree.currentItem()
        if not current:
            QMessageBox.information(self, "提示", "请先选择一个条目")
            return
        QMessageBox.information(self, "编辑设定", "编辑设定功能将在后续版本实现。\n请使用侧边栏「世界观」面板进行完整操作。")

    def _on_world_delete(self):
        """删除条目。"""
        if not self._project_id:
            return
        current = self._world_tree.currentItem()
        if not current:
            QMessageBox.information(self, "提示", "请先选择一个条目")
            return

        setting_id = current.data(0, Qt.UserRole)
        if not setting_id:
            QMessageBox.information(self, "提示", "不能删除分类节点")
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定删除「{current.text(0)}」？\n（子条目将取消关联）",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            world_tracker.delete_item(setting_id)
            self._load_world_tree(keyword=self._world_search.text().strip())
