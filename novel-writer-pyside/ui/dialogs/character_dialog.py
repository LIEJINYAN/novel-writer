"""角色详情对话框 - 编辑角色完整信息。"""
from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QComboBox, QTextEdit, QPushButton, QScrollArea, QWidget,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from services.character_service import character_service
from models.character import Character


class CharacterDialog(QDialog):
    """角色详情对话框 - 创建或编辑角色。"""

    def __init__(self, project_id: int, character_id: Optional[int] = None, parent=None):
        super().__init__(parent)
        self._project_id = project_id
        self._character_id = character_id
        self._character: Optional[Character] = None
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        self.setWindowTitle("角色详情" if self._character_id else "新建角色")
        self.setMinimumSize(500, 650)
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

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请输入角色姓名")
        basic_layout.addRow("姓名:", self.name_edit)

        self.aliases_edit = QLineEdit()
        self.aliases_edit.setPlaceholderText("别名，用逗号分隔")
        basic_layout.addRow("别名:", self.aliases_edit)

        row_layout = QHBoxLayout()
        row_layout.setSpacing(8)

        gender_layout = QHBoxLayout()
        self.gender_combo = QComboBox()
        self.gender_combo.addItem("")
        self.gender_combo.addItem("男")
        self.gender_combo.addItem("女")
        self.gender_combo.addItem("未知")
        gender_layout.addWidget(self.gender_combo)
        basic_layout.addRow("性别:", self.gender_combo)

        self.age_edit = QLineEdit()
        self.age_edit.setPlaceholderText("年龄或年龄段")
        basic_layout.addRow("年龄:", self.age_edit)

        scroll_layout.addWidget(basic_group)

        role_group = QGroupBox("角色设定")
        role_layout = QFormLayout(role_group)
        role_layout.setSpacing(8)

        self.role_type_combo = QComboBox()
        self.role_type_combo.addItem("")
        self.role_type_combo.addItem("主角")
        self.role_type_combo.addItem("配角")
        self.role_type_combo.addItem("反派")
        self.role_type_combo.addItem("路人")
        role_layout.addRow("角色类型:", self.role_type_combo)

        self.status_combo = QComboBox()
        self.status_combo.addItem("活跃")
        self.status_combo.addItem("已故")
        self.status_combo.addItem("失踪")
        self.status_combo.addItem("未知")
        role_layout.addRow("状态:", self.status_combo)

        scroll_layout.addWidget(role_group)

        personality_group = QGroupBox("性格标签")
        personality_layout = QVBoxLayout(personality_group)
        personality_layout.setSpacing(4)

        personality_label = QLabel("每行一个标签")
        personality_label.setStyleSheet("font-size: 11px; color: #666;")
        personality_layout.addWidget(personality_label)

        self.personality_edit = QTextEdit()
        self.personality_edit.setPlaceholderText("勇敢\n聪明\n固执")
        self.personality_edit.setMaximumHeight(80)
        personality_layout.addWidget(self.personality_edit)

        scroll_layout.addWidget(personality_group)

        appearance_group = QGroupBox("外貌描述")
        appearance_layout = QVBoxLayout(appearance_group)
        appearance_layout.setSpacing(4)

        self.appearance_edit = QTextEdit()
        self.appearance_edit.setPlaceholderText("描述角色的外貌特征...")
        self.appearance_edit.setMaximumHeight(100)
        appearance_layout.addWidget(self.appearance_edit)

        scroll_layout.addWidget(appearance_group)

        background_group = QGroupBox("背景故事")
        background_layout = QVBoxLayout(background_group)
        background_layout.setSpacing(4)

        self.background_edit = QTextEdit()
        self.background_edit.setPlaceholderText("描述角色的背景故事...")
        self.background_edit.setMaximumHeight(120)
        background_layout.addWidget(self.background_edit)

        scroll_layout.addWidget(background_group)

        arc_group = QGroupBox("角色弧线")
        arc_layout = QVBoxLayout(arc_group)
        arc_layout.setSpacing(4)

        self.arc_edit = QTextEdit()
        self.arc_edit.setPlaceholderText("描述角色的成长和变化弧线...")
        self.arc_edit.setMaximumHeight(100)
        arc_layout.addWidget(self.arc_edit)

        scroll_layout.addWidget(arc_group)

        notes_group = QGroupBox("备注")
        notes_layout = QVBoxLayout(notes_group)
        notes_layout.setSpacing(4)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("其他备注信息...")
        self.notes_edit.setMaximumHeight(80)
        notes_layout.addWidget(self.notes_edit)

        scroll_layout.addWidget(notes_group)

        appearance_group_box = QGroupBox("出场记录")
        appearance_layout = QVBoxLayout(appearance_group_box)
        appearance_layout.setSpacing(8)

        self.appearance_table = QTableWidget()
        self.appearance_table.setColumnCount(3)
        self.appearance_table.setHorizontalHeaderLabels(["章节", "角色", "描述"])
        self.appearance_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.appearance_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.appearance_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.appearance_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.appearance_table.setMaximumHeight(150)
        appearance_layout.addWidget(self.appearance_table)

        scroll_layout.addWidget(appearance_group_box)

        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_content)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addStretch()

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton("确定")
        self.ok_btn.setObjectName("character_dialog_ok")
        self.ok_btn.clicked.connect(self._on_ok)
        button_layout.addWidget(self.ok_btn)

        layout.addLayout(button_layout)

    def _load_data(self):
        if not self._character_id:
            return

        self._character = character_service.get(self._character_id)
        if not self._character:
            return

        self.name_edit.setText(self._character.name)
        self.aliases_edit.setText(self._character.aliases)
        self.gender_combo.setCurrentText(self._character.gender)
        self.age_edit.setText(self._character.age)
        self.role_type_combo.setCurrentText(self._character.role_type)
        self.status_combo.setCurrentText(self._character.status)
        self.personality_edit.setPlainText(self._character.personality)
        self.appearance_edit.setPlainText(self._character.appearance)
        self.background_edit.setPlainText(self._character.background)
        self.arc_edit.setPlainText(self._character.arc)
        self.notes_edit.setPlainText(self._character.notes)

        self._load_appearances()

    def _load_appearances(self):
        if not self._character_id:
            return

        appearances = character_service.get_appearances(self._character_id)
        self.appearance_table.setRowCount(len(appearances))

        for row, app in enumerate(appearances):
            chapter_title = QTableWidgetItem(app.get("chapter_title", ""))
            role = QTableWidgetItem(app.get("role", ""))
            context = QTableWidgetItem(app.get("context", ""))

            chapter_title.setFlags(chapter_title.flags() & ~Qt.ItemIsEditable)
            role.setFlags(role.flags() & ~Qt.ItemIsEditable)
            context.setFlags(context.flags() & ~Qt.ItemIsEditable)

            self.appearance_table.setItem(row, 0, chapter_title)
            self.appearance_table.setItem(row, 1, role)
            self.appearance_table.setItem(row, 2, context)

    def _on_ok(self):
        name = self.name_edit.text().strip()
        if not name:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "提示", "请输入角色姓名")
            return

        data = {
            "name": name,
            "aliases": self.aliases_edit.text().strip(),
            "gender": self.gender_combo.currentText(),
            "age": self.age_edit.text().strip(),
            "role_type": self.role_type_combo.currentText(),
            "personality": self.personality_edit.toPlainText().strip(),
            "appearance": self.appearance_edit.toPlainText().strip(),
            "background": self.background_edit.toPlainText().strip(),
            "arc": self.arc_edit.toPlainText().strip(),
            "status": self.status_combo.currentText(),
            "notes": self.notes_edit.toPlainText().strip(),
        }

        if self._character_id:
            self._character = character_service.update(self._character_id, **data)
        else:
            self._character = character_service.create(self._project_id, **data)

        if self._character:
            self.accept()

    def get_character(self) -> Optional[Character]:
        return self._character
