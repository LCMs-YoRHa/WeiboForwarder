# 使用Python官方镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai

# 安装系统依赖（移除字体下载，使用项目内置字体）
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源码
COPY sources/ ./

# 创建必要目录
RUN mkdir -p /app/outputs /app/logs /app/data

# 更新字体缓存（使项目内置字体生效）
RUN fc-cache -fv

# 设置权限
RUN chmod +x /app/*.py /app/*.sh

# 暴露端口（如果需要健康检查等）
EXPOSE 8000

# 启动命令
CMD ["python", "monitor.py"]
