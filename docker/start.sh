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

echo "✅ 配置文件检查通过"

# 检查Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行"
    exit 1
fi

echo "✅ Docker 运行正常"

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

echo ""
echo "✅ 服务启动完成！"
echo ""
echo "📋 管理命令："
echo "  查看日志: docker-compose logs -f"
echo "  查看状态: docker-compose ps"
echo "  停止服务: docker-compose down"
