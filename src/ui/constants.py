"""
UI常量配置
"""
import pygame

# 颜色定义
COLORS = {
    # 主色调
    "primary": (52, 152, 219),      # 蓝色主色
    "primary_dark": (41, 128, 185), # 深蓝色
    "primary_light": (93, 173, 226), # 浅蓝色
    
    # 辅助色
    "secondary": (241, 196, 15),    # 金色
    "secondary_dark": (243, 156, 18), # 深金色
    
    # 背景色
    "background": (236, 240, 241),  # 浅灰背景
    "surface": (255, 255, 255),     # 白色表面
    "card": (248, 249, 250),        # 卡片背景
    "panel": (255, 255, 255),       # 面板背景
    
    # 边框和分割线
    "border": (189, 195, 199),      # 边框颜色
    "divider": (236, 240, 241),     # 分割线颜色
    
    # 文字色
    "text_primary": (44, 62, 80),   # 主要文字
    "text_secondary": (127, 140, 141), # 次要文字
    "text_light": (255, 255, 255),  # 浅色文字
    
    # 状态色
    "success": (46, 204, 113),      # 成功绿
    "warning": (230, 126, 34),      # 警告橙
    "error": (231, 76, 60),         # 错误红
    "info": (52, 152, 219),         # 信息蓝
    "disabled": (149, 165, 166),    # 禁用灰色
    
    # 地图格子颜色
    "cell_empty": (255, 255, 255),  # 空地
    "cell_wall": (95, 95, 95),      # 墙
    "cell_void": (200, 200, 200),   # 空格
    "cell_shop": (155, 89, 182),    # 商店
    "cell_bank": (46, 204, 113),    # 银行
    "cell_jail": (231, 76, 60),     # 监狱
    "cell_luck": (241, 196, 15),    # 好运格
    "cell_bad_luck": (230, 126, 34), # 厄运格
    "cell_dice_shop": (52, 152, 219), # 骰子商店
    "cell_property": (26, 188, 156), # 房产
    "cell_property_owned": (155, 89, 182), # 已拥有房产
    "cell_property_level1": (46, 204, 113), # 一级房产
    "cell_property_level2": (241, 196, 15), # 二级房产
    "cell_property_level3": (230, 126, 34), # 三级房产
    "cell_property_level4": (231, 76, 60),  # 四级房产
    
    # 玩家颜色
    "player_1": (231, 76, 60),      # 玩家1 - 红色
    "player_2": (46, 204, 113),     # 玩家2 - 绿色
    "player_3": (52, 152, 219),     # 玩家3 - 蓝色
    "player_4": (241, 196, 15),     # 玩家4 - 黄色
    "player_5": (155, 89, 182),     # 玩家5 - 紫色
    "player_6": (230, 126, 34),     # 玩家6 - 橙色
    "ai_player": (127, 140, 141),   # AI玩家 - 灰色
}

# 窗口尺寸
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
# MAP_SIZE = 600  # 移除固定地图区域大小
CELL_SIZE = 60  # 格子大小（初始值，后续可自适应）

# 新增自适应地图区域配置
MAP_MARGIN = 20  # 地图区域与窗口边缘的间距
INFO_PANEL_WIDTH = 350  # 信息面板宽度（由350改为250）
MESSAGE_PANEL_HEIGHT = 180  # 消息栏高度

# 布局配置
LAYOUT = {
    "margin": 20,
    "padding": 10,
    "border_radius": 8,
    "button_height": 40,
    "panel_width": 300,
    "info_panel_height": 200,
}

# 字体配置
FONTS = {
    "title": 48,
    "subtitle": 32,
    "normal": 24,
    "small": 16,
    "body": 16,
    "heading": 24,
    "subheading": 18,
    "tiny": 12,
}

# 废弃的字体路径配置（现在使用全局字体管理器）
# 保留用于向后兼容，但建议使用 src.ui.font_manager
FONT_PATHS = [
    "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
    "C:/Windows/Fonts/simsun.ttc",    # 宋体
    "C:/Windows/Fonts/simhei.ttf",    # 黑体
    "/System/Library/Fonts/PingFang.ttc",  # macOS 苹方
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
    None  # 使用系统默认字体
]

# 获取可用的字体路径（废弃，使用font_manager代替）
def get_font_path():
    """获取可用的字体路径（废弃）"""
    import os
    for path in FONT_PATHS:
        if path and os.path.exists(path):
            return path
    return None

# 向后兼容
FONT_PATH = get_font_path()

# 动画配置
ANIMATION = {
    "fps": 60,
    "transition_duration": 300,  # 毫秒
    "dice_roll_duration": 1000,  # 骰子动画时长
    "move_duration": 500,        # 移动动画时长
}

# 游戏配置
GAME_UI = {
    "max_players": 6,
    "min_players": 3,
    "auto_save_interval": 30,  # 秒
    "message_display_time": 3,  # 秒
} 