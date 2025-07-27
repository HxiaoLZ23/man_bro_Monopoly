#!/usr/bin/env python3
"""
最终摄像头系统测试脚本
测试修复后的摄像头跟随和地图绘制坐标系统
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

def create_test_map():
    """创建测试地图"""
    game_map = Map(15, 15)
    
    # 设置一些测试格子
    test_positions = [(2, 2), (5, 5), (8, 8), (12, 12), (10, 3), (3, 10)]
    cell_types = ["shop", "bank", "jail", "luck", "bad_luck", "dice_shop"]
    
    for i, (x, y) in enumerate(test_positions):
        if 0 <= x < 15 and 0 <= y < 15:
            game_map.set_cell_type((x, y), cell_types[i % len(cell_types)])
    
    return game_map

def create_test_players(game_map):
    """创建测试玩家"""
    players = []
    for i in range(4):
        player = Player(f"玩家{i+1}", i+1)
        player.position = i * 5  # 不同的起始位置
        players.append(player)
    
    return players

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("摄像头系统最终测试")
    clock = pygame.time.Clock()
    
    # 创建测试数据
    game_map = create_test_map()
    players = create_test_players(game_map)
    
    # 创建地图视图
    map_view = MapView(game_map, 50, 50, 600)
    map_view.camera_follow_mode = True
    
    current_player_index = 0
    
    # 初始跟随第一个玩家
    if players:
        map_view.follow_player(players[current_player_index], True)
    
    font = pygame.font.Font(None, 24)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # 处理地图视图事件
            if map_view.handle_event(event):
                continue
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    # 切换到玩家1
                    current_player_index = 0
                    map_view.follow_player(players[current_player_index], True)
                elif event.key == pygame.K_2:
                    # 切换到玩家2
                    current_player_index = 1
                    map_view.follow_player(players[current_player_index], True)
                elif event.key == pygame.K_3:
                    # 切换到玩家3
                    current_player_index = 2
                    map_view.follow_player(players[current_player_index], True)
                elif event.key == pygame.K_4:
                    # 切换到玩家4
                    current_player_index = 3
                    map_view.follow_player(players[current_player_index], True)
                elif event.key == pygame.K_r:
                    # 重置视图
                    map_view.reset_view()
                elif event.key == pygame.K_f:
                    # 切换跟随模式
                    map_view.toggle_camera_follow()
                elif event.key == pygame.K_c:
                    # 居中到地图中心
                    map_view.center_on_cell(7, 7, True)
        
        # 更新摄像头
        map_view.update_camera()
        
        # 绘制
        screen.fill(COLORS["background"])
        
        # 绘制地图
        map_view.draw(screen, players)
        
        # 绘制说明文字
        instructions = [
            "摄像头系统测试",
            "1-4: 跟随对应玩家",
            "R: 重置视图",
            "F: 切换跟随模式",
            "C: 居中到地图中心",
            "空格: 切换跟随模式",
            "M: 切换手动模式",
            "方向键: 手动移动摄像头",
            f"当前跟随: 玩家{current_player_index + 1}",
            f"摄像头模式: {'跟随' if map_view.camera_follow_mode else '手动'}",
            f"偏移: ({map_view.offset_x:.0f}, {map_view.offset_y:.0f})"
        ]
        
        y = 10
        for instruction in instructions:
            text_surface = font.render(instruction, True, COLORS["text_primary"])
            screen.blit(text_surface, (WINDOW_WIDTH - 250, y))
            y += 25
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main() 