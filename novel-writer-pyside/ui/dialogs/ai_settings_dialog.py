"""AI 设置对话框。"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QSpinBox, QPushButton, QLabel,
    QCheckBox, QWidget, QFrame, QMessageBox,
    QGroupBox, QSlider, QDialogButtonBox
)
from PySide6.QtCore import Qt, QThread, Signal
from core.ai.manager import ai_manager
from core.ai.base import AIProviderError


class TestConnectionWorker(QThread):
    """测试连接后台线程。"""
    finished_signal = Signal(bool, str)  # (success, message)

    def __init__(self, provider_name: str, api_key: str, api_base: str, parent=None):
        super().__init__(parent)
        self._provider_name = provider_name
        self._api_key = api_key
        self._api_base = api_base

    def run(self):
        try:
            provider = ai_manager.get_provider(self._provider_name)
            if provider is None:
                self.finished_signal.emit(False, "未知的提供商")
                return
            provider.test_connection(self._api_key, self._api_base)
            self.finished_signal.emit(True, "连接成功！")
        except AIProviderError as e:
            self.finished_signal.emit(False, str(e))
        except Exception as e:
            self.finished_signal.emit(False, f"测试失败: {e}")


class FetchModelsWorker(QThread):
    """获取模型列表后台线程。"""
    finished_signal = Signal(bool, list, str)  # (success, models, message)

    def __init__(self, provider_name: str, api_key: str, api_base: str, parent=None):
        super().__init__(parent)
        self._provider_name = provider_name
        self._api_key = api_key
        self._api_base = api_base

    def run(self):
        try:
            provider = ai_manager.get_provider(self._provider_name)
            if provider is None:
                self.finished_signal.emit(False, [], "未知的提供商")
                return
            models = provider.list_models(self._api_key, self._api_base)
            self.finished_signal.emit(True, models, f"获取到 {len(models)} 个模型")
        except AIProviderError as e:
            self.finished_signal.emit(False, [], str(e))
        except Exception as e:
            self.finished_signal.emit(False, [], f"获取失败: {e}")


class AISettingsDialog(QDialog):
    """AI 设置对话框。"""

    settings_saved = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ai_settings_dialog")
        self.setWindowTitle("AI 设置")
        self.setFixedSize(600, 500)
        self._current_provider_name = None
        self._test_worker = None
        self._fetch_worker = None

        self._init_ui()
        self._load_providers()
        self._load_general_settings()

    def _init_ui(self):
        """初始化 UI。"""
        layout = QVBoxLayout(self)

        # ===== 分组框：AI 提供商 =====
        provider_group = QGroupBox("AI 提供商")
        provider_layout = QVBoxLayout(provider_group)

        self._provider_combo = QComboBox()
        self._provider_combo.setObjectName("ai_provider_combo")
        self._provider_combo.currentIndexChanged.connect(self._on_provider_selected)
        provider_layout.addWidget(self._provider_combo)

        # API Key
        api_key_layout = QHBoxLayout()
        self._api_key_input = QLineEdit()
        self._api_key_input.setEchoMode(QLineEdit.Password)
        self._api_key_input.setPlaceholderText("输入 API Key")
        self._toggle_key_btn = QPushButton("显示")
        self._toggle_key_btn.setFixedWidth(50)
        self._toggle_key_btn.clicked.connect(self._toggle_api_key_visibility)
        api_key_layout.addWidget(self._api_key_input)
        api_key_layout.addWidget(self._toggle_key_btn)
        provider_layout.addWidget(QLabel("API Key:"))
        provider_layout.addLayout(api_key_layout)

        # API Base
        self._api_base_input = QLineEdit()
        self._api_base_input.setPlaceholderText("自定义 API 地址（可选）")
        provider_layout.addWidget(QLabel("API 地址:"))
        provider_layout.addWidget(self._api_base_input)

        # 测试连接
        self._test_btn = QPushButton("测试连接")
        self._test_btn.setObjectName("ai_test_btn")
        self._test_btn.clicked.connect(self._on_test_connection)
        provider_layout.addWidget(self._test_btn)

        layout.addWidget(provider_group)

        # ===== 分组框：生成参数 =====
        params_group = QGroupBox("生成参数")
        params_layout = QFormLayout(params_group)

        # 模型选择
        model_layout = QHBoxLayout()
        self._model_combo = QComboBox()
        self._model_combo.setEditable(True)
        self._fetch_models_btn = QPushButton("获取模型")
        self._fetch_models_btn.setObjectName("ai_fetch_models_btn")
        self._fetch_models_btn.setFixedWidth(80)
        self._fetch_models_btn.clicked.connect(self._on_fetch_models)
        model_layout.addWidget(self._model_combo)
        model_layout.addWidget(self._fetch_models_btn)
        params_layout.addRow("模型:", model_layout)

        # 温度滑块
        temp_layout = QHBoxLayout()
        self._temp_slider = QSlider(Qt.Horizontal)
        self._temp_slider.setRange(0, 200)
        self._temp_slider.setValue(70)
        self._temp_slider.valueChanged.connect(self._on_temp_slider_changed)
        self._temp_label = QLabel("0.7")
        self._temp_label.setFixedWidth(30)
        temp_layout.addWidget(self._temp_slider)
        temp_layout.addWidget(self._temp_label)
        params_layout.addRow("温度:", temp_layout)

        # Max Tokens
        self._max_tokens_input = QSpinBox()
        self._max_tokens_input.setRange(100, 128000)
        self._max_tokens_input.setSingleStep(256)
        self._max_tokens_input.setValue(4000)
        params_layout.addRow("Max Tokens:", self._max_tokens_input)

        layout.addWidget(params_group)

        # ========== 分隔线 ==========
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # 通用设置标题
        general_label = QLabel("通用设置")
        general_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(general_label)

        # 通用设置表单
        general_form = QFormLayout()
        self._autosave_interval_input = QSpinBox()
        self._autosave_interval_input.setRange(10, 300)
        self._autosave_interval_input.setSingleStep(10)
        self._autosave_interval_input.setSuffix(" 秒")
        self._autosave_interval_input.setValue(30)
        general_form.addRow("自动保存间隔：", self._autosave_interval_input)

        self._undo_stack_depth_input = QSpinBox()
        self._undo_stack_depth_input.setRange(10, 500)
        self._undo_stack_depth_input.setSingleStep(10)
        self._undo_stack_depth_input.setSuffix(" 步")
        self._undo_stack_depth_input.setValue(100)
        general_form.addRow("撤销栈深度：", self._undo_stack_depth_input)
        layout.addLayout(general_form)

        # 设为当前 + 状态标签
        bottom_layout = QHBoxLayout()
        self._set_active_check = QCheckBox("设为当前提供商")
        bottom_layout.addWidget(self._set_active_check)
        bottom_layout.addStretch()
        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: gray; font-size: 12px;")
        bottom_layout.addWidget(self._status_label)
        layout.addLayout(bottom_layout)

        # ===== QDialogButtonBox =====
        self._button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self._button_box.accepted.connect(self._on_save)
        self._button_box.rejected.connect(self.reject)
        layout.addWidget(self._button_box)

    def _load_providers(self):
        """加载提供商列表。"""
        self._provider_combo.blockSignals(True)
        self._provider_combo.clear()
        providers = ai_manager.list_providers()

        for p in providers:
            # 状态标记
            prefix = "★ " if p["is_active"] else ""
            status = "●" if p["is_configured"] else "○"
            text = f"{prefix}{p['display_name']} {status}"
            self._provider_combo.addItem(text, p["name"])

        self._provider_combo.blockSignals(False)

        # 默认选中第一个
        if self._provider_combo.count() > 0:
            self._provider_combo.setCurrentIndex(0)

    def _on_provider_selected(self, index: int):
        """选择提供商时加载配置。"""
        if index < 0 or index >= self._provider_combo.count():
            return

        provider_name = self._provider_combo.currentData(Qt.UserRole)
        self._current_provider_name = provider_name

        # 获取配置
        config = ai_manager.get_config(provider_name)
        providers = ai_manager.list_providers()
        provider_info = next((p for p in providers if p["name"] == provider_name), None)

        if not provider_info:
            return

        # 填充表单（优先从加密 Vault 加载 API Key）
        from core.security.vault import vault
        if vault.has_api_key(provider_name):
            self._api_key_input.setText(vault.get_api_key(provider_name))
        else:
            self._api_key_input.setText(config.get("api_key", ""))
        self._api_base_input.setText(config.get("api_base", "") or provider_info["default_api_base"])
        self._api_base_input.setPlaceholderText(provider_info["default_api_base"])

        # 填充模型列表
        self._model_combo.clear()
        for model in provider_info["default_models"]:
            self._model_combo.addItem(model)

        current_model = config.get("model", "")
        if current_model:
            self._model_combo.setCurrentText(current_model)

        self._temp_slider.setValue(int(config.get("temperature", 0.8) * 100))
        self._on_temp_slider_changed(self._temp_slider.value())
        self._max_tokens_input.setValue(config.get("max_tokens", 4000))
        self._set_active_check.setChecked(provider_info["is_active"])

        # 清除状态
        self._status_label.setText("")

    def _load_general_settings(self):
        """从 app_config 表加载通用设置。"""
        from services.app_config_service import app_config_service
        interval = app_config_service.get_int("auto_save_interval", 30)
        self._autosave_interval_input.setValue(interval)
        depth = app_config_service.get_int("undo_stack_depth", 100)
        self._undo_stack_depth_input.setValue(depth)

    def _save_general_settings(self):
        """保存通用设置到 app_config 表。"""
        from services.app_config_service import app_config_service
        app_config_service.set("auto_save_interval",
                               str(self._autosave_interval_input.value()))
        app_config_service.set("undo_stack_depth",
                               str(self._undo_stack_depth_input.value()))

    def _toggle_api_key_visibility(self):
        """切换 API Key 显示/隐藏。"""
        if self._api_key_input.echoMode() == QLineEdit.Password:
            self._api_key_input.setEchoMode(QLineEdit.Normal)
            self._toggle_key_btn.setText("隐藏")
        else:
            self._api_key_input.setEchoMode(QLineEdit.Password)
            self._toggle_key_btn.setText("显示")

    def _on_temp_slider_changed(self, value: int):
        """温度滑块值变化时更新标签。"""
        self._temp_label.setText(f"{value / 100.0:.1f}")

    def _on_test_connection(self):
        """测试连接。"""
        if not self._current_provider_name:
            return

        api_key = self._api_key_input.text().strip()
        api_base = self._api_base_input.text().strip()

        self._test_btn.setEnabled(False)
        self._test_btn.setText("测试中...")
        self._status_label.setText("正在测试连接...")

        self._test_worker = TestConnectionWorker(
            self._current_provider_name, api_key, api_base, self
        )
        self._test_worker.finished_signal.connect(self._on_test_finished)
        self._test_worker.start()

    def _on_test_finished(self, success: bool, message: str):
        """测试连接完成。"""
        self._test_btn.setEnabled(True)
        self._test_btn.setText("测试连接")

        if success:
            self._status_label.setStyleSheet("color: green; font-size: 12px;")
            self._status_label.setText(f"✓ {message}")
        else:
            self._status_label.setStyleSheet("color: red; font-size: 12px;")
            self._status_label.setText(f"✗ {message}")

    def _on_fetch_models(self):
        """获取模型列表。"""
        if not self._current_provider_name:
            return

        api_key = self._api_key_input.text().strip()
        api_base = self._api_base_input.text().strip()

        self._fetch_models_btn.setEnabled(False)
        self._fetch_models_btn.setText("获取中...")
        self._status_label.setText("正在获取模型列表...")

        self._fetch_worker = FetchModelsWorker(
            self._current_provider_name, api_key, api_base, self
        )
        self._fetch_worker.finished_signal.connect(self._on_fetch_models_finished)
        self._fetch_worker.start()

    def _on_fetch_models_finished(self, success: bool, models: list, message: str):
        """获取模型列表完成。"""
        self._fetch_models_btn.setEnabled(True)
        self._fetch_models_btn.setText("获取模型")

        if success and models:
            self._model_combo.clear()
            for model in models:
                self._model_combo.addItem(model)
            self._status_label.setStyleSheet("color: green; font-size: 12px;")
            self._status_label.setText(f"✓ {message}")
        else:
            self._status_label.setStyleSheet("color: red; font-size: 12px;")
            self._status_label.setText(f"✗ {message}")

    def _on_save(self):
        """保存配置。"""
        if not self._current_provider_name:
            return

        api_key = self._api_key_input.text().strip()
        api_base = self._api_base_input.text().strip()
        model = self._model_combo.currentText().strip()
        temperature = self._temp_slider.value() / 100.0
        max_tokens = self._max_tokens_input.value()

        try:
            ai_manager.save_config(
                name=self._current_provider_name,
                api_key=api_key,
                api_base=api_base,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # 保存 API Key 到加密保险库（Vault）
            from core.security.vault import vault
            if api_key:
                vault.store_api_key(self._current_provider_name, api_key)
            else:
                vault.delete_api_key(self._current_provider_name)

            # 设为当前提供商
            if self._set_active_check.isChecked():
                ai_manager.set_active_provider(self._current_provider_name)

            # 刷新列表
            self._load_providers()

            # 保存通用设置
            self._save_general_settings()

            # 通知主窗口更新
            self.settings_saved.emit()

            QMessageBox.information(self, "成功", "配置已保存")

        except AIProviderError as e:
            QMessageBox.warning(self, "保存失败", str(e))
        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"保存配置时出错: {e}")
