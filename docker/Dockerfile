# 使用Python官方镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai

# 跳过系统依赖安装（使用项目内置字体，Python基础镜像已足够）

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源码
COPY sources/ ./

# 创建必要目录
RUN mkdir -p /app/outputs /app/logs /app/data

# 设置权限
RUN chmod +x /app/*.py /app/*.sh

# 启动命令
CMD ["python", "monitor.py"]
