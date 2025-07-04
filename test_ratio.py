# 测试不同比例图片的处理效果

import os
import sys
sys.path.append('.')
from Weibo import *

def test_image_ratios():
    """测试不同比例图片的处理效果"""
    
    # 创建一个WeiboImageGenerator实例
    generator = WeiboImageGenerator()
    
    print("📊 图片比例测试")
    print("="*40)
    
    # 测试resize_keep_ratio函数
    test_cases = [
        {"name": "正方形", "size": (500, 500), "max_size": (220, 220)},
        {"name": "横向长条", "size": (800, 200), "max_size": (220, 220)},
        {"name": "纵向长条", "size": (200, 800), "max_size": (220, 220)},
        {"name": "超宽图", "size": (1200, 300), "max_size": (220, 220)},
        {"name": "超高图", "size": (300, 1200), "max_size": (220, 220)},
    ]
    
    for case in test_cases:
        # 创建测试图片
        img = Image.new("RGB", case["size"], "#FF6B6B")
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), f"{case['name']}\n{case['size'][0]}x{case['size'][1]}", 
                 fill="white", font=generator.content_font)
        
        # 调整大小
        resized = generator.resize_keep_ratio(img, case["max_size"])
        
        print(f"{case['name']:8} | 原始: {case['size'][0]:4}x{case['size'][1]:4} | "
              f"调整后: {resized.size[0]:3}x{resized.size[1]:3} | "
              f"比例保持: {abs(case['size'][0]/case['size'][1] - resized.size[0]/resized.size[1]) < 0.01}")

if __name__ == "__main__":
    test_image_ratios()
