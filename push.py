# -*- coding: utf-8 -*-
"""
企业微信推送模块
负责图片上传和消息推送功能
"""

import requests
import os
import time


class WeComNotifier:
    """企业微信通知器"""
    
    def __init__(self, corpid, corpsecret, agentid):
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.agentid = agentid
        self.access_token = None
        self.token_expires_time = 0
    
    def get_access_token(self):
        """获取访问令牌"""
        current_time = time.time()
        
        # 如果token还没过期，直接返回
        if self.access_token and current_time < self.token_expires_time:
            return self.access_token
        
        try:
            url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
            params = {
                'corpid': self.corpid,
                'corpsecret': self.corpsecret
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('errcode') == 0:
                self.access_token = data['access_token']
                self.token_expires_time = current_time + data['expires_in'] - 60  # 提前60秒过期
                print("✅ 企业微信访问令牌获取成功")
                return self.access_token
            else:
                print(f"❌ 获取访问令牌失败: {data.get('errmsg', '未知错误')}")
                return None
                
        except Exception as e:
            print(f"❌ 获取访问令牌异常: {e}")
            return None
    
    def upload_media(self, file_path):
        """上传临时素材"""
        access_token = self.get_access_token()
        if not access_token:
            return None
        
        try:
            url = f"https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type=image"
            
            with open(file_path, 'rb') as f:
                files = {'media': (os.path.basename(file_path), f, 'image/jpeg')}
                response = requests.post(url, files=files, timeout=30)
                response.raise_for_status()
                data = response.json()
            
            if data.get('errcode') == 0:
                media_id = data['media_id']
                print(f"✅ 图片上传成功，media_id: {media_id}")
                return media_id
            else:
                print(f"❌ 图片上传失败: {data.get('errmsg', '未知错误')}")
                return None
                
        except Exception as e:
            print(f"❌ 图片上传异常: {e}")
            return None
    
    def send_image_message(self, media_id, touser="@all", toparty="", totag=""):
        """发送图片消息"""
        access_token = self.get_access_token()
        if not access_token:
            return False
        
        try:
            url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
            
            data = {
                "touser": touser,
                "toparty": toparty,
                "totag": totag,
                "msgtype": "image",
                "agentid": self.agentid,
                "image": {
                    "media_id": media_id
                },
                "safe": 0,
                "enable_duplicate_check": 0,
                "duplicate_check_interval": 1800
            }
            
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('errcode') == 0:
                print("✅ 企业微信消息发送成功")
                return True
            else:
                print(f"❌ 消息发送失败: {result.get('errmsg', '未知错误')}")
                return False
                
        except Exception as e:
            print(f"❌ 消息发送异常: {e}")
            return False
    
    def push_image(self, image_path, touser="@all", toparty="", totag=""):
        """推送图片（完整流程）"""
        print("📤 开始推送到企业微信...")
        
        # 1. 上传图片
        print("📎 上传图片到企业微信...")
        media_id = self.upload_media(image_path)
        if not media_id:
            return False
        
        # 2. 发送消息
        print("📢 发送图片消息...")
        success = self.send_image_message(media_id, touser, toparty, totag)
        
        if success:
            print("🎉 推送完成！")
        else:
            print("💥 推送失败！")
        
        return success


def create_notifier_from_config():
    """从配置文件创建通知器"""
    try:
        from wecom_config import WECOM_CONFIG
        corpid = WECOM_CONFIG.get('corpid')
        corpsecret = WECOM_CONFIG.get('corpsecret') 
        agentid = WECOM_CONFIG.get('agentid')
        
        if not all([corpid, corpsecret, agentid]):
            return None
            
        return WeComNotifier(corpid, corpsecret, agentid)
    except ImportError:
        return None
    except Exception as e:
        print(f"⚠️ 创建推送器失败: {e}")
        return None


def push_image_file(image_path, corpid=None, corpsecret=None, agentid=None, 
                   touser="@all", toparty="", totag=""):
    """推送图片文件的便捷函数"""
    # 优先使用传入的参数
    if all([corpid, corpsecret, agentid]):
        notifier = WeComNotifier(corpid, corpsecret, agentid)
    else:
        # 尝试从配置文件创建
        notifier = create_notifier_from_config()
        if not notifier:
            print("❌ 无法创建企业微信推送器：缺少配置信息")
            return False
    
    success = notifier.push_image(image_path, touser, toparty, totag)
    
    # 如果推送成功，标记图片用于后续清理
    if success:
        try:
            from cleanup import mark_image_pushed
            mark_image_pushed(image_path)
        except Exception as e:
            print(f"⚠️ 标记图片清理失败: {e}")
    
    return success
