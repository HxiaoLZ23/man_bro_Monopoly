#!/usr/bin/env python3
"""
房间管理功能测试脚本
"""
import pygame
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ui.enhanced_multiplayer_window import EnhancedMultiplayerWindow
from src.ui.room_management_window import RoomManagementWindow
from src.network.client.network_client import NetworkClient


async def test_room_management():
    """测试房间管理功能"""
    print("🧪 开始测试房间管理功能...")
    
    # 初始化pygame
    pygame.init()
    
    try:
        # 创建网络客户端
        network_client = NetworkClient()
        print("✅ 网络客户端创建成功")
        
        # 测试房间管理窗口创建
        room_window = RoomManagementWindow(
            network_client=network_client,
            on_close=lambda: print("房间管理窗口关闭")
        )
        print("✅ 房间管理窗口创建成功")
        
        # 测试增强版多人游戏窗口
        multiplayer_window = EnhancedMultiplayerWindow()
        print("✅ 增强版多人游戏窗口创建成功")
        
        print("🎉 所有组件创建测试通过！")
        
        # 询问是否要启动实际测试
        response = input("\n是否要启动图形界面测试？(y/n): ")
        if response.lower() == 'y':
            print("🚀 启动图形界面测试...")
            multiplayer_window.run()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()
        print("✅ 测试完成")


def test_ui_components():
    """测试UI组件"""
    print("🧪 测试UI组件...")
    
    try:
        from src.ui.room_management_window import InputBox, RoomCard
        from src.ui.enhanced_multiplayer_window import PlayerNameDialog
        
        # 测试输入框组件
        input_box = InputBox(100, 100, 200, 40, "测试输入框")
        print("✅ InputBox 组件创建成功")
        
        # 测试房间卡片组件
        room_data = {
            "room_id": "test_room",
            "name": "测试房间",
            "current_players": 2,
            "max_players": 4,
            "has_password": False,
            "state": "waiting"
        }
        room_card = RoomCard(50, 50, 300, 80, room_data)
        print("✅ RoomCard 组件创建成功")
        
        # 测试玩家名称对话框
        pygame.init()
        screen = pygame.display.set_mode((400, 300))
        dialog = PlayerNameDialog(50, 50, 300, 150)
        print("✅ PlayerNameDialog 组件创建成功")
        
        print("🎉 所有UI组件测试通过！")
        
    except Exception as e:
        print(f"❌ UI组件测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()


def main():
    """主函数"""
    print("🎮 房间管理功能测试")
    print("=" * 50)
    
    # 测试UI组件
    test_ui_components()
    print()
    
    # 测试房间管理功能
    asyncio.run(test_room_management())


if __name__ == "__main__":
    main() 