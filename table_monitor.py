#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音直播间表格监控工具（实时更新版）
"""

import requests
import time
import os
from datetime import datetime

class DouyinTableMonitor:
    def __init__(self):
        self.api_base_url = "http://localhost/api/douyin/web/fetch_user_live_videos"
        self.webcast_ids = ['27356915698', '847308587035', '858106419879']
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_live_info(self, webcast_id):
        try:
            url = f"{self.api_base_url}?webcast_id={webcast_id}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['code'] == 200 and data['data']['data']['data']:
                    live_data = data['data']['data']['data'][0]
                    user_info = data['data']['data']['user']
                    
                    user_count_str = live_data['user_count_str']
                    try:
                        if '+' in user_count_str:
                            user_count = int(user_count_str.replace('+', ''))
                            user_count_display = f"{user_count:,}+"
                        else:
                            user_count = int(user_count_str)
                            user_count_display = f"{user_count:,}"
                    except ValueError:
                        user_count = 0
                        user_count_display = "--"
                    
                    return {
                        'success': True,
                        'webcast_id': webcast_id,
                        'nickname': user_info['nickname'],
                        'title': live_data['title'],
                        'user_count': user_count,
                        'user_count_display': user_count_display,
                        'status': live_data['status']
                    }
            
            return {'success': False, 'webcast_id': webcast_id, 'error': '获取失败'}
        except Exception as e:
            return {'success': False, 'webcast_id': webcast_id, 'error': '连接失败'}
    
    def run(self):
        print("🚀 启动抖音直播间表格监控...")
        
        try:
            while True:
                live_infos = []
                
                for webcast_id in self.webcast_ids:
                    info = self.get_live_info(webcast_id)
                    live_infos.append(info)
                
                live_infos.sort(key=lambda x: x.get('user_count', 0) if x['success'] else -1, reverse=True)
                
                self.clear_screen()
                print("🎬 抖音直播间实时监控")
                print(f"📅 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("-" * 80)
                
                for i, info in enumerate(live_infos, 1):
                    if info['success']:
                        status = "🔴直播" if info['status'] == 2 else "⚪未播"
                        print(f"{i}. {status} {info['nickname'][:15]:15} - {info['user_count_display']:>8}人")
                    else:
                        print(f"{i}. ❌ 错误 {info['webcast_id'][:15]:15} - --")
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n👋 监控已停止")

if __name__ == "__main__":
    monitor = DouyinTableMonitor()
    monitor.run()