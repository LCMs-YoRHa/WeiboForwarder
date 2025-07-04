# -*- coding: utf-8 -*-
"""
字体管理模块 - 优先使用项目内置字体
"""

import os
from pathlib import Path

FONTS_DIR = Path(__file__).parent / "fonts"
FONTS_DIR.mkdir(exist_ok=True)

def get_font_path():
    """获取可用的中文字体路径"""
    
    # 首先扫描项目 fonts 目录中的所有字体文件
    if FONTS_DIR.exists():
        for font_file in FONTS_DIR.glob("*"):
            if font_file.suffix.lower() in ['.ttf', '.otf', '.ttc'] and font_file.is_file():
                print(f"✅ 使用项目内置字体: {font_file.name}")
                return str(font_file)
    
    # 如果没有项目内置字体，则检查预定义的字体
    predefined_fonts = [
        FONTS_DIR / "SourceHanSansCN-Regular.ttf",
        FONTS_DIR / "SourceHanSansCN-Regular.otf", 
        FONTS_DIR / "NotoSansCJKsc-Regular.ttf",
        FONTS_DIR / "NotoSansCJKsc-Regular.otf",
        FONTS_DIR / "SourceHanSerifCN-Regular.ttf",
        FONTS_DIR / "SourceHanSerifCN-Regular.otf",
        FONTS_DIR / "msyh.ttc",
        FONTS_DIR / "simhei.ttf",
        FONTS_DIR / "simsun.ttc",
    ]
    
    # 检查预定义的项目内置字体
    for font_path in predefined_fonts:
        if font_path.exists():
            print(f"✅ 使用项目内置字体: {font_path.name}")
            return str(font_path)
    
    # 如果没有项目内置字体，则使用系统字体
    system_fonts = [
        # Docker容器中的系统字体
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJKsc-Regular.otf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        
        # Linux 系统字体
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/arphic/uming.ttc",
        
        # Windows 系统字体（本地开发）
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
    ]
    
    # 查找系统字体
    for font_path in system_fonts:
        if Path(font_path).exists():
            print(f"✅ 使用系统字体: {font_path}")
            return str(font_path)
    
    print("⚠️ 未找到合适的中文字体，将使用系统默认字体")
    return None

def ensure_fonts():
    """确保字体可用"""
    return get_font_path()

def list_available_fonts():
    """列出可用的字体"""
    print("📝 扫描可用字体...")
    
    # 项目内置字体
    project_fonts = []
    if FONTS_DIR.exists():
        for font_file in FONTS_DIR.glob("*"):
            if font_file.suffix.lower() in ['.ttf', '.otf', '.ttc']:
                project_fonts.append(font_file)
    
    if project_fonts:
        print(f"📁 项目内置字体 ({len(project_fonts)} 个):")
        for font in project_fonts:
            print(f"  - {font.name}")
    else:
        print("📁 项目内置字体: 无")
    
    # 当前使用的字体
    current_font = get_font_path()
    if current_font:
        print(f"🎯 当前使用字体: {Path(current_font).name}")
    else:
        print("🎯 当前使用字体: 系统默认")

if __name__ == "__main__":
    # 测试字体获取
    list_available_fonts()
    print()
    font_path = ensure_fonts()
    if font_path:
        print(f"🎉 字体就绪: {font_path}")
    else:
        print("❌ 字体初始化失败")
