"""
岔路选择界面
"""
import pygame
from typing import List, Dict, Optional, Callable
from src.ui.constants import COLORS, FONTS
from src.ui.components import Button, Panel, Text
from src.models.player import Player
from src.models.map import Map
from src.ui.font_manager import render_text


class JunctionSelectionWindow:
    """岔路选择界面"""
    
    def __init__(self, player: Player, game_map: Map, current_position: int,
                 available_directions: List[int], on_direction_selected: Optional[Callable] = None):
        """
        初始化岔路选择界面
        
        Args:
            player: 当前玩家
            game_map: 游戏地图
            current_position: 当前位置路径索引
            available_directions: 可用方向列表
            on_direction_selected: 方向选择回调函数
        """
        self.player = player
        self.game_map = game_map
        self.current_position = current_position
        self.available_directions = available_directions
        self.on_direction_selected = on_direction_selected
        
        # 界面尺寸和位置
        self.width = 500
        self.height = 400
        self.x = (800 - self.width) // 2  # 假设屏幕宽度800
        self.y = (600 - self.height) // 2  # 假设屏幕高度600
        
        # UI组件
        self.buttons = []
        self.panels = []
        self.direction_buttons = []
        
        # 初始化界面
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        # 背景面板
        background = Panel(self.x, self.y, self.width, self.height, "", COLORS["background"])
        self.panels.append(background)
        
        # 标题
        title = Text(
            self.x + self.width // 2, self.y + 30,
            f"{self.player.name}，请选择前进方向",
            "title",
            align="center",
            color=COLORS["text_primary"]
        )
        self.panels.append(title)
        
        # 当前位置信息
        current_pos_info = self.game_map.get_position_by_path_index(self.current_position)
        pos_text = Text(
            self.x + self.width // 2, self.y + 70,
            f"当前位置: 路径索引 {self.current_position} ({current_pos_info})",
            "normal",
            align="center",
            color=COLORS["text_secondary"]
        )
        self.panels.append(pos_text)
        
        # 创建方向选择按钮
        self.create_direction_buttons()
        
        # 关闭按钮
        close_button = Button(
            self.x + self.width - 40, self.y + 10, 30, 30,
            "X", self.close, COLORS["error"]
        )
        self.buttons.append(close_button)
    
    def create_direction_buttons(self):
        """创建方向选择按钮"""
        self.direction_buttons.clear()
        
        start_y = self.y + 120
        button_height = 50
        button_spacing = 60
        
        for i, direction in enumerate(self.available_directions):
            # 获取目标位置信息
            target_pos = self.game_map.get_position_by_path_index(direction)
            target_cell = self.game_map.get_cell_by_path_index(direction)
            
            # 创建按钮文本
            if target_cell:
                cell_type_name = {
                    "empty": "空地",
                    "shop": "道具商店", 
                    "dice_shop": "骰子商店",
                    "bank": "银行",
                    "jail": "监狱",
                    "luck": "好运格",
                    "bad_luck": "厄运格"
                }.get(target_cell.cell_type, target_cell.cell_type)
                
                button_text = f"方向 {direction}: {target_pos} ({cell_type_name})"
            else:
                button_text = f"方向 {direction}: {target_pos}"
            
            # 创建按钮
            button = Button(
                self.x + 50, start_y + i * button_spacing,
                self.width - 100, button_height,
                button_text,
                lambda d=direction: self.select_direction(d),
                COLORS["primary"]
            )
            self.direction_buttons.append(button)
    
    def select_direction(self, direction: int):
        """选择方向"""
        if self.on_direction_selected:
            self.on_direction_selected(direction)
    
    def close(self):
        """关闭窗口"""
        # 如果没有选择方向，默认选择第一个可用方向
        if self.available_directions and self.on_direction_selected:
            self.on_direction_selected(self.available_directions[0])
    
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 检查关闭按钮
            for button in self.buttons:
                if button.handle_event(event):
                    return True
            
            # 检查方向按钮
            for button in self.direction_buttons:
                if button.handle_event(event):
                    return True
        
        elif event.type == pygame.KEYDOWN:
            # 键盘快捷键
            if event.key == pygame.K_ESCAPE:
                self.close()
                return True
            elif pygame.K_1 <= event.key <= pygame.K_9:
                # 数字键选择方向
                index = event.key - pygame.K_1
                if 0 <= index < len(self.available_directions):
                    self.select_direction(self.available_directions[index])
                    return True
        
        # 处理鼠标移动事件（用于按钮悬停效果）
        elif event.type == pygame.MOUSEMOTION:
            for button in self.buttons:
                button.handle_event(event)
            for button in self.direction_buttons:
                button.handle_event(event)
        
        return False
    
    def draw(self, screen):
        """绘制界面"""
        # 绘制背景
        background_surface = pygame.Surface((self.width, self.height))
        background_surface.fill(COLORS["background"])
        pygame.draw.rect(background_surface, COLORS["border"], (0, 0, self.width, self.height), 3)
        screen.blit(background_surface, (self.x, self.y))
        
        # 绘制文本
        for panel in self.panels:
            if hasattr(panel, 'draw'):
                panel.draw(screen)
        
        # 绘制按钮
        for button in self.buttons:
            button.draw(screen)
        
        for button in self.direction_buttons:
            button.draw(screen)
        
        # 绘制提示信息
        hint_text = "按数字键1-9快速选择，ESC键关闭"
        hint_surface = render_text(hint_text, "small", COLORS["text_secondary"], True)
        hint_rect = hint_surface.get_rect()
        hint_rect.centerx = self.x + self.width // 2
        hint_rect.bottom = self.y + self.height - 10
        screen.blit(hint_surface, hint_rect) 