"""
联机游戏界面
"""
import pygame
import sys
from typing import List, Dict, Any, Optional

try:
    from src.ui.constants import WINDOW_WIDTH, WINDOW_HEIGHT, COLORS, FONTS
    from src.ui.components import Button, Panel, Text, Dialog
    from src.ui.font_manager import get_font, render_text
except ImportError:
    # 如果导入失败，使用默认值
    WINDOW_WIDTH = 1024
    WINDOW_HEIGHT = 768
    COLORS = {
        "background": (240, 248, 255),
        "text": (0, 0, 0),
        "primary": (70, 130, 180),
        "success": (34, 139, 34),
        "error": (220, 20, 60),
        "warning": (255, 165, 0),
        "disabled": (128, 128, 128),
        "panel_bg": (255, 255, 255),
        "border": (128, 128, 128),
        "input_bg": (248, 248, 255)
    }

try:
    from src.network.client.network_client import NetworkClient
    from src.network.protocol import MessageType, NetworkMessage
except ImportError:
    # 如果网络模块未找到，创建占位符
    class NetworkClient:
        def __init__(self, *args, **kwargs):
            pass
        def is_connected(self):
            return False
        def start_client(self, name):
            print(f"模拟启动客户端: {name}")
        def stop_client(self):
            print("模拟停止客户端")
        def create_room(self, name, max_players=4, password=None):
            print(f"模拟创建房间: {name}")
        def join_room(self, room_id, password=None):
            print(f"模拟加入房间: {room_id}")
        def leave_room(self):
            print("模拟离开房间")
        def request_room_list(self):
            print("模拟请求房间列表")
        def set_message_handler(self, msg_type, handler):
            pass
    
    class MessageType:
        ROOM_LIST = "room_list"
        ROOM_INFO = "room_info"
        SUCCESS = "success"
        ERROR = "error"
    
    class NetworkMessage:
        def __init__(self, data):
            self.data = data

# 简单的UI组件
class SimpleButton:
    def __init__(self, x, y, width, height, text, callback, color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.color = color or COLORS["primary"]
        self.font = pygame.font.Font(None, 24)
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, COLORS["border"], self.rect, 2)
        
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class SimpleText:
    def __init__(self, x, y, text, font_size=24, color=None, align="left"):
        self.x = x
        self.y = y
        self.text = text
        self.color = color or COLORS["text"]
        self.font = pygame.font.Font(None, font_size)
        self.align = align
    
    def draw(self, screen):
        text_surface = self.font.render(self.text, True, self.color)
        if self.align == "center":
            text_rect = text_surface.get_rect(center=(self.x, self.y))
            screen.blit(text_surface, text_rect)
        else:
            screen.blit(text_surface, (self.x, self.y))

