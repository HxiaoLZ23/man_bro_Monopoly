#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏房间界面
"""

import pygame
import time
import os
import json
from typing import Dict, List, Callable, Optional, Any
from src.network.client.network_client import NetworkClient
from src.network.protocol import NetworkMessage, MessageType
from src.ui.font_manager import render_text, get_text_size
from src.ui.components import Button

# 颜色定义
COLORS = {
    "background": (240, 248, 255),
    "surface": (255, 255, 255),
    "primary": (70, 130, 180),
    "secondary": (108, 117, 125),
    "success": (40, 167, 69),
    "danger": (220, 53, 69),
    "warning": (255, 193, 7),
    "info": (23, 162, 184),
    "text_primary": (33, 37, 41),
    "text_secondary": (108, 117, 125),
    "border": (222, 226, 230),
    "hover": (233, 236, 239),
    "ready": (40, 167, 69),
    "not_ready": (220, 53, 69),
    "host": (255, 193, 7)
}

# 窗口尺寸
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700

class ChatMessage:
    """聊天消息类"""
    def __init__(self, sender: str, content: str, msg_type: str = "normal", timestamp: float = None):
        self.sender = sender
        self.content = content
        self.msg_type = msg_type  # normal, system, private
        self.timestamp = timestamp or time.time()

class PlayerInfo:
    """玩家信息类"""
    def __init__(self, client_id: str, name: str, is_ready: bool = False, is_host: bool = False):
        self.client_id = client_id
        self.name = name
        self.is_ready = is_ready
        self.is_host = is_host

class MapInfo:
    """地图信息类"""
    def __init__(self, name: str, path: str, description: str = "", preview_path: str = None):
        self.name = name
        self.path = path
        self.description = description
        self.preview_path = preview_path

class ChatInputBox:
    """聊天输入框"""
    def __init__(self, x: int, y: int, width: int, height: int, max_length: int = 100):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.max_length = max_length
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
                return True
            else:
                self.active = False
        
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                # 返回输入的文本
                if self.text.strip():
                    result = self.text.strip()
                    self.text = ""
                    return result
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode and len(self.text) < self.max_length:
                self.text += event.unicode
            return True
        
        return False
    
    def update(self, dt: float):
        """更新光标闪烁"""
        if self.active:
            self.cursor_timer += dt
            if self.cursor_timer >= 500:  # 0.5秒
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
    
    def draw(self, surface: pygame.Surface):
        """绘制输入框"""
        # 背景
        color = COLORS["surface"] if self.active else COLORS["hover"]
        pygame.draw.rect(surface, color, self.rect)
        
        # 边框
        border_color = COLORS["primary"] if self.active else COLORS["border"]
        pygame.draw.rect(surface, border_color, self.rect, 2)
        
        # 文本
        if self.text or self.active:
            text_surface = render_text(self.text, "normal", COLORS["text_primary"])
            surface.blit(text_surface, (self.rect.x + 5, self.rect.y + 8))
            
            # 光标
            if self.active and self.cursor_visible:
                text_width = get_text_size(self.text, "normal")[0]
                cursor_x = self.rect.x + 5 + text_width
                cursor_y = self.rect.y + 5
                pygame.draw.line(surface, COLORS["text_primary"], 
                               (cursor_x, cursor_y), (cursor_x, cursor_y + 20), 1)
        else:
            # 占位符
            placeholder_surface = render_text("输入聊天消息...", "normal", COLORS["text_secondary"])
            surface.blit(placeholder_surface, (self.rect.x + 5, self.rect.y + 8))

class MapCard:
    """地图卡片"""
    def __init__(self, x: int, y: int, width: int, height: int, map_info: MapInfo, selected: bool = False):
        self.rect = pygame.Rect(x, y, width, height)
        self.map_info = map_info
        self.selected = selected
        self.hover = False
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        elif event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        
        return False
    
    def draw(self, surface: pygame.Surface):
        """绘制地图卡片"""
        # 背景颜色
        if self.selected:
            bg_color = COLORS["primary"]
            text_color = COLORS["surface"]
        elif self.hover:
            bg_color = COLORS["hover"]
            text_color = COLORS["text_primary"]
        else:
            bg_color = COLORS["surface"]
            text_color = COLORS["text_primary"]
        
        # 绘制背景
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, COLORS["border"], self.rect, 2)
        
        # 绘制地图名称
        name_surface = render_text(self.map_info.name, "normal", text_color, True)
        name_rect = name_surface.get_rect(center=(self.rect.centerx, self.rect.y + 20))
        surface.blit(name_surface, name_rect)
        
        # 绘制描述
        if self.map_info.description:
            desc_surface = render_text(self.map_info.description, "small", text_color)
            desc_rect = desc_surface.get_rect(center=(self.rect.centerx, self.rect.y + 45))
            surface.blit(desc_surface, desc_rect)
        
        # 绘制预览图（如果有）
        if self.map_info.preview_path and os.path.exists(self.map_info.preview_path):
            try:
                preview_img = pygame.image.load(self.map_info.preview_path)
                preview_img = pygame.transform.scale(preview_img, (self.rect.width - 20, 40))
                surface.blit(preview_img, (self.rect.x + 10, self.rect.y + 60))
            except:
                pass

class GameRoomWindow:
    """游戏房间窗口"""
    def __init__(self, network_client: NetworkClient, room_info: Dict[str, Any], on_close: Callable = None, on_game_start: Callable = None):
        self.network_client = network_client
        self.room_info = room_info
        self.on_close = on_close
        self.on_game_start = on_game_start
        self.running = True
        
        # 界面状态
        self.players: List[PlayerInfo] = []
        self.chat_messages: List[ChatMessage] = []
        self.chat_scroll = 0
        self.max_chat_scroll = 0
        self.selected_map = None
        self.available_maps: List[MapInfo] = []
        self.current_player_ready = False
        self.is_host = False
        
        # 界面组件
        self.buttons: List[Button] = []
        self.map_cards: List[MapCard] = []
        self.chat_input = ChatInputBox(20, WINDOW_HEIGHT - 60, 350, 40)
        
        # 初始化界面
        self.load_available_maps()
        self.init_ui()
        self.setup_network_handlers()
        
        # 添加系统消息
        self.add_chat_message("系统", f"欢迎进入房间: {room_info.get('name', '未知房间')}", "system")
        
        # 更新玩家信息
        self.update_players_from_room_info()
    
    def load_available_maps(self):
        """加载可用地图"""
        self.available_maps = [
            MapInfo("经典地图", "1.json", "传统大富翁地图"),
            MapInfo("带分叉地图", "2_with_junctions.json", "包含分叉路口的地图"),
            MapInfo("简单地图", "2.json", "简化版地图"),
        ]
        
        # 默认选择第一个地图
        if self.available_maps:
            self.selected_map = self.available_maps[0]
    
    def init_ui(self):
        """初始化界面"""
        self.buttons.clear()
        self.map_cards.clear()
        
        # 准备按钮
        ready_text = "取消准备" if self.current_player_ready else "准备"
        ready_color = COLORS["warning"] if self.current_player_ready else COLORS["success"]
        ready_button = Button(
            420, WINDOW_HEIGHT - 120, 120, 40,
            ready_text, self.toggle_ready, ready_color
        )
        self.buttons.append(ready_button)
        
        # 开始游戏按钮（仅房主可见）
        if self.is_host:
            start_button = Button(
                560, WINDOW_HEIGHT - 120, 120, 40,
                "开始游戏", self.start_game, COLORS["primary"]
            )
            self.buttons.append(start_button)
            
            # 添加AI玩家按钮（仅房主可见）
            add_ai_button = Button(
                700, WINDOW_HEIGHT - 120, 120, 40,
                "添加AI", self.add_ai_player, COLORS["info"]
            )
            self.buttons.append(add_ai_button)
        
        # 离开房间按钮
        leave_button = Button(
            WINDOW_WIDTH - 140, WINDOW_HEIGHT - 120, 120, 40,
            "离开房间", self.leave_room, COLORS["danger"]
        )
        self.buttons.append(leave_button)
        
        # 发送消息按钮
        send_button = Button(
            380, WINDOW_HEIGHT - 60, 60, 40,
            "发送", self.send_chat_message, COLORS["primary"]
        )
        self.buttons.append(send_button)
        
        # 创建地图卡片
        self.create_map_cards()
    
    def create_map_cards(self):
        """创建地图卡片"""
        self.map_cards.clear()
        
        card_width = 150
        card_height = 120
        start_x = 500
        start_y = 80
        
        for i, map_info in enumerate(self.available_maps):
            x = start_x + (i % 3) * (card_width + 10)
            y = start_y + (i // 3) * (card_height + 10)
            
            selected = (self.selected_map and self.selected_map.name == map_info.name)
            card = MapCard(x, y, card_width, card_height, map_info, selected)
            self.map_cards.append(card)
    
    def setup_network_handlers(self):
        """设置网络消息处理器"""
        self.network_client.set_message_handler(MessageType.ROOM_INFO, self.handle_room_info)
        self.network_client.set_message_handler(MessageType.CHAT_MESSAGE, self.handle_chat_message)
        self.network_client.set_message_handler(MessageType.SUCCESS, self.handle_success)
        self.network_client.set_message_handler(MessageType.ERROR, self.handle_error)
        self.network_client.set_message_handler(MessageType.GAME_START, self.handle_game_start)
    
    def handle_room_info(self, message: NetworkMessage):
        """处理房间信息更新"""
        room_data = message.data.get("room", {})
        self.room_info.update(room_data)
        self.update_players_from_room_info()
    
    def update_players_from_room_info(self):
        """从房间信息更新玩家列表"""
        self.players.clear()
        current_client_id = self.network_client.client_id
        
        for player_data in self.room_info.get("players", []):
            player = PlayerInfo(
                player_data.get("client_id", ""),
                player_data.get("name", "未知玩家"),
                player_data.get("is_ready", False),
                player_data.get("is_host", False)
            )
            self.players.append(player)
            
            # 检查当前玩家状态
            if player.client_id == current_client_id:
                self.current_player_ready = player.is_ready
                self.is_host = player.is_host
        
        # 重新初始化UI以更新按钮状态
        self.init_ui()
    
    def handle_chat_message(self, message: NetworkMessage):
        """处理聊天消息"""
        content = message.data.get("content", "")
        sender = message.data.get("sender", "未知")
        msg_type = message.data.get("message_type", "normal")
        
        self.add_chat_message(sender, content, msg_type)
    
    def handle_success(self, message: NetworkMessage):
        """处理成功消息"""
        msg = message.data.get("message", "操作成功")
        self.add_chat_message("系统", msg, "system")
    
    def handle_error(self, message: NetworkMessage):
        """处理错误消息"""
        error_msg = message.data.get("error", "操作失败")
        self.add_chat_message("系统", f"错误: {error_msg}", "system")
    
    def handle_game_start(self, message: NetworkMessage):
        """处理游戏开始消息"""
        game_data = message.data
        self.add_chat_message("系统", "游戏即将开始！", "system")
        
        # 通知父窗口游戏开始
        if self.on_game_start:
            self.on_game_start(game_data)
        
        # 关闭房间窗口
        self.close()
    
    def add_chat_message(self, sender: str, content: str, msg_type: str = "normal"):
        """添加聊天消息"""
        message = ChatMessage(sender, content, msg_type)
        self.chat_messages.append(message)
        
        # 限制消息数量
        if len(self.chat_messages) > 100:
            self.chat_messages.pop(0)
        
        # 自动滚动到底部
        self.update_chat_scroll()
    
    def update_chat_scroll(self):
        """更新聊天滚动"""
        chat_area_height = 300  # 聊天区域高度
        message_height = 25     # 每条消息高度
        total_height = len(self.chat_messages) * message_height
        
        self.max_chat_scroll = max(0, total_height - chat_area_height)
        self.chat_scroll = self.max_chat_scroll  # 滚动到底部
    
    def toggle_ready(self):
        """切换准备状态"""
        # 发送准备状态切换请求
        import threading
        import asyncio
        
        def toggle_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.send_ready_status(not self.current_player_ready))
                loop.close()
            except Exception as e:
                self.add_chat_message("系统", f"切换准备状态失败: {e}", "system")
        
        thread = threading.Thread(target=toggle_async)
        thread.daemon = True
        thread.start()
    
    async def send_ready_status(self, ready: bool):
        """发送准备状态"""
        message_data = {
            "action": "toggle_ready",
            "ready": ready
        }
        await self.network_client.send_player_action("toggle_ready", message_data)
    
    def start_game(self):
        """开始游戏"""
        print(f"🎮 [DEBUG] 开始游戏按钮被点击")
        print(f"🎮 [DEBUG] 当前玩家是否是房主: {self.is_host}")
        print(f"🎮 [DEBUG] 玩家列表: {[(p.name, p.is_ready, p.is_host) for p in self.players]}")
        
        if not self.is_host:
            self.add_chat_message("系统", "只有房主可以开始游戏", "system")
            return
        
        # 检查所有玩家是否都已准备
        ready_count = sum(1 for player in self.players if player.is_ready or player.is_host)
        total_players = len(self.players)
        
        print(f"🎮 [DEBUG] 准备的玩家数: {ready_count}/{total_players}")
        
        if ready_count < total_players:
            self.add_chat_message("系统", f"还有 {total_players - ready_count} 名玩家未准备", "system")
            return
        
        if not self.selected_map:
            print(f"🎮 [DEBUG] 未选择地图")
            self.add_chat_message("系统", "请选择地图", "system")
            return
        
        print(f"🎮 [DEBUG] 选择的地图: {self.selected_map.name} ({self.selected_map.path})")
        self.add_chat_message("系统", "正在开始游戏...", "system")
        
        # 发送开始游戏请求
        import threading
        import asyncio
        
        def start_async():
            try:
                print(f"🎮 [DEBUG] 开始异步发送开始游戏请求")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.send_start_game())
                loop.close()
                print(f"🎮 [DEBUG] 开始游戏请求发送完成")
            except Exception as e:
                print(f"🎮 [DEBUG] 开始游戏请求失败: {e}")
                self.add_chat_message("系统", f"开始游戏失败: {e}", "system")
        
        thread = threading.Thread(target=start_async)
        thread.daemon = True
        thread.start()
    
    async def send_start_game(self):
        """发送开始游戏请求"""
        game_data = {
            "map_file": self.selected_map.path,
            "players": [{"client_id": p.client_id, "name": p.name} for p in self.players]
        }
        print(f"🎮 [DEBUG] 准备发送的游戏数据: {game_data}")
        print(f"🎮 [DEBUG] 网络客户端连接状态: {self.network_client.is_connected()}")
        print(f"🎮 [DEBUG] 当前房间ID: {self.network_client.current_room_id}")
        
        result = await self.network_client.send_player_action("start_game", game_data)
        print(f"🎮 [DEBUG] 发送结果: {result}")
        
        if not result:
            self.add_chat_message("系统", "发送开始游戏请求失败", "system")
    
    def leave_room(self):
        """离开房间"""
        import threading
        import asyncio
        
        def leave_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.network_client.leave_room())
                loop.close()
                # 离开成功后关闭窗口
                self.close()
            except Exception as e:
                self.add_chat_message("系统", f"离开房间失败: {e}", "system")
        
        thread = threading.Thread(target=leave_async)
        thread.daemon = True
        thread.start()
    
    def send_chat_message(self):
        """发送聊天消息"""
        if hasattr(self.chat_input, 'text') and self.chat_input.text.strip():
            message_content = self.chat_input.text.strip()
            self.chat_input.text = ""
            
            # 发送到服务器
            import threading
            import asyncio
            
            def send_async():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(
                        self.network_client.send_chat_message(message_content)
                    )
                    loop.close()
                except Exception as e:
                    self.add_chat_message("系统", f"发送消息失败: {e}", "system")
            
            thread = threading.Thread(target=send_async)
            thread.daemon = True
            thread.start()
    
    def select_map(self, map_info: MapInfo):
        """选择地图"""
        if not self.is_host:
            self.add_chat_message("系统", "只有房主可以选择地图", "system")
            return
        
        self.selected_map = map_info
        self.create_map_cards()  # 重新创建卡片以更新选中状态
        self.add_chat_message("系统", f"已选择地图: {map_info.name}", "system")
        
        # 发送地图选择到服务器（可选）
        # TODO: 实现地图选择同步
    
    def close(self):
        """关闭窗口"""
        self.running = False
        if self.on_close:
            self.on_close()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件"""
        if not self.running:
            return False
        
        # 处理聊天滚动
        if event.type == pygame.MOUSEWHEEL:
            chat_rect = pygame.Rect(20, 200, 400, 300)
            if chat_rect.collidepoint(pygame.mouse.get_pos()):
                self.chat_scroll -= event.y * 20
                self.chat_scroll = max(0, min(self.chat_scroll, self.max_chat_scroll))
                return True
        
        # 处理地图卡片点击
        for i, card in enumerate(self.map_cards):
            if card.handle_event(event):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.select_map(card.map_info)
                return True
        
        # 处理聊天输入
        result = self.chat_input.handle_event(event)
        if isinstance(result, str):  # 如果返回字符串，说明用户按了回车
            # 发送消息
            import threading
            import asyncio
            
            def send_async():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(
                        self.network_client.send_chat_message(result)
                    )
                    loop.close()
                except Exception as e:
                    self.add_chat_message("系统", f"发送消息失败: {e}", "system")
            
            thread = threading.Thread(target=send_async)
            thread.daemon = True
            thread.start()
            return True
        elif result:
            return True
        
        # 处理按钮事件
        for button in self.buttons:
            if button.handle_event(event):
                return True
        
        return False
    
    def update(self, dt: float):
        """更新"""
        if not self.running:
            return
        
        self.chat_input.update(dt)
        
        # 更新地图卡片悬停状态
        mouse_pos = pygame.mouse.get_pos()
        for card in self.map_cards:
            card.hover = card.rect.collidepoint(mouse_pos)
    
    def draw(self, surface: pygame.Surface):
        """绘制"""
        if not self.running:
            return
        
        # 绘制半透明背景
        overlay = pygame.Surface(surface.get_size())
        overlay.set_alpha(200)
        overlay.fill(COLORS["background"])
        surface.blit(overlay, (0, 0))
        
        # 绘制主面板
        panel_rect = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(surface, COLORS["surface"], panel_rect)
        pygame.draw.rect(surface, COLORS["border"], panel_rect, 2)
        
        # 绘制标题
        room_name = self.room_info.get("name", "未知房间")
        title_surface = render_text(f"房间: {room_name}", "title", COLORS["text_primary"], True)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 30))
        surface.blit(title_surface, title_rect)
        
        # 绘制房间信息
        current_players = len(self.players)
        max_players = self.room_info.get("max_players", 4)
        info_text = f"玩家: {current_players}/{max_players}"
        info_surface = render_text(info_text, "subtitle", COLORS["text_secondary"])
        surface.blit(info_surface, (20, 60))
        
        # 绘制玩家列表
        self.draw_player_list(surface)
        
        # 绘制地图选择区域
        self.draw_map_selection(surface)
        
        # 绘制聊天区域
        self.draw_chat_area(surface)
        
        # 绘制输入框
        self.chat_input.draw(surface)
        
        # 绘制按钮
        for button in self.buttons:
            button.draw(surface)
    
    def draw_player_list(self, surface: pygame.Surface):
        """绘制玩家列表"""
        # 玩家列表背景
        player_rect = pygame.Rect(20, 80, 400, 100)
        pygame.draw.rect(surface, COLORS["hover"], player_rect)
        pygame.draw.rect(surface, COLORS["border"], player_rect, 1)
        
        # 标题
        title_surface = render_text("玩家列表", "subtitle", COLORS["text_primary"], True)
        surface.blit(title_surface, (player_rect.x + 10, player_rect.y + 10))
        
        # 玩家信息
        y_offset = player_rect.y + 35
        for i, player in enumerate(self.players):
            if y_offset + 25 > player_rect.bottom:
                break
            
            # 玩家状态颜色和图标
            if player.is_host:
                name_color = COLORS["host"]
                status_text = "👑 房主"
            elif getattr(player, 'is_ai', False):
                name_color = COLORS["info"]
                status_text = "🤖 AI"
            elif player.is_ready:
                name_color = COLORS["ready"]
                status_text = "✅ 已准备"
            else:
                name_color = COLORS["not_ready"]
                status_text = "⏳ 未准备"
            
            # 玩家名称
            player_icon = "🤖" if getattr(player, 'is_ai', False) else "👤"
            name_surface = render_text(f"{player_icon} {player.name}", "normal", name_color)
            surface.blit(name_surface, (player_rect.x + 10, y_offset))
            
            # 状态
            status_surface = render_text(status_text, "small", name_color)
            surface.blit(status_surface, (player_rect.x + 200, y_offset))
            
            # 如果是房主且是AI玩家，显示移除按钮
            if self.is_host and getattr(player, 'is_ai', False):
                remove_text = "移除"
                remove_color = COLORS["danger"]
                # 这里可以添加移除AI玩家的按钮
                remove_surface = render_text(remove_text, "small", remove_color)
                surface.blit(remove_surface, (player_rect.x + 320, y_offset))
            
            y_offset += 20
    
    def draw_map_selection(self, surface: pygame.Surface):
        """绘制地图选择区域"""
        # 地图选择背景
        map_rect = pygame.Rect(500, 60, 480, 280)
        pygame.draw.rect(surface, COLORS["hover"], map_rect)
        pygame.draw.rect(surface, COLORS["border"], map_rect, 1)
        
        # 标题
        title_surface = render_text("地图选择", "subtitle", COLORS["text_primary"], True)
        surface.blit(title_surface, (map_rect.x + 10, map_rect.y + 10))
        
        # 权限提示
        if not self.is_host:
            hint_surface = render_text("(只有房主可以选择地图)", "small", COLORS["text_secondary"])
            surface.blit(hint_surface, (map_rect.x + 150, map_rect.y + 10))
        
        # 绘制地图卡片
        for card in self.map_cards:
            card.draw(surface)
        
        # 显示当前选中的地图
        if self.selected_map:
            selected_text = f"当前地图: {self.selected_map.name}"
            selected_surface = render_text(selected_text, "normal", COLORS["primary"], True)
            surface.blit(selected_surface, (map_rect.x + 10, map_rect.bottom - 25))
    
    def draw_chat_area(self, surface: pygame.Surface):
        """绘制聊天区域"""
        # 聊天区域背景
        chat_rect = pygame.Rect(20, 200, 400, 300)
        pygame.draw.rect(surface, COLORS["hover"], chat_rect)
        pygame.draw.rect(surface, COLORS["border"], chat_rect, 1)
        
        # 标题
        title_surface = render_text("聊天记录", "subtitle", COLORS["text_primary"], True)
        surface.blit(title_surface, (chat_rect.x + 10, chat_rect.y + 5))
        
        # 聊天消息
        message_y = chat_rect.y + 30
        message_height = 25
        visible_messages = (chat_rect.height - 30) // message_height
        
        start_index = max(0, len(self.chat_messages) - visible_messages - (self.chat_scroll // message_height))
        end_index = min(len(self.chat_messages), start_index + visible_messages + 2)
        
        for i in range(start_index, end_index):
            if i < 0 or i >= len(self.chat_messages):
                continue
                
            message = self.chat_messages[i]
            y_pos = message_y + (i - start_index) * message_height - (self.chat_scroll % message_height)
            
            if y_pos + message_height < chat_rect.y + 30 or y_pos > chat_rect.bottom:
                continue
            
            # 消息颜色
            if message.msg_type == "system":
                color = COLORS["info"]
                text = f"[系统] {message.content}"
            elif message.msg_type == "private":
                color = COLORS["warning"]
                text = f"[私聊] {message.sender}: {message.content}"
            else:
                color = COLORS["text_primary"]
                text = f"{message.sender}: {message.content}"
            
            # 绘制消息
            message_surface = render_text(text, "small", color)
            # 确保消息不超出聊天区域
            if message_surface.get_width() > chat_rect.width - 20:
                # 截断过长的消息
                text = text[:50] + "..." if len(text) > 50 else text
                message_surface = render_text(text, "small", color)
            
            surface.blit(message_surface, (chat_rect.x + 10, y_pos))
        
        # 滚动条
        if self.max_chat_scroll > 0:
            scrollbar_rect = pygame.Rect(chat_rect.right - 10, chat_rect.y + 30, 8, chat_rect.height - 30)
            pygame.draw.rect(surface, COLORS["border"], scrollbar_rect)
            
            # 滚动条滑块
            scroll_ratio = self.chat_scroll / self.max_chat_scroll
            slider_height = max(20, scrollbar_rect.height * 0.3)
            slider_y = scrollbar_rect.y + scroll_ratio * (scrollbar_rect.height - slider_height)
            slider_rect = pygame.Rect(scrollbar_rect.x, slider_y, scrollbar_rect.width, slider_height)
            pygame.draw.rect(surface, COLORS["secondary"], slider_rect)
    
    def add_ai_player(self):
        """添加AI玩家"""
        if not self.is_host:
            self.add_chat_message("系统", "只有房主可以添加AI玩家", "system")
            return
        
        # 检查房间是否已满
        current_players = len(self.players)
        max_players = self.room_info.get("max_players", 4)
        
        if current_players >= max_players:
            self.add_chat_message("系统", "房间已满，无法添加AI玩家", "system")
            return
        
        # 发送添加AI玩家请求
        import threading
        import asyncio
        
        def add_ai_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.send_add_ai_player())
                loop.close()
            except Exception as e:
                self.add_chat_message("系统", f"添加AI玩家失败: {e}", "system")
        
        thread = threading.Thread(target=add_ai_async)
        thread.daemon = True
        thread.start()
    
    async def send_add_ai_player(self):
        """发送添加AI玩家请求"""
        try:
            from src.network.protocol import NetworkProtocol, MessageType
            
            message = NetworkProtocol.create_message(
                MessageType.ADD_AI_PLAYER,
                {"difficulty": "简单"},  # 默认简单难度
                sender_id=self.network_client.client_id
            )
            
            await self.network_client._send_message(message)
            self.add_chat_message("系统", "正在添加AI玩家...", "system")
        except Exception as e:
            print(f"发送添加AI玩家请求失败: {e}")
            self.add_chat_message("系统", f"添加AI玩家失败: {e}", "system") 