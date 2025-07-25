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
- 🗂️ **智能管理**: 自动清理过期的seen_items记录，防止文件过大

## 🚀 快速开始

本项目未提供镜像，你可以自行构建镜像上传至DockerHub

### Docker Compose 部署

```bash
# 下载项目
cd weibo-rss-monitor

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的配置

 vim .env  # Linux

# 启动服务
docker-compose up -d --build

# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```


## 🛠️ 配置说明

### RSS监听配置

#### 连接到现有的RSSHub服务

如果您服务器内部已有本地部署好并运行的RSSHub Docker容器，可以直接连接：

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
WECOM_AGENTID=1000001  # 应用ID
WECOM_TOUSER=@all  # 接收者
```

### seen_items.json 自动清理配置

```bash
# seen_items.json 自动清理配置
SEEN_ITEMS_MAX_COUNT_PER_CHANNEL=50  # 每个频道最多保留50条记录
SEEN_ITEMS_CLEANUP_INTERVAL=7        # 每7天清理一次seen_items.json
```

**说明**:

- `seen_items.json` 用于记录已处理的微博，防止重复推送
- 系统会自动按频道ID分组，每个频道最多保留50条最新记录
- 超过50条的旧记录会被自动删除，保持文件大小合理
- 清理是安全的，只会删除旧记录，不会影响防重复功能

### 注意：

硬条件：2022年6月20日之后新创建的企业微信应用，企业微信官方要求配置可信IP。首先需具备一个域名进行认证。

获取企业微信配置的详细步骤请参考 `wecom_config.py` 文件中的说明。




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
`docker-compose restart`

# 停止服务
`docker-compose down`


## 📊 监控和日志


### 自动清理
系统会根据配置自动清理seen_items记录：
- 按频道分组：每个频道独立管理记录
- 数量限制：每个频道最多保留50条最新记录
- 清理频率：每7天检查一次

### 手动管理
```bash
# 进入容器
docker exec -it WeiboForwarder bash

# 查看统计信息（包含频道分布）
python /app/sources/manage_seen_items.py stats

# 列出所有频道
python /app/sources/manage_seen_items.py channels

# 备份当前文件
python /app/sources/manage_seen_items.py backup
```

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
   - 查看 `data/seen_items.json` 大小和记录数
   - 如果文件过大，会自动清理过期记录
   - 手动清理：`docker exec -it WeiboForwarder python /app/sources/manage_seen_items.py cleanup-days 30`
   - 完全重新开始：删除 `data/seen_items.json` （会导致所有微博重新推送）

5. **seen_items.json 文件过大**
   - 系统会自动清理，每个频道最多保留50条记录
   - 手动查看状态：`docker exec -it WeiboForwarder python /app/sources/manage_seen_items.py stats`
   - 手动备份：`docker exec -it WeiboForwarder python /app/sources/manage_seen_items.py backup`

### 调试模式

```bash
# 设置调试日志级别（在.env文件中）
LOG_LEVEL=DEBUG

# 查看详细日志
docker-compose logs -f
```

## FAQ

1. 为什么使用RSSHub抓取内容而不是直接通过微博API获取？

   微博API需要申请，申请麻烦，需要实名认证且有频率限制。

2. RSSHub服务一定要自建吗？

   不是必须的，你也可以使用公共实例，但是公共实例缓存刷新时间一般较长，会有消息滞后性，如果想获取实时的消息，建议自建服务,自行设置缓存刷新时间。

3. 为什么使用企业微信应用接口的方式推送，可以支持更多的推送方式吗？

   使用企业微信应用接口推送的方式可以直接在微信内获取到消息，不比下载企业微信应用。而微信作为日常必备应用，直接在微信内收取推送具有便利性，也避免了多开一个应用浪费资源。至于更多的推送方式，目前在考虑开发飞书自建应用的推送方式，如果还想有其他的推送方式，可以提交Issue，评价可行后（部分推送服务不支持图片推送）可能会支持。

   

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

