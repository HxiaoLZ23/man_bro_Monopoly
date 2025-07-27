"""
UI基础组件
"""
import pygame
from typing import Tuple, Optional, Callable, List
from src.ui.constants import COLORS, LAYOUT, FONTS
from src.ui.font_manager import get_font, render_text, get_text_size


class Button:
    """按钮组件"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 callback: Callable = None, color: Tuple[int, int, int] = None,
                 text_color: Tuple[int, int, int] = None, font_size: str = "normal"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.callback = callback
        self.color = color or COLORS["primary"]
        self.text_color = text_color or COLORS["text_primary"]
        self.font_size = font_size
        self.rect = pygame.Rect(x, y, width, height)
        self.is_hovered = False
        self.enabled = True  # 添加enabled属性
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件"""
        if not self.enabled:  # 检查是否启用
            return False
            
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.callback:
                self.callback()
                return True
        return False
    
    def draw(self, surface: pygame.Surface, fonts: dict = None):
        """绘制按钮"""
        # 根据enabled状态选择颜色
        if not self.enabled:
            button_color = COLORS["disabled"]
            text_color = COLORS["text_secondary"]
        elif self.is_hovered:
            # 悬停时颜色稍微变亮
            button_color = tuple(min(255, c + 20) for c in self.color)
            text_color = self.text_color
        else:
            button_color = self.color
            text_color = self.text_color
        
        # 绘制按钮背景
        pygame.draw.rect(surface, button_color, self.rect, border_radius=LAYOUT["border_radius"])
        
        # 绘制文本
        text_surface = render_text(self.text, self.font_size, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class Panel:
    """面板组件"""
    
    def __init__(self, x: int, y: int, width: int, height: int, title: str = "",
                 color: Tuple[int, int, int] = None, border_color: Tuple[int, int, int] = None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        self.color = color or COLORS["panel"]
        self.border_color = border_color or COLORS["border"]
        self.rect = pygame.Rect(x, y, width, height)
        
    def draw(self, surface: pygame.Surface, fonts: dict = None):
        """绘制面板"""
        # 绘制面板背景
        pygame.draw.rect(surface, self.color, self.rect, border_radius=LAYOUT["border_radius"])
        pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=LAYOUT["border_radius"])
        
        # 绘制标题
        if self.title:
            title_surface = render_text(self.title, "subtitle", COLORS["text_primary"], True)
            title_rect = title_surface.get_rect(center=(self.rect.centerx, self.rect.y + 30))
            surface.blit(title_surface, title_rect)


class Text:
    """文本组件"""
    
    def __init__(self, x: int, y: int, text: str, font_size: str = "normal", 
                 color: Tuple[int, int, int] = None, align: str = "left"):
        self.x = x
        self.y = y
        self.text = text
        self.font_size = font_size  # 使用字体大小名称而不是像素值
        self.color = color or COLORS["text_primary"]
        self.align = align  # "left", "center", "right"
        
    def draw(self, surface: pygame.Surface, fonts: dict = None):
        """绘制文本"""
        # 使用全局字体管理器渲染文本
        text_surface = render_text(self.text, self.font_size, self.color, True)
        
        if self.align == "center":
            text_rect = text_surface.get_rect(center=(self.x, self.y))
        elif self.align == "right":
            text_rect = text_surface.get_rect(right=self.x, top=self.y)
        else:  # left
            text_rect = text_surface.get_rect(left=self.x, top=self.y)
        
        surface.blit(text_surface, text_rect)


class Dialog:
    """对话框组件"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 title: str = "", content: str = "", buttons: List[dict] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.content = content
        self.buttons = buttons or []
        self.is_visible = False
        self.result = None
        
        # 创建按钮组件
        self.button_components = []
        self._create_buttons()
        
    def _create_buttons(self):
        """创建按钮组件"""
        self.button_components.clear()
        
        if not self.buttons:
            # 默认确定按钮
            self.buttons = [{"text": "确定", "callback": self.close, "color": COLORS["primary"]}]
        
        button_width = 80
        button_height = 30
        button_spacing = 10
        total_width = len(self.buttons) * button_width + (len(self.buttons) - 1) * button_spacing
        start_x = self.rect.centerx - total_width // 2
        
        for i, button_data in enumerate(self.buttons):
            button_x = start_x + i * (button_width + button_spacing)
            button_y = self.rect.bottom - button_height - 20
            
            button = Button(
                button_x, button_y, button_width, button_height,
                button_data["text"],
                button_data.get("callback"),
                button_data.get("color", COLORS["primary"]),
                button_data.get("text_color"),
                button_data.get("font_size", "normal")
            )
            self.button_components.append(button)
    
    def show(self):
        """显示对话框"""
        self.is_visible = True
        self.result = None
    
    def close(self, result=None):
        """关闭对话框"""
        self.is_visible = False
        self.result = result
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件"""
        if not self.is_visible:
            return False
        
        # 处理按钮事件
        for button in self.button_components:
            if button.handle_event(event):
                return True
        
        return False
    
    def draw(self, surface: pygame.Surface, fonts: dict = None):
        """绘制对话框"""
        if not self.is_visible:
            return
        
        # 绘制半透明背景
        overlay = pygame.Surface(surface.get_size())
        overlay.set_alpha(128)
        overlay.fill(COLORS["background"])
        surface.blit(overlay, (0, 0))
        
        # 绘制对话框背景
        pygame.draw.rect(surface, COLORS["surface"], self.rect, border_radius=LAYOUT["border_radius"])
        pygame.draw.rect(surface, COLORS["text_primary"], self.rect, 2, border_radius=LAYOUT["border_radius"])
        
        # 绘制标题
        if self.title and fonts and "subtitle" in fonts:
            font = fonts["subtitle"]
            title_surface = font.render(self.title, True, COLORS["text_primary"])
            title_rect = title_surface.get_rect(
                x=self.rect.x + LAYOUT["padding"],
                y=self.rect.y + LAYOUT["padding"]
            )
            surface.blit(title_surface, title_rect)
        
        # 绘制内容
        if self.content and fonts and "normal" in fonts:
            font = fonts["normal"]
            # 简单的文本换行处理
            words = self.content.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if get_text_size(test_line, "normal")[0] <= self.rect.width - 2 * LAYOUT["padding"]:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            content_y = self.rect.y + 60
            for line in lines:
                line_surface = font.render(line, True, COLORS["text_primary"])
                line_rect = line_surface.get_rect(
                    x=self.rect.x + LAYOUT["padding"],
                    y=content_y
                )
                surface.blit(line_surface, line_rect)
                content_y += 25
        
        # 绘制按钮
        for button in self.button_components:
            button.draw(surface, fonts)


class Image:
    """图片组件"""
    
    def __init__(self, x: int, y: int, image_path: str, scale: float = 1.0):
        self.x = x
        self.y = y
        self.scale = scale
        self.image = None
        self.load_image(image_path)
        
    def load_image(self, image_path: str):
        """加载图片"""
        try:
            self.image = pygame.image.load(image_path)
            if self.scale != 1.0:
                new_size = (int(self.image.get_width() * self.scale), 
                           int(self.image.get_height() * self.scale))
                self.image = pygame.transform.scale(self.image, new_size)
        except pygame.error:
            print(f"无法加载图片: {image_path}")
            self.image = None
    
    def draw(self, surface: pygame.Surface):
        """绘制图片"""
        if self.image:
            surface.blit(self.image, (self.x, self.y))


class ProgressBar:
    """进度条组件"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 value: float = 0.0, max_value: float = 100.0,
                 color: Tuple[int, int, int] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.value = value
        self.max_value = max_value
        self.color = color or COLORS["primary"]
        
    def set_value(self, value: float):
        """设置进度值"""
        self.value = max(0, min(value, self.max_value))
        
    def draw(self, surface: pygame.Surface):
        """绘制进度条"""
        # 绘制背景
        pygame.draw.rect(surface, COLORS["text_secondary"], self.rect, border_radius=LAYOUT["border_radius"])
        
        # 绘制进度
        if self.max_value > 0:
            progress_width = int((self.value / self.max_value) * self.rect.width)
            progress_rect = pygame.Rect(self.rect.x, self.rect.y, progress_width, self.rect.height)
            pygame.draw.rect(surface, self.color, progress_rect, border_radius=LAYOUT["border_radius"])
        
        # 绘制边框
        pygame.draw.rect(surface, COLORS["text_primary"], self.rect, 1, border_radius=LAYOUT["border_radius"])


class Message:
    """消息提示组件"""
    
    def __init__(self, text: str, message_type: str = "info", duration: float = 3.0):
        self.text = text
        self.type = message_type  # "info", "success", "warning", "error"
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.alpha = 255
        
        # 根据类型选择颜色
        self.color_map = {
            "info": COLORS["info"],
            "success": COLORS["success"],
            "warning": COLORS["warning"],
            "error": COLORS["error"]
        }
        
        self.color = self.color_map.get(message_type, COLORS["info"])
    
    def is_expired(self) -> bool:
        """检查消息是否过期"""
        return pygame.time.get_ticks() - self.start_time > self.duration * 1000
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font, x: int, y: int):
        """绘制消息"""
        # 计算透明度
        elapsed = pygame.time.get_ticks() - self.start_time
        if elapsed > (self.duration - 0.5) * 1000:
            self.alpha = int(255 * (1 - (elapsed - (self.duration - 0.5) * 1000) / 500))
        
        # 创建文本表面
        text_surface = font.render(self.text, True, self.color)
        
        # 设置透明度
        if self.alpha < 255:
            text_surface.set_alpha(self.alpha)
        
        # 绘制文本
        surface.blit(text_surface, (x, y)) 