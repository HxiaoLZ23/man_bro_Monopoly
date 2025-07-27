"""
测试UI清理功能
"""
import sys
import os
import traceback
import pygame

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

def test_ui_cleanup():
    """测试UI清理功能"""
    try:
        print("🧪 开始测试UI清理功能...")
        
        # 初始化pygame
        pygame.init()
        pygame.mixer.init()
        
        # 创建联机窗口screen（模拟增强多人游戏窗口）
        print("🖼️ 创建联机窗口...")
        from src.ui.constants import WINDOW_WIDTH, WINDOW_HEIGHT
        multiplayer_screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("测试UI清理")
        print("  ✅ 联机窗口创建成功")
        
        # 导入主窗口类
        print("📦 导入主窗口类...")
        from src.ui.main_window import MainWindow
        
        # 创建主游戏窗口实例，重用联机窗口的screen
        print("🔧 创建主游戏窗口（重用现有screen）...")
        main_window = MainWindow(screen=multiplayer_screen)
        print("  ✅ 主游戏窗口创建成功")
        
        # 检查初始状态
        print("🔍 检查初始状态...")
        print(f"  - current_scene: {main_window.current_scene}")
        print(f"  - buttons数量: {len(main_window.buttons)}")
        print(f"  - panels数量: {len(main_window.panels)}")
        print(f"  - is_multiplayer: {getattr(main_window, 'is_multiplayer', 'Not Set')}")
        
        # 模拟游戏数据
        game_data = {
            'map_file': '1.json',
            'players': [
                {'client_id': 'client_1', 'name': '测试玩家1'},
                {'client_id': 'ai_1', 'name': 'AI玩家1(简单)'},
                {'client_id': 'ai_2', 'name': 'AI玩家2(普通)'}
            ],
            'room_id': 'test_room',
            'game_mode': 'multiplayer'
        }
        
        # 初始化多人游戏
        print("🎲 初始化多人游戏...")
        result = main_window.init_multiplayer_game(game_data)
        
        if result:
            print("  ✅ 多人游戏初始化成功")
            
            # 检查清理后的状态
            print("🔍 检查清理后的状态...")
            print(f"  - current_scene: {main_window.current_scene}")
            print(f"  - buttons数量: {len(main_window.buttons)}")
            print(f"  - panels数量: {len(main_window.panels)}")
            print(f"  - phase_buttons数量: {len(main_window.phase_buttons)}")
            
            # 检查是否有主菜单按钮残留
            menu_buttons_found = False
            for button in main_window.buttons:
                if hasattr(button, 'text') and button.text in ["开始游戏", "联机模式", "地图编辑器", "游戏设置", "退出游戏"]:
                    print(f"  ⚠️ 发现主菜单按钮残留: {button.text}")
                    menu_buttons_found = True
            
            if not menu_buttons_found:
                print("  ✅ 没有主菜单按钮残留")
            
            # 简单绘制一帧来验证
            print("🎨 测试绘制...")
            main_window.draw()
            pygame.display.flip()
            print("  ✅ 绘制成功")
            
        else:
            print("  ❌ 多人游戏初始化失败")
        
        pygame.quit()
        print("🎉 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()
        try:
            pygame.quit()
        except:
            pass

if __name__ == "__main__":
    test_ui_cleanup() 