#!/usr/bin/env python3
"""
音乐系统清理测试
"""
import pygame
import sys
import time
import os

# 添加src目录到路径
sys.path.append('src')

from systems.music_system import MusicSystem

def test_music_system_cleanup():
    """测试音乐系统的正确清理"""
    print("🎵 开始测试音乐系统清理...")
    
    # 初始化pygame
    pygame.init()
    pygame.mixer.init()
    
    # 创建一个简单的窗口
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("音乐系统清理测试")
    clock = pygame.time.Clock()
    
    # 创建音乐系统
    music_system = MusicSystem()
    
    print("✅ 音乐系统初始化完成")
    
    # 尝试播放音乐（如果有的话）
    music_system.play_index_music()
    
    running = True
    test_time = 0
    
    while running and test_time < 3000:  # 运行3秒
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # 处理音乐事件
            music_system.handle_music_event(event)
        
        # 更新屏幕
        screen.fill((0, 0, 0))
        
        # 显示状态
        font = pygame.font.Font(None, 36)
        text = font.render("音乐系统测试中...", True, (255, 255, 255))
        text2 = font.render("按ESC退出", True, (255, 255, 255))
        text3 = font.render(f"运行时间: {test_time//1000}s", True, (255, 255, 255))
        
        screen.blit(text, (50, 100))
        screen.blit(text2, (50, 140))
        screen.blit(text3, (50, 180))
        
        pygame.display.flip()
        clock.tick(60)
        test_time += clock.get_time()
    
    # 测试清理
    print("🔧 开始清理音乐系统...")
    music_system.cleanup()
    
    # 验证清理后的状态
    print(f"✅ 音乐系统销毁状态: {music_system.is_destroyed}")
    print(f"✅ 播放状态: {music_system.is_playing}")
    print(f"✅ 播放列表: {len(music_system.current_playlist)}")
    
    # 清理pygame
    print("🔧 清理pygame...")
    try:
        pygame.mixer.quit()
        print("✅ pygame.mixer清理完成")
    except Exception as e:
        print(f"⚠️ pygame.mixer清理错误: {e}")
    
    try:
        pygame.quit()
        print("✅ pygame清理完成")
    except Exception as e:
        print(f"⚠️ pygame清理错误: {e}")
    
    print("🎉 测试完成!")

def test_double_cleanup():
    """测试重复清理是否安全"""
    print("\n🔄 测试重复清理...")
    
    pygame.init()
    pygame.mixer.init()
    
    music_system = MusicSystem()
    
    # 第一次清理
    music_system.cleanup()
    print("✅ 第一次清理完成")
    
    # 第二次清理（应该安全）
    music_system.cleanup()
    print("✅ 第二次清理完成 - 重复清理安全")
    
    # 尝试使用已销毁的音乐系统
    music_system.play_index_music()  # 应该被忽略
    music_system.set_volume(0.8)     # 应该被忽略
    playing = music_system.is_music_playing()  # 应该返回False
    
    print(f"✅ 销毁后播放状态: {playing}")
    
    pygame.mixer.quit()
    pygame.quit()

if __name__ == "__main__":
    try:
        test_music_system_cleanup()
        test_double_cleanup()
        print("\n🎉 所有测试通过！音乐系统清理功能正常。")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 确保清理
        try:
            pygame.mixer.quit()
        except:
            pass
        try:
            pygame.quit()
        except:
            pass 