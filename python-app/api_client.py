from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional

import requests

from config import AppConfig


API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"


@dataclass
class TranslateResult:
    translation: Optional[str] = None
    error: Optional[str] = None


def detect_is_chinese(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def translate_text(text: str, config: AppConfig) -> TranslateResult:
    if not config.api_key:
        return TranslateResult(error="请先设置 GLM API Key")

    is_chinese = detect_is_chinese(text)
    if is_chinese:
        prompt = f"请将以下文本翻译为英文：\n{text}"
    else:
        prompt = f"请将以下文本翻译为中文：\n{text}"

    payload = {
        "model": "glm-4-flash",
        "messages": [
            {"role": "system", "content": "你是一个专业翻译。只输出翻译结果，不要解释。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 1024,
    }

    try:
        resp = requests.post(
            API_URL,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config.api_key}",
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        choices = data.get("choices") or []
        if not choices:
            return TranslateResult(error=str(data.get("error", {}).get("message", "翻译失败")))
        content = (choices[0].get("message") or {}).get("content") or ""
        return TranslateResult(translation=content.strip())
    except requests.RequestException as e:
        return TranslateResult(error=f"网络错误: {e}")
    except Exception:
        return TranslateResult(error="解析响应失败")

