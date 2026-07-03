"""世界观条目编辑对话框。"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QComboBox, QDialogButtonBox, QMessageBox,
)
from services.world_service import world_service


SETTING_TYPES = ["地点", "规则", "物品", "传说", "种族", "文化", "其他"]
IMPORTANCE_LEVELS = ["核心", "重要", "次要"]


class WorldDialog(QDialog):
    """编辑世界观条目。"""

    def __init__(self, project_id: int, setting_id: int = None, parent_id: int = None, parent=None):
        super().__init__(parent)
        self._project_id = project_id
        self._setting_id = setting_id
        self._preset_parent_id = parent_id
        self._editing = setting_id is not None
        self.setWindowTitle("编辑条目" if self._editing else "新建条目")
        self.setMinimumWidth(500)
        self._init_ui()
        self._load_parents()
        if self._editing:
            self._load_setting()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        form.setSpacing(10)

        # 名称
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("条目名称")
        form.addRow("名称:", self._name_input)

        # 类型
        self._type_combo = QComboBox()
        self._type_combo.addItems(SETTING_TYPES)
        form.addRow("类型:", self._type_combo)

        # 父节点
        self._parent_combo = QComboBox()
        self._parent_combo.addItem("（无）", None)
        form.addRow("父节点:", self._parent_combo)

        # 重要性
        self._importance_combo = QComboBox()
        self._importance_combo.addItems(IMPORTANCE_LEVELS)
        form.addRow("重要性:", self._importance_combo)

        # 标签
        self._tags_input = QLineEdit()
        self._tags_input.setPlaceholderText("逗号分隔，如: 东方,森林,精灵")
        form.addRow("标签:", self._tags_input)

        # 描述
        self._desc_input = QTextEdit()
        self._desc_input.setPlaceholderText("详细描述（支持 Markdown 格式）...")
        form.addRow("描述:", self._desc_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_parents(self):
        """加载父节点下拉。"""
        items = world_service.list(self._project_id)
        for item in items:
            # 编辑模式排除自身和后代
            if self._editing and item.id == self._setting_id:
                continue
            self._parent_combo.addItem(
                f"[{item.setting_type}] {item.name}", item.id
            )

        # 预设父节点
        if self._preset_parent_id:
            idx = self._parent_combo.findData(self._preset_parent_id)
            if idx >= 0:
                self._parent_combo.setCurrentIndex(idx)

    def _load_setting(self):
        """加载已有数据。"""
        ws = world_service.get(self._setting_id)
        if not ws:
            return

        self._name_input.setText(ws.name)

        type_idx = self._type_combo.findText(ws.setting_type)
        if type_idx >= 0:
            self._type_combo.setCurrentIndex(type_idx)

        if ws.parent_id:
            idx = self._parent_combo.findData(ws.parent_id)
            if idx >= 0:
                self._parent_combo.setCurrentIndex(idx)

        imp_idx = self._importance_combo.findText(ws.importance)
        if imp_idx >= 0:
            self._importance_combo.setCurrentIndex(imp_idx)

        self._tags_input.setText(ws.tags or "")
        self._desc_input.setPlainText(ws.description)

    def _on_save(self):
        """保存。"""
        name = self._name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "验证失败", "条目名称不能为空")
            return

        parent_id = self._parent_combo.currentData()

        data = {
            "name": name,
            "setting_type": self._type_combo.currentText(),
            "parent_id": parent_id,
            "importance": self._importance_combo.currentText(),
            "tags": self._tags_input.text().strip(),
            "description": self._desc_input.toPlainText().strip(),
        }

        try:
            if self._editing:
                world_service.update(self._setting_id, **data)
            else:
                world_service.create(self._project_id, name, **data)
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "保存失败", str(e))
