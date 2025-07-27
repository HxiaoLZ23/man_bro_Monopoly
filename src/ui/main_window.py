"""
主窗口
"""
import pygame
import sys
import os
from typing import List, Optional, Dict, Any, Tuple
from src.models.map import Map
from src.models.player import Player
from src.models.game_state import GameState
from src.systems.player_manager import PlayerManager
from src.systems.dice_system import DiceSystem
from src.systems.event_system import EventManager
from src.systems.bank_system import BankSystem
from src.systems.music_system import MusicSystem
from src.systems.save_system import SaveSystem
from src.ui.constants import WINDOW_WIDTH, WINDOW_HEIGHT, COLORS, LAYOUT, FONTS, ANIMATION, MAP_MARGIN, INFO_PANEL_WIDTH, MESSAGE_PANEL_HEIGHT
from src.ui.components import Button, Panel, Text, Message, Dialog
from src.ui.map_view import MapView
from src.ui.inventory_window import InventoryWindow
from src.ui.dice_window import DiceWindow
from src.ui.target_selection_window import TargetSelectionWindow
from src.ui.dice_shop_window import DiceShopWindow
from src.ui.item_shop_window import ItemShopWindow
from src.ui.bank_window import BankWindow
from src.ui.property_window import PropertyWindow
from src.ui.save_load_window_pygame import SaveLoadWindow
from src.ui.font_manager import font_manager, get_font, render_text
from src.ui.animation_system import AnimationManager, PlayerMoveAnimation, DiceRollAnimation
from src.ui.dice_renderer import DiceRenderer


