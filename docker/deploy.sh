#!/bin/bash

# 微博RSS监听服务 - Linux服务器一键部署脚本
# 适用于 Ubuntu/Debian/CentOS/RHEL 系统

set -e

echo "🚀 微博RSS监听服务 - Linux服务器部署"
echo "=================================="

# 检测操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    echo "❌ 无法检测操作系统类型"
    exit 1
fi

echo "📋 系统信息: $OS $VER"

# 检查是否为root用户或有sudo权限
if [ "$EUID" -ne 0 ] && ! groups | grep -q sudo; then
    echo "❌ 需要root权限或sudo权限来安装依赖"
    echo "💡 请使用 sudo ./deploy.sh 运行"
    exit 1
fi

# 安装Docker
install_docker() {
    echo "🔧 安装 Docker..."
    
    if command -v docker &> /dev/null; then
        echo "✅ Docker 已安装"
        return
    fi
    
    # Ubuntu/Debian
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        sudo apt-get update
        sudo apt-get install -y ca-certificates curl gnupg lsb-release
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        rm get-docker.sh
    
    # CentOS/RHEL
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        sudo yum install -y yum-utils
        sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        sudo yum install -y docker-ce docker-ce-cli containerd.io
        sudo systemctl start docker
        sudo systemctl enable docker
    
    else
        echo "⚠️ 不支持的操作系统，请手动安装Docker"
        echo "💡 参考: https://docs.docker.com/engine/install/"
        exit 1
    fi
    
    # 添加当前用户到docker组
    sudo usermod -aG docker $USER
    echo "✅ Docker 安装完成"
}

# 安装Docker Compose
install_docker_compose() {
    echo "🔧 安装 Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        echo "✅ Docker Compose 已安装"
        return
    fi
    
    # 下载最新版本的docker-compose
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    echo "✅ Docker Compose 安装完成"
}

# 检查配置文件
check_config() {
    echo "📋 检查配置文件..."
    
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            echo "💡 复制配置模板..."
            cp .env.example .env
            echo "⚠️ 请编辑 .env 文件，填入你的RSS地址和企业微信配置"
            echo "💡 编辑命令: nano .env"
            return 1
        else
            echo "❌ 未找到配置文件模板"
            exit 1
        fi
    fi
    
    echo "✅ 配置文件检查完成"
}

# 创建必要目录
create_directories() {
    echo "📁 创建数据目录..."
    mkdir -p outputs logs data
    
    # 设置合适的权限
    chmod 755 outputs logs data
    
    echo "✅ 目录创建完成"
}

# 启动服务
start_service() {
    echo "🚀 启动服务..."
    
    # 确保start.sh有执行权限
    chmod +x start.sh
    
    # 构建并启动
    docker-compose build
    docker-compose up -d
    
    echo "✅ 服务启动完成"
}

# 显示状态信息
show_status() {
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
    echo "📁 数据目录:"
    echo "  输出图片: ./outputs"
    echo "  运行日志: ./logs"
    echo "  状态数据: ./data"
}

# 主流程
main() {
    # 安装依赖
    install_docker
    install_docker_compose
    
    # 创建目录
    create_directories
    
    # 检查配置
    if ! check_config; then
        echo ""
        echo "⚠️ 请先配置 .env 文件，然后重新运行部署脚本"
        echo "💡 配置完成后运行: ./deploy.sh"
        exit 1
    fi
    
    # 启动服务
    start_service
    
    # 显示状态
    show_status
    
    echo ""
    echo "🎉 部署完成！服务正在运行中..."
    echo "💡 如果这是首次运行，请确保 .env 文件中的配置正确"
}

# 运行主流程
main "$@"
