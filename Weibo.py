# -*- coding: utf-8 -*-
"""
基于RSS的微博长图生成器
通过RSS服务获取微博数据，生成美观的长图
"""

import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import xml.etree.ElementTree as ET
import re
import math
import os
from datetime import datetime
from html import unescape
import argparse

# 配置
RSS_URL = "http://68.64.177.186:1200/weibo/user/1195908387"
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"  # Windows字体路径
OUTPUT_DIR = "outputs"

# 演示用的RSS XML数据
DEMO_RSS_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
<channel>
<title>少年JUMP吧的微博</title>
<link>https://weibo.com/1935396210/</link>
<atom:link href="http://68.64.177.186:1200/weibo/user/1935396210" rel="self" type="application/rss+xml"/>
<description>合作+v jump52zn 这里是涨姿势刷情报爱销量的少年JUMP街道办 - Powered by RSSHub</description>
<generator>RSSHub</generator>
<webMaster>contact@rsshub.app (RSSHub)</webMaster>
<language>en</language>
<image>
<url>https://tvax2.sinaimg.cn/crop.0.0.310.310.180/735bcd72ly8ft3nr06beej208m08m749.jpg</url>
<title>少年JUMP吧的微博</title>
<link>https://weibo.com/1935396210/</link>
</image>
<lastBuildDate>Fri, 04 Jul 2025 09:23:58 GMT</lastBuildDate>
<ttl>1</ttl>
<item>
<title>纯视频微博测试</title>
<description><![CDATA[这是一个只包含视频的微博测试<br><br><a href="https://video.weibo.com/show?fid=1034:5184493913571420" data-hide=""><span class="url-icon"><img style="width: 1rem;height: 1rem" src="https://h5.sinaimg.cn/upload/2015/09/25/3/timeline_card_small_video_default.png" referrerpolicy="no-referrer"></span><span class="surl-text">测试视频</span></a> <br clear="both"><div style="clear: both"></div><video controls="controls" poster="https://tvax1.sinaimg.cn/orj480/0026YIXUgy1i31ywn95a7j60j20aqdjn02.jpg" style="width: 100%"><source src="https://f.video.weibocdn.com/o0/S4ln4fSqlx08pxcyRtb201041200SrlF0E010.mp4?label=mp4_720p" type="video/mp4"><p>视频无法显示</p></video>]]></description>
<link>https://weibo.com/1935396210/TestVideo001</link>
<guid isPermaLink="false">https://weibo.com/1935396210/TestVideo001</guid>
<pubDate>Fri, 04 Jul 2025 08:00:00 GMT</pubDate>
<author>测试用户</author>
<category>视频测试</category>
</item>
<item>
<title>混合媒体测试</title>
<description><![CDATA[这是一个包含图片和视频的混合媒体测试<br><br><img style="" src="https://tvax3.sinaimg.cn/large/0026YIXUgy1i320w2kuxej60nv0xcaji02.jpg" referrerpolicy="no-referrer"><video controls="controls" poster="https://tvax1.sinaimg.cn/orj480/0026YIXUgy1i31ywn95a7j60j20aqdjn02.jpg" style="width: 100%"><source src="https://f.video.weibocdn.com/o0/S4ln4fSqlx08pxcyRtb201041200SrlF0E010.mp4?label=mp4_720p" type="video/mp4"><p>视频无法显示</p></video>]]></description>
<link>https://weibo.com/1935396210/TestMixed001</link>
<guid isPermaLink="false">https://weibo.com/1935396210/TestMixed001</guid>
<pubDate>Fri, 04 Jul 2025 07:45:00 GMT</pubDate>
<author>测试用户</author>
<category>混合测试</category>
</item>
<item>
<title>6张图片测试</title>
<description><![CDATA[这是一个包含6张图片的网格对齐测试<br><br><img style="" src="https://tvax3.sinaimg.cn/large/0026YIXUgy1i320w2kuxej60nv0xcaji02.jpg" referrerpolicy="no-referrer"><img style="" src="https://tvax4.sinaimg.cn/large/0026YIXUgy1i320w3ooorj60nv0xcgu202.jpg" referrerpolicy="no-referrer"><img style="" src="https://tvax4.sinaimg.cn/large/0026YIXUgy1i320w4rqptj60nv0xc48502.jpg" referrerpolicy="no-referrer"><img style="" src="https://tvax3.sinaimg.cn/large/0026YIXUgy1i320w646wmj60xc0xcnb702.jpg" referrerpolicy="no-referrer"><img style="" src="https://tvax2.sinaimg.cn/large/0026YIXUgy1i320w71r4wj60p00xc46s02.jpg" referrerpolicy="no-referrer"><img style="" src="https://tvax3.sinaimg.cn/large/0026YIXUgy1i320w8jdswj60qo0xcqcd02.jpg" referrerpolicy="no-referrer">]]></description>
<link>https://weibo.com/1935396210/Test6Images</link>
<guid isPermaLink="false">https://weibo.com/1935396210/Test6Images</guid>
<pubDate>Fri, 04 Jul 2025 07:40:00 GMT</pubDate>
<author>测试用户</author>
<category>网格测试</category>
</item>
<item>
<title>4张图片测试</title>
<description><![CDATA[这是一个包含4张图片的网格对齐测试<br><br><img style="" src="https://tvax3.sinaimg.cn/large/0026YIXUgy1i320w2kuxej60nv0xcaji02.jpg" referrerpolicy="no-referrer"><img style="" src="https://tvax4.sinaimg.cn/large/0026YIXUgy1i320w3ooorj60nv0xcgu202.jpg" referrerpolicy="no-referrer"><img style="" src="https://tvax4.sinaimg.cn/large/0026YIXUgy1i320w4rqptj60nv0xc48502.jpg" referrerpolicy="no-referrer"><img style="" src="https://tvax3.sinaimg.cn/large/0026YIXUgy1i320w646wmj60xc0xcnb702.jpg" referrerpolicy="no-referrer">]]></description>
<link>https://weibo.com/1935396210/Test4Images</link>
<guid isPermaLink="false">https://weibo.com/1935396210/Test4Images</guid>
<pubDate>Fri, 04 Jul 2025 07:38:00 GMT</pubDate>
<author>测试用户</author>
<category>网格测试</category>
</item>
<item>
<title>庵野秀明妻子安野梦洋子的少女漫画『魔女的考验』新作短篇动画化</title>
<description><![CDATA[庵野秀明妻子安野梦洋子的少女漫画『魔女的考验』新作短篇动画化<br><br>监督：松井祐亮<br>动画制作：Khara <a href="https://video.weibo.com/show?fid=1034:5184493913571420" data-hide=""><span class="url-icon"><img style="width: 1rem;height: 1rem" src="https://h5.sinaimg.cn/upload/2015/09/25/3/timeline_card_small_video_default.png" referrerpolicy="no-referrer"></span><span class="surl-text">日推的微博视频</span></a> <br clear="both"><div style="clear: both"></div><video controls="controls" poster="https://tvax1.sinaimg.cn/orj480/0026YIXUgy1i31ywn95a7j60j20aqdjn02.jpg" style="width: 100%"><source src="https://f.video.weibocdn.com/o0/S4ln4fSqlx08pxcyRtb201041200SrlF0E010.mp4?label=mp4_720p&amp;template=1280x720.25.0" type="video/mp4"><p>视频无法显示</p></video>]]></description>
<link>https://weibo.com/1935396210/PzxMFDdIO</link>
<guid isPermaLink="false">https://weibo.com/1935396210/PzxMFDdIO</guid>
<pubDate>Fri, 04 Jul 2025 07:51:28 GMT</pubDate>
<author>日推</author>
<category>动画</category>
</item>
<item>
<title>『致不灭的你』动画第三季「现世篇」视觉图公开！2025年10月开播！#致不灭的你#致不灭的你 [图片]</title>
<description><![CDATA[『致不灭的你』动画第三季「现世篇」视觉图公开！2025年10月开播！<br><br><a href="https://m.weibo.cn/search?containerid=231522type%3D1%26t%3D10%26q%3D%23%E8%87%B4%E4%B8%8D%E7%81%AD%E7%9A%84%E4%BD%A0%23&amp;isnewpage=1" data-hide=""><span class="surl-text">#致不灭的你#</span></a><a href="https://m.weibo.cn/p/index?extparam=%E8%87%B4%E4%B8%8D%E7%81%AD%E7%9A%84%E4%BD%A0&amp;containerid=100808eabefa96b785163efc88d03e1ed298e8" data-hide=""><span class="url-icon"><img style="width: 1rem;height: 1rem" src="https://n.sinaimg.cn/photo/5213b46e/20180926/timeline_card_small_super_default.png" referrerpolicy="no-referrer"></span><span class="surl-text">致不灭的你</span></a> <img style="" src="https://tvax2.sinaimg.cn/large/0026YIXUgy1i31y7wpyenj60xc1b64a602.jpg" referrerpolicy="no-referrer">]]></description>
<link>https://weibo.com/1935396210/PzxMFDdIO</link>
<guid isPermaLink="false">https://weibo.com/1935396210/PzxMFDdIO</guid>
<pubDate>Fri, 04 Jul 2025 07:51:28 GMT</pubDate>
<author>少年JUMP吧</author>
<category>致不灭的你</category>
</item>
<item>
<title>小畑健新绘 『棋魂』展纪念插画合集棋魂 [图片][图片][图片][图片][图片][图片][图片][图片][图片]</title>
<description><![CDATA[小畑健新绘 『棋魂』展纪念插画合集<br><br><a href="https://m.weibo.cn/p/index?extparam=%E6%A3%8B%E9%AD%82&amp;containerid=100808ef90a0474af9b35708edbb838c88b9cb" data-hide=""><span class="url-icon"><img style="width: 1rem;height: 1rem" src="https://n.sinaimg.cn/photo/5213b46e/20180926/timeline_card_small_super_default.png" referrerpolicy="no-referrer"></span><span class="surl-text">棋魂</span></a> <img style="" src="https://tvax3.sinaimg.cn/large/0026YIXUgy1i320w2kuxej60nv0xcaji02.jpg" referrerpolicy="no-referrer"><img style="" src="https://tvax4.sinaimg.cn/large/0026YIXUgy1i320w3ooorj60nv0xcgu202.jpg" referrerpolicy="no-referrer"><img style="" src="https://tvax4.sinaimg.cn/large/0026YIXUgy1i320w4rqptj60nv0xc48502.jpg" referrerpolicy="no-referrer"><img style="" src="https://tvax3.sinaimg.cn/large/0026YIXUgy1i320w646wmj60xc0xcnb702.jpg" referrerpolicy="no-referrer"><img style="" src="https://tvax2.sinaimg.cn/large/0026YIXUgy1i320w71r4wj60p00xc46s02.jpg" referrerpolicy="no-referrer"><img style="" src="https://tvax3.sinaimg.cn/large/0026YIXUgy1i320w8jdswj60qo0xcqcd02.jpg" referrerpolicy="no-referrer"><img style="" src="https://tvax3.sinaimg.cn/large/0026YIXUgy1i320wa6fk3j61471e8nkn02.jpg" referrerpolicy="no-referrer"><img style="" src="https://tvax1.sinaimg.cn/large/0026YIXUgy1i320wbgfdrj618g1jknd402.jpg" referrerpolicy="no-referrer"><img style="" src="https://tvax2.sinaimg.cn/large/0026YIXUgy1i320wdop3uj61341jkavs02.jpg" referrerpolicy="no-referrer">]]></description>
<link>https://weibo.com/1935396210/PzxHZnoFG</link>
<guid isPermaLink="false">https://weibo.com/1935396210/PzxHZnoFG</guid>
<pubDate>Fri, 04 Jul 2025 07:39:56 GMT</pubDate>
<author>少年JUMP吧</author>
</item>
</channel>
</rss>'''

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
        """清理HTML内容，提取纯文本"""
        if not html_content:
            return ''
        
        # 移除视频标签
        html_content = re.sub(r'<video.*?</video>', '', html_content, flags=re.DOTALL)
        
        # 移除图片标签
        html_content = re.sub(r'<img[^>]*>', '', html_content)
        
        # 移除其他HTML标签，但保留链接文本
        html_content = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', html_content)
        html_content = re.sub(r'<[^>]+>', '', html_content)
        
        # 替换<br>为换行
        html_content = re.sub(r'<br\s*/?>', '\n', html_content)
        
        # 清理多余空行
        html_content = re.sub(r'\n\s*\n', '\n', html_content)
        
        # 解码HTML实体
        html_content = unescape(html_content)
        
        return html_content.strip()
    
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
        """设置字体"""
        try:
            self.name_font = ImageFont.truetype(FONT_PATH, 20)
            self.time_font = ImageFont.truetype(FONT_PATH, 14)
            self.content_font = ImageFont.truetype(FONT_PATH, 18)
            print("✅ 字体加载成功")
        except:
            print("⚠️ 字体加载失败，使用默认字体")
            self.name_font = ImageFont.load_default()
            self.time_font = ImageFont.load_default()
            self.content_font = ImageFont.load_default()
    
    def download_image(self, url, square_size=None, force_size=None):
        """下载图片，可选择裁剪为正方形或强制调整尺寸"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://weibo.com/'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            img = Image.open(BytesIO(response.content)).convert("RGB")
            
            if force_size:
                # 强制调整为指定尺寸（用于头像）
                img = img.resize(force_size, Image.Resampling.LANCZOS)
            elif square_size:
                # 裁剪为正方形
                img = self.crop_to_square(img, square_size)
            
            return img
        except Exception as e:
            print(f"⚠️ 图片下载失败: {url[:50]}... 错误: {e}")
            # 创建占位图片
            placeholder_size = force_size or square_size or (300, 300)
            placeholder = Image.new("RGB", placeholder_size, "#E0E0E0")
            draw = ImageDraw.Draw(placeholder)
            draw.text((10, 10), "图片\n加载失败", fill="#666666", font=self.content_font)
            return placeholder
    
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
        """从中心裁剪图片为正方形"""
        original_width, original_height = img.size
        target_size = size[0]  # 目标正方形边长
        
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
        """文字换行"""
        lines = []
        paragraphs = text.split('\n')
        
        temp_img = Image.new("RGB", (1, 1), "white")
        draw = ImageDraw.Draw(temp_img)
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                lines.append('')
                continue
            
            current_line = ''
            for char in paragraph:
                test_line = current_line + char
                bbox = draw.textbbox((0, 0), test_line, font=font)
                
                if bbox[2] - bbox[0] <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = char
            
            if current_line:
                lines.append(current_line)
        
        return '\n'.join(lines)
    
    def format_time(self, pub_date):
        """格式化时间"""
        try:
            # RSS时间格式: Fri, 04 Jul 2025 07:51:28 GMT
            from datetime import datetime
            dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
            return dt.strftime("%Y年%m月%d日 %H:%M")
        except:
            return pub_date
    
    def generate_screenshot(self, channel_info, weibo_item, filename=None):
        """生成微博截图"""
        
        # 设置画布参数
        width = 750
        margin = 20
        padding = 25
        spacing = 15
        avatar_size = (60, 60)
        single_image_size = (600, 600)  # 单张图片的正方形尺寸
        grid_image_size = (200, 200)    # 网格图片的正方形尺寸
        
        # 生成文件名
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_id = weibo_item.get('id', 'unknown')[:10]
            filename = f"weibo_{safe_id}_{timestamp}.jpg"
        
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
            print("📹 下载视频封面...")
            if is_video_only:
                # 纯视频微博：保持原始比例，但限制最大宽度（确保左右边距相等）
                max_video_width = width - 2 * (margin + padding)
                video_poster = self.download_image(weibo_item['video_info']['poster'], force_size=None)
                # 按比例缩放，保持宽高比
                video_poster = self.resize_keep_ratio(video_poster, (max_video_width, max_video_width))
            else:
                # 混合媒体：裁剪为正方形
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
        text_bbox = draw.multiline_textbbox((0, 0), wrapped_content, font=self.content_font, spacing=8)
        text_height = text_bbox[3] - text_bbox[1]
        
        # 计算配图区域高度
        image_area_height = 0
        if images:
            if len(images) == 1:
                if is_video_only:
                    # 纯视频微博：使用实际视频封面高度
                    image_area_height = images[0].size[1] + spacing
                else:
                    # 单张图片，固定正方形尺寸
                    image_area_height = single_image_size[1] + spacing
            else:
                # 多张图片，网格布局，固定正方形尺寸
                cols = min(3, len(images))
                rows = math.ceil(len(images) / cols)
                gap = 8
                image_area_height = rows * grid_image_size[1] + (rows - 1) * gap + spacing
        
        # 计算总高度
        header_height = avatar_size[1] + spacing
        content_height = text_height + spacing * 2
        total_height = margin * 2 + header_height + content_height + image_area_height + 40
        
        # 创建画布 - 使用更自然的背景色
        canvas = Image.new("RGB", (width, total_height), "#FAFAFA")
        draw = ImageDraw.Draw(canvas)
        
        # 不再绘制白色背景框
        
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
        
        # 发布时间
        time_y = name_y + 28
        formatted_time = self.format_time(weibo_item.get('pub_date', ''))
        draw.text((name_x, time_y), formatted_time, font=self.time_font, fill="#666666")
        
        # 绘制正文内容 - 使用更深的颜色增强可读性
        content_y = margin + padding + header_height + 10
        draw.multiline_text(
            (margin + padding, content_y),
            wrapped_content,
            font=self.content_font,
            fill="#1A1A1A",
            spacing=8
        )
        
        # 绘制配图
        if images:
            image_start_y = content_y + text_height + spacing
            
            if len(images) == 1:
                if is_video_only:
                    # 纯视频微博：居中显示，保持原始比例
                    video_width, video_height = images[0].size
                    content_area_width = width - 2 * (margin + padding)
                    img_x = margin + padding + (content_area_width - video_width) // 2
                    canvas.paste(images[0], (img_x, image_start_y))
                else:
                    # 单张图片，居中显示，正方形
                    content_area_width = width - 2 * (margin + padding)
                    img_x = margin + padding + (content_area_width - single_image_size[0]) // 2
                    canvas.paste(images[0], (img_x, image_start_y))
            else:
                # 多张图片网格布局 - 精确对齐
                cols = min(3, len(images))
                rows = math.ceil(len(images) / cols)
                gap = 8
                
                # 计算网格的总宽度
                total_grid_width = cols * grid_image_size[0] + (cols - 1) * gap
                
                # 计算网格起始位置（居中）
                content_area_width = width - 2 * (margin + padding)
                grid_start_x = margin + padding + (content_area_width - total_grid_width) // 2
                grid_start_y = image_start_y
                
                for i, image in enumerate(images):
                    col = i % cols
                    row = i // cols
                    
                    # 精确计算每个图片的位置
                    x = grid_start_x + col * (grid_image_size[0] + gap)
                    y = grid_start_y + row * (grid_image_size[1] + gap)
                    
                    canvas.paste(image, (x, y))
        
        # 保存图片
        canvas.save(output_path, quality=95, optimize=True)
        
        print(f"✅ 长图生成成功: {output_path}")
        print(f"📊 图片信息: {width}x{total_height}px")
        
        return output_path


def main():
    parser = argparse.ArgumentParser(description="基于RSS的微博长图生成器")
    parser.add_argument("--rss-url", default=RSS_URL, help="RSS源URL")
    parser.add_argument("--index", type=int, default=0, help="选择第几条微博 (从0开始)")
    parser.add_argument("--list", action="store_true", help="列出所有微博")
    parser.add_argument("--output", help="输出文件名")
    parser.add_argument("--demo", action="store_true", help="使用演示数据")
    
    args = parser.parse_args()
    
    print("🚀 基于RSS的微博长图生成器")
    print("="*50)
    
    # 获取RSS数据
    if args.demo:
        print("📋 使用演示数据...")
        xml_content = DEMO_RSS_XML
    else:
        xml_content = RSSWeiboParser.fetch_rss_data(args.rss_url)
        if not xml_content:
            print("❌ 无法获取RSS数据")
            print("💡 提示：可以使用 --demo 参数运行演示模式")
            return
    
    # 解析RSS
    channel_info, weibo_items = RSSWeiboParser.parse_rss_xml(xml_content)
    if not weibo_items:
        print("❌ 未找到微博数据")
        return
    
    print(f"✅ 成功获取 {len(weibo_items)} 条微博")
    print(f"📝 频道: {channel_info.get('title', '未知')}")
    
    # 列出所有微博
    if args.list:
        print("\n📋 微博列表:")
        for i, item in enumerate(weibo_items):
            content_preview = item['content'][:50] + ('...' if len(item['content']) > 50 else '')
            image_count = len(item.get('image_urls', []))
            has_video = bool(item.get('video_info'))
            print(f"  {i}. {content_preview}")
            print(f"     图片: {image_count}张 | 视频: {'是' if has_video else '否'}")
            print(f"     时间: {item.get('pub_date', '')}")
            print()
        return
    
    # 选择要生成的微博
    if args.index >= len(weibo_items):
        print(f"❌ 索引超出范围，最大索引为 {len(weibo_items) - 1}")
        return
    
    selected_weibo = weibo_items[args.index]
    
    print(f"\n📝 选择的微博 (索引 {args.index}):")
    print(f"  内容: {selected_weibo['content'][:100]}...")
    print(f"  图片: {len(selected_weibo.get('image_urls', []))} 张")
    print(f"  视频: {'是' if selected_weibo.get('video_info') else '否'}")
    print(f"  时间: {selected_weibo.get('pub_date', '')}")
    
    # 生成长图
    print("\n🎨 开始生成长图...")
    generator = WeiboImageGenerator()
    output_file = generator.generate_screenshot(channel_info, selected_weibo, args.output)
    
    print(f"\n🎉 完成！长图已保存到: {output_file}")


if __name__ == "__main__":
    main()
