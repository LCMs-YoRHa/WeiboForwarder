# -*- coding: utf-8 -*-
"""
测试监听服务（加载.env配置）
"""

import os
import sys

def load_env_file(env_file='.env'):
    """加载.env文件中的环境变量"""
    if not os.path.exists(env_file):
        print(f"❌ 配置文件 {env_file} 不存在")
        return False
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        print(f"✅ 已加载配置文件 {env_file}")
        return True
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
        return False

if __name__ == "__main__":
    # 加载环境变量
    if not load_env_file():
        sys.exit(1)
    
    # 导入并运行监听服务
    from monitor import main
    main()
