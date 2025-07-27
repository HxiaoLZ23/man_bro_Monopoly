#!/usr/bin/env python3
"""
UI闪烁问题调试工具
用于跟踪按钮点击、场景切换和UI状态变化
"""
import pygame
import sys
import time
import traceback

# 添加src目录到路径
sys.path.append('src')

def monkey_patch_main_window():
    """给MainWindow添加调试补丁"""
    from src.ui.main_window import MainWindow
    
    # 保存原始方法
    original_init_menu_scene = MainWindow.init_menu_scene
    original_return_to_menu = MainWindow.return_to_menu
    original_handle_events = MainWindow.handle_events
    original_draw = MainWindow.draw
    
    def debug_init_menu_scene(self):
        """调试版init_menu_scene"""
        print(f"🚨 [调试] init_menu_scene被调用!")
        print(f"  - 当前场景: {self.current_scene}")
        print(f"  - 是否多人游戏: {getattr(self, 'is_multiplayer', False)}")
        print(f"  - 调用堆栈:")
        traceback.print_stack()
        
        # 如果是多人游戏模式，阻止切换到菜单场景
        if getattr(self, 'is_multiplayer', False):
            print(f"  ⚠️ 多人游戏模式下阻止切换到菜单场景!")
            return
        
        return original_init_menu_scene(self)
    
    def debug_return_to_menu(self):
        """调试版return_to_menu"""
        print(f"🚨 [调试] return_to_menu被调用!")
        print(f"  - 当前场景: {self.current_scene}")
        print(f"  - 是否多人游戏: {getattr(self, 'is_multiplayer', False)}")
        print(f"  - 调用堆栈:")
        traceback.print_stack()
        
        return original_return_to_menu(self)
    
    def debug_handle_events(self):
        """调试版handle_events"""
        # 检查按钮点击
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # 检查是否点击了问题按钮
                for button in self.buttons:
                    if hasattr(button, 'rect') and button.rect.collidepoint(mouse_pos):
                        if hasattr(button, 'text') and button.text in ["返回菜单", "开始游戏", "联机模式"]:
                            print(f"🚨 [调试] 点击了可疑按钮: {button.text}")
                            print(f"  - 当前场景: {self.current_scene}")
                            print(f"  - 是否多人游戏: {getattr(self, 'is_multiplayer', False)}")
                            print(f"  - 按钮回调: {button.callback}")
                        break
            
            # 将事件重新放回队列
            pygame.event.post(event)
        
        return original_handle_events(self)
    
    def debug_draw(self):
        """调试版draw"""
        # 检查场景变化
        if not hasattr(self, '_last_scene'):
            self._last_scene = self.current_scene
        
        if self._last_scene != self.current_scene:
            print(f"🚨 [调试] 场景切换: {self._last_scene} -> {self.current_scene}")
            print(f"  - 是否多人游戏: {getattr(self, 'is_multiplayer', False)}")
            self._last_scene = self.current_scene
        
        # 检查按钮数量变化
        if not hasattr(self, '_last_button_count'):
            self._last_button_count = len(self.buttons)
        
        if self._last_button_count != len(self.buttons):
            print(f"🚨 [调试] 按钮数量变化: {self._last_button_count} -> {len(self.buttons)}")
            print(f"  - 当前按钮:")
            for i, button in enumerate(self.buttons):
                button_text = getattr(button, 'text', '未知')
                print(f"    {i+1}. {button_text}")
            self._last_button_count = len(self.buttons)
        
        return original_draw(self)
    
    # 应用补丁
    MainWindow.init_menu_scene = debug_init_menu_scene
    MainWindow.return_to_menu = debug_return_to_menu
    MainWindow.handle_events = debug_handle_events
    MainWindow.draw = debug_draw
    
    print("🔧 调试补丁已应用到MainWindow")

def test_multiplayer_ui_issue():
    """测试多人游戏UI问题"""
    print("🎮 开始测试多人游戏UI闪烁问题...")
    
    # 应用调试补丁
    monkey_patch_main_window()
    
    try:
        # 启动联机窗口
        from src.ui.enhanced_multiplayer_window import EnhancedMultiplayerWindow
        
        print("🚀 启动增强联机窗口...")
        multiplayer_window = EnhancedMultiplayerWindow()
        
        # 让窗口运行几秒，然后自动创建房间并开始游戏
        frames = 0
        test_phase = "init"
        
        while multiplayer_window.running and frames < 1000:  # 最多运行1000帧
            frames += 1
            
            # 自动化测试流程
            if test_phase == "init" and frames > 60:  # 1秒后自动创建房间
                print("🤖 [自动测试] 模拟创建房间...")
                test_phase = "room_created"
                # 模拟房间创建成功
                multiplayer_window.current_room = {
                    "room_id": "test_room",
                    "name": "测试房间",
                    "players": [
                        {"name": "玩家1", "client_id": "client1"},
                        {"name": "AI玩家1", "client_id": "ai_1"}
                    ]
                }
                multiplayer_window.room_players = multiplayer_window.current_room["players"]
                
            elif test_phase == "room_created" and frames > 180:  # 3秒后自动开始游戏
                print("🤖 [自动测试] 模拟开始游戏...")
                test_phase = "game_starting"
                
                # 模拟开始游戏
                game_data = {
                    'map_file': '1.json',
                    'players': multiplayer_window.current_room["players"]
                }
                
                try:
                    multiplayer_window.start_multiplayer_game(game_data)
                    break
                except Exception as e:
                    print(f"❌ 游戏启动失败: {e}")
                    break
            
            # 正常窗口循环
            multiplayer_window.handle_events()
            multiplayer_window.draw()
            multiplayer_window.clock.tick(60)
        
        print("🎉 测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()
    
    finally:
        try:
            pygame.quit()
        except:
            pass

if __name__ == "__main__":
    test_multiplayer_ui_issue() 