#!/bin/bash

echo "🚀 微博RSS监听服务启动"
echo "====================="

# 检查配置文件
if [ ! -f .env ]; then
    echo "❌ 配置文件 .env 不存在"
    echo "💡 请先复制并编辑配置文件："
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi

# 检查必要的网络和容器
echo "🔍 检查RSSHub网络连接..."

# 检查rsshub_default网络是否存在
if docker network ls | grep -q rsshub_default; then
    echo "✅ rsshub_default 网络已找到"
else
    echo "⚠️  rsshub_default 网络未找到"
    echo "💡 如果您的RSSHub使用不同的网络名称，请修改 docker-compose.yml"
fi

# 检查rsshub容器是否运行
if docker ps | grep -q rsshub; then
    echo "✅ RSSHub 容器正在运行"
else
    echo "⚠️  RSSHub 容器未运行"
    echo "💡 请确保RSSHub服务已启动，或在.env中使用外部地址"
fi

echo "✅ 配置文件检查通过"

# 检查Docker是否运行
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动Docker"
    exit 1
fi

echo "✅ Docker 服务正常"

# 创建必要目录
mkdir -p outputs logs data

echo "🔧 构建并启动服务..."

# 停止现有服务
docker-compose down

# 构建并启动
docker-compose up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo ""
echo "📊 服务状态:"
docker-compose ps

echo ""
echo "📋 管理命令:"
echo "  查看日志: docker-compose logs -f"
echo "  查看状态: docker-compose ps"
echo "  重启服务: docker-compose restart"
echo "  停止服务: docker-compose down"
echo "  健康检查: docker exec weibo-rss-monitor python healthcheck.py"

echo ""
echo "🎉 服务启动完成！"
