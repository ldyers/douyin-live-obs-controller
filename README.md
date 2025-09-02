# 抖音直播间OBS WebSocket自动化控制系统

这是一个基于Python的抖音直播间监控和OBS自动化控制系统，通过WebSocket协议连接OBS Studio，实现直播间数据的实时监控和自动场景切换。

## 🚀 主要功能

- 🔴 **实时监控多个抖音直播间** - 自动获取在线人数、主播信息等数据
- 📊 **智能排序** - 按在线人数自动排序直播间，精确到个位数
- 🎬 **OBS自动控制** - 通过WebSocket连接OBS，自动创建场景和浏览器源
- 🖥️ **多屏网格布局** - 在统一场景中展示多个直播间，2列网格排列
- ⚡ **实时切换** - 自动切换到人气最高的直播间
- 🔄 **动态更新** - 每10秒自动检查并更新排序

## 📋 系统要求

- Python 3.8+
- OBS Studio 28.0+（需开启WebSocket服务器）
- 抖音API服务（Douyin_TikTok_Download_API）

## 📦 安装依赖

```bash
pip install -r requirements.txt
```

## ⚙️ 配置说明

### 1. 修改OBS服务器地址
编辑 `obs_websocket_controller.py` 文件，修改OBS服务器IP：
```python
self.obs_host = "192.168.1.102"  # 修改为你的OBS服务器IP
self.obs_port = 4455               # WebSocket端口（默认4455）
```

### 2. 配置直播间URL
编辑 `live_url.txt` 文件，添加要监控的抖音直播间URL：
```
https://live.douyin.com/27356915698
https://live.douyin.com/847308587035
https://live.douyin.com/858106419879
```

### 3. 启动抖音API服务
确保抖音API服务在localhost:8000端口运行。

## 🎯 使用方法

1. **启动OBS Studio**
   - 打开 工具 → WebSocket服务器设置
   - 启用WebSocket服务器
   - 端口设置为4455（默认）

2. **运行控制器**
```bash
python obs_websocket_controller.py
```

3. **自动化特性**
   - 系统会自动创建"直播间综合监控"场景
   - 为每个直播间创建浏览器源（尺寸：1080x1920）
   - 按2列网格布局自动排列
   - 实时监控并自动排序显示

## 🛠️ 高级配置

### 浏览器源尺寸调整
在 `create_browser_source` 方法中修改：
```python
"inputSettings": {
    "url": url,
    "width": 1080,   # 宽度
    "height": 1920,  # 高度
    "fps": 30,
}
```

### 监控间隔调整
在 `auto_switch_logic` 方法中修改：
```python
await asyncio.sleep(10)  # 修改检查间隔（秒）
```

## 📈 数据准确性优化

系统采用多数据源优先级策略获取精确人数：
1. **stats.user_count_str** - 最高优先级
2. **room_view_stats.display_value** - 备用数据源
3. **user_count_str** - 兜底数据源

## 🔧 故障排除

### WebSocket连接失败
- 确保OBS已启动并开启WebSocket服务器
- 检查端口4455是否被占用
- 验证OBS服务器IP地址是否正确

### 直播间数据获取失败
- 确保抖音API服务正常运行
- 检查网络连接
- 验证直播间URL格式正确

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issues和Pull Requests！

## 📞 支持

如有问题，请在GitHub Issues中提出。