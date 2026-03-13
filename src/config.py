"""
划词翻译 - 配置管理
"""
import json
import os
import sys

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".word-translator")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "api_key": "",
    "api_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    "model": "glm-4-flash",
    "auto_start": False,
    "target_lang": "中文",
}


def get_config_dir():
    return CONFIG_DIR


def get_config_path():
    return CONFIG_FILE


def load_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            merged = DEFAULT_CONFIG.copy()
            merged.update(cfg)
            return merged
        except (json.JSONDecodeError, IOError):
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def is_first_run():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        return True
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        return not cfg.get("api_key", "").strip()
    except:
        return True
