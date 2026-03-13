"""
划词翻译 - 翻译悬浮窗
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QApplication, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt5.QtGui import QFont, QCursor, QIcon


class TranslateWindow(QWidget):
    """无边框悬浮翻译窗口"""

    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.current_result = ""
        self._loading_dots = 0

        self._setup_ui()

    def _setup_ui(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumWidth(320)
        self.setMaximumWidth(500)

        # 外层布局（加阴影边距）
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(10, 10, 10, 10)

        # 容器
        self.container = QWidget()
        self.container.setObjectName("container")

        # 阴影
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(80, 80, 80, 60)
        self.container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        # 标题栏
        header_layout = QHBoxLayout()
        self.title_label = QLabel("📖 划词翻译")
        self.title_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #2c3e50;"
        )
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
                font-size: 14px;
                color: #999;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #f0f0f0;
                color: #333;
            }
            """
        )
        self.close_btn.clicked.connect(self.hide)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.close_btn)
        layout.addLayout(header_layout)

        # 分割线
        line = QLabel()
        line.setFixedHeight(1)
        line.setStyleSheet("background: #eee;")
        layout.addWidget(line)

        # 原文
        self.source_label = QLabel()
        self.source_label.setWordWrap(True)
        self.source_label.setStyleSheet(
            "color: #888; font-size: 12px; padding: 4px 0; "
            "border-left: 3px solid #3498db; padding-left: 8px;"
        )
        layout.addWidget(self.source_label)

        # 译文
        self.result_label = QLabel()
        self.result_label.setWordWrap(True)
        self.result_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.result_label.setStyleSheet(
            "color: #2c3e50; font-size: 15px; padding: 8px 0; "
            "line-height: 1.6;"
        )
        layout.addWidget(self.result_label)

        # 按钮栏
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.copy_btn = QPushButton("📋 复制翻译")
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.setVisible(False)
        self.copy_btn.setFixedHeight(32)
        self.copy_btn.clicked.connect(self._copy_result)
        btn_layout.addWidget(self.copy_btn)
        layout.addLayout(btn_layout)

        # 样式
        self.container.setStyleSheet(
            """
            #container {
                background: #ffffff;
                border-radius: 12px;
                border: 1px solid #e8e8e8;
            }
            QPushButton#copy_btn, QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
            """
        )

        # 给 copy_btn 设定 objectName
        self.copy_btn.setObjectName("copy_btn")

        outer_layout.addWidget(self.container)

        # 加载动画定时器
        self._loading_timer = QTimer()
        self._loading_timer.timeout.connect(self._update_loading)
        self._loading_timer.setInterval(500)

    def show_translation(self, text):
        """开始翻译流程"""
        # 定位窗口到光标附近
        cursor_pos = QCursor.pos()
        screen = QApplication.screenAt(cursor_pos)
        if screen:
            geo = screen.availableGeometry()
            x = cursor_pos.x() + 15
            y = cursor_pos.y() + 15
            # 防止超出屏幕
            self.setMinimumWidth(320)
            self.setMaximumWidth(500)
            self.adjustSize()
            w = self.width()
            h = self.height()
            if x + w > geo.right():
                x = geo.right() - w - 10
            if y + h > geo.bottom():
                y = geo.bottom() - h - 10
            self.move(x, y)

        # 设置原文
        display_text = text[:200] + ("..." if len(text) > 200 else "")
        self.source_label.setText(display_text)
        self.source_label.setVisible(True)

        # 加载状态
        self.current_result = ""
        self._loading_dots = 0
        self.result_label.setStyleSheet(
            "color: #999; font-size: 14px; padding: 8px 0;"
        )
        self.result_label.setText("⏳ 翻译中")
        self.copy_btn.setVisible(False)
        self._loading_timer.start()

        self.show()
        self.raise_()
        self._adjust_height()

        # 异步翻译
        import threading

        def do_translate():
            try:
                result = self.translator.translate(text)
                self.current_result = result
                QTimer.singleShot(0, lambda: self._on_result(result))
            except Exception as e:
                QTimer.singleShot(0, lambda: self._on_error(str(e)))

        threading.Thread(target=do_translate, daemon=True).start()

    def _update_loading(self):
        self._loading_dots = (self._loading_dots + 1) % 4
        dots = "·" * self._loading_dots
        self.result_label.setText(f"⏳ 翻译中{dots}")

    def _on_result(self, result):
        self._loading_timer.stop()
        self.result_label.setText(result)
        self.result_label.setStyleSheet(
            "color: #2c3e50; font-size: 15px; padding: 8px 0; "
            "line-height: 1.6;"
        )
        self.copy_btn.setVisible(True)
        self._adjust_height()

    def _on_error(self, error_msg):
        self._loading_timer.stop()
        self.result_label.setText(f"❌ {error_msg}")
        self.result_label.setStyleSheet(
            "color: #e74c3c; font-size: 13px; padding: 8px 0;"
        )
        self.copy_btn.setVisible(False)
        self._adjust_height()

    def _copy_result(self):
        if self.current_result:
            QApplication.clipboard().setText(self.current_result)
            self.copy_btn.setText("✅ 已复制")
            QTimer.singleShot(2000, lambda: self.copy_btn.setText("📋 复制翻译"))

    def _adjust_height(self):
        """调整窗口高度适配内容"""
        self.setMinimumWidth(320)
        self.setMaximumWidth(500)
        self.adjustSize()
        self.container.adjustSize()
        self.adjustSize()
