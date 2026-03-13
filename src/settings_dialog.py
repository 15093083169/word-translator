"""
划词翻译 - 设置对话框
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QCheckBox, QPushButton,
    QFormLayout, QMessageBox, QWidget, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class SettingsDialog(QDialog):
    """设置窗口：API Key、目标语言、开机自启"""

    def __init__(self, config, config_manager, parent=None):
        super().__init__(parent)
        self.config = config
        self.config_manager = config_manager
        self.setWindowTitle("划词翻译 - 设置")
        self.setFixedSize(420, 320)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # 标题
        title = QLabel("⚙️ 设置")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        # 表单
        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # API Key
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("输入你的智谱 AI API Key")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setText(self.config.get("api_key", ""))
        form.addRow("API Key:", self.api_key_input)

        # 模型
        self.model_input = QComboBox()
        self.model_input.addItems(["glm-4-flash", "glm-4-air", "glm-4-plus"])
        idx = self.model_input.findText(self.config.get("model", "glm-4-flash"))
        if idx >= 0:
            self.model_input.setCurrentIndex(idx)
        form.addRow("模型:", self.model_input)

        # 目标语言
        self.lang_input = QComboBox()
        self.lang_input.addItems(["中文", "英文", "日文", "韩文", "法文", "德文", "俄文"])
        idx = self.lang_input.findText(self.config.get("target_lang", "中文"))
        if idx >= 0:
            self.lang_input.setCurrentIndex(idx)
        form.addRow("翻译为:", self.lang_input)

        # 开机自启
        self.auto_start_check = QCheckBox("开机自动启动")
        self.auto_start_check.setChecked(self.config.get("auto_start", False))
        form.addRow("", self.auto_start_check)

        layout.addLayout(form)

        layout.addStretch()

        # 按钮栏
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.save_btn = QPushButton("💾 保存")
        self.save_btn.setFixedHeight(36)
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self._save)
        btn_layout.addWidget(self.save_btn)

        layout.addLayout(btn_layout)

        # 全局样式
        self.setStyleSheet("""
            QDialog {
                background: #f8f9fa;
            }
            QLabel {
                color: #555;
                font-size: 13px;
            }
            QLineEdit, QComboBox {
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                background: white;
                font-size: 13px;
                min-height: 20px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #3498db;
            }
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
            QCheckBox {
                color: #555;
                font-size: 13px;
                spacing: 6px;
            }
        """)

    def _save(self):
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "提示", "请输入 API Key")
            return

        self.config["api_key"] = api_key
        self.config["model"] = self.model_input.currentText()
        self.config["target_lang"] = self.lang_input.currentText()
        self.config["auto_start"] = self.auto_start_check.isChecked()

        # 保存到文件
        self.config_manager.save_config(self.config)

        # 设置开机自启
        self._set_auto_start(self.config["auto_start"])

        QMessageBox.information(self, "成功", "设置已保存！\n\n选中文字后，连按两次 Ctrl 即可翻译。")
        self.accept()

    def _set_auto_start(self, enable):
        """设置 Windows 开机自启动"""
        try:
            import winreg
            import sys
            import os

            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE
            )

            if enable:
                # 获取 exe 路径
                if getattr(sys, "frozen", False):
                    exe_path = sys.executable
                else:
                    exe_path = os.path.abspath(
                        os.path.join(os.path.dirname(__file__), "..", "main.py")
                    )
                    # 如果是开发模式，用 pythonw.exe
                    python_exe = sys.executable.replace("python.exe", "pythonw.exe")
                    exe_path = f'"{python_exe}" "{exe_path}"'

                winreg.SetValueEx(key, "WordTranslator", 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(key, "WordTranslator")
                except FileNotFoundError:
                    pass

            winreg.CloseKey(key)
        except Exception as e:
            print(f"设置开机自启失败: {e}")
