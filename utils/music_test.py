#!/usr/bin/env python3
"""音乐系统测试"""
import pygame
import sys
import os

# 添加src目录到路径
sys.path.append('src')

from systems.music_system import MusicSystem

def main():
    pygame.init()
    pygame.mixer.init()
    
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("音乐测试")
    clock = pygame.time.Clock()
    
    music_system = MusicSystem()
    
    print("开始播放开始界面音乐...")
    music_system.play_index_music()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    print("播放开始界面音乐...")
                    music_system.play_index_music()
                elif event.key == pygame.K_2:
                    print("播放游戏界面音乐...")
                    music_system.play_main_music()
            elif event.type == pygame.USEREVENT + 1:
                music_system.handle_music_end_event()
        
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 36)
        text1 = font.render("按1播放开始界面音乐", True, (255, 255, 255))
        text2 = font.render("按2播放游戏界面音乐", True, (255, 255, 255))
        text3 = font.render("按ESC退出", True, (255, 255, 255))
        
        screen.blit(text1, (50, 100))
        screen.blit(text2, (50, 140))
        screen.blit(text3, (50, 180))
        
        pygame.display.flip()
        clock.tick(60)
    
    music_system.stop_music()
    pygame.quit()

if __name__ == "__main__":
    main() 