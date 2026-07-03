"""新建项目对话框。"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel,
    QDialogButtonBox, QTextEdit, QSpinBox,
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog
from core.methods.registry import list_method_choices


class NewProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新建项目")
        self.setFixedSize(500, 600)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 字段表单
        form = QFormLayout()
        form.setSpacing(8)

        # 1. 项目名称
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("输入小说名称")
        form.addRow("项目名称：", self._name_edit)

        # 2. 项目路径
        path_layout = QHBoxLayout()
        path_layout.setContentsMargins(0, 0, 0, 0)
        self._path_edit = QLineEdit()
        self._path_edit.setPlaceholderText("选择项目保存路径")
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self._browse_path)
        path_layout.addWidget(self._path_edit)
        path_layout.addWidget(browse_btn)
        form.addRow("项目路径：", path_layout)

        # 3. 小说类型
        self._genre_combo = QComboBox()
        self._genre_combo.addItems(
            ["玄幻", "仙侠", "都市", "科幻", "历史", "悬疑", "言情", "武侠", "游戏", "其他"]
        )
        form.addRow("小说类型：", self._genre_combo)

        # 4. 写作方法：从注册表中动态加载
        self._method_combo = QComboBox()
        for method_id, label in list_method_choices():
            self._method_combo.addItem(label, method_id)
        form.addRow("写作方法：", self._method_combo)

        layout.addLayout(form)

        # 方法简介（根据选择动态更新）
        self._method_desc = QLabel("")
        self._method_desc.setWordWrap(True)
        self._method_desc.setStyleSheet("color: #565f89; padding: 8px;")
        layout.addWidget(self._method_desc)
        self._method_combo.currentIndexChanged.connect(self._update_method_desc)
        self._update_method_desc()

        # 5. 预计字数
        words_form = QFormLayout()
        self._target_words = QSpinBox()
        self._target_words.setRange(10000, 5000000)
        self._target_words.setValue(200000)
        self._target_words.setSingleStep(10000)
        self._target_words.setSuffix(" 字")
        words_form.addRow("预计字数：", self._target_words)
        layout.addLayout(words_form)

        # 6. 项目简介
        desc_label = QLabel("项目简介：")
        self._desc_edit = QTextEdit()
        self._desc_edit.setPlaceholderText("（可选）输入小说简介、核心创意...")
        self._desc_edit.setMaximumHeight(100)
        layout.addWidget(desc_label)
        layout.addWidget(self._desc_edit)

        # 按钮
        buttons = QDialogButtonBox()
        self._ok_btn = buttons.addButton("确定", QDialogButtonBox.AcceptRole)
        self._cancel_btn = buttons.addButton("取消", QDialogButtonBox.RejectRole)
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse_path(self):
        from pathlib import Path
        directory = QFileDialog.getExistingDirectory(self, "选择项目保存路径")
        if directory:
            self._path_edit.setText(directory)

    def _update_method_desc(self):
        """根据选择的写作方法更新简介描述。"""
        from core.methods.registry import get_method
        method_id = self._method_combo.currentData()
        method = get_method(method_id)
        if method:
            desc = (
                f"<b>{method.name}</b> - {method.description}<br>"
                f"<span style='color:#565f89;'>"
                f"适合类型：{'、'.join(method.suitable_genres)} | "
                f"适合长度：{method.suitable_length} | "
                f"难度：{method.difficulty}</span>"
            )
            tips = " | ".join(method.tips[:2])
            desc += f"<br><span style='color:#565f89;font-size:11px;'>提示：{tips}</span>"
            self._method_desc.setText(desc)

    def _validate(self):
        if not self._name_edit.text().strip():
            self._name_edit.setFocus()
            self._name_edit.setStyleSheet("border-color: #f7768e;")
            return
        self.accept()

    def get_project_info(self) -> dict:
        return {
            "name": self._name_edit.text().strip(),
            "path": self._path_edit.text().strip(),
            "genre": self._genre_combo.currentText(),
            "writing_method": self._method_combo.currentData(),
            "target_words": self._target_words.value(),
            "description": self._desc_edit.toPlainText().strip(),
        }
