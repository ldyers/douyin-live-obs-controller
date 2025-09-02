# 抖音直播间OBS WebSocket自动化控制系统

这是一个基于Python的抖音直播间监控和OBS自动化控制系统，通过WebSocket协议连接OBS Studio，实现直播间数据的实时监控和自动场景切换。

## 🚀 主要功能

- 🔴 **实时监控多个抖音直播间** - 自动获取在线人数、主播信息等数据
- 📊 **智能排序** - 按在线人数自动排序直播间，精确到个位数
- 🎬 **OBS自动控制** - 通过WebSocket连接OBS，自动创建场景和浏览器源
- 🖥️ **多屏网格布局** - 在统一场景中展示多个直播间，3列网格排列
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
# 使用虚拟环境（推荐）
cd "c:\Users\Administrator\PycharmProjects\Douyin_TikTok_Download_API-main"
.\venv\Scripts\activate
python obs_websocket_controller.py
```

3. **自动化特性**
   - 系统会自动创建"直播间综合监控"场景
   - 为每个直播间创建浏览器源（尺寸：1080x1920，30FPS）
   - 按3列网格布局自动排列
   - 实时监控并自动排序显示

## 🛠️ 高级配置

### 浏览器源尺寸调整
在 `create_browser_source` 方法中修改：
```python
"inputSettings": {
    "url": url,
    "width": 1080,   # 宽度1080像素
    "height": 1920,  # 高度1920像素
    "fps": 30,       # 帧率30FPS
}
```

### 网格布局调整
在 `setup_obs_scenes` 方法中修改：
```python
# 3列排列配置
col = (rank - 1) % 3  # 列索引 (0, 1, 2)
row = (rank - 1) // 3  # 行索引 (0, 1, 2, ...)

x_pos = 20 + col * (1080 + 20)  # X位置：20, 1120, 2220
y_pos = 20 + row * (1920 + 20)  # Y位置：20, 1960, 3900
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

精确到个位显示，不使用"+"号模糊格式，确保数据对比的准确性。

## 📊 表格展示规范

- 在线人数右对齐，方便数值比较
- 主播昵称左对齐，保持统一格式
- 状态信息居中对齐，清晰展示
- 使用Unicode边框字符，支持中英文混合
- 数据实时更新，每秒刷新排序

## 🔧 故障排除

### WebSocket连接失败
- 确保OBS已启动并开启WebSocket服务器
- 检查端口4455是否被占用
- 验证OBS服务器IP地址是否正确

### 直播间数据获取失败
- 确保抖音API服务正常运行
- 检查网络连接
- 验证直播间URL格式正确

### 虚拟环境问题
```bash
# 如果虚拟环境不存在，创建新的
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issues和Pull Requests！

## 📞 支持

如有问题，请在GitHub Issues中提出。

---

## 🎯 更新日志

### v1.1.0 (2025-09-02)
- ✅ 更新为3列网格布局
- ✅ 优化浏览器源位置计算
- ✅ 完善项目文档和配置说明
- ✅ 增加虚拟环境使用指南