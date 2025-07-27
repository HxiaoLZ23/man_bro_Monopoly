"""
道具使用目标选择界面
"""
import pygame
import math
from typing import List, Dict, Optional, Callable, Tuple
from src.ui.constants import COLORS, FONTS
from src.ui.components import Button, Panel, Text
from src.models.player import Player
from src.models.map import Map
from src.models.item import create_item_by_id


class TargetSelectionWindow:
    """道具使用目标选择界面"""
    
    def __init__(self, player: Player, game_map: Map, item_id: int, 
                 on_target_select: Optional[Callable] = None,
                 map_origin: Tuple[int, int] = (0, 0), cell_size: int = 40):
        """
        初始化目标选择界面
        
        Args:
            player: 使用道具的玩家
            game_map: 游戏地图
            item_id: 道具ID
            on_target_select: 目标选择回调函数
            map_origin: 地图原点
            cell_size: 格子大小
        """
        self.player = player
        self.game_map = game_map
        self.item_id = item_id
        self.on_target_select = on_target_select
        self.map_origin = map_origin
        self.cell_size = cell_size
        
        # 界面尺寸
        self.width = 800
        self.height = 600
        self.x = 0
        self.y = 0
        
        # UI组件
        self.buttons = []
        self.panels = []
        self.target_buttons = []
        self.close_button = None
        
        # 获取道具信息
        self.item = create_item_by_id(item_id)
        
        # 初始化界面
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        # 标题
        title = Text(
            self.width // 2, 30, 
            f"选择{self.item.name if self.item else '道具'}的使用目标", 
            FONTS["title"], 
            align="center"
        )
        self.panels.append(title)
        
        # 道具描述
        if self.item:
            desc_text = Text(
                self.width // 2, 60,
                self.item.desc,
                FONTS["small"],
                align="center",
                color=COLORS["text_secondary"]
            )
            self.panels.append(desc_text)
        
        # 关闭按钮
        self.close_button = Button(
            self.width - 40, 10, 30, 30,
            "X", self.close, COLORS["error"]
        )
        self.buttons.append(self.close_button)
        
        # 创建目标选择按钮
        self.create_target_buttons()
    
    def create_target_buttons(self):
        """创建目标选择按钮"""
        self.target_buttons.clear()
        
        if self.item_id == 1:  # 路障
            self.create_roadblock_targets()
        elif self.item_id == 2:  # 再装逼让你飞起来
            self.create_fly_targets()
        else:
            # 其他道具不需要目标选择
            self.create_simple_targets()
    
    def create_roadblock_targets(self):
        """创建路障目标选择"""
        max_distance = 14
        player_pos = self.game_map.get_position_by_path_index(self.player.position)
        for x in range(self.game_map.width):
            for y in range(self.game_map.height):
                distance = math.sqrt((x - player_pos[0])**2 + (y - player_pos[1])**2)
                if distance <= max_distance:
                    cell = self.game_map.get_cell_at((x, y))
                    if cell and cell.cell_type in ["empty", "property"]:
                        target_button = RoadblockTargetButton(
                            x, y, cell, distance, self.player,
                            self.on_target_select,
                            self.map_origin, self.cell_size
                        )
                        self.target_buttons.append(target_button)
    
    def create_fly_targets(self):
        """创建飞行道具目标选择"""
        # 飞行道具可以对自身或同格玩家使用
        # 自身
        self_button = FlyTargetButton(
            "self", "自己", self.player, self.on_target_select
        )
        self.target_buttons.append(self_button)
        
        # 同格玩家（暂时简化，只显示自己）
        # 注意：这里需要游戏状态来获取同格玩家，暂时跳过
        # current_cell = self.game_map.get_cell_by_path_index(self.player.position)
        # if current_cell:
        #     for other_player in self.game_map.get_players_at_position(self.player.position):
        #         if other_player != self.player:
        #             other_button = FlyTargetButton(
        #                 "other", f"{other_player.name}", other_player, self.on_target_select
        #             )
        #             self.target_buttons.append(other_button)
    
    def create_simple_targets(self):
        """创建简单目标选择（不需要位置）"""
        # 对于不需要位置的道具，直接使用
        simple_button = SimpleTargetButton(
            "simple", "使用道具", self.player, self.on_target_select
        )
        self.target_buttons.append(simple_button)
    
    def on_target_select(self, target_info):
        """目标选择回调"""
        if self.on_target_select:
            self.on_target_select(target_info)
    
    def close(self):
        """关闭目标选择"""
        # 这里可以添加关闭逻辑
        pass
    
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # 检查关闭按钮
            if self.close_button and self.close_button.rect.collidepoint(mouse_pos):
                self.close()
                return True
            
            # 检查目标按钮
            for target_button in self.target_buttons:
                if target_button.rect.collidepoint(mouse_pos):
                    target_button.on_click()
                    return True
        
        return False
    
    def draw(self, screen):
        """绘制目标选择界面"""
        # 绘制背景
        background = pygame.Surface((self.width, self.height))
        background.fill(COLORS["background"])
        pygame.draw.rect(background, COLORS["border"], (0, 0, self.width, self.height), 3)
        screen.blit(background, (self.x, self.y))
        for panel in self.panels:
            panel.draw(screen)
        for button in self.buttons:
            button.draw(screen)
        for target_button in self.target_buttons:
            target_button.draw(screen, offset_x=self.x, offset_y=self.y)


