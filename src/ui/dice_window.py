"""
骰子包界面
"""
import pygame
import os
from typing import List, Dict, Optional, Callable
from src.ui.constants import COLORS, FONTS, FONT_PATH
from src.ui.components import Button, Panel, Text
from src.models.player import Player
from src.systems.dice_system import DiceSystem
from src.core.constants import DICE_TYPES

class DiceWindow:
    """骰子包界面"""
    
    def __init__(self, player: Player, dice_system, on_dice_select: Optional[Callable] = None, on_close: Optional[Callable] = None):
        """
        初始化骰子包窗口
        
        Args:
            player: 玩家对象
            dice_system: 骰子系统
            on_dice_select: 骰子选择回调
            on_close: 关闭回调
        """
        self.player = player
        self.dice_system = dice_system
        self.on_dice_select = on_dice_select
        self.on_close = on_close
        
        # 窗口状态
        self.is_open = True  # 添加状态属性，与其他窗口保持一致
        
        # 界面尺寸
        self.width = 600
        self.height = 500
        self.x = 0
        self.y = 0
        
        # UI组件
        self.buttons = []
        self.panels = []
        self.dice_buttons = []
        self.close_button = None
        
        # 骰子图片缓存
        self.dice_images = {}
        self.load_dice_images()
        
        # 字体初始化（必须在pygame.init之后）
        if FONT_PATH:
            self.cn_font = pygame.font.Font(FONT_PATH, 28)
            self.cn_font_big = pygame.font.Font(FONT_PATH, 36)
            self.cn_font_mid = pygame.font.Font(FONT_PATH, 28)
            self.cn_font_small = pygame.font.Font(FONT_PATH, 24)
        else:
            self.cn_font = pygame.font.SysFont("msyh", 28)
            self.cn_font_big = pygame.font.SysFont("msyh", 36)
            self.cn_font_mid = pygame.font.SysFont("msyh", 28)
            self.cn_font_small = pygame.font.SysFont("msyh", 24)
        
        # 初始化界面
        self.init_ui()
    
    def load_dice_images(self):
        """加载骰子图片"""
        dice_image_map = {
            "d6": "one_d6.jpeg",
            "d8": "one_d8.jpeg",
            "d12": "one_d12.png",
            "2d6": "two_d6.jpg",
            "2d8": "two_d8.jpg",
            "3d6": "three_d6.png",
            "2d20": "d20.jpg"
        }
        
        dice_path = "assets/images/dice"
        
        for dice_type, filename in dice_image_map.items():
            try:
                image_path = os.path.join(dice_path, filename)
                if os.path.exists(image_path):
                    # 加载并缩放图片
                    image = pygame.image.load(image_path)
                    # 缩放到合适大小
                    scaled_image = pygame.transform.scale(image, (80, 80))
                    self.dice_images[dice_type] = scaled_image
                else:
                    print(f"骰子图片不存在: {image_path}")
            except Exception as e:
                print(f"加载骰子图片失败 {filename}: {e}")
    
    def init_ui(self):
        """初始化UI"""
        # 标题
        title = Text(
            self.width // 2, 30, 
            f"{self.player.name}的骰子包", 
            FONTS["title"], 
            align="center"
        )
        self.panels.append(title)
        
        # 返回按钮 - 放在左下角
        self.close_button = Button(
            20, self.height - 50, 80, 35,
            "返回", self.close, COLORS["secondary"]
        )
        self.buttons.append(self.close_button)
        
        # 创建骰子按钮
        self.create_dice_buttons()
    
    def create_dice_buttons(self):
        """创建骰子按钮"""
        self.dice_buttons.clear()
        
        # 获取玩家可用的骰子
        available_dice = self.dice_system.get_available_dice_types()
        
        if not available_dice:
            # 没有骰子
            empty_text = Text(
                self.width // 2, self.height // 2,
                "没有可用的骰子", 
                FONTS["normal"], 
                align="center",
                color=COLORS["text_secondary"]
            )
            self.panels.append(empty_text)
            return
        
        # 计算布局
        items_per_row = 3
        item_width = 150
        item_height = 180
        start_x = 50
        start_y = 100
        spacing_x = 30
        spacing_y = 30
        
        row = 0
        col = 0
        
        for dice_type in available_dice:
            # 计算位置
            x = start_x + col * (item_width + spacing_x)
            y = start_y + row * (item_height + spacing_y)
            
            # 检查是否为当前骰子
            is_current = (dice_type == self.player.dice)
            
            # 获取骰组信息
            dice_info = DICE_TYPES.get(dice_type, {"sides": 6, "count": 1})
            dice_name = f"{dice_type}"
            dice_desc = f"{dice_info['count']}枚d{dice_info['sides']}"
            
            # 创建骰子按钮
            dice_button = DiceButton(
                x, y, item_width, item_height,
                dice_type, is_current, self.player,
                self.on_dice_select,
                dice_name=dice_name,
                dice_desc=dice_desc,
                cn_font=self.cn_font,
                cn_font_big=self.cn_font_big,
                cn_font_mid=self.cn_font_mid,
                cn_font_small=self.cn_font_small,
                dice_images=self.dice_images
            )
            self.dice_buttons.append(dice_button)
            
            # 更新行列
            col += 1
            if col >= items_per_row:
                col = 0
                row += 1
    
    def on_dice_select(self, dice_type: str):
        """骰子选择回调"""
        if self.on_dice_select:
            self.on_dice_select(dice_type)
    
    def close(self):
        """关闭骰子包"""
        self.is_open = False  # 设置状态为关闭
        if self.on_close:
            self.on_close()
    
    def refresh(self):
        """刷新骰子列表"""
        # 清除旧的UI组件
        self.panels = []
        self.buttons = []
        self.dice_buttons = []
        
        # 重新初始化UI
        self.init_ui()
    
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # 检查关闭按钮 - 考虑窗口偏移
            close_button_rect = pygame.Rect(
                self.x + self.close_button.x,
                self.y + self.close_button.y,
                self.close_button.width,
                self.close_button.height
            )
            if close_button_rect.collidepoint(mouse_pos):
                self.close()
                return True
            
            # 检查骰子按钮 - 考虑窗口偏移
            for dice_button in self.dice_buttons:
                button_rect = pygame.Rect(
                    self.x + dice_button.x,
                    self.y + dice_button.y,
                    dice_button.width,
                    dice_button.height
                )
                if button_rect.collidepoint(mouse_pos):
                    dice_button.on_click()
                    return True
        
        return False
    
    def draw(self, screen):
        """绘制骰子包界面"""
        # 绘制背景
        background = pygame.Surface((self.width, self.height))
        background.fill(COLORS["background"])
        
        # 绘制边框
        pygame.draw.rect(background, COLORS["border"], (0, 0, self.width, self.height), 3)
        
        # 绘制到屏幕
        screen.blit(background, (self.x, self.y))
        
        # 绘制UI组件
        for panel in self.panels:
            panel.draw(screen)
        
        # 绘制返回按钮 - 直接在窗口内绘制
        if self.close_button:
            button_rect = pygame.Rect(
                self.x + self.close_button.x,
                self.y + self.close_button.y,
                self.close_button.width,
                self.close_button.height
            )
            # 绘制按钮背景
            pygame.draw.rect(screen, self.close_button.color, button_rect, border_radius=5)
            pygame.draw.rect(screen, COLORS["border"], button_rect, 2, border_radius=5)
            
            # 绘制按钮文字
            from src.ui.font_manager import render_text
            text_surface = render_text(self.close_button.text, "normal", COLORS["text_light"], True)
            text_rect = text_surface.get_rect(center=button_rect.center)
            screen.blit(text_surface, text_rect)
        
        for dice_button in self.dice_buttons:
            dice_button.draw(screen, self.x, self.y)