class MainWindow:
    """主窗口"""
    
    def __init__(self, screen=None):
        pygame.init()
        pygame.mixer.init()
        
        # 如果传入了screen，重用现有的显示窗口；否则创建新窗口
        if screen is not None:
            self.screen = screen
            print("🎮 重用现有pygame窗口...")
        else:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption("man bro 大富翁")
            print("🎮 创建新的pygame窗口...")
        
        # 使用全局字体管理器
        print("🎮 初始化主窗口...")
        self.fonts = {
            "title": get_font("title"),
            "subtitle": get_font("subtitle"), 
            "normal": get_font("normal"),
            "small": get_font("small"),
            "body": get_font("body"),
            "heading": get_font("heading"),
            "subheading": get_font("subheading"),
            "tiny": get_font("tiny"),
        }
        print(f"✅ 字体初始化完成，当前字体: {font_manager.get_font_path()}")
        
        # 游戏状态
        self.game_state = GameState()
        self.player_manager = PlayerManager()
        self.dice_system = DiceSystem()
        self.event_manager = EventManager(20 * 20)  # 默认地图大小
        self.bank_system = BankSystem()
        self.music_system = MusicSystem()  # 初始化音乐系统
        self.save_system = SaveSystem()  # 初始化存档系统
        self.game_map = None
        self.current_scene = "menu"  # "menu", "game_setup", "game", "settings"
        
        # UI组件
        self.map_view = None
        self.messages = []
        self.buttons = []
        self.panels = []
        self.dialogs = []
        self.phase_buttons = []  # 阶段操作按钮
        
        # 子窗口
        self.inventory_window = None
        self.dice_window = None
        self.target_selection_window = None
        self.dice_shop_window = None
        self.item_shop_window = None
        self.bank_window = None
        self.property_window = None
        self.junction_window = None  # 岔路选择窗口
        self.save_load_window = None  # 存档管理窗口
        
        # 游戏设置
        self.selected_map = None
        self.player_count = 3
        self.ai_count = 2
        self.human_count = 1
        
        # 回合阶段控制
        self.phase_auto_advance = True
        self.current_phase_actions = []
        self.phase_timer = 0
        self.phase_delay = 1000  # 阶段切换延迟（毫秒）
        
        # 摄像头跟随模式
        self.camera_follow_mode = True
        
        # 动画系统
        self.animation_manager = AnimationManager()
        self.dice_renderer = DiceRenderer()
        
        # 动画状态
        self.current_move_animation = None
        self.current_dice_animation = None
        self.is_animating = False
        
        # 多人游戏标识（需要在init_menu_scene之前设置）
        self.is_multiplayer = False
        self.multiplayer_data = None
        
        # 只有在非多人游戏模式下才初始化菜单场景
        if screen is None:
            # 初始化场景（只有独立启动时才显示主菜单）
            self.init_menu_scene()
        else:
            # 如果传入了screen，说明是多人游戏模式，直接设置为游戏场景
            self.current_scene = "game"
            self.buttons.clear()
            self.panels.clear()
            self.dialogs.clear()
        
        # 游戏时钟
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.update_map_area()
        
        self.selecting_item_target = False
        self.selected_item_id = None
        self.selected_item_player = None
        self.target_select_tip = ""
        self._hovered_cell = None
        self._hovered_player = None
        self._selected_cell = None
        self._confirm_btn_rect = None
    
    def init_menu_scene(self):
        """初始化菜单场景"""
        # 在多人游戏模式下不允许切换到主菜单
        if hasattr(self, 'is_multiplayer') and self.is_multiplayer:
            print("⚠️ 多人游戏模式下不允许切换到主菜单场景")
            self.add_message("多人游戏模式下不允许切换到主菜单", "warning")
            # 强制保持游戏场景
            if self.current_scene != "game":
                self.current_scene = "game"
            return
            
        self.current_scene = "menu"
        self.buttons.clear()
        self.panels.clear()
        self.dialogs.clear()
        
        # 播放开始界面音乐
        self.music_system.play_index_music()
        
        # 按钮
        button_width = 200
        button_height = 50
        button_x = WINDOW_WIDTH // 2 - button_width // 2
        
        start_button = Button(
            button_x, 280, button_width, button_height, 
            "开始游戏", self.start_game_setup
        )
        self.buttons.append(start_button)
        
        # 加载存档按钮
        load_save_button = Button(
            button_x, 330, button_width, button_height,
            "加载存档", self.open_load_dialog, COLORS["info"]
        )
        self.buttons.append(load_save_button)
        
        # 联机模式按钮
        multiplayer_button = Button(
            button_x, 380, button_width, button_height,
            "联机模式", self.open_multiplayer, COLORS["secondary"]
        )
        self.buttons.append(multiplayer_button)
        
        editor_button = Button(
            button_x, 430, button_width, button_height,
            "地图编辑器", self.open_map_editor
        )
        self.buttons.append(editor_button)
        
        settings_button = Button(
            button_x, 480, button_width, button_height,
            "游戏设置", self.open_settings
        )
        self.buttons.append(settings_button)
        
        exit_button = Button(
            button_x, 530, button_width, button_height,
            "退出游戏", self.quit_game, COLORS["error"]
        )
        self.buttons.append(exit_button)
    
    def init_game_setup_scene(self):
        """初始化游戏设置场景"""
        # 在多人游戏模式下不允许切换到游戏设置场景
        if hasattr(self, 'is_multiplayer') and self.is_multiplayer:
            print("⚠️ 多人游戏模式下不允许切换到游戏设置场景")
            self.add_message("多人游戏模式下不允许切换到游戏设置", "warning")
            # 强制保持游戏场景
            if self.current_scene != "game":
                self.current_scene = "game"
            return
            
        self.current_scene = "game_setup"
        self.buttons.clear()
        self.panels.clear()
        self.dialogs.clear()
        
        # 标题
        title_text = Text(WINDOW_WIDTH // 2, 100, "游戏设置", FONTS["title"], align="center")
        self.panels.append(title_text)
        
        # 地图选择
        map_text = Text(WINDOW_WIDTH // 2, 200, "选择地图", FONTS["subtitle"], align="center")
        self.panels.append(map_text)
        
        # 地图选择按钮
        button_width = 150
        button_height = 40
        button_x = WINDOW_WIDTH // 2 - button_width // 2
        
        # 默认地图按钮（根据选择状态改变颜色）
        default_map_color = COLORS["success"] if self.selected_map == "default" else COLORS["primary"]
        default_map_button = Button(
            button_x, 250, button_width, button_height,
            "默认地图", lambda: self.select_map("default"), default_map_color
        )
        self.buttons.append(default_map_button)
        
        # 加载地图按钮
        load_map_color = COLORS["success"] if self.selected_map == "custom" else COLORS["primary"]
        load_map_button = Button(
            button_x, 300, button_width, button_height,
            "加载地图", self.load_map_dialog, load_map_color
        )
        self.buttons.append(load_map_button)
        
        # 显示当前选择的地图
        if self.selected_map:
            if self.selected_map == "default":
                map_status_text = "已选择: 默认地图 (20x20)"
            else:
                # 自定义地图
                if hasattr(self, 'custom_map_path') and self.custom_map_path:
                    import os
                    file_name = os.path.basename(self.custom_map_path)
                    map_status_text = f"已选择: 自定义地图 - {file_name}"
                else:
                    map_status_text = "已选择: 自定义地图"
            
            map_status = Text(WINDOW_WIDTH // 2, 350, map_status_text, FONTS["normal"], align="center", color=COLORS["success"])
            self.panels.append(map_status)
            
            # 显示地图信息
            if self.game_map:
                map_info_text = f"地图尺寸: {self.game_map.width}x{self.game_map.height}"
                map_info = Text(WINDOW_WIDTH // 2, 375, map_info_text, FONTS["small"], align="center", color=COLORS["text_secondary"])
                self.panels.append(map_info)
        
        # 玩家数量设置
        player_text = Text(WINDOW_WIDTH // 2, 410, "玩家设置", FONTS["subtitle"], align="center")
        self.panels.append(player_text)
        
        # 人类玩家数量
        human_text = Text(WINDOW_WIDTH // 2 - 100, 460, f"人类玩家: {self.human_count}", FONTS["normal"], align="center")
        self.panels.append(human_text)
        
        human_plus = Button(
            WINDOW_WIDTH // 2 + 50, 450, 30, 30,
            "+", lambda: self.change_player_count("human", 1)
        )
        self.buttons.append(human_plus)
        
        human_minus = Button(
            WINDOW_WIDTH // 2 + 90, 450, 30, 30,
            "-", lambda: self.change_player_count("human", -1)
        )
        self.buttons.append(human_minus)
        
        # AI玩家数量
        ai_text = Text(WINDOW_WIDTH // 2 - 100, 510, f"AI玩家: {self.ai_count}", FONTS["normal"], align="center")
        self.panels.append(ai_text)
        
        ai_plus = Button(
            WINDOW_WIDTH // 2 + 50, 500, 30, 30,
            "+", lambda: self.change_player_count("ai", 1)
        )
        self.buttons.append(ai_plus)
        
        ai_minus = Button(
            WINDOW_WIDTH // 2 + 90, 500, 30, 30,
            "-", lambda: self.change_player_count("ai", -1)
        )
        self.buttons.append(ai_minus)
        
        # 开始游戏按钮
        start_button = Button(
            WINDOW_WIDTH // 2 - 100, 580, 200, 50,
            "开始游戏", self.start_game, COLORS["success"]
        )
        self.buttons.append(start_button)
        
        # 返回按钮
        back_button = Button(
            WINDOW_WIDTH // 2 - 100, 650, 200, 50,
            "返回菜单", self.return_to_menu
        )
        self.buttons.append(back_button)
    
    def init_game_scene(self):
        """初始化游戏场景"""
        self.current_scene = "game"
        self.buttons.clear()
        self.panels.clear()
        self.dialogs.clear()
        
        # 播放游戏界面音乐
        self.music_system.play_main_music()
        
        # 创建地图视图
        map_x = LAYOUT["margin"]
        map_y = LAYOUT["margin"]
        self.map_view = MapView(self.game_map, map_x, map_y)
        
        # 右侧信息面板
        info_panel = Panel(
            WINDOW_WIDTH - LAYOUT["panel_width"] - LAYOUT["margin"],
            LAYOUT["margin"],
            LAYOUT["panel_width"],
            WINDOW_HEIGHT - 2 * LAYOUT["margin"],
            "游戏信息"
        )
        self.panels.append(info_panel)
        
        # 底部消息区域
        message_panel = Panel(
            LAYOUT["margin"],
            WINDOW_HEIGHT - 150 - LAYOUT["margin"],
            WINDOW_WIDTH - 2 * LAYOUT["margin"] - LAYOUT["panel_width"],
            150,
            "游戏消息"
        )
        self.panels.append(message_panel)
        
        # 摄像头控制按钮
        camera_button = Button(
            WINDOW_WIDTH - LAYOUT["panel_width"] - LAYOUT["margin"] - 120,
            LAYOUT["margin"] + 10,
            100,
            30,
            "跟随模式" if self.camera_follow_mode else "手动模式",
            self.toggle_camera_mode,
            COLORS["primary"] if self.camera_follow_mode else COLORS["secondary"]
        )
        self.buttons.append(camera_button)
        
        # 存档相关按钮
        save_button = Button(
            WINDOW_WIDTH - LAYOUT["panel_width"] - LAYOUT["margin"] - 120,
            LAYOUT["margin"] + 50,
            100,
            30,
            "保存游戏",
            self.open_save_dialog,
            COLORS["success"]
        )
        self.buttons.append(save_button)
        
        load_button = Button(
            WINDOW_WIDTH - LAYOUT["panel_width"] - LAYOUT["margin"] - 120,
            LAYOUT["margin"] + 90,
            100,
            30,
            "加载游戏",
            self.open_load_dialog,
            COLORS["info"]
        )
        self.buttons.append(load_button)
        
        # 快速保存按钮
        quick_save_button = Button(
            WINDOW_WIDTH - LAYOUT["panel_width"] - LAYOUT["margin"] - 120,
            LAYOUT["margin"] + 130,
            100,
            30,
            "快速保存",
            self.quick_save,
            COLORS["warning"]
        )
        self.buttons.append(quick_save_button)
        
        # 阶段操作按钮（只在需要时显示）
        self.phase_buttons = []
    
    def start_game_setup(self):
        """开始游戏设置"""
        # 在多人游戏模式下不允许切换到游戏设置
        if hasattr(self, 'is_multiplayer') and self.is_multiplayer:
            print("⚠️ 多人游戏模式下不允许切换到游戏设置")
            self.add_message("多人游戏模式下不允许切换到游戏设置", "warning")
            return
            
        self.init_game_setup_scene()
    
    def select_map(self, map_type: str):
        """选择地图"""
        if map_type == "default":
            self.game_map = Map(20, 20)
            self.selected_map = "default"
            self.add_message("已选择默认地图", "success")
            # 重新初始化设置场景以更新显示
            self.init_game_setup_scene()
        else:
            # 这里可以添加其他地图选择逻辑
            self.add_message("地图选择功能开发中...", "info")
    
    def load_map_dialog(self):
        """加载地图对话框"""
        try:
            # 使用tkinter文件对话框选择地图文件
            import tkinter as tk
            from tkinter import filedialog, messagebox
            
            # 创建隐藏的tkinter根窗口
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            
            # 设置文件对话框
            file_path = filedialog.askopenfilename(
                title="选择地图文件",
                filetypes=[
                    ("JSON地图文件", "*.json"),
                    ("Excel地图文件", "*.xlsx"),
                    ("所有文件", "*.*")
                ],
                initialdir="."  # 从当前目录开始
            )
            
            if file_path:
                # 根据文件扩展名选择加载方法
                from src.systems.map_data_manager import MapDataManager
                map_manager = MapDataManager()
                
                try:
                    # 根据文件扩展名确定格式
                    if file_path.endswith('.json'):
                        format_type = 'json'
                    elif file_path.endswith('.xlsx'):
                        format_type = 'xlsx'
                    else:
                        self.add_message("不支持的地图文件格式", "error")
                        return
                    
                    # 加载地图
                    self.game_map = map_manager.load_map(format_type, file_path)
                    
                    if self.game_map:
                        # 设置地图状态
                        self.selected_map = "custom"
                        self.custom_map_path = file_path  # 保存文件路径
                        
                        # 获取文件名用于显示
                        import os
                        file_name = os.path.basename(file_path)
                        self.add_message(f"已加载地图: {file_name}", "success")
                        
                        # 重新初始化设置场景以更新显示
                        self.init_game_setup_scene()
                    else:
                        self.add_message("地图文件加载失败", "error")
                    
                except Exception as e:
                    self.add_message(f"地图文件加载失败: {str(e)}", "error")
            else:
                # 用户取消了文件选择
                self.add_message("地图加载已取消", "info")
                
        except ImportError:
            # 如果没有tkinter，使用简单的命令行方式
            self.add_message("正在使用简单地图加载模式...", "info")
            self.load_map_simple()
        except Exception as e:
            self.add_message(f"地图加载失败: {str(e)}", "error")
    
    def load_map_simple(self):
        """简单的地图加载方式（备用方案）"""
        try:
            # 检查常见的地图文件
            import os
            map_files = [
                "demo_map.json",
                "map.json", 
                "game_map.json",
                "custom_map.json"
            ]
            
            loaded_map = None
            for map_file in map_files:
                if os.path.exists(map_file):
                    from src.systems.map_data_manager import MapDataManager
                    map_manager = MapDataManager()
                    loaded_map = map_manager.load_map('json', map_file)
                    if loaded_map:
                        self.add_message(f"已加载地图: {map_file}", "success")
                        break
            
            if not loaded_map:
                # 如果没有找到地图文件，创建一个示例地图
                loaded_map = self.create_sample_map()
                self.add_message("已创建示例地图", "success")
            
            self.game_map = loaded_map
            self.selected_map = "custom"  # 确保设置为自定义地图
            self.init_game_setup_scene()
            
        except Exception as e:
            self.add_message(f"简单地图加载失败: {str(e)}", "error")
    
    def create_sample_map(self):
        """创建一个示例地图"""
        from src.models.map import Map
        from src.models.property import Property
        
        # 创建一个20x20的示例地图（Map类会自动设置路径和特殊格子）
        sample_map = Map(20, 20)
        
        # 添加一些房产到路径上
        property_positions = [5, 15, 25, 35, 45, 55, 65, 75]  # 路径索引
        for i, path_index in enumerate(property_positions):
            if path_index < sample_map.path_length:
                cell = sample_map.get_cell_by_path_index(path_index)
                if cell and cell.cell_type == "empty":
                    cell.cell_type = "property"
                    # Property构造函数: (position, owner_id=None, level=0)
                    property_obj = Property(path_index, None, 1)  # 创建1级房产
                    cell.set_property(property_obj)
        
        return sample_map
    
    def change_player_count(self, player_type: str, delta: int):
        """改变玩家数量"""
        if player_type == "human":
            new_count = self.human_count + delta
            if 1 <= new_count <= 6:
                self.human_count = new_count
                self.player_count = self.human_count + self.ai_count
        elif player_type == "ai":
            new_count = self.ai_count + delta
            if 0 <= new_count <= 5:
                self.ai_count = new_count
                self.player_count = self.human_count + self.ai_count
        
        # 重新初始化设置场景以更新显示
        self.init_game_setup_scene()
    
    def start_game(self):
        """开始游戏"""
        if not self.game_map:
            self.add_message("请先选择地图", "error")
            return
        
        if self.player_count < 3 or self.player_count > 6:
            self.add_message("玩家数量必须在3-6人之间", "error")
            return
        
        # 创建玩家
        players = []
        player_id = 1
        
        # 创建人类玩家
        for i in range(self.human_count):
            player = Player(int(player_id), f"玩家{i+1}", is_ai=False)
            players.append(player)
            player_id += 1
        
        # 创建AI玩家
        for i in range(self.ai_count):
            player = Player(int(player_id), f"AI玩家{i+1}", is_ai=True)
            players.append(player)
            player_id += 1
        
        # 初始化游戏状态
        if self.game_state.initialize_game(players, self.game_map):
            # 设置PlayerManager
            self.player_manager.set_players(players)
            self.player_manager.set_game_map(self.game_map)
            
            # 确保清除任何残留的主菜单元素
            print("🧹 清理界面元素...")
            self.buttons.clear()
            self.panels.clear()
            self.dialogs.clear()
            self.phase_buttons.clear()
            
            # 初始化游戏界面
            print("🖼️ 初始化游戏界面...")
            self.init_game_scene()
            self.add_message("多人游戏开始！", "success")
            
            # 开始第一个回合
            print("🎯 开始游戏回合...")
            self.start_turn_phase()
            
            return True
        else:
            self.add_message("游戏初始化失败", "error")
            return False
    
    def start_turn_phase(self):
        """开始回合阶段"""
        current_player = self.game_state.get_current_player()
        if not current_player:
            return
        
        # 摄像头跟随当前玩家
        if self.map_view and self.camera_follow_mode:
            self.map_view.follow_player(current_player, True)
        
        # 重置阶段操作
        self.current_phase_actions = []
        self.phase_timer = 0
        
        # 根据当前阶段执行相应操作
        if self.game_state.current_phase == "preparation":
            self.start_preparation_phase()
        elif self.game_state.current_phase == "action":
            self.start_action_phase()
        elif self.game_state.current_phase == "settlement":
            self.start_settlement_phase()
        elif self.game_state.current_phase == "end":
            self.start_end_phase()
    
    def start_preparation_phase(self):
        """开始准备阶段"""
        current_player = self.game_state.get_current_player()
        self.add_message(f"{current_player.name}的准备阶段", "info")
        
        if current_player.is_ai:
            # AI自动决策
            self.ai_preparation_decision(current_player)
        else:
            # 人类玩家选择
            self.show_preparation_choices()
    
    def show_preparation_choices(self):
        """显示准备阶段选择"""
        self.phase_buttons.clear()
        
        # 更换骰子按钮
        dice_button = Button(
            WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT - 200, 120, 40,
            "更换骰子", self.change_dice
        )
        self.phase_buttons.append(dice_button)
        
        # 使用道具按钮
        item_button = Button(
            WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT - 200, 120, 40,
            "使用道具", self.use_item
        )
        self.phase_buttons.append(item_button)
        
        # 跳过按钮
        skip_button = Button(
            WINDOW_WIDTH // 2 + 80, WINDOW_HEIGHT - 200, 120, 40,
            "跳过", self.skip_preparation, COLORS["warning"]
        )
        self.phase_buttons.append(skip_button)
    
    def show_action_choices(self):
        """显示行动阶段选择"""
        self.phase_buttons.clear()
        
        # 投骰子按钮
        roll_button = Button(
            WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT - 200, 120, 40,
            "投骰子", self.roll_dice, COLORS["primary"]
        )
        self.phase_buttons.append(roll_button)
    
    def start_action_phase(self):
        """开始行动阶段"""
        current_player = self.game_state.get_current_player()
        self.add_message(f"{current_player.name}的行动阶段", "info")
        
        if current_player.is_ai:
            # AI自动投骰子
            self.ai_action_decision(current_player)
        else:
            # 显示投骰子按钮
            self.show_action_choices()
    
    def start_settlement_phase(self):
        """开始结算阶段"""
        current_player = self.game_state.get_current_player()
        self.add_message(f"{current_player.name}的结算阶段", "info")
        
        # 自动执行结算逻辑
        self.execute_settlement()
        
        # 检查是否有UI窗口打开，如果有则不自动推进
        has_open_window = False
        
        # 检查各种可能的窗口
        if hasattr(self, 'bank_window') and self.bank_window and getattr(self.bank_window, 'visible', False):
            has_open_window = True
            print("🔧 银行窗口已打开，暂停自动推进")
        elif hasattr(self, 'item_shop_window') and self.item_shop_window and getattr(self.item_shop_window, 'visible', False):
            has_open_window = True
            print("🔧 道具商店窗口已打开，暂停自动推进")
        elif hasattr(self, 'dice_shop_window') and self.dice_shop_window and getattr(self.dice_shop_window, 'visible', False):
            has_open_window = True
            print("🔧 骰子商店窗口已打开，暂停自动推进")
        elif hasattr(self, 'property_window') and self.property_window and getattr(self.property_window, 'visible', False):
            has_open_window = True
            print("🔧 房产窗口已打开，暂停自动推进")
        
        # 只有在没有窗口打开时才设置自动推进
        if not has_open_window:
            # 设置延迟自动推进到结束阶段，而不是立即推进
            self.phase_auto_advance = True
            self.phase_timer = 1500  # 1.5秒延迟
            print("🔧 设置自动推进定时器")
        else:
            # 有窗口打开，不自动推进，等待窗口关闭
            self.phase_auto_advance = False
            self.phase_timer = 0
            print("🔧 因窗口打开而暂停自动推进")
    
    def start_end_phase(self):
        """开始结束阶段"""
        current_player = self.game_state.get_current_player()
        self.add_message(f"{current_player.name}的结束阶段", "info")
        
        # 设置延迟自动推进到下一玩家，而不是立即推进
        self.phase_auto_advance = True
        self.phase_timer = 1000  # 1秒延迟
    
    def change_dice(self):
        """更换骰子"""
        current_player = self.game_state.get_current_player()
        if not current_player:
            return
        
        # 确保玩家有个人骰子系统
        if not hasattr(current_player, 'dice_system'):
            from src.systems.dice_system import DiceSystem
            current_player.dice_system = DiceSystem()
        
        # 打开骰子包界面，使用玩家个人的骰子系统
        self.dice_window = DiceWindow(
            current_player, 
            current_player.dice_system,  # 使用玩家个人的骰子系统
            on_dice_select=self.on_dice_selected,
            on_close=self.close_dice_window
        )
        
        print(f"🎲 {current_player.name}打开骰子选择界面，可用骰子: {current_player.dice_system.get_available_dice_types()}")
        
        # 居中显示
        self.dice_window.x = (WINDOW_WIDTH - self.dice_window.width) // 2
        self.dice_window.y = (WINDOW_HEIGHT - self.dice_window.height) // 2
    
    def close_dice_window(self):
        """关闭骰子窗口"""
        if self.dice_window:
            self.dice_window.is_open = False
            self.dice_window = None
        # 如果是在准备阶段关闭窗口，需要推进游戏
        if self.game_state.current_phase == "preparation":
            try:
                self.advance_phase()
            except Exception as e:
                print(f"🔧 关闭骰子窗口时推进阶段失败: {e}")
                # 设置自动推进作为备用方案
                self.phase_auto_advance = True
                self.phase_timer = 500  # 0.5秒后自动推进
    
    def on_dice_selected(self, dice_type: str):
        """骰子选择回调"""
        current_player = self.game_state.get_current_player()
        if not current_player:
            return
        
        # 确保玩家有个人骰子系统
        if not hasattr(current_player, 'dice_system'):
            from src.systems.dice_system import DiceSystem
            current_player.dice_system = DiceSystem()
        
        # 切换玩家个人的骰子
        success = current_player.dice_system.set_current_dice(dice_type)
        if success:
            current_player.dice = dice_type
            self.add_message(f"{current_player.name}切换骰子为{dice_type}", "info")
            print(f"🎲 {current_player.name}切换个人骰子为{dice_type}")
        else:
            self.add_message(f"切换骰子失败", "error")
        
        # 关闭骰子包界面
        self.dice_window = None
        
        # 推进到下一个阶段
        self.advance_phase()
    
    def use_item(self):
        """使用道具按钮点击事件"""
        if not self.inventory_window:
            from src.ui.inventory_window import InventoryWindow
            current_player = self.game_state.get_current_player()
            if current_player:
                self.inventory_window = InventoryWindow(
                    current_player, 
                    self.on_item_selected,
                    self.close_inventory_window  # 添加关闭回调
                )
                # 设置窗口位置（居中显示）
                screen_width, screen_height = self.screen.get_size()
                self.inventory_window.x = (screen_width - self.inventory_window.width) // 2
                self.inventory_window.y = (screen_height - self.inventory_window.height) // 2
    
    def on_item_selected(self, item_id: int):
        """道具选择回调"""
        if item_id == 1:  # 路障道具
            self.selected_item_id = item_id
            self.selecting_item_target = True
            self.target_select_tip = "请选择放置路障的位置（右键或ESC取消）"
            self.add_message("请选择放置路障的位置", "info")
        elif item_id == 2:  # 传送道具
            self.selected_item_id = item_id
            self.selecting_item_target = True
            self.target_select_tip = "请选择要传送的玩家（右键或ESC取消）"
            self.add_message("请选择要传送的玩家", "info")
        elif item_id == 3:  # 金钱道具
            # 金钱道具直接使用，不需要选择目标
            current_player = self.game_state.get_current_player()
            if current_player:
                money_gained = 500  # 假设获得500金钱
                current_player.money += money_gained
                self.add_message(f"{current_player.name}获得了{money_gained}金钱！", "success")
                # 从背包中移除道具
                if item_id in current_player.inventory:
                    current_player.inventory[item_id] -= 1
                    if current_player.inventory[item_id] <= 0:
                        del current_player.inventory[item_id]
        
        # 关闭道具窗口
        self.close_inventory_window()
    
    def skip_preparation(self):
        """跳过准备阶段"""
        print("skip_preparation方法被调用")
        print("准备调用advance_phase")
        self.advance_phase()
        print("advance_phase调用完成")
    
    def roll_dice(self):
        """投掷骰子"""
        try:
            current_player = self.game_state.get_current_player()
            if not current_player:
                print("❌ 没有当前玩家")
                return
            
            # 如果正在播放动画，不允许投掷
            if self.is_animating:
                print("⚠️ 正在播放动画，无法投掷骰子")
                return
            
            print(f"🎲 {current_player.name} 开始投掷骰子...")
            
            # 设置动画状态
            self.is_animating = True
            
            # 获取当前玩家的骰子系统
            player_dice_system = None
            if hasattr(current_player, 'dice_system'):
                player_dice_system = current_player.dice_system
            else:
                # 如果玩家没有个人骰子系统，使用全局系统
                player_dice_system = self.dice_system
            
            # 获取当前骰子信息
            current_dice_type = player_dice_system.get_current_dice_type()
            dice_config = player_dice_system.dice_set.dice_config
            dice_count = dice_config["count"]
            dice_sides = dice_config["sides"]
            
            print(f"🎲 {current_player.name}的骰子类型: {current_dice_type}, 数量: {dice_count}, 面数: {dice_sides}")
            
            # 获取骰子结果（包含每个骰子的结果）
            dice_results = player_dice_system.roll_current_dice()
            dice_sum = sum(dice_results)
            
            print(f"🎲 骰子结果: {dice_results}, 总和: {dice_sum}")
            
            # 创建骰子投掷动画
            dice_center_x = 450  # 固定中心位置
            dice_center_y = 350
            
            def on_dice_animation_complete():
                """骰子动画完成后的回调"""
                try:
                    print("🎬 骰子动画完成")
                    self.is_animating = False
                    
                    # 添加消息
                    if dice_count == 1:
                        self.add_message(f"{current_player.name} 投掷{current_dice_type}骰子: {dice_sum}", "info")
                    else:
                        results_str = " + ".join(map(str, dice_results))
                        self.add_message(f"{current_player.name} 投掷{current_dice_type}骰子: {results_str} = {dice_sum}", "info")
                    
                    # 创建爆炸特效
                    try:
                        self.animation_manager.create_particle_effect(
                            dice_center_x, dice_center_y, "explosion", 25, 1.5
                        )
                    except Exception as e:
                        print(f"⚠️ 创建粒子特效失败: {e}")
                    
                    # 延迟移动玩家
                    def delayed_move():
                        try:
                            print(f"🚶 开始移动玩家 {current_player.name}")
                            
                            # 检查玩家对象是否还有效
                            if not hasattr(current_player, 'position'):
                                print("❌ 玩家对象无效")
                                self.is_animating = False
                                return
                            
                            # 检查游戏地图是否还有效
                            if not self.game_map:
                                print("❌ 游戏地图无效")
                                self.is_animating = False
                                return
                            
                            self.move_player_with_animation(current_player, dice_sum)
                            
                            # 清除阶段按钮（防止重复点击）
                            self.phase_buttons.clear()
                            
                            # 直接进入结算阶段
                            print("⚖️ 进入结算阶段")
                            self.game_state.set_current_phase("settlement")
                            self.start_settlement_phase()
                            
                        except Exception as e:
                            print(f"❌ 延迟移动异常: {e}")
                            import traceback
                            traceback.print_exc()
                            
                            # 发生错误时重置动画状态
                            self.is_animating = False
                            self.add_message(f"移动玩家时发生错误: {e}", "error")
                            
                            # 尝试继续游戏流程
                            try:
                                self.advance_phase()
                            except Exception as e2:
                                print(f"❌ 推进阶段也失败: {e2}")
                                # 强制重置到准备阶段
                                try:
                                    self.game_state.set_current_phase("preparation")
                                    self.start_preparation_phase()
                                except:
                                    pass
                    
                    # 延迟500毫秒后移动玩家
                    pygame.time.set_timer(pygame.USEREVENT + 1, 500)
                    self._delayed_move_callback = delayed_move
                    
                except Exception as e:
                    print(f"❌ 骰子动画完成回调异常: {e}")
                    import traceback
                    traceback.print_exc()
                    
                    # 发生错误时重置状态
                    self.is_animating = False
                    self.add_message(f"动画处理时发生错误: {e}", "error")
                    
                    # 尝试继续游戏流程
                    try:
                        self.advance_phase()
                    except:
                        # 强制重置到准备阶段
                        try:
                            self.game_state.set_current_phase("preparation")
                            self.start_preparation_phase()
                        except:
                            pass
            
            # 创建骰子动画
            try:
                print("🎬 创建骰子动画")
                self.current_dice_animation = self.animation_manager.create_dice_roll_animation(
                    dice_count=dice_count,
                    duration=2.0,
                    dice_sides=dice_sides,
                    dice_type=current_dice_type,
                    final_values=dice_results,
                    on_complete=on_dice_animation_complete
                )
                print("✅ 骰子动画创建成功")
                
            except Exception as e:
                print(f"❌ 创建骰子动画失败: {e}")
                import traceback
                traceback.print_exc()
                
                # 如果动画创建失败，直接执行移动
                self.is_animating = False
                self.add_message(f"动画创建失败，直接移动: {e}", "warning")
                
                # 直接移动玩家
                try:
                    self.move_player_with_animation(current_player, dice_sum)
                    self.game_state.set_current_phase("settlement")
                    self.start_settlement_phase()
                except Exception as e2:
                    print(f"❌ 直接移动也失败: {e2}")
                    self.add_message(f"移动玩家失败: {e2}", "error")
                    # 强制推进阶段
                    try:
                        self.advance_phase()
                    except:
                        # 强制重置到准备阶段
                        try:
                            self.game_state.set_current_phase("preparation")
                            self.start_preparation_phase()
                        except:
                            pass
                    
        except Exception as e:
            print(f"❌ roll_dice方法异常: {e}")
            import traceback
            traceback.print_exc()
            
            # 发生错误时重置状态
            self.is_animating = False
            self.add_message(f"投掷骰子时发生错误: {e}", "error")
            
            # 尝试继续游戏流程
            try:
                self.advance_phase()
            except Exception as e2:
                print(f"❌ 推进阶段也失败: {e2}")
                # 如果连推进阶段都失败，可能需要重置游戏状态
                self.add_message("游戏出现严重错误，请重新开始", "error")
                # 强制重置到准备阶段
                try:
                    self.game_state.set_current_phase("preparation")
                    self.start_preparation_phase()
                except:
                    pass
    
    def move_player_with_animation(self, player: Player, steps: int):
        """带动画的移动玩家"""
        if steps <= 0:
            return
        
        # 检查玩家是否在监狱
        if hasattr(player, 'in_jail') and player.in_jail:
            # 在监狱中，尝试逃脱
            if steps >= 6:
                # 投掷6或以上，逃脱监狱
                player.in_jail = False
                player.jail_turns = 0
                # 恢复到进监狱前的位置
                if hasattr(player, 'pre_jail_position'):
                    player.position = player.pre_jail_position
                    del player.pre_jail_position
                self.add_message(f"{player.name}投掷{steps}点，成功逃脱监狱！", "success")
                # 逃脱后立即行动一回合
                remaining_steps = steps - 6
                if remaining_steps > 0:
                    self._move_player_with_animation_normal(player, remaining_steps)
                return
            else:
                # 逃脱失败
                if not hasattr(player, 'jail_turns'):
                    player.jail_turns = 0
                player.jail_turns += 1
                if player.jail_turns >= 3:
                    # 坐牢3轮后强制释放
                    player.in_jail = False
                    player.jail_turns = 0
                    if hasattr(player, 'pre_jail_position'):
                        player.position = player.pre_jail_position
                        del player.pre_jail_position
                    self.add_message(f"{player.name}刑满释放！", "info")
                    return
                else:
                    self.add_message(f"{player.name}投掷{steps}点，逃脱失败，还需坐牢{3 - player.jail_turns}轮", "warning")
                    return
        
        # 正常移动
        self._move_player_with_animation_normal(player, steps)
    
    def _move_player_with_animation_normal(self, player: Player, steps: int):
        """带动画的正常移动玩家（非监狱状态）"""
        # 获取移动路径
        old_position = player.position
        
        # 使用地图的移动方法
        final_position, path_taken = self.game_map.move_along_path(old_position, steps)
        
        # 更新玩家位置
        player.position = final_position
        
        # 处理路径上的事件
        for pos in path_taken[1:]:  # 跳过起始位置
            current_cell = self.game_map.get_cell_by_path_index(pos)
            if current_cell:
                # 检查路障
                if hasattr(current_cell, 'roadblock') and current_cell.roadblock:
                    # 玩家被路障阻挡，停在路障位置
                    current_cell.roadblock = False  # 移除路障
                    player.position = pos  # 更新玩家位置到路障位置
                    self.add_message(f"{player.name}被路障阻挡，停在位置{pos}，路障消失", "warning")
                    break
                
                # 检查地上的钱
                if hasattr(current_cell, 'money_on_ground') and current_cell.money_on_ground > 0:
                    money_collected = current_cell.collect_money_on_ground()
                    player.money += money_collected
                    self.add_message(f"{player.name}捡到了{money_collected}金钱", "success")
        
        actual_steps = len(path_taken) - 1
        self.add_message(f"{player.name}移动{actual_steps}步到位置 {player.position}", "info")
        
        # 如果是当前玩家且摄像头跟随模式开启，则跟随玩家
        if self.map_view and self.camera_follow_mode and player == self.game_state.get_current_player():
            self.map_view.follow_player(player, True)
    
    def _move_player_with_junction_choice(self, player: Player, steps: int):
        """带岔路选择的移动 - 分段移动逻辑"""
        # 查找第一个岔路点的距离
        steps_to_junction = self._find_first_junction_in_path(player.position, steps)
        
        if steps_to_junction is None:
            # 路径中没有岔路点，直接移动
            self._move_player_simple(player, steps)
            return
        
        # 先移动到岔路点
        self.add_message(f"{player.name}前进{steps_to_junction}步到达岔路口", "info")
        
        # 移动到岔路点
        old_position = player.position
        final_position, path_taken = self.game_map.move_along_path(old_position, steps_to_junction)
        
        # 处理路径上的事件（除了最后的岔路点）
        for pos in path_taken[1:-1]:  # 跳过起始位置和最终位置（岔路点）
            current_cell = self.game_map.get_cell_by_path_index(pos)
            if current_cell:
                # 检查路障
                if hasattr(current_cell, 'roadblock') and current_cell.roadblock:
                    current_cell.roadblock = False
                    self.add_message(f"{player.name}被路障阻挡，停在位置{pos}，路障消失", "warning")
                    player.position = pos
                    return  # 被路障阻挡，停止移动
                
                # 检查地上的钱
                if hasattr(current_cell, 'money_on_ground') and current_cell.money_on_ground > 0:
                    money_collected = current_cell.collect_money_on_ground()
                    player.money += money_collected
                    self.add_message(f"{player.name}捡到了{money_collected}金钱", "success")
        
        # 更新玩家位置到岔路点
        player.position = final_position
        
        # 设置待处理的移动信息
        remaining_steps = steps - steps_to_junction
        self.pending_movement = {
            'player': player,
            'total_steps': steps,
            'steps_to_junction': steps_to_junction,
            'remaining_steps': remaining_steps,
            'current_position': final_position,
            'path_taken': path_taken
        }
        
        # 显示岔路选择界面
        available_directions = self.game_map.get_available_directions(final_position)
        if len(available_directions) > 1:
            self._show_junction_selection(final_position, available_directions)
        else:
            # 只有一个方向，直接继续移动
            self._continue_after_junction_choice(available_directions[0])
    
    def _on_direction_selected(self, direction: int):
        """方向选择回调"""
        if hasattr(self, 'junction_window'):
            self.junction_window = None
        
        # 继续移动剩余步数
        self._continue_after_junction_choice(direction)
    
    def _continue_after_junction_choice(self, chosen_direction: int):
        """选择方向后继续移动剩余步数"""
        if not hasattr(self, 'pending_movement') or not self.pending_movement:
            return
        
        movement = self.pending_movement
        player = movement['player']
        remaining_steps = movement['remaining_steps']
        
        if remaining_steps <= 0:
            # 没有剩余步数，移动完成
            self.add_message(f"{player.name}在岔路口停下", "info")
            self.pending_movement = None
            return
        
        # 从岔路点继续移动剩余步数
        self.add_message(f"{player.name}选择方向，继续移动{remaining_steps}步", "info")
        
        # 从选择的方向开始移动
        old_position = player.position
        
        # 检查剩余路径中是否还有岔路点
        if self._has_junctions_in_path(chosen_direction, remaining_steps):
            # 还有岔路点，递归处理
            player.position = chosen_direction  # 先移动到选择的方向
            self._move_player_with_junction_choice(player, remaining_steps - 1)
        else:
            # 没有更多岔路点，直接移动剩余步数
            # 手动构建路径：从岔路点到选择的方向，然后继续移动
            if remaining_steps == 1:
                # 只移动一步到选择的方向
                player.position = chosen_direction
                final_path = [old_position, chosen_direction]
            else:
                # 移动多步：先到选择的方向，然后继续
                final_position, path_taken = self.game_map.move_along_path(chosen_direction, remaining_steps - 1)
                player.position = final_position
                final_path = [old_position] + path_taken
            
            # 处理路径上的事件
            for pos in final_path[1:]:  # 跳过起始位置（岔路点）
                current_cell = self.game_map.get_cell_by_path_index(pos)
                if current_cell:
                    # 检查路障
                    if hasattr(current_cell, 'roadblock') and current_cell.roadblock:
                        current_cell.roadblock = False
                        self.add_message(f"{player.name}被路障阻挡，停在位置{pos}，路障消失", "warning")
                        player.position = pos
                        break
                    
                    # 检查地上的钱
                    if hasattr(current_cell, 'money_on_ground') and current_cell.money_on_ground > 0:
                        money_collected = current_cell.collect_money_on_ground()
                        player.money += money_collected
                        self.add_message(f"{player.name}捡到了{money_collected}金钱", "success")
        
        # 清除移动状态
        self.pending_movement = None
        
        # 如果是当前玩家且摄像头跟随模式开启，则跟随玩家
        if self.map_view and self.camera_follow_mode and player == self.game_state.get_current_player():
            self.map_view.follow_player(player, True)
    
    def _show_junction_selection(self, current_position: int, available_directions: List[int]):
        """显示岔路选择界面"""
        from src.ui.junction_selection_window import JunctionSelectionWindow
        
        player = self.pending_movement['player']
        
        self.junction_window = JunctionSelectionWindow(
            player, self.game_map, current_position, available_directions,
            self._on_direction_selected
        )
        
        self.add_message(f"{player.name}到达岔路口，请选择前进方向", "info")
    

    
    def execute_settlement(self):
        """执行结算"""
        try:
            current_player = self.game_state.get_current_player()
            if not current_player:
                print("❌ execute_settlement: 没有当前玩家")
                return
            
            # 检查玩家是否在监狱，在监狱中的玩家不触发格子效果
            if hasattr(current_player, 'in_jail') and current_player.in_jail:
                self.add_message(f"{current_player.name}在监狱中，无法触发格子效果", "info")
                return
            
            current_cell = self.game_map.get_cell_by_path_index(current_player.position)
            if not current_cell:
                print(f"❌ execute_settlement: 无法获取位置 {current_player.position} 的格子")
                self.add_message(f"{current_player.name}位置异常", "error")
                return
            
            print(f"🏛️ {current_player.name} 结算格子: {current_cell.cell_type} (位置: {current_player.position})")
            
            # 根据格子类型执行相应逻辑
            if current_cell.cell_type == "start":
                self.add_message(f"{current_player.name}到达起点", "info")
                # 可以在这里添加经过起点的奖励逻辑
            elif current_cell.cell_type == "shop":
                self.add_message(f"{current_player.name}进入道具商店", "info")
                if current_player.is_ai:
                    # AI玩家自动决策是否购买道具
                    self._ai_shop_decision(current_player)
                else:
                    self.open_item_shop(current_player)
            elif current_cell.cell_type == "dice_shop":
                self.add_message(f"{current_player.name}进入骰子商店", "info")
                if current_player.is_ai:
                    # AI玩家自动决策是否购买骰子
                    self._ai_dice_shop_decision(current_player)
                else:
                    self.open_dice_shop(current_player)
            elif current_cell.cell_type == "bank":
                self.add_message(f"{current_player.name}进入银行", "info")
                if current_player.is_ai:
                    # AI玩家自动决策银行操作
                    self._ai_bank_decision(current_player)
                else:
                    self.open_bank(current_player)
            elif current_cell.cell_type == "jail":
                self.add_message(f"{current_player.name}进入监狱", "info")
                # 保存进监狱前的位置
                current_player.pre_jail_position = current_player.position
                current_player.in_jail = True
                current_player.jail_turns = 0
            elif current_cell.cell_type == "luck":
                self.add_message(f"{current_player.name}获得好运", "info")
                try:
                    self.execute_luck_event(current_player)
                except Exception as e:
                    print(f"❌ 执行好运事件失败: {e}")
                    self.add_message(f"好运事件执行失败", "error")
            elif current_cell.cell_type == "bad_luck":
                self.add_message(f"{current_player.name}遭遇厄运", "info")
                try:
                    self.execute_bad_luck_event(current_player)
                except Exception as e:
                    print(f"❌ 执行厄运事件失败: {e}")
                    self.add_message(f"厄运事件执行失败", "error")
            elif current_cell.cell_type == "empty":
                # 空地，检查是否有房产
                if not current_cell.has_property():
                    try:
                        # 创建空房产对象
                        from src.models.property import Property
                        current_cell.property = Property(current_player.position, None, 0)
                        self.add_message(f"{current_player.name}到达空地，可以建设房产", "info")
                        if current_player.is_ai:
                            self._ai_property_decision(current_player, current_cell)
                        else:
                            self.open_property_window(current_player, current_cell)
                    except Exception as e:
                        print(f"❌ 创建房产对象失败: {e}")
                        self.add_message(f"{current_player.name}到达空地", "info")
                        # 不处理房产，直接继续
                else:
                    # 已有房产，按房产逻辑处理
                    try:
                        self._handle_property_settlement(current_player, current_cell)
                    except Exception as e:
                        print(f"❌ 处理房产结算失败: {e}")
                        self.add_message(f"房产结算失败", "error")
            elif current_cell.has_property():
                # 其他类型格子但有房产
                try:
                    self._handle_property_settlement(current_player, current_cell)
                except Exception as e:
                    print(f"❌ 处理房产结算失败: {e}")
                    self.add_message(f"房产结算失败", "error")
            else:
                # 其他格子类型，暂无特殊处理
                self.add_message(f"{current_player.name}到达{current_cell.get_name()}", "info")
            
            print(f"✅ {current_player.name} 结算完成")
            
        except Exception as e:
            print(f"❌ execute_settlement 异常: {e}")
            import traceback
            traceback.print_exc()
            
            # 发生错误时添加提示消息
            try:
                current_player = self.game_state.get_current_player()
                if current_player:
                    self.add_message(f"{current_player.name}结算时发生错误: {e}", "error")
                else:
                    self.add_message(f"结算时发生错误: {e}", "error")
            except:
                pass
    
    def _handle_property_settlement(self, player: Player, cell):
        """处理房产结算"""
        property_obj = cell.property
        
        if property_obj.owner_id == player.player_id:
            # 自己的房产，可以升级
            if property_obj.level < 4:
                self.add_message(f"{player.name}到达自己的房产，可以升级", "info")
                if player.is_ai:
                    self._ai_property_decision(player, cell)
                else:
                    self.open_property_window(player, cell)
            else:
                self.add_message(f"{player.name}到达自己的四级房产", "info")
        elif property_obj.owner_id is not None:
            # 他人的房产，支付租金
            rent = property_obj.get_rent()
            if rent > 0:
                # 找到房产所有者
                owner = None
                for p in self.game_state.players:
                    if p.player_id == property_obj.owner_id:
                        owner = p
                        break
                
                if owner:
                    player.money -= rent
                    owner.money += rent
                    self.add_message(f"{player.name}支付租金{rent}给{owner.name}", "warning")
                else:
                    self.add_message(f"房产所有者不存在，无需支付租金", "info")
            else:
                self.add_message(f"{player.name}到达他人的空地", "info")
        else:
            # 无主房产，可以购买
            self.add_message(f"{player.name}到达无主房产，可以建设", "info")
            if player.is_ai:
                self._ai_property_decision(player, cell)
            else:
                self.open_property_window(player, cell)
    
    def advance_phase(self):
        """推进到下一个阶段"""
        try:
            current_player = self.game_state.get_current_player()
            if not current_player:
                print("❌ advance_phase: 没有当前玩家")
                return
            
            print(f"🔧 推进阶段: 当前阶段 {self.game_state.current_phase} -> ", end="")
            
            # 推进游戏状态
            self.game_state.advance_phase()
            
            print(f"{self.game_state.current_phase}")
            
            # 如果轮到下一个玩家，摄像头跟随新玩家
            if self.game_state.current_phase == "preparation":
                new_player = self.game_state.get_current_player()
                if new_player and self.map_view and self.camera_follow_mode:
                    self.map_view.follow_player(new_player, True)
            
            # 根据新阶段执行相应操作
            if self.game_state.current_phase == "preparation":
                self.start_preparation_phase()
            elif self.game_state.current_phase == "action":
                self.start_action_phase()
            elif self.game_state.current_phase == "settlement":
                self.start_settlement_phase()
            elif self.game_state.current_phase == "end":
                self.start_end_phase()
                
        except Exception as e:
            print(f"❌ advance_phase 异常: {e}")
            import traceback
            traceback.print_exc()
            
            # 异常时的安全处理
            try:
                # 重置自动推进状态
                self.phase_auto_advance = False
                self.phase_timer = 0
                
                # 添加错误消息
                self.add_message("阶段推进时出现错误，游戏将继续", "error")
                
                # 尝试获取当前玩家
                current_player = self.game_state.get_current_player()
                if current_player:
                    print(f"🔧 当前玩家: {current_player.name}")
                    # 确保游戏继续运行 - 设置紧急恢复
                    if not hasattr(self, 'emergency_recovery_timer'):
                        self.emergency_recovery_timer = 3000  # 3秒后尝试恢复
                        print("🔧 设置紧急恢复定时器")
                        
            except Exception as e2:
                print(f"❌ 紧急处理也失败: {e2}")
                # 保持游戏运行，不崩溃
                self.phase_auto_advance = False
                self.phase_timer = 0
    
    def ai_preparation_decision(self, player: Player):
        """AI准备阶段决策"""
        # AI自动决策逻辑，添加延迟避免快速循环
        self.add_message(f"{player.name}完成准备", "info")
        
        # 设置延迟自动推进
        self.phase_auto_advance = True
        self.phase_timer = 1000  # 1秒延迟
    
    def ai_action_decision(self, player: Player):
        """AI行动阶段决策"""
        # 获取当前骰子信息
        current_dice_type = self.dice_system.get_current_dice_type()
        dice_config = self.dice_system.dice_set.dice_config
        dice_count = dice_config["count"]
        dice_sides = dice_config["sides"]
        
        # 获取骰子结果（包含每个骰子的结果）
        dice_results = self.dice_system.roll_current_dice()
        dice_sum = sum(dice_results)
        
        # 添加消息
        if dice_count == 1:
            self.add_message(f"{player.name} 投掷{current_dice_type}骰子: {dice_sum}", "info")
        else:
            results_str = " + ".join(map(str, dice_results))
            self.add_message(f"{player.name} 投掷{current_dice_type}骰子: {results_str} = {dice_sum}", "info")
        
        # 移动玩家
        self.move_player_with_animation(player, dice_sum)
        
        # 清除阶段按钮
        self.phase_buttons.clear()
        
        # 设置延迟自动推进到结算阶段
        self.phase_auto_advance = True
        self.phase_timer = 1000  # 1秒延迟
    
    def toggle_camera_mode(self):
        """切换摄像头模式"""
        self.camera_follow_mode = not self.camera_follow_mode
        
        # 更新地图视图的摄像头模式
        if self.map_view:
            if self.camera_follow_mode:
                self.map_view.toggle_camera_follow()
                # 立即跟随当前玩家
                current_player = self.game_state.get_current_player()
                if current_player:
                    self.map_view.follow_player(current_player, True)
            else:
                self.map_view.toggle_camera_manual()
        
        # 更新按钮文本和颜色
        for button in self.buttons:
            if button.text in ["跟随模式", "手动模式"]:
                button.text = "跟随模式" if self.camera_follow_mode else "手动模式"
                button.color = COLORS["primary"] if self.camera_follow_mode else COLORS["secondary"]
                break
    
    def open_map_editor(self):
        """打开地图编辑器"""
        try:
            from src.utils.map_editor import MapEditor
            editor = MapEditor()
            editor.run_gui_editor()
        except Exception as e:
            self.add_message(f"打开地图编辑器失败: {e}", "error")
    
    def open_settings(self):
        """打开设置"""
        self.add_message("设置功能开发中...", "info")
    
    def quit_game(self):
        """退出游戏"""
        # 先清理音乐系统
        if hasattr(self, 'music_system') and self.music_system:
            self.music_system.cleanup()
        
        self.running = False
    
    def return_to_menu(self):
        """返回菜单"""
        # 在多人游戏模式下不允许返回主菜单
        if hasattr(self, 'is_multiplayer') and self.is_multiplayer:
            print("⚠️ 多人游戏模式下不允许返回主菜单")
            self.add_message("多人游戏模式下不允许返回主菜单", "warning")
            return
        self.init_menu_scene()
    
    def add_message(self, text: str, message_type: str = "info"):
        """添加消息"""
        message = Message(text, message_type)
        self.messages.append(message)
        
        # 限制消息数量
        if len(self.messages) > 10:
            self.messages.pop(0)
    
    def handle_events(self):
        """处理事件"""
        try:
            mouse_pos = pygame.mouse.get_pos()
            hovered_cell = None
            hovered_player = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # 清理音乐系统
                    if hasattr(self, 'music_system') and self.music_system:
                        self.music_system.cleanup()
                    self.running = False
                    return
                
                # 【最高优先级】处理存档窗口事件
                if self.save_load_window and self.save_load_window.is_open:
                    if self.save_load_window.handle_event(event):
                        continue  # 存档窗口拦截了事件，不继续处理
                
                # 处理音乐事件
                if self.music_system.handle_music_event(event):
                    continue
                
                # 处理延迟移动事件
                if event.type == pygame.USEREVENT + 1:
                    if hasattr(self, '_delayed_move_callback'):
                        self._delayed_move_callback()
                        delattr(self, '_delayed_move_callback')
                    continue
                
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                    self.update_map_area()
                    continue
                
                # 处理键盘事件
                if event.type == pygame.KEYDOWN:
                    # Ctrl+S 快速保存
                    if event.key == pygame.K_s and (event.mod & pygame.KMOD_CTRL):
                        if self.current_scene == "game":
                            self.quick_save()
                            continue
                    
                    # Ctrl+L 打开加载窗口
                    if event.key == pygame.K_l and (event.mod & pygame.KMOD_CTRL):
                        if self.current_scene == "game" and not (self.save_load_window and self.save_load_window.is_open):
                            self.open_load_dialog()
                            continue
                    
                    # ESC关闭顶层窗口
                    if event.key == pygame.K_ESCAPE:
                        # 按优先级关闭窗口
                        if self.save_load_window and self.save_load_window.is_open:
                            self.close_save_load_window()
                            continue
                        elif self.inventory_window and self.inventory_window.is_open:
                            self.close_inventory_window()
                            continue
                        elif self.dice_window and self.dice_window.is_open:
                            self.close_dice_window()
                            continue
                        elif self.target_selection_window and self.target_selection_window.is_open:
                            self.target_selection_window.is_open = False
                            self.selecting_item_target = False
                            continue
                        elif self.bank_window and getattr(self.bank_window, 'visible', False):
                            self.close_bank()
                            continue
                        elif self.dice_shop_window and getattr(self.dice_shop_window, 'visible', False):
                            self.close_dice_shop()
                            continue
                        elif self.item_shop_window and getattr(self.item_shop_window, 'visible', False):
                            self.close_item_shop()
                            continue
                        elif self.property_window and getattr(self.property_window, 'visible', False):
                            self.close_property_window()
                            continue
                    
                    # 玩家移动控制 (WASD)
                    if self.current_scene == "game" and self.map_view and not self.camera_follow_mode:
                        if event.key == pygame.K_w:
                            self.map_view.offset_y += 20
                        elif event.key == pygame.K_s:
                            self.map_view.offset_y -= 20
                        elif event.key == pygame.K_a:
                            self.map_view.offset_x += 20
                        elif event.key == pygame.K_d:
                            self.map_view.offset_x -= 20
                
                # 处理鼠标滚轮
                if event.type == pygame.MOUSEWHEEL:
                    if self.current_scene == "game" and self.map_view:
                        # 缩放地图
                        zoom_factor = 1.1 if event.y > 0 else 0.9
                        self.map_view.zoom(zoom_factor)
                        continue
                
                # 处理鼠标移动
                if event.type == pygame.MOUSEMOTION:
                    if self.current_scene == "game" and self.map_view:
                        # 让MapView处理鼠标移动事件（悬停效果）
                        self.map_view.handle_event(event)
                        # 更新本地悬停信息
                        hovered_cell = None
                        hovered_player = None
                        if self.map_view.hovered_cell:
                            hovered_cell = self.game_map.get_cell_at(self.map_view.hovered_cell)
                            # 检查是否悬停在玩家上
                            for player in self.game_state.players:
                                player_pos = self.game_map.get_position_by_path_index(player.position)
                                if player_pos and abs(player_pos[0] - self.map_view.hovered_cell[0]) < 0.5 and abs(player_pos[1] - self.map_view.hovered_cell[1]) < 0.5:
                                    hovered_player = player
                                    break
                
                # 处理鼠标按键
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # 处理道具目标选择
                    if self.selecting_item_target and self.current_scene == "game" and self.map_view:
                        map_pos = self.map_view.screen_to_map_pos(*mouse_pos)
                        if map_pos and self.selected_item_id:
                            cell = self.game_map.get_cell_at(map_pos)
                            if cell:
                                # 根据道具类型处理
                                if self.selected_item_id == 1:  # 路障
                                    if cell.cell_type != "void" and not getattr(cell, 'roadblock', False):
                                        self.execute_item_use(self.selected_item_id, {'type': 'cell', 'pos': map_pos})
                                        self.selecting_item_target = False
                                        self.selected_item_id = None
                                        if self.target_selection_window:
                                            self.target_selection_window.is_open = False
                                elif self.selected_item_id == 2:  # 传送门
                                    if cell.cell_type != "void":
                                        self.execute_item_use(self.selected_item_id, {'type': 'cell', 'pos': map_pos})
                                        self.selecting_item_target = False
                                        self.selected_item_id = None
                                        if self.target_selection_window:
                                            self.target_selection_window.is_open = False
                        continue
                    
                    # 处理子窗口点击
                    handled = False
                    
                    # 检查存档窗口
                    if self.save_load_window and self.save_load_window.is_open:
                        if self.save_load_window.handle_event(event):
                            handled = True
                    
                    # 检查道具窗口
                    if not handled and self.inventory_window and self.inventory_window.is_open:
                        if self.inventory_window.handle_event(event):
                            handled = True
                    
                    # 检查骰子窗口
                    if not handled and self.dice_window and self.dice_window.is_open:
                        if self.dice_window.handle_event(event):
                            handled = True
                    
                    # 检查目标选择窗口
                    if not handled and self.target_selection_window and self.target_selection_window.is_open:
                        if self.target_selection_window.handle_event(event):
                            handled = True
                    
                    # 检查银行窗口
                    if not handled and self.bank_window and getattr(self.bank_window, 'visible', False):
                        if self.bank_window.handle_event(event):
                            handled = True
                    
                    # 检查骰子商店窗口
                    if not handled and self.dice_shop_window and getattr(self.dice_shop_window, 'visible', False):
                        if self.dice_shop_window.handle_event(event):
                            handled = True
                    
                    # 检查道具商店窗口
                    if not handled and self.item_shop_window and getattr(self.item_shop_window, 'visible', False):
                        if self.item_shop_window.handle_event(event):
                            handled = True
                    
                    # 检查房产窗口
                    if not handled and self.property_window and getattr(self.property_window, 'visible', False):
                        if self.property_window.handle_event(event):
                            handled = True
                    
                    if handled:
                        continue
                    
                    # 处理主界面按钮
                    button_clicked = False
                    for button in self.buttons:
                        if button.rect.collidepoint(mouse_pos):
                            if button.callback:
                                button.callback()
                            button_clicked = True
                            break
                    
                    # 处理阶段按钮
                    if not button_clicked:
                        for button in self.phase_buttons:
                            if button.rect.collidepoint(mouse_pos):
                                if button.callback:
                                    button.callback()
                                button_clicked = True
                                break
                    
                    # 只有在没有点击任何按钮时才处理地图格子点击
                    if not button_clicked and self.current_scene == "game" and self.map_view:
                        # 让MapView处理事件，包括格子选择
                        if self.map_view.handle_event(event):
                            # 如果MapView处理了事件，获取选中的格子信息
                            if self.map_view.selected_cell:
                                cell = self.game_map.get_cell_at(self.map_view.selected_cell)
                                if cell:
                                    cell_info = self.map_view.get_cell_info_text(cell)
                                    print(f"🎯 选中格子: 位置{self.map_view.selected_cell}, 信息: {cell_info}")
                                    self.add_message(f"选中格子: {cell_info} 位置{self.map_view.selected_cell}", "info")
                    
                    # 处理地图点击（用于手动摄像头移动）
                    if self.current_scene == "game" and not self.camera_follow_mode and self.map_view:
                        # 中键拖拽移动地图
                        if event.button == 2:  # 中键
                            self.map_view.start_drag(mouse_pos)
            
            # 更新悬停状态
            self.hovered_cell = hovered_cell
            self.hovered_player = hovered_player
            
        except Exception as e:
            print(f"🔧 handle_events 异常: {e}")
            import traceback
            traceback.print_exc()
            # 不让异常传播，保持游戏运行
            try:
                self.add_message("事件处理时出现错误", "error")
            except:
                pass
    
    def update(self):
        """更新游戏状态"""
        try:
            # 更新动画系统
            self.animation_manager.update()
            
            # 更新摄像头
            if self.map_view and self.current_scene == "game":
                self.map_view.update_camera()
            
            # 处理紧急恢复
            if hasattr(self, 'emergency_recovery_timer') and self.emergency_recovery_timer > 0:
                self.emergency_recovery_timer -= self.clock.get_time()
                if self.emergency_recovery_timer <= 0:
                    print("🔧 执行紧急恢复")
                    delattr(self, 'emergency_recovery_timer')
                    # 尝试重新开始准备阶段
                    try:
                        self.game_state.set_current_phase("preparation")
                        self.start_preparation_phase()
                        self.add_message("游戏已恢复正常", "success")
                    except Exception as recovery_error:
                        print(f"🔧 紧急恢复失败: {recovery_error}")
                        # 最后手段：重置必要状态
                        self.phase_auto_advance = False
                        self.phase_timer = 0
                        self.is_animating = False
            
            # 更新阶段计时器
            if self.phase_auto_advance and self.phase_timer > 0:
                self.phase_timer -= self.clock.get_time()
                if self.phase_timer <= 0:
                    # 自动推进阶段
                    self.phase_auto_advance = False  # 重置自动推进标志
                    self.advance_phase()
            
            # 检查游戏结束
            if self.game_state.check_game_over():
                winner = self.game_state.winner
                if winner:
                    self.add_message(f"游戏结束！{winner.name}获胜！", "success")
                else:
                    self.add_message("游戏结束！", "info")
                    
        except Exception as e:
            print(f"🔧 update 异常: {e}")
            import traceback
            traceback.print_exc()
            # 不让异常传播，保持游戏运行
            try:
                self.add_message("游戏更新时出现错误", "error")
                # 重置可能有问题的状态
                self.phase_auto_advance = False
                self.phase_timer = 0
            except:
                pass
    
    def draw(self):
        """绘制界面"""
        self.screen.fill(COLORS["background"])
        
        # 在多人游戏模式下强制使用game场景
        if hasattr(self, 'is_multiplayer') and self.is_multiplayer and self.current_scene == "menu":
            print("⚠️ 多人游戏模式下强制切换回game场景")
            self.current_scene = "game"
        
        if self.current_scene == "menu":
            self.draw_menu()
        elif self.current_scene == "game_setup":
            self.draw_game_setup()
        elif self.current_scene == "game":
            self.draw_game()
        
        # 绘制子窗口（总是在最上层）
        if self.inventory_window and self.inventory_window.is_open:
            self.inventory_window.draw(self.screen)
        
        if self.dice_window and self.dice_window.is_open:
            self.dice_window.draw(self.screen)
        
        if self.target_selection_window and self.target_selection_window.is_open:
            self.target_selection_window.draw(self.screen)
        
        if self.dice_shop_window and getattr(self.dice_shop_window, 'visible', False):
            self.dice_shop_window.draw(self.screen)
        
        if self.item_shop_window and getattr(self.item_shop_window, 'visible', False):
            self.item_shop_window.draw(self.screen)
        
        if self.bank_window and getattr(self.bank_window, 'visible', False):
            self.bank_window.draw(self.screen)
        
        if self.property_window and getattr(self.property_window, 'visible', False):
            self.property_window.draw(self.screen)
        
        # 绘制存档窗口（最高优先级）
        if self.save_load_window and self.save_load_window.is_open:
            self.save_load_window.draw()
        
        pygame.display.flip()
    
    def draw_menu(self):
        """绘制菜单"""
        # 在多人游戏模式下不绘制主菜单
        if hasattr(self, 'is_multiplayer') and self.is_multiplayer:
            print("⚠️ 多人游戏模式下跳过主菜单绘制")
            return
            
        # 1. 绘制背景图片
        try:
            if not hasattr(self, '_menu_bg_img'):
                bg_img = pygame.image.load('assets/images/background/index.jpeg')
                self._menu_bg_img = pygame.transform.scale(bg_img, (self.screen.get_width(), self.screen.get_height()))
            else:
                # 窗口大小变化时重新缩放
                if self._menu_bg_img.get_width() != self.screen.get_width() or self._menu_bg_img.get_height() != self.screen.get_height():
                    bg_img = pygame.image.load('assets/images/background/index.jpeg')
                    self._menu_bg_img = pygame.transform.scale(bg_img, (self.screen.get_width(), self.screen.get_height()))
            self.screen.blit(self._menu_bg_img, (0, 0))
        except Exception as e:
            self.screen.fill(COLORS["background"])
        
        # 2. 绘制艺术字标题
        center_x = self.screen.get_width() // 2
        title_y = 60
        man_font = pygame.font.SysFont('arialblack', 64, bold=True)
        man_surface = man_font.render("man", True, (52, 152, 219))
        bro_font = pygame.font.SysFont('comicsansms', 64, italic=True)
        bro_surface = bro_font.render("bro", True, (230, 126, 34))
        
        # 使用全局字体管理器渲染中文
        cn_surface = render_text("大富翁", "large", (44, 62, 80), True)
        
        total_width = man_surface.get_width() + 24 + bro_surface.get_width() + 24 + cn_surface.get_width()
        start_x = center_x - total_width // 2
        self.screen.blit(man_surface, (start_x, title_y))
        self.screen.blit(bro_surface, (start_x + man_surface.get_width() + 24, title_y))
        self.screen.blit(cn_surface, (start_x + man_surface.get_width() + 24 + bro_surface.get_width() + 24, title_y + 8))
        
        # 3. 绘制六张玩家图片
        player_imgs = []
        player_img_paths = [
            'assets/images/player/player1_main.png',
            'assets/images/player/player2_main.jpg',
            'assets/images/player/player3_main.jpg',
            'assets/images/player/player4_main.jpeg',
            'assets/images/player/player5_main.jpeg',
            'assets/images/player/player6_main.png',
        ]
        img_size = 80
        for path in player_img_paths:
            try:
                img = pygame.image.load(path)
                img = pygame.transform.scale(img, (img_size, img_size))
                player_imgs.append(img)
            except Exception as e:
                pass
        total_img_width = len(player_imgs) * img_size + (len(player_imgs) - 1) * 24
        img_start_x = center_x - total_img_width // 2
        img_y = title_y + 90
        for i, img in enumerate(player_imgs):
            self.screen.blit(img, (img_start_x + i * (img_size + 24), img_y))
        
        # 4. 绘制标题和按钮
        for panel in self.panels:
            panel.draw(self.screen, self.fonts)
        for button in self.buttons:
            button.draw(self.screen, self.fonts)
    
    def draw_game_setup(self):
        """绘制游戏设置"""
        # 绘制标题和按钮
        for panel in self.panels:
            panel.draw(self.screen, self.fonts)
        
        for button in self.buttons:
            button.draw(self.screen, self.fonts)
    
    def draw_game(self):
        """绘制游戏界面"""
        # 绘制地图
        if self.map_view:
            players = self.game_state.players
            self.map_view.draw(self.screen, players)
        # 绘制面板
        for panel in self.panels:
            panel.draw(self.screen, self.fonts)
        # 绘制游戏信息
        self.draw_game_info()
        # 绘制消息
        self.draw_messages()
        # 绘制阶段按钮
        for button in self.phase_buttons:
            button.draw(self.screen, self.fonts)
        # 地图高亮合法目标
        if self.selecting_item_target and self.selected_item_id == 1:  # 路障
            for y in range(self.game_map.height):
                for x in range(self.game_map.width):
                    cell = self.game_map.get_cell_at((x, y))
                    if cell and cell.cell_type != "void" and not getattr(cell, 'roadblock', False):
                        # get_cell_rect已经返回了正确的屏幕坐标，不需要再加map_offset
                        rect = self.map_view.get_cell_rect(x, y)
                        # 区分选中、悬停和普通状态
                        if hasattr(self, '_selected_cell') and self._selected_cell == (x, y):
                            # 绿色：已选中 - 使用填充矩形
                            # 创建半透明表面
                            overlay = pygame.Surface((rect.width, rect.height))
                            overlay.set_alpha(100)
                            overlay.fill((0, 255, 0))
                            self.screen.blit(overlay, rect.topleft)
                            pygame.draw.rect(self.screen, (0, 255, 0), rect, 8)    # 绿色边框
                        elif self._hovered_cell == (x, y):
                            # 橙色：悬停预览 - 使用填充矩形
                            # 创建半透明表面
                            overlay = pygame.Surface((rect.width, rect.height))
                            overlay.set_alpha(60)
                            overlay.fill((255, 165, 0))
                            self.screen.blit(overlay, rect.topleft)
                            pygame.draw.rect(self.screen, (255, 165, 0), rect, 4)  # 橙色边框
                        else:
                            # 淡蓝色：可选择
                            pygame.draw.rect(self.screen, (173, 216, 230), rect, 2)  # 淡蓝色边框
            
            # 选中格子后显示确认按钮
            if hasattr(self, '_selected_cell') and self._selected_cell:
                btn_w, btn_h = 180, 50
                btn_x = self.screen.get_width() // 2 - btn_w // 2
                btn_y = self.screen.get_height() - btn_h - 40
                confirm_btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
                # 绘制按钮背景
                pygame.draw.rect(self.screen, (0, 200, 0), confirm_btn_rect, border_radius=10)
                pygame.draw.rect(self.screen, (0, 255, 0), confirm_btn_rect, 4, border_radius=10)
                # 绘制按钮文字
                font = self.fonts["normal"] if "normal" in self.fonts else pygame.font.Font(None, 24)
                text = f"确认放置路障在 {self._selected_cell}"
                text_surf = font.render(text, True, (255,255,255))
                text_rect = text_surf.get_rect(center=confirm_btn_rect.center)
                self.screen.blit(text_surf, text_rect)
                self._confirm_btn_rect = confirm_btn_rect
            else:
                self._confirm_btn_rect = None
        
        # 绘制骰子动画
        if self.current_dice_animation and self.current_dice_animation.is_playing:
            self.draw_dice_animation()
    
    def draw_game_info(self):
        """绘制游戏信息"""
        if not self.game_state.players:
            return
        
        # 获取信息面板
        info_panel = None
        for panel in self.panels:
            if panel.title == "游戏信息":
                info_panel = panel
                break
        
        if not info_panel:
            return
        
        # --- 当前玩家信息 ---
        current_player = self.game_state.get_current_player()
        y_offset = 30
        if current_player:
            # 头像
            player_key = f"player{current_player.player_id}"
            avatar = None
            if self.map_view and player_key in self.map_view.player_images:
                avatar = self.map_view.player_images[player_key]
            if avatar:
                avatar_rect = avatar.get_rect()
                avatar_rect.topleft = (info_panel.rect.x + 10, info_panel.rect.y + y_offset)
                self.screen.blit(avatar, avatar_rect)
                text_x = avatar_rect.right + 10
            else:
                text_x = info_panel.rect.x + 10
            # 名字（加粗）
            name_surface = self.fonts["subtitle"].render(f"{current_player.name}", True, COLORS["success"])
            self.screen.blit(name_surface, (text_x, info_panel.rect.y + y_offset))
            y_offset += max(avatar.get_height() if avatar else 40, 40) + 5
            # 资金
            money_surface = self.fonts["normal"].render(f"资金: {current_player.money}", True, COLORS["text_primary"])
            self.screen.blit(money_surface, (info_panel.rect.x + 10, info_panel.rect.y + y_offset))
            y_offset += 28
            # 银行余额（如有）
            bank_money = getattr(current_player, "bank_money", None)
            if bank_money is not None:
                bank_surface = self.fonts["normal"].render(f"银行: {bank_money}", True, COLORS["primary"])
                self.screen.blit(bank_surface, (info_panel.rect.x + 10, info_panel.rect.y + y_offset))
                y_offset += 28
            # 位置
            pos_surface = self.fonts["normal"].render(f"位置: {current_player.position}", True, COLORS["text_primary"])
            self.screen.blit(pos_surface, (info_panel.rect.x + 10, info_panel.rect.y + y_offset))
            y_offset += 28
            # 阶段
            phase_surface = self.fonts["normal"].render(f"阶段: {self.game_state.current_phase}", True, COLORS["text_primary"])
            self.screen.blit(phase_surface, (info_panel.rect.x + 10, info_panel.rect.y + y_offset))
            y_offset += 36
        else:
            y_offset += 40
        
        # --- 玩家列表 ---
        y_offset += 10
        title_surface = self.fonts["subtitle"].render("玩家列表:", True, COLORS["text_primary"])
        self.screen.blit(title_surface, (info_panel.rect.x + 10, info_panel.rect.y + y_offset))
        y_offset += 36
        avatar_size = 32
        for player in self.game_state.players:
            # 头像
            player_key = f"player{player.player_id}"
            avatar = None
            if self.map_view and player_key in self.map_view.player_images:
                avatar = pygame.transform.scale(self.map_view.player_images[player_key], (avatar_size, avatar_size))
            # 状态
            status = "当前" if player == current_player else ("破产" if player.is_bankrupt() else "等待")
            color = COLORS["success"] if player == current_player else (COLORS["error"] if player.is_bankrupt() else COLORS["text_primary"])
            # 资金
            money = player.money
            bank_money = getattr(player, "bank_money", None)
            # 绘制头像
            if avatar:
                avatar_rect = avatar.get_rect()
                avatar_rect.topleft = (info_panel.rect.x + 10, info_panel.rect.y + y_offset)
                self.screen.blit(avatar, avatar_rect)
                text_x = avatar_rect.right + 8
            else:
                text_x = info_panel.rect.x + 10
            # 名字和状态
            name_surface = self.fonts["normal"].render(f"{player.name}", True, color)
            self.screen.blit(name_surface, (text_x, info_panel.rect.y + y_offset))
            status_surface = self.fonts["small"].render(f"({status})", True, color)
            self.screen.blit(status_surface, (text_x + name_surface.get_width() + 8, info_panel.rect.y + y_offset + 4))
            # 资金
            money_surface = self.fonts["small"].render(f"资金:{money}", True, COLORS["text_primary"])
            self.screen.blit(money_surface, (text_x, info_panel.rect.y + y_offset + 22))
            # 银行余额
            if bank_money is not None:
                bank_surface = self.fonts["small"].render(f"银行:{bank_money}", True, COLORS["primary"])
                self.screen.blit(bank_surface, (text_x + money_surface.get_width() + 10, info_panel.rect.y + y_offset + 22))
            y_offset += avatar_size + 10
        
        # --- 存档操作说明 ---
        y_offset += 20
        save_title_surface = self.fonts["subtitle"].render("存档操作:", True, COLORS["text_primary"])
        self.screen.blit(save_title_surface, (info_panel.rect.x + 10, info_panel.rect.y + y_offset))
        y_offset += 30
        
        save_help_lines = [
            "F5 - 快速保存",
            "F9 - 快速加载", 
            "Ctrl+S - 保存游戏",
            "Ctrl+L - 加载游戏"
        ]
        
        for line in save_help_lines:
            help_surface = self.fonts["small"].render(line, True, COLORS["info"])
            self.screen.blit(help_surface, (info_panel.rect.x + 10, info_panel.rect.y + y_offset))
            y_offset += 18
    
    def draw_messages(self):
        """绘制消息"""
        # 获取消息面板
        message_panel = None
        for panel in self.panels:
            if panel.title == "游戏消息":
                message_panel = panel
                break
        
        if not message_panel:
            return
        
        # 绘制最近的消息
        y_offset = 30
        for message in self.messages[-5:]:  # 只显示最近5条消息
            message_surface = self.fonts["small"].render(message.text, True, message.color)
            self.screen.blit(message_surface, (message_panel.rect.x + 10, message_panel.rect.y + y_offset))
            y_offset += 20
    
    def update_map_area(self):
        """根据窗口大小自适应地图区域和格子大小"""
        win_w, win_h = self.screen.get_size()
        map_area_width = win_w - INFO_PANEL_WIDTH - MAP_MARGIN * 2
        map_area_height = win_h - MESSAGE_PANEL_HEIGHT - MAP_MARGIN * 2
        map_area_size = min(map_area_width, map_area_height)
        if self.game_map:
            cell_size = max(24, min(map_area_size // self.game_map.width, map_area_size // self.game_map.height))
            size = cell_size * self.game_map.width
        else:
            cell_size = 60
            size = cell_size * 15
        print(f"[最终修正] cell_size={cell_size}, size={size}, map_area_size={map_area_size}, width={self.game_map.width if self.game_map else 'N/A'}, height={self.game_map.height if self.game_map else 'N/A'}")
        if self.map_view:
            self.map_view.x = MAP_MARGIN
            self.map_view.y = MAP_MARGIN
            self.map_view.size = size
            self.map_view.cell_size = cell_size
            self.map_view._load_images()
            # 重置视图以适应新的尺寸
            self.map_view.reset_view()
            # 居中显示地图
            self.map_view.center_map()
    
    def run(self):
        """运行游戏主循环"""
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(60)
        finally:
            # 确保音乐系统正确清理
            if hasattr(self, 'music_system') and self.music_system:
                self.music_system.cleanup()
            
            # 清理pygame资源
            try:
                pygame.mixer.quit()
            except:
                pass
            
            pygame.quit()
            sys.exit()

    def close_inventory_window(self):
        """关闭道具窗口"""
        if self.inventory_window:
            self.inventory_window.is_open = False
            self.inventory_window = None
        # 如果是在准备阶段关闭窗口，需要推进游戏
        if self.game_state.current_phase == "preparation":
            try:
                self.advance_phase()
            except Exception as e:
                print(f"🔧 关闭道具窗口时推进阶段失败: {e}")
                # 设置自动推进作为备用方案
                self.phase_auto_advance = True
                self.phase_timer = 500  # 0.5秒后自动推进
    
    def execute_item_use(self, item_id: int, target_info: dict):
        """执行道具使用"""
        current_player = self.game_state.get_current_player()
        if not current_player:
            return
        
        if item_id == 1:  # 路障道具
            if target_info["type"] == "cell":
                pos = target_info["pos"]
                cell = self.game_map.get_cell_at(pos)
                if cell:
                    # 在目标格子放置路障
                    setattr(cell, 'roadblock', True)
                    self.add_message(f"在位置 {pos} 放置了路障", "success")
                    
                    # 从背包中移除道具
                    if item_id in current_player.inventory:
                        current_player.inventory[item_id] -= 1
                        if current_player.inventory[item_id] <= 0:
                            del current_player.inventory[item_id]
                    
                    # 道具使用完成，回到准备阶段等待玩家操作
                    self.add_message("道具使用完成，可以点击跳过继续游戏", "info")
                else:
                    self.add_message("无效的目标位置", "error")
        
        elif item_id == 2:  # 传送道具
            if target_info["type"] == "player":
                target_player = target_info["player"]
                # 传送到目标玩家的位置
                current_player.position = target_player.position
                self.add_message(f"{current_player.name}传送到了{target_player.name}的位置({target_player.position})", "success")
                
                # 摄像头跟随传送后的玩家
                if self.map_view and self.camera_follow_mode:
                    self.map_view.follow_player(current_player, True)
                
                # 从背包中移除道具
                if item_id in current_player.inventory:
                    current_player.inventory[item_id] -= 1
                    if current_player.inventory[item_id] <= 0:
                        del current_player.inventory[item_id]
                
                # 道具使用完成，回到准备阶段等待玩家操作
                self.add_message("道具使用完成，可以点击跳过继续游戏", "info")
        
        # 关闭道具窗口
        self.close_inventory_window()
    
    # ==================== 商店系统 ====================
    
    def open_dice_shop(self, player: Player):
        """打开骰子商店"""
        if not self.dice_shop_window:
            self.dice_shop_window = DiceShopWindow(
                on_close=self.close_dice_shop,
                on_purchase=self.purchase_dice
            )
        
        # 显示窗口
        screen_width, screen_height = self.screen.get_size()
        player_items_count = sum(player.inventory.values()) if hasattr(player, 'inventory') else 0
        self.dice_shop_window.show(screen_width, screen_height, player.money, player_items_count)
    
    def close_dice_shop(self):
        """关闭骰子商店"""
        if self.dice_shop_window:
            self.dice_shop_window.hide()
        # 恢复自动推进
        print("🔧 骰子商店窗口关闭，恢复自动推进")
        self.phase_auto_advance = True
        self.phase_timer = 1000  # 1秒后自动推进
    
    def purchase_dice(self, product):
        """购买骰子"""
        current_player = self.game_state.get_current_player()
        if not current_player:
            return
        
        # 检查是否有足够的金钱和道具卡
        price = product["price"]
        item_cost = product["item_cost"]
        
        if current_player.money < price:
            self.add_message("金钱不足", "error")
            return
        
        # 计算玩家道具卡数量
        item_count = sum(current_player.inventory.values()) if hasattr(current_player, 'inventory') else 0
        
        if item_count < item_cost:
            self.add_message("道具卡不足", "error")
            return
        
        # 扣除金钱
        current_player.money -= price
        
        # 扣除道具卡
        remaining_cost = item_cost
        for item_id in list(current_player.inventory.keys()):
            if remaining_cost <= 0:
                break
            take_count = min(current_player.inventory[item_id], remaining_cost)
            current_player.inventory[item_id] -= take_count
            remaining_cost -= take_count
            if current_player.inventory[item_id] <= 0:
                del current_player.inventory[item_id]
        
        # 直接使用产品ID作为骰子类型
        new_dice_type = product["id"]
        
        # 特殊处理d20神力骰子的映射
        if new_dice_type == "d20":
            new_dice_type = "2d20"  # d20神力实际上是2d20
        
        # 为当前玩家添加骰子类型（不影响全局系统）
        if not hasattr(current_player, 'dice_system'):
            from src.systems.dice_system import DiceSystem
            current_player.dice_system = DiceSystem()
        
        # 添加到玩家个人的骰子系统
        current_player.dice_system.add_dice_type(new_dice_type)
        current_player.dice_system.set_current_dice(new_dice_type)
        current_player.dice = new_dice_type
        
        print(f"🎲 {current_player.name}购买了{product['name']}，设置为个人骰子")
        
        # 刷新骰子窗口（如果打开的话）
        if self.dice_window:
            self.dice_window.refresh()
        
        self.add_message(f"购买{product['name']}成功！", "success")
        
        # 恢复自动推进
        print("🔧 骰子购买完成，恢复自动推进")
        self.phase_auto_advance = True
        self.phase_timer = 1000  # 1秒后自动推进
    
    def open_item_shop(self, player: Player):
        """打开道具商店"""
        if not self.item_shop_window:
            self.item_shop_window = ItemShopWindow(
                on_close=self.close_item_shop,
                on_purchase=self.purchase_item
            )
        
        # 显示窗口
        screen_width, screen_height = self.screen.get_size()
        self.item_shop_window.show(screen_width, screen_height, player.money)
    
    def close_item_shop(self):
        """关闭道具商店"""
        if self.item_shop_window:
            self.item_shop_window.hide()
        # 恢复自动推进
        print("🔧 道具商店窗口关闭，恢复自动推进")
        self.phase_auto_advance = True
        self.phase_timer = 1000  # 1秒后自动推进
    
    def purchase_item(self, item):
        """购买道具"""
        current_player = self.game_state.get_current_player()
        if not current_player:
            return
        
        # 检查资金（仅使用身上余额）
        if current_player.money >= item["price"]:
            # 扣除金钱
            current_player.money -= item["price"]
            
            # 添加道具到背包
            if not hasattr(current_player, 'inventory'):
                current_player.inventory = {}
            
            if item["id"] in current_player.inventory:
                current_player.inventory[item["id"]] += 1
            else:
                current_player.inventory[item["id"]] = 1
            
            self.add_message(f"{current_player.name}购买了{item['name']}", "success")
            
            # 更新窗口显示
            screen_width, screen_height = self.screen.get_size()
            self.item_shop_window.show(screen_width, screen_height, current_player.money)
            
            # 恢复自动推进
            print("🔧 道具购买完成，恢复自动推进")
            self.phase_auto_advance = True
            self.phase_timer = 1000  # 1秒后自动推进
        else:
            self.add_message("金钱不足", "error")
    
    def open_bank(self, player: Player):
        """打开银行"""
        if not self.bank_window:
            self.bank_window = BankWindow(
                on_close=self.close_bank,
                on_deposit=self.bank_deposit,
                on_withdraw=self.bank_withdraw
            )
        
        # 计算银行信息
        total_bank_assets = self.calculate_total_bank_assets()
        rounds_until_interest = self.calculate_rounds_until_interest()
        
        # 确保玩家有银行存款属性
        if not hasattr(player, 'bank_money'):
            player.bank_money = 0
        
        # 显示窗口
        screen_width, screen_height = self.screen.get_size()
        self.bank_window.show(screen_width, screen_height, player.money, player.bank_money, 
                             total_bank_assets, rounds_until_interest)
    
    def close_bank(self):
        """关闭银行"""
        if self.bank_window:
            self.bank_window.hide()
        # 恢复自动推进
        print("🔧 银行窗口关闭，恢复自动推进")
        self.phase_auto_advance = True
        self.phase_timer = 1000  # 1秒后自动推进
    
    def bank_deposit(self, amount: int):
        """银行存款"""
        current_player = self.game_state.get_current_player()
        if not current_player:
            return
        
        if current_player.money >= amount:
            # 转移资金
            current_player.money -= amount
            if not hasattr(current_player, 'bank_money'):
                current_player.bank_money = 0
            current_player.bank_money += amount
            
            self.add_message(f"{current_player.name}存入${amount:,}", "success")
            
            # 更新窗口显示
            total_bank_assets = self.calculate_total_bank_assets()
            rounds_until_interest = self.calculate_rounds_until_interest()
            screen_width, screen_height = self.screen.get_size()
            self.bank_window.show(screen_width, screen_height, current_player.money, 
                                 current_player.bank_money, total_bank_assets, rounds_until_interest)
        else:
            self.add_message("现金不足", "error")
    
    def bank_withdraw(self, amount: int):
        """银行取款"""
        current_player = self.game_state.get_current_player()
        if not current_player:
            return
        
        if not hasattr(current_player, 'bank_money'):
            current_player.bank_money = 0
        
        if current_player.bank_money >= amount:
            # 转移资金
            current_player.bank_money -= amount
            current_player.money += amount
            
            self.add_message(f"{current_player.name}取出${amount:,}", "success")
            
            # 更新窗口显示
            total_bank_assets = self.calculate_total_bank_assets()
            rounds_until_interest = self.calculate_rounds_until_interest()
            screen_width, screen_height = self.screen.get_size()
            self.bank_window.show(screen_width, screen_height, current_player.money, 
                                 current_player.bank_money, total_bank_assets, rounds_until_interest)
        else:
            self.add_message("银行存款不足", "error")
    
    def calculate_total_bank_assets(self) -> int:
        """计算银行总资产"""
        total = 0
        for player in self.game_state.players:
            if hasattr(player, 'bank_money'):
                total += player.bank_money
        return total
    
    def calculate_rounds_until_interest(self) -> int:
        """计算距离下次利息的轮数"""
        # 简化实现：假设每3轮发放一次利息
        # 这里需要根据实际的轮次计算系统来实现
        return 3 - (getattr(self.game_state, 'round_count', 0) % 3)
    
    def execute_luck_event(self, player: Player):
        """执行好运事件"""
        import random
        
        events = [
            ("money_percent", "获得等同于身上资产20%的资金"),
            ("bank_multiply", "银行中的资产翻1.3倍"),
            ("random_item", "随机获得一张道具卡"),
            ("fixed_money", "获得20,000")
        ]
        
        event_type, description = random.choice(events)
        
        if event_type == "money_percent":
            bonus = int(player.money * 0.2)
            player.money += bonus
            self.add_message(f"{player.name}{description}: ${bonus:,}", "success")
        
        elif event_type == "bank_multiply":
            if hasattr(player, 'bank_money') and player.bank_money > 0:
                old_amount = player.bank_money
                player.bank_money = int(player.bank_money * 1.3)
                bonus = player.bank_money - old_amount
                self.add_message(f"{player.name}{description}: +${bonus:,}", "success")
            else:
                # 如果没有银行存款，改为获得固定金额
                player.money += 20000
                self.add_message(f"{player.name}银行无存款，改为获得$20,000", "success")
        
        elif event_type == "random_item":
            if not hasattr(player, 'inventory'):
                player.inventory = {}
            
            # 随机选择一个道具
            item_ids = [1, 2, 3, 4, 5]
            item_id = random.choice(item_ids)
            
            if item_id in player.inventory:
                player.inventory[item_id] += 1
            else:
                player.inventory[item_id] = 1
            
            self.add_message(f"{player.name}{description}", "success")
        
        elif event_type == "fixed_money":
            player.money += 20000
            self.add_message(f"{player.name}{description}", "success")
    
    def execute_bad_luck_event(self, player: Player):
        """执行厄运事件"""
        import random
        
        def lose_random_item():
            """丢失随机道具"""
            if not hasattr(player, 'inventory') or not player.inventory:
                self.add_message(f"{player.name}没有道具可以丢失", "info")
                return
            
            # 随机选择一个道具类型
            item_ids = list(player.inventory.keys())
            if item_ids:
                selected_id = random.choice(item_ids)
                player.inventory[selected_id] -= 1
                if player.inventory[selected_id] <= 0:
                    del player.inventory[selected_id]
                self.add_message(f"{player.name}丢失了一个道具", "warning")
        
        bad_luck_events = [
            {
                "name": "罚款",
                "description": "缴纳罚款",
                "action": lambda: setattr(player, 'money', max(0, player.money - random.randint(5000, 15000)))
            },
            {
                "name": "倒退",
                "description": "倒退几步",
                "action": lambda: setattr(player, 'position', max(0, player.position - random.randint(1, 3)))
            },
            {
                "name": "丢失道具",
                "description": "随机丢失一个道具",
                "action": lose_random_item
            },
            {
                "name": "监禁",
                "description": "被关进监狱1轮",
                "action": lambda: (
                    setattr(player, 'pre_jail_position', player.position),
                    setattr(player, 'in_jail', True), 
                    setattr(player, 'jail_turns', 0)
                )
            },
            {
                "name": "房产损坏",
                "description": "随机一个房产降级",
                "action": lambda: self._downgrade_random_property(player)
            }
        ]
        
        # 随机选择一个厄运事件
        event = random.choice(bad_luck_events)
        self.add_message(f"{player.name}遭遇厄运：{event['description']}", "error")
        
        # 执行事件效果
        try:
            event["action"]()
        except Exception as e:
            print(f"执行厄运事件失败: {e}")
    
    def _downgrade_random_property(self, player: Player):
        """随机降级玩家的一个房产"""
        import random
        
        # 找到玩家拥有的所有房产
        player_properties = []
        for cell in self.game_map.cells.values():
            if cell.has_property() and cell.property.owner_id == player.player_id and cell.property.level > 0:
                player_properties.append(cell)
        
        if player_properties:
            # 随机选择一个房产降级
            selected_cell = random.choice(player_properties)
            if selected_cell.property.downgrade():
                self.add_message(f"{player.name}的房产（位置{selected_cell.property.position}）降级了", "warning")
            else:
                self.add_message(f"{player.name}的房产无法降级", "info")
        else:
            self.add_message(f"{player.name}没有可降级的房产", "info")
    
    def open_property_window(self, player: Player, cell):
        """打开房产建设/升级窗口"""
        if not self.property_window:
            self.property_window = PropertyWindow(
                on_close=self.close_property_window,
                on_build=self.build_property,
                on_upgrade=self.upgrade_property
            )
        
        # 确定房产状态
        property_level = 0
        is_owner = False
        
        if cell.has_property():
            property_level = cell.property.level
            is_owner = (cell.property.owner_id == player.player_id)
        
        # 显示窗口
        self.property_window.show(
            self.screen.get_width(),
            self.screen.get_height(),
            player.money,
            property_level,
            is_owner,
            player.position
        )
    
    def close_property_window(self):
        """关闭房产窗口"""
        if self.property_window:
            self.property_window.hide()
        # 恢复自动推进
        print("🔧 房产窗口关闭，恢复自动推进")
        self.phase_auto_advance = True
        self.phase_timer = 1000  # 1秒后自动推进
    
    def build_property(self, position: int):
        """建设房产"""
        from src.models.property import Property
        from src.core.constants import PROPERTY_LEVELS
        
        current_player = self.game_state.get_current_player()
        current_cell = self.game_map.get_cell_by_path_index(position)
        
        if not current_cell:
            self.add_message("无效的位置", "error")
            return
        
        # 检查费用
        build_cost = PROPERTY_LEVELS[1]["cost"]
        if current_player.money < build_cost:
            self.add_message("金钱不足，无法建设", "error")
            return
        
        # 扣除费用
        current_player.money -= build_cost
        
        # 创建或更新房产
        if not current_cell.has_property():
            current_cell.property = Property(position, current_player.player_id, 1)
        else:
            current_cell.property.owner_id = current_player.player_id
            current_cell.property.level = 1
        
        self.add_message(f"{current_player.name}在位置{position}建设了一级房产，花费${build_cost:,}", "success")
        
        # 恢复自动推进
        print("🔧 房产建设完成，恢复自动推进")
        self.phase_auto_advance = True
        self.phase_timer = 1000  # 1秒后自动推进
    
    def upgrade_property(self, position: int):
        """升级房产"""
        from src.core.constants import PROPERTY_LEVELS
        
        current_player = self.game_state.get_current_player()
        current_cell = self.game_map.get_cell_by_path_index(position)
        
        if not current_cell or not current_cell.has_property():
            self.add_message("无效的房产", "error")
            return
        
        property_obj = current_cell.property
        
        # 检查所有权
        if property_obj.owner_id != current_player.player_id:
            self.add_message("这不是您的房产", "error")
            return
        
        # 检查是否可以升级
        if property_obj.level >= 4:
            self.add_message("房产已达到最高等级", "error")
            return
        
        # 检查费用
        upgrade_cost = PROPERTY_LEVELS[property_obj.level + 1]["cost"]
        if current_player.money < upgrade_cost:
            self.add_message("金钱不足，无法升级", "error")
            return
        
        # 扣除费用并升级
        current_player.money -= upgrade_cost
        old_level = property_obj.level
        property_obj.upgrade()
        
        level_names = ["", "一级", "二级", "三级", "四级"]
        self.add_message(f"{current_player.name}将位置{position}的房产从{level_names[old_level]}升级到{level_names[property_obj.level]}，花费${upgrade_cost:,}", "success")
        
        # 恢复自动推进
        print("🔧 房产升级完成，恢复自动推进")
        self.phase_auto_advance = True
        self.phase_timer = 1000  # 1秒后自动推进
    
    def _ai_shop_decision(self, player: Player):
        """AI道具商店决策"""
        import random
        
        # AI有30%概率购买道具
        if random.random() < 0.3 and player.money >= 15000:
            # 随机选择一个道具购买
            available_items = [
                {"id": 1, "name": "路障", "price": 10000},
                {"id": 2, "name": "再装逼让你飞起来!!", "price": 20000},
                {"id": 3, "name": "庇护术", "price": 20000},
                {"id": 4, "name": "六百六十六", "price": 15000},
                {"id": 5, "name": "违规爆建", "price": 25000}
            ]
            
            # 筛选买得起的道具
            affordable_items = [item for item in available_items if player.money >= item["price"]]
            
            if affordable_items:
                selected_item = random.choice(affordable_items)
                player.money -= selected_item["price"]
                
                # 添加道具到背包
                if not hasattr(player, 'inventory'):
                    player.inventory = {}
                player.inventory[selected_item["id"]] = player.inventory.get(selected_item["id"], 0) + 1
                
                self.add_message(f"{player.name}购买了{selected_item['name']}，花费${selected_item['price']:,}", "info")
            else:
                self.add_message(f"{player.name}金钱不足，离开道具商店", "info")
        else:
            self.add_message(f"{player.name}离开道具商店", "info")
        
        # 恢复自动推进
        print("🔧 AI道具商店决策完成，恢复自动推进")
        self.phase_auto_advance = True
        self.phase_timer = 1000  # 1秒后自动推进
    
    def _ai_dice_shop_decision(self, player: Player):
        """AI骰子商店决策"""
        import random
        
        # AI有20%概率购买骰子
        if random.random() < 0.2 and player.money >= 10000:
            dice_products = [
                {"id": 2, "name": "d8骰", "price": 10000, "item_cost": 1},
                {"id": 3, "name": "d12骰", "price": 50000, "item_cost": 1},
                {"id": 4, "name": "双d6骰", "price": 10000, "item_cost": 3},
                {"id": 5, "name": "双d8骰", "price": 50000, "item_cost": 3},
                {"id": 6, "name": "三d6骰", "price": 40000, "item_cost": 4},
                {"id": 7, "name": "d20神力!!", "price": 77777, "item_cost": 7}
            ]
            
            # 计算道具卡数量
            item_count = sum(player.inventory.values()) if hasattr(player, 'inventory') else 0
            
            # 筛选买得起的骰子
            affordable_dice = [
                dice for dice in dice_products 
                if player.money >= dice["price"] and item_count >= dice["item_cost"]
            ]
            
            if affordable_dice:
                selected_dice = random.choice(affordable_dice)
                player.money -= selected_dice["price"]
                
                # 扣除道具卡
                remaining_cost = selected_dice["item_cost"]
                for item_id in list(player.inventory.keys()):
                    if remaining_cost <= 0:
                        break
                    take_count = min(player.inventory[item_id], remaining_cost)
                    player.inventory[item_id] -= take_count
                    remaining_cost -= take_count
                    if player.inventory[item_id] <= 0:
                        del player.inventory[item_id]
                
                # 更换骰子
                dice_type_map = {2: "d8", 3: "d12", 4: "2d6", 5: "2d8", 6: "3d6", 7: "2d20"}
                new_dice = dice_type_map.get(selected_dice["id"], "d6")
                player.dice = new_dice
                player.dice_system.set_current_dice(new_dice)
                
                self.add_message(f"{player.name}购买了{selected_dice['name']}，花费${selected_dice['price']:,}和{selected_dice['item_cost']}张道具卡", "info")
            else:
                self.add_message(f"{player.name}资源不足，离开骰子商店", "info")
        else:
            self.add_message(f"{player.name}离开骰子商店", "info")
        
        # 恢复自动推进
        print("🔧 AI骰子商店决策完成，恢复自动推进")
        self.phase_auto_advance = True
        self.phase_timer = 1000  # 1秒后自动推进
    
    def _ai_bank_decision(self, player: Player):
        """AI银行决策"""
        import random
        
        # AI简单的银行策略：如果身上钱太多就存一部分
        if player.money > 100000:
            # 存入一半的钱
            deposit_amount = player.money // 2
            player.money -= deposit_amount
            if not hasattr(player, 'bank_money'):
                player.bank_money = 0
            player.bank_money += deposit_amount
            self.add_message(f"{player.name}存入${deposit_amount:,}到银行", "info")
        elif hasattr(player, 'bank_money') and player.bank_money > 0 and player.money < 20000:
            # 如果身上钱不够，取出一些
            withdraw_amount = min(player.bank_money, 30000)
            player.bank_money -= withdraw_amount
            player.money += withdraw_amount
            self.add_message(f"{player.name}从银行取出${withdraw_amount:,}", "info")
        else:
            self.add_message(f"{player.name}离开银行", "info")
        
        # 恢复自动推进
        print("🔧 AI银行决策完成，恢复自动推进")
        self.phase_auto_advance = True
        self.phase_timer = 1000  # 1秒后自动推进
    
    def _ai_property_decision(self, player: Player, cell):
        """AI房产决策"""
        import random
        from src.core.constants import PROPERTY_LEVELS
        
        if not cell.has_property() or cell.property.level == 0:
            # 空地，考虑建设
            build_cost = PROPERTY_LEVELS[1]["cost"]
            if player.money >= build_cost * 2:  # AI比较保守，需要双倍资金才建设
                if random.random() < 0.6:  # 60%概率建设
                    self.build_property(player.position)
                    # 恢复自动推进
                    print("🔧 AI房产建设完成，恢复自动推进")
                    self.phase_auto_advance = True
                    self.phase_timer = 1000  # 1秒后自动推进
                    return
        elif cell.property.owner_id == player.player_id and cell.property.level < 4:
            # 自己的房产，考虑升级
            upgrade_cost = PROPERTY_LEVELS[cell.property.level + 1]["cost"]
            if upgrade_cost > 0 and player.money >= upgrade_cost * 2:  # 需要双倍资金
                if random.random() < 0.4:  # 40%概率升级
                    self.upgrade_property(player.position)
                    # 恢复自动推进
                    print("🔧 AI房产升级完成，恢复自动推进")
                    self.phase_auto_advance = True
                    self.phase_timer = 1000  # 1秒后自动推进
                    return
        
        self.add_message(f"{player.name}选择不进行房产操作", "info")
        # 恢复自动推进
        print("🔧 AI房产决策完成，恢复自动推进")
        self.phase_auto_advance = True
        self.phase_timer = 1000  # 1秒后自动推进
    
    def draw_dice_animation(self):
        """绘制骰子动画"""
        if not self.current_dice_animation:
            return
        
        # 获取动画信息
        dice_states = self.current_dice_animation.dice_states
        dice_count = self.current_dice_animation.dice_count
        dice_type = self.current_dice_animation.dice_type
        
        if not dice_states:
            return
        
        # 计算骰子中心位置
        dice_center_x = WINDOW_WIDTH // 2
        dice_center_y = WINDOW_HEIGHT // 2 - 100
        
        # 绘制骰子背景效果（只在投掷阶段）
        if self.current_dice_animation.progress < 0.8:
            intensity = 1.0 - self.current_dice_animation.progress
            self.dice_renderer.draw_rolling_dice_background(
                self.screen, dice_center_x, dice_center_y, 100, intensity
            )
        
        # 绘制所有骰子
        for i, dice_state in enumerate(dice_states):
            # 计算每个骰子的位置
            dice_x = dice_center_x + dice_state['position_x'] + dice_state['offset_x']
            dice_y = dice_center_y + dice_state['position_y'] + dice_state['offset_y']
            
            # 绘制骰子（使用带类型指示器的版本）
            self.dice_renderer.draw_dice_with_type_indicator(
                self.screen,
                int(dice_x),
                int(dice_y),
                dice_state['value'],
                dice_type,
                dice_state['scale']
            )
            
            # 如果动画接近完成，显示数字弹出效果
            if self.current_dice_animation.progress > 0.85:
                alpha = int(255 * (self.current_dice_animation.progress - 0.85) / 0.15)
                popup_y = dice_y - 60
                
                # 为每个骰子创建数字弹出
                font = pygame.font.Font(None, 48)
                text = font.render(str(dice_state['value']), True, (255, 255, 255))
                text_surface = pygame.Surface(text.get_size(), pygame.SRCALPHA)
                text_surface.set_alpha(alpha)
                text_surface.blit(text, (0, 0))
                
                text_rect = text_surface.get_rect(center=(int(dice_x), int(popup_y)))
                self.screen.blit(text_surface, text_rect)
        
        # 如果有多个骰子，在动画后期显示总和
        if dice_count > 1 and self.current_dice_animation.progress > 0.9:
            total_sum = sum(dice['value'] for dice in dice_states)
            alpha = int(255 * (self.current_dice_animation.progress - 0.9) / 0.1)
            
            # 绘制总和
            sum_font = pygame.font.Font(None, 64)
            sum_text = sum_font.render(f"总和: {total_sum}", True, (255, 215, 0))  # 金色
            sum_surface = pygame.Surface(sum_text.get_size(), pygame.SRCALPHA)
            sum_surface.set_alpha(alpha)
            sum_surface.blit(sum_text, (0, 0))
            
            sum_rect = sum_surface.get_rect(center=(dice_center_x, dice_center_y + 120))
            self.screen.blit(sum_surface, sum_rect)
    
    def open_multiplayer(self):
        """打开联机模式"""
        print("🔗 尝试打开联机模式...")
        try:
            # 优先使用增强版联机窗口
            from src.ui.enhanced_multiplayer_window import EnhancedMultiplayerWindow
            print("✅ 成功导入增强版 EnhancedMultiplayerWindow")
            
            # 创建并运行联机窗口
            multiplayer_window = EnhancedMultiplayerWindow()
            print("✅ 成功创建 EnhancedMultiplayerWindow 实例")
            
            multiplayer_window.run()
            print("✅ 增强版联机窗口运行完成")
            
        except ImportError as e:
            print(f"❌ 导入错误: {e}")
            self.add_message(f"联机模块导入失败，使用备用界面", "warning")
            self._open_enhanced_multiplayer()
        except Exception as e:
            print(f"❌ 运行错误: {e}")
            self.add_message(f"打开联机模式失败: {e}", "error")
            # 提供备用选项
            self._open_enhanced_multiplayer()
    
    def _open_enhanced_multiplayer(self):
        """打开增强版联机界面"""
        print("🚀 启动增强版联机界面...")
        
        # 创建联机界面
        screen = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption("大富翁 - 联机模式")
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 36)
        button_font = pygame.font.Font(None, 24)
        
        # 界面状态
        current_page = "main"  # main, server_setup, client_setup
        input_text = ""
        input_active = False
        input_prompt = ""
        messages = []
        
        def add_message(text, msg_type="info"):
            messages.append({
                "text": text,
                "type": msg_type,
                "time": pygame.time.get_ticks()
            })
            if len(messages) > 5:
                messages.pop(0)
            print(f"[{msg_type.upper()}] {text}")
        
        # 按钮定义
        buttons = {}
        
        def init_main_page():
            nonlocal buttons
            buttons = {
                "start_server": pygame.Rect(300, 250, 200, 50),
                "start_client": pygame.Rect(300, 320, 200, 50),
                "test_connection": pygame.Rect(300, 390, 200, 50),
                "back": pygame.Rect(300, 460, 200, 50)
            }
        
        def init_server_page():
            nonlocal buttons
            buttons = {
                "launch_server": pygame.Rect(300, 250, 200, 50),
                "test_server": pygame.Rect(300, 320, 200, 50),
                "back": pygame.Rect(300, 390, 200, 50)
            }
        
        def init_client_page():
            nonlocal buttons
            buttons = {
                "launch_client": pygame.Rect(300, 250, 200, 50),
                "test_client": pygame.Rect(300, 320, 200, 50),
                "back": pygame.Rect(300, 390, 200, 50)
            }
        
        # 初始化主页面
        init_main_page()
        
        running = True
        while running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if current_page == "main":
                            running = False
                        else:
                            current_page = "main"
                            init_main_page()
                    
                    elif input_active:
                        if event.key == pygame.K_RETURN:
                            if input_text.strip():
                                # 处理输入
                                if input_prompt == "服务器地址":
                                    add_message(f"尝试连接到: {input_text}", "info")
                                elif input_prompt == "玩家名称":
                                    add_message(f"玩家名称: {input_text}", "info")
                                input_active = False
                                input_text = ""
                                input_prompt = ""
                        elif event.key == pygame.K_BACKSPACE:
                            input_text = input_text[:-1]
                        else:
                            if len(input_text) < 50:
                                input_text += event.unicode
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # 检查按钮点击
                    for button_name, button_rect in buttons.items():
                        if button_rect.collidepoint(mouse_pos):
                            # 处理按钮点击
                            if button_name == "start_server":
                                current_page = "server_setup"
                                init_server_page()
                                add_message("进入服务器设置", "info")
                            
                            elif button_name == "start_client":
                                current_page = "client_setup"
                                init_client_page()
                                add_message("进入客户端设置", "info")
                            
                            elif button_name == "test_connection":
                                add_message("测试网络连接...", "info")
                                try:
                                    import socket
                                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                    sock.settimeout(2)
                                    result = sock.connect_ex(('localhost', 8765))
                                    sock.close()
                                    if result == 0:
                                        add_message("✅ 本地服务器可连接", "success")
                                    else:
                                        add_message("❌ 本地服务器不可达", "error")
                                except Exception as e:
                                    add_message(f"❌ 网络测试失败: {e}", "error")
                            
                            elif button_name == "launch_server":
                                add_message("正在启动快速服务器...", "info")
                                try:
                                    import subprocess
                                    import os
                                    import sys
                                    
                                    # 优先使用房间服务器批处理脚本（确保虚拟环境）
                                    batch_script = os.path.join(os.getcwd(), "start_room_server.bat")
                                    if not os.path.exists(batch_script):
                                        batch_script = os.path.join(os.getcwd(), "start_server_venv.bat")
                                    
                                    if os.path.exists(batch_script) and os.name == 'nt':
                                        # Windows系统使用批处理脚本
                                        subprocess.Popen([batch_script], 
                                                       creationflags=subprocess.CREATE_NEW_CONSOLE)
                                        add_message("✅ 服务器启动脚本已执行（虚拟环境）", "success")
                                    else:
                                        # 获取当前Python解释器路径（确保使用虚拟环境）
                                        python_exe = sys.executable
                                        
                                        # 检查是否在虚拟环境中
                                        venv_check = "DaFuWeng" in python_exe or "venv" in python_exe.lower()
                                        if not venv_check:
                                            add_message("⚠️ 当前不在虚拟环境中，可能缺少依赖", "warning")
                                        
                                        # 优先使用房间管理服务器
                                        server_path = os.path.join(os.getcwd(), "room_server.py")
                                        if os.path.exists(server_path):
                                            subprocess.Popen([
                                                python_exe, server_path
                                            ], creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
                                            add_message("✅ 房间管理服务器启动成功！", "success")
                                        else:
                                            # 备用：使用快速服务器
                                            backup_server = os.path.join(os.getcwd(), "quick_server.py")
                                            if os.path.exists(backup_server):
                                                subprocess.Popen([
                                                    python_exe, backup_server
                                                ], creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
                                                add_message("✅ 备用服务器启动成功！", "success")
                                            else:
                                                add_message("❌ 找不到任何服务器启动脚本", "error")
                                except Exception as e:
                                    add_message(f"❌ 启动服务器失败: {e}", "error")
                            
                            elif button_name == "test_server":
                                add_message("测试服务器状态...", "info")
                                # 这里可以添加服务器状态检查
                                add_message("服务器测试功能开发中...", "warning")
                            
                            elif button_name == "launch_client":
                                add_message("正在启动测试客户端...", "info")
                                try:
                                    import subprocess
                                    import os
                                    import sys
                                    
                                    # 获取当前Python解释器路径（确保使用虚拟环境）
                                    python_exe = sys.executable
                                    
                                    # 启动测试客户端
                                    client_path = os.path.join(os.getcwd(), "test_client.py")
                                    if os.path.exists(client_path):
                                        subprocess.Popen([
                                            python_exe, client_path
                                        ], creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
                                        add_message("✅ 测试客户端启动命令已执行", "success")
                                    else:
                                        add_message("❌ 找不到测试客户端脚本", "error")
                                except Exception as e:
                                    add_message(f"❌ 启动客户端失败: {e}", "error")
                            
                            elif button_name == "test_client":
                                input_prompt = "服务器地址"
                                input_text = "localhost:8765"
                                input_active = True
                                add_message("请输入服务器地址...", "info")
                            
                            elif button_name == "back":
                                if current_page in ["server_setup", "client_setup"]:
                                    current_page = "main"
                                    init_main_page()
                                else:
                                    running = False
            
            # 绘制界面
            screen.fill((240, 248, 255))
            
            # 绘制标题
            if current_page == "main":
                title = font.render("联机模式控制中心", True, (0, 0, 0))
                title_rect = title.get_rect(center=(512, 100))
                screen.blit(title, title_rect)
                
                # 绘制说明
                instructions = [
                    "选择启动模式:",
                    "",
                    "• 启动服务器 - 创建游戏服务器",
                    "• 启动客户端 - 连接到游戏服务器",
                    "• 测试连接 - 检查网络状态"
                ]
                
                for i, instruction in enumerate(instructions):
                    color = (100, 100, 100) if instruction.startswith("•") else (50, 50, 50)
                    text = button_font.render(instruction, True, color)
                    text_rect = text.get_rect(center=(512, 160 + i * 25))
                    screen.blit(text, text_rect)
            
            elif current_page == "server_setup":
                title = font.render("服务器设置", True, (0, 0, 0))
                title_rect = title.get_rect(center=(512, 100))
                screen.blit(title, title_rect)
                
                info_text = button_font.render("服务器将在 localhost:8765 启动", True, (100, 100, 100))
                info_rect = info_text.get_rect(center=(512, 180))
                screen.blit(info_text, info_rect)
            
            elif current_page == "client_setup":
                title = font.render("客户端设置", True, (0, 0, 0))
                title_rect = title.get_rect(center=(512, 100))
                screen.blit(title, title_rect)
                
                info_text = button_font.render("启动测试客户端连接到服务器", True, (100, 100, 100))
                info_rect = info_text.get_rect(center=(512, 180))
                screen.blit(info_text, info_rect)
            
            # 绘制按钮
            for button_name, button_rect in buttons.items():
                # 按钮背景
                if button_name == "back":
                    color = (220, 20, 60)
                elif button_name in ["launch_server", "launch_client"]:
                    color = (34, 139, 34)
                else:
                    color = (70, 130, 180)
                
                pygame.draw.rect(screen, color, button_rect)
                pygame.draw.rect(screen, (0, 0, 0), button_rect, 2)
                
                # 按钮文字
                button_texts = {
                    "start_server": "启动服务器",
                    "start_client": "启动客户端",
                    "test_connection": "测试连接",
                    "launch_server": "启动服务器",
                    "test_server": "测试服务器",
                    "launch_client": "启动客户端",
                    "test_client": "测试连接",
                    "back": "返回"
                }
                
                text = button_font.render(button_texts.get(button_name, button_name), True, (255, 255, 255))
                text_rect = text.get_rect(center=button_rect.center)
                screen.blit(text, text_rect)
            
            # 绘制输入对话框
            if input_active:
                # 背景
                dialog_rect = pygame.Rect(200, 300, 400, 120)
                pygame.draw.rect(screen, (255, 255, 255), dialog_rect)
                pygame.draw.rect(screen, (0, 0, 0), dialog_rect, 2)
                
                # 提示文本
                prompt_text = button_font.render(input_prompt + ":", True, (0, 0, 0))
                screen.blit(prompt_text, (dialog_rect.x + 10, dialog_rect.y + 10))
                
                # 输入框
                input_rect = pygame.Rect(dialog_rect.x + 10, dialog_rect.y + 40, dialog_rect.width - 20, 30)
                pygame.draw.rect(screen, (248, 248, 255), input_rect)
                pygame.draw.rect(screen, (128, 128, 128), input_rect, 2)
                
                # 输入文本
                input_surface = button_font.render(input_text, True, (0, 0, 0))
                screen.blit(input_surface, (input_rect.x + 5, input_rect.y + 5))
                
                # 提示
                hint_text = button_font.render("按 Enter 确认，ESC 取消", True, (100, 100, 100))
                screen.blit(hint_text, (dialog_rect.x + 10, dialog_rect.y + 80))
            
            # 绘制消息
            if messages:
                message_y = 550
                for message in messages[-3:]:  # 只显示最后3条消息
                    color_map = {
                        "info": (0, 0, 0),
                        "success": (34, 139, 34),
                        "error": (220, 20, 60),
                        "warning": (255, 165, 0)
                    }
                    color = color_map.get(message["type"], (0, 0, 0))
                    text = button_font.render(message["text"], True, color)
                    text_rect = text.get_rect(center=(512, message_y))
                    screen.blit(text, text_rect)
                    message_y += 25
            
            # 绘制底部提示
            hint_text = button_font.render("按 ESC 键返回主菜单", True, (150, 150, 150))
            hint_rect = hint_text.get_rect(center=(512, 720))
            screen.blit(hint_text, hint_rect)
            
            pygame.display.flip()
            clock.tick(60)
        
        print("🔚 联机界面已关闭")

    def init_multiplayer_game(self, game_data: dict):
        """初始化多人游戏"""
        print(f"🎮 初始化多人游戏: {game_data}")
        
        try:
            # 设置多人游戏标识
            self.is_multiplayer = True
            self.multiplayer_data = game_data
            
            # 加载地图
            map_file = game_data.get('map_file', '1.json')
            print(f"🗺️ 加载地图文件: {map_file}")
            
            # 使用地图数据管理器加载地图
            from src.systems.map_data_manager import MapDataManager
            map_manager = MapDataManager()
            
            # 尝试加载地图
            map_loaded = False
            for map_path in [map_file, f"data/{map_file}", f"{map_file}"]:
                try:
                    self.game_map = map_manager.load_map('json', map_path)
                    if self.game_map:
                        print(f"✅ 地图加载成功: {map_path}")
                        map_loaded = True
                        break
                except Exception as e:
                    print(f"⚠️ 尝试加载地图失败 {map_path}: {e}")
                    continue
            
            if not map_loaded:
                print(f"❌ 地图加载失败，使用默认地图")
                self.add_message("地图加载失败，使用默认地图", "warning")
                # 创建默认地图
                self.game_map = self.create_sample_map()
                if not self.game_map:
                    print(f"❌ 默认地图创建失败")
                    return False
            
            # 创建多人游戏玩家
            players_data = game_data.get('players', [])
            print(f"👥 创建玩家: {len(players_data)}人")
            
            players = []
            for i, player_data in enumerate(players_data):
                from src.models.player import Player
                
                player_id = i + 1
                player_name = player_data.get('name', f'玩家{player_id}')
                client_id = player_data.get('client_id', '')
                
                # 判断是否是AI玩家
                is_ai = 'ai_' in client_id.lower() or 'ai玩家' in player_name
                
                player = Player(player_id, player_name, is_ai=is_ai)
                player.client_id = client_id  # 添加客户端ID用于网络同步
                players.append(player)
                
                print(f"  - 玩家{player_id}: {player_name} ({'AI' if is_ai else '人类'})")
            
            if len(players) < 2:
                print(f"❌ 玩家数量不足: {len(players)}")
                self.add_message("玩家数量不足，无法开始游戏", "error")
                return False
            
            # 初始化游戏状态
            print("🎲 初始化游戏状态...")
            if self.game_state.initialize_game(players, self.game_map):
                print("✅ 游戏状态初始化成功")
                
                # 设置PlayerManager
                self.player_manager.set_players(players)
                self.player_manager.set_game_map(self.game_map)
                
                # 确保清除任何残留的主菜单元素
                print("🧹 清理界面元素...")
                self.buttons.clear()
                self.panels.clear()
                self.dialogs.clear()
                self.phase_buttons.clear()
                
                # 初始化游戏界面
                print("🖼️ 初始化游戏界面...")
                self.init_game_scene()
                self.add_message("多人游戏开始！", "success")
                
                # 开始第一个回合
                print("🎯 开始游戏回合...")
                self.start_turn_phase()
                
                return True
            else:
                print("❌ 游戏状态初始化失败")
                self.add_message("游戏初始化失败", "error")
                return False
        
        except Exception as e:
            print(f"❌ 多人游戏初始化异常: {e}")
            import traceback
            traceback.print_exc()
            self.add_message(f"游戏初始化失败: {e}", "error")
            return False
    
    def open_load_dialog(self):
        """打开加载存档对话框"""
        try:
            # 创建存档管理窗口
            if not self.save_load_window:
                self.save_load_window = SaveLoadWindow(self.screen)
            
            # 显示加载对话框
            self.save_load_window.show_load_dialog(self.on_game_loaded)
            
        except Exception as e:
            self.add_message(f"打开存档对话框失败: {e}", "error")
            import traceback
            traceback.print_exc()
    
    def open_save_dialog(self):
        """打开保存存档对话框"""
        try:
            # 检查是否有游戏状态可以保存
            if not self.game_state or not self.game_state.players:
                self.add_message("没有可保存的游戏状态", "warning")
                return
            
            # 创建存档管理窗口
            if not self.save_load_window:
                self.save_load_window = SaveLoadWindow(self.screen)
            
            # 显示保存对话框
            self.save_load_window.show_save_dialog(self.game_state, self.on_game_saved)
            
        except Exception as e:
            self.add_message(f"打开保存对话框失败: {e}", "error")
            import traceback
            traceback.print_exc()
    
    def on_game_loaded(self, load_result: Dict[str, Any]):
        """处理游戏加载完成"""
        try:
            if load_result["success"]:
                # 获取加载的游戏状态
                loaded_game_state = load_result["game_state"]
                metadata = load_result["metadata"]
                save_name = load_result["save_name"]
                
                # 恢复游戏状态
                self.game_state = loaded_game_state
                
                # 恢复地图
                if self.game_state.map:
                    self.game_map = self.game_state.map
                else:
                    self.add_message("存档中没有地图数据，使用默认地图", "warning")
                    self.create_sample_map()
                
                # 设置玩家管理器
                self.player_manager.set_players(self.game_state.players)
                self.player_manager.set_game_map(self.game_map)
                
                # 更新事件管理器
                self.event_manager = EventManager(self.game_map.width * self.game_map.height)
                
                # 切换到游戏场景
                self.init_game_scene()
                
                # 添加成功消息
                player_name = metadata.get("current_player", "未知")
                turn_count = metadata.get("turn_count", 0)
                self.add_message(f"存档 '{save_name}' 加载成功！当前玩家: {player_name}, 回合: {turn_count}", "success")
                
                # 开始回合
                self.start_turn_phase()
                
            else:
                self.add_message(f"加载失败: {load_result['error']}", "error")
                
        except Exception as e:
            self.add_message(f"游戏加载异常: {e}", "error")
            import traceback
            traceback.print_exc()
    
    def on_game_saved(self, save_result: Dict[str, Any]):
        """处理游戏保存完成"""
        try:
            if save_result["success"]:
                save_name = save_result["save_name"]
                file_size = save_result.get("size", 0) // 1024  # KB
                self.add_message(f"游戏已保存为 '{save_name}' ({file_size}KB)", "success")
            else:
                self.add_message(f"保存失败: {save_result['error']}", "error")
                
        except Exception as e:
            self.add_message(f"保存处理异常: {e}", "error")
    
    def quick_save(self):
        """快速保存"""
        try:
            if not self.game_state or not self.game_state.players:
                self.add_message("没有可保存的游戏状态", "warning")
                return
            
            # 执行快速保存
            result = self.save_system.quick_save(self.game_state)
            
            if result["success"]:
                save_name = result["save_name"]
                file_size = result.get("size", 0) // 1024  # KB
                self.add_message(f"快速保存成功: {save_name} ({file_size}KB)", "success")
            else:
                self.add_message(f"快速保存失败: {result['error']}", "error")
                
        except Exception as e:
            self.add_message(f"快速保存异常: {e}", "error")
            import traceback
            traceback.print_exc()
    
    def auto_save_check(self):
        """检查自动保存"""
        try:
            if self.game_state and self.game_state.players:
                result = self.save_system.auto_save(self.game_state)
                if result["success"]:
                    save_name = result["save_name"]
                    self.add_message(f"自动保存: {save_name}", "info")
                    
        except Exception as e:
            # 自动保存失败不显示错误消息，只记录日志
            print(f"自动保存失败: {e}")
    
    def close_save_load_window(self):
        """关闭存档管理窗口"""
        if self.save_load_window:
            self.save_load_window.close()
            self.save_load_window = None