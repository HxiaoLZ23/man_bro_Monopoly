#!/usr/bin/env python3
"""
测试房间系统开始游戏功能
"""
import pygame
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.enhanced_multiplayer_window import EnhancedMultiplayerWindow

def main():
    """主函数"""
    pygame.init()
    
    # 设置显示模式
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("大富翁 - 开始游戏功能测试")
    
    # 创建增强多人游戏窗口
    multiplayer_window = EnhancedMultiplayerWindow()
    
    print("🎮 测试流程:")
    print("1. 创建房间")
    print("2. 进入房间")
    print("3. 添加AI玩家（可选）")
    print("4. 点击准备")
    print("5. 点击开始游戏")
    print("6. 检查是否收到game_start消息")
    
    # 运行窗口
    multiplayer_window.run()
    
    pygame.quit()

if __name__ == "__main__":
    main() 