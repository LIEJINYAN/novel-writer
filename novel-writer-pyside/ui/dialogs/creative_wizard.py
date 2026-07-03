"""七步法创作向导。"""
from PySide6.QtWidgets import QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QLineEdit, QComboBox, QPushButton, QSpinBox, QFormLayout
from PySide6.QtCore import Qt


class IntroPage(QWizardPage):
    """第一步：创作宪法输入。"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("第1步：创作宪法")
        self.setSubTitle("定义小说的核心原则、风格指南和质量标准")
        layout = QFormLayout(self)
        self.genre_input = QComboBox()
        self.genre_input.addItems(["玄幻","仙侠","都市","科幻","历史","悬疑","言情","武侠","游戏","其他"])
        self.genre_input.setEditable(True)
        layout.addRow("小说类型:", self.genre_input)
        self.audience_input = QLineEdit()
        self.audience_input.setPlaceholderText("如：网文读者、严肃文学读者")
        layout.addRow("目标读者:", self.audience_input)
        self.length_input = QSpinBox()
        self.length_input.setRange(10000, 5000000)
        self.length_input.setValue(200000)
        self.length_input.setSingleStep(10000)
        layout.addRow("预计字数:", self.length_input)
        self.tone_input = QLineEdit()
        self.tone_input.setPlaceholderText("如：轻松幽默、沉重严肃")
        layout.addRow("基调:", self.tone_input)
        self.themes_input = QLineEdit()
        self.themes_input.setPlaceholderText("如：友情、成长、复仇")
        layout.addRow("主题:", self.themes_input)
        self.ai_btn = QPushButton("AI 生成宪法")
        layout.addRow(self.ai_btn)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(150)
        layout.addRow(self.result_text)


class ResultPage(QWizardPage):
    """后续步骤：显示 AI 结果（通用页面）。"""
    def __init__(self, title, subtitle, parent=None):
        super().__init__(parent)
        self.setTitle(title)
        self.setSubTitle(subtitle)
        layout = QVBoxLayout(self)
        self.ai_btn = QPushButton("AI 生成")
        layout.addWidget(self.ai_btn)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text, 1)


class CreativeWizard(QWizard):
    """创作向导 - 7 步创作流程。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("创作向导")
        self.setFixedSize(700, 550)
        self.setWizardStyle(QWizard.ModernStyle)

        # 7 个页面
        self._page1 = IntroPage()
        self._page2 = ResultPage("第2步：故事规格", "定义故事的核心结构和要素")
        self._page3 = ResultPage("第3步：决策澄清", "识别并澄清需要决策的关键点")
        self._page4 = ResultPage("第4步：创作计划", "制定详细的章节规划")
        self._page5 = ResultPage("第5步：任务分解", "将创作计划分解为可执行任务")
        self._page6 = ResultPage("第6步：AI 续写", "打开编辑器并触发续写")
        self._page7 = ResultPage("第7步：质量分析", "综合验证分析，确保质量一致")

        self.addPage(self._page1)
        self.addPage(self._page2)
        self.addPage(self._page3)
        self.addPage(self._page4)
        self.addPage(self._page5)
        self.addPage(self._page6)
        self.addPage(self._page7)

        # 第 6 步不需要 AI 生成按钮，显示提示文字
        self._page6.ai_btn.hide()
        hint_label = QLabel("请回到编辑器，打开目标章节后使用「AI 续写」功能（快捷键 Ctrl+I）")
        hint_label.setWordWrap(True)
        hint_label.setStyleSheet("color: #666; padding: 12px; font-size: 13px;")
        hint_layout = self._page6.layout()
        hint_layout.insertWidget(0, hint_label)

        # 连接 AI 按钮
        self._page1.ai_btn.clicked.connect(self._on_generate_constitution)
        for page in [self._page2, self._page3, self._page4, self._page5]:
            page.ai_btn.clicked.connect(lambda checked, p=page: self._on_ai_generate(p))

    def _on_generate_constitution(self):
        """生成创作宪法。"""
        from services.ai_service import AIService
        p = self._page1
        ai = AIService()
        try:
            worker = ai.create_constitution(
                genre=p.genre_input.currentText(),
                target_audience=p.audience_input.text(),
                estimated_length=str(p.length_input.value()),
                tone=p.tone_input.text(),
                themes=p.themes_input.text(),
                user_input="",
            )
            worker.finished_signal.connect(lambda t: p.result_text.setText(t))
            worker.error_signal.connect(lambda e: p.result_text.setText(f"[错误] {e}"))
            worker.start()
            p.result_text.setText("正在生成...")
        except Exception as e:
            p.result_text.setText(f"[错误] {e}")

    def _on_ai_generate(self, page):
        """通用 AI 生成。"""
        page.result_text.setText("功能开发中，请手动填写")
