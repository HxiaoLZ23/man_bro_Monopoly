"""
增强版联机游戏界面
"""
import pygame
import asyncio
import sys
from typing import List, Dict, Any, Optional
from src.ui.constants import WINDOW_WIDTH, WINDOW_HEIGHT, COLORS, FONTS
from src.ui.components import Button, Panel, Text, Dialog
from src.ui.font_manager import get_font, render_text, get_text_size
from src.ui.room_management_window import RoomManagementWindow
from src.network.client.network_client import NetworkClient
from src.network.protocol import MessageType, NetworkMessage


class PlayerNameDialog:
    """玩家名称输入对话框"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.player_name = ""
        self.active = True
        self.cursor_visible = True
        self.cursor_timer = 0
        self.font = get_font("normal")
        self.result = None  # None, "ok", "cancel"
        
        # 按钮
        self.ok_button = Button(
            x + width - 160, y + height - 50, 70, 30,
            "确定", self.on_ok, COLORS["success"]
        )
        
        self.cancel_button = Button(
            x + width - 80, y + height - 50, 70, 30,
            "取消", self.on_cancel, COLORS["error"]
        )
    
    def on_ok(self):
        if self.player_name.strip():
            self.result = "ok"
            self.active = False
    
    def on_cancel(self):
        self.result = "cancel"
        self.active = False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.active:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
                return True
            elif event.key == pygame.K_RETURN:
                self.on_ok()
                return True
            elif event.key == pygame.K_ESCAPE:
                self.on_cancel()
                return True
            elif len(self.player_name) < 20:
                self.player_name += event.unicode
                return True
        
        # 处理按钮事件
        return self.ok_button.handle_event(event) or self.cancel_button.handle_event(event)
    
    def update(self, dt: float):
        if not self.active:
            return
        
        self.cursor_timer += dt
        if self.cursor_timer >= 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, surface: pygame.Surface):
        if not self.active:
            return
        
        # 半透明背景
        overlay = pygame.Surface(surface.get_size())
        overlay.set_alpha(128)
        overlay.fill(COLORS["background"])
        surface.blit(overlay, (0, 0))
        
        # 对话框背景
        pygame.draw.rect(surface, COLORS["surface"], self.rect, border_radius=8)
        pygame.draw.rect(surface, COLORS["border"], self.rect, 2, border_radius=8)
        
        # 标题
        title_surface = render_text("请输入玩家名称", "subtitle", COLORS["text_primary"], True)
        title_rect = title_surface.get_rect(center=(self.rect.centerx, self.rect.y + 30))
        surface.blit(title_surface, title_rect)
        
        # 输入框
        input_rect = pygame.Rect(self.rect.x + 20, self.rect.y + 60, self.rect.width - 40, 40)
        pygame.draw.rect(surface, COLORS["panel"], input_rect)
        pygame.draw.rect(surface, COLORS["border"], input_rect, 2)
        
        # 输入文本
        if self.player_name:
            text_surface = render_text(self.player_name, "normal", COLORS["text_primary"])
            surface.blit(text_surface, (input_rect.x + 10, input_rect.y + 10))
        else:
            placeholder_surface = render_text("输入玩家名称...", "normal", COLORS["text_secondary"])
            surface.blit(placeholder_surface, (input_rect.x + 10, input_rect.y + 10))
        
        # 光标
        if self.cursor_visible:
            cursor_x = input_rect.x + 10
            if self.player_name:
                text_width = get_text_size(self.player_name, "normal")[0]
                cursor_x += text_width
            pygame.draw.line(surface, COLORS["text_primary"], 
                           (cursor_x, input_rect.y + 5), 
                           (cursor_x, input_rect.bottom - 5), 2)
        
        # 按钮
        self.ok_button.draw(surface)
        self.cancel_button.draw(surface)


class EnhancedMultiplayerWindow:
    """增强版联机游戏窗口"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("大富翁 - 增强联机模式")
        
        # 网络客户端
        self.network_client = NetworkClient()
        self.setup_network_handlers()
        
        # 界面状态
        self.current_scene = "main_menu"  # main_menu, connecting, connected, in_room
        self.running = True
        
        # 数据
        self.player_name = ""
        self.connection_status = "disconnected"  # disconnected, connecting, connected
        self.current_room = None
        self.room_players = []
        self.pending_action = None  # 待执行的动作：create_room, join_room
        
        # UI组件
        self.buttons: List[Button] = []
        self.messages = []
        self.dialogs = []
        
        # 子窗口
        self.room_management_window: Optional[RoomManagementWindow] = None
        self.player_name_dialog: Optional[PlayerNameDialog] = None
        self.game_room_window = None  # 添加游戏房间窗口
        
        # 游戏时钟
        self.clock = pygame.time.Clock()
        
        self.init_main_menu()
    
    def setup_network_handlers(self):
        """设置网络消息处理器"""
        self.network_client.set_message_handler(MessageType.SUCCESS, self.handle_success)
        self.network_client.set_message_handler(MessageType.ERROR, self.handle_error)
        self.network_client.set_message_handler(MessageType.ROOM_INFO, self.handle_room_info)
        self.network_client.set_message_handler(MessageType.NOTIFICATION, self.handle_notification)
    
    def handle_success(self, message: NetworkMessage):
        """处理成功消息"""
        msg = message.data.get("message", "操作成功")
        self.add_message(msg, "success")
        
        # 根据消息内容更新状态
        if "连接成功" in msg:
            self.connection_status = "connected"
            self.init_connected_scene()
        elif "房间" in msg and ("创建" in msg or "加入" in msg):
            self.current_scene = "in_room"
            self.init_room_scene()
    
    def handle_error(self, message: NetworkMessage):
        """处理错误消息"""
        error_msg = message.data.get("error", "操作失败")
        self.add_message(error_msg, "error")
    
    def handle_room_info(self, message: NetworkMessage):
        """处理房间信息"""
        room_data = message.data.get("room")
        if room_data:
            self.current_room = room_data
            self.room_players = room_data.get("players", [])
    
    def handle_notification(self, message: NetworkMessage):
        """处理通知消息"""
        notification = message.data.get("notification", "未知通知")
        self.add_message(notification, "info")
    
    def add_message(self, text: str, msg_type: str = "info"):
        """添加消息"""
        self.messages.append({
            "text": text,
            "type": msg_type,
            "time": pygame.time.get_ticks()
        })
        
        # 限制消息数量
        if len(self.messages) > 5:
            self.messages.pop(0)
        
        print(f"[{msg_type.upper()}] {text}")
    
    def init_main_menu(self):
        """初始化主菜单"""
        self.current_scene = "main_menu"
        self.buttons.clear()
        
        button_width = 200
        button_height = 50
        button_x = WINDOW_WIDTH // 2 - button_width // 2
        
        # 创建房间按钮
        create_room_button = Button(
            button_x, 200, button_width, button_height,
            "创建房间", self.create_room_direct, COLORS["success"]
        )
        self.buttons.append(create_room_button)
        
        # 加入房间按钮
        join_room_button = Button(
            button_x, 270, button_width, button_height,
            "加入房间", self.join_room_direct, COLORS["primary"]
        )
        self.buttons.append(join_room_button)
        
        # 连接服务器按钮（高级选项）
        connect_button = Button(
            button_x, 340, button_width, button_height,
            "连接服务器", self.show_connect_dialog, COLORS["secondary"]
        )
        self.buttons.append(connect_button)
        
        # 启动本地服务器按钮
        server_button = Button(
            button_x, 410, button_width, button_height,
            "启动本地服务器", self.start_local_server, COLORS["warning"]
        )
        self.buttons.append(server_button)
        
        # 返回主菜单按钮
        back_button = Button(
            button_x, 480, button_width, button_height,
            "返回主菜单", self.close, COLORS["error"]
        )
        self.buttons.append(back_button)
    
    def init_connected_scene(self):
        """初始化已连接场景"""
        self.current_scene = "connected"
        self.buttons.clear()
        
        button_width = 200
        button_height = 50
        button_x = WINDOW_WIDTH // 2 - button_width // 2
        
        # 房间管理按钮
        room_button = Button(
            button_x, 250, button_width, button_height,
            "房间管理", self.open_room_management, COLORS["success"]
        )
        self.buttons.append(room_button)
        
        # 断开连接按钮
        disconnect_button = Button(
            button_x, 320, button_width, button_height,
            "断开连接", self.disconnect_server_sync, COLORS["warning"]
        )
        self.buttons.append(disconnect_button)
        
        # 返回主菜单按钮
        back_button = Button(
            button_x, 390, button_width, button_height,
            "返回主菜单", self.close, COLORS["error"]
        )
        self.buttons.append(back_button)
    
    def init_room_scene(self):
        """初始化房间场景"""
        self.current_scene = "in_room"
        self.buttons.clear()
        
        button_width = 150
        button_height = 40
        
        # 准备/取消准备按钮
        ready_button = Button(
            50, WINDOW_HEIGHT - 100, button_width, button_height,
            "准备", lambda: self.add_message("准备功能开发中...", "info"), COLORS["success"]
        )
        self.buttons.append(ready_button)
        
        # 开始游戏按钮（房主专用）
        start_button = Button(
            220, WINDOW_HEIGHT - 100, button_width, button_height,
            "开始游戏", lambda: self.add_message("开始游戏功能开发中...", "info"), COLORS["primary"]
        )
        self.buttons.append(start_button)
        
        # 离开房间按钮
        leave_button = Button(
            WINDOW_WIDTH - 200, WINDOW_HEIGHT - 100, button_width, button_height,
            "离开房间", self.leave_room_sync, COLORS["error"]
        )
        self.buttons.append(leave_button)
    
    def show_connect_dialog(self):
        """显示连接对话框"""
        dialog_width = 400
        dialog_height = 200
        dialog_x = WINDOW_WIDTH // 2 - dialog_width // 2
        dialog_y = WINDOW_HEIGHT // 2 - dialog_height // 2
        
        self.player_name_dialog = PlayerNameDialog(dialog_x, dialog_y, dialog_width, dialog_height)
    
    async def connect_to_server(self, player_name: str):
        """连接到服务器"""
        self.player_name = player_name
        self.connection_status = "connecting"
        self.add_message(f"正在连接服务器，玩家名: {player_name}", "info")
        
        # 启动网络客户端并等待连接结果
        try:
            success = await self.network_client.start_client(player_name)
            if success:
                self.add_message("连接成功！", "success")
                self.connection_status = "connected"
                
                # 处理待执行的动作
                if self.pending_action == "create_room":
                    self.open_room_management_with_action("create")
                    self.pending_action = None
                elif self.pending_action == "join_room":
                    self.open_room_management_with_action("join")
                    self.pending_action = None
                else:
                    self.init_connected_scene()
            else:
                self.add_message("连接失败", "error")
                self.connection_status = "disconnected"
                self.pending_action = None
        except Exception as e:
            self.add_message(f"连接错误: {e}", "error")
            self.connection_status = "disconnected"
            self.pending_action = None
    
    def start_local_server(self):
        """启动本地服务器"""
        try:
            import subprocess
            import os
            
            # 查找服务器脚本，优先使用房间管理服务器
            server_files = ["room_server.py", "quick_server.py", "simple_server.py", "enhanced_server.py"]
            server_started = False
            
            for server_file in server_files:
                server_path = os.path.join(os.getcwd(), server_file)
                if os.path.exists(server_path):
                    subprocess.Popen([
                        "python", server_path
                    ], creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
                    self.add_message(f"✅ 本地服务器启动成功 ({server_file})", "success")
                    server_started = True
                    break
            
            if not server_started:
                self.add_message("❌ 找不到服务器启动脚本", "error")
                
        except Exception as e:
            self.add_message(f"❌ 启动服务器失败: {e}", "error")
    
    def open_room_management(self):
        """打开房间管理"""
        if self.connection_status != "connected":
            self.add_message("请先连接服务器", "error")
            return
        
        self.room_management_window = RoomManagementWindow(
            self.network_client,
            self.close_room_management,
            self.on_room_joined  # 添加房间加入成功回调
        )
    
    def close_room_management(self, event_type=None, data=None):
        """关闭房间管理窗口"""
        if event_type == "room_opened" and data:
            # 房间窗口已创建，设置为当前的游戏房间窗口
            self.game_room_window = data
            # 设置游戏房间窗口的关闭回调
            if self.game_room_window:
                self.game_room_window.on_close = self.on_game_room_close
            # 不关闭房间管理窗口，只是设置游戏房间窗口
            return
        
        if event_type == "game_start" and data:
            # 游戏开始事件，启动游戏
            print(f"🎮 收到游戏开始事件: {data}")
            self.start_multiplayer_game(data)
            return
        
        if self.room_management_window:
            self.room_management_window.running = False
            # 检查房间管理窗口是否创建了游戏房间窗口
            if hasattr(self.room_management_window, 'room_window'):
                self.game_room_window = self.room_management_window.room_window
                # 设置游戏房间窗口的关闭回调
                if self.game_room_window:
                    self.game_room_window.on_close = self.on_game_room_close
            self.room_management_window = None
    
    def on_room_joined(self, room_data: dict):
        """房间加入成功回调"""
        self.current_room = room_data
        self.room_players = room_data.get("players", [])
        self.current_scene = "in_room"
        # 不要调用init_room_scene，因为我们将使用游戏房间窗口
        self.close_room_management()
        self.add_message(f"成功进入房间: {room_data.get('name', '未知房间')}", "success")
    
    def create_room_direct(self):
        """直接创建房间（自动连接服务器）"""
        if self.connection_status != "connected":
            # 如果未连接，显示玩家名输入对话框
            self.pending_action = "create_room"
            self.show_connect_dialog()
        else:
            # 已连接，直接打开房间管理并创建房间
            self.open_room_management_with_action("create")
    
    def join_room_direct(self):
        """直接加入房间（自动连接服务器）"""
        if self.connection_status != "connected":
            # 如果未连接，显示玩家名输入对话框
            self.pending_action = "join_room"
            self.show_connect_dialog()
        else:
            # 已连接，直接打开房间管理并显示房间列表
            self.open_room_management_with_action("join")
    
    def open_room_management_with_action(self, action: str):
        """打开房间管理窗口并执行指定动作"""
        if self.connection_status != "connected":
            self.add_message("请先连接服务器", "error")
            return
        
        self.room_management_window = RoomManagementWindow(
            self.network_client,
            self.close_room_management,
            self.on_room_joined  # 添加房间加入成功回调
        )
        
        # 根据动作设置房间管理窗口的初始状态
        if action == "create":
            # 可以在这里添加自动创建房间的逻辑
            self.add_message("请在房间管理窗口中创建新房间", "info")
        elif action == "join":
            # 可以在这里添加自动刷新房间列表的逻辑
            self.add_message("请在房间管理窗口中选择要加入的房间", "info")
    
    async def disconnect_server(self):
        """断开服务器连接"""
        await self.network_client.stop_client()
        self.connection_status = "disconnected"
        self.current_room = None
        self.room_players = []
        self.add_message("已断开连接", "info")
        self.init_main_menu()
    
    async def toggle_ready(self):
        """切换准备状态"""
        # 这里需要实现准备状态切换逻辑
        self.add_message("准备状态切换功能开发中...", "info")
    
    async def start_game(self):
        """开始游戏"""
        # 这里需要实现开始游戏逻辑
        self.add_message("开始游戏功能开发中...", "info")
    
    async def leave_room(self):
        """离开房间"""
        if self.network_client.current_room_id:
            success = await self.network_client.leave_room()
            if success:
                self.current_room = None
                self.room_players = []
                self.init_connected_scene()
    
    def close(self):
        """关闭窗口"""
        self.running = False
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            # 优先处理游戏房间窗口事件
            if self.game_room_window and self.game_room_window.running:
                if self.game_room_window.handle_event(event):
                    continue
            
            # 然后处理房间管理窗口事件
            if self.room_management_window and self.room_management_window.running:
                if self.room_management_window.handle_event(event):
                    continue
            
            # 处理玩家名称对话框事件
            if self.player_name_dialog:
                if self.player_name_dialog.handle_event(event):
                    if self.player_name_dialog.result == "ok":
                        player_name = self.player_name_dialog.player_name
                        self.player_name_dialog = None
                        # 连接到服务器
                        self.connect_to_server_sync(player_name)
                    elif self.player_name_dialog.result == "cancel":
                        self.player_name_dialog = None
                        self.pending_action = None
                    continue
            
            # 处理按钮事件
            for button in self.buttons:
                if button.handle_event(event):
                    break
            
            # 处理键盘事件
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_scene == "in_room":
                        # 使用同步方法离开房间
                        self.leave_room_sync()
    
    def connect_to_server_sync(self, player_name: str):
        """同步连接到服务器"""
        import threading
        import asyncio
        
        def connect_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.connect_to_server(player_name))
                loop.close()
            except Exception as e:
                self.add_message(f"连接错误: {e}", "error")
        
        thread = threading.Thread(target=connect_async)
        thread.daemon = True
        thread.start()
    
    def leave_room_sync(self):
        """同步离开房间"""
        import threading
        import asyncio
        
        def leave_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.leave_room())
                loop.close()
            except Exception as e:
                self.add_message(f"离开房间错误: {e}", "error")
        
        thread = threading.Thread(target=leave_async)
        thread.daemon = True
        thread.start()
    
    def disconnect_server_sync(self):
        """同步断开服务器连接"""
        import threading
        import asyncio
        
        def disconnect_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.disconnect_server())
                loop.close()
            except Exception as e:
                self.add_message(f"断开连接错误: {e}", "error")
        
        thread = threading.Thread(target=disconnect_async)
        thread.daemon = True
        thread.start()
    
    def update(self, dt: float):
        """更新"""
        # 更新玩家名称对话框
        if self.player_name_dialog:
            self.player_name_dialog.update(dt)
        
        # 更新房间管理窗口
        if self.room_management_window:
            self.room_management_window.update(dt)
        
        # 更新游戏房间窗口
        if self.game_room_window:
            self.game_room_window.update(dt)
            # 检查游戏房间窗口是否被关闭
            if not self.game_room_window.running:
                self.on_game_room_close()
        
        # 清理过期消息
        current_time = pygame.time.get_ticks()
        self.messages = [msg for msg in self.messages if current_time - msg["time"] < 5000]
    
    def draw(self):
        """绘制"""
        self.screen.fill(COLORS["background"])
        
        # 如果有游戏房间窗口，优先绘制它
        if self.game_room_window and self.game_room_window.running:
            self.game_room_window.draw(self.screen)
            pygame.display.flip()
            return
        
        # 绘制标题
        if self.current_scene == "main_menu":
            title = "联机模式"
        elif self.current_scene == "connecting":
            title = "正在连接..."
        elif self.current_scene == "connected":
            title = f"已连接 - {self.player_name}"
        elif self.current_scene == "in_room":
            room_name = self.current_room.get("name", "未知房间") if self.current_room else "房间"
            title = f"房间: {room_name}"
        else:
            title = "联机模式"
        
        title_surface = render_text(title, "title", COLORS["text_primary"], True)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 60))
        self.screen.blit(title_surface, title_rect)
        
        # 绘制连接状态
        status_text = {
            "disconnected": "未连接",
            "connecting": "连接中...",
            "connected": "已连接"
        }.get(self.connection_status, "未知状态")
        
        status_color = {
            "disconnected": COLORS["error"],
            "connecting": COLORS["warning"],
            "connected": COLORS["success"]
        }.get(self.connection_status, COLORS["text_secondary"])
        
        status_surface = render_text(f"状态: {status_text}", "normal", status_color)
        self.screen.blit(status_surface, (20, 20))
        
        # 绘制房间信息
        if self.current_scene == "in_room" and self.current_room:
            room_info_y = 120
            
            # 房间基本信息
            room_name = self.current_room.get("name", "未知房间")
            current_players = self.current_room.get("current_players", 0)
            max_players = self.current_room.get("max_players", 4)
            
            info_text = f"房间: {room_name}  玩家: {current_players}/{max_players}"
            info_surface = render_text(info_text, "subtitle", COLORS["text_primary"])
            info_rect = info_surface.get_rect(center=(WINDOW_WIDTH // 2, room_info_y))
            self.screen.blit(info_surface, info_rect)
            
            # 玩家列表
            players_title = render_text("玩家列表:", "normal", COLORS["text_primary"], True)
            self.screen.blit(players_title, (50, room_info_y + 50))
            
            for i, player in enumerate(self.room_players):
                player_name = player.get("name", "未知玩家")
                is_ready = player.get("is_ready", False)
                is_host = player.get("is_host", False)
                
                # 状态图标
                status_icon = "👑" if is_host else ("✅" if is_ready else "⏳")
                player_text = f"{status_icon} {player_name}"
                
                player_surface = render_text(player_text, "normal", COLORS["text_primary"])
                self.screen.blit(player_surface, (70, room_info_y + 80 + i * 25))
        
        # 绘制按钮
        for button in self.buttons:
            button.draw(self.screen)
        
        # 绘制消息
        self.draw_messages()
        
        # 绘制房间管理窗口
        if self.room_management_window and self.room_management_window.running:
            self.room_management_window.draw(self.screen)
        
        # 绘制玩家名称对话框
        if self.player_name_dialog:
            self.player_name_dialog.draw(self.screen)
        
        pygame.display.flip()
    
    def draw_messages(self):
        """绘制消息"""
        if not self.messages:
            return
        
        y_offset = WINDOW_HEIGHT - 150
        for i, msg in enumerate(reversed(self.messages)):
            color = {
                "info": COLORS["text_secondary"],
                "success": COLORS["success"],
                "error": COLORS["error"],
                "warning": COLORS["warning"]
            }.get(msg["type"], COLORS["text_primary"])
            
            text_surface = render_text(msg["text"], "normal", color)
            self.screen.blit(text_surface, (20, y_offset - i * 25))
    
    def on_game_room_close(self):
        """游戏房间窗口关闭回调"""
        self.game_room_window = None
        self.current_room = None
        self.room_players = []
        self.current_scene = "connected"
        self.init_connected_scene()
        self.add_message("已离开房间", "info")
    
    def start_multiplayer_game(self, game_data: dict):
        """启动多人游戏"""
        print(f"🚀 启动多人游戏: {game_data}")
        
        try:
            # 关闭所有子窗口
            if self.room_management_window:
                self.room_management_window.running = False
                self.room_management_window = None
            
            if self.game_room_window:
                self.game_room_window.running = False
                self.game_room_window = None
            
            # 启动主游戏
            self.launch_main_game(game_data)
            
        except Exception as e:
            print(f"❌ 启动游戏失败: {e}")
            import traceback
            traceback.print_exc()
            self.add_message(f"启动游戏失败: {e}", "error")

    def launch_main_game(self, game_data: dict):
        """启动主游戏"""
        print(f"🎯 启动主游戏界面")
        
        try:
            # 导入主窗口类
            print(f"📦 导入主窗口类...")
            from src.ui.main_window import MainWindow
            
            # 创建主游戏窗口实例，重用现有的pygame显示窗口
            print(f"🔧 创建主游戏窗口...")
            main_window = MainWindow(screen=self.screen)
            print(f"✅ 主游戏窗口创建成功")
            
            # 设置多人游戏模式
            print(f"📡 设置网络游戏模式...")
            main_window.network_client = self.network_client
            main_window.is_multiplayer = True
            main_window.multiplayer_data = game_data
            
            # 加载地图
            map_file = game_data.get('map_file', '1.json')
            print(f"🗺️ 准备加载地图: {map_file}")
            
            # 初始化游戏状态
            print(f"🎲 初始化多人游戏...")
            result = main_window.init_multiplayer_game(game_data)
            
            if not result:
                print(f"❌ 多人游戏初始化失败")
                self.add_message("游戏初始化失败", "error")
                return
            
            print(f"✅ 多人游戏初始化成功")
            
            # 关闭当前窗口
            print(f"🔄 关闭联机窗口...")
            self.running = False
            
            # 运行主游戏
            print(f"🎮 启动游戏主循环...")
            main_window.run()
            
        except ImportError as e:
            print(f"❌ 导入主窗口失败: {e}")
            import traceback
            traceback.print_exc()
            self.add_message("无法启动游戏主界面", "error")
        except Exception as e:
            print(f"❌ 启动游戏异常: {e}")
            import traceback
            traceback.print_exc()
            self.add_message(f"游戏启动异常: {e}", "error")
    
    def run(self):
        """运行主循环"""
        print("🚀 启动增强版联机窗口...")
        
        while self.running:
            dt = self.clock.tick(60)
            
            self.handle_events()
            self.update(dt)
            self.draw()
        
        # 清理
        if self.network_client.is_connected():
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.network_client.stop_client())
                loop.close()
            except Exception as e:
                print(f"清理网络连接时出错: {e}")
        
        print("✅ 增强版联机窗口已关闭") 