class DiceButton:
    """骰子按钮"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 dice_type: str, is_current: bool, player: Player, 
                 on_select: Callable[[str], None], dice_name: str = "", dice_desc: str = "",
                 cn_font=None, cn_font_big=None, cn_font_mid=None, cn_font_small=None,
                 dice_images=None):
        """
        初始化骰子按钮
        
        Args:
            x, y: 位置
            width, height: 尺寸
            dice_type: 骰子类型
            is_current: 是否为当前骰子
            player: 玩家对象
            on_select: 选择回调
            dice_name: 骰组名称
            dice_desc: 骰组描述
            cn_font: 中文小字体
            cn_font_big: 中文大字体
            cn_font_mid: 中文中字体
            cn_font_small: 中文小字体
            dice_images: 骰子图片缓存
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.dice_type = dice_type
        self.is_current = is_current
        self.player = player
        self.on_select = on_select
        self.dice_name = dice_name
        self.dice_desc = dice_desc
        self.cn_font = cn_font
        self.cn_font_big = cn_font_big
        self.cn_font_mid = cn_font_mid
        self.cn_font_small = cn_font_small
        self.dice_images = dice_images
        
        # 创建矩形
        self.rect = pygame.Rect(x, y, width, height)
        
        # 获取骰子信息
        self.dice_info = self.player.dice_system.get_dice_info(dice_type)
        
        # 加载图片
        self.image = None
        self.load_image()
    
    def load_image(self):
        """加载骰子图片"""
        if self.dice_images and self.dice_type in self.dice_images:
            self.image = self.dice_images[self.dice_type]
        else:
            self.image = None
    
    def on_click(self):
        """点击事件"""
        if self.on_select:
            self.on_select(self.dice_type)
    
    def draw(self, screen, offset_x: int = 0, offset_y: int = 0):
        """绘制骰子按钮"""
        # 高亮当前骰组
        if self.is_current:
            bg_color = COLORS["success"]
        else:
            bg_color = COLORS["panel"]
        pygame.draw.rect(screen, bg_color, 
                        (self.x + offset_x, self.y + offset_y, self.width, self.height))
        border_color = COLORS["primary"] if self.is_current else COLORS["border"]
        pygame.draw.rect(screen, border_color, 
                        (self.x + offset_x, self.y + offset_y, self.width, self.height), 3)
        # 骰子图片
        if self.image:
            image_x = self.x + offset_x + (self.width - 80) // 2
            image_y = self.y + offset_y + 10
            screen.blit(self.image, (image_x, image_y))
        else:
            placeholder_rect = pygame.Rect(
                self.x + offset_x + (self.width - 80) // 2,
                self.y + offset_y + 10,
                80, 80
            )
            pygame.draw.rect(screen, COLORS["divider"], placeholder_rect)
            pygame.draw.rect(screen, COLORS["border"], placeholder_rect, 2)
            text_surface = self.cn_font.render(self.dice_type, True, (255,0,0))
            text_rect = text_surface.get_rect(center=placeholder_rect.center)
            screen.blit(text_surface, text_rect)
        # 骰组名称
        name_surface = self.cn_font_big.render(self.dice_name, True, (255,0,0))
        name_rect = name_surface.get_rect(center=(self.x + offset_x + self.width // 2, self.y + offset_y + 120))
        screen.blit(name_surface, name_rect)
        # 骰组描述
        desc_surface = self.cn_font_mid.render(self.dice_desc, True, (255,0,0))
        desc_rect = desc_surface.get_rect(center=(self.x + offset_x + self.width // 2, self.y + offset_y + 160))
        screen.blit(desc_surface, desc_rect)
        # 当前使用
        if self.is_current:
            current_surface = self.cn_font_small.render("当前使用", True, (255,0,0))
            current_rect = current_surface.get_rect(center=(self.x + offset_x + self.width // 2, self.y + offset_y + 190))
            screen.blit(current_surface, current_rect) 