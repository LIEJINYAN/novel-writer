"""关系编辑对话框。"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox, QTextEdit,
    QSlider, QLabel, QPushButton, QDialogButtonBox, QListWidget, QListWidgetItem,
    QMessageBox,
)
from PySide6.QtCore import Qt
from services.relationship_service import relationship_service
from services.character_service import character_service


class RelationshipDialog(QDialog):
    """编辑角色关系。"""

    def __init__(self, project_id: int, relationship_id: int = None, parent=None):
        super().__init__(parent)
        self._project_id = project_id
        self._relationship_id = relationship_id
        self._editing = relationship_id is not None
        self.setWindowTitle("编辑关系" if self._editing else "新建关系")
        self.setMinimumWidth(500)
        self._init_ui()
        self._load_characters()
        if self._editing:
            self._load_relationship()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        form.setSpacing(10)

        # 角色 A
        self._char_a_combo = QComboBox()
        form.addRow("角色 A:", self._char_a_combo)

        # 角色 B
        self._char_b_combo = QComboBox()
        form.addRow("角色 B:", self._char_b_combo)

        # 互换按钮
        swap_btn = QPushButton("⇄ 互换")
        swap_btn.clicked.connect(self._swap_characters)
        form.addRow("", swap_btn)

        # 关系类型
        self._type_combo = QComboBox()
        self._type_combo.addItems(["盟友", "敌对", "恋人", "家人", "师徒", "中立", "其他"])
        form.addRow("关系类型:", self._type_combo)

        # 关系状态标签
        self._relation_input = QTextEdit()
        self._relation_input.setMaximumHeight(60)
        self._relation_input.setPlaceholderText("如: 生死之交、貌合神离")
        form.addRow("关系状态:", self._relation_input)

        # 强度
        intensity_layout = QHBoxLayout()
        self._intensity_slider = QSlider(Qt.Horizontal)
        self._intensity_slider.setRange(1, 10)
        self._intensity_slider.setValue(5)
        self._intensity_label = QLabel("5")
        self._intensity_slider.valueChanged.connect(
            lambda v: self._intensity_label.setText(str(v))
        )
        intensity_layout.addWidget(self._intensity_slider)
        intensity_layout.addWidget(self._intensity_label)
        form.addRow("强度:", intensity_layout)

        # 描述
        self._desc_input = QTextEdit()
        self._desc_input.setPlaceholderText("关系描述...")
        form.addRow("描述:", self._desc_input)

        layout.addLayout(form)

        # 变化历史
        if self._editing:
            history_label = QLabel("变化历史")
            history_label.setStyleSheet("font-weight: bold; margin-top: 8px;")
            layout.addWidget(history_label)
            self._history_list = QListWidget()
            self._history_list.setMaximumHeight(120)
            layout.addWidget(self._history_list)

        # 按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_characters(self):
        """加载项目角色到下拉框。"""
        chars = character_service.list(self._project_id)
        for c in chars:
            self._char_a_combo.addItem(c.name, c.id)
            self._char_b_combo.addItem(c.name, c.id)

    def _swap_characters(self):
        """互换角色 A 和 B。"""
        a_idx = self._char_a_combo.currentIndex()
        b_idx = self._char_b_combo.currentIndex()
        self._char_a_combo.setCurrentIndex(b_idx)
        self._char_b_combo.setCurrentIndex(a_idx)

    def _load_relationship(self):
        """加载已有关系数据。"""
        rel = relationship_service.get(self._relationship_id)
        if not rel:
            return

        idx_a = self._char_a_combo.findData(rel.character_a_id)
        idx_b = self._char_b_combo.findData(rel.character_b_id)
        if idx_a >= 0:
            self._char_a_combo.setCurrentIndex(idx_a)
        if idx_b >= 0:
            self._char_b_combo.setCurrentIndex(idx_b)

        type_idx = self._type_combo.findText(rel.relationship_type)
        if type_idx >= 0:
            self._type_combo.setCurrentIndex(type_idx)

        self._relation_input.setPlainText(rel.current_relation)
        self._intensity_slider.setValue(rel.intensity)
        self._desc_input.setPlainText(rel.description)

        # 加载变化历史
        for ch in rel.changes:
            chapter_info = f"第{ch.chapter.chapter_number}章: " if ch.chapter else ""
            text = f"[{ch.change_type}] {chapter_info}{ch.old_relation} → {ch.new_relation}"
            item = QListWidgetItem(text)
            self._history_list.addItem(item)

    def _on_save(self):
        """保存关系。"""
        a_id = self._char_a_combo.currentData()
        b_id = self._char_b_combo.currentData()

        if a_id == b_id:
            QMessageBox.warning(self, "验证失败", "角色 A 和角色 B 不能相同")
            return

        if not a_id or not b_id:
            QMessageBox.warning(self, "验证失败", "请选择两个角色")
            return

        data = {
            "relationship_type": self._type_combo.currentText(),
            "current_relation": self._relation_input.toPlainText().strip(),
            "intensity": self._intensity_slider.value(),
            "description": self._desc_input.toPlainText().strip(),
        }

        try:
            if self._editing:
                relationship_service.update(self._relationship_id, **data)
            else:
                relationship_service.create(self._project_id, a_id, b_id, **data)
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "保存失败", str(e))
