#!/usr/bin/env python3
"""
简单测试新建地图对话框
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.map_editor import NewMapDialog


def test_dialog():
    """测试对话框"""
    root = tk.Tk()
    root.title("测试对话框")
    root.geometry("400x300")
    
    def show_dialog():
        dialog = NewMapDialog(root)
        root.wait_window(dialog.dialog)
        if dialog.result:
            width, height = dialog.result
            result_label.config(text=f"结果: {width}x{height}")
        else:
            result_label.config(text="用户取消了")
    
    # 创建测试界面
    ttk.Label(root, text="测试新建地图对话框", font=("Arial", 16)).pack(pady=20)
    
    ttk.Button(root, text="显示对话框", command=show_dialog).pack(pady=10)
    
    result_label = ttk.Label(root, text="等待测试...", font=("Arial", 12))
    result_label.pack(pady=20)
    
    ttk.Button(root, text="退出", command=root.quit).pack(pady=10)
    
    root.mainloop()


if __name__ == "__main__":
    test_dialog() 