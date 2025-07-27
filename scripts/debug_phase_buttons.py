#!/usr/bin/env python3
"""
调试phase_buttons变化的工具
"""
import pygame
import sys
import traceback

# 添加src目录到路径
sys.path.append('src')

def patch_phase_buttons():
    """给phase_buttons相关方法添加调试补丁"""
    
    from src.ui.main_window import MainWindow
    
    # 补丁phase_buttons相关方法
    original_show_preparation_choices = MainWindow.show_preparation_choices
    original_show_action_choices = MainWindow.show_action_choices
    original_ai_action_decision = MainWindow.ai_action_decision
    
    def debug_show_preparation_choices(self):
        """调试版show_preparation_choices"""
        print(f"🎯 [CALL] show_preparation_choices被调用！")
        print(f"   - 多人游戏: {getattr(self, 'is_multiplayer', False)}")
        print(f"   - 当前阶段按钮数: {len(self.phase_buttons)}")
        print(f"   - 调用栈:")
        for line in traceback.format_stack()[-5:]:
            print(f"     {line.strip()}")
        
        result = original_show_preparation_choices(self)
        
        print(f"   - 执行后阶段按钮数: {len(self.phase_buttons)}")
        if self.phase_buttons:
            print(f"   - 新增按钮:")
            for i, button in enumerate(self.phase_buttons):
                button_text = getattr(button, 'text', 'No text')
                print(f"     [{i}] {button_text}")
        
        return result
    
    def debug_show_action_choices(self):
        """调试版show_action_choices"""
        print(f"🎯 [CALL] show_action_choices被调用！")
        print(f"   - 多人游戏: {getattr(self, 'is_multiplayer', False)}")
        print(f"   - 当前阶段按钮数: {len(self.phase_buttons)}")
        print(f"   - 调用栈:")
        for line in traceback.format_stack()[-5:]:
            print(f"     {line.strip()}")
        
        result = original_show_action_choices(self)
        
        print(f"   - 执行后阶段按钮数: {len(self.phase_buttons)}")
        if self.phase_buttons:
            print(f"   - 新增按钮:")
            for i, button in enumerate(self.phase_buttons):
                button_text = getattr(button, 'text', 'No text')
                print(f"     [{i}] {button_text}")
        
        return result
    
    def debug_ai_action_decision(self, player):
        """调试版ai_action_decision"""
        print(f"🤖 [CALL] ai_action_decision被调用！玩家: {player.name}")
        print(f"   - 多人游戏: {getattr(self, 'is_multiplayer', False)}")
        print(f"   - 当前阶段按钮数: {len(self.phase_buttons)}")
        
        result = original_ai_action_decision(self, player)
        
        print(f"   - AI决策后阶段按钮数: {len(self.phase_buttons)}")
        
        return result
    
    # 补丁清理方法
    original_clear = list.clear
    
    def debug_clear(self):
        """调试版clear"""
        # 只在是phase_buttons时打印
        if hasattr(self, '__name__') and 'phase_buttons' in str(self):
            print(f"🧹 [CLEAR] phase_buttons被清理！")
            print(f"   - 清理前按钮数: {len(self)}")
            print(f"   - 调用栈:")
            for line in traceback.format_stack()[-5:]:
                print(f"     {line.strip()}")
        return original_clear(self)
    
    # 不能直接替换list.clear，因为会影响所有list
    # 而是创建一个专门的追踪函数
    def track_phase_buttons_clear(main_window):
        """追踪特定main_window的phase_buttons清理"""
        original_phase_buttons = main_window.phase_buttons
        
        class TrackedList(list):
            def clear(self):
                print(f"🧹 [CLEAR] phase_buttons被清理！")
                print(f"   - 清理前按钮数: {len(self)}")
                print(f"   - 调用栈:")
                for line in traceback.format_stack()[-5:]:
                    print(f"     {line.strip()}")
                return super().clear()
        
        # 替换phase_buttons为追踪版本
        tracked_buttons = TrackedList(original_phase_buttons)
        main_window.phase_buttons = tracked_buttons
    
    MainWindow.show_preparation_choices = debug_show_preparation_choices
    MainWindow.show_action_choices = debug_show_action_choices
    MainWindow.ai_action_decision = debug_ai_action_decision
    
    print("🔧 phase_buttons调试补丁已应用")
    return track_phase_buttons_clear

def run_phase_buttons_test():
    """运行phase_buttons调试测试"""
    print("🕵️ 开始phase_buttons调试...")
    
    # 应用调试补丁
    track_phase_buttons_clear = patch_phase_buttons()
    
    try:
        from src.ui.main_window import MainWindow
        
        # 创建主窗口
        main_window = MainWindow()
        
        # 应用追踪
        track_phase_buttons_clear(main_window)
        
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
        print(f"📊 初始状态: 阶段按钮数={len(main_window.phase_buttons)}")
        
        # 模拟一些游戏循环来触发阶段按钮变化
        print("🎮 开始事件循环...")
        clock = pygame.time.Clock()
        frame_count = 0
        
        while frame_count < 180:  # 运行3秒
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
            
            # 每30帧检查一次状态
            if frame_count % 30 == 0:
                print(f"📊 [检查] 帧:{frame_count}, 阶段按钮数:{len(main_window.phase_buttons)}")
            
            clock.tick(60)
        
        pygame.quit()
        print("🎉 phase_buttons调试测试完成")
        
    except Exception as e:
        print(f"❌ 调试测试失败: {e}")
        traceback.print_exc()
        try:
            pygame.quit()
        except:
            pass

if __name__ == "__main__":
    run_phase_buttons_test() 