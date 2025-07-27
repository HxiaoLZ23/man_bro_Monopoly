"""
道具商店界面
"""
import pygame
import random
from typing import Callable, Optional, List, Dict
from src.ui.components import Button
from src.ui.constants import COLORS
from src.ui.font_manager import get_font, render_text


class ItemShopWindow:
    """道具商店窗口"""
    
    def __init__(self, on_close: Callable = None, on_purchase: Callable = None):
        """初始化道具商店窗口"""
        self.on_close = on_close
        self.on_purchase = on_purchase
        self.visible = False
        
        # 窗口属性
        self.width = 700
        self.height = 500
        self.x = 0
        self.y = 0
        
        # 所有道具信息
        self.all_items = [
            {
                "id": 1,
                "name": "路障",
                "description": "在距自身直线距离不超过14的格子上\n放置一个路障，使经过的玩家停止移动",
                "price": 10000,
                "image": "assets/images/items/路障.jpeg"
            },
            {
                "id": 2,
                "name": "再装逼让你飞起来!!",
                "description": "对自身或同格玩家使用，获得【起飞】\n下次移动无视地图限制，但落地后\n身上所有钱散落在周围格子",
                "price": 20000,
                "image": "assets/images/items/再装逼让你飞起来.png"
            },
            {
                "id": 3,
                "name": "庇护术",
                "description": "直到下次使用道具卡为止\n不会受到任何道具的影响",
                "price": 20000,
                "image": "assets/images/items/庇护术.png"
            },
            {
                "id": 4,
                "name": "六百六十六",
                "description": "下次投掷时每个骰子的结果总为6",
                "price": 15000,
                "image": "assets/images/items/六百六十六.png"
            },
            {
                "id": 5,
                "name": "违规爆建",
                "description": "使自身的一处房产升一级\n或使别人的一处房产降一级\n（无法降级四级房产）",
                "price": 25000,
                "image": "assets/images/items/违规爆建.jpeg"
            }
        ]
        
        # 加载图片
        self.item_images = {}
        for item in self.all_items:
            try:
                image = pygame.image.load(item["image"])
                self.item_images[item["id"]] = pygame.transform.scale(image, (100, 100))
            except Exception as e:
                print(f"加载道具图片失败: {item['image']}, 错误: {e}")
                # 创建占位符
                placeholder = pygame.Surface((100, 100))
                placeholder.fill(COLORS["secondary"])
                self.item_images[item["id"]] = placeholder
        
        # 当前显示的商品（随机2个）
        self.current_items = []
        
        # 按钮
        self.buttons = []
        self.close_button = None
        self.refresh_button = None
        
        # 当前玩家信息（由外部设置）
        self.player_money = 0
        
    def show(self, screen_width: int, screen_height: int, player_money: int):
        """显示窗口"""
        self.visible = True
        self.player_money = player_money
        
        # 居中显示
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        
        # 随机选择2个道具
        self._refresh_items()
        
        # 创建按钮
        self._create_buttons()
    
    def hide(self):
        """隐藏窗口"""
        self.visible = False
        
    def _refresh_items(self):
        """刷新商品（随机选择2个）"""
        self.current_items = random.sample(self.all_items, 2)
        
    def _create_buttons(self):
        """创建按钮"""
        self.buttons = []
        
        # 关闭按钮
        self.close_button = Button(
            self.x + self.width - 100, self.y + 10, 80, 40,
            "关闭", lambda: self._handle_close(),
            font_size="normal"
        )
        
        # 为每个道具创建购买按钮
        item_width = 300
        item_height = 250
        start_x = self.x + 50
        start_y = self.y + 80
        
        for i, item in enumerate(self.current_items):
            btn_x = start_x + i * item_width + 90  # 调整按钮位置
            btn_y = start_y + item_height - 50
            
            # 检查是否可以购买
            can_afford = self.player_money >= item["price"]
            
            # 创建购买按钮，使用闭包正确捕获item
            def create_purchase_callback(item_data):
                return lambda: self._handle_purchase(item_data)
            
            button = Button(
                btn_x, btn_y, 120, 35,
                "购买" if can_afford else "金钱不足",
                create_purchase_callback(item) if can_afford else None,
                font_size="small",
                color=COLORS["success"] if can_afford else COLORS["disabled"]
            )
            button.enabled = can_afford  # 添加自定义属性
            self.buttons.append(button)
    
    def _handle_close(self):
        """处理关闭"""
        self.hide()
        if self.on_close:
            self.on_close()
    
    def _handle_purchase(self, item):
        """处理购买"""
        if self.on_purchase:
            self.on_purchase(item)
            # 购买后关闭窗口
            self.hide()
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件"""
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # 检查关闭按钮
            if self.close_button.rect.collidepoint(mouse_pos):
                self.close_button.callback()
                return True
            
            # 检查购买按钮
            for button in self.buttons:
                if hasattr(button, 'enabled') and button.enabled and button.rect.collidepoint(mouse_pos):
                    if button.callback:
                        button.callback()
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
        title_surface = render_text("道具商店", "large", COLORS["text_primary"], True)
        title_x = self.x + (self.width - title_surface.get_width()) // 2
        surface.blit(title_surface, (title_x, self.y + 20))
        
        # 绘制玩家信息
        info_text = f"金钱: ${self.player_money:,}  (仅可使用身上余额)"
        info_surface = render_text(info_text, "normal", COLORS["text_secondary"])
        surface.blit(info_surface, (self.x + 20, self.y + 50))
        
        # 绘制道具商品
        item_width = 300
        item_height = 250
        start_x = self.x + 50
        start_y = self.y + 80
        
        for i, item in enumerate(self.current_items):
            item_x = start_x + i * item_width
            item_y = start_y
            
            # 绘制商品背景
            item_rect = pygame.Rect(item_x, item_y, item_width - 20, item_height)
            
            # 检查是否可以购买
            can_afford = self.player_money >= item["price"]
            
            bg_color = COLORS["cell_empty"] if can_afford else COLORS["cell_void"]
            pygame.draw.rect(surface, bg_color, item_rect)
            pygame.draw.rect(surface, COLORS["text_primary"], item_rect, 2)
            
            # 绘制道具图片
            if item["id"] in self.item_images:
                image_x = item_x + (item_width - 120) // 2
                image_y = item_y + 10
                surface.blit(self.item_images[item["id"]], (image_x, image_y))
            
            # 绘制商品信息
            text_x = item_x + 10
            text_y = item_y + 120
            
            # 名称
            name_surface = render_text(item["name"], "subtitle", COLORS["text_primary"], True)
            name_x = item_x + (item_width - name_surface.get_width()) // 2
            surface.blit(name_surface, (name_x, text_y))
            
            # 描述
            desc_lines = item["description"].split('\n')
            for j, line in enumerate(desc_lines):
                desc_surface = render_text(line, "tiny", COLORS["text_secondary"])
                desc_x = item_x + (item_width - desc_surface.get_width()) // 2
                surface.blit(desc_surface, (desc_x, text_y + 35 + j * 16))
            
            # 价格
            price_text = f"${item['price']:,}"
            price_color = COLORS["success"] if can_afford else COLORS["error"]
            price_surface = render_text(price_text, "normal", price_color, True)
            price_x = item_x + (item_width - price_surface.get_width()) // 2
            surface.blit(price_surface, (price_x, text_y + 120))
        
        # 绘制按钮
        self.close_button.draw(surface, {})
        for button in self.buttons:
            button.draw(surface, {}) 