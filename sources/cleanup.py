# -*- coding: utf-8 -*-
"""
自动清理脚本 - 清理推送成功后的图片（1天后自动删除）和seen_items.json的过期记录
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging

# 配置
OUTPUTS_DIR = Path("/app/outputs") if os.path.exists("/app/outputs") else Path("./outputs")
DATA_DIR = Path("./data") if os.path.exists("./data") else Path("/app/data") if os.path.exists("/app/data") else Path("./data")
CLEANUP_LOG_FILE = DATA_DIR / "cleanup.json"
SEEN_ITEMS_FILE = DATA_DIR / "seen_items.json"
CLEANUP_AFTER_DAYS = 1  # 推送成功后几天删除图片

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ImageCleanupManager:
    """图片清理管理器"""
    
    def __init__(self):
        self.cleanup_data = self.load_cleanup_data()
    
    def load_cleanup_data(self):
        """加载清理数据"""
        try:
            if CLEANUP_LOG_FILE.exists():
                with open(CLEANUP_LOG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"pushed_images": {}, "last_cleanup": None}
        except Exception as e:
            logger.error(f"加载清理数据失败: {e}")
            return {"pushed_images": {}, "last_cleanup": None}
    
    def save_cleanup_data(self):
        """保存清理数据"""
        try:
            DATA_DIR.mkdir(exist_ok=True)
            with open(CLEANUP_LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.cleanup_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存清理数据失败: {e}")
    
    def mark_image_pushed(self, image_path):
        """标记图片已推送"""
        try:
            abs_path = str(Path(image_path).resolve())
            push_time = datetime.now().isoformat()
            
            self.cleanup_data["pushed_images"][abs_path] = {
                "push_time": push_time,
                "file_size": os.path.getsize(image_path) if os.path.exists(image_path) else 0
            }
            
            self.save_cleanup_data()
            logger.info(f"✅ 标记图片已推送: {image_path}")
            
        except Exception as e:
            logger.error(f"标记图片失败: {e}")
    
    def cleanup_old_images(self):
        """清理旧图片"""
        try:
            current_time = datetime.now()
            deleted_count = 0
            total_size_freed = 0
            
            # 获取需要清理的图片列表
            images_to_delete = []
            
            for image_path, info in self.cleanup_data["pushed_images"].items():
                try:
                    push_time = datetime.fromisoformat(info["push_time"])
                    age_days = (current_time - push_time).days
                    
                    if age_days >= CLEANUP_AFTER_DAYS:
                        images_to_delete.append((image_path, info))
                        
                except Exception as e:
                    logger.warning(f"解析推送时间失败 {image_path}: {e}")
                    # 如果解析失败，也加入删除列表（可能是格式错误的数据）
                    images_to_delete.append((image_path, info))
            
            # 执行删除
            for image_path, info in images_to_delete:
                try:
                    if os.path.exists(image_path):
                        file_size = os.path.getsize(image_path)
                        os.remove(image_path)
                        total_size_freed += file_size
                        deleted_count += 1
                        logger.info(f"🗑️ 删除旧图片: {image_path}")
                    
                    # 从记录中移除
                    del self.cleanup_data["pushed_images"][image_path]
                    
                except Exception as e:
                    logger.error(f"删除图片失败 {image_path}: {e}")
            
            # 更新最后清理时间
            self.cleanup_data["last_cleanup"] = current_time.isoformat()
            self.save_cleanup_data()
            
            # 输出清理统计
            if deleted_count > 0:
                size_mb = total_size_freed / (1024 * 1024)
                logger.info(f"🧹 清理完成: 删除了 {deleted_count} 个文件，释放了 {size_mb:.2f}MB 空间")
            else:
                logger.info("✅ 清理完成: 没有需要删除的文件")
            
            return deleted_count, total_size_freed
            
        except Exception as e:
            logger.error(f"清理过程失败: {e}")
            return 0, 0
    
    def cleanup_orphaned_images(self):
        """清理孤儿图片（存在于文件系统但不在记录中的旧图片）"""
        try:
            if not OUTPUTS_DIR.exists():
                return 0, 0
            
            current_time = datetime.now()
            deleted_count = 0
            total_size_freed = 0
            
            # 获取所有图片文件
            image_files = list(OUTPUTS_DIR.glob("*.jpg")) + list(OUTPUTS_DIR.glob("*.png"))
            
            for image_file in image_files:
                try:
                    # 检查文件修改时间
                    file_mtime = datetime.fromtimestamp(image_file.stat().st_mtime)
                    age_days = (current_time - file_mtime).days
                    
                    # 检查是否在推送记录中
                    abs_path = str(image_file.resolve())
                    in_records = abs_path in self.cleanup_data["pushed_images"]
                    
                    # 如果文件超过3天且不在记录中，则删除（可能是测试文件或失败的生成）
                    if age_days >= 3 and not in_records:
                        file_size = image_file.stat().st_size
                        image_file.unlink()
                        total_size_freed += file_size
                        deleted_count += 1
                        logger.info(f"🗑️ 删除孤儿图片: {image_file}")
                        
                except Exception as e:
                    logger.warning(f"处理文件失败 {image_file}: {e}")
            
            if deleted_count > 0:
                size_mb = total_size_freed / (1024 * 1024)
                logger.info(f"🧹 孤儿清理完成: 删除了 {deleted_count} 个文件，释放了 {size_mb:.2f}MB 空间")
            
            return deleted_count, total_size_freed
            
        except Exception as e:
            logger.error(f"孤儿清理失败: {e}")
            return 0, 0
    
    def get_cleanup_stats(self):
        """获取清理统计信息"""
        try:
            stats = {
                "tracked_images": len(self.cleanup_data["pushed_images"]),
                "last_cleanup": self.cleanup_data.get("last_cleanup"),
                "pending_cleanup": 0,
                "total_size": 0
            }
            
            current_time = datetime.now()
            
            for image_path, info in self.cleanup_data["pushed_images"].items():
                try:
                    push_time = datetime.fromisoformat(info["push_time"])
                    age_days = (current_time - push_time).days
                    
                    if age_days >= CLEANUP_AFTER_DAYS:
                        stats["pending_cleanup"] += 1
                    
                    if os.path.exists(image_path):
                        stats["total_size"] += os.path.getsize(image_path)
                        
                except Exception:
                    continue
            
            return stats
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}


def mark_image_pushed(image_path):
    """标记图片已推送（供外部调用）"""
    manager = ImageCleanupManager()
    manager.mark_image_pushed(image_path)

def run_cleanup():
    """运行清理任务"""
    logger.info("🧹 开始自动清理任务...")
    
    manager = ImageCleanupManager()
    
    # 显示清理前统计
    stats = manager.get_cleanup_stats()
    logger.info(f"📊 清理前统计: 跟踪图片 {stats.get('tracked_images', 0)} 个，"
                f"待清理 {stats.get('pending_cleanup', 0)} 个，"
                f"总大小 {stats.get('total_size', 0) / (1024*1024):.2f}MB")
    
    # 清理已推送的旧图片
    deleted1, size1 = manager.cleanup_old_images()
    
    # 清理孤儿图片
    deleted2, size2 = manager.cleanup_orphaned_images()
    
    # 清理seen_items.json
    cleaned_seen_items = cleanup_seen_items()
    
    # 总计
    total_deleted = deleted1 + deleted2
    total_size = (size1 + size2) / (1024 * 1024)
    
    logger.info(f"🎉 清理任务完成: 删除图片 {total_deleted} 个，释放 {total_size:.2f}MB 空间，清理seen_items {cleaned_seen_items} 个")
    
    return {
        'deleted_images': total_deleted,
        'freed_size_mb': total_size,
        'cleaned_seen_items': cleaned_seen_items
    }

def cleanup_seen_items():
    """清理seen_items.json中的过期记录（每个频道最多保留50条）"""
    try:
        if not SEEN_ITEMS_FILE.exists():
            logger.info("📋 seen_items.json 文件不存在，跳过清理")
            return 0
        
        # 读取配置
        max_count_per_channel = int(os.getenv('SEEN_ITEMS_MAX_COUNT_PER_CHANNEL', 50))
        
        # 加载seen_items数据
        with open(SEEN_ITEMS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 兼容旧格式和新格式
        if isinstance(data, dict) and 'items' in data:
            # 新格式：{'items': [{'id': 'xxx', 'timestamp': 'xxx', 'channel_uid': 'xxx'}]}
            items_data = data.get('items', [])
        else:
            # 旧格式：{'seen_items': ['id1', 'id2'], 'last_update': 'xxx'} 或 ['id1', 'id2']
            old_items = data.get('seen_items', data) if isinstance(data, dict) else data
            if isinstance(old_items, list):
                # 为旧数据补充时间戳和频道信息
                current_time = datetime.now()
                items_data = [{
                    'id': item_id,
                    'timestamp': current_time.isoformat(),
                    'rss_url': 'unknown',
                    'channel_uid': 'unknown'
                } for item_id in old_items]
            else:
                items_data = []
        
        initial_count = len(items_data)
        logger.info(f"📋 开始清理seen_items，当前记录数: {initial_count}")
        
        if initial_count == 0:
            return 0
        
        # 按频道ID分组
        items_by_channel = {}
        for item in items_data:
            channel_uid = item.get('channel_uid', 'unknown')
            if channel_uid not in items_by_channel:
                items_by_channel[channel_uid] = []
            items_by_channel[channel_uid].append(item)
        
        # 对每个频道只保留最新的N条记录
        cleaned_items = []
        channel_stats = {}
        
        for channel_uid, channel_items in items_by_channel.items():
            original_count = len(channel_items)
            
            # 按时间戳排序，保留最新的记录
            channel_items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # 只保留最新的N条记录
            kept_items = channel_items[:max_count_per_channel]
            removed_from_channel = original_count - len(kept_items)
            
            if removed_from_channel > 0:
                channel_stats[channel_uid] = {
                    'removed': removed_from_channel,
                    'remaining': len(kept_items)
                }
            
            # 添加到清理后的列表
            cleaned_items.extend(kept_items)
        
        removed_count = initial_count - len(cleaned_items)
        
        if removed_count > 0:
            # 保存清理后的数据
            new_data = {
                'items': cleaned_items,
                'last_update': datetime.now().isoformat(),
                'total_count': len(cleaned_items),
                'last_cleanup': datetime.now().isoformat(),
                'cleaned_count': removed_count,
                'channel_stats': channel_stats
            }
            
            with open(SEEN_ITEMS_FILE, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"🧹 seen_items清理完成: 删除了 {removed_count} 个旧记录，剩余 {len(cleaned_items)} 个")
            for channel_uid, stats in channel_stats.items():
                logger.info(f"   📋 频道 {channel_uid}: 删除 {stats['removed']} 个，保留 {stats['remaining']} 个")
        else:
            logger.info(f"✅ seen_items无需清理，当前记录数: {len(cleaned_items)}")
        
        return removed_count
        
    except Exception as e:
        logger.error(f"⚠️ 清理seen_items失败: {e}")
        return 0


