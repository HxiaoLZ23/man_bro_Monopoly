"""
地图编辑器
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Tuple, Optional
from src.models.map import Map, Cell
from src.systems.map_data_manager import MapDataManager
from src.core.constants import CELL_TYPES, CELL_COLORS


class MapEditor:
    """地图编辑器"""
    
    def __init__(self):
        """初始化地图编辑器"""
        self.map_data_manager = MapDataManager()
        self.current_map = None
        self.editor_mode = "view"  # view, edit, path
        self.gui_mode = False  # 是否使用图形界面
    
    def create_new_map(self, width: int = 20, height: int = 20) -> Map:
        """
        创建新地图
        
        Args:
            width: 地图宽度
            height: 地图高度
            
        Returns:
            Map: 新创建的地图对象
        """
        self.current_map = Map(width, height)
        print(f"创建了新地图: {width}x{height}")
        return self.current_map
    
    def load_map(self, file_path: str, format_type: str = None) -> bool:
        """
        加载地图
        
        Args:
            file_path: 文件路径
            format_type: 文件格式，如果为None则自动检测
            
        Returns:
            bool: 加载是否成功
        """
        if format_type is None:
            # 根据文件扩展名自动检测格式
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.json':
                format_type = 'json'
            elif ext == '.xlsx':
                format_type = 'xlsx'
            elif ext == '.db':
                format_type = 'db'
            else:
                print("无法自动检测文件格式，请指定format_type")
                return False
        
        self.current_map = self.map_data_manager.load_map(format_type, file_path)
        if self.current_map:
            print(f"成功加载地图: {file_path}")
            return True
        else:
            print(f"加载地图失败: {file_path}")
            return False
    
    def save_map(self, file_path: str, format_type: str = None) -> bool:
        """
        保存地图
        
        Args:
            file_path: 文件路径
            format_type: 文件格式，如果为None则自动检测
            
        Returns:
            bool: 保存是否成功
        """
        if not self.current_map:
            print("没有可保存的地图")
            return False
        
        if format_type is None:
            # 根据文件扩展名自动检测格式
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.json':
                format_type = 'json'
            elif ext == '.xlsx':
                format_type = 'xlsx'
            elif ext == '.db':
                format_type = 'db'
            else:
                print("无法自动检测文件格式，请指定format_type")
                return False
        
        success = self.map_data_manager.save_map(self.current_map, format_type, file_path)
        if success:
            print(f"成功保存地图: {file_path}")
        else:
            print(f"保存地图失败: {file_path}")
        return success
    
    def display_map(self, show_coordinates: bool = True) -> None:
        """
        显示地图
        
        Args:
            show_coordinates: 是否显示坐标
        """
        if not self.current_map:
            print("没有可显示的地图")
            return
        
        print(f"\n地图大小: {self.current_map.width}x{self.current_map.height}")
        print(f"路径长度: {self.current_map.path_length}")
        print()
        
        # 显示坐标行
        if show_coordinates:
            print("   ", end="")
            for x in range(self.current_map.width):
                print(f"{x:2}", end="")
            print()
        
        # 显示地图
        for y in range(self.current_map.height):
            if show_coordinates:
                print(f"{y:2} ", end="")
            
            for x in range(self.current_map.width):
                cell = self.current_map.get_cell_at((x, y))
                if cell:
                    # 根据格子类型显示不同字符
                    char = self._get_cell_char(cell)
                    print(char, end=" ")
                else:
                    print("?", end=" ")
            print()
        
        # 显示图例
        self._display_legend()
    
    def _get_cell_char(self, cell: Cell) -> str:
        """
        获取格子的显示字符
        
        Args:
            cell: 格子对象
            
        Returns:
            str: 显示字符
        """
        char_map = {
            "empty": ".",
            "wall": "#",
            "void": " ",
            "bank": "B",
            "shop": "S",
            "dice_shop": "D",
            "jail": "J",
            "luck": "L",
            "bad_luck": "X"
        }
        
        char = char_map.get(cell.cell_type, "?")
        
        # 如果有路障，用大写字母
        if cell.roadblock:
            char = char.upper()
        
        # 如果有房产，添加数字
        if cell.property and cell.property.level > 0:
            char = str(cell.property.level)
        
        # 如果是岔路口，添加星号
        if cell.is_junction:
            char = "*"
        
        return char
    
    def _display_legend(self) -> None:
        """显示图例"""
        print("\n图例:")
        print("  . - 空地")
        print("  # - 墙")
        print("    - 空格")
        print("  B - 银行")
        print("  S - 道具商店")
        print("  D - 骰子商店")
        print("  J - 监狱")
        print("  L - 好运格")
        print("  X - 厄运格")
        print("  * - 岔路口")
        print("  大写字母 - 有路障")
        print("  数字 - 房产等级")
    
    def set_cell_type(self, x: int, y: int, cell_type: str) -> bool:
        """
        设置格子类型
        
        Args:
            x: X坐标
            y: Y坐标
            cell_type: 格子类型
            
        Returns:
            bool: 设置是否成功
        """
        if not self.current_map:
            print("没有可编辑的地图")
            return False
        
        if cell_type not in CELL_TYPES.values():
            print(f"无效的格子类型: {cell_type}")
            print(f"有效的类型: {list(CELL_TYPES.values())}")
            return False
        
        success = self.current_map.set_cell_type((x, y), cell_type)
        if success:
            print(f"设置格子 ({x}, {y}) 为 {cell_type}")
        else:
            print(f"设置格子失败: ({x}, {y})")
        return success
    
    def toggle_roadblock(self, x: int, y: int) -> bool:
        """
        切换路障状态
        
        Args:
            x: X坐标
            y: Y坐标
            
        Returns:
            bool: 操作是否成功
        """
        if not self.current_map:
            print("没有可编辑的地图")
            return False
        
        cell = self.current_map.get_cell_at((x, y))
        if not cell:
            print(f"无效的坐标: ({x}, {y})")
            return False
        
        if cell.roadblock:
            self.current_map.remove_roadblock((x, y))
            print(f"移除路障: ({x}, {y})")
        else:
            self.current_map.place_roadblock((x, y))
            print(f"放置路障: ({x}, {y})")
        
        return True
    
    def set_property(self, x: int, y: int, level: int, owner_id: int = None) -> bool:
        """
        设置房产
        
        Args:
            x: X坐标
            y: Y坐标
            level: 房产等级
            owner_id: 所有者ID
            
        Returns:
            bool: 设置是否成功
        """
        if not self.current_map:
            print("没有可编辑的地图")
            return False
        
        cell = self.current_map.get_cell_at((x, y))
        if not cell:
            print(f"无效的坐标: ({x}, {y})")
            return False
        
        if level < 0 or level > 4:
            print(f"无效的房产等级: {level} (0-4)")
            return False
        
        from src.models.property import Property
        property_obj = Property(x * self.current_map.width + y, owner_id, level)
        cell.set_property(property_obj)
        
        print(f"设置房产: ({x}, {y}) 等级{level}")
        return True
    
    def validate_current_map(self) -> None:
        """验证当前地图"""
        if not self.current_map:
            print("没有可验证的地图")
            return
        
        result = self.map_data_manager.validate_map(self.current_map)
        
        print("\n地图验证结果:")
        
        if result["errors"]:
            print("错误:")
            for error in result["errors"]:
                print(f"  ✗ {error}")
        else:
            print("  ✓ 没有错误")
        
        if result["warnings"]:
            print("警告:")
            for warning in result["warnings"]:
                print(f"  ⚠ {warning}")
        else:
            print("  ✓ 没有警告")
    
    def add_path_connection(self, from_index: int, to_index: int) -> bool:
        """
        添加路径连接
        
        Args:
            from_index: 起始路径索引
            to_index: 目标路径索引
            
        Returns:
            bool: 操作是否成功
        """
        if not self.current_map:
            print("没有可编辑的地图")
            return False
        
        success = self.current_map.add_path_connection(from_index, to_index)
        if success:
            print(f"成功添加路径连接: {from_index} -> {to_index}")
        else:
            print(f"添加路径连接失败: {from_index} -> {to_index}")
        return success
    
    def remove_path_connection(self, from_index: int, to_index: int) -> bool:
        """
        移除路径连接
        
        Args:
            from_index: 起始路径索引
            to_index: 目标路径索引
            
        Returns:
            bool: 操作是否成功
        """
        if not self.current_map:
            print("没有可编辑的地图")
            return False
        
        success = self.current_map.remove_path_connection(from_index, to_index)
        if success:
            print(f"成功移除路径连接: {from_index} -> {to_index}")
        else:
            print(f"移除路径连接失败: {from_index} -> {to_index}")
        return success
    
    def display_path_info(self) -> None:
        """显示路径信息"""
        if not self.current_map:
            print("没有可显示的地图")
            return
        
        print(f"\n路径信息:")
        print(f"路径总长度: {self.current_map.path_length}")
        print(f"岔路口数量: {len(self.current_map.junctions)}")
        
        if self.current_map.junctions:
            print("岔路口位置:")
            for junction_index in sorted(self.current_map.junctions):
                pos = self.current_map.get_position_by_path_index(junction_index)
                cell = self.current_map.get_cell_by_path_index(junction_index)
                connections = len(cell.connections) if cell else 0
                print(f"  索引 {junction_index}: 位置 {pos}, {connections} 个连接")
        
        print("\n路径连接:")
        for i, (x, y) in enumerate(self.current_map.path):
            cell = self.current_map.get_cell_by_path_index(i)
            if cell:
                connections = list(cell.connections)
                print(f"  索引 {i}: 位置 ({x}, {y}), 连接: {connections}")
    
    def test_path_movement(self, start_index: int, steps: int, direction_choices: List[int] = None) -> None:
        """
        测试路径移动
        
        Args:
            start_index: 起始路径索引
            steps: 移动步数
            direction_choices: 方向选择列表
        """
        if not self.current_map:
            print("没有可测试的地图")
            return
        
        final_index, path_taken = self.current_map.move_along_path(start_index, steps, direction_choices)
        
        print(f"\n路径移动测试:")
        print(f"起始位置: {start_index}")
        print(f"移动步数: {steps}")
        print(f"方向选择: {direction_choices}")
        print(f"最终位置: {final_index}")
        print(f"移动路径: {path_taken}")
        
        # 显示移动轨迹
        print("移动轨迹:")
        for i, path_index in enumerate(path_taken):
            pos = self.current_map.get_position_by_path_index(path_index)
            cell = self.current_map.get_cell_by_path_index(path_index)
            cell_name = cell.get_name() if cell else "未知"
            print(f"  步骤 {i}: 索引 {path_index}, 位置 {pos}, 格子类型: {cell_name}")
    
    def get_available_directions(self, path_index: int) -> List[int]:
        """
        获取可用方向
        
        Args:
            path_index: 路径索引
            
        Returns:
            List[int]: 可用方向列表
        """
        if not self.current_map:
            return []
        
        return self.current_map.get_available_directions(path_index)
    
    def run_interactive_editor(self) -> None:
        """运行交互式编辑器"""
        print("=== 大富翁地图编辑器 ===")
        print("命令:")
        print("  new <width> <height> - 创建新地图")
        print("  load <file> - 加载地图")
        print("  save <file> - 保存地图")
        print("  display - 显示地图")
        print("  set <x> <y> <type> - 设置格子类型")
        print("  roadblock <x> <y> - 切换路障")
        print("  property <x> <y> <level> [owner] - 设置房产")
        print("  path - 显示路径信息")
        print("  connect <from> <to> - 添加路径连接")
        print("  disconnect <from> <to> - 移除路径连接")
        print("  test <start> <steps> [directions...] - 测试路径移动")
        print("  directions <index> - 显示可用方向")
        print("  validate - 验证地图")
        print("  gui - 启动图形界面")
        print("  quit - 退出")
        print()
        
        while True:
            try:
                command = input("编辑器> ").strip().split()
                if not command:
                    continue
                
                cmd = command[0].lower()
                
                if cmd == "quit":
                    break
                elif cmd == "gui":
                    self.run_gui_editor()
                elif cmd == "new":
                    if len(command) >= 3:
                        width = int(command[1])
                        height = int(command[2])
                        self.create_new_map(width, height)
                    else:
                        print("用法: new <width> <height>")
                
                elif cmd == "load":
                    if len(command) >= 2:
                        file_path = command[1]
                        self.load_map(file_path)
                    else:
                        print("用法: load <file>")
                
                elif cmd == "save":
                    if len(command) >= 2:
                        file_path = command[1]
                        self.save_map(file_path)
                    else:
                        print("用法: save <file>")
                
                elif cmd == "display":
                    self.display_map()
                
                elif cmd == "set":
                    if len(command) >= 4:
                        x = int(command[1])
                        y = int(command[2])
                        cell_type = command[3]
                        self.set_cell_type(x, y, cell_type)
                    else:
                        print("用法: set <x> <y> <type>")
                
                elif cmd == "roadblock":
                    if len(command) >= 3:
                        x = int(command[1])
                        y = int(command[2])
                        self.toggle_roadblock(x, y)
                    else:
                        print("用法: roadblock <x> <y>")
                
                elif cmd == "property":
                    if len(command) >= 4:
                        x = int(command[1])
                        y = int(command[2])
                        level = int(command[3])
                        owner_id = int(command[4]) if len(command) > 4 else None
                        self.set_property(x, y, level, owner_id)
                    else:
                        print("用法: property <x> <y> <level> [owner]")
                
                elif cmd == "path":
                    self.display_path_info()
                
                elif cmd == "connect":
                    if len(command) >= 3:
                        from_index = int(command[1])
                        to_index = int(command[2])
                        self.add_path_connection(from_index, to_index)
                    else:
                        print("用法: connect <from> <to>")
                
                elif cmd == "disconnect":
                    if len(command) >= 3:
                        from_index = int(command[1])
                        to_index = int(command[2])
                        self.remove_path_connection(from_index, to_index)
                    else:
                        print("用法: disconnect <from> <to>")
                
                elif cmd == "test":
                    if len(command) >= 3:
                        start_index = int(command[1])
                        steps = int(command[2])
                        direction_choices = [int(x) for x in command[3:]] if len(command) > 3 else None
                        self.test_path_movement(start_index, steps, direction_choices)
                    else:
                        print("用法: test <start> <steps> [directions...]")
                
                elif cmd == "directions":
                    if len(command) >= 2:
                        path_index = int(command[1])
                        directions = self.get_available_directions(path_index)
                        print(f"位置 {path_index} 的可用方向: {directions}")
                    else:
                        print("用法: directions <index>")
                
                elif cmd == "validate":
                    self.validate_current_map()
                
                else:
                    print(f"未知命令: {cmd}")
                    
            except ValueError as e:
                print(f"参数错误: {e}")
            except Exception as e:
                print(f"错误: {e}")
    
    def run_gui_editor(self) -> None:
        """运行图形化编辑器"""
        self.gui_mode = True
        gui = MapEditorGUI(self)
        gui.run()
    
    def toggle_junction(self, x: int, y: int) -> bool:
        """
        切换岔路点状态
        
        Args:
            x: X坐标
            y: Y坐标
            
        Returns:
            bool: 操作是否成功
        """
        if not self.current_map:
            print("没有可编辑的地图")
            return False
        
        cell = self.current_map.get_cell_at((x, y))
        if not cell:
            print(f"无效的坐标: ({x}, {y})")
            return False
        
        # 获取路径索引
        path_index = None
        for i, (px, py) in enumerate(self.current_map.path):
            if px == x and py == y:
                path_index = i
                break
        
        if path_index is None:
            print(f"位置 ({x}, {y}) 不在路径上，无法设置为岔路点")
            return False
        
        # 切换岔路状态
        if cell.is_junction:
            # 移除岔路点
            cell.is_junction = False
            if path_index in self.current_map.junctions:
                self.current_map.junctions.remove(path_index)
            print(f"移除岔路点: ({x}, {y})")
        else:
            # 设置为岔路点
            cell.is_junction = True
            if path_index not in self.current_map.junctions:
                self.current_map.junctions.add(path_index)
            print(f"设置岔路点: ({x}, {y})")
        
        return True
    
    def add_junction_connection(self, from_x: int, from_y: int, to_x: int, to_y: int) -> bool:
        """
        为岔路点添加连接
        
        Args:
            from_x: 起始X坐标
            from_y: 起始Y坐标
            to_x: 目标X坐标
            to_y: 目标Y坐标
            
        Returns:
            bool: 操作是否成功
        """
        if not self.current_map:
            print("没有可编辑的地图")
            return False
        
        # 获取路径索引
        from_index = None
        to_index = None
        
        for i, (px, py) in enumerate(self.current_map.path):
            if px == from_x and py == from_y:
                from_index = i
            if px == to_x and py == to_y:
                to_index = i
        
        if from_index is None or to_index is None:
            print(f"坐标不在路径上: ({from_x}, {from_y}) -> ({to_x}, {to_y})")
            return False
        
        return self.add_path_connection(from_index, to_index)


class MapEditorGUI:
    """图形化地图编辑器"""
    
    def __init__(self, editor: MapEditor):
        """初始化图形化编辑器"""
        self.editor = editor
        self.root = tk.Tk()
        self.root.title("大富翁地图编辑器")
        self.root.geometry("1200x800")
        
        # 编辑器状态
        self.current_tool = "select"
        self.selected_cell = None
        self.cell_size = 30
        self.zoom_level = 1.0
        
        # 创建界面
        self.setup_ui()
        
        # 绑定快捷键
        self.bind_shortcuts()
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建工具栏
        self.create_toolbar(main_frame)
        
        # 创建地图画布
        self.create_canvas(main_frame)
        
        # 创建属性面板
        self.create_property_panel(main_frame)
        
        # 创建状态栏
        self.create_status_bar()
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="新建地图", command=self.new_map, accelerator="Ctrl+N")
        file_menu.add_command(label="打开地图", command=self.open_map, accelerator="Ctrl+O")
        file_menu.add_command(label="保存地图", command=self.save_map, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="撤销", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="重做", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="验证地图", command=self.validate_map)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        
        # 视图菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="放大", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="缩小", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="重置缩放", command=self.zoom_reset, accelerator="Ctrl+0")
        menubar.add_cascade(label="视图", menu=view_menu)
        
        self.root.config(menu=menubar)
    
    def create_toolbar(self, parent):
        """创建工具栏"""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 工具按钮
        tools = [
            ("选择", "select", "🔍"),
            ("空地", "empty", "⬜"),
            ("墙", "wall", "🧱"),
            ("空格", "void", "⬛"),
            ("银行", "bank", "🏦"),
            ("道具商店", "shop", "🏪"),
            ("骰子商店", "dice_shop", "🎲"),
            ("监狱", "jail", "🚔"),
            ("好运格", "luck", "🍀"),
            ("厄运格", "bad_luck", "💀"),
            ("岔路点", "junction", "⭐"),
            ("橡皮擦", "eraser", "🧽")
        ]
        
        for text, tool, icon in tools:
            btn = ttk.Button(toolbar_frame, text=f"{icon} {text}", 
                           command=lambda t=tool: self.set_tool(t))
            btn.pack(side=tk.LEFT, padx=2)
        
        # 分隔符
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 地图信息
        self.map_info_label = ttk.Label(toolbar_frame, text="未创建地图")
        self.map_info_label.pack(side=tk.RIGHT, padx=5)
    
    def create_canvas(self, parent):
        """创建地图画布"""
        # 创建画布框架
        canvas_frame = ttk.Frame(parent)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建画布和滚动条
        self.canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=0)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # 布局
        self.canvas.grid(row=0, column=0, sticky="nsew")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # 绑定事件
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<MouseWheel>", self.on_canvas_scroll)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
    
    def create_property_panel(self, parent):
        """创建属性面板"""
        # 创建属性面板框架
        self.property_frame = ttk.LabelFrame(parent, text="属性面板", width=250)
        self.property_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        self.property_frame.pack_propagate(False)
        
        # 属性内容
        self.property_content = ttk.Frame(self.property_frame)
        self.property_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 默认显示
        self.update_property_panel()
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def bind_shortcuts(self):
        """绑定快捷键"""
        self.root.bind("<Control-n>", lambda e: self.new_map())
        self.root.bind("<Control-o>", lambda e: self.open_map())
        self.root.bind("<Control-s>", lambda e: self.save_map())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        self.root.bind("<Control-plus>", lambda e: self.zoom_in())
        self.root.bind("<Control-minus>", lambda e: self.zoom_out())
        self.root.bind("<Control-0>", lambda e: self.zoom_reset())
        
        # 工具快捷键
        self.root.bind("<Key-1>", lambda e: self.set_tool("select"))
        self.root.bind("<Key-2>", lambda e: self.set_tool("empty"))
        self.root.bind("<Key-3>", lambda e: self.set_tool("wall"))
        self.root.bind("<Key-4>", lambda e: self.set_tool("void"))
        self.root.bind("<Key-5>", lambda e: self.set_tool("bank"))
        self.root.bind("<Key-6>", lambda e: self.set_tool("shop"))
        self.root.bind("<Key-7>", lambda e: self.set_tool("jail"))
        self.root.bind("<Key-8>", lambda e: self.set_tool("luck"))
        self.root.bind("<Key-9>", lambda e: self.set_tool("bad_luck"))
        self.root.bind("<Key-r>", lambda e: self.set_tool("roadblock"))
        self.root.bind("<Key-p>", lambda e: self.set_tool("property"))
        self.root.bind("<Key-e>", lambda e: self.set_tool("eraser"))
    
    def set_tool(self, tool: str):
        """设置当前工具"""
        self.current_tool = tool
        self.update_status(f"当前工具: {tool}")
    
    def on_canvas_click(self, event):
        """处理画布点击事件"""
        if not self.editor.current_map:
            return
        
        # 获取画布坐标
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # 转换为地图坐标
        map_x = int(canvas_x // (self.cell_size * self.zoom_level))
        map_y = int(canvas_y // (self.cell_size * self.zoom_level))
        
        # 检查坐标是否有效
        if not (0 <= map_x < self.editor.current_map.width and 
                0 <= map_y < self.editor.current_map.height):
            return
        
        # 执行工具操作
        if self.current_tool == "select":
            self.select_cell(map_x, map_y)
        elif self.current_tool in ["empty", "wall", "void", "bank", "shop", "dice_shop", "jail", "luck", "bad_luck"]:
            self.editor.set_cell_type(map_x, map_y, self.current_tool)
        elif self.current_tool == "junction":
            self.editor.toggle_junction(map_x, map_y)
        elif self.current_tool == "eraser":
            # 橡皮擦设置为空格（void），并清除所有特殊状态
            self.editor.set_cell_type(map_x, map_y, "void")
            cell = self.editor.current_map.get_cell_at((map_x, map_y))
            if cell:
                cell.is_junction = False
                # 从岔路集合中移除
                path_index = None
                for i, (px, py) in enumerate(self.editor.current_map.path):
                    if px == map_x and py == map_y:
                        path_index = i
                        break
                if path_index is not None and path_index in self.editor.current_map.junctions:
                    self.editor.current_map.junctions.remove(path_index)
        
        # 重绘地图
        self.redraw_map()
        self.update_property_panel()
    
    def on_canvas_drag(self, event):
        """处理画布拖拽事件"""
        # 实现地图拖拽功能
        pass
    
    def on_canvas_scroll(self, event):
        """处理画布滚轮事件"""
        # 实现地图缩放功能
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def on_canvas_motion(self, event):
        """处理画布鼠标移动事件"""
        if not self.editor.current_map:
            return
        
        # 获取画布坐标
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # 转换为地图坐标
        map_x = int(canvas_x // (self.cell_size * self.zoom_level))
        map_y = int(canvas_y // (self.cell_size * self.zoom_level))
        
        # 更新状态栏显示坐标
        if (0 <= map_x < self.editor.current_map.width and 
            0 <= map_y < self.editor.current_map.height):
            self.update_status(f"坐标: ({map_x}, {map_y})")
        else:
            self.update_status("坐标: 无效")
    
    def select_cell(self, x: int, y: int):
        """选择格子"""
        if x is None or y is None:
            self.selected_cell = None
        else:
            self.selected_cell = (x, y)
        self.update_property_panel()
    
    def redraw_map(self):
        """重绘地图"""
        self.canvas.delete("all")
        
        if not self.editor.current_map:
            return
        
        # 绘制网格
        self.draw_grid()
        
        # 绘制格子
        self.draw_cells()
        
        # 绘制选中格子
        if self.selected_cell:
            self.draw_selected_cell()
        
        # 更新画布滚动区域
        self.update_scroll_region()
    
    def draw_grid(self):
        """绘制网格"""
        grid_color = "#E0E0E0"
        line_width = 1
        
        for x in range(self.editor.current_map.width + 1):
            x_pos = x * self.cell_size * self.zoom_level
            self.canvas.create_line(x_pos, 0, x_pos, 
                                  self.editor.current_map.height * self.cell_size * self.zoom_level,
                                  fill=grid_color, width=line_width)
        
        for y in range(self.editor.current_map.height + 1):
            y_pos = y * self.cell_size * self.zoom_level
            self.canvas.create_line(0, y_pos,
                                  self.editor.current_map.width * self.cell_size * self.zoom_level, y_pos,
                                  fill=grid_color, width=line_width)
    
    def draw_cells(self):
        """绘制格子"""
        for cell in self.editor.current_map.cells:
            x = cell.x * self.cell_size * self.zoom_level
            y = cell.y * self.cell_size * self.zoom_level
            size = self.cell_size * self.zoom_level
            
            # 获取格子颜色
            color = self.get_cell_color(cell.cell_type)
            
            # 绘制格子背景
            self.canvas.create_rectangle(x, y, x + size, y + size,
                                       fill=color, outline="black", width=1)
            
            # 绘制格子内容
            self.draw_cell_content(cell, x, y, size)
    
    def get_cell_color(self, cell_type: str) -> str:
        """获取格子颜色"""
        colors = {
            "empty": "white",
            "wall": "#666666",  # 深灰色
            "void": "#000000",  # 黑色
            "bank": "#4CAF50",
            "shop": "#FF9800",
            "dice_shop": "#00BCD4",  # 青色
            "jail": "#F44336",
            "luck": "#9C27B0",
            "bad_luck": "#795548"
        }
        return colors.get(cell_type, "white")
    
    def draw_cell_content(self, cell: Cell, x: float, y: float, size: float):
        """绘制格子内容"""
        # 绘制格子类型文字
        text = cell.cell_type[:3].upper()
        font_size = int(10 * self.zoom_level)
        self.canvas.create_text(x + size//2, y + size//2, text=text,
                              font=("Arial", font_size, "bold"))
        
        # 如果有路障，绘制路障标记
        if cell.roadblock:
            self.canvas.create_text(x + size//2, y + size//4, text="🚧",
                                  font=("Arial", int(8 * self.zoom_level)))
        
        # 如果有房产，绘制房产等级
        if cell.property and cell.property.level > 0:
            self.canvas.create_text(x + size//2, y + 3*size//4,
                                  text=str(cell.property.level),
                                  fill="blue", font=("Arial", int(12 * self.zoom_level), "bold"))
    
    def draw_selected_cell(self):
        """绘制选中的格子"""
        if not self.selected_cell:
            return
        
        x, y = self.selected_cell
        canvas_x = x * self.cell_size * self.zoom_level
        canvas_y = y * self.cell_size * self.zoom_level
        size = self.cell_size * self.zoom_level
        
        # 绘制选中框
        self.canvas.create_rectangle(canvas_x, canvas_y, canvas_x + size, canvas_y + size,
                                   outline="red", width=3)
    
    def update_scroll_region(self):
        """更新画布滚动区域"""
        if not self.editor.current_map:
            return
        
        width = self.editor.current_map.width * self.cell_size * self.zoom_level
        height = self.editor.current_map.height * self.cell_size * self.zoom_level
        
        self.canvas.configure(scrollregion=(0, 0, width, height))
    
    def update_property_panel(self):
        """更新属性面板"""
        # 清除原有内容
        for widget in self.property_content.winfo_children():
            widget.destroy()
        
        if not self.selected_cell:
            ttk.Label(self.property_content, text="未选择格子").pack()
            return
        
        x, y = self.selected_cell
        cell = self.editor.current_map.get_cell_at((x, y))
        
        if not cell:
            ttk.Label(self.property_content, text="无效格子").pack()
            return
        
        # 显示格子属性
        ttk.Label(self.property_content, text=f"坐标: ({x}, {y})", font=("Arial", 12, "bold")).pack(pady=5)
        
        # 格子类型
        ttk.Label(self.property_content, text=f"类型: {cell.cell_type}").pack(anchor=tk.W)
        
        # 路障状态
        ttk.Label(self.property_content, text=f"路障: {'是' if cell.roadblock else '否'}").pack(anchor=tk.W)
        
        # 房产信息
        if cell.property:
            ttk.Label(self.property_content, text=f"房产等级: {cell.property.level}").pack(anchor=tk.W)
            ttk.Label(self.property_content, text=f"所有者: {cell.property.owner_id or '无主'}").pack(anchor=tk.W)
        
        # 地上金钱
        if cell.money_on_ground > 0:
            ttk.Label(self.property_content, text=f"地上金钱: {cell.money_on_ground}").pack(anchor=tk.W)
    
    def update_status(self, message: str):
        """更新状态栏"""
        self.status_bar.config(text=message)
    
    def new_map(self):
        """新建地图"""
        try:
            # 创建对话框获取地图尺寸
            dialog = NewMapDialog(self.root)
            
            # 等待对话框关闭
            self.root.wait_window(dialog.dialog)
            
            if dialog.result:
                width, height = dialog.result
                
                # 显示创建进度
                self.update_status(f"正在创建地图 {width}x{height}...")
                self.root.update()
                
                # 创建地图
                self.editor.create_new_map(width, height)
                
                # 重绘地图
                self.redraw_map()
                self.update_map_info()
                
                # 显示成功消息
                self.update_status(f"已创建新地图: {width}x{height}")
                messagebox.showinfo("成功", f"已创建新地图 {width}x{height}")
                
            else:
                self.update_status("取消创建地图")
                
        except Exception as e:
            error_msg = f"创建地图失败: {e}"
            self.update_status(error_msg)
            messagebox.showerror("错误", error_msg)
            import traceback
            print(traceback.format_exc())
    
    def open_map(self):
        """打开地图"""
        file_path = filedialog.askopenfilename(
            title="打开地图",
            filetypes=[
                ("JSON文件", "*.json"),
                ("Excel文件", "*.xlsx"),
                ("数据库文件", "*.db"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            if self.editor.load_map(file_path):
                self.redraw_map()
                self.update_map_info()
                self.update_status(f"已加载地图: {file_path}")
            else:
                messagebox.showerror("错误", "加载地图失败")
    
    def save_map(self):
        """保存地图"""
        if not self.editor.current_map:
            messagebox.showwarning("警告", "没有可保存的地图")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存地图",
            defaultextension=".json",
            filetypes=[
                ("JSON文件", "*.json"),
                ("Excel文件", "*.xlsx"),
                ("数据库文件", "*.db")
            ]
        )
        
        if file_path:
            if self.editor.save_map(file_path):
                self.update_status(f"已保存地图: {file_path}")
            else:
                messagebox.showerror("错误", "保存地图失败")
    
    def validate_map(self):
        """验证地图"""
        if not self.editor.current_map:
            messagebox.showwarning("警告", "没有可验证的地图")
            return
        
        self.editor.validate_current_map()
        messagebox.showinfo("验证完成", "地图验证完成，请查看控制台输出")
    
    def update_map_info(self):
        """更新地图信息显示"""
        if self.editor.current_map:
            info = f"地图: {self.editor.current_map.width}x{self.editor.current_map.height} | 路径: {self.editor.current_map.path_length}"
            self.map_info_label.config(text=info)
        else:
            self.map_info_label.config(text="未创建地图")
    
    def zoom_in(self):
        """放大"""
        self.zoom_level = min(self.zoom_level * 1.2, 3.0)
        self.redraw_map()
    
    def zoom_out(self):
        """缩小"""
        self.zoom_level = max(self.zoom_level / 1.2, 0.3)
        self.redraw_map()
    
    def zoom_reset(self):
        """重置缩放"""
        self.zoom_level = 1.0
        self.redraw_map()
    
    def undo(self):
        """撤销操作"""
        # TODO: 实现撤销功能
        self.update_status("撤销功能待实现")
    
    def redo(self):
        """重做操作"""
        # TODO: 实现重做功能
        self.update_status("重做功能待实现")
    
    def run(self):
        """运行图形化编辑器"""
        self.root.mainloop()


class NewMapDialog:
    """新建地图对话框"""
    
    def __init__(self, parent):
        self.result = None
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("新建地图")
        self.dialog.geometry("350x250")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        
        # 设置模态化
        self.dialog.focus_set()
        self.dialog.wait_visibility()
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        # 标题
        title_label = ttk.Label(self.dialog, text="创建新地图", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(10, 20))
        
        # 说明文字
        desc_label = ttk.Label(self.dialog, text="请输入地图尺寸（建议20x20）", font=("Arial", 10))
        desc_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # 宽度输入
        ttk.Label(self.dialog, text="地图宽度:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        self.width_var = tk.StringVar(value="20")
        self.width_entry = ttk.Entry(self.dialog, textvariable=self.width_var, width=10)
        self.width_entry.grid(row=2, column=1, padx=10, pady=10)
        
        # 高度输入
        ttk.Label(self.dialog, text="地图高度:").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        self.height_var = tk.StringVar(value="20")
        self.height_entry = ttk.Entry(self.dialog, textvariable=self.height_var, width=10)
        self.height_entry.grid(row=3, column=1, padx=10, pady=10)
        
        # 按钮
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="确定", command=self.ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.cancel).pack(side=tk.LEFT, padx=10)
        
        # 绑定回车键和焦点
        self.dialog.bind("<Return>", lambda e: self.ok())
        self.dialog.bind("<Escape>", lambda e: self.cancel())
        
        # 设置焦点到宽度输入框
        self.width_entry.focus_set()
    
    def ok(self):
        """确定按钮"""
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            
            if width < 5 or height < 5:
                messagebox.showerror("错误", "地图尺寸不能小于5x5")
                return
            
            if width > 50 or height > 50:
                messagebox.showerror("错误", "地图尺寸不能大于50x50")
                return
            
            self.result = (width, height)
            self.dialog.destroy()
        
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
    
    def cancel(self):
        """取消按钮"""
        self.dialog.destroy()


def main():
    """主函数"""
    editor = MapEditor()
    editor.run_interactive_editor()


if __name__ == "__main__":
    main() 