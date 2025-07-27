"""
音乐控制面板
"""
import pygame
from src.ui.components import Button
from src.ui.constants import COLORS, FONTS
from src.ui.font_manager import get_font

class MusicControlPanel:
    """音乐控制面板"""
    
    def __init__(self, music_system, x=10, y=10):
        self.music_system = music_system
        self.x = x
        self.y = y
        self.width = 200
        self.height = 120
        self.visible = False
        
        # 字体
        self.font = get_font("small")
        
        # 按钮
        button_width = 60
        button_height = 25
        button_y = self.y + 30
        
        self.play_pause_button = Button(
            self.x + 10, button_y, button_width, button_height,
            "暂停", self.toggle_play_pause, COLORS["primary"]
        )
        
        self.stop_button = Button(
            self.x + 80, button_y, button_width, button_height,
            "停止", self.stop_music, COLORS["error"]
        )
        
        self.volume_up_button = Button(
            self.x + 10, button_y + 35, 30, button_height,
            "+", self.volume_up, COLORS["success"]
        )
        
        self.volume_down_button = Button(
            self.x + 50, button_y + 35, 30, button_height,
            "-", self.volume_down, COLORS["warning"]
        )
        
        self.buttons = [
            self.play_pause_button,
            self.stop_button,
            self.volume_up_button,
            self.volume_down_button
        ]
    
    def toggle_visibility(self):
        """切换面板可见性"""
        self.visible = not self.visible
    
    def toggle_play_pause(self):
        """切换播放/暂停"""
        if self.music_system.is_music_playing():
            self.music_system.pause_music()
            self.play_pause_button.text = "播放"
        else:
            self.music_system.resume_music()
            self.play_pause_button.text = "暂停"
    
    def stop_music(self):
        """停止音乐"""
        self.music_system.stop_music()
        self.play_pause_button.text = "播放"
    
    def volume_up(self):
        """增加音量"""
        current_volume = self.music_system.get_volume()
        new_volume = min(1.0, current_volume + 0.1)
        self.music_system.set_volume(new_volume)
    
    def volume_down(self):
        """减少音量"""
        current_volume = self.music_system.get_volume()
        new_volume = max(0.0, current_volume - 0.1)
        self.music_system.set_volume(new_volume)
    
    def handle_event(self, event):
        """处理事件"""
        if not self.visible:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # 检查是否点击在面板区域内
            panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            if not panel_rect.collidepoint(mouse_pos):
                return False
            
            # 检查按钮点击
            for button in self.buttons:
                if button.rect.collidepoint(mouse_pos):
                    button.callback()
                    return True
        
        return False
    
    def draw(self, screen):
        """绘制面板"""
        if not self.visible:
            return
        
        # 绘制背景
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, COLORS["panel_bg"], panel_rect)
        pygame.draw.rect(screen, COLORS["border"], panel_rect, 2)
        
        # 绘制标题
        title_text = self.font.render("音乐控制", True, COLORS["text"])
        screen.blit(title_text, (self.x + 10, self.y + 5))
        
        # 绘制音量信息
        volume = self.music_system.get_volume()
        volume_text = self.font.render(f"音量: {int(volume * 100)}%", True, COLORS["text"])
        screen.blit(volume_text, (self.x + 90, self.y + 65))
        
        # 绘制按钮
        for button in self.buttons:
            button.draw(screen) 