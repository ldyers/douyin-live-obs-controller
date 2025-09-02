#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音直播间WebSocket自动OBS控制器
功能：
1. 通过WebSocket连接OBS
2. 根据在线人数自动排序直播间
3. 自动切换OBS场景到人气最高的直播间
4. 实时监控并动态调整
"""

import asyncio
import websockets
import json
import requests
import time
import os
from datetime import datetime
import re

class DouyinOBSWebSocketController:
    def __init__(self):
        self.api_base_url = "http://localhost:8000/api/douyin/web/fetch_user_live_videos"
        self.obs_host = "192.168.1.102"  # 远程OBS服务器IP
        self.obs_port = 4455               # WebSocket端口
        self.obs_password = ""  # OBS WebSocket密码，如果有的话
        self.websocket = None
        self.live_urls = []
        self.current_scene = None
        self.scene_mapping = {}  # 直播间ID到OBS场景名的映射
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
    
    def get_live_info(self, webcast_id):
        """获取单个直播间信息（使用最准确的数据源）"""
        try:
            url = f"{self.api_base_url}?webcast_id={webcast_id}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['code'] == 200 and data['data']['data']['data']:
                    live_data = data['data']['data']['data'][0]
                    user_info = data['data']['data']['user']
                    
                    # 获取最精确的在线人数（数据源优先级：stats → room_view_stats → user_count_str）
                    accurate_count_str = None
                    
                    # 1. 优先检查stats对象中的精确人数
                    if 'stats' in live_data and isinstance(live_data['stats'], dict):
                        stats_count = live_data['stats'].get('user_count_str')
                        if stats_count and str(stats_count).strip():
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
                        # 处理所有格式的人数字符串，精确到个位显示
                        if '+' in accurate_count_str:
                            clean_str = accurate_count_str.replace('+', '')
                            user_count = int(clean_str)
                        else:
                            user_count = int(accurate_count_str)
                        
                        user_count_display = f"{user_count}"
                        
                    except ValueError:
                        user_count = 0
                        user_count_display = "--"
                    
                    return {
                        'success': True,
                        'webcast_id': webcast_id,
                        'url': f"https://live.douyin.com/{webcast_id}",
                        'nickname': user_info['nickname'],
                        'title': live_data['title'],
                        'user_count': user_count,
                        'user_count_display': user_count_display,
                        'status': live_data['status'],
                        'room_id': live_data['id_str']
                    }
                else:
                    return {
                        'success': False,
                        'webcast_id': webcast_id,
                        'url': f"https://live.douyin.com/{webcast_id}",
                        'error': '直播间关闭'
                    }
            else:
                return {
                    'success': False,
                    'webcast_id': webcast_id,
                    'url': f"https://live.douyin.com/{webcast_id}",
                    'error': f'请求失败({response.status_code})'
                }
        except Exception as e:
            return {
                'success': False,
                'webcast_id': webcast_id,
                'url': f"https://live.douyin.com/{webcast_id}",
                'error': '连接失败'
            }
    
    async def connect_obs(self):
        """连接到OBS WebSocket服务器"""
        try:
            uri = f"ws://{self.obs_host}:{self.obs_port}"
            print(f"🔗 正在连接OBS WebSocket: {uri}")
            
            self.websocket = await websockets.connect(uri)
            print("✅ OBS WebSocket连接成功！")
            
            # 发送认证消息（如果需要）
            await self.authenticate()
            
            return True
        except Exception as e:
            print(f"❌ OBS WebSocket连接失败: {e}")
            print("💡 请确保：")
            print("   1. OBS已启动")
            print("   2. 工具 → WebSocket服务器设置 → 启用WebSocket服务器")
            print("   3. 端口设置为4455（默认）")
            return False
    
    async def authenticate(self):
        """WebSocket认证处理"""
        try:
            # 发送Hello消息
            hello_request = {
                "op": 1,
                "d": {
                    "rpcVersion": 1
                }
            }
            
            await self.websocket.send(json.dumps(hello_request))
            response = await self.websocket.recv()
            hello_data = json.loads(response)
            
            if hello_data.get("op") == 0:  # Hello message received
                print("✅ WebSocket握手成功")
                return True
            else:
                print(f"❌ WebSocket握手失败: {hello_data}")
                return False
        except Exception as e:
            print(f"❌ WebSocket认证出错: {e}")
            return False
    
    async def get_scene_list(self):
        """获取OBS场景列表"""
        try:
            request = {
                "op": 6,
                "d": {
                    "requestType": "GetSceneList",
                    "requestId": "get_scenes"
                }
            }
            
            await self.websocket.send(json.dumps(request))
            response = await self.websocket.recv()
            data = json.loads(response)
            
            if data.get("op") == 7 and data["d"]["requestStatus"]["result"]:
                scenes = data["d"]["responseData"]["scenes"]
                scene_names = [scene["sceneName"] for scene in scenes]
                print(f"📋 检测到OBS场景: {', '.join(scene_names)}")
                return scene_names
            else:
                print("❌ 获取OBS场景列表失败")
                return []
        except Exception as e:
            print(f"❌ 获取场景列表出错: {e}")
            return []
    
    async def switch_scene(self, scene_name):
        """切换到指定场景"""
        try:
            request = {
                "op": 6,
                "d": {
                    "requestType": "SetCurrentProgramScene",
                    "requestId": f"switch_to_{scene_name}",
                    "requestData": {
                        "sceneName": scene_name
                    }
                }
            }
            
            await self.websocket.send(json.dumps(request))
            response = await self.websocket.recv()
            data = json.loads(response)
            
            if data.get("op") == 7 and data["d"]["requestStatus"]["result"]:
                print(f"✅ 已切换到场景: {scene_name}")
                self.current_scene = scene_name
                return True
            else:
                print(f"❌ 切换场景失败: {scene_name}")
                return False
        except Exception as e:
            print(f"❌ 切换场景出错: {e}")
            return False
    
    async def create_scene(self, scene_name):
        """创建新场景"""
        try:
            request = {
                "op": 6,
                "d": {
                    "requestType": "CreateScene",
                    "requestId": f"create_scene_{int(time.time())}",
                    "requestData": {
                        "sceneName": scene_name
                    }
                }
            }
            
            await self.websocket.send(json.dumps(request))
            response = await self.websocket.recv()
            data = json.loads(response)
            
            if data.get("op") == 7 and data["d"]["requestStatus"]["result"]:
                print(f"✅ 已创建场景: {scene_name}")
                return True
            else:
                # 场景可能已存在，这不是错误
                print(f"📝 场景已存在或创建失败: {scene_name}")
                return False
        except Exception as e:
            print(f"❌ 创建场景出错: {e}")
            return False
    
    async def create_browser_source(self, scene_name, source_name, url):
        """在指定场景中创建浏览器源"""
        try:
            request = {
                "op": 6,
                "d": {
                    "requestType": "CreateInput",
                    "requestId": f"create_source_{int(time.time())}",
                    "requestData": {
                        "sceneName": scene_name,
                        "inputName": source_name,
                        "inputKind": "browser_source",
                        "inputSettings": {
                            "url": url,
                            "width": 1080,   # 调整宽度为1080
                            "height": 1920,  # 调整高度为1920
                            "fps": 30,
                            "shutdown": False,
                            "restart_when_active": False
                        }
                    }
                }
            }
            
            await self.websocket.send(json.dumps(request))
            response = await self.websocket.recv()
            data = json.loads(response)
            
            if data.get("op") == 7 and data["d"]["requestStatus"]["result"]:
                print(f"✅ 已在场景'{scene_name}'中创建浏览器源: {source_name}")
                return True
            else:
                error_msg = data["d"]["requestStatus"].get("comment", "未知错误")
                print(f"📝 浏览器源已存在或创建失败: {source_name} - {error_msg}")
                return False
        except Exception as e:
            print(f"❌ 创建浏览器源出错: {e}")
            return False
    
    async def set_source_transform(self, scene_name, source_name, x_pos, y_pos, width=1080, height=1920):
        """设置源的位置和大小"""
        try:
            # 先获取场景项ID
            scene_item_id = await self.get_scene_item_id(scene_name, source_name)
            if scene_item_id is None:
                print(f"❌ 未找到源: {source_name}")
                return False
            
            request = {
                "op": 6,
                "d": {
                    "requestType": "SetSceneItemTransform",
                    "requestId": f"transform_{int(time.time())}",
                    "requestData": {
                        "sceneName": scene_name,
                        "sceneItemId": scene_item_id,
                        "sceneItemTransform": {
                            "positionX": float(x_pos),
                            "positionY": float(y_pos),
                            "scaleX": 1.0,
                            "scaleY": 1.0
                        }
                    }
                }
            }
            
            await self.websocket.send(json.dumps(request))
            response = await self.websocket.recv()
            data = json.loads(response)
            
            if data.get("op") == 7 and data["d"]["requestStatus"]["result"]:
                print(f"✅ 已设置源位置: {source_name} -> ({x_pos}, {y_pos})")
                return True
            else:
                print(f"❌ 设置源位置失败: {source_name}")
                return False
        except Exception as e:
            print(f"❌ 设置源位置出错: {e}")
            return False
    
    async def get_scene_item_id(self, scene_name, source_name):
        """获取场景项ID"""
        try:
            request = {
                "op": 6,
                "d": {
                    "requestType": "GetSceneItemList",
                    "requestId": f"get_items_{int(time.time())}",
                    "requestData": {
                        "sceneName": scene_name
                    }
                }
            }
            
            await self.websocket.send(json.dumps(request))
            response = await self.websocket.recv()
            data = json.loads(response)
            
            if data.get("op") == 7 and data["d"]["requestStatus"]["result"]:
                scene_items = data["d"]["responseData"]["sceneItems"]
                for item in scene_items:
                    if item["sourceName"] == source_name:
                        return item["sceneItemId"]
            return None
        except Exception as e:
            print(f"❌ 获取场景项ID出错: {e}")
            return None
    
    def get_all_rooms_sorted(self):
        """获取所有直播间信息并按在线人数降序排序"""
        live_infos = []
        
        for url in self.live_urls:
            webcast_id = self.extract_webcast_id(url)
            if webcast_id:
                info = self.get_live_info(webcast_id)
                live_infos.append(info)
        
        # 按在线人数降序排序
        live_infos.sort(key=lambda x: x.get('user_count', 0) if x['success'] else -1, reverse=True)
        
        return live_infos
    
    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_status(self, live_infos, target_scene):
        """显示当前状态"""
        self.clear_screen()
        
        print("=" * 80)
        print("🎬 抖音直播间WebSocket自动OBS控制器")
        print("=" * 80)
        print(f"📅 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔗 OBS连接状态: {'✅ 已连接' if self.websocket else '❌ 未连接'}")
        print(f"🎯 当前场景: {self.current_scene or '未知'}")
        print(f"🏆 目标场景: {target_scene or '无'}")
        print("=" * 80)
        
        print("📊 直播间排序（按在线人数降序）:")
        print("-" * 80)
        
        for rank, info in enumerate(live_infos[:10], 1):  # 只显示前10个
            if info['success']:
                status_icon = "🔴" if info['status'] == 2 else "⚪"
                print(f"  {rank:2d}. {status_icon} {info['nickname'][:20]:20} - {info['user_count_display']:>6}人")
            else:
                print(f"  {rank:2d}. ❌ {info['webcast_id'][:20]:20} - 错误")
        
        print("-" * 80)
        print("💡 自动控制说明:")
        print("   • 每10秒检查一次排序")
        print("   • 自动切换到人气最高的直播间")
        print("   • 人数变化时自动调整场景")
        print("   • 按Ctrl+C停止自动控制")
        print("=" * 80)
    
    async def setup_obs_scenes(self, live_infos):
        """设置OBS场景和浏览器源（在一个场景中创建多个浏览器源）"""
        print("🛠️ 正在创建统一直播间场景和多个浏览器源...")
        
        # 创建一个统一的场景来包含所有直播间
        master_scene_name = "直播间综合监控"
        print(f"   📺 正在创建主场景: {master_scene_name}")
        
        # 先创建主场景
        await self.create_scene(master_scene_name)
        
        created_count = 0
        
        # 在一个场景中为每个直播间创建浏览器源
        for rank, info in enumerate(live_infos[:6], 1):  # 最多6个直播间
            if info['success']:
                source_name = f"直播{rank}_{info['nickname']}"
                url = info['url']
                
                print(f"   🌐 正在添加浏览器源: {source_name}")
                
                # 在主场景中创建浏览器源
                source_created = await self.create_browser_source(master_scene_name, source_name, url)
                
                if source_created:
                    # 等待一下确保源创建完成
                    await asyncio.sleep(1.0)
                    
                    # 计算源的位置（按网格排列）
                    # 3列排列，每个1080x1920像素，间距20像素
                    col = (rank - 1) % 3  # 列索引 (0, 1, 2)
                    row = (rank - 1) // 3  # 行索引 (0, 1, 2, ...)
                    
                    x_pos = 20 + col * (1080 + 20)  # X位置：20, 1120, 2220
                    y_pos = 20 + row * (1920 + 20)  # Y位置：20, 1960, 3900
                    
                    print(f"   📏 设置位置: 第{row+1}行第{col+1}列 -> ({x_pos}, {y_pos})")
                    
                    # 设置源的位置
                    position_set = await self.set_source_transform(master_scene_name, source_name, x_pos, y_pos)
                    
                    if position_set:
                        created_count += 1
                        print(f"   ✅ 源'{source_name}'配置完成: {url}")
                        # 记录映射关系
                        self.scene_mapping[info['webcast_id']] = master_scene_name
                    else:
                        print(f"   ⚠️ 源'{source_name}'位置设置失败，但源已创建")
                        created_count += 1  # 仍然计为成功，只是位置设置失败
                        self.scene_mapping[info['webcast_id']] = master_scene_name
                else:
                    print(f"   📝 源'{source_name}'创建失败或已存在")
                
                # 稍微延迟以避免过快的请求
                await asyncio.sleep(0.8)
        
        print(f"✅ 统一直播间场景设置完成，成功创建: {created_count}个浏览器源")
        print(f"📺 主场景: {master_scene_name}")
        print(f"📏 排列方式: 3列网格布局，每个源高度1920x宽度1080像素")
        
        # 设置默认圼景为主场景
        self.current_scene = master_scene_name
    
    async def auto_switch_logic(self):
        """自动切换逻辑（优化为统一场景模式）"""
        while True:
            try:
                # 获取排序后的直播间信息
                live_infos = self.get_all_rooms_sorted()
                
                # 在统一场景模式下，我们不需要切换场景
                # 只需要确保当前场景是主场景
                master_scene_name = "直播间综合监控"
                
                if self.current_scene != master_scene_name:
                    print(f"🔄 切换到主监控场景: {master_scene_name}")
                    await self.switch_scene(master_scene_name)
                else:
                    # 找到人气最高的直播间
                    top_room = None
                    for info in live_infos:
                        if info['success'] and info['status'] == 2:  # 正在直播
                            top_room = info
                            break
                    
                    if top_room:
                        print(f"🏆 当前最高人气: {top_room['nickname']} ({top_room['user_count_display']}人)")
                    else:
                        print(f"⚠️ 未找到正在直播的房间")
                
                # 显示状态
                self.display_status(live_infos, master_scene_name)
                
                # 等待10秒后再次检查
                await asyncio.sleep(10)
                
            except Exception as e:
                print(f"❌ 自动切换逻辑出错: {e}")
                await asyncio.sleep(5)
    
    async def run(self):
        """运行WebSocket自动控制器"""
        if not self.live_urls:
            print("❌ 没有找到有效的直播间URL，请检查 live_url.txt 文件")
            return
        
        print("🚀 启动抖音直播间WebSocket自动OBS控制器...")
        print("📋 功能特性:")
        print("   • WebSocket连接OBS")
        print("   • 自动按人气排序直播间")
        print("   • 自动切换到最高人气场景")
        print("   • 实时监控动态调整")
        
        # 连接OBS
        if not await self.connect_obs():
            return
        
        try:
            # 获取初始排序
            live_infos = self.get_all_rooms_sorted()
            
            # 设置OBS场景
            await self.setup_obs_scenes(live_infos)
            
            # 启动自动切换逻辑
            await self.auto_switch_logic()
            
        except KeyboardInterrupt:
            print(f"\n\n👋 WebSocket自动控制已停止，感谢使用！")
        except Exception as e:
            print(f"\n❌ 程序运行出错: {e}")
        finally:
            if self.websocket:
                await self.websocket.close()
                print("🔗 OBS WebSocket连接已关闭")

async def main():
    """主函数"""
    controller = DouyinOBSWebSocketController()
    await controller.run()

if __name__ == "__main__":
    # 安装依赖提示
    try:
        import websockets
    except ImportError:
        print("❌ 缺少websockets依赖")
        print("📦 请运行: pip install websockets")
        exit(1)
    
    asyncio.run(main())