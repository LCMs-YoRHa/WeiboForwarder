# -*- coding: utf-8 -*-
"""
基于RSS的微博长图生成器 - 命令行工具
通过RSS服务获取微博数据，生成美观的长图
"""

import argparse
from create import RSSWeiboParser, WeiboImageGenerator
from push import push_image_file


# 配置
RSS_URL = "http://68.64.177.186:1200/weibo/user/1935396210"  # 请修改为你的RSS服务地址

# 企业微信配置（默认为空，需要通过配置文件或命令行参数提供）
WECOM_CONFIG = {}

# 尝试从配置文件加载企业微信配置
try:
    from wecom_config import WECOM_CONFIG as USER_WECOM_CONFIG
    WECOM_CONFIG.update(USER_WECOM_CONFIG)
    print("✅ 已加载企业微信配置文件")
except ImportError:
    print("💡 提示：可以创建 wecom_config.py 文件来配置企业微信信息")
except Exception as e:
    print(f"⚠️ 加载企业微信配置失败: {e}")


def main():
    parser = argparse.ArgumentParser(description="基于RSS的微博长图生成器")
    parser.add_argument("--rss-url", default=RSS_URL, help="RSS源URL")
    parser.add_argument("--index", type=int, default=0, help="选择第几条微博 (从0开始)")
    parser.add_argument("--list", action="store_true", help="列出所有微博")
    parser.add_argument("--output", help="输出文件名")
    
    # 企业微信推送参数
    parser.add_argument("--push", action="store_true", help="推送到企业微信")
    parser.add_argument("--corpid", help="企业微信企业ID")
    parser.add_argument("--corpsecret", help="企业微信应用密钥")
    parser.add_argument("--agentid", type=int, help="企业微信应用ID")
    parser.add_argument("--touser", default="@all", help="接收者ID，多个用|分隔，默认@all")
    parser.add_argument("--toparty", default="", help="部门ID，多个用|分隔")
    parser.add_argument("--totag", default="", help="标签ID，多个用|分隔")
    
    args = parser.parse_args()
    
    print("🚀 基于RSS的微博长图生成器")
    print("="*50)
    
    # 获取RSS数据
    xml_content = RSSWeiboParser.fetch_rss_data(args.rss_url)
    if not xml_content:
        print("❌ 无法获取RSS数据")
        return
    
    # 解析RSS
    channel_info, weibo_items = RSSWeiboParser.parse_rss_xml(xml_content)
    if not weibo_items:
        print("❌ 未找到微博数据")
        return
    
    print(f"✅ 成功获取 {len(weibo_items)} 条微博")
    print(f"📝 频道: {channel_info.get('title', '未知')}")
    
    # 列出所有微博
    if args.list:
        print("\n📋 微博列表:")
        for i, item in enumerate(weibo_items):
            content_preview = item['content'][:50] + ('...' if len(item['content']) > 50 else '')
            image_count = len(item.get('image_urls', []))
            has_video = bool(item.get('video_info'))
            print(f"  {i}. {content_preview}")
            print(f"     图片: {image_count}张 | 视频: {'是' if has_video else '否'}")
            print(f"     时间: {item.get('pub_date', '')}")
            print()
        return
    
    # 选择要生成的微博
    if args.index >= len(weibo_items):
        print(f"❌ 索引超出范围，最大索引为 {len(weibo_items) - 1}")
        return
    
    selected_weibo = weibo_items[args.index]
    
    print(f"\n📝 选择的微博 (索引 {args.index}):")
    print(f"  内容: {selected_weibo['content'][:100]}...")
    print(f"  图片: {len(selected_weibo.get('image_urls', []))} 张")
    print(f"  视频: {'是' if selected_weibo.get('video_info') else '否'}")
    print(f"  时间: {selected_weibo.get('pub_date', '')}")
    
    # 生成长图
    print("\n🎨 开始生成长图...")
    generator = WeiboImageGenerator()
    output_file = generator.generate_screenshot(channel_info, selected_weibo, args.output)
    
    print(f"\n🎉 完成！长图已保存到: {output_file}")
    
    # 检查必需的企业微信参数
    corpid = args.corpid or WECOM_CONFIG.get('corpid')
    corpsecret = args.corpsecret or WECOM_CONFIG.get('corpsecret')
    agentid = args.agentid or WECOM_CONFIG.get('agentid')
    
    # 自动推送逻辑：如果有完整配置或显式指定了--push，则进行推送
    should_push = args.push or (corpid and corpsecret and agentid)
    
    if should_push:
        if not all([corpid, corpsecret, agentid]):
            print("⚠️ 企业微信推送参数不完整，跳过推送")
            print("💡 如需推送，请配置以下参数：")
            print("   - 在 wecom_config.py 中配置企业微信信息")
            print("   - 或使用命令行参数：--corpid --corpsecret --agentid")
        else:
            if corpid and corpsecret and agentid and not args.push:
                print("\n📤 检测到完整的企业微信配置，自动推送到企业微信...")
            else:
                print("\n📤 推送到企业微信...")
            
            # 推送图片
            success = push_image_file(
                output_file,
                corpid=corpid,
                corpsecret=corpsecret,
                agentid=agentid,
                touser=args.touser or WECOM_CONFIG.get('touser', '@all'),
                toparty=args.toparty,
                totag=args.totag
            )
            
            if not success:
                print("💡 提示：推送失败，请检查企业微信配置是否正确")
                print("   - 企业ID (corpid)")
                print("   - 应用密钥 (corpsecret)")
                print("   - 应用ID (agentid)")
                print("   - 应用是否有发送消息权限")
    else:
        print("\n💡 提示：如需推送到企业微信，请在 wecom_config.py 中配置企业微信信息，或添加 --push 参数")


if __name__ == "__main__":
    main()
