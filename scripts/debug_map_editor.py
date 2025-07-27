#!/usr/bin/env python3
"""
调试版地图编辑器
"""
import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.map_editor import MapEditor


class DebugMapEditorGUI:
    """调试版地图编辑器GUI"""
    
    def __init__(self):
        self.editor = MapEditor()
        self.root = tk.Tk()
        self.root.title("调试版地图编辑器")
        self.root.geometry("800x600")
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        # 创建菜单
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="新建地图", command=self.debug_new_map)
        menubar.add_cascade(label="文件", menu=file_menu)
        self.root.config(menu=menubar)
        
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建按钮
        ttk.Button(main_frame, text="测试新建地图", command=self.debug_new_map).pack(pady=10)
        ttk.Button(main_frame, text="测试创建地图对象", command=self.debug_create_map).pack(pady=10)
        ttk.Button(main_frame, text="测试对话框", command=self.debug_dialog).pack(pady=10)
        
        # 创建日志区域
        log_frame = ttk.LabelFrame(main_frame, text="调试日志")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = tk.Text(log_frame, height=20)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 清空日志按钮
        ttk.Button(main_frame, text="清空日志", command=self.clear_log).pack(pady=5)
    
    def log(self, message):
        """添加日志"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        print(message)  # 同时输出到控制台
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
    
    def debug_new_map(self):
        """调试新建地图功能"""
        self.log("=== 开始调试新建地图功能 ===")
        
        try:
            self.log("1. 创建对话框...")
            from src.utils.map_editor import NewMapDialog
            dialog = NewMapDialog(self.root)
            self.log("   对话框创建成功")
            
            self.log("2. 等待对话框关闭...")
            self.root.wait_window(dialog.dialog)
            self.log("   对话框已关闭")
            
            self.log(f"3. 对话框结果: {dialog.result}")
            
            if dialog.result:
                width, height = dialog.result
                self.log(f"4. 创建地图: {width}x{height}")
                
                self.editor.create_new_map(width, height)
                self.log("   地图创建成功")
                
                self.log(f"5. 地图信息: {self.editor.current_map.width}x{self.editor.current_map.height}")
                self.log(f"   路径长度: {self.editor.current_map.path_length}")
                self.log(f"   格子数量: {len(self.editor.current_map.cells)}")
                
            else:
                self.log("4. 用户取消了操作")
                
        except Exception as e:
            self.log(f"错误: {e}")
            import traceback
            self.log(traceback.format_exc())
    
    def debug_create_map(self):
        """调试创建地图对象"""
        self.log("=== 调试创建地图对象 ===")
        
        try:
            self.log("1. 直接创建地图对象...")
            self.editor.create_new_map(15, 15)
            self.log("   地图创建成功")
            
            self.log(f"2. 地图信息: {self.editor.current_map.width}x{self.editor.current_map.height}")
            self.log(f"   路径长度: {self.editor.current_map.path_length}")
            self.log(f"   格子数量: {len(self.editor.current_map.cells)}")
            
            # 测试一些格子
            cell = self.editor.current_map.get_cell_at((0, 0))
            self.log(f"3. 测试格子(0,0): {cell.cell_type}")
            
            cell = self.editor.current_map.get_cell_at((7, 7))
            self.log(f"4. 测试格子(7,7): {cell.cell_type}")
            
        except Exception as e:
            self.log(f"错误: {e}")
            import traceback
            self.log(traceback.format_exc())
    
    def debug_dialog(self):
        """调试对话框"""
        self.log("=== 调试对话框 ===")
        
        try:
            self.log("1. 创建简单对话框...")
            
            # 创建简单的输入对话框
            dialog = tk.Toplevel(self.root)
            dialog.title("测试对话框")
            dialog.geometry("300x150")
            dialog.transient(self.root)
            dialog.grab_set()
            
            result = tk.StringVar()
            
            ttk.Label(dialog, text="输入宽度:").pack(pady=5)
            width_entry = ttk.Entry(dialog, textvariable=result)
            width_entry.pack(pady=5)
            
            def ok():
                dialog.destroy()
            
            ttk.Button(dialog, text="确定", command=ok).pack(pady=10)
            
            self.log("2. 显示对话框...")
            self.root.wait_window(dialog)
            self.log("3. 对话框关闭")
            self.log(f"4. 输入结果: {result.get()}")
            
        except Exception as e:
            self.log(f"错误: {e}")
            import traceback
            self.log(traceback.format_exc())
    
    def run(self):
        """运行调试器"""
        self.log("调试版地图编辑器已启动")
        self.root.mainloop()


def main():
    """主函数"""
    debugger = DebugMapEditorGUI()
    debugger.run()


if __name__ == "__main__":
    main() 