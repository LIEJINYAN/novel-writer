"""时间线事件编辑对话框。"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QComboBox, QDialogButtonBox, QMessageBox,
)
from services.timeline_service import timeline_service
from models import Volume, Chapter
from models.database import db_manager


class TimelineEventDialog(QDialog):
    """编辑时间线事件。"""

    def __init__(self, project_id: int, event_id: int = None, parent=None):
        super().__init__(parent)
        self._project_id = project_id
        self._event_id = event_id
        self._editing = event_id is not None
        self.setWindowTitle("编辑事件" if self._editing else "新建事件")
        self.setMinimumWidth(450)
        self._init_ui()
        self._load_chapters()
        if self._editing:
            self._load_event()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        form.setSpacing(10)

        # 事件名称
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("事件名称")
        form.addRow("名称:", self._name_input)

        # 描述
        self._desc_input = QTextEdit()
        self._desc_input.setPlaceholderText("事件描述...")
        form.addRow("描述:", self._desc_input)

        # 故事内日期
        self._date_input = QLineEdit()
        self._date_input.setPlaceholderText("如: 第3年春、纪元1024年")
        form.addRow("故事内日期:", self._date_input)

        # 地点
        self._location_input = QLineEdit()
        self._location_input.setPlaceholderText("发生地点")
        form.addRow("地点:", self._location_input)

        # 关联章节
        self._chapter_combo = QComboBox()
        self._chapter_combo.addItem("（无）", None)
        form.addRow("关联章节:", self._chapter_combo)

        # 重要性
        self._importance_combo = QComboBox()
        self._importance_combo.addItems(["核心", "重要", "次要"])
        form.addRow("重要性:", self._importance_combo)

        layout.addLayout(form)

        # 按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_chapters(self):
        """加载项目章节。"""
        session = db_manager.get_project_session()
        try:
            chapters = session.query(Chapter).filter(
                Chapter.is_deleted == 0,
            ).order_by(Chapter.chapter_number).all()
            for ch in chapters:
                self._chapter_combo.addItem(
                    f"第{ch.chapter_number}章 {ch.title}", ch.id
                )
        finally:
            session.close()

    def _load_event(self):
        """加载已有事件数据。"""
        ev = timeline_service.get(self._event_id)
        if not ev:
            return

        self._name_input.setText(ev.event_name)
        self._desc_input.setPlainText(ev.description)
        self._date_input.setText(ev.story_date)
        self._location_input.setText(ev.location)

        if ev.chapter_id:
            idx = self._chapter_combo.findData(ev.chapter_id)
            if idx >= 0:
                self._chapter_combo.setCurrentIndex(idx)

        imp_idx = self._importance_combo.findText(ev.importance)
        if imp_idx >= 0:
            self._importance_combo.setCurrentIndex(imp_idx)

    def _on_save(self):
        """保存事件。"""
        name = self._name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "验证失败", "事件名称不能为空")
            return

        data = {
            "event_name": name,
            "description": self._desc_input.toPlainText().strip(),
            "story_date": self._date_input.text().strip(),
            "location": self._location_input.text().strip(),
            "chapter_id": self._chapter_combo.currentData(),
            "importance": self._importance_combo.currentText(),
        }

        try:
            if self._editing:
                timeline_service.update(self._event_id, **data)
            else:
                timeline_service.create(self._project_id, name, **data)
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "保存失败", str(e))
