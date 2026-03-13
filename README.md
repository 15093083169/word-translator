# 划词翻译 (Word Translator)

> 🌍 选中文字，连按两次 **Ctrl**，即可翻译。基于智谱 AI GLM-4-Flash 模型。

## ✨ 功能特性

- **划词翻译** — 在任意应用中选中文字，连按两次 Ctrl 触发翻译
- **悬浮窗口** — 翻译结果以优雅的悬浮窗展示，不遮挡工作
- **一键复制** — 翻译完成后可一键复制结果
- **系统托盘** — 常驻右下角，右键菜单支持设置、开机自启、退出
- **浏览器扩展** — 支持 Chrome/Edge 等主流浏览器
- **多种语言** — 支持中、英、日、韩、法、德、俄等语言互译
- **完全免费** — 使用 GLM-4-Flash 免费模型

## 📸 效果预览

桌面端：选中文字 → 连按两次 Ctrl → 弹出翻译窗口 → 复制结果

## 🖥️ 桌面应用

### 安装

1. 下载最新的安装包：[Releases](../../releases)
2. 运行安装程序
3. 首次启动会提示输入 API Key

### 从源码运行

```bash
# 克隆仓库
git clone https://github.com/your-username/word-translator.git
cd word-translator

# 安装依赖
pip install -r requirements.txt

# 运行
python src/main.py
```

### 构建安装包

```bash
# 安装构建工具
pip install pyinstaller pillow

# 生成图标
python resources/generate_icons.py

# 构建 EXE
python build.py

# 使用 Inno Setup 生成安装包（可选）
# 用 Inno Setup Compiler 打开 installer/word-translator.iss
```

### 依赖

- Python 3.8+
- PyQt5
- pynput
- pyperclip
- requests

### 获取 API Key

1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册/登录账号
3. 创建 API Key
4. 在应用设置中填入

## 🌐 浏览器扩展

### 安装

1. 打开 Chrome/Edge 浏览器
2. 进入扩展管理页面 (`chrome://extensions/`)
3. 开启「开发者模式」
4. 点击「加载已解压的扩展程序」
5. 选择 `browser-extension` 文件夹

### 使用

- 选中网页中的文字
- 连按两次 **Ctrl**
- 或使用快捷键 **Ctrl+Shift+T**
- 翻译窗口会自动弹出

### 配置

- 点击扩展图标打开设置页面
- 输入 API Key
- 选择模型和目标语言

## ⌨️ 使用方法

| 操作 | 说明 |
|------|------|
| 选中文字 + 连按两次 Ctrl | 触发翻译 |
| 点击复制按钮 | 复制翻译结果 |
| 点击关闭按钮 / 点击其他区域 | 关闭翻译窗口 |
| 右键托盘图标 | 打开设置菜单 |
| 左键托盘图标 | 快速打开设置 |

## 🔧 配置项

| 配置 | 默认值 | 说明 |
|------|--------|------|
| API Key | 空 | 智谱 AI API Key（必填） |
| 模型 | glm-4-flash | 翻译使用的模型 |
| 目标语言 | 中文 | 翻译目标语言 |
| 开机自启 | 关闭 | 是否开机自动启动 |

## 🛠️ 技术栈

**桌面应用：**
- Python + PyQt5（GUI）
- pynput（全局热键）
- requests（API 调用）

**浏览器扩展：**
- Manifest V3
- Chrome Extension API
- 原生 JavaScript

**构建工具：**
- PyInstaller（EXE 打包）
- Inno Setup（Windows 安装包）

## 📁 项目结构

```
word-translator/
├── src/                        # 桌面应用源码
│   ├── main.py                 # 主入口
│   ├── config.py               # 配置管理
│   ├── translator.py           # GLM API 翻译引擎
│   ├── hotkey_manager.py       # 全局热键（双击 Ctrl）
│   ├── translate_window.py     # 翻译悬浮窗
│   └── settings_dialog.py      # 设置对话框
├── browser-extension/          # 浏览器扩展
│   ├── manifest.json
│   ├── content.js / content.css
│   ├── background.js
│   ├── popup.html / popup.js
│   └── icons/
├── installer/                  # Inno Setup 安装脚本
├── resources/                  # 图标资源
├── build.py                    # 构建脚本
├── requirements.txt
├── README.md
└── LICENSE
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
