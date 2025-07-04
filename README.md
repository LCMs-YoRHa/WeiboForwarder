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
  - 纯视频微博保持原始比例，混合媒体统一正方形
- 🔄 **智能布局** - 圆形头像、智能换行、整齐的正方形网格布局
- 📤 **企业微信推送** - 生成长图后自动推送到企业微信
  - 支持推送给指定用户、部门、标签
  - 自动上传图片并发送消息
  - 支持配置文件和命令行参数两种配置方式
- 💻 **命令行工具** - 支持多种命令行参数，灵活使用
- 🛡️ **容错处理** - 图片下载失败时显示占位图
- 🎯 **演示模式** - 内置样例数据，无需网络即可体验

## 项目结构

```
f:\Projects\Python\Weibo\
├── Weibo.py                           # 主程序入口（命令行界面）
├── create.py                          # 长图生成模块
├── push.py                            # 企业微信推送模块
├── wecom_config.py                    # 企业微信配置模板
├── requirements.txt                   # 依赖列表
├── README.md                          # 主要说明文档
├── 快速开始.md                        # 快速开始指南
├── 企业微信推送使用说明.md             # 推送配置说明
├── quick_push.bat                     # 推送启动器（英文）
├── 微博推送器.bat                     # 推送启动器（中文）
├── 推送启动器.bat                     # 原始推送启动器
├── 启动器.bat                         # 基础启动器
├── .gitignore                         # Git忽略文件
└── outputs/                           # 输出目录
```

### 模块说明

- **Weibo.py** - 主程序，处理命令行参数和业务逻辑
- **create.py** - 长图生成模块，包含RSS解析和图片生成功能
- **push.py** - 企业微信推送模块，处理图片上传和消息发送

## 环境要求

- Python 3.7+
- Windows系统（使用微软雅黑字体）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

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

### 3. 企业微信推送

配置企业微信信息后，生成并推送长图：
```bash
python Weibo.py --demo --push
```

## 企业微信推送配置

1. 复制 `wecom_config.py` 文件，填入你的企业微信信息：
```python
WECOM_CONFIG = {
    'corpid': 'your_corp_id_here',
    'corpsecret': 'your_corp_secret_here', 
    'agentid': 1000000,
    'touser': '@all',
}
```

2. 详细配置方法请参考：[企业微信推送使用说明.md](企业微信推送使用说明.md)

## 常用命令

```bash
# 列出所有微博
python Weibo.py --list

# 生成指定微博
python Weibo.py --index 2

# 生成并推送
python Weibo.py --index 0 --push

# 自定义输出文件名
python Weibo.py --index 1 --output "我的微博.jpg"

# 使用自定义RSS源
python Weibo.py --rss-url "http://your-rss-server.com/weibo/user/123456"
```

## 配置说明

在 `Weibo.py` 文件顶部可以修改以下配置：

```python
# RSS源URL - 修改为你的RSS服务地址
RSS_URL = "http://your-rss-server:1200/weibo/user/user_id"

# 字体路径 - Windows系统默认微软雅黑
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"

# 输出目录
OUTPUT_DIR = "outputs"
```

## 常见问题

### Q: 图片下载失败
A: 脚本会自动使用占位图代替失败的图片，不会中断生成过程。

### Q: 字体显示异常
A: 确保Windows系统中有微软雅黑字体，或修改 `FONT_PATH` 为其他可用字体。

### Q: RSS获取超时
A: 检查RSS服务是否正常运行，网络连接是否稳定。

### Q: 企业微信推送失败
A: 检查企业微信配置是否正确，参考推送使用说明文档。

## 输出说明

- 长图保存在 `outputs` 目录下
- 文件名格式：`weibo_{微博ID}_{时间戳}.jpg`
- 图片质量：95%，启用优化压缩

## 许可证

MIT License
