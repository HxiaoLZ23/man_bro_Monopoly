"""
增强版地图编辑器 - 支持GUI路径连接功能
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Tuple, Optional

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.map import Map, Cell
from src.utils.map_editor import MapEditor


class EnhancedMapEditorGUI:
    """增强版图形化地图编辑器"""
    
    def __init__(self):
        """初始化增强版编辑器"""
        self.editor = MapEditor()
        self.root = tk.Tk()
        self.root.title("大富翁地图编辑器 - 增强版")
        self.root.geometry("1400x900")
        
        # 编辑器状态
        self.current_tool = "select"
        self.selected_cell = None
        self.cell_size = 30
        self.zoom_level = 1.0
        
        # 路径连接状态
        self.connecting_from = None  # 连接起点坐标 (x, y)
        self.connecting_mode = False  # 是否在连接模式
        
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
        file_menu.add_command(label="显示路径信息", command=self.show_path_info)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="验证地图", command=self.validate_map)
        edit_menu.add_separator()
        edit_menu.add_command(label="清除所有连接", command=self.clear_all_connections)
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
            ("连接路径", "connect", "🔗"),
            ("橡皮擦", "eraser", "🧽")
        ]
        
        for text, tool, icon in tools:
            btn = ttk.Button(toolbar_frame, text=f"{icon} {text}", 
                           command=lambda t=tool: self.set_tool(t))
            btn.pack(side=tk.LEFT, padx=2)
        
        # 分隔符
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 连接状态标签
        self.connect_status_label = ttk.Label(toolbar_frame, text="", foreground="blue")
        self.connect_status_label.pack(side=tk.LEFT, padx=5)
        
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
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)  # 右键取消连接
        self.canvas.bind("<Motion>", self.on_canvas_motion)
    
    def create_property_panel(self, parent):
        """创建属性面板"""
        # 创建属性面板框架
        self.property_frame = ttk.LabelFrame(parent, text="属性面板", width=300)
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
        self.root.bind("<Escape>", lambda e: self.cancel_connection())
        
        # 工具快捷键
        self.root.bind("<Key-c>", lambda e: self.set_tool("connect"))
        self.root.bind("<Key-j>", lambda e: self.set_tool("junction"))
        self.root.bind("<Key-s>", lambda e: self.set_tool("select"))
    
    def set_tool(self, tool: str):
        """设置当前工具"""
        # 如果切换工具，取消当前连接
        if self.current_tool == "connect" and tool != "connect":
            self.cancel_connection()
        
        self.current_tool = tool
        
        if tool == "connect":
            self.update_status("连接模式：点击第一个格子选择起点")
            self.connecting_mode = True
        else:
            self.update_status(f"当前工具: {tool}")
            self.connecting_mode = False
    
    def on_canvas_click(self, event):
        """处理画布点击事件"""
        if not self.editor.current_map:
            return
        
        # 获取地图坐标
        map_x, map_y = self.get_map_coordinates(event.x, event.y)
        if map_x is None or map_y is None:
            return
        
        # 执行工具操作
        if self.current_tool == "connect":
            self.handle_connection_click(map_x, map_y)
        elif self.current_tool == "select":
            self.select_cell(map_x, map_y)
        elif self.current_tool in ["empty", "wall", "void", "bank", "shop", "dice_shop", "jail", "luck", "bad_luck"]:
            self.editor.set_cell_type(map_x, map_y, self.current_tool)
        elif self.current_tool == "junction":
            self.editor.toggle_junction(map_x, map_y)
        elif self.current_tool == "eraser":
            self.erase_cell(map_x, map_y)
        
        # 重绘地图
        self.redraw_map()
        self.update_property_panel()
    
    def on_canvas_right_click(self, event):
        """处理右键点击事件"""
        if self.current_tool == "connect":
            self.cancel_connection()
    
    def handle_connection_click(self, map_x: int, map_y: int):
        """处理连接工具的点击"""
        # 检查点击的格子是否在路径上
        path_index = self.get_path_index(map_x, map_y)
        if path_index is None:
            self.update_status("只能连接路径上的格子！")
            return
        
        if self.connecting_from is None:
            # 选择起点
            self.connecting_from = (map_x, map_y)
            self.update_status(f"已选择起点：位置{path_index}，请点击终点")
            self.connect_status_label.config(text=f"起点: ({map_x},{map_y})")
            self.redraw_map()  # 重绘以显示起点标记
        else:
            # 选择终点，创建连接
            from_x, from_y = self.connecting_from
            from_index = self.get_path_index(from_x, from_y)
            to_index = path_index
            
            if from_index == to_index:
                self.update_status("不能连接到自己！")
                return
            
            # 创建连接
            success = self.editor.add_path_connection(from_index, to_index)
            if success:
                self.update_status(f"成功创建连接：{from_index} -> {to_index}")
                messagebox.showinfo("成功", f"成功创建路径连接：位置{from_index} -> 位置{to_index}")
            else:
                self.update_status(f"连接失败：{from_index} -> {to_index}")
                messagebox.showerror("失败", "创建路径连接失败")
            
            # 重置连接状态
            self.cancel_connection()
    
    def cancel_connection(self):
        """取消连接"""
        self.connecting_from = None
        self.connect_status_label.config(text="")
        if self.connecting_mode:
            self.update_status("连接模式：点击第一个格子选择起点")
        self.redraw_map()  # 重绘以清除起点标记
    
    def get_map_coordinates(self, canvas_x: float, canvas_y: float) -> Tuple[Optional[int], Optional[int]]:
        """获取地图坐标"""
        # 转换画布坐标为地图坐标
        canvas_x = self.canvas.canvasx(canvas_x)
        canvas_y = self.canvas.canvasy(canvas_y)
        
        map_x = int(canvas_x // (self.cell_size * self.zoom_level))
        map_y = int(canvas_y // (self.cell_size * self.zoom_level))
        
        # 检查坐标是否有效
        if (0 <= map_x < self.editor.current_map.width and 
            0 <= map_y < self.editor.current_map.height):
            return map_x, map_y
        return None, None
    
    def get_path_index(self, map_x: int, map_y: int) -> Optional[int]:
        """获取格子的路径索引"""
        for i, (px, py) in enumerate(self.editor.current_map.path):
            if px == map_x and py == map_y:
                return i
        return None
    
    def erase_cell(self, map_x: int, map_y: int):
        """擦除格子"""
        self.editor.set_cell_type(map_x, map_y, "void")
        cell = self.editor.current_map.get_cell_at((map_x, map_y))
        if cell:
            cell.is_junction = False
            # 从岔路集合中移除
            path_index = self.get_path_index(map_x, map_y)
            if path_index is not None and path_index in self.editor.current_map.junctions:
                self.editor.current_map.junctions.remove(path_index)
    
    def on_canvas_motion(self, event):
        """处理画布鼠标移动事件"""
        if not self.editor.current_map:
            return
        
        map_x, map_y = self.get_map_coordinates(event.x, event.y)
        if map_x is not None and map_y is not None:
            path_index = self.get_path_index(map_x, map_y)
            if path_index is not None:
                self.update_status(f"坐标: ({map_x}, {map_y}), 路径索引: {path_index}")
            else:
                self.update_status(f"坐标: ({map_x}, {map_y})")
        else:
            self.update_status("坐标: 无效")
    
    def select_cell(self, x: int, y: int):
        """选择格子"""
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
        
        # 绘制路径连接线
        self.draw_path_connections()
        
        # 绘制选中格子
        if self.selected_cell:
            self.draw_selected_cell()
        
        # 绘制连接起点
        if self.connecting_from:
            self.draw_connecting_from()
        
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
    
    def draw_path_connections(self):
        """绘制路径连接线"""
        if not self.editor.current_map:
            return
        
        # 绘制所有路径连接
        for i, (x, y) in enumerate(self.editor.current_map.path):
            cell = self.editor.current_map.get_cell_by_path_index(i)
            if cell and len(cell.connections) > 2:  # 有额外连接（不只是前后相邻）
                center_x = (x + 0.5) * self.cell_size * self.zoom_level
                center_y = (y + 0.5) * self.cell_size * self.zoom_level
                
                for connected_index in cell.connections:
                    # 检查是否是分支连接（不是主路径的前后相邻）
                    prev_index = (i - 1) % self.editor.current_map.path_length
                    next_index = (i + 1) % self.editor.current_map.path_length
                    
                    if connected_index != prev_index and connected_index != next_index:
                        # 这是一个分支连接
                        connected_pos = self.editor.current_map.get_position_by_path_index(connected_index)
                        if connected_pos:
                            target_x = (connected_pos[0] + 0.5) * self.cell_size * self.zoom_level
                            target_y = (connected_pos[1] + 0.5) * self.cell_size * self.zoom_level
                            
                            # 绘制连接线
                            self.canvas.create_line(center_x, center_y, target_x, target_y,
                                                  fill="red", width=3, dash=(5, 5))
    
    def draw_connecting_from(self):
        """绘制连接起点标记"""
        if not self.connecting_from:
            return
        
        x, y = self.connecting_from
        canvas_x = x * self.cell_size * self.zoom_level
        canvas_y = y * self.cell_size * self.zoom_level
        size = self.cell_size * self.zoom_level
        
        # 绘制蓝色边框表示起点
        self.canvas.create_rectangle(canvas_x, canvas_y, canvas_x + size, canvas_y + size,
                                   outline="blue", width=4)
    
    def get_cell_color(self, cell_type: str) -> str:
        """获取格子颜色"""
        colors = {
            "empty": "white",
            "wall": "#666666",
            "void": "#000000",
            "bank": "#4CAF50",
            "shop": "#FF9800",
            "dice_shop": "#00BCD4",
            "jail": "#F44336",
            "luck": "#9C27B0",
            "bad_luck": "#795548"
        }
        return colors.get(cell_type, "white")
    
    def draw_cell_content(self, cell: Cell, x: float, y: float, size: float):
        """绘制格子内容"""
        # 绘制路径索引
        if cell.path_index >= 0:
            font_size = int(8 * self.zoom_level)
            self.canvas.create_text(x + size//4, y + size//4, text=str(cell.path_index),
                                  font=("Arial", font_size), fill="blue")
        
        # 绘制格子类型文字
        if cell.cell_type != "void":
            text = cell.cell_type[:3].upper()
            font_size = int(10 * self.zoom_level)
            self.canvas.create_text(x + size//2, y + size//2, text=text,
                                  font=("Arial", font_size, "bold"))
        
        # 如果是岔路点，绘制星号标记
        if cell.is_junction:
            self.canvas.create_text(x + 3*size//4, y + size//4, text="⭐",
                                  font=("Arial", int(12 * self.zoom_level)))
    
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
        
        # 显示格子信息
        ttk.Label(self.property_content, text=f"坐标: ({x}, {y})").pack(anchor="w")
        ttk.Label(self.property_content, text=f"类型: {cell.cell_type}").pack(anchor="w")
        ttk.Label(self.property_content, text=f"路径索引: {cell.path_index}").pack(anchor="w")
        ttk.Label(self.property_content, text=f"是否岔路: {cell.is_junction}").pack(anchor="w")
        
        # 显示连接信息
        if cell.connections:
            ttk.Label(self.property_content, text="连接到:").pack(anchor="w")
            for conn in sorted(cell.connections):
                ttk.Label(self.property_content, text=f"  -> 位置 {conn}").pack(anchor="w")
        
        # 如果是路径格子，显示操作按钮
        if cell.path_index >= 0:
            ttk.Separator(self.property_content, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
            
            # 切换岔路点状态
            junction_btn = ttk.Button(self.property_content, 
                                    text="取消岔路点" if cell.is_junction else "设为岔路点",
                                    command=lambda: self.toggle_junction_for_selected())
            junction_btn.pack(fill=tk.X, pady=2)
            
            # 显示可用方向
            directions = self.editor.get_available_directions(cell.path_index)
            if directions:
                ttk.Label(self.property_content, text=f"可用方向: {directions}").pack(anchor="w")
    
    def toggle_junction_for_selected(self):
        """切换选中格子的岔路点状态"""
        if self.selected_cell:
            x, y = self.selected_cell
            self.editor.toggle_junction(x, y)
            self.redraw_map()
            self.update_property_panel()
    
    def update_status(self, message: str):
        """更新状态栏"""
        self.status_bar.config(text=message)
    
    def new_map(self):
        """新建地图"""
        dialog = NewMapDialog(self.root)
        if dialog.result:
            width, height = dialog.result
            self.editor.create_new_map(width, height)
            self.redraw_map()
            self.update_map_info()
            self.update_status(f"创建了新地图: {width}x{height}")
    
    def open_map(self):
        """打开地图"""
        file_path = filedialog.askopenfilename(
            title="打开地图文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if file_path:
            success = self.editor.load_map(file_path)
            if success:
                self.redraw_map()
                self.update_map_info()
                self.update_status(f"成功打开地图: {file_path}")
            else:
                messagebox.showerror("错误", "打开地图文件失败")
    
    def save_map(self):
        """保存地图"""
        if not self.editor.current_map:
            messagebox.showwarning("警告", "没有可保存的地图")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存地图文件",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if file_path:
            success = self.editor.save_map(file_path)
            if success:
                self.update_status(f"成功保存地图: {file_path}")
                messagebox.showinfo("成功", "地图保存成功")
            else:
                messagebox.showerror("错误", "保存地图文件失败")
    
    def show_path_info(self):
        """显示路径信息"""
        if not self.editor.current_map:
            messagebox.showwarning("警告", "没有可显示的地图")
            return
        
        # 创建新窗口显示路径信息
        info_window = tk.Toplevel(self.root)
        info_window.title("路径信息")
        info_window.geometry("600x400")
        
        # 创建文本框和滚动条
        text_frame = ttk.Frame(info_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 显示路径信息
        info_text = f"路径信息:\n"
        info_text += f"路径总长度: {self.editor.current_map.path_length}\n"
        info_text += f"岔路口数量: {len(self.editor.current_map.junctions)}\n\n"
        
        if self.editor.current_map.junctions:
            info_text += "岔路口位置:\n"
            for junction_index in sorted(self.editor.current_map.junctions):
                pos = self.editor.current_map.get_position_by_path_index(junction_index)
                cell = self.editor.current_map.get_cell_by_path_index(junction_index)
                connections = len(cell.connections) if cell else 0
                info_text += f"  索引 {junction_index}: 位置 {pos}, {connections} 个连接\n"
        
        info_text += "\n路径连接:\n"
        for i, (x, y) in enumerate(self.editor.current_map.path):
            cell = self.editor.current_map.get_cell_by_path_index(i)
            if cell:
                connections = list(cell.connections)
                info_text += f"  索引 {i}: 位置 ({x}, {y}), 连接: {connections}\n"
        
        text_widget.insert(tk.END, info_text)
        text_widget.config(state=tk.DISABLED)
    
    def validate_map(self):
        """验证地图"""
        if not self.editor.current_map:
            messagebox.showwarning("警告", "没有可验证的地图")
            return
        
        self.editor.validate_current_map()
        messagebox.showinfo("验证完成", "地图验证完成，请查看控制台输出")
    
    def clear_all_connections(self):
        """清除所有路径连接"""
        if not self.editor.current_map:
            return
        
        result = messagebox.askyesno("确认", "确定要清除所有额外的路径连接吗？\n这将保留主路径，但删除所有分支连接。")
        if result:
            # 重置所有路径格子的连接为默认（只连接前后相邻）
            for i, (x, y) in enumerate(self.editor.current_map.path):
                cell = self.editor.current_map.get_cell_by_path_index(i)
                if cell:
                    prev_index = (i - 1) % self.editor.current_map.path_length
                    next_index = (i + 1) % self.editor.current_map.path_length
                    cell.connections = {prev_index, next_index}
                    cell.is_junction = False
            
            # 清空岔路集合
            self.editor.current_map.junctions.clear()
            
            self.redraw_map()
            self.update_property_panel()
            self.update_status("已清除所有路径连接")
    
    def update_map_info(self):
        """更新地图信息"""
        if self.editor.current_map:
            info = f"地图: {self.editor.current_map.width}x{self.editor.current_map.height}"
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
    
    def run(self):
        """运行编辑器"""
        self.root.mainloop()


class NewMapDialog:
    """新建地图对话框"""
    
    def __init__(self, parent):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("新建地图")
        self.dialog.geometry("300x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
        self.dialog.wait_window()
    
    def setup_ui(self):
        """设置UI"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 宽度
        ttk.Label(main_frame, text="宽度:").grid(row=0, column=0, sticky="w", pady=5)
        self.width_var = tk.StringVar(value="10")
        width_entry = ttk.Entry(main_frame, textvariable=self.width_var, width=10)
        width_entry.grid(row=0, column=1, padx=(10, 0), pady=5)
        
        # 高度
        ttk.Label(main_frame, text="高度:").grid(row=1, column=0, sticky="w", pady=5)
        self.height_var = tk.StringVar(value="10")
        height_entry = ttk.Entry(main_frame, textvariable=self.height_var, width=10)
        height_entry.grid(row=1, column=1, padx=(10, 0), pady=5)
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="确定", command=self.ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        # 绑定回车键
        self.dialog.bind('<Return>', lambda e: self.ok())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        # 焦点
        width_entry.focus()
    
    def ok(self):
        """确定"""
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            
            if width < 3 or height < 3:
                messagebox.showerror("错误", "地图尺寸不能小于3x3")
                return
            
            if width > 50 or height > 50:
                messagebox.showerror("错误", "地图尺寸不能大于50x50")
                return
            
            self.result = (width, height)
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
    
    def cancel(self):
        """取消"""
        self.dialog.destroy()


def main():
    """主函数"""
    editor = EnhancedMapEditorGUI()
    editor.run()


if __name__ == "__main__":
    main() 