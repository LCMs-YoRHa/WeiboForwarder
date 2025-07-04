# 微博RSS长图生成器

基于RSS服务的微博长图生成器，无需Cookie，直接从RSS源获取微博内容并生成美观的长图。

## 功能特性

- 📡 **RSS数据获取** - 从自建RSS服务获取微博数据，避免Cookie和反爬问题
- 🎨 **美观长图** - 生成与微博官方风格一致的长图
- ✂️ **智能图片裁剪** - 所有图片统一裁剪为正方形，保持视觉一致性
  - 单张图片：中心裁剪为600x600正方形
  - 多张图片：中心裁剪为200x200正方形，整齐网格布局
  - 智能缩放：先缩放到合适大小，再从中心裁剪
- 🎬 **视频封面支持** - 智能提取视频封面，添加播放图标标识
  - 自动识别视频内容，提取poster封面图
  - 添加半透明播放图标，清晰标识视频内容
  - 与图片统一处理，保持布局一致性
- 🔄 **智能布局** - 圆形头像、智能换行、整齐的正方形网格布局
- 💻 **命令行工具** - 支持多种命令行参数，灵活使用
- 🛡️ **容错处理** - 图片下载失败时显示占位图
- 🎯 **演示模式** - 内置样例数据，无需网络即可体验

## 环境要求

- Python 3.7+
- Windows系统（使用微软雅黑字体）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 基本使用

生成最新一条微博的长图：
```bash
python Weibo.py
```

### 2. 演示模式（推荐新手试用）

使用内置演示数据，无需网络连接：
```bash
python Weibo.py --demo
```

查看演示数据中的所有微博：
```bash
python Weibo.py --demo --list
```

生成演示数据中的特定微博：
```bash
python Weibo.py --demo --index 1 --output "我的测试图.jpg"
```

### 3. 选择特定微博

生成第3条微博的长图（索引从0开始）：
```bash
python Weibo.py --index 2
```

### 4. 列出所有微博

查看RSS源中的所有微博：
```bash
python Weibo.py --list
```

### 5. 自定义输出文件名

```bash
python Weibo.py --index 1 --output "我的微博.jpg"
```

### 6. 使用自定义RSS源

```bash
python Weibo.py --rss-url "http://your-rss-server.com/weibo/user/123456"
```

## 配置说明

在 `Weibo.py` 文件顶部可以修改以下配置：

```python
# RSS源URL - 修改为你的RSS服务地址
RSS_URL = "http://68.64.177.186:1200/weibo/user/1935396210"

# 字体路径 - Windows系统默认微软雅黑
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"

# 输出目录
OUTPUT_DIR = "outputs"
```

## 输出说明

- 长图保存在 `outputs` 目录下
- 文件名格式：`weibo_{微博ID}_{时间戳}.jpg`
- 图片质量：95%，启用优化压缩

## RSS服务要求

需要RSS服务返回如下格式的XML数据：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>用户名的微博</title>
    <description>微博RSS源</description>
    <link>https://weibo.com/u/1935396210</link>
    <image>
      <url>头像URL</url>
    </image>
    <item>
      <title>微博标题</title>
      <description><![CDATA[包含HTML的微博内容]]></description>
      <link>https://weibo.com/detail/微博ID</link>
      <pubDate>Fri, 04 Jul 2025 07:51:28 GMT</pubDate>
      <author>用户名</author>
    </item>
  </channel>
</rss>
```

## 常见问题

### Q: 图片下载失败
A: 脚本会自动使用占位图代替失败的图片，不会中断生成过程。

### Q: 字体显示异常
A: 确保Windows系统中有微软雅黑字体，或修改 `FONT_PATH` 为其他可用字体。

### Q: RSS获取超时
A: 检查RSS服务是否正常运行，网络连接是否稳定。

## 示例

1. 列出微博列表：
```bash
python Weibo.py --list
```

2. 生成第一条微博：
```bash
python Weibo.py --index 0 --output "最新微博.jpg"
```

3. 使用其他RSS源：
```bash
python Weibo.py --rss-url "http://localhost:1200/weibo/user/其他用户ID"
```

## 更新日志

- v1.0 - 初始版本，支持基于RSS的微博长图生成
- 支持多图布局、视频封面、智能换行
- 命令行参数支持
- 容错处理机制
