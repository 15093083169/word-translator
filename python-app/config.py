import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path


APP_NAME = "click_translate"


def _get_config_dir() -> Path:
    """
    返回跨平台的配置目录：
    - Windows: %APPDATA%/click_translate
    - macOS: ~/Library/Application Support/click_translate
    - Linux: ~/.config/click_translate
    """
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
        return Path(base) / APP_NAME
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_NAME
    else:
        return Path.home() / ".config" / APP_NAME


CONFIG_DIR = _get_config_dir()
CONFIG_PATH = CONFIG_DIR / "config.json"


@dataclass
class AppConfig:
    api_key: str = ""

    @classmethod
    def load(cls) -> "AppConfig":
        try:
            if CONFIG_PATH.exists():
                data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
                return cls(api_key=data.get("api_key", ""))
        except Exception:
            pass
        return cls()

    def save(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = {"api_key": self.api_key}
        CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

