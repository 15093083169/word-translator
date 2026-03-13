from __future__ import annotations

import os
import sys
from pathlib import Path


def _is_windows() -> bool:
    return sys.platform.startswith("win")


def get_executable_path() -> str:
    """
    返回当前程序的可执行路径：
    - 打包后：ClickTranslate.exe 的绝对路径
    - 直接运行 main.py：python 解释器 + main.py 组合
    为了简单，这里在 Windows 下仅用于注册 exe 形式。
    """
    if getattr(sys, "frozen", False):
        # PyInstaller 打包后的 exe
        return os.path.abspath(sys.executable)
    # 源码运行时不强制写入自启动，返回空字符串
    return ""


def is_autostart_enabled(app_name: str = "ClickTranslate") -> bool:
    if not _is_windows():
        return False
    try:
        import winreg
    except ImportError:
        return False

    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, app_name)
            return bool(value)
    except FileNotFoundError:
        return False
    except OSError:
        return False


def set_autostart(enabled: bool, app_name: str = "ClickTranslate") -> None:
    if not _is_windows():
        return
    try:
        import winreg
    except ImportError:
        return

    exe_path = get_executable_path()
    if not exe_path:
        # 源码运行时不写入自启动，避免错误路径
        return

    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE
        ) as key:
            if enabled:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
    except OSError:
        return

