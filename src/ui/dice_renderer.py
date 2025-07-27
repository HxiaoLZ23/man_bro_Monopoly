"""
骰子渲染器
支持2D和伪3D骰子渲染效果，支持多种骰子类型
"""
import pygame
import math
import random
from typing import Tuple, List, Optional


class DiceRenderer:
    """骰子渲染器"""
    
    def __init__(self):
        self.dice_size = 60
        self.dot_radius = 4
        self.colors = {
            'dice_face': (240, 240, 240),
            'dice_edge': (180, 180, 180),
            'dice_shadow': (100, 100, 100),
            'dot': (50, 50, 50),
            'highlight': (255, 255, 255),
            'number': (50, 50, 50),
            'd6': (240, 240, 240),    # d6 - 白色
            'd8': (255, 200, 200),    # d8 - 淡红色
            'd12': (200, 255, 200),   # d12 - 淡绿色
            'd20': (200, 200, 255),   # d20 - 淡蓝色
        }
        
        # 预计算d6骰子点数的位置
        self.dot_patterns = {
            1: [(0.5, 0.5)],
            2: [(0.25, 0.25), (0.75, 0.75)],
            3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
            4: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75)],
            5: [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)],
            6: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.5), (0.75, 0.5), (0.25, 0.75), (0.75, 0.75)]
        }
        
        # 初始化字体
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def get_dice_color(self, dice_type: str) -> Tuple[int, int, int]:
        """根据骰子类型获取颜色"""
        return self.colors.get(dice_type, self.colors['dice_face'])
    
    def draw_2d_dice(self, surface: pygame.Surface, x: int, y: int, value: int, 
                     dice_type: str = "d6", rotation: float = 0, scale: float = 1.0, 
                     offset_x: float = 0, offset_y: float = 0):
        """绘制2D骰子"""
        size = int(self.dice_size * scale)
        actual_x = int(x + offset_x)
        actual_y = int(y + offset_y)
        
        # 创建骰子表面
        dice_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # 获取骰子颜色
        dice_color = self.get_dice_color(dice_type)
        
        # 绘制骰子主体
        dice_rect = pygame.Rect(2, 2, size - 4, size - 4)
        pygame.draw.rect(dice_surface, dice_color, dice_rect, border_radius=8)
        pygame.draw.rect(dice_surface, self.colors['dice_edge'], dice_rect, width=2, border_radius=8)
        
        # 绘制高光
        highlight_rect = pygame.Rect(4, 4, size // 3, size // 4)
        pygame.draw.rect(dice_surface, self.colors['highlight'], highlight_rect, border_radius=4)
        
        # 根据骰子类型绘制内容
        if dice_type == "d6" and value <= 6:
            # d6使用点数
            self._draw_dots(dice_surface, value, size, scale)
        else:
            # 其他类型使用数字
            self._draw_number(dice_surface, value, size, scale)
        
        # 应用旋转
        if rotation != 0:
            rotated_surface = pygame.transform.rotate(dice_surface, rotation)
            # 计算旋转后的中心偏移
            old_center = dice_surface.get_rect().center
            new_center = rotated_surface.get_rect().center
            offset_x += old_center[0] - new_center[0]
            offset_y += old_center[1] - new_center[1]
            dice_surface = rotated_surface
        
        # 绘制到目标表面
        surface.blit(dice_surface, (actual_x - size // 2, actual_y - size // 2))
    
    def _draw_dots(self, surface: pygame.Surface, value: int, size: int, scale: float):
        """绘制d6骰子的点数"""
        if value in self.dot_patterns:
            dot_size = int(self.dot_radius * scale)
            for dot_x, dot_y in self.dot_patterns[value]:
                dot_pos_x = int(dot_x * (size - 16) + 8)
                dot_pos_y = int(dot_y * (size - 16) + 8)
                pygame.draw.circle(surface, self.colors['dot'], (dot_pos_x, dot_pos_y), dot_size)
    
    def _draw_number(self, surface: pygame.Surface, value: int, size: int, scale: float):
        """绘制骰子数字"""
        # 选择合适的字体大小
        font_size = int(24 * scale) if value < 10 else int(20 * scale)
        font = pygame.font.Font(None, font_size)
        
        # 渲染数字
        text = font.render(str(value), True, self.colors['number'])
        text_rect = text.get_rect(center=(size // 2, size // 2))
        surface.blit(text, text_rect)
    
    def draw_3d_dice(self, surface: pygame.Surface, x: int, y: int, value: int,
                     dice_type: str = "d6", rotation_x: float = 0, rotation_y: float = 0, 
                     rotation_z: float = 0, scale: float = 1.0, offset_x: float = 0, offset_y: float = 0):
        """绘制伪3D骰子"""
        size = int(self.dice_size * scale)
        actual_x = int(x + offset_x)
        actual_y = int(y + offset_y)
        
        # 计算3D投影参数
        depth_offset = int(size * 0.3 * math.sin(rotation_y))
        height_offset = int(size * 0.2 * math.sin(rotation_x))
        
        # 绘制阴影
        shadow_offset = 8
        shadow_rect = pygame.Rect(
            actual_x - size // 2 + shadow_offset,
            actual_y - size // 2 + shadow_offset,
            size, size
        )
        pygame.draw.rect(surface, self.colors['dice_shadow'], shadow_rect, border_radius=8)
        
        # 绘制骰子的三个可见面
        self._draw_dice_face(surface, actual_x, actual_y - height_offset, size, value, 'top', dice_type)
        self._draw_dice_face(surface, actual_x - depth_offset, actual_y, size, (value + 1) % 6 + 1, 'left', dice_type)
        self._draw_dice_face(surface, actual_x, actual_y, size, value, 'front', dice_type)
    
    def _draw_dice_face(self, surface: pygame.Surface, x: int, y: int, size: int, 
                       value: int, face: str, dice_type: str = "d6"):
        """绘制骰子的一个面"""
        # 获取基础颜色
        base_color = self.get_dice_color(dice_type)
        
        # 根据面的类型调整颜色
        if face == 'top':
            face_color = tuple(min(255, c + 20) for c in base_color)
            edge_color = tuple(min(255, c + 10) for c in self.colors['dice_edge'])
        elif face == 'left':
            face_color = tuple(max(0, c - 30) for c in base_color)
            edge_color = tuple(max(0, c - 20) for c in self.colors['dice_edge'])
        else:  # front
            face_color = base_color
            edge_color = self.colors['dice_edge']
        
        # 绘制面
        face_rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
        pygame.draw.rect(surface, face_color, face_rect, border_radius=6)
        pygame.draw.rect(surface, edge_color, face_rect, width=2, border_radius=6)
        
        # 绘制内容
        if dice_type == "d6" and value <= 6:
            # d6使用点数
            if value in self.dot_patterns:
                for dot_x, dot_y in self.dot_patterns[value]:
                    dot_pos_x = int(x - size // 2 + dot_x * size)
                    dot_pos_y = int(y - size // 2 + dot_y * size)
                    pygame.draw.circle(surface, self.colors['dot'], (dot_pos_x, dot_pos_y), self.dot_radius)
        else:
            # 其他类型使用数字
            font_size = 20 if value < 10 else 16
            font = pygame.font.Font(None, font_size)
            text = font.render(str(value), True, self.colors['number'])
            text_rect = text.get_rect(center=(x, y))
            surface.blit(text, text_rect)
    
    def draw_dice_with_type_indicator(self, surface: pygame.Surface, x: int, y: int, 
                                    value: int, dice_type: str, scale: float = 1.0):
        """绘制带类型指示器的骰子"""
        # 绘制主骰子
        self.draw_2d_dice(surface, x, y, value, dice_type, scale=scale)
        
        # 绘制类型标签
        if dice_type != "d6":
            label_font = pygame.font.Font(None, 16)
            label_text = label_font.render(dice_type.upper(), True, self.colors['number'])
            label_rect = label_text.get_rect()
            label_rect.bottomright = (x + int(self.dice_size * scale // 2), y - int(self.dice_size * scale // 2))
            
            # 绘制标签背景
            bg_rect = label_rect.inflate(4, 2)
            pygame.draw.rect(surface, (255, 255, 255, 180), bg_rect, border_radius=3)
            pygame.draw.rect(surface, (100, 100, 100), bg_rect, width=1, border_radius=3)
            
            surface.blit(label_text, label_rect)
    
    def draw_dice_trail(self, surface: pygame.Surface, positions: List[Tuple[int, int]], 
                       alpha_values: List[int], value: int):
        """绘制骰子运动轨迹"""
        for i, ((x, y), alpha) in enumerate(zip(positions, alpha_values)):
            if alpha > 0:
                # 创建半透明表面
                trail_surface = pygame.Surface((self.dice_size, self.dice_size), pygame.SRCALPHA)
                
                # 绘制简化的骰子
                dice_rect = pygame.Rect(2, 2, self.dice_size - 4, self.dice_size - 4)
                color_with_alpha = (*self.colors['dice_face'], alpha)
                pygame.draw.rect(trail_surface, color_with_alpha, dice_rect, border_radius=8)
                
                surface.blit(trail_surface, (x - self.dice_size // 2, y - self.dice_size // 2))
    
    def create_dice_explosion_effect(self, x: int, y: int, particle_count: int = 15) -> List[dict]:
        """创建骰子爆炸特效的粒子"""
        particles = []
        colors = [
            (255, 255, 255),  # 白色
            (240, 240, 240),  # 浅灰
            (200, 200, 200),  # 灰色
            (255, 255, 0),    # 黄色
            (255, 215, 0)     # 金色
        ]
        
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - random.uniform(1, 3),
                'life': 1.0,
                'size': random.uniform(3, 8),
                'color': random.choice(colors),
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(-10, 10)
            })
        
        return particles
    
    def draw_rolling_dice_background(self, surface: pygame.Surface, x: int, y: int, 
                                   size: int, intensity: float = 1.0):
        """绘制投掷中的骰子背景效果"""
        # 绘制模糊的圆形背景
        blur_radius = int(size * 0.8 * intensity)
        blur_surface = pygame.Surface((blur_radius * 2, blur_radius * 2), pygame.SRCALPHA)
        
        # 创建径向渐变效果
        for i in range(blur_radius, 0, -2):
            alpha = int(30 * intensity * (blur_radius - i) / blur_radius)
            color = (255, 255, 255, alpha)
            pygame.draw.circle(blur_surface, color, (blur_radius, blur_radius), i)
        
        surface.blit(blur_surface, (x - blur_radius, y - blur_radius))
    
    def get_dice_bounce_positions(self, start_x: int, start_y: int, end_x: int, end_y: int,
                                progress: float, bounce_count: int = 3) -> Tuple[int, int]:
        """计算骰子弹跳轨迹"""
        # 基础位置插值
        base_x = start_x + (end_x - start_x) * progress
        base_y = start_y + (end_y - start_y) * progress
        
        # 添加弹跳效果
        bounce_progress = progress * bounce_count
        bounce_height = 30 * (1 - progress) * abs(math.sin(bounce_progress * math.pi))
        
        return int(base_x), int(base_y - bounce_height)
    
    def create_number_popup(self, surface: pygame.Surface, x: int, y: int, 
                          number: int, scale: float = 1.0, alpha: int = 255):
        """创建数字弹出效果"""
        font_size = int(36 * scale)
        font = pygame.font.Font(None, font_size)
        
        # 渲染数字
        text_surface = font.render(str(number), True, (255, 255, 255))
        
        # 添加描边效果
        outline_surface = font.render(str(number), True, (0, 0, 0))
        
        # 创建带透明度的表面
        popup_surface = pygame.Surface((text_surface.get_width() + 4, text_surface.get_height() + 4), pygame.SRCALPHA)
        
        # 绘制描边
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    popup_surface.blit(outline_surface, (2 + dx, 2 + dy))
        
        # 绘制主文本
        popup_surface.blit(text_surface, (2, 2))
        
        # 应用透明度
        popup_surface.set_alpha(alpha)
        
        # 绘制到目标表面
        text_rect = popup_surface.get_rect(center=(x, y))
        surface.blit(popup_surface, text_rect) 