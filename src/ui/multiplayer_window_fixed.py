"""
联机游戏界面 - 修复版
"""
import pygame
import sys
import os
from typing import List, Dict, Any, Optional

# 基础配置
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

# 尝试加载中文字体
def load_chinese_font(size=24):
    """加载中文字体"""
    try:
        # Windows系统字体路径
        font_paths = [
            "C:/Windows/Fonts/simsun.ttc",      # 宋体
            "C:/Windows/Fonts/msyh.ttc",        # 微软雅黑
            "C:/Windows/Fonts/simhei.ttf",      # 黑体
            "C:/Windows/Fonts/arial.ttf",       # Arial
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                return pygame.font.Font(font_path, size)
        
        # 如果没有找到字体文件，使用系统默认字体
        return pygame.font.Font(None, size)
    except:
        # 备用方案：使用pygame默认字体
        return pygame.font.Font(None, size)


class SimpleButton:
    def __init__(self, x, y, width, height, text, callback, color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.color = color or COLORS["primary"]
        self.font = load_chinese_font(24)
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, COLORS["border"], self.rect, 2)
        
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class SimpleText:
    def __init__(self, x, y, text, font_size=24, color=None, align="left"):
        self.x = x
        self.y = y
        self.text = text
        self.color = color or COLORS["text"]
        self.font = load_chinese_font(font_size)
        self.align = align
    
    def draw(self, screen):
        text_surface = self.font.render(self.text, True, self.color)
        if self.align == "center":
            text_rect = text_surface.get_rect(center=(self.x, self.y))
            screen.blit(text_surface, text_rect)
        else:
            screen.blit(text_surface, (self.x, self.y))


class MultiplayerWindow:
    """联机游戏窗口 - 修复版"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("大富翁 - 联机模式")
        
        # 界面状态
        self.current_scene = "main_menu"
        self.buttons = []
        self.texts = []
        self.messages = []
        
        # 输入框状态
        self.input_active = False
        self.input_text = ""
        self.input_prompt = ""
        
        # 游戏时钟
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 字体
        self.title_font = load_chinese_font(36)
        self.normal_font = load_chinese_font(24)
        self.small_font = load_chinese_font(20)
        
        self.init_main_menu()
    
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
        
        # 启动服务器按钮
        start_server_button = SimpleButton(
            button_x, 200, button_width, button_height,
            "启动服务器", self.start_server, COLORS["success"]
        )
        self.buttons.append(start_server_button)
        
        # 启动客户端按钮
        start_client_button = SimpleButton(
            button_x, 270, button_width, button_height,
            "启动客户端", self.start_client, COLORS["primary"]
        )
        self.buttons.append(start_client_button)
        
        # 测试连接按钮
        test_button = SimpleButton(
            button_x, 340, button_width, button_height,
            "测试连接", self.test_connection, COLORS["warning"]
        )
        self.buttons.append(test_button)
        
        # 返回按钮
        back_button = SimpleButton(
            button_x, 410, button_width, button_height,
            "返回主菜单", self.return_to_main, COLORS["error"]
        )
        self.buttons.append(back_button)
        
        # 说明文本
        instructions = [
            "联机功能说明:",
            "• 启动服务器 - 创建游戏服务器等待玩家连接",
            "• 启动客户端 - 连接到游戏服务器参与游戏",
            "• 测试连接 - 检查本地网络连接状态",
            "",
            "✅ 完整联机功能已启用",
            "📍 服务器地址: localhost:8765",
            "🔧 支持功能: 房间管理、聊天系统、玩家连接",
            "",
            "💡 使用步骤: 先启动服务器，再启动客户端"
        ]
        
        for i, instruction in enumerate(instructions):
            color = COLORS["text"] if instruction.startswith("•") or instruction.startswith("📍") or instruction.startswith("💡") else COLORS["disabled"]
            text = SimpleText(50, 480 + i * 25, instruction, 20, color)
            self.texts.append(text)
    
    def start_server(self):
        """启动服务器"""
        self.add_message("正在启动稳定服务器...", "info")
        try:
            import subprocess
            
            # 检查虚拟环境是否存在
            venv_python = os.path.join(os.getcwd(), "DaFuWeng", "Scripts", "python.exe")
            
            if os.path.exists(venv_python):
                # 使用虚拟环境中的Python启动服务器
                server_path = "quick_server.py"
                if os.path.exists(server_path):
                    if os.name == 'nt':  # Windows
                        subprocess.Popen([
                            venv_python, server_path
                        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
                    else:  # Linux/Mac
                        subprocess.Popen([
                            venv_python, server_path
                        ])
                    
                    self.add_message("✅ 服务器启动成功！(使用虚拟环境)", "success")
                    self.add_message("控制台窗口将保持打开状态", "info")
                else:
                    self.add_message("❌ 找不到 quick_server.py", "error")
            else:
                # 备用：使用系统Python
                self.add_message("⚠️ 虚拟环境不可用，使用系统Python", "warning")
                server_path = "quick_server.py"
                if os.path.exists(server_path):
                    if os.name == 'nt':  # Windows
                        subprocess.Popen([
                            "python", server_path
                        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
                    else:  # Linux/Mac
                        subprocess.Popen([
                            "python", server_path
                        ])
                    self.add_message("✅ 服务器启动成功！(使用系统Python)", "success")
                else:
                    self.add_message("❌ 找不到任何服务器启动脚本", "error")
                
        except Exception as e:
            self.add_message(f"❌ 启动服务器失败: {e}", "error")
    
    def start_client(self):
        """启动客户端"""
        self.add_message("正在启动稳定测试客户端...", "info")
        try:
            import subprocess
            
            # 检查虚拟环境是否存在
            venv_python = os.path.join(os.getcwd(), "DaFuWeng", "Scripts", "python.exe")
            
            if os.path.exists(venv_python):
                # 使用虚拟环境中的Python启动客户端
                client_path = "quick_client.py"
                if os.path.exists(client_path):
                    if os.name == 'nt':  # Windows
                        subprocess.Popen([
                            venv_python, client_path
                        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
                    else:  # Linux/Mac
                        subprocess.Popen([
                            venv_python, client_path
                        ])
                    
                    self.add_message("✅ 客户端启动成功！(使用虚拟环境)", "success")
                    self.add_message("控制台窗口将保持打开状态", "info")
                else:
                    self.add_message("❌ 找不到 quick_client.py", "error")
            else:
                # 备用：使用系统Python
                self.add_message("⚠️ 虚拟环境不可用，使用系统Python", "warning")
                client_path = "quick_client.py"
                if os.path.exists(client_path):
                    if os.name == 'nt':  # Windows
                        subprocess.Popen([
                            "python", client_path
                        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
                    else:  # Linux/Mac
                        subprocess.Popen([
                            "python", client_path
                        ])
                    self.add_message("✅ 客户端启动成功！(使用系统Python)", "success")
                else:
                    self.add_message("❌ 找不到任何客户端测试脚本", "error")
                
        except Exception as e:
            self.add_message(f"❌ 启动客户端失败: {e}", "error")
    
    def test_connection(self):
        """测试连接"""
        self.add_message("测试网络连接...", "info")
        try:
            import socket
            
            # 测试本地连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('localhost', 8765))
            sock.close()
            
            if result == 0:
                self.add_message("✅ 本地服务器可连接", "success")
                self.add_message("服务器在 localhost:8765 运行正常", "info")
            else:
                self.add_message("❌ 本地服务器不可达", "error")
                self.add_message("请先启动服务器", "warning")
                
        except Exception as e:
            self.add_message(f"❌ 网络测试失败: {e}", "error")
    
    def return_to_main(self):
        """返回主菜单"""
        self.running = False
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for button in self.buttons:
                    if button.is_clicked(mouse_pos):
                        try:
                            button.callback()
                        except Exception as e:
                            self.add_message(f"按钮操作出错: {e}", "error")
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
        
        # 绘制底部提示
        hint_text = "按 ESC 键返回主菜单"
        hint_surface = self.small_font.render(hint_text, True, (150, 150, 150))
        hint_rect = hint_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
        self.screen.blit(hint_surface, hint_rect)
        
        pygame.display.flip()
    
    def draw_messages(self):
        """绘制消息"""
        if not self.messages:
            return
        
        message_y = 650
        for message in self.messages[-3:]:  # 只显示最后3条消息
            color_map = {
                "info": COLORS["text"],
                "success": COLORS["success"],
                "error": COLORS["error"],
                "warning": COLORS["warning"]
            }
            color = color_map.get(message["type"], COLORS["text"])
            
            text_surface = self.small_font.render(message["text"], True, color)
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, message_y))
            self.screen.blit(text_surface, text_rect)
            message_y += 25
    
    def run(self):
        """运行联机窗口"""
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)
        
        print("联机界面已关闭")


if __name__ == "__main__":
    window = MultiplayerWindow()
    window.run() 