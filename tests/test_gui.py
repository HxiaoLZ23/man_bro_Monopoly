#!/usr/bin/env python3
"""
GUI启动测试脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """测试导入"""
    print("🔍 测试模块导入...")
    
    try:
        import pygame
        print("✅ pygame 导入成功")
    except ImportError as e:
        print(f"❌ pygame 导入失败: {e}")
        return False
    
    try:
        from src.models.map import Map
        print("✅ Map 模型导入成功")
    except ImportError as e:
        print(f"❌ Map 模型导入失败: {e}")
        return False
    
    try:
        from src.models.player import Player
        print("✅ Player 模型导入成功")
    except ImportError as e:
        print(f"❌ Player 模型导入失败: {e}")
        return False
    
    try:
        from src.models.game_state import GameState
        print("✅ GameState 模型导入成功")
    except ImportError as e:
        print(f"❌ GameState 模型导入失败: {e}")
        return False
    
    try:
        from src.systems.player_manager import PlayerManager
        print("✅ PlayerManager 系统导入成功")
    except ImportError as e:
        print(f"❌ PlayerManager 系统导入失败: {e}")
        return False
    
    try:
        from src.systems.dice_system import DiceSystem
        print("✅ DiceSystem 系统导入成功")
    except ImportError as e:
        print(f"❌ DiceSystem 系统导入失败: {e}")
        return False
    
    try:
        from src.ui.constants import WINDOW_WIDTH, WINDOW_HEIGHT, COLORS
        print("✅ UI 常量导入成功")
    except ImportError as e:
        print(f"❌ UI 常量导入失败: {e}")
        return False
    
    try:
        from src.ui.components import Button, Panel, Text
        print("✅ UI 组件导入成功")
    except ImportError as e:
        print(f"❌ UI 组件导入失败: {e}")
        return False
    
    try:
        from src.ui.map_view import MapView
        print("✅ MapView 导入成功")
    except ImportError as e:
        print(f"❌ MapView 导入失败: {e}")
        return False
    
    return True

def test_pygame_init():
    """测试pygame初始化"""
    print("\n🎮 测试pygame初始化...")
    
    try:
        import pygame
        pygame.init()
        print("✅ pygame 初始化成功")
        
        # 测试创建窗口
        screen = pygame.display.set_mode((800, 600))
        print("✅ 窗口创建成功")
        
        pygame.quit()
        print("✅ pygame 退出成功")
        return True
        
    except Exception as e:
        print(f"❌ pygame 初始化失败: {e}")
        return False

def test_main_window():
    """测试主窗口创建"""
    print("\n🪟 测试主窗口创建...")
    
    try:
        from src.ui.main_window import MainWindow
        print("✅ MainWindow 类导入成功")
        
        # 尝试创建主窗口（但不运行）
        window = MainWindow()
        print("✅ MainWindow 实例创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ MainWindow 创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 开始GUI启动诊断...\n")
    
    # 测试导入
    if not test_imports():
        print("\n❌ 模块导入失败，无法启动GUI")
        return
    
    # 测试pygame
    if not test_pygame_init():
        print("\n❌ pygame初始化失败，无法启动GUI")
        return
    
    # 测试主窗口
    if not test_main_window():
        print("\n❌ 主窗口创建失败，无法启动GUI")
        return
    
    print("\n✅ 所有测试通过！GUI应该可以正常启动")
    print("💡 如果GUI仍然无法启动，可能是运行时的问题")

if __name__ == "__main__":
    main() 