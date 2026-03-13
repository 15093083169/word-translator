"""
划词翻译 - GLM API 翻译引擎
"""
import requests
import json


class Translator:
    def __init__(self, config):
        self.config = config

    def translate(self, text):
        api_key = self.config.get("api_key", "").strip()
        if not api_key:
            raise ValueError("请先配置 API Key（右键托盘图标 → 设置）")

        api_url = self.config.get("api_url", "https://open.bigmodel.cn/api/paas/v4/chat/completions")
        model = self.config.get("model", "glm-4-flash")
        target_lang = self.config.get("target_lang", "中文")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": f"你是一个翻译专家。将用户输入的文本翻译为{target_lang}。只输出翻译结果，不要添加任何解释、注释或额外格式。",
                },
                {
                    "role": "user",
                    "content": text,
                },
            ],
            "temperature": 0.1,
            "max_tokens": 1024,
        }

        try:
            resp = requests.post(api_url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except requests.exceptions.Timeout:
            raise Exception("请求超时，请检查网络连接")
        except requests.exceptions.ConnectionError:
            raise Exception("网络连接失败，请检查网络")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("API Key 无效，请检查配置")
            elif e.response.status_code == 429:
                raise Exception("请求过于频繁，请稍后再试")
            else:
                try:
                    err_data = e.response.json()
                    msg = err_data.get("error", {}).get("message", str(e))
                    raise Exception(f"API 错误: {msg}")
                except:
                    raise Exception(f"API 错误: {e}")
        except (KeyError, IndexError, json.JSONDecodeError):
            raise Exception("API 返回数据格式异常")
        except Exception as e:
            raise Exception(f"翻译失败: {str(e)}")
