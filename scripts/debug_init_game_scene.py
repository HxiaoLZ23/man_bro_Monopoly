#!/usr/bin/env python3
"""
调试init_game_scene调用的工具
"""
import pygame
import sys
import traceback

# 添加src目录到路径
sys.path.append('src')

def patch_init_game_scene():
    """给init_game_scene添加调试补丁"""
    
    from src.ui.main_window import MainWindow
    original_init_game_scene = MainWindow.init_game_scene
    
    def debug_init_game_scene(self):
        """调试版init_game_scene"""
        print(f"🎮 [CALL] init_game_scene被调用！")
        print(f"   - 当前场景: {self.current_scene}")
        print(f"   - 多人游戏: {getattr(self, 'is_multiplayer', False)}")
        print(f"   - 当前按钮数: {len(self.buttons)}")
        print(f"   - 调用栈:")
        for line in traceback.format_stack()[-8:]:
            print(f"     {line.strip()}")
        
        # 记录调用前的状态
        buttons_before = len(self.buttons)
        panels_before = len(self.panels)
        
        # 调用原方法
        result = original_init_game_scene(self)
        
        # 记录调用后的状态
        buttons_after = len(self.buttons)
        panels_after = len(self.panels)
        
        print(f"   - 按钮变化: {buttons_before} -> {buttons_after}")
        print(f"   - 面板变化: {panels_before} -> {panels_after}")
        
        # 列出当前按钮
        if self.buttons:
            print(f"   - 当前按钮:")
            for i, button in enumerate(self.buttons):
                button_text = getattr(button, 'text', 'No text')
                print(f"     [{i}] {button_text}")
        
        return result
    
    MainWindow.init_game_scene = debug_init_game_scene
    print("🔧 init_game_scene调试补丁已应用")

def run_init_game_scene_test():
    """运行init_game_scene调试测试"""
    print("🕵️ 开始init_game_scene调试...")
    
    # 应用调试补丁
    patch_init_game_scene()
    
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
        
        print("🚀 初始化多人游戏...")
        result = main_window.init_multiplayer_game(game_data)
        if not result:
            print("❌ 游戏初始化失败")
            return
        
        print("✅ 游戏初始化成功")
        print(f"📊 最终状态: 场景={main_window.current_scene}, 按钮数={len(main_window.buttons)}")
        
        # 模拟一些事件来看是否会触发init_game_scene
        print("🎮 开始事件循环...")
        clock = pygame.time.Clock()
        frame_count = 0
        
        while frame_count < 300:  # 运行5秒 (60fps * 5)
            frame_count += 1
            
            # 处理pygame事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("🛑 收到退出事件")
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    print(f"🖱️ 鼠标点击: {event.pos}")
            
            # 正常游戏循环
            main_window.handle_events()
            main_window.update()
            main_window.draw()
            
            clock.tick(60)
        
        pygame.quit()
        print("🎉 调试测试完成")
        
    except Exception as e:
        print(f"❌ 调试测试失败: {e}")
        traceback.print_exc()
        try:
            pygame.quit()
        except:
            pass

if __name__ == "__main__":
    run_init_game_scene_test() 