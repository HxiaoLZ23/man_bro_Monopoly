"""
测试pygame版本的存档窗口
"""
import pygame
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ui.save_load_window_pygame import SaveLoadWindow
from src.models.game_state import GameState
from src.models.player import Player
from src.models.map import Map

def main():
    """主测试函数"""
    # 初始化pygame
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("pygame存档窗口测试")
    
    # 创建测试游戏状态
    game_state = GameState()
    
    # 创建测试玩家
    players = [
        Player(1, "测试玩家1"),
        Player(2, "测试玩家2"),
        Player(3, "AI玩家", is_ai=True)
    ]
    
    # 创建测试地图
    test_map = Map(10, 10)
    
    # 初始化游戏状态
    game_state.initialize_game(players, test_map)
    
    # 创建存档窗口
    save_window = SaveLoadWindow(screen)
    
    print("✅ 创建pygame存档窗口成功")
    
    # 测试回调函数
    def on_load(result):
        print(f"📥 加载回调: {result}")
    
    def on_save(result):
        print(f"💾 保存回调: {result}")
    
    def on_close():
        print("❌ 窗口关闭")
    
    save_window.set_callbacks(on_save=on_save, on_load=on_load, on_close=on_close)
    
    # 主循环
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    # 按S键测试保存对话框
                    print("🪟 显示保存对话框...")
                    save_window.show_save_dialog(game_state, on_save)
                elif event.key == pygame.K_l:
                    # 按L键测试加载对话框
                    print("🪟 显示加载对话框...")
                    save_window.show_load_dialog(on_load)
                elif event.key == pygame.K_ESCAPE:
                    running = False
            else:
                # 让存档窗口处理事件
                save_window.handle_event(event)
        
        # 填充背景
        screen.fill((30, 30, 30))
        
        # 显示说明文字
        font = pygame.font.Font(None, 36)
        title_text = font.render("pygame存档窗口测试", True, (255, 255, 255))
        instruction1 = font.render("按 S 键打开保存对话框", True, (255, 255, 255))
        instruction2 = font.render("按 L 键打开加载对话框", True, (255, 255, 255))
        instruction3 = font.render("按 ESC 键退出", True, (255, 255, 255))
        
        screen.blit(title_text, (400, 200))
        screen.blit(instruction1, (350, 250))
        screen.blit(instruction2, (350, 300))
        screen.blit(instruction3, (450, 350))
        
        # 绘制存档窗口
        save_window.draw()
        
        pygame.display.flip()
        clock.tick(60)
    
    # 清理
    save_window.close()
    pygame.quit()

if __name__ == "__main__":
    main() 