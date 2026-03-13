# Click Translate (Python 版本)

使用 Python + PySide6 实现的划词翻译小工具：

- Windows：选中一段文本，在 400ms 内 **连续按两次 Ctrl**（双击 Ctrl），程序会自动复制并翻译
- 翻译气泡会出现在鼠标附近，调用 **GLM-4-Flash** 完成中英互译，并提供一键复制按钮

> 当前版本重点支持 Windows；在 macOS / Linux 上可以运行界面和翻译，但全局热键行为可能受到系统权限和版本限制。

## 环境准备

```bash
cd word-translator/python-app
python -m venv .venv            # Windows
.venv\Scripts\activate
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

首次运行如果没有配置 GLM API Key，会有提示信息。

配置文件路径为：

- Windows: `%APPDATA%/click_translate/config.json`
- macOS: `~/Library/Application Support/click_translate/config.json`
- Linux: `~/.config/click_translate/config.json`

示例内容：

```json
{
  "api_key": "your_glm_api_key_here"
}
```

## 打包思路（示例）

可以使用 `PyInstaller` 打包为独立可执行文件：

```bash
pip install pyinstaller pillow

# Windows 示例（带图标）
pyinstaller --name ClickTranslate --noconsole --onefile ^
  --icon icon_t.ico ^
  --add-data "icon_t.ico;." ^
  main.py
```

- **Windows 安装包**：在此基础上可以使用 NSIS / Inno Setup 等生成安装程序。

后续也可以在 GitHub Actions 中配置 CI，自动构建各平台包并上传 Release。

