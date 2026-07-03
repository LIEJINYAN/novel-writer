"""导入预览对话框 - 展示全书拆分为章节的预览，让用户确认或调整后再导入。"""
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QPlainTextEdit, QComboBox, QLineEdit, QPushButton,
    QSplitter, QWidget,
)
from PySide6.QtCore import Qt

from models import db_manager, Volume


class ImportPreviewDialog(QDialog):
    """导入预览对话框 - 展示全书拆分结果并允许用户确认导入。"""

    def __init__(self, sections: list[dict], project_id: int, parent=None):
        super().__init__(parent)
        self._sections = sections
        self._project_id = project_id
        self._selected_volume_id: Optional[int] = None
        self._init_ui()
        self._load_volumes()

    def _init_ui(self):
        self.setWindowTitle("导入预览")
        self.setMinimumSize(700, 500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 标题
        title_label = QLabel(f"导入预览 - 共 {len(self._sections)} 个章节")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)

        # 左右分割面板
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        # 左侧：章节列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(4)

        left_label = QLabel("章节列表")
        left_label.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(left_label)

        self._list_widget = QListWidget()
        self._list_widget.currentRowChanged.connect(self._on_selection_changed)
        left_layout.addWidget(self._list_widget)

        splitter.addWidget(left_widget)

        # 右侧：内容预览
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)

        right_label = QLabel("内容预览")
        right_label.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(right_label)

        self._preview_edit = QPlainTextEdit()
        self._preview_edit.setReadOnly(True)
        right_layout.addWidget(self._preview_edit)

        splitter.addWidget(right_widget)

        # 设置初始比例 (左:右 = 1:2)
        splitter.setSizes([230, 470])
        layout.addWidget(splitter)

        # 填充章节列表
        self._populate_list()

        # 目标分卷选择
        volume_layout = QHBoxLayout()
        volume_layout.setSpacing(8)

        volume_label = QLabel("导入到分卷：")
        volume_layout.addWidget(volume_label)

        self._volume_combo = QComboBox()
        self._volume_combo.setMinimumWidth(200)
        self._volume_combo.currentIndexChanged.connect(self._on_volume_changed)
        volume_layout.addWidget(self._volume_combo)

        self._new_volume_edit = QLineEdit()
        self._new_volume_edit.setPlaceholderText("新分卷名称")
        self._new_volume_edit.setText("导入章节")
        self._new_volume_edit.hide()
        volume_layout.addWidget(self._new_volume_edit)

        volume_layout.addStretch()
        layout.addLayout(volume_layout)

        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addStretch()

        self._cancel_btn = QPushButton("取消")
        self._cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self._cancel_btn)

        self._ok_btn = QPushButton("确认导入")
        self._ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self._ok_btn)

        layout.addLayout(button_layout)

    def _populate_list(self):
        """填充章节列表。"""
        for section in self._sections:
            title = section.get("title", "未命名")
            word_count = section.get("word_count", 0)
            self._list_widget.addItem(f"{title} ({word_count} 字)")

        # 默认选中第一个
        if self._sections:
            self._list_widget.setCurrentRow(0)

    def _on_selection_changed(self, row: int):
        """当左侧列表选中项改变时，更新右侧内容预览。"""
        if 0 <= row < len(self._sections):
            section = self._sections[row]
            content = section.get("content", "")
            self._preview_edit.setPlainText(content)

    def _load_volumes(self):
        """从数据库加载已有分卷列表。"""
        self._volume_combo.blockSignals(True)
        self._volume_combo.clear()

        session = db_manager.get_session()
        try:
            volumes = (
                session.query(Volume)
                .filter_by(project_id=self._project_id)
                .order_by(Volume.sort_order.asc())
                .all()
            )
            for vol in volumes:
                self._volume_combo.addItem(vol.name, vol.id)
        finally:
            session.close()

        # 添加"新建分卷"选项
        self._volume_combo.addItem("新建分卷", None)
        self._volume_combo.blockSignals(False)

    def _on_volume_changed(self, index: int):
        """当分卷选择改变时，控制新分卷名称输入框的显隐。"""
        is_new = self._volume_combo.itemData(index) is None
        self._new_volume_edit.setVisible(is_new)

    def get_target_volume_id(self) -> Optional[int]:
        """返回选择的分卷 ID，新建分卷时返回 None。"""
        return self._volume_combo.currentData()

    def get_new_volume_name(self) -> str:
        """返回新分卷名称（新建分卷时有效）。"""
        return self._new_volume_edit.text().strip() or "导入章节"

    def get_sections(self) -> list[dict]:
        """返回章节列表（可被调用方修改后用于导入）。"""
        return self._sections
