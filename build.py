"""
PyInstaller 构建脚本
用法: python build.py
"""
import os
import sys
import subprocess
import shutil


def run(cmd):
    print(f"▶ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error:\n{result.stderr}")
        sys.exit(1)
    return result


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(root, "src")
    dist = os.path.join(root, "dist")
    build_dir = os.path.join(root, "build")

    # 先生成图标
    print("🎨 生成图标...")
    icon_script = os.path.join(root, "resources", "generate_icons.py")
    run([sys.executable, icon_script])

    # 安装依赖
    print("📦 安装依赖...")
    run([sys.executable, "-m", "pip", "install", "-r", os.path.join(root, "requirements.txt")])
    run([sys.executable, "-m", "pip", "install", "pyinstaller", "pillow"])

    # 检查图标文件
    icon_path = os.path.join(root, "resources", "icon.ico")
    if not os.path.exists(icon_path):
        # 如果没有 icon.ico，用 PyInstaller 默认图标
        icon_path = None
        print("⚠️  icon.ico not found, using default icon")

    # PyInstaller 参数
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "WordTranslator",
        "--windowed",  # 无控制台窗口
        "--onefile",   # 单文件
        "--clean",
        "--noconfirm",
    ]

    if icon_path:
        cmd.extend(["--icon", icon_path])

    # 添加数据文件（如果有）
    cmd.append(os.path.join(src, "main.py"))
    cmd.extend(["--hidden-import", "pynput.keyboard._win32"])
    cmd.extend(["--hidden-import", "pynput.mouse._win32"])

    print("🔨 构建可执行文件...")
    run(cmd)

    print(f"\n✅ 构建完成！")
    print(f"📁 输出文件: {os.path.join(dist, 'WordTranslator.exe')}")

    # 如果有 Inno Setup，提示可以生成安装包
    inno_script = os.path.join(root, "installer", "word-translator.iss")
    if os.path.exists(inno_script):
        print(f"\n💡 可以使用 Inno Setup 编译 {inno_script} 生成安装包")


if __name__ == '__main__':
    main()
