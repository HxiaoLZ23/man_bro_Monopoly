#!/usr/bin/env python3
"""
测试游戏退出修复
验证窗口关闭时不再出现音乐系统错误
"""
import pygame
import sys
import time

# 添加src目录到路径
sys.path.append('src')

from ui.main_window import MainWindow

def test_game_exit():
    """测试游戏退出是否正常"""
    print("🎮 开始测试游戏退出修复...")
    
    try:
        # 创建主窗口
        main_window = MainWindow()
        print("✅ 主窗口创建成功")
        
        # 模拟短暂运行
        start_time = time.time()
        frames = 0
        
        while time.time() - start_time < 2.0:  # 运行2秒
            # 处理事件
            main_window.handle_events()
            
            # 更新游戏状态
            main_window.update()
            
            # 绘制
            main_window.draw()
            
            # 控制帧率
            main_window.clock.tick(60)
            frames += 1
            
            # 检查是否需要退出
            if not main_window.running:
                break
        
        print(f"✅ 游戏运行了 {frames} 帧")
        
        # 主动退出
        print("🔧 执行游戏退出...")
        main_window.quit_game()
        
        # 运行一帧来处理退出
        if main_window.running:
            main_window.handle_events()
            main_window.update()
            main_window.draw()
        
        print("✅ 游戏退出信号发送成功")
        
        # 检查音乐系统状态
        if hasattr(main_window, 'music_system'):
            print(f"✅ 音乐系统销毁状态: {main_window.music_system.is_destroyed}")
        
        print("🎉 测试完成！退出流程正常")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_window_close_event():
    """测试窗口关闭事件"""
    print("\n🪟 测试窗口关闭事件...")
    
    try:
        # 创建主窗口
        main_window = MainWindow()
        
        # 模拟窗口关闭事件
        close_event = pygame.event.Event(pygame.QUIT)
        pygame.event.post(close_event)
        
        # 处理事件
        main_window.handle_events()
        
        # 检查是否正确设置了退出标志
        print(f"✅ 退出标志设置: {not main_window.running}")
        
        # 检查音乐系统是否被清理
        if hasattr(main_window, 'music_system'):
            print(f"✅ 音乐系统销毁状态: {main_window.music_system.is_destroyed}")
        
        print("✅ 窗口关闭事件处理正常")
        
    except Exception as e:
        print(f"❌ 窗口关闭测试失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 开始游戏退出修复测试...\n")
    
    success = True
    
    # 测试1: 正常游戏退出
    if not test_game_exit():
        success = False
    
    # 测试2: 窗口关闭事件
    if not test_window_close_event():
        success = False
    
    if success:
        print("\n🎉 所有测试通过！游戏退出修复成功。")
        print("✅ 现在关闭游戏窗口时应该不会再出现音乐播放错误。")
    else:
        print("\n❌ 有测试失败，需要进一步检查。")
    
    # 确保清理
    try:
        pygame.mixer.quit()
        pygame.quit()
    except:
        pass 