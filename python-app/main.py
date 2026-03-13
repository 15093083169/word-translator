from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Optional

import keyboard
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox, QMenu, QSystemTrayIcon, QStyle

from config import AppConfig
from hotkey_listener import HotkeyListener
from ui import BubbleWindow
from settings_dialog import show_settings_dialog
from autostart import is_autostart_enabled, set_autostart


def get_selected_text() -> Optional[str]:
    """
    只需“选中 + 双击 Ctrl”：
    这里自动发送一次 Ctrl+C，然后从剪贴板读取文本。
    """
    # 模拟 Ctrl+C，将当前选中内容复制到剪贴板
    keyboard.send("ctrl+c")
    # 等待目标程序完成复制
    time.sleep(0.12)

    clipboard = QApplication.clipboard()
    text = clipboard.text()
    if text:
        text = text.strip()
    return text or None


def load_app_icon(app: QApplication) -> QIcon:
    """
    加载应用图标：
    - 开发环境：使用与 main.py 同目录下的 icon_t.ico
    - 打包后：使用 PyInstaller 解包目录中的 icon_t.ico（需通过 --add-data 打入）
    - 如果不存在，则回退到 Qt 标准图标
    """
    if getattr(sys, "frozen", False):
        # PyInstaller 打包后的 exe，资源文件位于 _MEIPASS 目录
        base_dir = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        icon_path = base_dir / "icon_t.ico"
    else:
        icon_path = Path(__file__).with_name("icon_t.ico")

    if icon_path.exists():
        return QIcon(str(icon_path))
    return app.style().standardIcon(QStyle.SP_DesktopIcon)


def main() -> None:
    app = QApplication(sys.argv)
    # 关闭所有窗口时不退出进程，保持托盘常驻
    app.setQuitOnLastWindowClosed(False)

    config = AppConfig.load()

    app_icon = load_app_icon(app)
    app.setWindowIcon(app_icon)

    # 首次使用时，弹出设置对话框让用户填写 API Key
    if not config.api_key:
        ok = show_settings_dialog(config)
        if not ok or not config.api_key:
            QMessageBox.warning(
                None,
                "Click Translate",
                "未配置 GLM API Key，程序将退出。",
            )
            return

    bubble = BubbleWindow(config)

    def on_double_ctrl() -> None:
        text = get_selected_text()
        if not text:
            # 无选中文本，直接忽略
            return
        bubble.translate(text)

    def on_open_settings() -> None:
        # 重新打开设置窗口，允许查看 / 修改当前 Key
        ok = show_settings_dialog(config, parent=bubble)
        if ok:
            QMessageBox.information(
                bubble,
                "Click Translate",
                "API Key 已更新。",
            )

    # 双击 Ctrl 触发翻译
    listener = HotkeyListener(on_double_ctrl=on_double_ctrl)
    listener.start()

    # Ctrl+Alt+K 打开设置窗口
    keyboard.add_hotkey("ctrl+alt+k", on_open_settings)

    # 创建系统托盘图标和菜单
    tray_icon = QSystemTrayIcon()
    # 使用统一的应用图标
    tray_icon.setIcon(app_icon)
    tray_icon.setToolTip("Click Translate - 双击 Ctrl 划词翻译")

    tray_menu = QMenu()

    action_settings = tray_menu.addAction("配置 API Key...")
    action_settings.triggered.connect(on_open_settings)

    tray_menu.addSeparator()

    autostart_action = tray_menu.addAction("开机启动")
    autostart_action.setCheckable(True)
    autostart_action.setChecked(is_autostart_enabled())

    def on_toggle_autostart(checked: bool) -> None:
        set_autostart(checked)

    autostart_action.toggled.connect(on_toggle_autostart)

    tray_menu.addSeparator()

    def on_quit() -> None:
        listener.stop()
        tray_icon.hide()
        app.quit()

    action_quit = tray_menu.addAction("退出")
    action_quit.triggered.connect(on_quit)

    tray_icon.setContextMenu(tray_menu)
    tray_icon.show()

    try:
        sys.exit(app.exec())
    finally:
        listener.stop()


if __name__ == "__main__":
    main()


