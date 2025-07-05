#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
seen_items.json 管理工具
提供查看、清理、备份等功能
"""

import os
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# 配置
DATA_DIR = Path("./data") if os.path.exists("./data") else Path("/app/data") if os.path.exists("/app/data") else Path("./data")
SEEN_ITEMS_FILE = DATA_DIR / "seen_items.json"


def load_seen_items():
    """加载seen_items数据"""
    if not SEEN_ITEMS_FILE.exists():
        return {'items': [], 'last_update': None, 'total_count': 0}
    
    with open(SEEN_ITEMS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 兼容旧格式
    if isinstance(data, dict) and 'items' in data:
        return data
    else:
        # 旧格式转换
        old_items = data.get('seen_items', data) if isinstance(data, dict) else data
        if isinstance(old_items, list):
            current_time = datetime.now()
            items_data = [{
                'id': item_id,
                'timestamp': current_time.isoformat(),
                'rss_url': 'unknown'
            } for item_id in old_items]
            return {
                'items': items_data,
                'last_update': current_time.isoformat(),
                'total_count': len(items_data)
            }
        return {'items': [], 'last_update': None, 'total_count': 0}


def save_seen_items(data):
    """保存seen_items数据"""
    DATA_DIR.mkdir(exist_ok=True)
    with open(SEEN_ITEMS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def show_stats():
    """显示统计信息"""
    data = load_seen_items()
    items = data.get('items', [])
    
    print("📋 seen_items.json 统计信息")
    print("=" * 40)
    print(f"总记录数: {len(items)}")
    print(f"最后更新: {data.get('last_update', '未知')}")
    
    if items:
        # 按RSS源统计
        rss_stats = {}
        for item in items:
            rss_url = item.get('rss_url', 'unknown')
            rss_stats[rss_url] = rss_stats.get(rss_url, 0) + 1
        
        print("\n📊 RSS源分布:")
        for rss_url, count in sorted(rss_stats.items()):
            print(f"  {rss_url}: {count} 条")
        
        # 按频道ID统计
        channel_stats = {}
        for item in items:
            channel_uid = item.get('channel_uid', 'unknown')
            channel_stats[channel_uid] = channel_stats.get(channel_uid, 0) + 1
        
        print("\n🎯 频道ID分布:")
        for channel_uid, count in sorted(channel_stats.items()):
            print(f"  {channel_uid}: {count} 条")
        
        # 按时间统计
        current_time = datetime.now()
        time_stats = {'1天内': 0, '7天内': 0, '30天内': 0, '更早': 0}
        
        for item in items:
            try:
                item_time = datetime.fromisoformat(item.get('timestamp', current_time.isoformat()))
                age_days = (current_time - item_time).days
                
                if age_days <= 1:
                    time_stats['1天内'] += 1
                elif age_days <= 7:
                    time_stats['7天内'] += 1
                elif age_days <= 30:
                    time_stats['30天内'] += 1
                else:
                    time_stats['更早'] += 1
            except:
                time_stats['更早'] += 1
        
        print("\n⏰ 时间分布:")
        for period, count in time_stats.items():
            print(f"  {period}: {count} 条")
        
        # 显示频道清理规则
        rules_str = os.getenv('SEEN_ITEMS_CHANNEL_RULES', '')
        if rules_str:
            print("\n🎯 频道清理规则:")
            for rule in rules_str.split(','):
                rule = rule.strip()
                if ':' in rule:
                    parts = rule.split(':')
                    if len(parts) == 3:
                        channel_id, max_count, max_days = parts
                        print(f"  {channel_id.strip()}: 保留{max_count.strip()}条记录，{max_days.strip()}天内")


def cleanup_by_days(days):
    """按天数清理"""
    data = load_seen_items()
    items = data.get('items', [])
    
    if not items:
        print("📋 没有记录需要清理")
        return
    
    current_time = datetime.now()
    cutoff_date = current_time - timedelta(days=days)
    
    cleaned_items = []
    for item in items:
        try:
            item_time = datetime.fromisoformat(item.get('timestamp', current_time.isoformat()))
            if item_time >= cutoff_date:
                cleaned_items.append(item)
        except:
            # 时间戳解析失败，保留记录
            cleaned_items.append(item)
    
    removed_count = len(items) - len(cleaned_items)
    
    if removed_count > 0:
        data['items'] = cleaned_items
        data['total_count'] = len(cleaned_items)
        data['last_update'] = current_time.isoformat()
        
        save_seen_items(data)
        print(f"🧹 清理完成: 删除了 {removed_count} 个超过 {days} 天的记录")
        print(f"📋 剩余记录: {len(cleaned_items)} 个")
    else:
        print(f"✅ 没有超过 {days} 天的记录需要清理")


def cleanup_by_count(max_count):
    """按数量清理，保留最新的记录"""
    data = load_seen_items()
    items = data.get('items', [])
    
    if len(items) <= max_count:
        print(f"✅ 记录数量 ({len(items)}) 未超过限制 ({max_count})，无需清理")
        return
    
    # 按时间戳排序，保留最新的记录
    items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    cleaned_items = items[:max_count]
    removed_count = len(items) - len(cleaned_items)
    
    data['items'] = cleaned_items
    data['total_count'] = len(cleaned_items)
    data['last_update'] = datetime.now().isoformat()
    
    save_seen_items(data)
    print(f"🧹 清理完成: 删除了 {removed_count} 个最旧的记录")
    print(f"📋 剩余记录: {len(cleaned_items)} 个")


def cleanup_by_channel(channel_uid, max_count=None, max_days=None):
    """按频道ID清理"""
    data = load_seen_items()
    items = data.get('items', [])
    
    if not items:
        print("📋 没有记录需要清理")
        return
    
    # 筛选出指定频道的记录
    channel_items = [item for item in items if item.get('channel_uid') == channel_uid]
    other_items = [item for item in items if item.get('channel_uid') != channel_uid]
    
    if not channel_items:
        print(f"📋 频道 {channel_uid} 没有记录")
        return
    
    print(f"📋 频道 {channel_uid} 当前有 {len(channel_items)} 条记录")
    
    current_time = datetime.now()
    cleaned_channel_items = channel_items[:]
    
    # 按时间清理
    if max_days and max_days > 0:
        cutoff_date = current_time - timedelta(days=max_days)
        cleaned_channel_items = []
        for item in channel_items:
            try:
                item_time = datetime.fromisoformat(item.get('timestamp', current_time.isoformat()))
                if item_time >= cutoff_date:
                    cleaned_channel_items.append(item)
            except:
                # 时间戳解析失败，保留记录
                cleaned_channel_items.append(item)
    
    # 按数量清理
    if max_count and max_count > 0 and len(cleaned_channel_items) > max_count:
        # 按时间戳排序，保留最新的记录
        cleaned_channel_items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        cleaned_channel_items = cleaned_channel_items[:max_count]
    
    removed_count = len(channel_items) - len(cleaned_channel_items)
    
    if removed_count > 0:
        # 合并其他频道的记录
        all_cleaned_items = other_items + cleaned_channel_items
        
        data['items'] = all_cleaned_items
        data['total_count'] = len(all_cleaned_items)
        data['last_update'] = current_time.isoformat()
        
        save_seen_items(data)
        print(f"🧹 频道 {channel_uid} 清理完成: 删除了 {removed_count} 个记录")
        print(f"📋 频道 {channel_uid} 剩余记录: {len(cleaned_channel_items)} 个")
        print(f"📋 总剩余记录: {len(all_cleaned_items)} 个")
    else:
        print(f"✅ 频道 {channel_uid} 无需清理")


def backup_file():
    """备份文件"""
    if not SEEN_ITEMS_FILE.exists():
        print("📋 seen_items.json 文件不存在，无法备份")
        return
    
    backup_name = f"seen_items_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    backup_path = DATA_DIR / backup_name
    
    data = load_seen_items()
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 备份已保存: {backup_path}")


def list_channels():
    """列出所有频道"""
    data = load_seen_items()
    items = data.get('items', [])
    
    if not items:
        print("📋 没有记录")
        return
    
    # 按频道ID统计
    channel_stats = {}
    current_time = datetime.now()
    
    for item in items:
        channel_uid = item.get('channel_uid', 'unknown')
        if channel_uid not in channel_stats:
            channel_stats[channel_uid] = {
                'count': 0,
                'latest': None,
                'oldest': None
            }
        
        channel_stats[channel_uid]['count'] += 1
        
        try:
            item_time = datetime.fromisoformat(item.get('timestamp', current_time.isoformat()))
            if not channel_stats[channel_uid]['latest'] or item_time > channel_stats[channel_uid]['latest']:
                channel_stats[channel_uid]['latest'] = item_time
            if not channel_stats[channel_uid]['oldest'] or item_time < channel_stats[channel_uid]['oldest']:
                channel_stats[channel_uid]['oldest'] = item_time
        except:
            pass
    
    print("🎯 频道列表:")
    print("=" * 60)
    for channel_uid, stats in sorted(channel_stats.items()):
        latest_str = stats['latest'].strftime('%Y-%m-%d %H:%M') if stats['latest'] else '未知'
        oldest_str = stats['oldest'].strftime('%Y-%m-%d %H:%M') if stats['oldest'] else '未知'
        print(f"📋 {channel_uid}: {stats['count']} 条记录")
        print(f"   最新: {latest_str} | 最旧: {oldest_str}")
        print()


def clear_all():
    """清空所有记录"""
    if not SEEN_ITEMS_FILE.exists():
        print("📋 seen_items.json 文件不存在")
        return
    
    confirm = input("⚠️ 确认要删除所有记录吗？这将导致所有微博重新推送！输入 'yes' 确认: ")
    if confirm.lower() != 'yes':
        print("❌ 操作已取消")
        return
    
    data = {
        'items': [],
        'last_update': datetime.now().isoformat(),
        'total_count': 0
    }
    
    save_seen_items(data)
    print("🗑️ 所有记录已清空")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="seen_items.json 管理工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 统计信息
    subparsers.add_parser('stats', help='显示统计信息')
    
    # 按天数清理
    cleanup_days = subparsers.add_parser('cleanup-days', help='按天数清理过期记录')
    cleanup_days.add_argument('days', type=int, help='保留最近N天的记录')
    
    # 按数量清理
    cleanup_count = subparsers.add_parser('cleanup-count', help='按数量清理，保留最新记录')
    cleanup_count.add_argument('count', type=int, help='最多保留N条记录')
    
    # 按频道清理
    cleanup_channel = subparsers.add_parser('cleanup-channel', help='按频道ID清理记录')
    cleanup_channel.add_argument('channel_uid', type=str, help='频道ID')
    cleanup_channel.add_argument('--count', type=int, help='最多保留N条记录')
    cleanup_channel.add_argument('--days', type=int, help='保留最近N天的记录')
    
    # 备份
    subparsers.add_parser('backup', help='备份当前文件')
    
    # 清空
    subparsers.add_parser('clear', help='清空所有记录（危险操作）')
    
    # 列出频道
    subparsers.add_parser('channels', help='列出所有频道及其记录数')
    
    args = parser.parse_args()
    
    if args.command == 'stats':
        show_stats()
    elif args.command == 'cleanup-days':
        cleanup_by_days(args.days)
    elif args.command == 'cleanup-count':
        cleanup_by_count(args.count)
    elif args.command == 'cleanup-channel':
        cleanup_by_channel(args.channel_uid, args.count, args.days)
    elif args.command == 'backup':
        backup_file()
    elif args.command == 'clear':
        clear_all()
    elif args.command == 'channels':
        list_channels()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
