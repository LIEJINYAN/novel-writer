"""一致性检查面板。"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
    QTreeWidgetItem, QLabel, QMessageBox,
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor
from services.consistency_service import consistency_service, CheckResult
from utils.signal_bus import signal_bus
from core.ai.manager import ai_manager


SEVERITY_COLORS = {
    "error": QColor("#E74C3C"),
    "warning": QColor("#F39C12"),
    "info": QColor("#95A5A6"),
}
CATEGORY_NODES = ["角色问题", "时间线问题", "情节问题", "AI 分析"]


class CheckPanel(QWidget):
    """侧边栏一致性检查面板。"""

    navigate_to_chapter = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("check_panel")
        self._project_id = None
        self._ai_worker = None
        self._category_items: dict[str, QTreeWidgetItem] = {}
        self._init_ui()
        signal_bus.project_opened.connect(self._on_project_opened)
        signal_bus.project_closed.connect(self._on_project_closed)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # 按钮
        btn_layout = QHBoxLayout()
        self._rule_btn = QPushButton("规则扫描")
        self._rule_btn.clicked.connect(self._on_rule_scan)
        btn_layout.addWidget(self._rule_btn)

        self._ai_btn = QPushButton("AI 深度检查")
        self._ai_btn.clicked.connect(self._on_ai_check)
        btn_layout.addWidget(self._ai_btn)
        layout.addLayout(btn_layout)

        # 树
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self._tree)

        # 状态
        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(self._status_label)

    def _on_project_opened(self, project_id: int):
        self._project_id = project_id
        self._clear_results()

    def _on_project_closed(self):
        self._project_id = None
        self._clear_results()

    def clear(self):
        self._project_id = None
        self._clear_results()

    def _clear_results(self):
        self._tree.clear()
        self._category_items = {}
        self._status_label.setText("")
        if self._ai_worker and self._ai_worker.isRunning():
            self._ai_worker.cancel()
            self._ai_worker = None

    # ---- 规则扫描 ----

    def _on_rule_scan(self):
        """执行规则扫描。"""
        if not self._project_id:
            return

        self._rule_btn.setEnabled(False)
        self._rule_btn.setText("扫描中...")
        self._status_label.setText("正在扫描...")
        self._clear_results()

        # 用 QTimer 让 UI 先刷新
        QTimer.singleShot(50, lambda: self._do_rule_scan())

    def _do_rule_scan(self):
        """实际执行扫描（异步回调）。"""
        try:
            results = consistency_service.run_rules(self._project_id)
            self._populate_results(results)

            if results:
                errors = sum(1 for r in results if r.severity == "error")
                warnings = sum(1 for r in results if r.severity == "warning")
                self._status_label.setText(
                    f"扫描完成：{errors} 个错误, {warnings} 个警告, "
                    f"{len(results) - errors - warnings} 个提示"
                )
            else:
                self._status_label.setText("扫描完成：未发现问题 ✓")
        except Exception as e:
            self._status_label.setText(f"扫描失败: {e}")
        finally:
            self._rule_btn.setEnabled(True)
            self._rule_btn.setText("规则扫描")

    def _populate_results(self, results: list[CheckResult]):
        """展示结果到树。"""
        self._tree.clear()
        self._category_items = {}

        for cat_name in CATEGORY_NODES:
            item = QTreeWidgetItem(self._tree)
            item.setText(0, cat_name)
            item.setData(0, Qt.UserRole, None)
            self._category_items[cat_name] = item
            self._tree.addTopLevelItem(item)

        for r in results:
            cat_item = self._get_category_item(r.category)
            if not cat_item:
                cat_item = self._category_items.get("情节问题", self._tree.topLevelItem(2))

            child = QTreeWidgetItem(cat_item)
            child.setText(0, r.message)
            child.setToolTip(0, r.detail)
            child.setData(0, Qt.UserRole, r.chapter_id)
            child.setForeground(0, SEVERITY_COLORS.get(r.severity, QColor("gray")))
            cat_item.addChild(child)

        # 更新类别计数
        for i in range(self._tree.topLevelItemCount()):
            cat = self._tree.topLevelItem(i)
            count = cat.childCount()
            current_text = cat.text(0).split(" (")[0]
            if count > 0:
                cat.setText(0, f"{current_text} ({count})")
                cat.setExpanded(True)

        # 折叠 AI 分析节点（初始空）
        ai_item = self._category_items.get("AI 分析")
        if ai_item:
            ai_item.setExpanded(False)

    def _get_category_item(self, category: str) -> QTreeWidgetItem | None:
        """根据类别名获取顶层节点。"""
        mapping = {
            "角色": "角色问题",
            "时间线": "时间线问题",
            "情节": "情节问题",
        }
        cat_name = mapping.get(category)
        if cat_name:
            return self._category_items.get(cat_name)
        return None

    # ---- AI 深度检查 ----

    def _on_ai_check(self):
        """AI 深度检查。"""
        if not self._project_id:
            return

        # 检查 AI 配置
        provider = ai_manager.get_active_provider()
        if provider is None:
            QMessageBox.information(
                self, "AI 未配置",
                "请先在「工具 → AI 设置」中配置 AI 提供商"
            )
            return

        self._ai_btn.setEnabled(False)
        self._ai_btn.setText("检查中...")
        self._status_label.setText("AI 正在分析...")

        # 确保 AI 分析节点存在
        ai_item = self._category_items.get("AI 分析")
        if ai_item is None:
            self._tree.clear()
            self._category_items = {}
            for cat_name in CATEGORY_NODES:
                item = QTreeWidgetItem(self._tree)
                item.setText(0, cat_name)
                item.setData(0, Qt.UserRole, None)
                self._category_items[cat_name] = item
                self._tree.addTopLevelItem(item)
            ai_item = self._category_items["AI 分析"]

        # 添加占位节点
        self._ai_placeholder = QTreeWidgetItem(ai_item)
        self._ai_placeholder.setText(0, "等待 AI 回复...")
        self._ai_placeholder.setForeground(0, QColor("gray"))
        ai_item.addChild(self._ai_placeholder)
        ai_item.setExpanded(True)

        self._ai_buffer = ""
        self._ai_worker = consistency_service.run_ai_check(
            self._project_id,
            on_chunk=self._on_ai_chunk,
            on_done=self._on_ai_done,
            on_error=self._on_ai_error,
        )

    def _on_ai_chunk(self, text: str):
        """AI 流式输出。"""
        self._ai_buffer += text
        if self._ai_placeholder:
            display = self._ai_buffer
            if len(display) > 100:
                display = display[-100:]
            self._ai_placeholder.setText(display)

    def _on_ai_done(self):
        """AI 检查完成。"""
        self._ai_btn.setEnabled(True)
        self._ai_btn.setText("AI 深度检查")
        self._status_label.setText("AI 检查完成")
        if self._ai_placeholder:
            self._ai_placeholder.setText(self._ai_buffer[:200] if self._ai_buffer else "AI 检查完成")
            self._ai_placeholder.setData(0, Qt.UserRole, None)
            self._ai_placeholder = None

        # 更新计数
        ai_item = self._category_items.get("AI 分析")
        if ai_item:
            ai_item.setText(0, f"AI 分析 (1)")
            ai_item.setExpanded(True)

    def _on_ai_error(self, msg: str):
        """AI 检查出错。"""
        self._ai_btn.setEnabled(True)
        self._ai_btn.setText("AI 深度检查")
        self._status_label.setText(f"AI 检查失败: {msg}")
        if self._ai_placeholder:
            self._ai_placeholder.setText(f"错误: {msg}")
            self._ai_placeholder.setForeground(0, QColor("#E74C3C"))
            self._ai_placeholder = None

    # ---- 跳转 ----

    def _on_item_double_clicked(self, item):
        """双击跳转。"""
        chapter_id = item.data(0, Qt.UserRole)
        if chapter_id is not None:
            self.navigate_to_chapter.emit(chapter_id)
