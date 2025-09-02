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
        # 从文件读取的直播间ID
        self.webcast_ids = ['27356915698', '847308587035', '858106419879']
    
    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_live_info(self, webcast_id):
        """获取单个直播间信息"""
        try:
            url = f"{self.api_base_url}?webcast_id={webcast_id}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['code'] == 200 and data['data']['data']['data']:
                    live_data = data['data']['data']['data'][0]
                    user_info = data['data']['data']['user']
                    
                    # 处理在线人数，可能包含'+'号
                    user_count_str = live_data['user_count_str']
                    try:
                        # 去除'+'号并转换为整数
                        if '+' in user_count_str:
                            user_count = int(user_count_str.replace('+', ''))
                            # 如果有+号，显示时保留+号表示这是最低人数
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
                else:
                    return {
                        'success': False,
                        'webcast_id': webcast_id,
                        'error': '直播间关闭'
                    }
            else:
                return {
                    'success': False,
                    'webcast_id': webcast_id,
                    'error': f'请求失败({response.status_code})'
                }
        except Exception as e:
            return {
                'success': False,
                'webcast_id': webcast_id,
                'error': '连接失败'
            }
    
    def display_table(self, live_infos):
        """显示优化后的表格"""
        self.clear_screen()
        
        print("┌" + "─" * 138 + "┐")
        print("│" + "🎬 抖音直播间实时监控 - 优化表格展示".center(136) + "│")
        print("├" + "─" * 138 + "┤")
        print(f"│ 📅 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} │ 📊 监控数量: {len(self.webcast_ids)} 个直播间" + " " * (136 - 60 - len(str(len(self.webcast_ids)))) + "│")
        print("├" + "─" * 138 + "┤")
        
        # 优化的表格标题
        print("│ 序号 │   直播间ID   │        主播昵称        │  在线人数  │  状态  │                    直播标题                    │")
        print("├──────┼──────────────┼────────────────────────┼────────────┼────────┼────────────────────────────────────────────────┤")
        
        # 表格内容 - 优化对齐
        for i, info in enumerate(live_infos, 1):
            if info['success']:
                # 处理文本长度并确保对齐
                nickname = self._format_text(info['nickname'], 20)
                title = self._format_text(info['title'], 44)
                
                status_map = {
                    2: "🔴直播",
                    4: "🟡回放", 
                    0: "⚪未播"
                }
                status = status_map.get(info['status'], "❓未知")
                
                # 确保人数右对齐显示
                user_count_formatted = f"{info['user_count_display']:>8}"
                
                print(f"│ {i:^4} │ {info['webcast_id']:^12} │ {nickname:<22} │ {user_count_formatted} │ {status:^6} │ {title:<46} │")
            else:
                error = self._format_text(info['error'], 44)
                print(f"│ {i:^4} │ {info['webcast_id']:^12} │ {'❌ 错误':<22} │ {'--':>8} │ {'❌':^6} │ {error:<46} │")
        
        print("├" + "─" * 138 + "┤")
        
        # 统计信息
        success_count = sum(1 for info in live_infos if info['success'])
        total_viewers = sum(info.get('user_count', 0) for info in live_infos if info['success'])
        
        stats_line = f"📊 成功: {success_count}/{len(live_infos)} 个 │ 总观众: {total_viewers:,}+ 人 │ 🔄 每秒更新 │ 💡 Ctrl+C 退出"
        print(f"│ {stats_line:<136} │")
        print("└" + "─" * 138 + "┘")
    
    def _format_text(self, text, max_length):
        """格式化文本，确保不超过指定长度"""
        if len(text) <= max_length:
            return text
        else:
            return text[:max_length-3] + "..."
    
    def run(self):
        """运行监控"""
        print("🚀 启动抖音直播间表格监控...")
        print("⏳ 正在初始化...")
        
        try:
            while True:
                live_infos = []
                
                # 获取所有直播间信息
                for webcast_id in self.webcast_ids:
                    info = self.get_live_info(webcast_id)
                    live_infos.append(info)
                
                # 按在线人数排序
                live_infos.sort(key=lambda x: x.get('user_count', 0) if x['success'] else -1, reverse=True)
                
                # 显示表格
                self.display_table(live_infos)
                
                # 等待1秒
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n👋 监控已停止，感谢使用！")
        except Exception as e:
            print(f"\n❌ 程序运行出错: {e}")

if __name__ == "__main__":
    monitor = DouyinTableMonitor()
    monitor.run()