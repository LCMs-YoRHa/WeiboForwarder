#!/bin/bash

echo "🚀 微博RSS监听服务 Docker 启动脚本"
echo "=================================="

# 检查是否存在.env文件
if [ ! -f .env ]; then
    echo "❌ 未找到 .env 配置文件"
    echo "💡 请复制 .env.example 为 .env 并填写配置"
    echo ""
    echo "cp .env.example .env"
    echo "nano .env  # 编辑配置文件"
    exit 1
fi

echo "✅ 找到配置文件 .env"

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker 服务"
    echo "💡 Ubuntu/Debian: sudo systemctl start docker"
    echo "💡 CentOS/RHEL: sudo systemctl start docker"
    exit 1
fi

echo "✅ Docker 运行正常"

# 检查docker-compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose 未安装"
    echo "💡 请先安装 docker-compose："
    echo "   curl -L \"https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
    echo "   chmod +x /usr/local/bin/docker-compose"
    exit 1
fi

echo "✅ docker-compose 可用"

# 构建并启动容器
echo "🔨 构建 Docker 镜像..."
docker-compose build

echo "🚀 启动服务..."
docker-compose up -d

echo ""
echo "✅ 服务启动完成！"
echo ""
echo "📋 管理命令："
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo "  查看状态: docker-compose ps"
echo ""
echo "📁 输出目录: ./outputs"
echo "📁 日志目录: ./logs"
echo "📁 数据目录: ./data"
echo ""
echo "🔍 健康检查: docker exec weibo-rss-monitor python healthcheck.py"
