# 测试正方形裁剪功能

import os
import sys
sys.path.append('.')
from Weibo import *

def test_square_crop():
    """测试正方形裁剪功能"""
    
    # 创建一个WeiboImageGenerator实例
    generator = WeiboImageGenerator()
    
    print("✂️ 正方形裁剪测试")
    print("="*40)
    
    # 测试不同比例的图片裁剪
    test_cases = [
        {"name": "正方形", "size": (500, 500), "color": "#FF6B6B"},
        {"name": "横向长条", "size": (800, 200), "color": "#4ECDC4"},
        {"name": "纵向长条", "size": (200, 800), "color": "#45B7D1"},
        {"name": "超宽图", "size": (1200, 300), "color": "#FFA07A"},
        {"name": "超高图", "size": (300, 1200), "color": "#98D8C8"},
    ]
    
    target_size = (200, 200)
    
    for case in test_cases:
        # 创建测试图片
        img = Image.new("RGB", case["size"], case["color"])
        draw = ImageDraw.Draw(img)
        
        # 在图片上画一个标记，用于验证裁剪位置
        draw.rectangle([10, 10, case["size"][0]-10, case["size"][1]-10], outline="white", width=5)
        draw.text((case["size"][0]//2-20, case["size"][1]//2-10), f"{case['name']}", 
                 fill="white", font=generator.content_font, anchor="mm")
        
        # 执行裁剪
        cropped = generator.crop_to_square(img, target_size)
        
        print(f"{case['name']:8} | 原始: {case['size'][0]:4}x{case['size'][1]:4} | "
              f"裁剪后: {cropped.size[0]:3}x{cropped.size[1]:3} | "
              f"正方形: {cropped.size[0] == cropped.size[1] == target_size[0]}")
        
        # 保存测试结果
        cropped.save(f"outputs/test_crop_{case['name']}.jpg")

if __name__ == "__main__":
    test_square_crop()
    print("\n✅ 测试完成！检查 outputs 目录中的测试图片")