class RoadblockTargetButton:
    """路障目标按钮"""
    
    def __init__(self, x: int, y: int, cell, distance: float, 
                 player: Player, on_select: Callable,
                 map_origin: Tuple[int, int], cell_size: int):
        """
        初始化路障目标按钮
        
        Args:
            x, y: 格子坐标
            cell: 格子对象
            distance: 距离
            player: 玩家对象
            on_select: 选择回调
            map_origin: 地图原点
            cell_size: 格子大小
        """
        self.x = x
        self.y = y
        self.cell = cell
        self.distance = distance
        self.player = player
        self.on_select = on_select
        self.map_origin = map_origin
        self.cell_size = cell_size
        self.width = cell_size
        self.height = cell_size
        self.rect = pygame.Rect(
            map_origin[0] + x * cell_size,
            map_origin[1] + y * cell_size,
            cell_size, cell_size
        )
    
    def on_click(self):
        """点击事件"""
        if self.on_select:
            self.on_select({
                "type": "roadblock",
                "position": (self.x, self.y),
                "distance": self.distance
            })
    
    def draw(self, screen, offset_x: int = 0, offset_y: int = 0):
        """绘制路障目标按钮"""
        color = COLORS["success"] if self.distance <= 10 else COLORS["warning"]
        rect = self.rect.move(offset_x, offset_y)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, COLORS["border"], rect, 2)


class FlyTargetButton:
    """飞行道具目标按钮"""
    
    def __init__(self, target_type: str, target_name: str, 
                 target_player: Player, on_select: Callable):
        """
        初始化飞行道具目标按钮
        
        Args:
            target_type: 目标类型 ("self" 或 "other")
            target_name: 目标名称
            target_player: 目标玩家
            on_select: 选择回调
        """
        self.target_type = target_type
        self.target_name = target_name
        self.target_player = target_player
        self.on_select = on_select
        
        # 按钮位置
        self.x = 100
        self.y = 150 + (len(self.target_buttons) if hasattr(self, 'target_buttons') else 0) * 60
        self.width = 200
        self.height = 50
        
        # 创建矩形
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def on_click(self):
        """点击事件"""
        if self.on_select:
            self.on_select({
                "type": "fly",
                "target_type": self.target_type,
                "target_player": self.target_player
            })
    
    def draw(self, screen, offset_x: int = 0, offset_y: int = 0):
        """绘制飞行道具目标按钮"""
        # 绘制背景
        bg_color = COLORS["primary"] if self.target_type == "self" else COLORS["secondary"]
        pygame.draw.rect(screen, bg_color, 
                        (self.x + offset_x, self.y + offset_y, self.width, self.height))
        
        # 绘制边框
        pygame.draw.rect(screen, COLORS["border"], 
                        (self.x + offset_x, self.y + offset_y, self.width, self.height), 2)
        
        # 绘制文本
        text = Text(
            self.x + self.width // 2, self.y + self.height // 2,
            self.target_name,
            FONTS["normal"],
            align="center"
        )
        text.draw(screen)


class SimpleTargetButton:
    """简单目标按钮（不需要位置的道具）"""
    
    def __init__(self, target_type: str, target_name: str, 
                 player: Player, on_select: Callable):
        """
        初始化简单目标按钮
        
        Args:
            target_type: 目标类型
            target_name: 目标名称
            player: 玩家对象
            on_select: 选择回调
        """
        self.target_type = target_type
        self.target_name = target_name
        self.player = player
        self.on_select = on_select
        
        # 按钮位置
        self.x = 100
        self.y = 150
        self.width = 200
        self.height = 50
        
        # 创建矩形
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def on_click(self):
        """点击事件"""
        if self.on_select:
            self.on_select({
                "type": "simple",
                "target_type": self.target_type
            })
    
    def draw(self, screen, offset_x: int = 0, offset_y: int = 0):
        """绘制简单目标按钮"""
        # 绘制背景
        pygame.draw.rect(screen, COLORS["primary"], 
                        (self.x + offset_x, self.y + offset_y, self.width, self.height))
        
        # 绘制边框
        pygame.draw.rect(screen, COLORS["border"], 
                        (self.x + offset_x, self.y + offset_y, self.width, self.height), 2)
        
        # 绘制文本
        text = Text(
            self.x + self.width // 2, self.y + self.height // 2,
            self.target_name,
            FONTS["normal"],
            align="center"
        )
        text.draw(screen) 