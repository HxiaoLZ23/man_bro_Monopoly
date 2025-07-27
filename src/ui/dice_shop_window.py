"""
骰子商店界面
"""
import pygame
from typing import Callable, Optional
from src.ui.components import Button
from src.ui.constants import COLORS
from src.ui.font_manager import get_font, render_text


class DiceShopWindow:
    """骰子商店窗口"""
    
    def __init__(self, on_close: Callable = None, on_purchase: Callable = None):
        """初始化骰子商店窗口"""
        self.on_close = on_close
        self.on_purchase = on_purchase
        self.visible = False
        
        # 窗口属性
        self.width = 800
        self.height = 600
        self.x = 0
        self.y = 0
        
        # 骰子商品信息
        self.dice_products = [
            {
                "id": "d8",
                "name": "d8骰",
                "description": "包含一枚8面骰",
                "price": 10000,
                "item_cost": 1,
                "image": "assets/images/dice/one_d8.jpeg"
            },
            {
                "id": "d12", 
                "name": "d12骰",
                "description": "包含一枚12面骰",
                "price": 50000,
                "item_cost": 1,
                "image": "assets/images/dice/one_d12.png"
            },
            {
                "id": "2d6",
                "name": "双d6骰",
                "description": "包含两枚6面骰",
                "price": 10000,
                "item_cost": 3,
                "image": "assets/images/dice/two_d6.jpg"
            },
            {
                "id": "2d8",
                "name": "双d8骰", 
                "description": "包含两枚8面骰",
                "price": 50000,
                "item_cost": 3,
                "image": "assets/images/dice/two_d8.jpg"
            },
            {
                "id": "3d6",
                "name": "三d6骰",
                "description": "包含三枚6面骰",
                "price": 40000,
                "item_cost": 4,
                "image": "assets/images/dice/three_d6.png"
            },
            {
                "id": "d20",
                "name": "d20神力!!",
                "description": "两枚20面骰，取最大值\n投出20有奖励，投出1有惩罚",
                "price": 77777,
                "item_cost": 7,
                "image": "assets/images/dice/d20.jpg"
            }
        ]
        
        # 加载图片
        self.dice_images = {}
        for product in self.dice_products:
            try:
                image = pygame.image.load(product["image"])
                self.dice_images[product["id"]] = pygame.transform.scale(image, (80, 80))
            except Exception as e:
                print(f"加载骰子图片失败: {product['image']}, 错误: {e}")
                # 创建占位符
                placeholder = pygame.Surface((80, 80))
                placeholder.fill(COLORS["secondary"])
                self.dice_images[product["id"]] = placeholder
        
        # 按钮
        self.buttons = []
        self.close_button = None
        
        # 当前玩家信息（由外部设置）
        self.player_money = 0
        self.player_items = 0
        
    def show(self, screen_width: int, screen_height: int, player_money: int, player_items: int):
        """显示窗口"""
        self.visible = True
        self.player_money = player_money
        self.player_items = player_items
        
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
        self.buttons = []
        
        # 关闭按钮
        self.close_button = Button(
            self.x + self.width - 100, self.y + 10, 80, 40,
            "关闭", lambda: self._handle_close(),
            font_size="normal"
        )
        
        # 为每个骰子创建购买按钮
        cols = 2
        rows = 3
        item_width = 350
        item_height = 150
        start_x = self.x + 50
        start_y = self.y + 80
        
        for i, product in enumerate(self.dice_products):
            row = i // cols
            col = i % cols
            
            btn_x = start_x + col * item_width + 200
            btn_y = start_y + row * item_height + 100
            
            # 检查是否可以购买
            can_afford = (self.player_money >= product["price"] and 
                         self.player_items >= product["item_cost"])
            
            # 创建购买按钮，使用闭包正确捕获product
            def create_purchase_callback(product_data):
                return lambda: self._handle_purchase(product_data)
            
            button = Button(
                btn_x, btn_y, 120, 35,
                "购买" if can_afford else "无法购买",
                create_purchase_callback(product) if can_afford else None,
                font_size="small",
                color=COLORS["success"] if can_afford else COLORS["disabled"]
            )
            button.can_afford = can_afford  # 添加自定义属性
            self.buttons.append(button)
    
    def _handle_close(self):
        """处理关闭"""
        self.hide()
        if self.on_close:
            self.on_close()
    
    def _handle_purchase(self, product):
        """处理购买"""
        if self.on_purchase:
            self.on_purchase(product)
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
                if hasattr(button, 'can_afford') and button.can_afford and button.rect.collidepoint(mouse_pos):
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
        title_surface = render_text("骰子商店", "large", COLORS["text_primary"], True)
        title_x = self.x + (self.width - title_surface.get_width()) // 2
        surface.blit(title_surface, (title_x, self.y + 20))
        
        # 绘制玩家信息
        info_text = f"金钱: ${self.player_money:,}  道具卡: {self.player_items}张"
        info_surface = render_text(info_text, "normal", COLORS["text_secondary"])
        surface.blit(info_surface, (self.x + 20, self.y + 50))
        
        # 绘制骰子商品
        cols = 2
        rows = 3
        item_width = 350
        item_height = 150
        start_x = self.x + 50
        start_y = self.y + 80
        
        for i, product in enumerate(self.dice_products):
            row = i // cols
            col = i % cols
            
            item_x = start_x + col * item_width
            item_y = start_y + row * item_height
            
            # 绘制商品背景
            item_rect = pygame.Rect(item_x, item_y, item_width - 20, item_height - 20)
            
            # 检查是否可以购买
            can_afford = (self.player_money >= product["price"] and 
                         self.player_items >= product["item_cost"])
            
            bg_color = COLORS["cell_empty"] if can_afford else COLORS["cell_void"]
            pygame.draw.rect(surface, bg_color, item_rect)
            pygame.draw.rect(surface, COLORS["text_primary"], item_rect, 2)
            
            # 绘制骰子图片
            if product["id"] in self.dice_images:
                image_x = item_x + 10
                image_y = item_y + 10
                surface.blit(self.dice_images[product["id"]], (image_x, image_y))
            
            # 绘制商品信息
            text_x = item_x + 100
            text_y = item_y + 10
            
            # 名称
            name_surface = render_text(product["name"], "subtitle", COLORS["text_primary"], True)
            surface.blit(name_surface, (text_x, text_y))
            
            # 描述
            desc_lines = product["description"].split('\n')
            for j, line in enumerate(desc_lines):
                desc_surface = render_text(line, "small", COLORS["text_secondary"])
                surface.blit(desc_surface, (text_x, text_y + 35 + j * 20))
            
            # 价格
            price_text = f"${product['price']:,} + {product['item_cost']}张道具卡"
            price_color = COLORS["success"] if can_afford else COLORS["error"]
            price_surface = render_text(price_text, "normal", price_color, True)
            surface.blit(price_surface, (text_x, text_y + 75))
        
        # 绘制按钮
        self.close_button.draw(surface, {})
        for button in self.buttons:
            button.draw(surface, {}) 