# -*- coding: utf-8 -*-
"""
微博RSS实时监听服务
支持多个RSS地址监听，发现更新时自动生成长图并推送到企业微信
"""

import os
import time
import logging
import hashlib
import json
from datetime import datetime, timedelta
from typing import List, Dict, Set, Optional
from create import RSSWeiboParser, WeiboImageGenerator
from push import push_image_file


class Config:
    """配置管理类"""
    
    def __init__(self):
        # RSS监听配置
        self.rss_urls = self._get_env_list('RSS_URLS', [])
        self.check_interval = int(os.getenv('CHECK_INTERVAL', 300))  # 默认5分钟
        
        # 企业微信配置
        self.wecom_corpid = os.getenv('WECOM_CORPID', '')
        self.wecom_corpsecret = os.getenv('WECOM_CORPSECRET', '')
        self.wecom_agentid = int(os.getenv('WECOM_AGENTID', 0)) if os.getenv('WECOM_AGENTID') else None
        self.wecom_touser = os.getenv('WECOM_TOUSER', '@all')
        self.wecom_toparty = os.getenv('WECOM_TOPARTY', '')
        self.wecom_totag = os.getenv('WECOM_TOTAG', '')
        
        # seen_items.json 清理配置
        self.seen_items_max_count_per_channel = int(os.getenv('SEEN_ITEMS_MAX_COUNT_PER_CHANNEL', 50))
        self.seen_items_cleanup_interval = int(os.getenv('SEEN_ITEMS_CLEANUP_INTERVAL', 7))
        
        # 其他配置
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.max_retries = int(os.getenv('MAX_RETRIES', 3))
        self.timeout = int(os.getenv('TIMEOUT', 30))
        
        # 数据目录
        self.output_dir = '/app/outputs'
        self.log_dir = '/app/logs'
        self.data_dir = '/app/data'
        
        # 确保目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _get_env_list(self, key: str, default: List[str]) -> List[str]:
        """从环境变量获取列表"""
        value = os.getenv(key, '')
        if not value:
            return default
        return [item.strip() for item in value.split(',') if item.strip()]
    
    def is_wecom_configured(self) -> bool:
        """检查企业微信是否配置完整"""
        return bool(self.wecom_corpid and self.wecom_corpsecret and self.wecom_agentid)
    
    def validate(self) -> bool:
        """验证配置"""
        if not self.rss_urls:
            logging.error("❌ 未配置RSS地址，请设置 RSS_URLS 环境变量")
            return False
        
        if not self.is_wecom_configured():
            logging.warning("⚠️ 企业微信配置不完整，将跳过推送功能")
        
        return True


