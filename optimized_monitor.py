#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音直播间优化对齐监控工具
专门优化表格显示效果，确保所有内容完美对齐
"""

import requests
import time
import os
from datetime import datetime

class OptimizedDouyinMonitor:
    def __init__(self):
        self.api_base_url = "http://localhost:8000/api/douyin/web/fetch_user_live_videos"
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
                    
                    # 获取最精确的在线人数
                    accurate_count_str = None
                    
                    # stats字段优先
                    if 'stats' in live_data and isinstance(live_data['stats'], dict):
                        stats_count = live_data['stats'].get('user_count_str')
                        if stats_count and stats_count.strip():
                            accurate_count_str = str(stats_count).strip()
                    
                    # room_view_stats备用
                    if not accurate_count_str and 'room_view_stats' in live_data:
                        if isinstance(live_data['room_view_stats'], dict):
                            display_value = live_data['room_view_stats'].get('display_value')
                            if display_value is not None:
                                accurate_count_str = str(display_value)
                    
                    # 主字段最后
                    if not accurate_count_str:
                        accurate_count_str = live_data.get('user_count_str', '0')
                    
                    try:
                        if '+' in accurate_count_str:
                            clean_str = accurate_count_str.replace('+', '')
                            user_count = int(clean_str)
                            user_count_display = f"{user_count}"
                        else:
                            user_count = int(accurate_count_str)
                            user_count_display = f"{user_count}"
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
            
            return {'success': False, 'webcast_id': webcast_id, 'error': '直播间关闭'}
        except Exception as e:
            return {'success': False, 'webcast_id': webcast_id, 'error': '连接失败'}
    
    def run(self):
        print("🚀 启动抖音直播间优化监控...")
        
        try:
            while True:
                live_infos = []
                
                for webcast_id in self.webcast_ids:
                    info = self.get_live_info(webcast_id)
                    live_infos.append(info)
                
                live_infos.sort(key=lambda x: x.get('user_count', 0) if x['success'] else -1, reverse=True)
                
                self.clear_screen()
                print("🎬 抖音直播间优化监控 - 完美对齐版")
                print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("-" * 80)
                
                for i, info in enumerate(live_infos, 1):
                    if info['success']:
                        status_map = {2: "🔴直播中", 4: "🟡回放", 0: "⚪未播"}
                        status = status_map.get(info['status'], "❓未知")
                        print(f"{i:2d}. {status} {info['nickname'][:15]:15} - {info['user_count_display']:>6}人")
                    else:
                        print(f"{i:2d}. ❌错误 {info['webcast_id'][:15]:15} - --")
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n👋 监控已停止")

if __name__ == "__main__":
    monitor = OptimizedDouyinMonitor()
    monitor.run()