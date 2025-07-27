"""
房产建设/升级窗口
"""
import pygame
from typing import Callable, Optional
from src.ui.components import Button
from src.ui.constants import COLORS
from src.ui.font_manager import get_font, render_text
from src.core.constants import PROPERTY_LEVELS


class PropertyWindow:
    """房产建设/升级窗口"""
    
    def __init__(self, on_close: Callable = None, on_build: Callable = None, on_upgrade: Callable = None):
        """初始化房产窗口"""
        self.on_close = on_close
        self.on_build = on_build
        self.on_upgrade = on_upgrade
        self.visible = False
        
        # 窗口属性
        self.width = 500
        self.height = 350
        self.x = 0
        self.y = 0
        
        # 按钮
        self.close_button = None
        self.build_button = None
        self.upgrade_button = None
        
        # 当前状态
        self.player_money = 0
        self.property_level = 0
        self.is_owner = False
        self.position = 0
        
    def show(self, screen_width: int, screen_height: int, player_money: int, 
             property_level: int, is_owner: bool, position: int):
        """显示窗口"""
        self.visible = True
        self.player_money = player_money
        self.property_level = property_level
        self.is_owner = is_owner
        self.position = position
        
        # 居中显示
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        
        # 创建按钮
        self._create_buttons()
    
    def hide(self):
        """隐藏窗口"""
        self.visible = False
        
    def _create_buttons(self):
        """创建按钮"""
        # 关闭按钮
        self.close_button = Button(
            self.x + self.width - 100, self.y + 10, 80, 40,
            "关闭", lambda: self._handle_close(),
            font_size="normal"
        )
        
        button_y = self.y + self.height - 80
        button_width = 120
        button_height = 40
        
        if self.property_level == 0:  # 空地，可以建设
            # 建设一级房产按钮
            build_cost = PROPERTY_LEVELS[1]["cost"]
            can_build = self.player_money >= build_cost
            
            self.build_button = Button(
                self.x + (self.width - button_width) // 2, button_y, 
                button_width, button_height,
                f"建设 (${build_cost:,})" if can_build else "金钱不足",
                lambda: self._handle_build() if can_build else None,
                font_size="normal",
                color=COLORS["success"] if can_build else COLORS["disabled"]
            )
        elif self.is_owner and self.property_level < 4:  # 自己的房产，可以升级
            # 升级房产按钮
            upgrade_cost = PROPERTY_LEVELS[self.property_level + 1]["cost"]
            can_upgrade = self.player_money >= upgrade_cost
            
            self.upgrade_button = Button(
                self.x + (self.width - button_width) // 2, button_y,
                button_width, button_height,
                f"升级 (${upgrade_cost:,})" if can_upgrade else "金钱不足",
                lambda: self._handle_upgrade() if can_upgrade else None,
                font_size="normal", 
                color=COLORS["success"] if can_upgrade else COLORS["disabled"]
            )
    
    def _handle_close(self):
        """处理关闭"""
        self.hide()
        if self.on_close:
            self.on_close()
    
    def _handle_build(self):
        """处理建设"""
        if self.on_build:
            self.on_build(self.position)
        self.hide()
    
    def _handle_upgrade(self):
        """处理升级"""
        if self.on_upgrade:
            self.on_upgrade(self.position)
        self.hide()
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件"""
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # 检查关闭按钮
            if self.close_button.rect.collidepoint(mouse_pos):
                if self.close_button.callback:
                    self.close_button.callback()
                return True
            
            # 检查建设按钮
            if self.build_button and self.build_button.rect.collidepoint(mouse_pos):
                if self.build_button.callback:
                    self.build_button.callback()
                return True
                
            # 检查升级按钮
            if self.upgrade_button and self.upgrade_button.rect.collidepoint(mouse_pos):
                if self.upgrade_button.callback:
                    self.upgrade_button.callback()
                return True
        
        return True  # 消费所有事件
    
    def draw(self, surface: pygame.Surface):
        """绘制窗口"""
        if not self.visible:
            return
            
        # 绘制半透明背景
        overlay = pygame.Surface((surface.get_width(), surface.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # 绘制窗口背景
        window_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, COLORS["background"], window_rect)
        pygame.draw.rect(surface, COLORS["primary"], window_rect, 3)
        
        # 绘制标题
        if self.property_level == 0:
            title = "建设房产"
        elif self.is_owner:
            title = "升级房产"
        else:
            title = "房产信息"
            
        title_surface = render_text(title, "large", COLORS["text_primary"], True)
        title_x = self.x + (self.width - title_surface.get_width()) // 2
        surface.blit(title_surface, (self.x + 20, self.y + 20))
        
        # 绘制玩家信息
        info_text = f"您的金钱: ${self.player_money:,}"
        info_surface = render_text(info_text, "normal", COLORS["text_secondary"])
        surface.blit(info_surface, (self.x + 20, self.y + 60))
        
        # 绘制位置信息
        pos_text = f"位置: {self.position}"
        pos_surface = render_text(pos_text, "normal", COLORS["text_secondary"])
        surface.blit(pos_surface, (self.x + 20, self.y + 90))
        
        # 绘制房产状态
        y_offset = 130
        
        if self.property_level == 0:
            # 空地状态
            status_text = "当前状态: 空地"
            status_surface = render_text(status_text, "subtitle", COLORS["text_primary"])
            surface.blit(status_surface, (self.x + 20, self.y + y_offset))
            
            # 建设信息
            build_info = f"建设一级房产需要: ${PROPERTY_LEVELS[1]['cost']:,}"
            build_surface = render_text(build_info, "normal", COLORS["text_secondary"])
            surface.blit(build_surface, (self.x + 20, self.y + y_offset + 40))
            
            rent_info = f"建成后租金: ${PROPERTY_LEVELS[1]['rent']:,}"
            rent_surface = render_text(rent_info, "normal", COLORS["success"])
            surface.blit(rent_surface, (self.x + 20, self.y + y_offset + 70))
            
        else:
            # 已有房产
            level_names = ["", "一级房产", "二级房产", "三级房产", "四级房产"]
            status_text = f"当前状态: {level_names[self.property_level]}"
            status_surface = render_text(status_text, "subtitle", COLORS["text_primary"])
            surface.blit(status_surface, (self.x + 20, self.y + y_offset))
            
            # 当前租金
            current_rent = f"当前租金: ${PROPERTY_LEVELS[self.property_level]['rent']:,}"
            rent_surface = render_text(current_rent, "normal", COLORS["text_secondary"])
            surface.blit(rent_surface, (self.x + 20, self.y + y_offset + 40))
            
            # 升级信息（如果可以升级）
            if self.is_owner and self.property_level < 4:
                upgrade_cost = PROPERTY_LEVELS[self.property_level + 1]["cost"]
                upgrade_rent = PROPERTY_LEVELS[self.property_level + 1]["rent"]
                
                upgrade_info = f"升级到{level_names[self.property_level + 1]}需要: ${upgrade_cost:,}"
                upgrade_surface = render_text(upgrade_info, "normal", COLORS["text_secondary"])
                surface.blit(upgrade_surface, (self.x + 20, self.y + y_offset + 70))
                
                new_rent_info = f"升级后租金: ${upgrade_rent:,}"
                new_rent_surface = render_text(new_rent_info, "normal", COLORS["success"])
                surface.blit(new_rent_surface, (self.x + 20, self.y + y_offset + 100))
            elif self.property_level == 4:
                max_level_info = "已达到最高等级"
                max_surface = render_text(max_level_info, "normal", COLORS["warning"])
                surface.blit(max_surface, (self.x + 20, self.y + y_offset + 70))
        
        # 绘制按钮
        self.close_button.draw(surface, {})
        if self.build_button:
            self.build_button.draw(surface, {})
        if self.upgrade_button:
            self.upgrade_button.draw(surface, {}) 