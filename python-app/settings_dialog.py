from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QPushButton,
    QWidget,
)

from config import AppConfig


class SettingsDialog(QDialog):
    def __init__(self, config: AppConfig, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._config = config
        self.setWindowTitle("Click Translate - 设置 GLM API Key")
        self.setMinimumWidth(460)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 20, 24, 16)
        layout.setSpacing(14)

        self.setStyleSheet("background-color: #020617; color: #e5e7eb;")

        title = QLabel("🌐 Click Translate")
        title.setStyleSheet("font-size: 20px; font-weight: 600; color: #f9fafb;")
        layout.addWidget(title)

        desc = QLabel(
            "首次使用，请输入你的智谱 GLM API Key。\n"
            "可在下方点击链接前往 bigmodel 控制台获取。"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #9ca3af; font-size: 13px;")
        layout.addWidget(desc)

        link = QLabel(
            '<a href="https://open.bigmodel.cn">在浏览器中打开 bigmodel 控制台（https://open.bigmodel.cn）</a>'
        )
        link.setOpenExternalLinks(True)
        link.setStyleSheet("color: #38bdf8; font-size: 13px;")
        layout.addWidget(link)

        model_info = QLabel("当前使用模型：glm-4-flash（官方提供免费额度，可直接使用）")
        model_info.setStyleSheet("color: #6b7280; font-size: 12px;")
        layout.addWidget(model_info)

        self._edit = QLineEdit()
        self._edit.setPlaceholderText("请输入 GLM API Key")
        self._edit.setEchoMode(QLineEdit.Password)
        self._edit.setText(config.api_key or "")
        self._edit.setStyleSheet(
            "QLineEdit {"
            "  border: 1px solid #374151;"
            "  border-radius: 6px;"
            "  padding: 8px 10px;"
            "  font-size: 13px;"
            "  background-color: #020617;"
            "  color: #e5e7eb;"
            "}"
            "QLineEdit:focus {"
            "  border-color: #38bdf8;"
            "}"
        )
        layout.addWidget(self._edit)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_cancel = QPushButton("取消")
        btn_ok = QPushButton("保存")

        btn_cancel.setStyleSheet(
            "QPushButton {"
            "  padding: 6px 14px;"
            "  border-radius: 6px;"
            "  border: 1px solid #4b5563;"
            "  background-color: transparent;"
            "  color: #e5e7eb;"
            "  font-size: 13px;"
            "}"
            "QPushButton:hover { background-color: #111827; }"
        )
        btn_ok.setStyleSheet(
            "QPushButton {"
            "  padding: 6px 16px;"
            "  border-radius: 6px;"
            "  border: none;"
            "  background-color: #0ea5e9;"
            "  color: #020617;"
            "  font-size: 13px;"
            "  font-weight: 500;"
            "}"
            "QPushButton:hover { background-color: #38bdf8; }"
            "QPushButton:pressed { background-color: #0891b2; }"
        )

        btn_cancel.clicked.connect(self.reject)
        btn_ok.clicked.connect(self.accept)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)

        layout.addLayout(btn_row)

        self.setLayout(layout)

    def get_api_key(self) -> str:
        return self._edit.text().strip()


def show_settings_dialog(config: AppConfig, parent: Optional[QWidget] = None) -> bool:
    """
    弹出设置对话框，返回是否成功保存了非空 Key。
    """
    dlg = SettingsDialog(config, parent)
    result = dlg.exec()
    if result == QDialog.Accepted:
        key = dlg.get_api_key()
        if key:
            config.api_key = key
            config.save()
            return True
    return False

