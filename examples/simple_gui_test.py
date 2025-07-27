#!/usr/bin/env python3
"""
简单的GUI测试
"""
import pygame
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

def main():
    """主函数"""
    print("🎮 启动简单GUI测试...")
    
    try:
        # 初始化pygame
        pygame.init()
        
        # 创建窗口
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("大富翁游戏 - 测试")
        
        # 初始化字体
        font = pygame.font.Font(None, 36)
        
        # 游戏循环
        running = True
        clock = pygame.time.Clock()
        
        while running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # 清屏
            screen.fill((255, 255, 255))
            
            # 绘制文本
            text = font.render("大富翁游戏测试", True, (0, 0, 0))
            text_rect = text.get_rect(center=(400, 300))
            screen.blit(text, text_rect)
            
            # 绘制说明
            instruction = font.render("按ESC键退出", True, (100, 100, 100))
            instruction_rect = instruction.get_rect(center=(400, 350))
            screen.blit(instruction, instruction_rect)
            
            # 更新显示
            pygame.display.flip()
            
            # 控制帧率
            clock.tick(60)
        
        # 退出
        pygame.quit()
        print("✅ GUI测试完成")
        
    except Exception as e:
        print(f"❌ GUI测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 