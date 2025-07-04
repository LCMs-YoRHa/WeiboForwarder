#!/bin/bash

# 手动清理脚本 - 可以直接运行或通过Docker执行

echo "🧹 微博图片清理工具"
echo "==================="

# 检查是否在Docker容器中
if [ -f /.dockerenv ]; then
    echo "📦 在Docker容器中运行"
    cd /app
else
    echo "💻 在主机中运行"
    cd "$(dirname "$0")"
fi

# 显示使用方法
show_usage() {
    echo "用法："
    echo "  $0 [选项]"
    echo ""
    echo "选项："
    echo "  --stats    显示清理统计信息"
    echo "  --dry-run  预览清理（不实际删除）"
    echo "  --force    强制清理所有旧文件"
    echo "  --help     显示帮助信息"
    echo ""
}

# 显示统计信息
show_stats() {
    python3 -c "
from cleanup import ImageCleanupManager
import json

manager = ImageCleanupManager()
stats = manager.get_cleanup_stats()

print('📊 清理统计信息:')
print(f'  跟踪的图片: {stats.get(\"tracked_images\", 0)} 个')
print(f'  待清理图片: {stats.get(\"pending_cleanup\", 0)} 个')
print(f'  总占用空间: {stats.get(\"total_size\", 0) / (1024*1024):.2f}MB')
print(f'  最后清理时间: {stats.get(\"last_cleanup\", \"从未\")}')
"
}

# 预览清理
dry_run() {
    echo "🔍 预览清理（不会实际删除文件）..."
    python3 -c "
from cleanup import ImageCleanupManager
from datetime import datetime
import os

manager = ImageCleanupManager()
current_time = datetime.now()
to_delete = []

for image_path, info in manager.cleanup_data['pushed_images'].items():
    try:
        push_time = datetime.fromisoformat(info['push_time'])
        age_days = (current_time - push_time).days
        
        if age_days >= 1:  # CLEANUP_AFTER_DAYS
            file_size = os.path.getsize(image_path) if os.path.exists(image_path) else 0
            to_delete.append((image_path, age_days, file_size))
    except:
        continue

if to_delete:
    print(f'📋 将删除 {len(to_delete)} 个文件:')
    total_size = 0
    for path, age, size in to_delete:
        print(f'  {os.path.basename(path)} ({age}天前, {size/1024:.1f}KB)')
        total_size += size
    print(f'总计释放空间: {total_size/1024/1024:.2f}MB')
else:
    print('✅ 没有需要删除的文件')
"
}

# 强制清理
force_cleanup() {
    echo "⚠️ 强制清理所有旧文件..."
    read -p "确定要继续吗？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 cleanup.py
    else
        echo "❌ 清理已取消"
    fi
}

# 解析参数
case "$1" in
    --stats)
        show_stats
        ;;
    --dry-run)
        dry_run
        ;;
    --force)
        force_cleanup
        ;;
    --help)
        show_usage
        ;;
    "")
        echo "🧹 执行正常清理..."
        python3 cleanup.py
        ;;
    *)
        echo "❌ 未知选项: $1"
        show_usage
        exit 1
        ;;
esac
