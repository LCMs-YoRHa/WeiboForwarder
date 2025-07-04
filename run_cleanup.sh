#!/bin/bash

# 定时清理脚本 - 用于cron定时任务

cd "$(dirname "$0")"

echo "$(date '+%Y-%m-%d %H:%M:%S') - 开始执行清理任务" >> logs/cleanup.log

# 运行清理脚本
python3 cleanup.py >> logs/cleanup.log 2>&1

echo "$(date '+%Y-%m-%d %H:%M:%S') - 清理任务完成" >> logs/cleanup.log
echo "----------------------------------------" >> logs/cleanup.log
