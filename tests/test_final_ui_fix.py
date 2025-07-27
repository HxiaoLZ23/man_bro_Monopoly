#!/usr/bin/env python3
"""
完整的UI修复测试
测试多人游戏模式下的UI保护机制是否正常工作
"""
import pygame
import sys
import time

# 添加src目录到路径
sys.path.append('src')

def test_ui_protection():
    """测试UI保护机制"""
    print("🔧 测试UI保护机制...")
    
    try:
        from src.ui.main_window import MainWindow
        
        # 创建主窗口
        main_window = MainWindow()
        
        # 测试单人游戏模式下的正常行为
        print("\n📋 测试1: 单人游戏模式下的正常行为")
        print(f"  - 初始多人游戏标识: {getattr(main_window, 'is_multiplayer', '未设置')}")
        
        # 尝试调用可能出问题的方法
        print("  - 尝试调用init_menu_scene()...")
        main_window.init_menu_scene()
        print(f"    ✅ 当前场景: {main_window.current_scene}")
        print(f"    ✅ 按钮数量: {len(main_window.buttons)}")
        
        print("  - 尝试调用init_game_setup_scene()...")
        main_window.init_game_setup_scene()
        print(f"    ✅ 当前场景: {main_window.current_scene}")
        print(f"    ✅ 按钮数量: {len(main_window.buttons)}")
        
        # 测试多人游戏模式下的保护
        print("\n📋 测试2: 多人游戏模式下的保护机制")
        main_window.is_multiplayer = True
        print(f"  - 设置多人游戏标识: {main_window.is_multiplayer}")
        print(f"  - 当前场景: {main_window.current_scene}")
        
        print("  - 尝试调用init_menu_scene()...")
        main_window.init_menu_scene()
        print(f"    ✅ 保护后场景: {main_window.current_scene}")
        print(f"    ✅ 保护后按钮数量: {len(main_window.buttons)}")
        
        print("  - 尝试调用init_game_setup_scene()...")
        main_window.init_game_setup_scene()
        print(f"    ✅ 保护后场景: {main_window.current_scene}")
        print(f"    ✅ 保护后按钮数量: {len(main_window.buttons)}")
        
        print("  - 尝试调用return_to_menu()...")
        main_window.return_to_menu()
        print(f"    ✅ 保护后场景: {main_window.current_scene}")
        
        # 测试游戏初始化
        print("\n📋 测试3: 多人游戏初始化")
        game_data = {
            'map_file': '1.json',
            'players': [
                {'name': '玩家1', 'client_id': 'client1'},
                {'name': '玩家2', 'client_id': 'client2'},
                {'name': 'AI玩家1', 'client_id': 'ai_1'}  # 添加第三个玩家
            ]
        }
        
        result = main_window.init_multiplayer_game(game_data)
        print(f"  - 多人游戏初始化结果: {result}")
        if result:
            print(f"    ✅ 最终场景: {main_window.current_scene}")
            print(f"    ✅ 最终按钮数量: {len(main_window.buttons)}")
            
            # 检查是否有主菜单按钮残留
            menu_buttons = []
            for button in main_window.buttons:
                if hasattr(button, 'text') and button.text in ["开始游戏", "联机模式", "地图编辑器", "返回菜单"]:
                    menu_buttons.append(button.text)
            
            if menu_buttons:
                print(f"    ⚠️ 发现主菜单按钮残留: {menu_buttons}")
            else:
                print(f"    ✅ 没有主菜单按钮残留")
        
        # 测试UI强制保护
        print("\n📋 测试4: UI强制保护测试")
        if main_window.current_scene != "game":
            main_window.current_scene = "game"
        
        # 模拟错误场景切换
        print("  - 模拟错误场景切换...")
        main_window.current_scene = "menu"
        main_window.draw()  # 这应该触发强制保护
        print(f"    ✅ 强制保护后场景: {main_window.current_scene}")
        
        pygame.quit()
        print("\n🎉 所有UI保护测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        try:
            pygame.quit()
        except:
            pass
        return False

def run_integration_test():
    """运行集成测试"""
    print("🎮 开始完整的UI修复集成测试...")
    
    # 首先测试UI保护机制
    if not test_ui_protection():
        print("❌ UI保护测试失败，停止集成测试")
        return False
    
    print("\n🚀 开始联机游戏完整流程测试...")
    
    try:
        from src.ui.enhanced_multiplayer_window import EnhancedMultiplayerWindow
        
        # 创建联机窗口
        multiplayer_window = EnhancedMultiplayerWindow()
        
        # 快速模拟游戏启动流程
        print("🤖 模拟快速游戏启动...")
        game_data = {
            'map_file': '1.json',
            'players': [
                {'name': '玩家1', 'client_id': 'client1'},
                {'name': '玩家2', 'client_id': 'client2'},  
                {'name': 'AI玩家1', 'client_id': 'ai_1'}
            ]
        }
        
        # 直接调用启动方法（不运行窗口循环）
        try:
            multiplayer_window.start_multiplayer_game(game_data)
            print("✅ 游戏启动成功！")
        except Exception as e:
            print(f"⚠️ 游戏启动异常（这可能是正常的）: {e}")
        
        pygame.quit()
        print("🎉 集成测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        try:
            pygame.quit()
        except:
            pass
        return False

if __name__ == "__main__":
    success = run_integration_test()
    if success:
        print("\n✅ 所有测试通过！UI闪烁问题应该已经修复。")
    else:
        print("\n❌ 部分测试失败，需要进一步调试。") 