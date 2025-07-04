# Linux服务器快速部署指南

## 🚀 一键部署

```bash
# 1. 克隆项目
git clone <your-repository-url>
cd weibo-rss-monitor

# 2. 一键部署（自动安装Docker等依赖）
chmod +x deploy.sh
sudo ./deploy.sh

# 3. 编辑配置文件
nano .env

# 4. 重启服务
docker-compose restart
```

## ⚙️ 配置说明

编辑 `.env` 文件，填入以下配置：

```bash
# RSS源配置（必需）
RSS_URLS=http://your-rss-url1,http://your-rss-url2

# 企业微信配置（必需）
WECOM_CORPID=ww1234567890abcdef
WECOM_CORPSECRET=your_secret_here
WECOM_AGENTID=1000002

# 可选配置
CHECK_INTERVAL=300  # 检查间隔（秒）
WECOM_TOUSER=@all   # 推送对象
LOG_LEVEL=INFO      # 日志级别
```

## 📋 管理命令

```bash
# 查看服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 健康检查
docker exec weibo-rss-monitor python healthcheck.py
```

## 🔍 验证部署

1. **检查服务状态**
   ```bash
   docker-compose ps
   # 应该显示 weibo-rss-monitor 容器运行中
   ```

2. **查看日志**
   ```bash
   docker-compose logs --tail=20
   # 应该看到监听服务启动和RSS检查的日志
   ```

3. **健康检查**
   ```bash
   docker exec weibo-rss-monitor python healthcheck.py
   # 应该返回 "✅ 健康检查通过"
   ```

## 📁 重要目录

- `./outputs/` - 生成的长图保存位置
- `./logs/` - 服务运行日志
- `./data/` - 已处理微博记录

## ⚠️ 故障排除

**服务无法启动：**
- 检查Docker是否正常运行：`docker info`
- 检查配置文件是否正确：`cat .env`

**推送失败：**
- 验证企业微信配置
- 检查网络连接
- 查看详细日志：`docker-compose logs | grep ERROR`

**重复推送：**
- 清除历史记录：`rm -f data/seen_items.json`
- 重启服务：`docker-compose restart`

更多详细说明请参考 [DOCKER.md](DOCKER.md)
