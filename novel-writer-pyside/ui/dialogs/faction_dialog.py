"""派系编辑对话框。"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QTextEdit, QComboBox, QPushButton, QDialogButtonBox, QListWidget,
    QListWidgetItem, QMessageBox,
)
from services.relationship_service import relationship_service
from services.character_service import character_service


class FactionDialog(QDialog):
    """编辑派系。"""

    def __init__(self, project_id: int, faction_id: int = None, parent=None):
        super().__init__(parent)
        self._project_id = project_id
        self._faction_id = faction_id
        self._editing = faction_id is not None
        self.setWindowTitle("编辑派系" if self._editing else "新建派系")
        self.setMinimumWidth(500)
        self._init_ui()
        self._load_characters()
        if self._editing:
            self._load_faction()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        form.setSpacing(10)

        # 名称
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("派系名称")
        form.addRow("名称:", self._name_input)

        # 描述
        self._desc_input = QTextEdit()
        self._desc_input.setPlaceholderText("派系描述...")
        form.addRow("描述:", self._desc_input)

        # 领导者
        self._leader_combo = QComboBox()
        self._leader_combo.addItem("（无）", None)
        form.addRow("领导者:", self._leader_combo)

        # 目标
        self._goals_input = QTextEdit()
        self._goals_input.setPlaceholderText("每行一个目标")
        form.addRow("目标:", self._goals_input)

        # 状态
        self._status_combo = QComboBox()
        self._status_combo.addItems(["活跃", "休眠", "解散"])
        form.addRow("状态:", self._status_combo)

        layout.addLayout(form)

        # 成员列表
        member_label = QPushButton("成员列表")
        member_label.setStyleSheet("font-weight: bold; margin-top: 8px;")
        member_label.setFlat(True)
        member_label.setEnabled(False)
        layout.addWidget(member_label)

        member_layout = QHBoxLayout()
        self._member_list = QListWidget()
        member_layout.addWidget(self._member_list)

        member_btn_layout = QVBoxLayout()
        self._add_member_btn = QPushButton("+ 添加成员")
        self._add_member_btn.clicked.connect(self._add_member)
        self._remove_member_btn = QPushButton("- 移除成员")
        self._remove_member_btn.clicked.connect(self._remove_member)
        member_btn_layout.addWidget(self._add_member_btn)
        member_btn_layout.addWidget(self._remove_member_btn)
        member_btn_layout.addStretch()
        member_layout.addLayout(member_btn_layout)
        layout.addLayout(member_layout)

        # 按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_characters(self):
        """加载角色到领导者和成员选择。"""
        chars = character_service.list(self._project_id)
        for c in chars:
            self._leader_combo.addItem(c.name, c.id)

    def _load_faction(self):
        """加载已有派系数据。"""
        fac = relationship_service.get_faction(self._faction_id)
        if not fac:
            return

        self._name_input.setText(fac.name)
        self._desc_input.setPlainText(fac.description)

        if fac.leader_id:
            idx = self._leader_combo.findData(fac.leader_id)
            if idx >= 0:
                self._leader_combo.setCurrentIndex(idx)

        self._goals_input.setPlainText(fac.goals or "")
        status_idx = self._status_combo.findText(fac.status)
        if status_idx >= 0:
            self._status_combo.setCurrentIndex(status_idx)

        # 加载成员
        members = relationship_service.list_faction_members(fac.id)
        for m in members:
            char = character_service.get(m.character_id)
            text = char.name if char else f"[ID:{m.character_id}]"
            item = QListWidgetItem(text)
            item.setData(256, m.character_id)
            self._member_list.addItem(item)

    def _add_member(self):
        """弹出角色选择对话框添加成员。"""
        from PySide6.QtWidgets import QInputDialog

        chars = character_service.list(self._project_id)
        names = [c.name for c in chars]
        if not names:
            QMessageBox.information(self, "提示", "项目中还没有角色")
            return

        name, ok = QInputDialog.getItem(self, "添加成员", "选择角色:", names, False)
        if ok and name:
            char = next((c for c in chars if c.name == name), None)
            if char:
                # 检查是否已在列表中
                for i in range(self._member_list.count()):
                    if self._member_list.item(i).data(256) == char.id:
                        return
                item = QListWidgetItem(char.name)
                item.setData(256, char.id)
                self._member_list.addItem(item)

    def _remove_member(self):
        """移除选中的成员。"""
        item = self._member_list.currentItem()
        if item:
            row = self._member_list.row(item)
            self._member_list.takeItem(row)

    def _on_save(self):
        """保存派系。"""
        name = self._name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "验证失败", "派系名称不能为空")
            return

        leader_id = self._leader_combo.currentData()

        data = {
            "name": name,
            "description": self._desc_input.toPlainText().strip(),
            "leader_id": leader_id,
            "goals": self._goals_input.toPlainText().strip(),
            "status": self._status_combo.currentText(),
        }

        try:
            if self._editing:
                relationship_service.update_faction(self._faction_id, **data)
            else:
                fac = relationship_service.create_faction(self._project_id, name, **data)
                self._faction_id = fac.id

            # 同步成员：先清空再全部添加
            if self._faction_id:
                for i in range(self._member_list.count()):
                    cid = self._member_list.item(i).data(256)
                    relationship_service.add_member(self._faction_id, cid)

            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "保存失败", str(e))
