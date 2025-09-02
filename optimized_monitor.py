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
        # 从用户文件读取的直播间ID
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
                    
                    # 获取最精确的在线人数（解决数据不准确问题）
                    # 优先使用stats.user_count_str，它包含最准确的实时人数
                    accurate_count_str = None
                    
                    # 1. 优先检查stats对象中的精确人数
                    if 'stats' in live_data and isinstance(live_data['stats'], dict):
                        stats_count = live_data['stats'].get('user_count_str')
                        if stats_count and stats_count.strip():
                            accurate_count_str = str(stats_count).strip()
                    
                    # 2. 如果stats中没有，检查room_view_stats
                    if not accurate_count_str:
                        if 'room_view_stats' in live_data and isinstance(live_data['room_view_stats'], dict):
                            room_stats = live_data['room_view_stats']
                            display_value = room_stats.get('display_value')
                            if display_value is not None:
                                accurate_count_str = str(display_value)
                    
                    # 3. 最后才使用主字段（可能不准确）
                    if not accurate_count_str:
                        accurate_count_str = live_data.get('user_count_str', '0')
                    
                    try:
                        # 处理所有格式的人数字符串
                        if '+' in accurate_count_str:
                            # 对于"400+"格式，去除+号并显示准确数字
                            clean_str = accurate_count_str.replace('+', '')
                            user_count = int(clean_str)
                            user_count_display = f"{user_count}"
                        else:
                            # 对于精确数字，直接使用
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
    
    def format_text(self, text, width, align='left'):
        """格式化文本，确保指定宽度和对齐方式"""
        # 计算中文字符宽度（中文字符占2个位置）
        display_width = 0
        for char in text:
            if ord(char) > 127:  # 中文字符
                display_width += 2
            else:  # 英文字符
                display_width += 1
        
        # 如果文本太长，截断并添加省略号
        if display_width > width:
            truncated = ""
            current_width = 0
            for char in text:
                char_width = 2 if ord(char) > 127 else 1
                if current_width + char_width <= width - 3:  # 留出省略号空间
                    truncated += char
                    current_width += char_width
                else:
                    break
            text = truncated + "..."
            display_width = current_width + 3
        
        # 计算需要填充的空格数
        padding = width - display_width
        
        if align == 'center':
            left_pad = padding // 2
            right_pad = padding - left_pad
            return ' ' * left_pad + text + ' ' * right_pad
        elif align == 'right':
            return ' ' * padding + text
        else:  # left
            return text + ' ' * padding
    
    def display_optimized_table(self, live_infos):
        """显示优化对齐的表格"""
        self.clear_screen()
        
        # 表格宽度配置
        col_widths = {
            'seq': 4,      # 序号
            'id': 12,      # 直播间ID
            'name': 24,    # 主播昵称
            'count': 12,   # 在线人数
            'status': 8,   # 状态
            'title': 50    # 直播标题
        }
        
        total_width = sum(col_widths.values()) + 7  # 6个分隔符 + 2个边框
        
        # 顶部边框
        print("┌" + "─" * (total_width - 2) + "┐")
        
        # 标题行
        title_text = "🎬 抖音直播间实时监控 - 完美对齐版"
        print(f"│{title_text:^{total_width-2}}│")
        
        # 分隔线
        print("├" + "─" * (total_width - 2) + "┤")
        
        # 信息行
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        info_text = f"📅 {current_time} │ 📊 监控: {len(self.webcast_ids)}个直播间"
        print(f"│ {info_text:<{total_width-3}}│")
        
        # 表头分隔线
        print("├" + "─" * col_widths['seq'] + "┬" + "─" * col_widths['id'] + "┬" + 
              "─" * col_widths['name'] + "┬" + "─" * col_widths['count'] + "┬" + 
              "─" * col_widths['status'] + "┬" + "─" * col_widths['title'] + "┤")
        
        # 表头
        header_seq = self.format_text("序号", col_widths['seq'], 'center')
        header_id = self.format_text("直播间ID", col_widths['id'], 'center') 
        header_name = self.format_text("主播昵称", col_widths['name'], 'center')
        header_count = self.format_text("在线人数", col_widths['count'], 'center')
        header_status = self.format_text("状态", col_widths['status'], 'center')
        header_title = self.format_text("直播标题", col_widths['title'], 'center')
        
        print(f"│{header_seq}│{header_id}│{header_name}│{header_count}│{header_status}│{header_title}│")
        
        # 数据分隔线
        print("├" + "─" * col_widths['seq'] + "┼" + "─" * col_widths['id'] + "┼" + 
              "─" * col_widths['name'] + "┼" + "─" * col_widths['count'] + "┼" + 
              "─" * col_widths['status'] + "┼" + "─" * col_widths['title'] + "┤")
        
        # 数据行
        for i, info in enumerate(live_infos, 1):
            if info['success']:
                status_map = {
                    2: "🔴直播中",
                    4: "🟡回放", 
                    0: "⚪未播"
                }
                status_text = status_map.get(info['status'], "❓未知")
                
                # 格式化每列数据
                seq_text = self.format_text(str(i), col_widths['seq'], 'center')
                id_text = self.format_text(info['webcast_id'], col_widths['id'], 'center')
                name_text = self.format_text(info['nickname'], col_widths['name'], 'left')
                count_text = self.format_text(info['user_count_display'], col_widths['count'], 'right')
                status_text_formatted = self.format_text(status_text, col_widths['status'], 'center')
                title_text = self.format_text(info['title'], col_widths['title'], 'left')
                
                print(f"│{seq_text}│{id_text}│{name_text}│{count_text}│{status_text_formatted}│{title_text}│")
            else:
                # 错误行
                seq_text = self.format_text(str(i), col_widths['seq'], 'center')
                id_text = self.format_text(info['webcast_id'], col_widths['id'], 'center')
                name_text = self.format_text("❌ 错误", col_widths['name'], 'left')
                count_text = self.format_text("--", col_widths['count'], 'right')
                status_text = self.format_text("❌", col_widths['status'], 'center')
                error_text = self.format_text(info['error'], col_widths['title'], 'left')
                
                print(f"│{seq_text}│{id_text}│{name_text}│{count_text}│{status_text}│{error_text}│")
        
        # 底部边框
        print("└" + "─" * col_widths['seq'] + "┴" + "─" * col_widths['id'] + "┴" + 
              "─" * col_widths['name'] + "┴" + "─" * col_widths['count'] + "┴" + 
              "─" * col_widths['status'] + "┴" + "─" * col_widths['title'] + "┘")
        
        # 统计信息
        success_count = sum(1 for info in live_infos if info['success'])
        total_viewers = sum(info.get('user_count', 0) for info in live_infos if info['success'])
        
        print("\n📊 统计信息:")
        print(f"   • 成功获取: {success_count}/{len(live_infos)} 个直播间")
        print(f"   • 总观众数: {total_viewers:,} 人")
        print(f"   • 刷新间隔: 1秒")
        print(f"   • 退出方式: Ctrl+C")
    
    def run(self):
        """运行监控"""
        print("🚀 启动抖音直播间优化对齐监控...")
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
                self.display_optimized_table(live_infos)
                
                # 等待1秒
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n👋 监控已停止，感谢使用！")
        except Exception as e:
            print(f"\n❌ 程序运行出错: {e}")

if __name__ == "__main__":
    monitor = OptimizedDouyinMonitor()
    monitor.run()