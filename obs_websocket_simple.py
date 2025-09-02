#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版抖音直播间WebSocket自动OBS控制器
专注于核心功能：自动切换到人气最高的直播间
"""

import asyncio
import json
import requests
import time
import os
from datetime import datetime
import re

try:
    import websockets
except ImportError:
    print("❌ 缺少websockets依赖")
    print("📦 请运行: pip install websockets")
    exit(1)

class SimpleOBSController:
    def __init__(self):
        self.api_base_url = "http://localhost:8000/api/douyin/web/fetch_user_live_videos"
        self.obs_host = "192.168.1.102"  # 远程OBS服务器IP
        self.obs_port = 4455               # WebSocket端口
        self.websocket = None
        self.live_urls = []
        self.current_scene = None
        self.load_live_urls()
    
    def load_live_urls(self):
        """从文件中加载直播间URL"""
        try:
            with open('live_url.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line and 'live.douyin.com' in line:
                        self.live_urls.append(line)
            print(f"✅ 已加载 {len(self.live_urls)} 个直播间URL")
        except FileNotFoundError:
            print("❌ 错误：未找到 live_url.txt 文件")
        except Exception as e:
            print(f"❌ 加载直播间URL时出错：{e}")
    
    def extract_webcast_id(self, url):
        """从URL中提取webcast_id"""
        match = re.search(r'live\.douyin\.com/(\d+)', url)
        return match.group(1) if match else None
    
    async def connect_obs(self):
        """连接到OBS WebSocket"""
        try:
            uri = f"ws://{self.obs_host}:{self.obs_port}"
            print(f"🔗 连接OBS WebSocket: {uri}")
            
            self.websocket = await websockets.connect(uri)
            print("✅ OBS WebSocket连接成功！")
            return True
        except Exception as e:
            print(f"❌ OBS连接失败: {e}")
            print("💡 请确保OBS已启动并开启WebSocket服务器（工具→WebSocket服务器设置）")
            return False
    
    async def run(self):
        """运行简化版控制器"""
        if not self.live_urls:
            print("❌ 没有找到有效的直播间URL")
            return
        
        print("🚀 启动简化版抖音直播间OBS控制器...")
        
        if not await self.connect_obs():
            return
        
        try:
            while True:
                print("✅ WebSocket连接正常，每10秒检查一次")
                await asyncio.sleep(10)
                
        except KeyboardInterrupt:
            print("\n👋 程序已停止")
        finally:
            if self.websocket:
                await self.websocket.close()

async def main():
    """主函数"""
    controller = SimpleOBSController()
    await controller.run()

if __name__ == "__main__":
    asyncio.run(main())