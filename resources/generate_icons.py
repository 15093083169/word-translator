"""
生成浏览器扩展和应用程序图标
"""
import os
import sys

# 修复 Windows 控制台编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from PIL import Image, ImageDraw, ImageFont


def create_icon(size, output_path):
    """生成蓝色圆形 T 字母图标"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 蓝色圆形背景
    padding = max(1, int(size * 0.03))
    draw.ellipse(
        [padding, padding, size - padding, size - padding],
        fill=(52, 152, 219, 255)
    )

    # 白色 T 字母
    font_size = int(size * 0.55)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()

    text = "T"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (size - tw) // 2
    y = (size - th) // 2 - int(size * 0.03)

    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

    img.save(output_path)
    print(f"✅ Created: {output_path} ({size}x{size})")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 浏览器扩展图标
    ext_icons = os.path.join(script_dir, "..", "browser-extension", "icons")
    for size in [16, 48, 128]:
        create_icon(size, os.path.join(ext_icons, f"icon{size}.png"))

    # 应用程序图标 (.ico)
    app_icon = os.path.join(script_dir, "..", "resources", "icon.ico")
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    imgs = []
    for s in sizes:
        img = Image.new('RGBA', s, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        padding = max(1, int(s[0] * 0.03))
        draw.ellipse([padding, padding, s[0] - padding, s[1] - padding], fill=(52, 152, 219, 255))
        font_size = int(s[0] * 0.55)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                font = ImageFont.load_default()
        text = "T"
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (s[0] - tw) // 2
        y = (s[1] - th) // 2 - int(s[0] * 0.03)
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        imgs.append(img)

    # 保存为 ICO
    largest = imgs[-1].resize((256, 256), Image.LANCZOS)
    largest.save(app_icon, format='ICO', sizes=[s for s in sizes], append_images=imgs[:-1])
    print(f"✅ Created: {app_icon}")

    # SVG 版本（用于 GitHub）
    svg_path = os.path.join(script_dir, "..", "resources", "icon.svg")
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="128" height="128">
  <circle cx="64" cy="64" r="60" fill="#3498db"/>
  <text x="64" y="85" text-anchor="middle" font-family="Arial, sans-serif" font-size="72" font-weight="bold" fill="white">T</text>
</svg>'''
    with open(svg_path, 'w') as f:
        f.write(svg_content)
    print(f"✅ Created: {svg_path}")


if __name__ == '__main__':
    main()
