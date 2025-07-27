#!/usr/bin/env python3
"""
摄像头系统测试脚本
演示地图视图的摄像头功能，包括自动跟随、手动控制、多玩家显示等
"""

import pygame
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.map import Map
from src.models.player import Player
from src.ui.map_view import MapView
from src.ui.constants import COLORS, WINDOW_WIDTH, WINDOW_HEIGHT
from src.models.map import Cell
from src.models.property import Property

class CameraTestApp:
    """摄像头系统测试应用"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("摄像头系统测试")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 创建测试地图
        self.game_map = self.create_test_map()
        
        # 创建地图视图
        self.map_view = MapView(self.game_map, 50, 50, 600)
        
        # 创建测试玩家
        self.players = [
            Player("1", "玩家1", is_ai=False),
            Player("2", "玩家2", is_ai=True),
            Player("3", "玩家3", is_ai=True),
            Player("4", "玩家4", is_ai=False),
        ]
        
        # 设置玩家初始位置
        self.players[0].position = 0
        self.players[1].position = 5
        self.players[2].position = 10
        self.players[3].position = 15
        
        # 当前玩家索引
        self.current_player_index = 0
        
        # 摄像头模式
        self.camera_follow_mode = True
        
        # 字体
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 16)
        
        # 尝试加载中文字体
        try:
            from src.ui.constants import FONT_PATH
            if FONT_PATH:
                self.font = pygame.font.Font(FONT_PATH, 24)
                self.small_font = pygame.font.Font(FONT_PATH, 16)
        except Exception as e:
            print(f"中文字体加载失败: {e}")
            # 使用系统默认字体
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 16)
    
    def create_test_map(self):
        """创建测试地图"""
        # 创建一个15x15的地图
        game_map = Map(15, 15)
        
        # 设置一些测试格子
        test_cells = [
            (0, 0, "start", "起点"),
            (2, 2, "property", "房产1"),
            (4, 4, "shop", "商店"),
            (6, 6, "bank", "银行"),
            (8, 8, "jail", "监狱"),
            (10, 10, "luck", "好运格"),
            (12, 12, "bad_luck", "厄运格"),
            (14, 14, "dice_shop", "骰子商店"),
            (1, 1, "property", "房产2"),
            (3, 3, "property", "房产3"),
            (5, 5, "property", "房产4"),
            (7, 7, "property", "房产5"),
            (9, 9, "property", "房产6"),
            (11, 11, "property", "房产7"),
            (13, 13, "property", "房产8"),
        ]
        
        for x, y, cell_type, name in test_cells:
            if 0 <= x < 15 and 0 <= y < 15:
                # 设置格子类型
                game_map.set_cell_type((x, y), cell_type)
                # 获取格子并设置属性
                cell = game_map.get_cell_at((x, y))
                if cell and cell_type == "property":
                    # Property构造函数: (position, owner_id, level)
                    # position是路径索引，这里用x+y作为简单的位置标识
                    property_obj = Property(x + y, None, 1)  # 1级房产，无主
                    cell.set_property(property_obj)
        
        # 生成路径
        # game_map.generate_path()
        
        return game_map
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            # 处理地图视图事件
            if self.map_view.handle_event(event):
                continue
            
            # 键盘事件
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # 空格键切换摄像头模式
                    self.toggle_camera_mode()
                elif event.key == pygame.K_m:
                    # M键切换手动模式
                    self.map_view.toggle_camera_manual()
                elif event.key == pygame.K_n:
                    # N键切换到下一个玩家
                    self.next_player()
                elif event.key == pygame.K_r:
                    # R键重置视图
                    self.map_view.reset_view()
                elif event.key == pygame.K_1:
                    # 数字键1-4直接跟随指定玩家
                    self.follow_player(0)
                elif event.key == pygame.K_2:
                    self.follow_player(1)
                elif event.key == pygame.K_3:
                    self.follow_player(2)
                elif event.key == pygame.K_4:
                    self.follow_player(3)
    
    def toggle_camera_mode(self):
        """切换摄像头模式"""
        self.camera_follow_mode = not self.camera_follow_mode
        if self.camera_follow_mode:
            self.map_view.toggle_camera_follow()
            # 立即跟随当前玩家
            self.follow_current_player()
        else:
            self.map_view.toggle_camera_manual()
    
    def next_player(self):
        """切换到下一个玩家"""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        if self.camera_follow_mode:
            self.follow_current_player()
    
    def follow_player(self, player_index):
        """跟随指定玩家"""
        if 0 <= player_index < len(self.players):
            self.current_player_index = player_index
            self.follow_current_player()
    
    def follow_current_player(self):
        """跟随当前玩家"""
        current_player = self.players[self.current_player_index]
        self.map_view.follow_player(current_player, True)
    
    def update(self):
        """更新游戏状态"""
        # 更新摄像头
        self.map_view.update_camera()
    
    def draw(self):
        """绘制界面"""
        self.screen.fill(COLORS["background"])
        
        # 绘制地图
        self.map_view.draw(self.screen, self.players)
        
        # 绘制控制说明
        self.draw_controls()
        
        # 绘制玩家信息
        self.draw_player_info()
        
        pygame.display.flip()
    
    def draw_controls(self):
        """绘制控制说明"""
        controls = [
            "摄像头系统测试",
            "",
            "控制说明:",
            "空格键 - 切换摄像头模式",
            "M键 - 切换手动控制",
            "N键 - 切换到下一个玩家",
            "R键 - 重置视图",
            "1-4键 - 直接跟随指定玩家",
            "方向键 - 手动移动摄像头",
            "鼠标中键拖拽 - 手动移动摄像头",
            "鼠标滚轮 - 上下移动摄像头",
            "",
            f"当前模式: {'跟随模式' if self.camera_follow_mode else '手动模式'}",
            f"当前玩家: {self.players[self.current_player_index].name}"
        ]
        
        y = 10
        for i, text in enumerate(controls):
            if i == 0:  # 标题
                surface = self.font.render(text, True, COLORS["text_primary"])
            elif i == 2:  # 控制说明标题
                surface = self.font.render(text, True, COLORS["secondary"])
            elif i >= 12:  # 状态信息
                surface = self.small_font.render(text, True, COLORS["success"])
            else:
                surface = self.small_font.render(text, True, COLORS["text_secondary"])
            
            self.screen.blit(surface, (WINDOW_WIDTH - 300, y))
            if i == 0 or i == 2:
                y += 20
            else:
                y += 16
    
    def draw_player_info(self):
        """绘制玩家信息"""
        y = 400
        title_surface = self.font.render("玩家信息:", True, COLORS["text_primary"])
        self.screen.blit(title_surface, (WINDOW_WIDTH - 300, y))
        y += 30
        
        for i, player in enumerate(self.players):
            # 玩家状态
            status = "当前" if i == self.current_player_index else "等待"
            if player.is_ai:
                status += " (AI)"
            
            # 颜色
            color = COLORS["success"] if i == self.current_player_index else COLORS["text_secondary"]
            
            # 玩家文本
            player_text = f"{player.name}: 位置{player.position} ({status})"
            surface = self.small_font.render(player_text, True, color)
            self.screen.blit(surface, (WINDOW_WIDTH - 300, y))
            y += 20
    
    def run(self):
        """运行测试应用"""
        # 初始跟随第一个玩家
        self.follow_current_player()
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    app = CameraTestApp()
    app.run() 