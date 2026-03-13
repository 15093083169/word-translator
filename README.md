# Click Translate - 划词翻译

> 选中文字，连按两次 **Ctrl**，即可翻译。基于智谱 AI GLM-4-Flash 模型，免费使用。

## ✨ 功能

- **划词翻译** — 任意应用中选中文字，连按两次 Ctrl 触发翻译
- **深色气泡窗口** — 翻译结果以暗色悬浮气泡展示，跟随光标位置
- **一键复制** — 翻译完成后点击 📋 按钮复制结果
- **系统托盘常驻** — 右下角托盘图标，右键菜单：配置 / 开机自启 / 退出
- **浏览器扩展** — 支持 Chrome/Edge，双击 Ctrl 或右键菜单翻译
- **中英自动识别** — 自动检测中文/英文，翻译为对应语言
- **完全免费** — 使用 GLM-4-Flash 免费模型

## 🖥️ 桌面应用

### 快速开始

```bash
cd python-app
pip install -r requirements.txt
python main.py
```

首次启动会弹出设置窗口，输入智谱 AI API Key 即可。

### 获取 API Key

1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册/登录
3. 在控制台创建 API Key
4. 粘贴到应用设置中

### 打包 EXE

```bash
pip install pyinstaller
pyinstaller ClickTranslate.spec
```

产物在 `dist/ClickTranslate.exe`。

### 使用方法

| 操作 | 说明 |
|------|------|
| 选中文字 + 连按两次 Ctrl | 触发翻译 |
| Ctrl+Alt+K | 打开设置窗口 |
| 右键托盘图标 | 配置 / 开机自启 / 退出 |
| 点击 📋 按钮 | 复制翻译结果 |

## 🌐 浏览器扩展

### 安装（开发者模式）

1. 打开 `chrome://extensions/`
2. 开启「开发者模式」
3. 点击「加载已解压的扩展程序」
4. 选择 `browser-extension` 文件夹

### 使用

- 选中网页文字，**连按两次 Ctrl**
- 或使用快捷键 **Alt+Shift+T**
- 或**右键 → Click Translate：翻译选中文本**
- 点击扩展图标可配置 API Key

## 📁 项目结构

```
word-translator/
├── python-app/                # 桌面应用 (PySide6 + keyboard)
│   ├── main.py                # 入口：托盘、热键、翻译触发
│   ├── ui.py                  # 深色气泡翻译窗口
│   ├── api_client.py          # GLM-4-Flash API 调用
│   ├── config.py              # 配置管理
│   ├── settings_dialog.py     # API Key 设置对话框
│   ├── hotkey_listener.py     # 双击 Ctrl 监听
│   ├── autostart.py           # Windows 开机自启
│   ├── ClickTranslate.spec    # PyInstaller 打包配置
│   └── requirements.txt
├── browser-extension/         # 浏览器扩展 (Manifest V3)
│   ├── manifest.json
│   ├── background.js          # API 调用 + 快捷键 + 右键菜单
│   ├── contentScript.js       # 页面注入：双击 Ctrl + 气泡 UI
│   ├── content.css            # 气泡样式
│   ├── popup.html / popup.js  # 扩展弹窗设置
│   └── options.html           # 选项页
├── README.md
└── LICENSE
```

## 🛠️ 技术栈

- **桌面端**: Python + PySide6 + keyboard + requests
- **浏览器**: Manifest V3 + Chrome Extension API
- **构建**: PyInstaller

## 📄 许可证

MIT License