class MultiplayerWindow:
    """联机游戏窗口"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("大富翁 - 联机模式")
        
        # 网络客户端
        self.network_client = NetworkClient()
        self.setup_network_handlers()
        
        # 界面状态
        self.current_scene = "main_menu"  # main_menu, room_list, room
        self.buttons = []
        self.texts = []
        self.messages = []
        
        # 数据
        self.room_list = []
        self.current_room = None
        self.player_name = ""
        
        # 输入框状态
        self.input_active = False
        self.input_text = ""
        self.input_prompt = ""
        
        # 游戏时钟
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.init_main_menu()
    
    def setup_network_handlers(self):
        """设置网络消息处理器"""
        try:
            self.network_client.set_message_handler(
                MessageType.ROOM_LIST, 
                self.handle_room_list
            )
            self.network_client.set_message_handler(
                MessageType.ROOM_INFO, 
                self.handle_room_info
            )
        except:
            pass  # 如果网络模块不可用，忽略错误
    
    def handle_room_list(self, message):
        """处理房间列表消息"""
        self.room_list = message.data.get("rooms", [])
        if self.current_scene == "room_list":
            self.init_room_list_scene()
    
    def handle_room_info(self, message):
        """处理房间信息消息"""
        room_data = message.data.get("room")
        if room_data:
            self.current_room = room_data
    
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
        self.texts.clear()
        
        # 标题
        title = SimpleText(WINDOW_WIDTH // 2, 100, "联机模式", 36, align="center")
        self.texts.append(title)
        
        # 按钮
        button_width = 200
        button_height = 50
        button_x = WINDOW_WIDTH // 2 - button_width // 2
        
        # 连接服务器按钮
        connect_button = SimpleButton(
            button_x, 200, button_width, button_height,
            "连接服务器", self.show_connect_dialog
        )
        self.buttons.append(connect_button)
        
        # 房间列表按钮
        room_list_button = SimpleButton(
            button_x, 270, button_width, button_height,
            "房间列表", self.show_room_list,
            COLORS["primary"] if self.network_client.is_connected() else COLORS["disabled"]
        )
        self.buttons.append(room_list_button)
        
        # 创建房间按钮
        create_room_button = SimpleButton(
            button_x, 340, button_width, button_height,
            "创建房间", self.show_create_room_dialog,
            COLORS["success"] if self.network_client.is_connected() else COLORS["disabled"]
        )
        self.buttons.append(create_room_button)
        
        # 返回按钮
        back_button = SimpleButton(
            button_x, 410, button_width, button_height,
            "返回主菜单", self.return_to_main
        )
        self.buttons.append(back_button)
        
        # 连接状态显示
        status_text = "已连接" if self.network_client.is_connected() else "未连接"
        status_color = COLORS["success"] if self.network_client.is_connected() else COLORS["error"]
        status = SimpleText(WINDOW_WIDTH // 2, 480, f"服务器状态: {status_text}", 
                           color=status_color, align="center")
        self.texts.append(status)
    
    def init_room_list_scene(self):
        """初始化房间列表场景"""
        self.current_scene = "room_list"
        self.buttons.clear()
        self.texts.clear()
        
        # 标题
        title = SimpleText(WINDOW_WIDTH // 2, 50, "房间列表", 32, align="center")
        self.texts.append(title)
        
        # 刷新按钮
        refresh_button = SimpleButton(
            WINDOW_WIDTH - 120, 20, 100, 30,
            "刷新", self.refresh_room_list
        )
        self.buttons.append(refresh_button)
        
        # 返回按钮
        back_button = SimpleButton(
            20, 20, 100, 30,
            "返回", self.init_main_menu
        )
        self.buttons.append(back_button)
        
        # 房间列表（简化显示）
        if not self.room_list:
            no_rooms_text = SimpleText(WINDOW_WIDTH // 2, 200, "暂无房间", align="center")
            self.texts.append(no_rooms_text)
        else:
            y_offset = 120
            for i, room in enumerate(self.room_list[:5]):  # 最多显示5个房间
                room_name = room.get("name", "未知房间")
                current_players = room.get("current_players", 0)
                max_players = room.get("max_players", 4)
                
                room_text = SimpleText(100, y_offset + i * 40, 
                                     f"{room_name} ({current_players}/{max_players})")
                self.texts.append(room_text)
                
                # 加入按钮
                join_button = SimpleButton(
                    WINDOW_WIDTH - 200, y_offset + i * 40 - 10, 80, 30,
                    "加入", lambda r=room: self.join_room_direct(r)
                )
                self.buttons.append(join_button)
    
    def show_connect_dialog(self):
        """显示连接对话框"""
        self.input_prompt = "请输入玩家名称:"
        self.input_text = ""
        self.input_active = True
    
    def show_create_room_dialog(self):
        """显示创建房间对话框"""
        if not self.network_client.is_connected():
            self.add_message("请先连接服务器", "error")
            return
        
        self.input_prompt = "请输入房间名称:"
        self.input_text = ""
        self.input_active = True
    
    def connect_to_server(self, player_name: str):
        """连接到服务器"""
        self.player_name = player_name
        self.network_client.start_client(player_name)
        self.add_message(f"正在连接服务器，玩家名: {player_name}", "info")
        
        # 延迟更新界面
        pygame.time.set_timer(pygame.USEREVENT + 1, 2000)  # 2秒后更新
    
    def create_room(self, room_name: str):
        """创建房间"""
        self.network_client.create_room(room_name, 4)
        self.add_message(f"正在创建房间: {room_name}", "info")
    
    def join_room_direct(self, room: Dict[str, Any]):
        """直接加入房间"""
        room_id = room.get("room_id")
        if room_id:
            self.network_client.join_room(room_id)
            self.add_message(f"正在加入房间: {room.get('name', '未知房间')}", "info")
    
    def show_room_list(self):
        """显示房间列表"""
        if not self.network_client.is_connected():
            self.add_message("请先连接服务器", "error")
            return
        
        self.network_client.request_room_list()
        self.init_room_list_scene()
    
    def refresh_room_list(self):
        """刷新房间列表"""
        self.network_client.request_room_list()
        self.add_message("正在刷新房间列表...", "info")
    
    def return_to_main(self):
        """返回主菜单"""
        # 断开网络连接
        if self.network_client.is_connected():
            self.network_client.stop_client()
        
        # 返回到主游戏菜单
        self.running = False
    
    def handle_input(self, text: str):
        """处理输入"""
        if self.input_prompt.startswith("请输入玩家名称"):
            self.connect_to_server(text)
        elif self.input_prompt.startswith("请输入房间名称"):
            self.create_room(text)
        
        self.input_active = False
        self.input_text = ""
        self.input_prompt = ""
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            elif event.type == pygame.USEREVENT + 1:
                # 更新连接状态
                self.init_main_menu()
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # 取消定时器
            
            elif event.type == pygame.KEYDOWN:
                if self.input_active:
                    if event.key == pygame.K_RETURN:
                        if self.input_text.strip():
                            self.handle_input(self.input_text.strip())
                    elif event.key == pygame.K_ESCAPE:
                        self.input_active = False
                        self.input_text = ""
                        self.input_prompt = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        if hasattr(event, 'unicode'):
                            self.input_text += event.unicode
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not self.input_active:
                    mouse_pos = pygame.mouse.get_pos()
                    for button in self.buttons:
                        if button.rect.collidepoint(mouse_pos):
                            try:
                                button.callback()
                            except Exception as e:
                                print(f"按钮回调错误: {e}")
                            break
    
    def draw(self):
        """绘制界面"""
        self.screen.fill(COLORS["background"])
        
        # 绘制文本
        for text in self.texts:
            text.draw(self.screen)
        
        # 绘制按钮
        for button in self.buttons:
            button.draw(self.screen)
        
        # 绘制消息
        self.draw_messages()
        
        # 绘制输入框
        if self.input_active:
            self.draw_input_dialog()
        
        pygame.display.flip()
    
    def draw_messages(self):
        """绘制消息"""
        y_offset = WINDOW_HEIGHT - 150
        font = pygame.font.Font(None, 20)
        for i, message in enumerate(self.messages):
            color = COLORS.get(message["type"], COLORS["text"])
            text_surface = font.render(message["text"], True, color)
            self.screen.blit(text_surface, (20, y_offset + i * 25))
    
    def draw_input_dialog(self):
        """绘制输入对话框"""
        # 背景
        dialog_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2 - 50, 400, 100)
        pygame.draw.rect(self.screen, COLORS["panel_bg"], dialog_rect)
        pygame.draw.rect(self.screen, COLORS["border"], dialog_rect, 2)
        
        # 提示文本
        font = pygame.font.Font(None, 24)
        prompt_surface = font.render(self.input_prompt, True, COLORS["text"])
        prompt_rect = prompt_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
        self.screen.blit(prompt_surface, prompt_rect)
        
        # 输入框
        input_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2, 300, 30)
        pygame.draw.rect(self.screen, COLORS["input_bg"], input_rect)
        pygame.draw.rect(self.screen, COLORS["border"], input_rect, 2)
        
        # 输入文本
        input_surface = font.render(self.input_text, True, COLORS["text"])
        self.screen.blit(input_surface, (input_rect.x + 5, input_rect.y + 5))
        
        # 光标
        cursor_x = input_rect.x + 5 + input_surface.get_width()
        if pygame.time.get_ticks() % 1000 < 500:  # 闪烁效果
            pygame.draw.line(self.screen, COLORS["text"], 
                           (cursor_x, input_rect.y + 5), 
                           (cursor_x, input_rect.y + 25), 2)
    
    def run(self):
        """运行联机窗口"""
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)
        
        # 清理
        if self.network_client.is_connected():
            self.network_client.stop_client()
        
        pygame.quit()

if __name__ == "__main__":
    window = MultiplayerWindow()
    window.run()