from __future__ import annotations

import threading
import time
from typing import Callable, Optional

try:
    import keyboard  # type: ignore
except ImportError:
    keyboard = None  # type: ignore


class HotkeyListener(threading.Thread):
    """
    监听“快速双击 Ctrl”的线程。
    在大多数 Windows 环境下可用；如果 keyboard 未安装或在当前平台不可用，则不会启用。
    """

    def __init__(self, on_double_ctrl: Callable[[], None], interval_ms: int = 400) -> None:
        super().__init__(daemon=True)
        self.on_double_ctrl = on_double_ctrl
        self.interval_ms = interval_ms
        self._last_time: Optional[float] = None
        self._running = True

    def stop(self) -> None:
        self._running = False
        if keyboard is not None:
            try:
                keyboard.unhook_all()
            except Exception:
                pass

    def run(self) -> None:
        if keyboard is None:
            return

        def _on_ctrl_event(event) -> None:
            if not self._running:
                return
            if event.event_type != "down":
                return
            if "ctrl" not in event.name.lower():
                return

            now = time.time() * 1000
            if self._last_time is not None and (now - self._last_time) < self.interval_ms:
                # 认为是双击 Ctrl
                self._last_time = None
                try:
                    self.on_double_ctrl()
                except Exception:
                    pass
            else:
                self._last_time = now

        keyboard.hook(_on_ctrl_event)

        # 阻塞线程，直到 stop 被调用
        while self._running:
            time.sleep(0.1)

