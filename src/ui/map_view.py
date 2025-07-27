"""
地图渲染器
"""
import pygame
from typing import Tuple, Optional, List
from src.models.map import Map, Cell
from src.models.player import Player
from src.ui.constants import COLORS, CELL_SIZE, LAYOUT
from src.ui.font_manager import get_font, render_text


class MapView:
    """地图视图"""
    
    def __init__(self, game_map: Map, x: int, y: int, size: int = None):
        """
        初始化地图视图
        
        Args:
            game_map: 地图对象
            x, y: 地图视图在屏幕上的位置
            size: 地图视图的尺寸（正方形）
        """
        self.game_map = game_map
        self.x = x
        self.y = y
        
        # 计算自适应尺寸
        if size is None:
            # 使用窗口尺寸减去信息面板和边距
            from .constants import WINDOW_WIDTH, WINDOW_HEIGHT, INFO_PANEL_WIDTH, MESSAGE_PANEL_HEIGHT, MAP_MARGIN
            available_width = WINDOW_WIDTH - INFO_PANEL_WIDTH - MAP_MARGIN * 3
            available_height = WINDOW_HEIGHT - MESSAGE_PANEL_HEIGHT - MAP_MARGIN * 3
            self.size = min(available_width, available_height)
        else:
            self.size = size
            
        # 计算格子大小
        self.cell_size = min(self.size // max(game_map.width, game_map.height), 60)
        
        # 摄像头相关
        self.offset_x = 0
        self.offset_y = 0
        self.camera_x = 0
        self.camera_y = 0
        self.target_x = 0
        self.target_y = 0
        self.camera_follow_mode = True  # 默认开启跟随模式
        self.camera_manual_mode = False
        self.camera_animation_start = 0
        self.camera_animation_duration = 500  # 毫秒
        self.is_animating = False
        
        # 选中状态
        self.selected_cell = None
        self.hovered_cell = None  # 添加悬停格子状态
        self.highlighted_path = []
        
        # 图片缓存
        self.building_images = {}
        self.player_images = {}
        
        # 加载图片
        self._load_images()
        
        # 字体
        try:
            self.chinese_font = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", 12)
        except:
            self.chinese_font = pygame.font.Font(None, 12)
        
        # 格子图标
        self.icons = {
            "empty": "空",
            "wall": "墙",
            "bank": "银",
            "shop": "店",
            "dice_shop": "骰",
            "jail": "狱",
            "luck": "运",
            "bad_luck": "凶"
        }
        
        print(f"[地图视图] 初始化完成: 位置=({x}, {y}), 尺寸={self.size}, 格子大小={self.cell_size}")
        
    def set_camera_target(self, target_x: int, target_y: int, animate: bool = True):
        """设置摄像头目标位置"""
        self.target_x = target_x
        self.target_y = target_y
        
        if animate:
            # 记录动画开始时的偏移
            self._start_offset_x = self.offset_x
            self._start_offset_y = self.offset_y
            self.camera_animation_start = pygame.time.get_ticks()
            self.is_animating = True
        else:
            # 立即移动到目标位置 - 让目标格子居中显示
            self.offset_x = self.size // 2 - target_x * self.cell_size - self.cell_size // 2
            self.offset_y = self.size // 2 - target_y * self.cell_size - self.cell_size // 2
            self.is_animating = False
    
    def follow_player(self, player: Player, animate: bool = True):
        """跟随玩家"""
        if not player:
            return
            
        # 获取玩家在地图上的位置
        player_pos = self.game_map.get_position_by_path_index(player.position)
        if player_pos:
            self.set_camera_target(player_pos[0], player_pos[1], animate)
    
    def center_on_cell(self, cell_x: int, cell_y: int, animate: bool = True):
        """将摄像头居中到指定格子"""
        self.set_camera_target(cell_x, cell_y, animate)
    
    def update_camera(self, current_time: int = None):
        """更新摄像头位置"""
        if current_time is None:
            current_time = pygame.time.get_ticks()
        
        # 如果正在动画中，更新动画
        if self.is_animating and self.camera_animation_start > 0:
            elapsed = current_time - self.camera_animation_start
            progress = min(elapsed / self.camera_animation_duration, 1.0)
            
            # 使用缓动函数使动画更自然
            progress = self._ease_out_quad(progress)
            
            # 计算目标偏移 - 让目标格子居中显示
            target_offset_x = self.size // 2 - self.target_x * self.cell_size - self.cell_size // 2
            target_offset_y = self.size // 2 - self.target_y * self.cell_size - self.cell_size // 2
            
            # 插值计算当前偏移
            start_offset_x = getattr(self, '_start_offset_x', self.offset_x)
            start_offset_y = getattr(self, '_start_offset_y', self.offset_y)
            
            self.offset_x = start_offset_x + (target_offset_x - start_offset_x) * progress
            self.offset_y = start_offset_y + (target_offset_y - start_offset_y) * progress
            
            # 动画完成
            if progress >= 1.0:
                self.camera_animation_start = 0
                self.offset_x = target_offset_x
                self.offset_y = target_offset_y
                self.is_animating = False
    
    def _ease_out_quad(self, t: float) -> float:
        """缓出二次函数，使动画更自然"""
        return t * (2 - t)
    
    def toggle_camera_follow(self):
        """切换摄像头跟随模式"""
        self.camera_follow_mode = not self.camera_follow_mode
        if self.camera_follow_mode:
            self.camera_manual_mode = False
    
    def toggle_camera_manual(self):
        """切换手动控制模式"""
        self.camera_manual_mode = not self.camera_manual_mode
        if self.camera_manual_mode:
            self.camera_follow_mode = False
    
    def get_cell_color(self, cell: Cell) -> Tuple[int, int, int]:
        """获取格子颜色"""
        if not cell:
            return COLORS["cell_void"]
            
        # 根据格子类型选择颜色
        color_map = {
            "empty": COLORS["cell_empty"],
            "wall": COLORS["cell_wall"],
            "void": COLORS["cell_void"],
            "shop": COLORS["cell_shop"],
            "bank": COLORS["cell_bank"],
            "jail": COLORS["cell_jail"],
            "luck": COLORS["cell_luck"],
            "bad_luck": COLORS["cell_bad_luck"],
            "dice_shop": COLORS["cell_dice_shop"],
        }
        
        base_color = color_map.get(cell.cell_type, COLORS["cell_empty"])
        
        # 如果是房产格子，根据等级调整颜色
        if cell.has_property():
            property_obj = cell.property
            if property_obj.is_owned():
                if property_obj.level == 1:
                    return COLORS["cell_property_level1"]
                elif property_obj.level == 2:
                    return COLORS["cell_property_level2"]
                elif property_obj.level == 3:
                    return COLORS["cell_property_level3"]
                elif property_obj.level == 4:
                    return COLORS["cell_property_level4"]
                else:
                    return COLORS["cell_property_owned"]
            else:
                return COLORS["cell_property"]
        
        return base_color
    
    def get_map_draw_origin(self):
        """获取地图内容在区域内的居中起点坐标"""
        map_pixel_w = self.cell_size * self.game_map.width
        map_pixel_h = self.cell_size * self.game_map.height
        origin_x = self.x + (self.size - map_pixel_w) // 2
        origin_y = self.y + (self.size - map_pixel_h) // 2
        return origin_x, origin_y

    def get_cell_rect(self, cell_x: int, cell_y: int) -> pygame.Rect:
        """获取格子的屏幕坐标（考虑摄像头偏移）"""
        # 使用统一的坐标计算，包含摄像头偏移
        screen_x = self.x + cell_x * self.cell_size + self.offset_x
        screen_y = self.y + cell_y * self.cell_size + self.offset_y
        size = self.cell_size
        return pygame.Rect(screen_x, screen_y, size, size)
    
    def screen_to_map_pos(self, screen_x: int, screen_y: int) -> Optional[Tuple[int, int]]:
        """屏幕坐标转换为地图坐标（考虑摄像头偏移）"""
        # 考虑摄像头偏移的屏幕坐标转换
        map_x = (screen_x - self.x - self.offset_x) // self.cell_size
        map_y = (screen_y - self.y - self.offset_y) // self.cell_size
        
        if 0 <= map_x < self.game_map.width and 0 <= map_y < self.game_map.height:
            return int(map_x), int(map_y)
        return None
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                map_pos = self.screen_to_map_pos(*event.pos)
                if map_pos:
                    # 检查是否点击到了有效格子
                    cell = self.game_map.get_cell_at(map_pos)
                    if cell and cell.cell_type != "void":  # 只有点击到非无效格子才消费事件
                        self.selected_cell = map_pos
                        # 点击时切换到手动模式并居中到点击的格子
                        if self.camera_manual_mode:
                            self.center_on_cell(map_pos[0], map_pos[1], True)
                        return True  # 只有点击到有效格子才消费事件
            elif event.button == 4:  # 滚轮向上 - 现在用于手动移动摄像头
                if self.camera_manual_mode:
                    self.offset_y += 50
                    return True
            elif event.button == 5:  # 滚轮向下
                if self.camera_manual_mode:
                    self.offset_y -= 50
                    return True
        elif event.type == pygame.MOUSEMOTION:
            # 处理鼠标悬停
            map_pos = self.screen_to_map_pos(*event.pos)
            if map_pos:
                cell = self.game_map.get_cell_at(map_pos)
                if cell and cell.cell_type != "void":
                    self.hovered_cell = map_pos
                else:
                    self.hovered_cell = None
            else:
                self.hovered_cell = None
                
            if event.buttons[1]:  # 中键拖拽 - 手动移动摄像头
                if self.camera_manual_mode:
                    self.offset_x += event.rel[0]
                    self.offset_y += event.rel[1]
                    return True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # 空格键切换跟随模式
                self.toggle_camera_follow()
                return True
            elif event.key == pygame.K_m:  # M键切换手动模式
                self.toggle_camera_manual()
                return True
            elif event.key == pygame.K_LEFT:  # 方向键手动移动
                if self.camera_manual_mode:
                    self.offset_x += 50
                    return True
            elif event.key == pygame.K_RIGHT:
                if self.camera_manual_mode:
                    self.offset_x -= 50
                    return True
            elif event.key == pygame.K_UP:
                if self.camera_manual_mode:
                    self.offset_y += 50
                    return True
            elif event.key == pygame.K_DOWN:
                if self.camera_manual_mode:
                    self.offset_y -= 50
                    return True
        return False
    
    def get_cell_info_text(self, cell: Cell) -> str:
        """获取格子信息文本"""
        if not cell:
            return ""
        
        info_parts = []
        
        # 格子类型
        type_names = {
            "empty": "空地",
            "wall": "墙壁",
            "void": "无效",
            "shop": "商店",
            "bank": "银行",
            "jail": "监狱",
            "luck": "好运",
            "bad_luck": "厄运",
            "dice_shop": "骰子店"
        }
        
        if cell.cell_type in type_names:
            info_parts.append(type_names[cell.cell_type])
        
        # 房产信息
        if cell.has_property():
            property_obj = cell.property
            if property_obj.is_owned():
                info_parts.append(f"Lv{property_obj.level}")
                if property_obj.owner_id:
                    # 这里需要通过owner_id获取玩家对象来显示名称
                    # 暂时先显示ID，后续可以优化为显示玩家名称
                    info_parts.append(f"(玩家{property_obj.owner_id})")
            else:
                info_parts.append("可购买")
        
        # 路障信息
        if cell.roadblock:
            info_parts.append("路障")
        
        # 金钱信息
        if cell.money_on_ground > 0:
            info_parts.append(f"${cell.money_on_ground}")
        
        return " ".join(info_parts)
    
    def draw_cell(self, surface: pygame.Surface, cell: Cell, cell_x: int, cell_y: int, rect: pygame.Rect):
        """绘制单个格子"""
        # 绘制格子背景
        if cell.cell_type == "void":
            color = (220, 220, 220)  # 浅灰色
            pygame.draw.rect(surface, color, rect)
            return
        
        # 优先使用图片
        image_key = None
        if cell.has_property():
            property_obj = cell.property
            if property_obj.is_owned():
                image_key = f"house_lv{property_obj.level}"
            else:
                image_key = "empty"  # 未拥有的房产显示为空地
        else:
            image_key = cell.cell_type
        
        # 如果有对应的图片，使用图片
        if image_key and image_key in self.building_images:
            surface.blit(self.building_images[image_key], rect)
        else:
            # 没有图片时使用颜色
            color = self.get_cell_color(cell)
            pygame.draw.rect(surface, color, rect)
        
        # 绘制边框
        border_color = COLORS["text_primary"]
        border_width = 1
        if (cell_x, cell_y) == self.selected_cell:
            border_color = COLORS["secondary"]
            border_width = 2
        elif cell.is_path_cell():
            border_color = COLORS["primary"]
            border_width = 2
        
        pygame.draw.rect(surface, border_color, rect, border_width)
        
        # 计算字体大小
        font_size = max(8, 10)
        font = self.chinese_font
        
        # 如果没有图片，绘制格子类型图标
        if not image_key or image_key not in self.building_images:
            if cell and cell.cell_type in self.icons:
                icon = self.icons[cell.cell_type]
                icon_surface = font.render(icon, True, COLORS["text_primary"])
                icon_rect = icon_surface.get_rect()
                icon_rect.centerx = rect.centerx
                icon_rect.centery = rect.centery - 5
                surface.blit(icon_surface, icon_rect)
        
        # 如果是路径格子，显示路径索引
        if cell.is_path_cell():
            path_text = str(cell.path_index)
            path_surface = font.render(path_text, True, COLORS["text_primary"])
            path_rect = path_surface.get_rect()
            # 调整位置到格子的左上角，避免被其他元素覆盖
            path_rect.topleft = (rect.x + 2, rect.y + 2)
            
            # 绘制半透明背景
            bg_rect = path_rect.inflate(4, 2)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.set_alpha(180)
            bg_surface.fill(COLORS["background"])
            surface.blit(bg_surface, bg_rect)
            
            surface.blit(path_surface, path_rect)
        
        # 绘制房产等级（如果使用图片且已拥有）
        if cell.has_property():
            property_obj = cell.property
            if property_obj.is_owned():
                level_text = f"Lv{property_obj.level}"
                level_surface = font.render(level_text, True, COLORS["text_light"])
                level_rect = level_surface.get_rect()
                level_rect.topleft = (rect.x + 2, rect.y + 2)
                surface.blit(level_surface, level_rect)
        
        # 绘制路障
        if cell.roadblock:
            obstacle_rect = pygame.Rect(rect.right - 8, rect.top + 2, 6, 6)
            pygame.draw.rect(surface, COLORS["error"], obstacle_rect)
        
        # 绘制金钱
        if cell.money_on_ground > 0:
            money_text = f"${cell.money_on_ground}"
            money_surface = font.render(money_text, True, COLORS["success"])
            money_rect = money_surface.get_rect()
            money_rect.bottomright = (rect.right - 2, rect.bottom - 2)
            surface.blit(money_surface, money_rect)
        
        # 如果是岔路口，显示特殊标记
        if cell.is_junction:
            center = rect.center
            radius = 3
            pygame.draw.circle(surface, COLORS["secondary"], center, radius)
    
    def draw_players_on_cell(self, surface: pygame.Surface, players: List[Player], cell_x: int, cell_y: int, rect: pygame.Rect):
        """在指定格子上绘制多个玩家"""
        if not players:
            return
            
        cell_center = rect.center
        
        # 玩家颜色列表
        player_colors = [
            COLORS["player_1"], COLORS["player_2"], COLORS["player_3"],
            COLORS["player_4"], COLORS["player_5"], COLORS["player_6"]
        ]
        
        # 计算玩家标记的大小和位置
        if len(players) == 1:
            # 单个玩家：大圆圈
            self._draw_single_player(surface, players[0], cell_center, player_colors)
        else:
            # 多个玩家：小圆圈排列
            self._draw_multiple_players(surface, players, cell_center, player_colors, rect)
    
    def _draw_single_player(self, surface: pygame.Surface, player: Player, center: Tuple[int, int], player_colors: List):
        """绘制单个玩家"""
        # 尝试使用玩家图片
        player_key = f"player{player.player_id}"
        if player_key in self.player_images:
            # 使用玩家图片
            image = self.player_images[player_key]
            image_rect = image.get_rect(center=center)
            surface.blit(image, image_rect)
            
            # 绘制边框
            border_rect = image_rect.inflate(4, 4)
            pygame.draw.rect(surface, COLORS["text_primary"], border_rect, 2)
        else:
            # 没有图片时使用圆圈
            color = player_colors[(int(player.player_id) - 1) % len(player_colors)]
            if player.is_ai:
                color = COLORS["ai_player"]
            
            # 绘制外圈（玩家颜色）
            radius = 10
            pygame.draw.circle(surface, color, center, radius)
            pygame.draw.circle(surface, COLORS["text_primary"], center, radius, 2)
            
            # 绘制内圈（白色背景）
            inner_radius = 6
            pygame.draw.circle(surface, COLORS["background"], center, inner_radius)
            
            # 绘制玩家ID
            font = self.chinese_font
            text = font.render(str(player.player_id), True, COLORS["text_primary"])
            text_rect = text.get_rect(center=center)
            surface.blit(text, text_rect)
    
    def _draw_multiple_players(self, surface: pygame.Surface, players: List[Player], center: Tuple[int, int], 
                             player_colors: List, cell_rect: pygame.Rect):
        """绘制多个玩家"""
        # 计算小图片的大小和间距
        small_size = min(self.cell_size // 3, 25)  # 小图片大小
        spacing = 4
        
        # 计算总宽度
        total_width = len(players) * (small_size + spacing) - spacing
        start_x = center[0] - total_width // 2
        
        for i, player in enumerate(players):
            player_center = (start_x + i * (small_size + spacing) + small_size // 2, center[1])
            
            # 尝试使用玩家图片
            player_key = f"player{player.player_id}"
            if player_key in self.player_images:
                # 使用玩家图片
                image = self.player_images[player_key]
                # 缩放到小尺寸
                small_image = pygame.transform.scale(image, (small_size, small_size))
                image_rect = small_image.get_rect(center=player_center)
                surface.blit(small_image, image_rect)
                
                # 绘制边框
                border_rect = image_rect.inflate(2, 2)
                pygame.draw.rect(surface, COLORS["text_primary"], border_rect, 1)
            else:
                # 没有图片时使用小圆圈
                color = player_colors[(int(player.player_id) - 1) % len(player_colors)]
                if player.is_ai:
                    color = COLORS["ai_player"]
                
                # 绘制小圆圈
                pygame.draw.circle(surface, color, player_center, small_size // 2)
                pygame.draw.circle(surface, COLORS["text_primary"], player_center, small_size // 2, 1)
                
                # 绘制玩家ID（小字体）
                font = pygame.font.Font(None, 8)
                text = font.render(str(player.player_id), True, COLORS["text_primary"])
                text_rect = text.get_rect(center=player_center)
                surface.blit(text, text_rect)
    
    def draw_player(self, surface: pygame.Surface, player: Player):
        """绘制玩家（兼容旧版本）"""
        if not player:
            return
            
        # 获取玩家在地图上的位置
        map_pos = self.game_map.get_position_by_path_index(player.position)
        if not map_pos:
            return
            
        cell_x, cell_y = map_pos
        self._draw_single_player(surface, player, self.get_cell_rect(cell_x, cell_y).center, 
                               [COLORS["player_1"], COLORS["player_2"], COLORS["player_3"],
                                COLORS["player_4"], COLORS["player_5"], COLORS["player_6"]])
    
    def draw_path(self, surface: pygame.Surface, path_indices: List[int], color: Tuple[int, int, int] = None):
        """绘制路径"""
        if not path_indices:
            return
            
        color = color or COLORS["primary"]
        
        for i in range(len(path_indices) - 1):
            start_pos = self.game_map.get_position_by_path_index(path_indices[i])
            end_pos = self.game_map.get_position_by_path_index(path_indices[i + 1])
            
            if start_pos and end_pos:
                start_rect = pygame.Rect(
                    self.x + start_pos[0] * self.cell_size + self.offset_x,
                    self.y + start_pos[1] * self.cell_size + self.offset_y,
                    self.cell_size, self.cell_size)
                end_rect = pygame.Rect(
                    self.x + end_pos[0] * self.cell_size + self.offset_x,
                    self.y + end_pos[1] * self.cell_size + self.offset_y,
                    self.cell_size, self.cell_size)
                
                start_center = start_rect.center
                end_center = end_rect.center
                
                # 绘制路径线
                pygame.draw.line(surface, color, start_center, end_center, 3)
    
    def draw_highlighted_path(self, surface: pygame.Surface):
        """绘制高亮路径"""
        if self.highlighted_path:
            self.draw_path(surface, self.highlighted_path, COLORS["secondary"])
    
    def draw_cell_tooltip(self, surface: pygame.Surface, cell: Cell, cell_x: int, cell_y: int, rect: pygame.Rect):
        """绘制格子提示信息"""
        if not cell:
            return
        
        info_text = self.get_cell_info_text(cell)
        
        if info_text:
            # 使用深色文本在白色背景上显示
            text_surface = render_text(info_text, "small", COLORS["text_primary"], True)
            text_rect = text_surface.get_rect()
            
            # 计算提示框位置
            tooltip_rect = text_rect.inflate(10, 6)
            tooltip_rect.topleft = (rect.right + 5, rect.top)
            
            # 确保提示框不超出屏幕
            if tooltip_rect.right > self.x + self.size:
                tooltip_rect.right = rect.left - 5
            if tooltip_rect.bottom > self.y + self.size:
                tooltip_rect.bottom = rect.top - 5
            
            # 绘制提示框背景
            pygame.draw.rect(surface, COLORS["surface"], tooltip_rect)
            pygame.draw.rect(surface, COLORS["text_secondary"], tooltip_rect, 1)
            
            # 绘制文本
            text_rect.topleft = tooltip_rect.topleft
            text_rect.x += 5
            text_rect.y += 3
            surface.blit(text_surface, text_rect)
    
    def get_players_on_cell(self, cell_x: int, cell_y: int) -> List[Player]:
        """获取指定格子上的所有玩家"""
        players_on_cell = []
        if not hasattr(self, '_players_cache'):
            self._players_cache = []
        
        for player in self._players_cache:
            if player:
                player_pos = self.game_map.get_position_by_path_index(player.position)
                if player_pos and player_pos[0] == cell_x and player_pos[1] == cell_y:
                    players_on_cell.append(player)
        
        return players_on_cell
    
    def draw(self, surface: pygame.Surface, players: List[Player] = None):
        """绘制地图"""
        if players is not None:
            self._players_cache = players
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                cell = self.game_map.get_cell_at((x, y))
                if cell:
                    rect = pygame.Rect(
                        self.x + x * self.cell_size + self.offset_x,
                        self.y + y * self.cell_size + self.offset_y,
                        self.cell_size, self.cell_size)
                    self.draw_cell(surface, cell, x, y, rect)
                    self.draw_players_on_cell(surface, self.get_players_on_cell(x, y), x, y, rect)
        
        # 绘制路径
        if self.game_map.path:
            path_indices = list(range(len(self.game_map.path)))
            self.draw_path(surface, path_indices)
        
        # 绘制高亮路径
        self.draw_highlighted_path(surface)
        
        # 绘制选中格子的提示
        if self.selected_cell:
            cell = self.game_map.get_cell_at(self.selected_cell)
            if cell:
                rect = pygame.Rect(
                    self.x + self.selected_cell[0] * self.cell_size + self.offset_x,
                    self.y + self.selected_cell[1] * self.cell_size + self.offset_y,
                    self.cell_size, self.cell_size)
                self.draw_cell_tooltip(surface, cell, self.selected_cell[0], self.selected_cell[1], rect)
        
        # 绘制悬停格子的提示
        if self.hovered_cell and self.hovered_cell != self.selected_cell:
            cell = self.game_map.get_cell_at(self.hovered_cell)
            if cell:
                rect = pygame.Rect(
                    self.x + self.hovered_cell[0] * self.cell_size + self.offset_x,
                    self.y + self.hovered_cell[1] * self.cell_size + self.offset_y,
                    self.cell_size, self.cell_size)
                self.draw_cell_tooltip(surface, cell, self.hovered_cell[0], self.hovered_cell[1], rect)
        
        # 绘制摄像头状态指示器
        self._draw_camera_status(surface)
    
    def _draw_camera_status(self, surface: pygame.Surface):
        """绘制摄像头状态指示器"""
        status_text = ""
        if self.camera_follow_mode:
            status_text = "跟随模式 (空格切换)"
        elif self.camera_manual_mode:
            status_text = "手动模式 (M切换, 方向键移动)"
        
        if status_text:
            # 使用全局字体管理器渲染文本
            text_surface = render_text(status_text, "tiny", COLORS["text_secondary"], True)
            text_rect = text_surface.get_rect()
            text_rect.topleft = (self.x + 10, self.y + 10)
            
            # 绘制背景
            bg_rect = text_rect.inflate(10, 6)
            pygame.draw.rect(surface, COLORS["surface"], bg_rect)
            pygame.draw.rect(surface, COLORS["text_secondary"], bg_rect, 1)
            
            surface.blit(text_surface, text_rect)
    
    def set_highlighted_path(self, path_indices: List[int]):
        """设置高亮路径"""
        self.highlighted_path = path_indices
    
    def clear_highlighted_path(self):
        """清除高亮路径"""
        self.highlighted_path = []
    
    def reset_view(self):
        """重置视图到默认状态"""
        # 重置摄像头偏移到合理的初始值
        self.offset_x = 0
        self.offset_y = 0
        self.camera_x = 0
        self.camera_y = 0
        self.target_x = 0
        self.target_y = 0
        self.selected_cell = None
        self.hovered_cell = None
        self.highlighted_path = []
        self.camera_animation_start = 0
        self.is_animating = False
        
        # 如果有当前玩家，居中到当前玩家位置
        print(f"[重置视图] 摄像头偏移重置为: offset_x={self.offset_x}, offset_y={self.offset_y}")
        
    def center_map(self):
        """将地图居中显示"""
        # 计算让地图居中的偏移
        map_pixel_w = self.cell_size * self.game_map.width
        map_pixel_h = self.cell_size * self.game_map.height
        
        # 让地图在视图区域内居中
        self.offset_x = (self.size - map_pixel_w) // 2
        self.offset_y = (self.size - map_pixel_h) // 2
        
        print(f"[居中地图] 地图尺寸: {map_pixel_w}x{map_pixel_h}, 视图尺寸: {self.size}")
        print(f"[居中地图] 设置偏移为: offset_x={self.offset_x}, offset_y={self.offset_y}")

    def _load_images(self):
        """加载图片资源"""
        try:
            # 加载建筑图片
            building_paths = {
                "empty": "assets/images/building/empty.jpeg",
                "shop": "assets/images/building/shop.jpeg",
                "bank": "assets/images/building/bank.jpeg",
                "jail": "assets/images/building/jail.jpeg",
                "dice_shop": "assets/images/building/dice_shop.jpeg",
                "luck": "assets/images/building/luck.jpg",
                "bad_luck": "assets/images/building/bad_luck.png",
                "house_lv1": "assets/images/building/house_lv1.png",
                "house_lv2": "assets/images/building/house_lv2.png",
                "house_lv3": "assets/images/building/house_lv3.jpeg",
                "house_lv4": "assets/images/building/house_lv4.jpeg"
            }
            
            for cell_type, path in building_paths.items():
                try:
                    image = pygame.image.load(path)
                    # 缩放到格子大小
                    scaled_image = pygame.transform.scale(image, (self.cell_size, self.cell_size))
                    self.building_images[cell_type] = scaled_image
                except Exception as e:
                    print(f"无法加载建筑图片 {path}: {e}")
            
            # 加载玩家图片
            player_paths = {
                "player1": "assets/images/player/player1_main.png",
                "player2": "assets/images/player/player2_main.jpg",
                "player3": "assets/images/player/player3_main.jpg",
                "player4": "assets/images/player/player4_main.jpeg",
                "player5": "assets/images/player/player5_main.jpeg",
                "player6": "assets/images/player/player6_main.png"
            }
            
            for player_id, path in player_paths.items():
                try:
                    image = pygame.image.load(path)
                    # 缩放到玩家标记大小
                    player_size = min(self.cell_size // 2, 40)  # 玩家标记大小
                    scaled_image = pygame.transform.scale(image, (player_size, player_size))
                    self.player_images[player_id] = scaled_image
                except Exception as e:
                    print(f"无法加载玩家图片 {path}: {e}")
                    
        except Exception as e:
            print(f"加载图片资源时出错: {e}") 