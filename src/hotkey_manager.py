"""
划词翻译 - 全局热键管理（双击 Ctrl）
"""
import time
import threading
import ctypes
import pyperclip


class HotkeyManager:
    """监听全局双击 Ctrl 热键，触发时获取选中文本"""

    def __init__(self, callback):
        """
        callback: 被调用时接收一个参数 (selected_text: str)
        """
        self.callback = callback
        self.interval = 0.4  # 双击间隔（秒）
        self.last_ctrl_time = 0
        self._running = True
        self._thread = None

    def start(self):
        """启动热键监听线程"""
        from pynput import keyboard

        def on_press(key):
            if not self._running:
                return False

            try:
                is_ctrl = key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l,
                                  keyboard.Key.ctrl_r)
            except AttributeError:
                is_ctrl = False

            if is_ctrl:
                now = time.time()
                if 0 < now - self.last_ctrl_time < self.interval:
                    self.last_ctrl_time = 0
                    # 在新线程中执行，避免阻塞监听器
                    threading.Thread(target=self._trigger, daemon=True).start()
                else:
                    self.last_ctrl_time = now

        self._listener = keyboard.Listener(on_press=on_press)
        self._listener.start()

    def _trigger(self):
        """热键触发：等待按键释放 → 模拟 Ctrl+C → 读取剪贴板"""
        time.sleep(0.15)  # 等待用户松开 Ctrl
        text = self._get_selected_text()
        if text.strip():
            self.callback(text)

    def _get_selected_text(self):
        """通过模拟 Ctrl+C 获取当前选中的文本"""
        # 保存当前剪贴板
        old_clipboard = pyperclip.paste()

        # 模拟 Ctrl+C
        VK_CONTROL = 0x11
        VK_C = 0x43
        KEYEVENTF_KEYUP = 0x0002

        ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0)
        ctypes.windll.user32.keybd_event(VK_C, 0, 0, 0)
        time.sleep(0.05)
        ctypes.windll.user32.keybd_event(VK_C, 0, KEYEVENTF_KEYUP, 0)
        ctypes.windll.user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

        time.sleep(0.15)
        text = pyperclip.paste()

        # 恢复剪贴板
        try:
            pyperclip.copy(old_clipboard)
        except:
            pass

        if text and text != old_clipboard:
            return text
        return ""

    def stop(self):
        """停止热键监听"""
        self._running = False
        if hasattr(self, "_listener") and self._listener:
            self._listener.stop()
