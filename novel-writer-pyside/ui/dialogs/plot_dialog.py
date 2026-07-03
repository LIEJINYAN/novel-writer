"""情节详情对话框 - 编辑情节节点信息和伏笔管理。"""
from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QComboBox, QTextEdit, QPushButton, QScrollArea, QWidget,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QAbstractItemView, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from services.plot_service import plot_service
from services.chapter_service import ChapterService
from models import PlotNode


class PlotDialog(QDialog):
    """情节详情对话框 - 创建或编辑情节节点。"""

    def __init__(self, project_id: int, node_id: Optional[int] = None,
                 arc_id: Optional[int] = None, parent=None):
        super().__init__(parent)
        self._project_id = project_id
        self._node_id = node_id
        self._arc_id = arc_id
        self._node: Optional[PlotNode] = None
        self._chapter_service = ChapterService()
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        self.setWindowTitle("情节节点详情" if self._node_id else "新建情节节点")
        self.setMinimumSize(500, 700)
        self.setMaximumWidth(600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        layout.addWidget(scroll_area)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(12)

        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout(basic_group)
        basic_layout.setSpacing(8)

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("请输入节点标题")
        basic_layout.addRow("标题:", self.title_edit)

        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("描述情节节点的详细内容...")
        self.description_edit.setMaximumHeight(100)
        basic_layout.addRow("描述:", self.description_edit)

        scroll_layout.addWidget(basic_group)

        meta_group = QGroupBox("属性设置")
        meta_layout = QFormLayout(meta_group)
        meta_layout.setSpacing(8)

        self.arc_combo = QComboBox()
        self.arc_combo.addItem("无")
        meta_layout.addRow("所属弧线:", self.arc_combo)

        self.status_combo = QComboBox()
        self.status_combo.addItem("计划中")
        self.status_combo.addItem("进行中")
        self.status_combo.addItem("已完成")
        self.status_combo.addItem("已放弃")
        meta_layout.addRow("状态:", self.status_combo)

        self.chapter_combo = QComboBox()
        self.chapter_combo.addItem("无")
        meta_layout.addRow("关联章节:", self.chapter_combo)

        self.importance_combo = QComboBox()
        self.importance_combo.addItem("核心")
        self.importance_combo.addItem("重要")
        self.importance_combo.addItem("次要")
        meta_layout.addRow("重要性:", self.importance_combo)

        scroll_layout.addWidget(meta_group)

        foreshadow_group = QGroupBox("伏笔管理")
        foreshadow_layout = QVBoxLayout(foreshadow_group)
        foreshadow_layout.setSpacing(8)

        self.foreshadow_table = QTableWidget()
        self.foreshadow_table.setColumnCount(3)
        self.foreshadow_table.setHorizontalHeaderLabels(["描述", "揭示节点", "状态"])
        self.foreshadow_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.foreshadow_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.foreshadow_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.foreshadow_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.foreshadow_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.foreshadow_table.setMaximumHeight(150)
        foreshadow_layout.addWidget(self.foreshadow_table)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.add_foreshadow_btn = QPushButton("添加伏笔")
        self.add_foreshadow_btn.setObjectName("foreshadow_add_btn")
        self.add_foreshadow_btn.clicked.connect(self._on_add_foreshadow)
        btn_layout.addWidget(self.add_foreshadow_btn)

        self.edit_foreshadow_btn = QPushButton("编辑伏笔")
        self.edit_foreshadow_btn.setObjectName("foreshadow_edit_btn")
        self.edit_foreshadow_btn.clicked.connect(self._on_edit_foreshadow)
        btn_layout.addWidget(self.edit_foreshadow_btn)

        self.delete_foreshadow_btn = QPushButton("删除伏笔")
        self.delete_foreshadow_btn.setObjectName("foreshadow_delete_btn")
        self.delete_foreshadow_btn.clicked.connect(self._on_delete_foreshadow)
        btn_layout.addWidget(self.delete_foreshadow_btn)

        btn_layout.addStretch()

        foreshadow_layout.addLayout(btn_layout)

        scroll_layout.addWidget(foreshadow_group)

        notes_group = QGroupBox("备注")
        notes_layout = QVBoxLayout(notes_group)
        notes_layout.setSpacing(4)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("其他备注信息...")
        self.notes_edit.setMaximumHeight(80)
        notes_layout.addWidget(self.notes_edit)

        scroll_layout.addWidget(notes_group)

        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_content)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addStretch()

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton("确定")
        self.ok_btn.setObjectName("plot_dialog_ok")
        self.ok_btn.clicked.connect(self._on_ok)
        button_layout.addWidget(self.ok_btn)

        layout.addLayout(button_layout)

    def _load_data(self):
        self._load_arcs()
        self._load_chapters()

        if not self._node_id:
            if self._arc_id:
                idx = self.arc_combo.findData(self._arc_id)
                if idx >= 0:
                    self.arc_combo.setCurrentIndex(idx)
            return

        self._node = plot_service.get_node(self._node_id)
        if not self._node:
            return

        self.title_edit.setText(self._node.name)
        self.description_edit.setPlainText(self._node.description)

        if self._node.parent_id:
            idx = self.arc_combo.findData(self._node.parent_id)
            if idx >= 0:
                self.arc_combo.setCurrentIndex(idx)

        self.status_combo.setCurrentText(self._node.status)

        if self._node.start_chapter:
            idx = self.chapter_combo.findData(self._node.start_chapter)
            if idx >= 0:
                self.chapter_combo.setCurrentIndex(idx)

        self._load_foreshadows()

    def _load_arcs(self):
        self.arc_combo.blockSignals(True)
        self.arc_combo.clear()
        self.arc_combo.addItem("无", None)

        arcs = plot_service.list_arcs(self._project_id)
        for arc in arcs:
            self.arc_combo.addItem(arc.name, arc.id)
        self.arc_combo.blockSignals(False)

    def _load_chapters(self):
        self.chapter_combo.blockSignals(True)
        self.chapter_combo.clear()
        self.chapter_combo.addItem("无", None)

        chapters = self._chapter_service.list_chapters(self._project_id)
        for ch in chapters:
            self.chapter_combo.addItem(f"第{ch.chapter_number}章 {ch.title}", ch.id)
        self.chapter_combo.blockSignals(False)

    def _load_foreshadows(self):
        if not self._node_id:
            return

        foreshadows = plot_service.list_foreshadows(self._node_id)
        self.foreshadow_table.setRowCount(len(foreshadows))

        for row, fs in enumerate(foreshadows):
            desc_item = QTableWidgetItem(fs.content)
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEditable)
            self.foreshadow_table.setItem(row, 0, desc_item)

            target_title = ""
            if fs.reveal_chapter_id:
                target_title = f"第{fs.reveal_chapter_id}章"
            target_item = QTableWidgetItem(target_title)
            target_item.setFlags(target_item.flags() & ~Qt.ItemIsEditable)
            self.foreshadow_table.setItem(row, 1, target_item)

            status_item = QTableWidgetItem(fs.status)
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
            self.foreshadow_table.setItem(row, 2, status_item)

            self.foreshadow_table.item(row, 0).setData(Qt.UserRole, fs.id)

    def _on_add_foreshadow(self):
        self._edit_foreshadow_dialog()

    def _on_edit_foreshadow(self):
        row = self.foreshadow_table.currentRow()
        if row < 0:
            return
        item = self.foreshadow_table.item(row, 0)
        if item:
            fs_id = item.data(Qt.UserRole)
            if fs_id:
                self._edit_foreshadow_dialog(fs_id)

    def _on_delete_foreshadow(self):
        row = self.foreshadow_table.currentRow()
        if row < 0:
            return

        item = self.foreshadow_table.item(row, 0)
        if not item:
            return
        fs_id = item.data(Qt.UserRole)
        if not fs_id:
            return

        reply = QMessageBox.warning(
            self, "确认删除",
            "确定要删除这条伏笔吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        plot_service.delete_foreshadow(fs_id)
        self._load_foreshadows()

    def _edit_foreshadow_dialog(self, fs_id: Optional[int] = None):
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QDialogButtonBox

        dialog = QDialog(self)
        dialog.setWindowTitle("编辑伏笔" if fs_id else "添加伏笔")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        desc_edit = QTextEdit()
        desc_edit.setPlaceholderText("描述这条伏笔的内容...")
        desc_edit.setMaximumHeight(80)
        form_layout.addRow("描述:", desc_edit)

        target_combo = QComboBox()
        target_combo.addItem("无", None)

        all_nodes = plot_service.list_nodes(self._project_id)
        for node in all_nodes:
            if node.id != self._node_id:
                target_combo.addItem(node.name, node.id)
        form_layout.addRow("揭示节点:", target_combo)

        status_combo = QComboBox()
        status_combo.addItem("已埋设")
        status_combo.addItem("已揭示")
        status_combo.addItem("已废弃")
        form_layout.addRow("状态:", status_combo)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if fs_id:
            fs = plot_service.get_foreshadow(fs_id)
            if fs:
                desc_edit.setPlainText(fs.content)
                if fs.reveal_chapter_id:
                    idx = target_combo.findData(fs.reveal_chapter_id)
                    if idx >= 0:
                        target_combo.setCurrentIndex(idx)
                status_combo.setCurrentText(fs.status)

        if dialog.exec():
            desc = desc_edit.toPlainText().strip()
            if not desc:
                QMessageBox.warning(self, "提示", "请输入伏笔描述")
                return

            target_id = target_combo.currentData()

            if fs_id:
                plot_service.update_foreshadow(fs_id, description=desc,
                                               target_node_id=target_id,
                                               status=status_combo.currentText())
            else:
                if not self._node_id:
                    temp_node = plot_service.create_node(self._project_id, "临时节点")
                    self._node_id = temp_node.id
                    self._node = temp_node

                plot_service.create_foreshadow(self._project_id, self._node_id,
                                               description=desc,
                                               target_node_id=target_id)

            self._load_foreshadows()

    def _on_ok(self):
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "提示", "请输入节点标题")
            return

        arc_id = self.arc_combo.currentData()
        chapter_id = self.chapter_combo.currentData()

        data = {
            "name": title,
            "description": self.description_edit.toPlainText().strip(),
            "parent_id": arc_id,
            "status": self.status_combo.currentText(),
            "start_chapter": chapter_id,
        }

        if self._node_id:
            self._node = plot_service.update_node(self._node_id, **data)
        else:
            self._node = plot_service.create_node(self._project_id, **data)

        if self._node:
            self.accept()

    def get_node(self) -> Optional[PlotNode]:
        return self._node
