"""AI 创作向导 - 分步引导创建新项目。"""

from PySide6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QTextEdit, QRadioButton,
    QGroupBox, QListWidget, QListWidgetItem, QPushButton,
    QButtonGroup, QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from dataclasses import dataclass, field


@dataclass
class WizardResult:
    """向导结果。"""
    genre: str = ""
    method_name: str = ""
    protagonist: str = ""
    world_keywords: str = ""
    description: str = ""


class GenrePage(QWizardPage):
    """第1步：选择小说类型和题材。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("选择小说类型")
        self.setSubTitle("请选择你要创作的小说类型")

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("小说类型："))
        self._genre_combo = QComboBox()
        self._genre_combo.addItems(["玄幻", "都市", "言情", "科幻", "悬疑", "历史", "武侠", "奇幻", "仙侠", "轻小说"])
        layout.addWidget(self._genre_combo)

        layout.addWidget(QLabel("题材描述（可选）："))
        self._desc_edit = QTextEdit()
        self._desc_edit.setMaximumHeight(80)
        self._desc_edit.setPlaceholderText("简短描述你的故事主题，如'重生校园'、'星际冒险'等")
        layout.addWidget(self._desc_edit)

        layout.addStretch()

    def get_genre(self) -> str:
        return self._genre_combo.currentText()

    def get_description(self) -> str:
        return self._desc_edit.toPlainText().strip()


class MethodPage(QWizardPage):
    """第2步：选择写作方法。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("选择写作方法")
        self.setSubTitle("选择一个结构化写作方法来规划你的小说")

        layout = QVBoxLayout(self)
        self._method_list = QListWidget()
        self._method_list.setMinimumHeight(150)
        layout.addWidget(QLabel("推荐方法（按匹配度排序）："))
        layout.addWidget(self._method_list)

        self._info_label = QLabel("选择一个方法查看说明")
        self._info_label.setWordWrap(True)
        self._info_label.setStyleSheet("color: #666; padding: 8px;")
        layout.addWidget(self._info_label)

        self._method_list.currentItemChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self, current, previous):
        if current:
            self._info_label.setText(current.data(Qt.UserRole))

    def set_recommendations(self, recommendations: list):
        """设置推荐结果。"""
        self._method_list.clear()
        for rec in recommendations:
            item = QListWidgetItem(f"{rec.method_name}（{rec.score}分）")
            reasons = "\n".join(f"• {r}" for r in rec.reasons)
            item.setData(Qt.UserRole, reasons)
            item.setData(Qt.UserRole + 1, rec.method_name)
            self._method_list.addItem(item)

        if self._method_list.count() > 0:
            self._method_list.setCurrentRow(0)

    def get_method_name(self) -> str:
        item = self._method_list.currentItem()
        if item:
            return item.data(Qt.UserRole + 1)
        return ""


class SettingPage(QWizardPage):
    """第3步：设定主角和世界观关键词。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("设定主角和世界观")
        self.setSubTitle("输入你的故事核心设定")

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("主角名称："))
        self._protagonist_edit = QLineEdit()
        self._protagonist_edit.setPlaceholderText("输入主角名字")
        layout.addWidget(self._protagonist_edit)

        layout.addWidget(QLabel("世界观关键词："))
        self._keywords_edit = QLineEdit()
        self._keywords_edit.setPlaceholderText("如'修真、宗门、炼器'或'赛博朋克、人工智能'")
        layout.addWidget(self._keywords_edit)

        layout.addStretch()

    def get_protagonist(self) -> str:
        return self._protagonist_edit.text().strip()

    def get_keywords(self) -> str:
        return self._keywords_edit.text().strip()


class PreviewPage(QWizardPage):
    """第4步：预览大纲结构。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("预览大纲结构")
        self.setSubTitle("确认以下信息，然后创建项目")

        layout = QVBoxLayout(self)

        self._preview_text = QTextEdit()
        self._preview_text.setReadOnly(True)
        layout.addWidget(self._preview_text)

    def set_preview(self, genre: str, method_name: str,
                    protagonist: str, keywords: str):
        """设置预览信息。"""
        from core.methods.advisor import method_advisor

        method = method_advisor.get_method(method_name)
        text = f"【项目概要】\n\n"
        text += f"小说类型：{genre}\n"
        text += f"写作方法：{method_name}\n"
        text += f"主角：{protagonist or '（待定）'}\n"
        text += f"世界观关键词：{keywords or '（待定）'}\n\n"

        if method:
            text += f"【{method_name}结构】\n"
            for stage in method.stages:
                text += f"  {stage.order + 1}. {stage.name}\n"
                text += f"     {stage.description}\n\n"

        self._preview_text.setPlainText(text)


class CreationWizard(QWizard):
    """创作向导。"""

    project_created = Signal(dict)  # 创建项目后发射项目信息

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI 创作向导")
        self.setMinimumSize(550, 450)

        self._genre_page = GenrePage()
        self._method_page = MethodPage()
        self._setting_page = SettingPage()
        self._preview_page = PreviewPage()

        self.addPage(self._genre_page)
        self.addPage(self._method_page)
        self.addPage(self._setting_page)
        self.addPage(self._preview_page)

        # 在显示方法页面时更新推荐
        self.currentIdChanged.connect(self._on_page_changed)

    def _on_page_changed(self, page_id):
        """页面切换时更新推荐。"""
        if self.page(page_id) == self._method_page:
            genre = self._genre_page.get_genre()
            from core.methods.advisor import method_advisor
            recs = method_advisor.recommend(genre, "新手", "长篇")
            self._method_page.set_recommendations(recs)

        elif self.page(page_id) == self._preview_page:
            self._preview_page.set_preview(
                self._genre_page.get_genre(),
                self._method_page.get_method_name(),
                self._setting_page.get_protagonist(),
                self._setting_page.get_keywords(),
            )

    def get_result(self) -> WizardResult:
        """获取向导结果。"""
        return WizardResult(
            genre=self._genre_page.get_genre(),
            method_name=self._method_page.get_method_name(),
            protagonist=self._setting_page.get_protagonist(),
            world_keywords=self._setting_page.get_keywords(),
            description=self._genre_page.get_description(),
        )

    def accept(self):
        """向导完成。"""
        result = self.get_result()
        self.project_created.emit({
            "genre": result.genre,
            "method": result.method_name,
            "protagonist": result.protagonist,
            "keywords": result.world_keywords,
            "description": result.description,
        })
        super().accept()
