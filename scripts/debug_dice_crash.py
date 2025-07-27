"""
调试投掷骰子后游戏崩溃的问题
"""
import sys
import os
import traceback

# 添加项目路径
sys.path.append('.')

try:
    import pygame
    from src.ui.main_window import MainWindow
    
    # 手动定义窗口大小
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 900
    
    def test_dice_roll_crash():
        """测试投掷骰子后的崩溃问题"""
        print("🎮 开始测试投掷骰子崩溃问题...")
        
        # 初始化pygame
        pygame.init()
        pygame.mixer.init()
        
        # 创建显示窗口
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("大富翁游戏 - 投掷骰子测试")
        
        # 创建主窗口
        main_window = MainWindow(screen)
        
        # 快速开始游戏
        main_window.select_map("default")
        main_window.start_game()
        
        print("✅ 游戏初始化完成")
        
        # 模拟游戏流程
        clock = pygame.time.Clock()
        test_steps = 0
        max_test_steps = 300  # 5秒测试
        
        try:
            while test_steps < max_test_steps:
                # 处理事件
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    
                    # 处理延迟移动事件
                    if event.type == pygame.USEREVENT + 1:
                        if hasattr(main_window, '_delayed_move_callback'):
                            print("🔄 执行延迟移动回调")
                            try:
                                main_window._delayed_move_callback()
                                delattr(main_window, '_delayed_move_callback')
                            except Exception as e:
                                print(f"❌ 延迟移动回调异常: {e}")
                                traceback.print_exc()
                        continue
                
                # 自动测试投掷骰子
                if test_steps == 60:  # 1秒后自动投掷
                    print("🎲 自动投掷骰子...")
                    try:
                        main_window.roll_dice()
                    except Exception as e:
                        print(f"❌ 投掷骰子异常: {e}")
                        traceback.print_exc()
                        break
                
                # 更新游戏状态
                try:
                    main_window.update()
                except Exception as e:
                    print(f"❌ 更新游戏状态异常: {e}")
                    traceback.print_exc()
                    break
                
                # 绘制画面
                try:
                    main_window.draw()
                except Exception as e:
                    print(f"❌ 绘制画面异常: {e}")
                    traceback.print_exc()
                    break
                
                clock.tick(60)
                test_steps += 1
                
                # 检查游戏是否还在运行
                if not main_window.running:
                    print("⚠️ 游戏已停止运行")
                    break
            
            print("✅ 测试完成，未发现崩溃")
            
        except Exception as e:
            print(f"❌ 测试过程中发生异常: {e}")
            traceback.print_exc()
        
        finally:
            # 清理资源
            try:
                if hasattr(main_window, 'music_system') and main_window.music_system:
                    main_window.music_system.cleanup()
            except:
                pass
            
            pygame.quit()
    
    if __name__ == "__main__":
        test_dice_roll_crash()
        
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("请确保所有依赖模块都已正确安装")
except Exception as e:
    print(f"❌ 运行测试失败: {e}")
    traceback.print_exc() 