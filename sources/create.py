# -*- coding: utf-8 -*-
"""
微博长图生成模块
负责RSS解析和长图生成功能
"""

import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import xml.etree.ElementTree as ET
import re
import math
import os
from datetime import datetime, timedelta
from html import unescape
from font_manager import ensure_fonts


# 配置
FONT_PATH = ensure_fonts()  # 使用字体管理器获取字体路径
OUTPUT_DIR = "outputs"


class RSSWeiboParser:
    """RSS微博数据解析器"""
    
    @staticmethod
    def fetch_rss_data(rss_url):
        """获取RSS数据"""
        try:
            print(f"🔍 获取RSS数据: {rss_url}")
            response = requests.get(rss_url, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"❌ 获取RSS数据失败: {e}")
            return None
    
    @staticmethod
    def parse_rss_xml(xml_content):
        """解析RSS XML"""
        try:
            root = ET.fromstring(xml_content)
            channel = root.find('channel')
            
            # 获取频道信息
            channel_info = {
                'title': channel.find('title').text if channel.find('title') is not None else '',
                'description': channel.find('description').text if channel.find('description') is not None else '',
                'link': channel.find('link').text if channel.find('link') is not None else '',
                'image_url': ''
            }
            
            # 获取头像URL
            image_elem = channel.find('image')
            if image_elem is not None:
                url_elem = image_elem.find('url')
                if url_elem is not None:
                    channel_info['image_url'] = url_elem.text
            
            # 解析微博条目
            items = []
            for item in channel.findall('item'):
                weibo_item = RSSWeiboParser.parse_weibo_item(item)
                if weibo_item:
                    items.append(weibo_item)
            
            return channel_info, items
            
        except Exception as e:
            print(f"❌ 解析RSS XML失败: {e}")
            return None, []
    
    @staticmethod
    def parse_weibo_item(item):
        """解析单条微博"""
        try:
            title = item.find('title').text if item.find('title') is not None else ''
            description = item.find('description').text if item.find('description') is not None else ''
            link = item.find('link').text if item.find('link') is not None else ''
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
            author = item.find('author').text if item.find('author') is not None else ''
            
            # 提取微博ID
            weibo_id = ''
            if link:
                match = re.search(r'/(\w+)$', link)
                if match:
                    weibo_id = match.group(1)
            
            # 清理和解析内容
            clean_title = RSSWeiboParser.clean_text(title)
            clean_description = RSSWeiboParser.clean_html(description)
            
            # 提取图片URLs
            image_urls = RSSWeiboParser.extract_image_urls(description)
            
            # 提取视频信息
            video_info = RSSWeiboParser.extract_video_info(description)
            
            return {
                'id': weibo_id,
                'title': clean_title,
                'content': clean_description,
                'link': link,
                'pub_date': pub_date,
                'author': author,
                'image_urls': image_urls,
                'video_info': video_info,
                'raw_description': description
            }
            
        except Exception as e:
            print(f"⚠️ 解析微博条目失败: {e}")
            return None
    
    @staticmethod
    def clean_text(text):
        """清理文本"""
        if not text:
            return ''
        
        # 移除多余的[图片]标记
        text = re.sub(r'\[图片\]', '', text)
        # 解码HTML实体
        text = unescape(text)
        return text.strip()
    
    @staticmethod
    def clean_html(html_content):
        """清理HTML内容，提取纯文本并保留正确的换行"""
        if not html_content:
            return ''
        
        # 先替换<br>为换行（在删除其他标签之前）
        html_content = re.sub(r'<br\s*/?>', '\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<br>', '\n', html_content, flags=re.IGNORECASE)
        
        # 移除视频标签
        html_content = re.sub(r'<video.*?</video>', '', html_content, flags=re.DOTALL)
        
        # 移除图片标签
        html_content = re.sub(r'<img[^>]*>', '', html_content)
        
        # 移除其他HTML标签，但保留链接文本
        html_content = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', html_content)
        html_content = re.sub(r'<[^>]+>', '', html_content)
        
        # 处理段落标签为双换行
        html_content = re.sub(r'</p>\s*<p[^>]*>', '\n\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'</?p[^>]*>', '\n', html_content, flags=re.IGNORECASE)
        
        # 处理div标签为换行
        html_content = re.sub(r'</div>\s*<div[^>]*>', '\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'</?div[^>]*>', '\n', html_content, flags=re.IGNORECASE)
        
        # 解码HTML实体
        html_content = unescape(html_content)
        
        # 清理多余空行（保留单个换行）
        html_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', html_content)
        html_content = re.sub(r'^\s+|\s+$', '', html_content)  # 去除首尾空白
        
        return html_content
    
    @staticmethod
    def extract_image_urls(html_content):
        """从HTML中提取图片URLs"""
        if not html_content:
            return []
        
        # 查找所有img标签的src属性
        image_pattern = r'<img[^>]*src="([^"]*)"[^>]*>'
        matches = re.findall(image_pattern, html_content)
        
        # 过滤出有效的图片URL
        valid_urls = []
        for url in matches:
            # 跳过小图标和系统图标
            skip_keywords = ['icon', 'emoji', 'timeline_card', 'small_video_default', '1rem', 'avatar']
            should_skip = any(keyword in url.lower() for keyword in skip_keywords)
            
            # 检查img标签的style属性是否包含小尺寸
            img_match = re.search(rf'<img[^>]*src="{re.escape(url)}"[^>]*>', html_content)
            if img_match:
                img_tag = img_match.group(0)
                if 'width: 1rem' in img_tag or 'height: 1rem' in img_tag:
                    should_skip = True
            
            if not should_skip and url.startswith('http'):
                valid_urls.append(url)
        
        return valid_urls
    
    @staticmethod
    def extract_video_info(html_content):
        """提取视频信息"""
        if not html_content:
            return None
        
        video_info = {}
        
        # 提取视频封面
        poster_match = re.search(r'poster="([^"]*)"', html_content)
        if poster_match:
            video_info['poster'] = poster_match.group(1)
        
        # 提取视频链接
        video_match = re.search(r'<source src="([^"]*)"[^>]*>', html_content)
        if video_match:
            video_info['video_url'] = video_match.group(1)
        
        return video_info if video_info else None


class WeiboImageGenerator:
    """微博长图生成器"""
    
    def __init__(self):
        self.setup_fonts()
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    def setup_fonts(self):
        """设置字体（超高清版）"""
        try:
            if FONT_PATH:
                self.name_font = ImageFont.truetype(FONT_PATH, 70)  # 用户名字体更大
                self.time_font = ImageFont.truetype(FONT_PATH, 50)  # 时间字体更大
                self.content_font = ImageFont.truetype(FONT_PATH, 64)  # 正文字体更大
                print("✅ 超高清字体加载成功")
            else:
                raise Exception("字体路径为空")
        except Exception as e:
            print(f"⚠️ 字体加载失败，使用默认字体: {e}")
            self.name_font = ImageFont.load_default()
            self.time_font = ImageFont.load_default()
            self.content_font = ImageFont.load_default()
    
    def download_image(self, url, square_size=None, force_size=None):
        """下载图片，智能获取最佳分辨率版本"""
        if not url:
            return self.create_placeholder_image(force_size or square_size or (640, 640))
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://weibo.com/'
        }
        
        # 尝试多个URL策略
        urls_to_try = []
        
        # 1. 高分辨率URL
        high_res_url = self.get_high_resolution_url(url)
        if high_res_url != url:
            urls_to_try.append(('高分辨率', high_res_url))
        
        # 2. 原始URL  
        urls_to_try.append(('原始', url))
        
        # 3. 如果是crop URL，尝试直接去掉crop参数
        if '/crop.' in url:
            try:
                # 简单去掉crop参数的方法
                base_url = url.split('/crop.')[0]
                filename = url.split('/')[-1]
                simple_url = f"{base_url}/{filename}"
                urls_to_try.append(('去crop', simple_url))
            except:
                pass
        
        # 依次尝试不同的URL
        for desc, test_url in urls_to_try:
            try:
                response = requests.get(test_url, headers=headers, timeout=15)
                response.raise_for_status()
                
                img = Image.open(BytesIO(response.content)).convert("RGB")
                print(f"📷 {desc}图片获取成功: {img.size[0]}x{img.size[1]}px")
                
                # 处理图片尺寸
                if force_size:
                    img = img.resize(force_size, Image.Resampling.LANCZOS)
                elif square_size:
                    img = self.crop_to_square(img, square_size)
                
                return img
                
            except requests.exceptions.RequestException as e:
                if "404" in str(e):
                    print(f"⚠️ {desc}图片不存在 (404): {test_url[:80]}...")
                else:
                    print(f"⚠️ {desc}图片下载失败: {str(e)[:100]}...")
                continue
            except Exception as e:
                print(f"⚠️ {desc}图片处理失败: {str(e)[:100]}...")
                continue
        
        # 所有URL都失败，创建占位图片
        print(f"❌ 所有图片URL都无法访问，使用占位图片")
        return self.create_placeholder_image(force_size or square_size or (640, 640))
    
    def create_placeholder_image(self, size):
        """创建占位图片"""
        if isinstance(size, tuple):
            width, height = size
        else:
            width = height = size
            
        placeholder = Image.new("RGB", (width, height), "#F0F0F0")
        draw = ImageDraw.Draw(placeholder)
        
        # 绘制一个简单的图标
        center_x, center_y = width // 2, height // 2
        icon_size = min(width, height) // 4
        
        # 绘制相机图标
        draw.rectangle([
            center_x - icon_size, center_y - icon_size//2,
            center_x + icon_size, center_y + icon_size//2
        ], fill="#CCCCCC", outline="#999999")
        
        draw.ellipse([
            center_x - icon_size//2, center_y - icon_size//2,
            center_x + icon_size//2, center_y + icon_size//2
        ], fill="#999999", outline="#666666")
        
        # 添加文字
        try:
            font_size = max(12, min(width, height) // 20)
            if hasattr(self, 'content_font'):
                font = ImageFont.truetype(self.content_font.path, font_size)
            else:
                font = ImageFont.load_default()
            draw.text((center_x, center_y + icon_size), "图片加载失败", 
                     fill="#666666", font=font, anchor="mt")
        except:
            pass
            
        return placeholder

    def get_high_resolution_url(self, url):
        """尝试获取高分辨率图片URL - 改进版"""
        if not url:
            return url
            
        # 微博图片URL规律分析和处理
        if 'sinaimg.cn' in url:
            # 对于包含crop参数的URL（如头像），直接移除crop参数
            if '/crop.' in url:
                # 移除crop参数，获取原始图片
                # 例：https://tvax2.sinaimg.cn/crop.0.0.310.310.180/735bcd72ly8ft3nr06beej208m08m749.jpg
                # 转为：https://tvax2.sinaimg.cn/735bcd72ly8ft3nr06beej208m08m749.jpg
                parts = url.split('/crop.')
                if len(parts) >= 2:
                    # 找到文件名部分
                    after_crop = parts[1]
                    filename_start = after_crop.find('/')
                    if filename_start != -1:
                        filename = after_crop[filename_start + 1:]
                        base_url = parts[0]
                        # 尝试large尺寸
                        high_res_url = f"{base_url}/large/{filename}"
                        return high_res_url
            
            # 对于已经包含orj360的URL，避免重复添加
            if '/orj360/orj360/' in url:
                # 移除重复的orj360
                url = url.replace('/orj360/orj360/', '/orj360/')
                return url
            
            # 对于普通的微博图片URL进行尺寸升级
            size_mappings = [
                ('/thumbnail/', '/large/'),
                ('/bmiddle/', '/large/'),
                ('/small/', '/large/'),
                ('/square/', '/large/'),
                ('/orj480/', '/large/'),  # 避免使用可能不存在的orj360
            ]
            
            for old_size, new_size in size_mappings:
                if old_size in url:
                    return url.replace(old_size, new_size)
            
            # 如果没有找到已知的尺寸标识，尝试添加large
            if '/large/' not in url and '/orj360/' not in url:
                # 检查URL结构，在域名后添加large
                import re
                match = re.match(r'(https?://[^/]+/)(.+)', url)
                if match:
                    domain_part, path_part = match.groups()
                    # 如果路径不是以尺寸标识开始，添加large
                    if not re.match(r'^(large|orj360|thumbnail|bmiddle|small|square)/', path_part):
                        return f"{domain_part}large/{path_part}"
        
        # 对于其他图片源，返回原URL
        return url
    
    def resize_keep_ratio(self, img, max_size):
        """保持比例调整图片大小"""
        original_width, original_height = img.size
        max_width, max_height = max_size
        
        # 计算缩放比例
        width_ratio = max_width / original_width
        height_ratio = max_height / original_height
        ratio = min(width_ratio, height_ratio)
        
        # 计算新尺寸
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def add_video_play_icon(self, img):
        """在图片上添加视频播放图标"""
        width, height = img.size
        
        # 创建带透明度的播放图标
        icon_size = min(width, height) // 4
        icon_x = (width - icon_size) // 2
        icon_y = (height - icon_size) // 2
        
        # 创建一个新的图层用于绘制图标
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # 绘制半透明圆形背景
        circle_radius = icon_size // 2
        circle_center = (icon_x + circle_radius, icon_y + circle_radius)
        draw.ellipse([
            circle_center[0] - circle_radius, circle_center[1] - circle_radius,
            circle_center[0] + circle_radius, circle_center[1] + circle_radius
        ], fill=(0, 0, 0, 128))
        
        # 绘制三角形播放图标
        triangle_size = icon_size // 3
        triangle_x = circle_center[0] - triangle_size // 3
        triangle_y = circle_center[1]
        
        triangle_points = [
            (triangle_x, triangle_y - triangle_size // 2),
            (triangle_x, triangle_y + triangle_size // 2),
            (triangle_x + triangle_size, triangle_y)
        ]
        draw.polygon(triangle_points, fill=(255, 255, 255, 255))
        
        # 将图标叠加到原图片上
        result = img.convert('RGBA')
        result = Image.alpha_composite(result, overlay)
        return result.convert('RGB')
    
    def crop_to_square(self, img, size):
        """从中心裁剪图片为正方形，优化高分辨率处理"""
        original_width, original_height = img.size
        target_size = size[0]  # 目标正方形边长
        
        # 如果原图已经很小，先放大再处理
        min_dimension = min(original_width, original_height)
        if min_dimension < target_size:
            # 放大到至少目标尺寸的1.5倍，确保质量
            scale_factor = (target_size * 1.5) / min_dimension
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            original_width, original_height = new_width, new_height
        
        # 计算裁剪区域，从中心开始
        if original_width > original_height:
            # 横向图片，以高度为准
            scale = target_size / original_height
            new_width = int(original_width * scale)
            new_height = target_size
            
            # 先缩放
            img_scaled = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 从中心裁剪为正方形
            left = (new_width - target_size) // 2
            top = 0
            right = left + target_size
            bottom = target_size
            
        else:
            # 纵向图片或正方形，以宽度为准
            scale = target_size / original_width
            new_width = target_size
            new_height = int(original_height * scale)
            
            # 先缩放
            img_scaled = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 从中心裁剪为正方形
            left = 0
            top = (new_height - target_size) // 2
            right = target_size
            bottom = top + target_size
        
        # 执行裁剪
        cropped = img_scaled.crop((left, top, right, bottom))
        return cropped
    
    def create_circle_avatar(self, avatar_img, size):
        """创建圆形头像，带微妙阴影"""
        # 创建圆形蒙版
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)
        
        # 调整头像尺寸
        avatar_resized = avatar_img.resize(size, Image.Resampling.LANCZOS)
        
        # 创建带阴影的头像
        shadow_size = (size[0] + 4, size[1] + 4)
        shadow = Image.new("RGBA", shadow_size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        
        # 绘制阴影
        shadow_draw.ellipse([2, 2, size[0] + 2, size[1] + 2], fill=(0, 0, 0, 30))
        
        # 创建头像
        result = Image.new("RGBA", shadow_size, (0, 0, 0, 0))
        avatar_bg = Image.new("RGBA", size, (255, 255, 255, 255))
        avatar_bg.paste(avatar_resized, (0, 0))
        avatar_bg.putalpha(mask)
        
        # 合成阴影和头像
        result = Image.alpha_composite(result, shadow)
        result.paste(avatar_bg, (0, 0), avatar_bg)
        
        return result
    
    def wrap_text(self, text, font, max_width):
        """文字换行（优化中文换行）"""
        if not text:
            return ''
            
        lines = []
        paragraphs = text.split('\n')
        
        temp_img = Image.new("RGB", (1, 1), "white")
        draw = ImageDraw.Draw(temp_img)
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                lines.append('')
                continue
            
            # 对于很长的段落，优先在标点符号处换行
            current_line = ''
            i = 0
            while i < len(paragraph):
                char = paragraph[i]
                test_line = current_line + char
                bbox = draw.textbbox((0, 0), test_line, font=font)
                
                if bbox[2] - bbox[0] <= max_width:
                    current_line = test_line
                    i += 1
                else:
                    # 如果当前行为空，强制添加字符避免无限循环
                    if not current_line:
                        current_line = char
                        i += 1
                    
                    # 尝试在合适的位置断行
                    break_pos = self.find_break_position(current_line)
                    if break_pos > 0 and break_pos < len(current_line):
                        # 在找到的位置断行
                        lines.append(current_line[:break_pos])
                        current_line = current_line[break_pos:]
                        # 不增加i，重新检查当前字符
                    else:
                        # 没找到合适断点，在当前位置断行
                        lines.append(current_line)
                        current_line = ''
                        # 不增加i，重新处理当前字符
            
            if current_line:
                lines.append(current_line)
        
        return '\n'.join(lines)
    
    def find_break_position(self, text):
        """找到合适的断行位置"""
        # 中文标点符号
        chinese_punctuation = '，。！？；：、""''（）【】《》'
        # 英文标点符号和空格
        english_breaks = ' ,.!?;:'
        
        # 从后往前找断点
        for i in range(len(text) - 1, -1, -1):
            char = text[i]
            if char in chinese_punctuation:
                return i + 1  # 在标点后断行
            elif char in english_breaks:
                return i + 1  # 在标点或空格后断行
        
        # 如果没找到标点，在3/4位置断行
        return int(len(text) * 0.75) if len(text) > 4 else len(text) - 1
    
    def format_time(self, pub_date):
        """格式化时间（将GMT时间转换为东八区时间）"""
        try:
            # RSS时间格式: Fri, 04 Jul 2025 07:51:28 GMT
            dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
            
            # 将GMT时间转换为东八区时间（UTC+8）
            import pytz
            gmt = pytz.timezone('GMT')
            beijing = pytz.timezone('Asia/Shanghai')
            
            # 如果dt没有时区信息，先设置为GMT
            if dt.tzinfo is None:
                dt = gmt.localize(dt)
            
            # 转换为北京时间
            beijing_time = dt.astimezone(beijing)
            
            return beijing_time.strftime("%Y年%m月%d日 %H:%M")
        except Exception as e:
            # 如果转换失败，尝试简单的+8小时处理
            try:
                dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
                # 简单加8小时
                beijing_time = dt + timedelta(hours=8)
                return beijing_time.strftime("%Y年%m月%d日 %H:%M")
            except:
                return pub_date
    
    def generate_screenshot(self, channel_info, weibo_item, filename=None, output_prefix=None):
        """生成微博截图（高清版）"""
        # 设置超高清画布参数
        width = 2400
        margin = 64
        padding = 80
        spacing = 48
        image_spacing = 80  # 文字和图片之间的间距
        avatar_size = (192, 192)
        single_image_size = (1920, 1920)  # 单张图片的正方形尺寸
        grid_image_size = (640, 640)    # 网格图片的正方形尺寸
        
        # 生成规范的文件名：weibo_频道uid_帖子id_日期_时间（东八区）
        if not filename:
            # 提取频道UID
            channel_uid = self.extract_channel_uid(channel_info)
            
            # 提取帖子ID
            post_id = self.extract_post_id(weibo_item)
            
            # 获取东八区时间
            beijing_datetime = self.get_beijing_datetime(weibo_item.get('pub_date', ''))
            
            # 生成文件名
            filename = f"weibo_{channel_uid}_{post_id}_{beijing_datetime}.jpg"
        
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        # 下载头像
        print("📷 下载头像...")
        if channel_info.get('image_url'):
            avatar_img = self.download_image(channel_info['image_url'], force_size=avatar_size)
        else:
            # 创建默认头像
            avatar_img = Image.new("RGB", avatar_size, "#4A90E2")
            draw = ImageDraw.Draw(avatar_img)
            draw.ellipse([5, 5, avatar_size[0]-5, avatar_size[1]-5], fill="white")
        
        avatar = self.create_circle_avatar(avatar_img, avatar_size)
        
        # 下载配图和视频封面
        images = []
        total_media_count = len(weibo_item.get('image_urls', []))
        
        # 如果有视频，计入总媒体数量
        if weibo_item.get('video_info') and weibo_item['video_info'].get('poster'):
            total_media_count += 1
        
        # 根据总媒体数量决定尺寸
        use_single_size = (total_media_count == 1)
        target_size = single_image_size if use_single_size else grid_image_size
        
        # 检查是否为纯视频微博（只有视频，没有图片）
        is_video_only = (len(weibo_item.get('image_urls', [])) == 0 and 
                        weibo_item.get('video_info') and 
                        weibo_item['video_info'].get('poster'))
        
        # 下载图片
        if weibo_item.get('image_urls'):
            print(f"📷 下载 {len(weibo_item['image_urls'])} 张配图...")
            for i, url in enumerate(weibo_item['image_urls'], 1):
                print(f"  下载第 {i}/{len(weibo_item['image_urls'])} 张图片...")
                img = self.download_image(url, square_size=target_size)
                images.append(img)
        
        # 下载视频封面
        if weibo_item.get('video_info') and weibo_item['video_info'].get('poster'):
            print("📹 下载高分辨率视频封面...")
            if is_video_only:
                # 纯视频微博：保持原始比例，但限制最大宽度
                max_video_width = width - 2 * (margin + padding)
                video_poster = self.download_image(weibo_item['video_info']['poster'], force_size=None)
                # 如果原图分辨率太小，智能放大
                if video_poster.size[0] < max_video_width * 0.8:
                    scale_factor = max_video_width / video_poster.size[0]
                    new_width = int(video_poster.size[0] * scale_factor)
                    new_height = int(video_poster.size[1] * scale_factor)
                    video_poster = video_poster.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    print(f"📈 视频封面智能放大到: {new_width}x{new_height}px")
                # 按比例缩放，保持宽高比
                video_poster = self.resize_keep_ratio(video_poster, (max_video_width, max_video_width))
            else:
                # 混合媒体：裁剪为正方形高分辨率
                video_poster = self.download_image(weibo_item['video_info']['poster'], square_size=target_size)
            
            if video_poster:
                # 添加播放图标
                video_poster_with_icon = self.add_video_play_icon(video_poster)
                images.append(video_poster_with_icon)
        
        # 计算文字区域 - 确保左右边距相等
        side_margin = margin + padding  # 左右边距相等
        text_width = width - 2 * side_margin
        wrapped_content = self.wrap_text(weibo_item['content'], self.content_font, text_width)
        
        temp_img = Image.new("RGB", (width, 1000), "white")
        draw = ImageDraw.Draw(temp_img)
        text_bbox = draw.multiline_textbbox((0, 0), wrapped_content, font=self.content_font, spacing=20)
        text_height = text_bbox[3] - text_bbox[1]
        
        # 计算配图区域高度
        image_area_height = 0
        if images:
            if len(images) == 1:
                if is_video_only:
                    # 纯视频微博：使用实际视频封面高度
                    image_area_height = images[0].size[1] + image_spacing
                else:
                    # 单张图片，固定正方形尺寸
                    image_area_height = single_image_size[1] + image_spacing
            else:
                # 多张图片，网格布局，固定正方形尺寸
                cols = min(3, len(images))
                rows = math.ceil(len(images) / cols)
                gap = 12  # 增加网格间距
                image_area_height = rows * grid_image_size[1] + (rows - 1) * gap + image_spacing
        
        # 计算总高度
        header_height = avatar_size[1] + spacing
        content_height = text_height + spacing * 2
        total_height = margin * 2 + header_height + content_height + image_area_height + 40
        
        # 创建画布 - 使用更自然的背景色
        canvas = Image.new("RGB", (width, total_height), "#FAFAFA")
        draw = ImageDraw.Draw(canvas)
        
        # 绘制头像（带阴影）
        avatar_x = margin + padding
        avatar_y = margin + padding
        
        # 粘贴带阴影的头像
        canvas.paste(avatar, (avatar_x - 2, avatar_y - 2), avatar)
        
        # 绘制用户信息
        name_x = avatar_x + avatar_size[0] + 15
        name_y = avatar_y + 8
        
        # 用户名 - 使用更深的颜色增强对比度
        author_name = weibo_item.get('author', '未知用户')
        draw.text((name_x, name_y), author_name, font=self.name_font, fill="#1A1A1A")
        # 动态计算用户名底部
        name_bbox = draw.textbbox((name_x, name_y), author_name, font=self.name_font)
        name_bottom = name_bbox[1] + (name_bbox[3] - name_bbox[1])
        # 发布时间，紧跟在用户名下方，留足间距
        time_y = name_bottom + 10  # 10像素额外间距
        formatted_time = self.format_time(weibo_item.get('pub_date', ''))
        draw.text((name_x, time_y), formatted_time, font=self.time_font, fill="#666666")
        
        # 绘制正文内容 - 使用更深的颜色增强可读性
        content_y = margin + padding + header_height + 16
        draw.multiline_text(
            (margin + padding, content_y),
            wrapped_content,
            font=self.content_font,
            fill="#1A1A1A",
            spacing=20
        )
        
        # 绘制配图
        if images:
            image_start_y = content_y + text_height + image_spacing
            
            if len(images) == 1:
                if is_video_only:
                    # 纯视频微博：左对齐显示，保持原始比例
                    img_x = margin + padding  # 与文字左对齐
                    canvas.paste(images[0], (img_x, image_start_y))
                else:
                    # 单张图片，左对齐显示，正方形
                    img_x = margin + padding  # 与文字左对齐
                    canvas.paste(images[0], (img_x, image_start_y))
            else:
                # 多张图片网格布局 - 左对齐
                cols = min(3, len(images))
                rows = math.ceil(len(images) / cols)
                gap = 8
                
                # 网格从文字左边开始，不居中
                grid_start_x = margin + padding  # 与文字左对齐
                grid_start_y = image_start_y
                
                for i, image in enumerate(images):
                    col = i % cols
                    row = i // cols
                    
                    # 精确计算每个图片的位置
                    x = grid_start_x + col * (grid_image_size[0] + gap)
                    y = grid_start_y + row * (grid_image_size[1] + gap)
                    
                    canvas.paste(image, (x, y))
        
        # 保存图片（超高清DPI）
        canvas.save(output_path, quality=98, optimize=True, dpi=(400, 400))
        print(f"✅ 超高清长图生成成功: {output_path}")
        print(f"📊 图片信息: {width}x{total_height}px (DPI 400)")
        
        return output_path
    
    def extract_channel_uid(self, channel_info):
        """提取频道UID"""
        try:
            # 从频道链接中提取UID
            link = channel_info.get('link', '')
            if '/u/' in link:
                # 格式：https://weibo.com/u/1234567890
                uid = link.split('/u/')[-1].split('?')[0].split('/')[0]
                return uid[:10]  # 限制长度
            elif 'weibo.com/' in link:
                # 其他格式尝试提取数字ID
                import re
                numbers = re.findall(r'\d+', link)
                if numbers:
                    return numbers[0][:10]
            
            # 如果无法提取，使用频道标题的哈希
            title = channel_info.get('title', 'unknown')
            return str(abs(hash(title)))[:8]
        except:
            return "unknown"
    
    def extract_post_id(self, weibo_item):
        """提取微博博文ID（如：PzAWQejXh）"""
        try:
            import re
            
            # 从link中提取微博博文ID
            link = weibo_item.get('link', '')
            if link:
                # 匹配微博博文ID格式：通常是字母数字组合，长度7-12位
                # 格式如：https://weibo.com/1234567890/PzAWQejXh
                # 或：https://weibo.com/u/1234567890/PzAWQejXh
                weibo_id_patterns = [
                    r'/([A-Za-z0-9]{7,12})(?:\?|$|#)',  # 路径末尾的ID
                    r'/([A-Za-z0-9]{7,12})/',           # 路径中间的ID
                    r'id=([A-Za-z0-9]{7,12})',          # 参数中的ID
                ]
                
                for pattern in weibo_id_patterns:
                    match = re.search(pattern, link)
                    if match:
                        post_id = match.group(1)
                        # 验证是否为有效的微博ID格式（包含字母和数字）
                        if re.match(r'^[A-Za-z0-9]{7,12}$', post_id) and re.search(r'[A-Za-z]', post_id):
                            return post_id
            
            # 从guid中提取
            guid = weibo_item.get('guid', '')
            if guid:
                for pattern in weibo_id_patterns:
                    match = re.search(pattern, guid)
                    if match:
                        post_id = match.group(1)
                        if re.match(r'^[A-Za-z0-9]{7,12}$', post_id) and re.search(r'[A-Za-z]', post_id):
                            return post_id
            
            # 如果无法从链接提取，查找任何符合微博ID格式的字符串
            all_text = f"{link} {guid} {weibo_item.get('title', '')} {weibo_item.get('description', '')}"
            weibo_ids = re.findall(r'\b([A-Za-z0-9]{7,12})\b', all_text)
            for post_id in weibo_ids:
                if re.search(r'[A-Za-z]', post_id) and re.search(r'[0-9]', post_id):
                    return post_id
            
            # 最终备用：使用内容生成短哈希ID（模拟微博ID格式）
            title = weibo_item.get('title', '')
            content = weibo_item.get('description', '')
            pub_date = weibo_item.get('pub_date', '')
            text = (title + content + pub_date)[:200]
            hash_value = abs(hash(text))
            
            # 转换为类似微博ID的格式（字母+数字组合）
            chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
            result = ''
            for _ in range(9):  # 生成9位ID
                result += chars[hash_value % len(chars)]
                hash_value //= len(chars)
            return result
            
        except Exception as e:
            return "unknown"
    
    def get_beijing_datetime(self, pub_date):
        """获取北京时间格式的日期时间字符串"""
        try:
            if not pub_date:
                # 如果没有发布时间，使用当前北京时间
                import pytz
                beijing = pytz.timezone('Asia/Shanghai')
                now = datetime.now(beijing)
                return now.strftime("%Y%m%d_%H%M%S")
            
            # 解析GMT时间并转换为北京时间
            dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
            
            # 转换为北京时间
            import pytz
            gmt = pytz.timezone('GMT')
            beijing = pytz.timezone('Asia/Shanghai')
            
            if dt.tzinfo is None:
                dt = gmt.localize(dt)
            
            beijing_time = dt.astimezone(beijing)
            return beijing_time.strftime("%Y%m%d_%H%M%S")
        except:
            # 备用方案：简单加8小时
            try:
                dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
                beijing_time = dt + timedelta(hours=8)
                return beijing_time.strftime("%Y%m%d_%H%M%S")
            except:
                # 最终备用：使用当前时间
                return datetime.now().strftime("%Y%m%d_%H%M%S")


def create_weibo_image(rss_url, index=0, output_filename=None):
    """创建微博长图的便捷函数"""
    # 获取数据
    if not rss_url:
        raise ValueError("需要提供RSS URL")
    
    xml_content = RSSWeiboParser.fetch_rss_data(rss_url)
    if not xml_content:
        raise Exception("无法获取RSS数据")
    
    # 解析数据
    channel_info, weibo_items = RSSWeiboParser.parse_rss_xml(xml_content)
    if not weibo_items:
        raise Exception("未找到微博数据")
    
    if index >= len(weibo_items):
        raise ValueError(f"索引超出范围，最大索引为 {len(weibo_items) - 1}")
    
    # 生成长图
    generator = WeiboImageGenerator()
    return generator.generate_screenshot(channel_info, weibo_items[index], output_filename)
