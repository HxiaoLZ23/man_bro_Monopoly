#!/usr/bin/env python3
"""
深度UI调试工具
追踪所有可能导致界面闪烁的事件处理路径
"""
import pygame
import sys
import traceback

# 添加src目录到路径
sys.path.append('src')

def patch_all_event_handlers():
    """给所有可能的事件处理器添加调试补丁"""
    
    # 补丁MainWindow
    from src.ui.main_window import MainWindow
    original_handle_events = MainWindow.handle_events
    original_draw = MainWindow.draw
    
    def debug_handle_events(self):
        """调试版handle_events"""
        try:
            return original_handle_events(self)
        except Exception as e:
            print(f"🚨 [ERROR] MainWindow.handle_events异常: {e}")
            traceback.print_exc()
    
    def debug_draw(self):
        """调试版draw"""
        # 记录状态变化
        if not hasattr(self, '_debug_last_scene'):
            self._debug_last_scene = self.current_scene
        
        if self._debug_last_scene != self.current_scene:
            print(f"🔄 [SCENE] 场景变化: {self._debug_last_scene} -> {self.current_scene}")
            print(f"   - 多人游戏: {getattr(self, 'is_multiplayer', False)}")
            self._debug_last_scene = self.current_scene
        
        try:
            return original_draw(self)
        except Exception as e:
            print(f"🚨 [ERROR] MainWindow.draw异常: {e}")
            traceback.print_exc()
    
    MainWindow.handle_events = debug_handle_events
    MainWindow.draw = debug_draw
    
    # 补丁MapView
    try:
        from src.ui.map_view import MapView
        original_map_handle_event = MapView.handle_event
        
        def debug_map_handle_event(self, event):
            """调试版MapView.handle_event"""
            try:
                result = original_map_handle_event(self, event)
                if result and event.type == pygame.MOUSEBUTTONDOWN:
                    print(f"🗺️ [MAP] 地图处理了鼠标点击事件: {event.pos}")
                    if hasattr(self, 'selected_cell'):
                        print(f"   - 选中格子: {self.selected_cell}")
                return result
            except Exception as e:
                print(f"🚨 [ERROR] MapView.handle_event异常: {e}")
                traceback.print_exc()
                return False
        
        MapView.handle_event = debug_map_handle_event
    except ImportError:
        print("⚠️ 无法导入MapView")
    
    # 补丁所有可能调用init_menu_scene的方法
    original_init_menu = MainWindow.init_menu_scene
    original_init_setup = MainWindow.init_game_setup_scene
    original_return_menu = MainWindow.return_to_menu
    
    def debug_init_menu(self):
        print(f"🚨 [CALL] init_menu_scene被调用！")
        print(f"   - 当前场景: {self.current_scene}")
        print(f"   - 多人游戏: {getattr(self, 'is_multiplayer', False)}")
        print(f"   - 调用栈:")
        for line in traceback.format_stack()[-5:]:
            print(f"     {line.strip()}")
        return original_init_menu(self)
    
    def debug_init_setup(self):
        print(f"🚨 [CALL] init_game_setup_scene被调用！")
        print(f"   - 当前场景: {self.current_scene}")
        print(f"   - 多人游戏: {getattr(self, 'is_multiplayer', False)}")
        print(f"   - 调用栈:")
        for line in traceback.format_stack()[-5:]:
            print(f"     {line.strip()}")
        return original_init_setup(self)
    
    def debug_return_menu(self):
        print(f"🚨 [CALL] return_to_menu被调用！")
        print(f"   - 当前场景: {self.current_scene}")
        print(f"   - 多人游戏: {getattr(self, 'is_multiplayer', False)}")
        print(f"   - 调用栈:")
        for line in traceback.format_stack()[-5:]:
            print(f"     {line.strip()}")
        return original_return_menu(self)
    
    MainWindow.init_menu_scene = debug_init_menu
    MainWindow.init_game_setup_scene = debug_init_setup
    MainWindow.return_to_menu = debug_return_menu
    
    print("🔧 深度调试补丁已应用")

def test_deep_debugging():
    """深度调试测试"""
    print("🕵️ 开始深度UI调试...")
    
    # 应用调试补丁
    patch_all_event_handlers()
    
    try:
        from src.ui.enhanced_multiplayer_window import EnhancedMultiplayerWindow
        
        # 创建联机窗口
        multiplayer_window = EnhancedMultiplayerWindow()
        
        # 快速启动游戏
        game_data = {
            'map_file': '1.json',
            'players': [
                {'name': '玩家1', 'client_id': 'client1'},
                {'name': '玩家2', 'client_id': 'client2'},  
                {'name': 'AI玩家1', 'client_id': 'ai_1'}
            ]
        }
        
        print("🚀 启动多人游戏...")
        try:
            multiplayer_window.start_multiplayer_game(game_data)
        except SystemExit:
            print("✅ 游戏正常退出")
        except Exception as e:
            print(f"❌ 游戏异常: {e}")
            traceback.print_exc()
        
        pygame.quit()
        
    except Exception as e:
        print(f"❌ 深度调试失败: {e}")
        traceback.print_exc()
        try:
            pygame.quit()
        except:
            pass

def run_interactive_test():
    """运行交互式测试"""
    print("🎮 启动交互式深度调试...")
    
    # 应用调试补丁
    patch_all_event_handlers()
    
    try:
        from src.ui.main_window import MainWindow
        
        # 创建主窗口
        main_window = MainWindow()
        
        # 设置多人游戏模式
        main_window.is_multiplayer = True
        
        # 模拟游戏初始化
        game_data = {
            'map_file': '1.json',
            'players': [
                {'name': '玩家1', 'client_id': 'client1'},
                {'name': '玩家2', 'client_id': 'client2'},  
                {'name': 'AI玩家1', 'client_id': 'ai_1'}
            ]
        }
        
        result = main_window.init_multiplayer_game(game_data)
        if not result:
            print("❌ 游戏初始化失败")
            return
        
        print("✅ 游戏初始化成功，开始交互式测试...")
        print("🖱️ 请点击游戏界面的任何地方，观察调试输出...")
        print("🛑 按ESC键退出测试")
        
        clock = pygame.time.Clock()
        running = True
        frame_count = 0
        
        while running:
            frame_count += 1
            
            # 每60帧输出一次状态
            if frame_count % 60 == 0:
                print(f"📊 [STATUS] 帧:{frame_count}, 场景:{main_window.current_scene}, 按钮数:{len(main_window.buttons)}")
            
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    print(f"🖱️ [CLICK] 鼠标点击: {event.pos}, 按钮: {event.button}")
            
            # 正常游戏循环
            main_window.handle_events()
            main_window.update()
            main_window.draw()
            
            clock.tick(60)
        
        pygame.quit()
        print("🎉 交互式测试完成")
        
    except Exception as e:
        print(f"❌ 交互式测试失败: {e}")
        traceback.print_exc()
        try:
            pygame.quit()
        except:
            pass

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        run_interactive_test()
    else:
        test_deep_debugging() 