class WeiboMonitor:
    """微博RSS监听器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.seen_items: Set[str] = set()
        self.seen_items_with_time: Dict[str, Dict] = {}  # 新增：保存item的时间戳和RSS源信息
        self.rss_parser = RSSWeiboParser()
        self.image_generator = WeiboImageGenerator()
        
        # 加载已见过的微博ID
        self._load_seen_items()
        
        # seen_items清理计数器
        self.seen_cleanup_counter = 0
        
        # 设置日志
        self._setup_logging()
    
    def _setup_logging(self):
        """设置日志"""
        log_file = os.path.join(self.config.log_dir, 'weibo_monitor.log')
        
        # 配置根日志记录器
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def _load_seen_items(self):
        """加载已见过的微博ID"""
        seen_file = os.path.join(self.config.data_dir, 'seen_items.json')
        try:
            if os.path.exists(seen_file):
                with open(seen_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 支持新的数据结构（包含时间戳）和旧的数据结构（只有ID列表）
                    if isinstance(data, dict) and 'items' in data:
                        # 新格式：{'items': [{'id': 'xxx', 'timestamp': 'xxx', 'rss_url': 'xxx'}], 'last_update': 'xxx'}
                        items_data = data.get('items', [])
                        self.seen_items = set(item['id'] for item in items_data if isinstance(item, dict) and 'id' in item)
                        self.seen_items_with_time = {item['id']: {
                            'timestamp': item.get('timestamp', datetime.now().isoformat()),
                            'rss_url': item.get('rss_url', 'unknown'),
                            'channel_uid': item.get('channel_uid', 'unknown')
                        } for item in items_data if isinstance(item, dict) and 'id' in item}
                    else:
                        # 旧格式：{'seen_items': ['id1', 'id2'], 'last_update': 'xxx'} 或 ['id1', 'id2']
                        old_items = data.get('seen_items', data) if isinstance(data, dict) else data
                        self.seen_items = set(old_items) if isinstance(old_items, list) else set()
                        # 为旧数据补充时间戳和频道信息
                        self.seen_items_with_time = {item_id: {
                            'timestamp': datetime.now().isoformat(),
                            'rss_url': 'unknown',
                            'channel_uid': 'unknown'
                        } for item_id in self.seen_items}
                logging.info(f"✅ 加载了 {len(self.seen_items)} 个已处理的微博ID")
        except Exception as e:
            logging.error(f"⚠️ 加载已见微博ID失败: {e}")
            self.seen_items = set()
            self.seen_items_with_time = {}
    
    def _save_seen_items(self):
        """保存已见过的微博ID"""
        seen_file = os.path.join(self.config.data_dir, 'seen_items.json')
        try:
            # 使用新的数据结构保存
            items_data = []
            for item_id in self.seen_items:
                item_info = self.seen_items_with_time.get(item_id, {
                    'timestamp': datetime.now().isoformat(),
                    'rss_url': 'unknown'
                })
                items_data.append({
                    'id': item_id,
                    'timestamp': item_info['timestamp'],
                    'rss_url': item_info['rss_url'],
                    'channel_uid': item_info.get('channel_uid', 'unknown')
                })
            
            data = {
                'items': items_data,
                'last_update': datetime.now().isoformat(),
                'total_count': len(items_data)
            }
            
            with open(seen_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"⚠️ 保存已见微博ID失败: {e}")
    
    def _cleanup_seen_items(self):
        """清理过期的seen_items记录（每个频道最多保留指定条数）"""
        try:
            initial_count = len(self.seen_items)
            if initial_count == 0:
                return False
            
            cleaned_items = set()
            cleaned_items_with_time = {}
            
            # 按频道ID分组
            items_by_channel = {}
            for item_id in self.seen_items:
                item_info = self.seen_items_with_time.get(item_id, {})
                channel_uid = item_info.get('channel_uid', 'unknown')
                if channel_uid not in items_by_channel:
                    items_by_channel[channel_uid] = []
                items_by_channel[channel_uid].append((item_id, item_info))
            
            # 对每个频道只保留最新的N条记录
            for channel_uid, channel_items in items_by_channel.items():
                # 按时间戳排序，保留最新的记录
                channel_items.sort(key=lambda x: x[1].get('timestamp', ''), reverse=True)
                
                # 只保留最新的N条记录
                max_count = self.config.seen_items_max_count_per_channel
                kept_items = channel_items[:max_count]
                
                # 添加到清理后的集合
                for item_id, item_info in kept_items:
                    cleaned_items.add(item_id)
                    cleaned_items_with_time[item_id] = item_info
                
                # 记录清理情况
                removed_from_channel = len(channel_items) - len(kept_items)
                if removed_from_channel > 0:
                    logging.info(f"🧹 频道 {channel_uid}: 删除了 {removed_from_channel} 个旧记录，保留 {len(kept_items)} 个")
            
            # 更新数据
            removed_count = initial_count - len(cleaned_items)
            if removed_count > 0:
                self.seen_items = cleaned_items
                self.seen_items_with_time = cleaned_items_with_time
                logging.info(f"🧹 seen_items清理完成: 总共删除 {removed_count} 个记录，剩余 {len(cleaned_items)} 个")
                return True
            else:
                logging.info(f"✅ seen_items无需清理，当前记录数: {len(cleaned_items)}")
                return False
                
        except Exception as e:
            logging.error(f"⚠️ 清理seen_items失败: {e}")
            return False
    
    def _extract_channel_uid(self, channel_info, rss_url):
        """提取频道UID"""
        try:
            # 方法1：从频道链接中提取UID
            link = channel_info.get('link', '')
            if '/u/' in link:
                # 格式：https://weibo.com/u/1234567890
                uid = link.split('/u/')[-1].split('?')[0].split('/')[0]
                return uid[:10]  # 限制长度
            elif 'weibo.com/' in link:
                # 其他格式尝试提取数字ID
                import re
                numbers = re.findall(r'\d+', link)
                if numbers:
                    return numbers[0][:10]
            
            # 方法2：从RSS URL中提取
            if '/weibo/user/' in rss_url:
                import re
                match = re.search(r'/weibo/user/(\w+)', rss_url)
                if match:
                    return match.group(1)[:10]
            
            # 方法3：如果无法提取，使用频道标题的哈希
            title = channel_info.get('title', 'unknown')
            return str(abs(hash(title)))[:8]
        except:
            return "unknown"
    
    def _generate_item_id(self, rss_url: str, item: Dict) -> str:
        """生成微博项目的唯一ID"""
        # 使用RSS URL、发布时间和内容的哈希作为唯一标识
        content = f"{rss_url}_{item.get('pub_date', '')}_{item.get('content', '')[:100]}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _check_rss_updates(self, rss_url: str) -> List[Dict]:
        """检查单个RSS地址的更新"""
        try:
            logging.info(f"🔍 检查RSS更新: {rss_url}")
            
            # 获取RSS数据
            xml_content = self.rss_parser.fetch_rss_data(rss_url)
            if not xml_content:
                logging.warning(f"⚠️ 无法获取RSS数据: {rss_url}")
                return []
            
            # 解析RSS
            channel_info, weibo_items = self.rss_parser.parse_rss_xml(xml_content)
            if not weibo_items:
                logging.warning(f"⚠️ RSS中未找到微博数据: {rss_url}")
                return []
            
            # 检查新微博
            new_items = []
            for item in weibo_items:
                item_id = self._generate_item_id(rss_url, item)
                if item_id not in self.seen_items:
                    # 添加RSS源信息
                    item['rss_url'] = rss_url
                    item['channel_info'] = channel_info
                    item['item_id'] = item_id
                    new_items.append(item)
                    self.seen_items.add(item_id)
                    # 提取频道ID并保存时间戳和RSS源信息
                    channel_uid = self._extract_channel_uid(channel_info, rss_url)
                    self.seen_items_with_time[item_id] = {
                        'timestamp': datetime.now().isoformat(),
                        'rss_url': rss_url,
                        'channel_uid': channel_uid
                    }
            
            if new_items:
                logging.info(f"🆕 发现 {len(new_items)} 条新微博: {rss_url}")
            
            return new_items
            
        except Exception as e:
            logging.error(f"❌ 检查RSS更新失败 {rss_url}: {e}")
            return []
    
    def _process_new_weibo(self, item: Dict) -> Optional[str]:
        """处理新微博，生成长图"""
        try:
            rss_url = item['rss_url']
            channel_info = item['channel_info']
            
            logging.info(f"🎨 开始处理新微博: {item.get('content', '')[:50]}...")
            
            # 生成长图（使用新的规范命名）
            output_file = self.image_generator.generate_screenshot(
                channel_info, 
                item
            )
            
            logging.info(f"✅ 长图生成成功: {output_file}")
            return output_file
            
        except Exception as e:
            logging.error(f"❌ 处理新微博失败: {e}")
            return None
    
    def _push_to_wecom(self, image_file: str, item: Dict) -> bool:
        """推送到企业微信"""
        if not self.config.is_wecom_configured():
            logging.warning("⚠️ 企业微信未配置，跳过推送")
            return False
        
        try:
            logging.info(f"📤 推送到企业微信: {image_file}")
            
            success = push_image_file(
                image_file,
                corpid=self.config.wecom_corpid,
                corpsecret=self.config.wecom_corpsecret,
                agentid=self.config.wecom_agentid,
                touser=self.config.wecom_touser,
                toparty=self.config.wecom_toparty,
                totag=self.config.wecom_totag
            )
            
            if success:
                logging.info("✅ 企业微信推送成功")
            else:
                logging.error("❌ 企业微信推送失败")
            
            return success
            
        except Exception as e:
            logging.error(f"❌ 企业微信推送异常: {e}")
            return False
    
    def run_once(self):
        """执行一次监听检查"""
        logging.info("🔄 开始检查所有RSS源...")
        
        total_new_items = 0
        
        for rss_url in self.config.rss_urls:
            try:
                # 检查RSS更新
                new_items = self._check_rss_updates(rss_url)
                total_new_items += len(new_items)
                
                # 处理每个新微博
                for item in new_items:
                    # 生成长图
                    image_file = self._process_new_weibo(item)
                    if image_file:
                        # 推送到企业微信
                        self._push_to_wecom(image_file, item)
                
                # 短暂延迟，避免请求过于频繁
                if new_items:
                    time.sleep(2)
                    
            except Exception as e:
                logging.error(f"❌ 处理RSS源失败 {rss_url}: {e}")
        
        # 保存已见过的微博ID
        self._save_seen_items()
        
        if total_new_items > 0:
            logging.info(f"✅ 本次检查完成，处理了 {total_new_items} 条新微博")
        else:
            logging.info("✅ 本次检查完成，无新微博")
    
    def run(self):
        """启动监听服务"""
        logging.info("🚀 微博RSS监听服务启动")
        logging.info(f"📋 监听RSS源: {len(self.config.rss_urls)} 个")
        logging.info(f"⏰ 检查间隔: {self.config.check_interval} 秒")
        logging.info(f"📤 企业微信推送: {'已配置' if self.config.is_wecom_configured() else '未配置'}")
        
        # 清理计数器
        cleanup_counter = 0
        cleanup_interval = 24  # 每24次检查（大约一天）运行一次清理
        
        # seen_items清理间隔（根据配置，默认每7天清理一次）
        seen_cleanup_interval = max(1, self.config.seen_items_cleanup_interval * 24)  # 转换为检查次数
        
        try:
            while True:
                self.run_once()
                
                # 定期运行清理任务
                cleanup_counter += 1
                if cleanup_counter >= cleanup_interval:
                    try:
                        logging.info("🧹 开始定期清理任务...")
                        from cleanup import run_cleanup
                        run_cleanup()
                        cleanup_counter = 0
                    except Exception as e:
                        logging.error(f"⚠️ 清理任务失败: {e}")
                
                # 定期清理seen_items
                self.seen_cleanup_counter += 1
                if self.seen_cleanup_counter >= seen_cleanup_interval:
                    try:
                        logging.info("🧹 开始清理seen_items...")
                        if self._cleanup_seen_items():
                            self._save_seen_items()
                        self.seen_cleanup_counter = 0
                    except Exception as e:
                        logging.error(f"⚠️ seen_items清理失败: {e}")
                
                # 等待下次检查
                logging.info(f"⏳ 等待 {self.config.check_interval} 秒后进行下次检查...")
                time.sleep(self.config.check_interval)
                
        except KeyboardInterrupt:
            logging.info("👋 收到停止信号，正在关闭监听服务...")
        except Exception as e:
            logging.error(f"❌ 监听服务异常: {e}")
            raise


def main():
    """主函数"""
    print("🚀 微博RSS实时监听服务")
    print("=" * 50)
    
    # 加载配置
    config = Config()
    
    # 验证配置
    if not config.validate():
        print("❌ 配置验证失败，服务无法启动")
        return 1
    
    # 启动监听服务
    monitor = WeiboMonitor(config)
    monitor.run()
    
    return 0


if __name__ == "__main__":
    exit(main())
