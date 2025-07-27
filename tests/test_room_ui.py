#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试房间界面
"""

import pygame
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_room_ui():
    """测试房间界面"""
    print("🎮 测试房间界面...")
    
    try:
        from src.network.client.network_client import NetworkClient
        from src.ui.game_room_window import GameRoomWindow
        
        # 初始化pygame
        pygame.init()
        screen = pygame.display.set_mode((1000, 700))
        pygame.display.set_caption("房间界面测试")
        clock = pygame.time.Clock()
        
        # 创建模拟的房间数据
        room_info = {
            "room_id": "test_room",
            "name": "测试房间",
            "current_players": 2,
            "max_players": 4,
            "players": [
                {
                    "client_id": "player1",
                    "name": "玩家1",
                    "is_ready": True,
                    "is_host": True
                },
                {
                    "client_id": "player2", 
                    "name": "玩家2",
                    "is_ready": False,
                    "is_host": False
                }
            ]
        }
        
        # 创建模拟的网络客户端
        network_client = NetworkClient()
        network_client.client_id = "player1"
        network_client.player_name = "玩家1"
        
        # 创建房间窗口
        room_window = GameRoomWindow(
            network_client,
            room_info,
            lambda: print("房间窗口关闭"),
            lambda data: print(f"游戏开始: {data}")
        )
        
        # 主循环
        running = True
        while running and room_window.running:
            dt = clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                else:
                    room_window.handle_event(event)
            
            room_window.update(dt)
            room_window.draw(screen)
            pygame.display.flip()
        
        pygame.quit()
        print("✅ 房间界面测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("🎮 大富翁房间界面测试")
    print("=" * 50)
    
    print("\n📋 测试说明:")
    print("1. 查看房间界面布局")
    print("2. 测试玩家列表显示")
    print("3. 测试地图选择功能")
    print("4. 测试聊天界面")
    print("5. 按ESC键退出")
    
    input("\n按 Enter 键开始测试...")
    
    try:
        result = test_room_ui()
        if result:
            print("\n✅ 测试成功!")
        else:
            print("\n❌ 测试失败!")
    except KeyboardInterrupt:
        print("\n⌨️ 用户取消测试")
    except Exception as e:
        print(f"\n❌ 测试错误: {e}")
    
    input("\n按 Enter 键退出...")

if __name__ == "__main__":
    main() 