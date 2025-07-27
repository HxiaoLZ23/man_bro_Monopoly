"""
房间管理界面
"""
import pygame
import asyncio
from typing import List, Dict, Any, Optional, Callable
from src.ui.constants import WINDOW_WIDTH, WINDOW_HEIGHT, COLORS, FONTS
from src.ui.components import Button, Panel, Text, Dialog
from src.ui.font_manager import get_font, render_text, get_text_size
from src.network.client.network_client import NetworkClient
from src.network.protocol import MessageType, NetworkMessage


class InputBox:
    """输入框组件"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 placeholder: str = "", max_length: int = 50, password: bool = False):
        self.rect = pygame.Rect(x, y, width, height)
        self.placeholder = placeholder
        self.max_length = max_length
        self.password = password
        self.text = ""
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        # 延迟获取字体，确保字体管理器已初始化
        self.font = None
    
    def _get_font(self):
        """获取字体，确保字体管理器已初始化"""
        if self.font is None:
            self.font = get_font("normal")
        return self.font
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            return self.active
        
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                return True
            elif event.key == pygame.K_RETURN:
                self.active = False
                return True
            elif len(self.text) < self.max_length:
                self.text += event.unicode
                return True
        
        return False
    
    def update(self, dt: float):
        """更新光标闪烁"""
        self.cursor_timer += dt
        if self.cursor_timer >= 500:  # 500ms
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, surface: pygame.Surface):
        """绘制输入框"""
        # 背景
        color = COLORS.get("input_focus", COLORS["surface"]) if self.active else COLORS.get("input_bg", COLORS["panel"])
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, COLORS["border"], self.rect, 2)
        
        # 文本
        display_text = self.text
        if self.password and self.text:
            display_text = "*" * len(self.text)
        elif not self.text and not self.active:
            display_text = self.placeholder
        
        if display_text:
            text_color = COLORS["text_primary"] if self.text else COLORS["text_secondary"]
            text_surface = render_text(display_text, "normal", text_color)
            text_rect = text_surface.get_rect(left=self.rect.x + 10, centery=self.rect.centery)
            surface.blit(text_surface, text_rect)
        
        # 光标
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 10
            if self.text:
                text_width = get_text_size(display_text, "normal")[0]
                cursor_x += text_width
            pygame.draw.line(surface, COLORS["text_primary"], 
                           (cursor_x, self.rect.y + 5), 
                           (cursor_x, self.rect.bottom - 5), 2)


class RoomCard:
    """房间卡片组件"""
    
    def __init__(self, x: int, y: int, width: int, height: int, room_data: Dict[str, Any]):
        self.rect = pygame.Rect(x, y, width, height)
        self.room_data = room_data
        self.join_button = Button(
            x + width - 80, y + height - 35, 70, 25,
            "加入", None, COLORS["success"], font_size="small"
        )
        self.is_hovered = False
        
    def set_join_callback(self, callback: Callable):
        """设置加入回调"""
        self.join_button.callback = callback
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        
        return self.join_button.handle_event(event)
    
    def draw(self, surface: pygame.Surface):
        """绘制房间卡片"""
        # 背景
        bg_color = COLORS.get("surface_hover", COLORS["surface"]) if self.is_hovered else COLORS["surface"]
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, COLORS["border"], self.rect, 2, border_radius=8)
        
        # 房间信息
        room_name = self.room_data.get("name", "未知房间")
        current_players = self.room_data.get("current_players", 0)
        max_players = self.room_data.get("max_players", 4)
        has_password = self.room_data.get("has_password", False)
        state = self.room_data.get("state", "waiting")
        
        # 房间名称
        name_surface = render_text(room_name, "subtitle", COLORS["text_primary"], True)
        surface.blit(name_surface, (self.rect.x + 15, self.rect.y + 10))
        
        # 玩家数量
        player_text = f"玩家: {current_players}/{max_players}"
        player_surface = render_text(player_text, "normal", COLORS["text_secondary"])
        surface.blit(player_surface, (self.rect.x + 15, self.rect.y + 35))
        
        # 状态标签
        state_text = {"waiting": "等待中", "playing": "游戏中", "finished": "已结束"}.get(state, state)
        state_color = {"waiting": COLORS["success"], "playing": COLORS["warning"], "finished": COLORS["error"]}.get(state, COLORS["text_secondary"])
        state_surface = render_text(state_text, "small", state_color)
        surface.blit(state_surface, (self.rect.x + 15, self.rect.y + 55))
        
        # 密码图标
        if has_password:
            lock_surface = render_text("🔒", "small", COLORS["warning"])
            surface.blit(lock_surface, (self.rect.x + self.rect.width - 120, self.rect.y + 10))
        
        # 加入按钮
        if state == "waiting" and current_players < max_players:
            self.join_button.enabled = True
            self.join_button.draw(surface)
        else:
            self.join_button.enabled = False


class RoomManagementWindow:
    """房间管理窗口"""
    
    def __init__(self, network_client: NetworkClient, on_close: Callable = None, on_room_joined: Callable = None):
        self.network_client = network_client
        self.on_close = on_close
        self.on_room_joined = on_room_joined  # 房间加入成功回调
        self.running = True
        
        # 界面状态
        self.current_scene = "room_list"  # room_list, create_room, join_room
        
        # 数据
        self.room_list = []
        self.selected_room = None
        self.player_name = ""
        
        # UI组件
        self.buttons = []
        self.input_boxes = []
        self.room_cards = []
        self.messages = []
        
        # 输入框
        self.room_name_input = None
        self.max_players_input = None
        self.password_input = None
        self.room_id_input = None
        self.join_password_input = None
        
        # 滚动
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # 设置网络处理器
        self.setup_network_handlers()
        
        # 初始化界面
        self.init_room_list_scene()
        
        # 请求房间列表
        self.refresh_room_list_sync()
    
    def setup_network_handlers(self):
        """设置网络消息处理器"""
        self.network_client.set_message_handler(MessageType.ROOM_LIST, self.handle_room_list)
        self.network_client.set_message_handler(MessageType.SUCCESS, self.handle_success)
        self.network_client.set_message_handler(MessageType.ERROR, self.handle_error)
        self.network_client.set_message_handler(MessageType.ROOM_INFO, self.handle_room_info)
    
    def handle_room_list(self, message: NetworkMessage):
        """处理房间列表消息"""
        self.room_list = message.data.get("rooms", [])
        self.update_room_cards()
    
    def handle_success(self, message: NetworkMessage):
        """处理成功消息"""
        msg = message.data.get("message", "操作成功")
        self.add_message(msg, "success")
        
        # 如果是创建或加入房间成功，等待房间信息
        if "创建房间" in msg or "加入房间" in msg:
            self.add_message("等待房间信息...", "info")
    
    def handle_error(self, message: NetworkMessage):
        """处理错误消息"""
        error_msg = message.data.get("error", "操作失败")
        self.add_message(error_msg, "error")
    
    def handle_room_info(self, message: NetworkMessage):
        """处理房间信息消息"""
        print(f"🏠 收到房间信息: {message.data}")
        room_data = message.data.get("room", {})
        if room_data:
            print(f"🚪 准备打开房间窗口: {room_data.get('name', '未知房间')}")
            # 直接打开房间窗口
            self.open_room_window(room_data)
        else:
            print("❌ 房间数据为空")
    
    def open_room_window(self, room_data: dict):
        """打开房间界面"""
        print(f"🔧 开始创建房间窗口，房间数据: {room_data}")
        try:
            from src.ui.game_room_window import GameRoomWindow
            print("✅ 成功导入GameRoomWindow")
            
            # 创建房间窗口
            print("🔨 正在创建GameRoomWindow实例...")
            self.room_window = GameRoomWindow(
                self.network_client, 
                room_data, 
                self.on_room_window_close,
                self.on_game_start  # 添加游戏开始回调
            )
            print("✅ GameRoomWindow实例创建成功")
            
            # 通知父窗口房间窗口已创建
            if self.on_close:
                print("📞 通知父窗口房间窗口已创建")
                self.on_close("room_opened", self.room_window)
            else:
                print("⚠️ 没有父窗口回调")
            
            # 隐藏房间管理窗口
            self.running = False
            print("🚪 房间管理窗口已隐藏")
            
        except ImportError as e:
            print(f"❌ 导入错误: {e}")
            self.add_message(f"无法打开房间界面: {e}", "error")
        except Exception as e:
            print(f"❌ 创建房间窗口错误: {e}")
            import traceback
            traceback.print_exc()
            self.add_message(f"创建房间窗口失败: {e}", "error")
    
    def on_room_window_close(self):
        """房间窗口关闭回调"""
        # 重新显示房间管理窗口
        self.running = True
        self.init_room_list_scene()
        # 刷新房间列表
        self.refresh_room_list_sync()
    
    def on_game_start(self, game_data: dict):
        """游戏开始回调"""
        # 这里可以启动游戏或通知父窗口
        print(f"🎮 游戏开始！地图: {game_data.get('map_file', '未知')}")
        if self.on_close:
            # 通知父窗口游戏开始
            self.on_close("game_start", game_data)
    
    def add_message(self, text: str, msg_type: str = "info"):
        """添加消息"""
        self.messages.append({
            "text": text,
            "type": msg_type,
            "time": pygame.time.get_ticks()
        })
        
        # 限制消息数量
        if len(self.messages) > 3:
            self.messages.pop(0)
    
    def init_room_list_scene(self):
        """初始化房间列表场景"""
        self.current_scene = "room_list"
        self.buttons.clear()
        self.input_boxes.clear()
        self.room_cards.clear()
        
        # 标题按钮
        create_button = Button(
            20, 20, 120, 40,
            "创建房间", self.init_create_room_scene, COLORS["success"]
        )
        self.buttons.append(create_button)
        
        refresh_button = Button(
            160, 20, 120, 40,
            "刷新列表", lambda: self.refresh_room_list_sync()
        )
        self.buttons.append(refresh_button)
        
        close_button = Button(
            WINDOW_WIDTH - 140, 20, 120, 40,
            "关闭", self.close, COLORS["error"]
        )
        self.buttons.append(close_button)
        
        # 更新房间卡片
        self.update_room_cards()
    
    def init_create_room_scene(self):
        """初始化创建房间场景"""
        self.current_scene = "create_room"
        self.buttons.clear()
        self.input_boxes.clear()
        
        # 返回按钮
        back_button = Button(
            20, 20, 100, 40,
            "返回", self.init_room_list_scene, COLORS["secondary"]
        )
        self.buttons.append(back_button)
        
        # 输入框
        center_x = WINDOW_WIDTH // 2
        
        # 房间名称
        self.room_name_input = InputBox(
            center_x - 150, 150, 300, 40,
            "请输入房间名称", 30
        )
        self.input_boxes.append(self.room_name_input)
        
        # 最大玩家数
        self.max_players_input = InputBox(
            center_x - 150, 220, 300, 40,
            "最大玩家数 (2-6)", 1
        )
        self.input_boxes.append(self.max_players_input)
        
        # 房间密码（可选）
        self.password_input = InputBox(
            center_x - 150, 290, 300, 40,
            "房间密码（可选）", 20, True
        )
        self.input_boxes.append(self.password_input)
        
        # 创建按钮
        create_button = Button(
            center_x - 100, 360, 200, 50,
            "创建房间", self.create_room_sync, COLORS["success"]
        )
        self.buttons.append(create_button)
    
    def init_join_room_scene(self, room_data: Dict[str, Any]):
        """初始化加入房间场景"""
        self.current_scene = "join_room"
        self.selected_room = room_data
        self.buttons.clear()
        self.input_boxes.clear()
        
        # 返回按钮
        back_button = Button(
            20, 20, 100, 40,
            "返回", self.init_room_list_scene, COLORS["secondary"]
        )
        self.buttons.append(back_button)
        
        center_x = WINDOW_WIDTH // 2
        
        # 如果房间有密码，显示密码输入框
        if room_data.get("has_password", False):
            self.join_password_input = InputBox(
                center_x - 150, 200, 300, 40,
                "请输入房间密码", 20, True
            )
            self.input_boxes.append(self.join_password_input)
            button_y = 280
        else:
            button_y = 200
        
        # 加入按钮
        join_button = Button(
            center_x - 100, button_y, 200, 50,
            "加入房间", self.join_room_sync, COLORS["success"]
        )
        self.buttons.append(join_button)
    
    def update_room_cards(self):
        """更新房间卡片"""
        self.room_cards.clear()
        
        card_width = WINDOW_WIDTH - 40
        card_height = 80
        start_y = 80
        
        for i, room_data in enumerate(self.room_list):
            card_y = start_y + i * (card_height + 10) - self.scroll_offset
            
            # 只创建可见的卡片
            if card_y + card_height > 0 and card_y < WINDOW_HEIGHT:
                card = RoomCard(20, card_y, card_width, card_height, room_data)
                card.set_join_callback(lambda r=room_data: self.init_join_room_scene(r))
                self.room_cards.append(card)
        
        # 计算最大滚动距离
        total_height = len(self.room_list) * (card_height + 10)
        visible_height = WINDOW_HEIGHT - start_y
        self.max_scroll = max(0, total_height - visible_height)
    
    def refresh_room_list_sync(self):
        """同步刷新房间列表"""
        import threading
        import asyncio
        
        def refresh_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.refresh_room_list())
                loop.close()
            except Exception as e:
                self.add_message(f"刷新错误: {e}", "error")
        
        thread = threading.Thread(target=refresh_async)
        thread.daemon = True
        thread.start()
    
    def create_room_sync(self):
        """同步创建房间"""
        import threading
        import asyncio
        
        def create_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.create_room())
                loop.close()
            except Exception as e:
                self.add_message(f"创建房间错误: {e}", "error")
        
        thread = threading.Thread(target=create_async)
        thread.daemon = True
        thread.start()
    
    def join_room_sync(self):
        """同步加入房间"""
        import threading
        import asyncio
        
        def join_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.join_room())
                loop.close()
            except Exception as e:
                self.add_message(f"加入房间错误: {e}", "error")
        
        thread = threading.Thread(target=join_async)
        thread.daemon = True
        thread.start()
    
    async def refresh_room_list(self):
        """刷新房间列表"""
        await self.network_client.request_room_list()
        self.add_message("正在刷新房间列表...", "info")
    
    async def create_room(self):
        """创建房间"""
        print("🔍 开始创建房间...")
        print(f"🌐 网络客户端连接状态: {self.network_client.is_connected()}")
        print(f"🌐 网络客户端状态: {self.network_client.get_connection_state()}")
        print(f"👤 玩家名称: {self.network_client.player_name}")
        print(f"🆔 客户端ID: {self.network_client.client_id}")
        
        if not self.network_client.is_connected():
            print("❌ 网络客户端未连接")
            self.add_message("未连接到服务器，请先连接", "error")
            return
        
        if not self.room_name_input or not self.room_name_input.text.strip():
            print("❌ 房间名称为空")
            self.add_message("请输入房间名称", "error")
            return
        
        room_name = self.room_name_input.text.strip()
        print(f"🏠 房间名称: {room_name}")
        
        # 验证最大玩家数
        max_players = 4  # 默认值
        if self.max_players_input and self.max_players_input.text.strip():
            try:
                max_players = int(self.max_players_input.text.strip())
                if max_players < 2 or max_players > 6:
                    print(f"❌ 无效的最大玩家数: {max_players}")
                    self.add_message("最大玩家数必须在2-6之间", "error")
                    return
            except ValueError:
                print(f"❌ 无法解析最大玩家数: {self.max_players_input.text}")
                self.add_message("请输入有效的最大玩家数", "error")
                return
        
        print(f"👥 最大玩家数: {max_players}")
        
        password = None
        if self.password_input and self.password_input.text.strip():
            password = self.password_input.text.strip()
            print(f"🔒 房间密码: {'已设置' if password else '未设置'}")
        
        # 发送创建房间请求
        try:
            print("📤 发送创建房间请求...")
            success = await self.network_client.create_room(room_name, max_players, password)
            print(f"📥 创建房间结果: {success}")
            if success:
                self.add_message("正在创建房间...", "info")
            else:
                self.add_message("创建房间失败", "error")
        except Exception as e:
            print(f"❌ 创建房间异常: {e}")
            import traceback
            traceback.print_exc()
            self.add_message(f"创建房间错误: {e}", "error")
    
    async def join_room(self):
        """加入房间"""
        if not self.selected_room:
            self.add_message("未选择房间", "error")
            return
        
        room_id = self.selected_room.get("room_id")
        if not room_id:
            self.add_message("房间ID无效", "error")
            return
        
        password = None
        if self.join_password_input and self.join_password_input.text.strip():
            password = self.join_password_input.text.strip()
        elif self.selected_room.get("has_password", False):
            self.add_message("请输入房间密码", "error")
            return
        
        # 发送加入房间请求
        success = await self.network_client.join_room(room_id, password)
        if success:
            self.add_message("正在加入房间...", "info")
        else:
            self.add_message("加入房间失败", "error")
    
    def close(self):
        """关闭窗口"""
        self.running = False
        if self.on_close:
            self.on_close()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件"""
        if not self.running:
            return False
        
        # 处理滚动
        if event.type == pygame.MOUSEWHEEL and self.current_scene == "room_list":
            self.scroll_offset -= event.y * 30
            self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
            self.update_room_cards()
            return True
        
        # 处理按钮事件
        for button in self.buttons:
            if button.handle_event(event):
                return True
        
        # 处理输入框事件
        for input_box in self.input_boxes:
            if input_box.handle_event(event):
                return True
        
        # 处理房间卡片事件
        for card in self.room_cards:
            if card.handle_event(event):
                return True
        
        return False
    
    def update(self, dt: float):
        """更新"""
        if not self.running:
            return
        
        # 更新输入框
        for input_box in self.input_boxes:
            input_box.update(dt)
        
        # 清理过期消息
        current_time = pygame.time.get_ticks()
        self.messages = [msg for msg in self.messages if current_time - msg["time"] < 5000]
    
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
        if self.current_scene == "room_list":
            title = "房间列表"
        elif self.current_scene == "create_room":
            title = "创建房间"
        elif self.current_scene == "join_room":
            title = f"加入房间 - {self.selected_room.get('name', '未知房间')}"
        else:
            title = "房间管理"
        
        title_surface = render_text(title, "title", COLORS["text_primary"], True)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 40))
        surface.blit(title_surface, title_rect)
        
        # 绘制按钮
        for button in self.buttons:
            button.draw(surface)
        
        # 绘制输入框
        for input_box in self.input_boxes:
            input_box.draw(surface)
        
        # 绘制输入框标签
        if self.current_scene == "create_room":
            center_x = WINDOW_WIDTH // 2
            
            # 房间名称标签
            name_label = render_text("房间名称:", "normal", COLORS["text_primary"])
            surface.blit(name_label, (center_x - 150, 125))
            
            # 最大玩家数标签
            players_label = render_text("最大玩家数:", "normal", COLORS["text_primary"])
            surface.blit(players_label, (center_x - 150, 195))
            
            # 密码标签
            password_label = render_text("房间密码:", "normal", COLORS["text_primary"])
            surface.blit(password_label, (center_x - 150, 265))
        
        elif self.current_scene == "join_room":
            center_x = WINDOW_WIDTH // 2
            
            # 房间信息
            if self.selected_room:
                room_name = self.selected_room.get("name", "未知房间")
                current_players = self.selected_room.get("current_players", 0)
                max_players = self.selected_room.get("max_players", 4)
                
                info_text = f"房间: {room_name}  玩家: {current_players}/{max_players}"
                info_surface = render_text(info_text, "subtitle", COLORS["text_primary"])
                info_rect = info_surface.get_rect(center=(center_x, 120))
                surface.blit(info_surface, info_rect)
                
                # 密码标签
                if self.selected_room.get("has_password", False):
                    password_label = render_text("房间密码:", "normal", COLORS["text_primary"])
                    surface.blit(password_label, (center_x - 150, 175))
        
        # 绘制房间卡片
        for card in self.room_cards:
            card.draw(surface)
        
        # 如果没有房间，显示提示
        if self.current_scene == "room_list" and not self.room_list:
            no_rooms_text = render_text("暂无房间，点击创建房间开始游戏", "subtitle", COLORS["text_secondary"])
            no_rooms_rect = no_rooms_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            surface.blit(no_rooms_text, no_rooms_rect)
        
        # 绘制消息
        self.draw_messages(surface)
    
    def draw_messages(self, surface: pygame.Surface):
        """绘制消息"""
        if not self.messages:
            return
        
        y_offset = WINDOW_HEIGHT - 100
        for i, msg in enumerate(reversed(self.messages)):
            color = {
                "info": COLORS["text_secondary"],
                "success": COLORS["success"],
                "error": COLORS["error"],
                "warning": COLORS["warning"]
            }.get(msg["type"], COLORS["text_primary"])
            
            text_surface = render_text(msg["text"], "normal", color)
            surface.blit(text_surface, (20, y_offset - i * 25)) 