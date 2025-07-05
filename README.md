# 微博RSS长图生成器

一个功能强大的微博RSS监听和长图生成工具，支持实时监听多个RSS源，自动生成美观的长图并推送到企业微信。

## ✨ 特性

- 🔄 **实时监听**: 支持监听多个RSS地址，自动检测新微博
- 🎨 **美观长图**: 自动生成包含头像、文字、图片的精美长图
- 📱 **企业微信推送**: 自动推送到企业微信，支持全员或指定用户
- 🐳 **Docker部署**: 完整的Docker化支持，易于部署和管理
- 🛡️ **稳定可靠**: 智能重试机制，完善的错误处理和日志记录
- 📊 **去重机制**: 自动记录已处理的微博，避免重复推送
- 🎭 **中文字体**: Docker环境下完整的中文字体支持
- 🧹 **自动清理**: 推送成功后1天自动删除图片，节省存储空间

## 🚀 快速开始

### Docker Compose 部署（唯一支持方式）

```bash
# 下载项目
git clone <repository-url>
cd weibo-rss-monitor

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的配置
notepad .env  # Windows
# 或 nano .env  # Linux/macOS

# 启动服务
docker-compose up -d --build

# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 📋 功能模块

### 核心模块

- **`create.py`**: RSS解析和长图生成
- **`push.py`**: 企业微信推送
- **`monitor.py`**: 实时监听服务
- **`Weibo.py`**: 命令行工具

### Docker支持

- **`Dockerfile`**: Docker镜像定义
- **`docker-compose.yml`**: 服务编排

## 🛠️ 配置说明

### RSS监听配置

#### 连接到现有的RSSHub服务

如果您已有运行的RSSHub Docker容器，可以直接连接：

```bash
# 查看RSSHub容器信息
docker inspect rsshub

# 在.env文件中配置Docker内部地址
RSS_URLS=http://rsshub:1200/weibo/user/123456  # 使用容器名
CHECK_INTERVAL=300  # 检查间隔（秒）
```

**重要**: 确保 `docker-compose.yml` 中的网络名称与您的RSSHub容器网络一致：
- 如果RSSHub网络名为 `rsshub_default`，已自动配置
- 如果不同，请修改 `docker-compose.yml` 中的网络名称

#### 外部RSS地址配置

```bash
# 使用外部地址
RSS_URLS=http://your-server-ip:1200/weibo/user/123456,https://rsshub.app/weibo/user/789012
```

### 企业微信配置

```bash
WECOM_CORPID=ww1234567890abcdef  # 企业ID
WECOM_CORPSECRET=your_secret_here  # 应用密钥
WECOM_AGENTID=1000002  # 应用ID
WECOM_TOUSER=@all  # 接收者
```

获取企业微信配置的详细步骤请参考 `wecom_config.py` 文件中的说明。

## 📁 项目结构

```
weibo-rss-monitor/
├── sources/               # 源码目录
│   ├── create.py          # 长图生成模块
│   ├── push.py            # 企业微信推送模块
│   ├── monitor.py         # 实时监听服务
│   ├── Weibo.py           # 命令行工具
│   ├── font_manager.py    # 字体管理模块
│   ├── cleanup.py         # 自动清理模块
│   ├── wecom_config.py    # 企业微信配置
│   └── fonts/            # 字体文件目录
├── docker/               # Docker相关文件
│   ├── Dockerfile        # Docker镜像定义
│   ├── .dockerignore     # Docker忽略文件
│   └── healthcheck.py    # 健康检查脚本
├── docker-compose.yml    # Docker编排文件
├── .env.example          # 配置模板
├── .env                  # 配置文件（需要创建）
├── requirements.txt      # Python依赖
├── outputs/              # 输出图片目录
├── logs/                 # 日志目录
├── data/                 # 数据目录
└── README.md            # 项目说明
```

## 🔧 服务管理

### Docker Compose 命令

```bash
# 查看服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 更新并重启
docker-compose up -d --build

# 停止服务
docker-compose down

# 进入容器调试
docker exec -it WeiboForwarder bash
```
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down
```

### 编程接口

```python
from create import create_weibo_image
from push import push_image_file

# 生成长图
image_file = create_weibo_image(rss_url, weibo_index=0)

# 推送到企业微信
success = push_image_file(image_file, corpid="...", corpsecret="...", agentid=123)
```

## 📊 监控和日志

### 日志文件

- `logs/weibo_monitor.log`: 监听服务日志
- `data/seen_items.json`: 已处理微博记录

### 健康检查

```bash
# Docker环境健康检查
docker exec WeiboForwarder python /app/docker/healthcheck.py
```

### 关键指标

- 监听RSS源数量
- 检查频率和最后检查时间
- 生成长图数量
- 推送成功率

## 🔍 故障排除

### RSSHub 连接问题

#### 手动验证连接

```bash
# 检查RSSHub容器状态
docker ps | grep rsshub

# 检查网络
docker network ls | grep rsshub

# 测试内部连接
docker exec WeiboForwarder ping rsshub
```

#### 常见解决方案

1. **网络名称不匹配**
   ```bash
   # 查看RSSHub实际网络名称
   docker inspect rsshub | grep NetworkMode
   
   # 修改 docker-compose.yml 中的网络名称
   ```

2. **RSSHub未运行**
   ```bash
   # 启动RSSHub服务
   docker start rsshub
   ```

3. **使用外部地址**
   ```bash
   # 在.env中使用服务器IP
   RSS_URLS=http://your-server-ip:1200/weibo/user/xxx
   ```

### 常见问题

1. **RSS地址无法访问**
   - 检查网络连接和RSS地址有效性
   - 查看监听服务日志：`docker-compose logs -f`

2. **企业微信推送失败**
   - 验证企业微信配置信息
   - 检查应用权限设置

3. **长图生成失败**
   - 检查图片下载是否正常
   - 确认字体文件是否存在

4. **重复推送**
   - 删除 `data/seen_items.json` 重新开始
   - 检查RSS源内容是否有变化

### 调试模式

```bash
# 设置调试日志级别（在.env文件中）
LOG_LEVEL=DEBUG

# 查看详细日志
docker-compose logs -f
```

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🔗 相关链接

- [Docker部署指南](DOCKER.md)
- [模块化使用示例](模块化使用示例.md)
- [快速开始指南](快速开始.md)

---

**注意**: 首次运行时会自动下载字体文件，请确保网络连接正常。如果您在企业网络环境中，可能需要配置代理设置。
