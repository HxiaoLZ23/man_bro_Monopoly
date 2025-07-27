"""
背包界面
"""
import pygame
import os
from typing import List, Dict, Optional, Callable
from src.ui.constants import COLORS, FONTS, FONT_PATH
from src.ui.components import Button, Panel, Text
from src.models.item import create_item_by_id
from src.models.player import Player


class InventoryWindow:
    """背包界面"""
    
    def __init__(self, player: Player, on_item_use: Optional[Callable] = None, on_close: Optional[Callable] = None):
        """
        初始化背包界面
        
        Args:
            player: 玩家对象
            on_item_use: 道具使用回调函数
            on_close: 关闭回调函数
        """
        self.player = player
        self.on_item_use = on_item_use
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
        self.item_buttons = []
        self.close_button = None
        
        # 道具图片缓存
        self.item_images = {}
        self.load_item_images()
        
        # 初始化界面
        self.init_ui()
        
        self.selected_index = None
    
    def load_item_images(self):
        """加载道具图片"""
        item_image_map = {
            1: "路障.jpeg",
            2: "再装逼让你飞起来.png", 
            3: "庇护术.png",
            4: "六百六十六.png",
            5: "违规爆建.jpeg"
        }
        
        items_path = "assets/images/items"
        
        for item_id, filename in item_image_map.items():
            try:
                image_path = os.path.join(items_path, filename)
                if os.path.exists(image_path):
                    # 加载并缩放图片
                    image = pygame.image.load(image_path)
                    # 缩放到合适大小
                    scaled_image = pygame.transform.scale(image, (64, 64))
                    self.item_images[item_id] = scaled_image
                else:
                    print(f"道具图片不存在: {image_path}")
            except Exception as e:
                print(f"加载道具图片失败 {filename}: {e}")
    
    def init_ui(self):
        """初始化UI"""
        # 标题
        title = Text(
            self.width // 2, 30, 
            f"{self.player.name}的背包", 
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
        
        # 创建道具按钮
        self.create_item_buttons()
    
    def create_item_buttons(self):
        """创建道具按钮"""
        self.item_buttons.clear()
        
        # 使用inventory属性（与主窗口保持一致）
        player_items = getattr(self.player, 'inventory', {}) or getattr(self.player, 'items', {})
        if not player_items:
            # 背包为空
            empty_text = Text(
                self.width // 2, self.height // 2,
                "背包为空", 
                FONTS["normal"], 
                align="center",
                color=COLORS["text_secondary"]
            )
            self.panels.append(empty_text)
            return
        
        # 计算布局
        items_per_row = 4
        item_width = 120
        item_height = 140
        start_x = 50
        start_y = 80
        spacing_x = 20
        spacing_y = 20
        
        row = 0
        col = 0
        
        for item_id, count in player_items.items():
            if count <= 0:
                continue
            
            # 计算位置
            x = start_x + col * (item_width + spacing_x)
            y = start_y + row * (item_height + spacing_y)
            
            # 创建道具按钮
            item_button = ItemButton(
                x, y, item_width, item_height,
                item_id, count, self.player,
                self.on_item_use,
                item_images=self.item_images
            )
            self.item_buttons.append(item_button)
            
            # 更新行列
            col += 1
            if col >= items_per_row:
                col = 0
                row += 1
    
    def on_item_select(self, item_id: int):
        # 只设置选中索引，不直接用道具
        for i, btn in enumerate(self.item_buttons):
            btn.is_selected = (btn.item_id == item_id)
            if btn.is_selected:
                self.selected_index = i
        # 不调用on_item_use
    
    def close(self):
        """关闭背包"""
        self.is_open = False  # 设置状态为关闭
        if self.on_close:
            self.on_close()
    
    def handle_event(self, event, offset_x=0, offset_y=0):
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # 检查关闭按钮 - 使用创建的按钮对象
            if self.close_button:
                close_button_rect = pygame.Rect(
                    self.x + self.close_button.x,
                    self.y + self.close_button.y,
                    self.close_button.width,
                    self.close_button.height
                )
                if close_button_rect.collidepoint(mouse_pos):
                    self.close()
                    return True
            
            # 检查道具按钮
            for i, btn in enumerate(self.item_buttons):
                if btn.handle_event(event, self.x, self.y):
                    for j, other in enumerate(self.item_buttons):
                        other.is_selected = (i == j)
                    self.selected_index = i
                    return True
        
        # 处理鼠标移动事件（用于悬停效果）
        if event.type == pygame.MOUSEMOTION:
            for btn in self.item_buttons:
                btn.handle_event(event, self.x, self.y)
        
        return False
    
    def draw(self, screen):
        """绘制背包界面"""
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
        
        for item_button in self.item_buttons:
            item_button.draw(screen, self.x, self.y)


class ItemButton:
    """道具按钮"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 item_id: int, count: int, player: Player, 
                 on_select: Callable[[int], None],
                 item_images: Dict[int, pygame.Surface]):
        """
        初始化道具按钮
        
        Args:
            x, y: 位置
            width, height: 尺寸
            item_id: 道具ID
            count: 数量
            player: 玩家对象
            on_select: 选择回调
            item_images: 道具图片缓存
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.item_id = item_id
        self.count = count
        self.player = player
        self.on_select = on_select
        self.item_images = item_images
        self.image = item_images.get(item_id) if item_images else None
        self.is_hovered = False
        self.is_selected = False
        self.use_button_rect = None
        # 获取道具信息
        self.item = create_item_by_id(item_id)
    
    def handle_event(self, event, offset_x=0, offset_y=0):
        if event.type not in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            return False
        local_pos = (event.pos[0] - offset_x, event.pos[1] - offset_y)
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(local_pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_selected and self.use_button_rect and self.use_button_rect.collidepoint(local_pos):
                if self.on_select:
                    self.on_select(self.item_id)
                return True
            if self.rect.collidepoint(local_pos):
                self.is_selected = True
                return True
        return False
    
    def on_click(self):
        """点击事件"""
        if self.on_select:
            self.on_select(self.item_id)
    
    def draw(self, screen, offset_x=0, offset_y=0):
        draw_rect = self.rect.move(offset_x, offset_y)
        bg_color = (220, 240, 255) if self.is_hovered or self.is_selected else (245, 245, 245)
        border_color = (52, 152, 219) if self.is_selected else (100, 150, 200)
        pygame.draw.rect(screen, bg_color, draw_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, draw_rect, 2, border_radius=8)
        # 图片
        if self.image:
            img_rect = pygame.Rect(draw_rect.x + 10, draw_rect.y + 10, 60, 60)
            img = pygame.transform.smoothscale(self.image, (60, 60))
            screen.blit(img, img_rect)
        else:
            img_rect = pygame.Rect(draw_rect.x + 10, draw_rect.y + 10, 60, 60)
            pygame.draw.rect(screen, (200,200,200), img_rect)
        # 中文字体
        if FONT_PATH:
            font = pygame.font.Font(FONT_PATH, 18)
        else:
            font = pygame.font.SysFont("msyh", 18)
        name = self.item.name if self.item else str(self.item_id)
        name_surface = font.render(name, True, (40, 40, 40))
        screen.blit(name_surface, (draw_rect.x + 80, draw_rect.y + 10))
        count_surface = font.render(f"x{self.count}", True, (80, 80, 80))
        screen.blit(count_surface, (draw_rect.x + self.width - 40, draw_rect.y + 10))
        # "使用"按钮
        if self.is_selected:
            btn_w, btn_h = 60, 28
            btn_x = self.rect.centerx - btn_w // 2
            btn_y = self.rect.bottom - btn_h - 8
            self.use_button_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)  # 局部坐标
            screen_btn_rect = self.use_button_rect.move(offset_x, offset_y)
            pygame.draw.rect(screen, (52, 152, 219), screen_btn_rect, border_radius=6)
            btn_font = font
            btn_text = btn_font.render("使用", True, (255,255,255))
            btn_text_rect = btn_text.get_rect(center=screen_btn_rect.center)
            screen.blit(btn_text, btn_text_rect)
        else:
            self.use_button_rect = None 