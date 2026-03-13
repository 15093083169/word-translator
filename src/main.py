"""
划词翻译 - 主程序入口
系统托盘 + 热键监听 + 翻译窗口
"""
import sys
import os

# 修复 Windows 控制台编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 将 src 目录加入路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox
)
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import QSize, Qt

from config import load_config, save_config, is_first_run
from translator import Translator
from hotkey_manager import HotkeyManager
from translate_window import TranslateWindow
from settings_dialog import SettingsDialog


def create_tray_icon():
    """程序化生成托盘图标"""
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # 蓝色圆形背景
    painter.setBrush(QColor("#3498db"))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(2, 2, size - 4, size - 4)

    # 白色 "T" 字母
    painter.setBrush(Qt.white)
    painter.setPen(Qt.NoPen)
    # T 横杠
    painter.drawRoundedRect(16, 16, 32, 8, 3, 3)
    # T 竖杠
    painter.drawRoundedRect(26, 16, 8, 32, 3, 3)

    painter.end()
    return QIcon(pixmap)


class WordTranslatorApp:
    """划词翻译主应用"""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # 加载配置
        self.config = load_config()

        # 翻译器
        self.translator = Translator(self.config)

        # 翻译窗口
        self.translate_window = TranslateWindow(self.translator)

        # 系统托盘
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(create_tray_icon())
        self.tray_icon.setToolTip("划词翻译 - 双击 Ctrl 翻译")
        self._setup_tray_menu()
        self.tray_icon.show()

        # 热键管理
        self.hotkey = HotkeyManager(self._on_hotkey)
        self.hotkey.start()

        # 首次运行提示
        if is_first_run():
            self._show_first_run()

    def _setup_tray_menu(self):
        """创建托盘右键菜单"""
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 6px;
                font-size: 13px;
            }
            QMenu::item {
                padding: 8px 30px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background: #3498db;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background: #eee;
                margin: 4px 10px;
            }
        """)

        # 开机自启
        self.auto_start_action = QAction("🖥️ 开机自启动", menu)
        self.auto_start_action.setCheckable(True)
        self.auto_start_action.setChecked(self.config.get("auto_start", False))
        self.auto_start_action.triggered.connect(self._toggle_auto_start)
        menu.addAction(self.auto_start_action)

        menu.addSeparator()

        # 设置
        settings_action = QAction("⚙️ 设置", menu)
        settings_action.triggered.connect(self._show_settings)
        menu.addAction(settings_action)

        menu.addSeparator()

        # 退出
        quit_action = QAction("🚪 退出", menu)
        quit_action.triggered.connect(self._quit)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)

        # 左键点击也可以打开设置
        self.tray_icon.activated.connect(self._on_tray_activated)

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self._show_settings()

    def _on_hotkey(self, text):
        """热键触发回调"""
        self.translate_window.show_translation(text)

    def _show_first_run(self):
        """首次运行：提示输入 API Key"""
        self.tray_icon.showMessage(
            "划词翻译",
            "欢迎使用！请右键托盘图标 → 设置，输入 API Key\n\n"
            "使用方法：选中文字，连按两次 Ctrl",
            QSystemTrayIcon.Information,
            5000
        )
        # 延迟显示设置窗口
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1000, self._show_settings)

    def _show_settings(self):
        dialog = SettingsDialog(self.config, self)
        dialog.exec_()
        # 刷新配置
        self.config = load_config()
        self.translator = Translator(self.config)
        self.auto_start_action.setChecked(self.config.get("auto_start", False))

    def _toggle_auto_start(self, checked):
        self.config["auto_start"] = checked
        save_config(self.config)
        try:
            import winreg
            import os

            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE
            )

            if checked:
                if getattr(sys, "frozen", False):
                    exe_path = sys.executable
                else:
                    python_exe = sys.executable.replace("python.exe", "pythonw.exe")
                    exe_path = f'"{python_exe}" "{os.path.abspath(sys.argv[0])}"'
                winreg.SetValueEx(key, "WordTranslator", 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(key, "WordTranslator")
                except FileNotFoundError:
                    pass

            winreg.CloseKey(key)
        except Exception as e:
            print(f"设置自启失败: {e}")

        self.tray_icon.showMessage(
            "划词翻译",
            f"开机自启动已{'开启' if checked else '关闭'}",
            QSystemTrayIcon.Information,
            2000
        )

    def _quit(self):
        self.hotkey.stop()
        self.tray_icon.hide()
        self.app.quit()

    def run(self):
        return self.app.exec_()


if __name__ == "__main__":
    app = WordTranslatorApp()
    sys.exit(app.run())
