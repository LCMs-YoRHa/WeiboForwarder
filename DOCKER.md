# 微博RSS实时监听服务 Docker 部署指南

本项目提供了Docker化的微博RSS实时监听服务，可以监听多个RSS地址，发现新微博时自动生成长图并推送到企业微信。

## 🚀 快速开始

### 1. 准备配置文件

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
nano .env
```

### 2. 配置说明

在 `.env` 文件中配置以下参数：

```bash
# RSS监听配置
RSS_URLS=http://example.com/rss1,http://example.com/rss2  # 多个RSS地址用逗号分隔
CHECK_INTERVAL=300  # 检查间隔（秒），默认5分钟

# 企业微信配置
WECOM_CORPID=ww1234567890abcdef  # 企业ID
WECOM_CORPSECRET=your_secret_here  # 应用密钥
WECOM_AGENTID=1000002  # 应用ID
WECOM_TOUSER=@all  # 接收者，@all表示全员
WECOM_TOPARTY=  # 部门ID（可选）
WECOM_TOTAG=  # 标签ID（可选）

# 其他配置
LOG_LEVEL=INFO  # 日志级别：DEBUG, INFO, WARNING, ERROR
MAX_RETRIES=3  # 最大重试次数
TIMEOUT=30  # 网络超时时间（秒）
```

### 3. 启动服务

#### 使用启动脚本（推荐）

```bash
chmod +x start.sh
./start.sh
```

#### 手动启动

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d
```

## 📋 管理命令

```bash
# 查看服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 查看最近日志
docker-compose logs --tail=100

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新代码后重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📁 目录结构

```
weibo-rss-monitor/
├── outputs/          # 生成的长图文件
├── logs/             # 日志文件
├── data/             # 数据文件（已处理的微博ID）
├── .env              # 配置文件（需要创建）
├── .env.example      # 配置模板
├── docker-compose.yml # Docker编排文件
├── Dockerfile        # Docker镜像定义
└── start.sh          # 启动脚本
```

## 🔧 高级配置

### 多RSS源配置

在 `RSS_URLS` 中用逗号分隔多个RSS地址：

```bash
RSS_URLS=http://rss1.example.com/weibo/user/123,http://rss2.example.com/weibo/user/456,http://rss3.example.com/weibo/user/789
```

### 检查频率调整

根据需要调整检查频率：

```bash
CHECK_INTERVAL=180  # 3分钟检查一次
CHECK_INTERVAL=600  # 10分钟检查一次
CHECK_INTERVAL=1800 # 30分钟检查一次
```

### 企业微信推送范围

```bash
WECOM_TOUSER=@all              # 全员
WECOM_TOUSER=user1|user2       # 指定用户
WECOM_TOPARTY=1|2              # 指定部门
WECOM_TOTAG=tag1|tag2          # 指定标签
```

## 🔍 监控和故障排除

### 查看服务状态

```bash
# 检查容器状态
docker-compose ps

# 检查健康状态
docker exec weibo-rss-monitor python healthcheck.py
```

### 查看日志

```bash
# 实时日志
docker-compose logs -f

# 只看错误日志
docker-compose logs | grep ERROR

# 查看最近50行日志
docker-compose logs --tail=50
```

### 常见问题

1. **RSS地址无法访问**
   - 检查网络连接
   - 确认RSS地址是否正确
   - 查看日志中的具体错误信息

2. **企业微信推送失败**
   - 检查企业微信配置是否正确
   - 确认应用权限设置
   - 查看推送相关的错误日志

3. **重复推送问题**
   - 删除 `data/seen_items.json` 文件重新开始
   - 检查RSS源是否有重复内容

### 数据备份

重要数据文件：
- `data/seen_items.json` - 已处理的微博ID记录
- `logs/weibo_monitor.log` - 运行日志
- `outputs/` - 生成的长图文件

定期备份这些文件以防数据丢失。

## 🛠️ 开发模式

如需修改代码，可以使用开发模式：

```bash
# 停止服务
docker-compose down

# 修改代码后重新构建
docker-compose build --no-cache

# 启动服务
docker-compose up -d
```

或者直接在容器外运行：

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export $(cat .env | xargs)

# 运行监听服务
python monitor.py
```

## 📝 日志说明

日志级别说明：
- `INFO`: 正常运行信息
- `WARNING`: 警告信息，服务仍正常运行
- `ERROR`: 错误信息，可能影响功能
- `DEBUG`: 详细调试信息

重要日志关键字：
- `🆕 发现新微博`: 检测到新内容
- `✅ 长图生成成功`: 长图生成完成
- `✅ 企业微信推送成功`: 推送成功
- `❌`: 错误信息
- `⚠️`: 警告信息

## 🔧 系统要求

### 最低配置
- CPU: 1核
- 内存: 512MB
- 磁盘: 1GB可用空间
- 网络: 稳定的互联网连接

### 推荐配置
- CPU: 2核
- 内存: 1GB
- 磁盘: 5GB可用空间
- 网络: 带宽 ≥ 10Mbps

### 依赖服务
- Docker Engine 20.10+
- Docker Compose 2.0+

### 安装Docker（如未安装）

**Ubuntu/Debian:**
```bash
# 更新包索引
sudo apt-get update

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 添加用户到docker组
sudo usermod -aG docker $USER
```

**CentOS/RHEL:**
```bash
# 安装Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动Docker
sudo systemctl start docker
sudo systemctl enable docker

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
