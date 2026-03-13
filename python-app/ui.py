from __future__ import annotations

import threading
from typing import Optional

from PySide6.QtCore import QPoint, Qt, Signal, QObject
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from api_client import TranslateResult, translate_text
from config import AppConfig


class TranslatorController(QObject):
    show_loading = Signal(str)
    show_result = Signal(TranslateResult)

    def __init__(self, config: AppConfig, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._config = config

    def start_translate(self, text: str) -> None:
        def worker() -> None:
            result = translate_text(text, self._config)
            self.show_result.emit(result)

        self.show_loading.emit(text)
        threading.Thread(target=worker, daemon=True).start()


class BubbleWindow(QWidget):
    def __init__(self, config: AppConfig, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent, Qt.Tool | Qt.FramelessWindowHint)
        self.setWindowTitle("Click Translate")
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self._config = config
        self._controller = TranslatorController(config)
        self._controller.show_loading.connect(self._on_show_loading)
        self._controller.show_result.connect(self._on_show_result)

        self._init_ui()

    def _init_ui(self) -> None:
        root = QVBoxLayout()

        title_bar = QHBoxLayout()
        self.title_label = QLabel("🌐 Click Translate")
        self.title_label.setStyleSheet(
            "color: #f9fafb; font-weight: 600; font-size: 13px;"
        )
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedWidth(24)
        self.close_btn.setStyleSheet(
            "QPushButton { border: none; color: #9ca3af; background: transparent; }"
            "QPushButton:hover { background: rgba(156,163,175,0.18); }"
        )
        # 仅隐藏窗口，不销毁，避免重复创建 / 残留
        self.close_btn.clicked.connect(self.hide)
        title_bar.addWidget(self.title_label)
        title_bar.addStretch()
        title_bar.addWidget(self.close_btn)

        header = QWidget()
        header.setLayout(title_bar)
        header.setStyleSheet(
            "background: #111827; border-bottom: 1px solid #1f2937; border-radius: 10px 10px 0 0;"
        )

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet(
            "QTextEdit {"
            "  border: none;"
            "  font-size: 14px;"
            "  line-height: 1.6;"
            "  color: #f9fafb;"
            "  background-color: #020617;"
            "}"
        )

        self.copy_btn = QPushButton("📋")
        self.copy_btn.setFixedWidth(32)
        self.copy_btn.setStyleSheet(
            "QPushButton {"
            "  padding: 4px;"
            "  border-radius: 999px;"
            "  color: #e5e7eb;"
            "  font-size: 13px;"
            "  background-color: #1f2937;"
            "}"
            "QPushButton:hover { background-color: #374151; }"
            "QPushButton:pressed { background-color: #4b5563; }"
        )
        self.copy_btn.clicked.connect(self._on_copy_clicked)

        body = QVBoxLayout()
        body.addWidget(self.text_area)
        body.addWidget(self.copy_btn)

        body_widget = QWidget()
        body_widget.setLayout(body)
        body_widget.setStyleSheet(
            "background: #020617; border-radius: 0 0 10px 10px;"
        )

        root.addWidget(header)
        root.addWidget(body_widget)

        container = QWidget()
        container.setLayout(root)
        container.setStyleSheet(
            "background: transparent; border-radius: 10px;"
            "box-shadow: 0px 14px 40px rgba(0, 0, 0, 0.65);"
        )

        layout = QVBoxLayout()
        layout.addWidget(container)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.resize(360, 220)

    def _on_show_loading(self, text: str) -> None:
        self.text_area.setPlainText("翻译中...\n\n" + text)
        self.copy_btn.setText("📋")
        self.copy_btn.setEnabled(False)
        self._move_to_cursor()
        self.show()
        self.activateWindow()

    def _on_show_result(self, result: TranslateResult) -> None:
        if result.error:
            self.text_area.setPlainText(f"❌ {result.error}")
            self.copy_btn.setEnabled(False)
        else:
            self.text_area.setPlainText(result.translation or "")
            self.copy_btn.setEnabled(True)

    def _on_copy_clicked(self) -> None:
        text = self.text_area.toPlainText()
        if not text:
            return
        QApplication.clipboard().setText(text)
        self.copy_btn.setText("✅ 已复制")
        self.copy_btn.setEnabled(False)

    def closeEvent(self, event) -> None:
        # 拦截系统关闭事件，统一改为隐藏窗口
        self.hide()
        event.ignore()

    def _move_to_cursor(self) -> None:
        screen_pos: QPoint = QCursor.pos()
        self.move(screen_pos + QPoint(10, 10))

    def translate(self, text: str) -> None:
        self._controller.start_translate(text)

