#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康检查脚本
"""

import os
import sys
import json
from datetime import datetime, timedelta

def check_health():
    """检查服务健康状态"""
    
    # 检查日志文件是否存在
    log_file = '/app/logs/weibo_monitor.log'
    if not os.path.exists(log_file):
        print("❌ 日志文件不存在")
        return False
    
    # 检查日志文件是否过旧
    try:
        stat = os.stat(log_file)
        last_modified = datetime.fromtimestamp(stat.st_mtime)
        if datetime.now() - last_modified > timedelta(minutes=30):
            print("❌ 日志文件过旧，服务可能已停止")
            return False
    except Exception as e:
        print(f"❌ 检查日志文件时间失败: {e}")
        return False
    
    # 检查数据文件
    data_file = '/app/data/seen_items.json'
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                last_update = data.get('last_update')
                if last_update:
                    last_update_time = datetime.fromisoformat(last_update.replace('Z', '+00:00').replace('+00:00', ''))
                    if datetime.now() - last_update_time > timedelta(hours=24):
                        print("⚠️ 数据文件超过24小时未更新")
        except Exception as e:
            print(f"⚠️ 检查数据文件失败: {e}")
    
    print("✅ 健康检查通过")
    return True

if __name__ == "__main__":
    if check_health():
        sys.exit(0)
    else:
        sys.exit(1)
