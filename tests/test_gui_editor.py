"""
图形化地图编辑器测试
"""
import unittest
import sys
import os
import tempfile
import tkinter as tk
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.map_editor import MapEditor, MapEditorGUI, NewMapDialog


class TestMapEditorGUI(unittest.TestCase):
    """图形化地图编辑器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.editor = MapEditor()
        self.editor.create_new_map(10, 10)
    
    def test_gui_initialization(self):
        """测试GUI初始化"""
        # 模拟tkinter环境
        with patch('tkinter.Tk') as mock_tk:
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            
            gui = MapEditorGUI(self.editor)
            
            # 验证GUI组件创建
            self.assertIsNotNone(gui.root)
            self.assertIsNotNone(gui.canvas)
            self.assertEqual(gui.current_tool, "select")
            self.assertEqual(gui.zoom_level, 1.0)
    
    def test_tool_selection(self):
        """测试工具选择"""
        with patch('tkinter.Tk'):
            gui = MapEditorGUI(self.editor)
            
            # 测试工具切换
            gui.set_tool("bank")
            self.assertEqual(gui.current_tool, "bank")
            
            gui.set_tool("shop")
            self.assertEqual(gui.current_tool, "shop")
    
    def test_cell_color_mapping(self):
        """测试格子颜色映射"""
        with patch('tkinter.Tk'):
            gui = MapEditorGUI(self.editor)
            
            # 测试不同格子类型的颜色
            self.assertEqual(gui.get_cell_color("empty"), "white")
            self.assertEqual(gui.get_cell_color("bank"), "#4CAF50")
            self.assertEqual(gui.get_cell_color("shop"), "#FF9800")
            self.assertEqual(gui.get_cell_color("jail"), "#F44336")
            self.assertEqual(gui.get_cell_color("luck"), "#9C27B0")
            self.assertEqual(gui.get_cell_color("bad_luck"), "#795548")
    
    def test_zoom_functions(self):
        """测试缩放功能"""
        with patch('tkinter.Tk'):
            gui = MapEditorGUI(self.editor)
            
            # 测试放大
            original_zoom = gui.zoom_level
            gui.zoom_in()
            self.assertGreater(gui.zoom_level, original_zoom)
            
            # 测试缩小
            gui.zoom_out()
            self.assertLess(gui.zoom_level, gui.zoom_level)
            
            # 测试重置
            gui.zoom_reset()
            self.assertEqual(gi.zoom_level, 1.0)
    
    def test_map_operations(self):
        """测试地图操作"""
        with patch('tkinter.Tk'):
            gui = MapEditorGUI(self.editor)
            
            # 测试地图信息更新
            gui.update_map_info()
            expected_text = "地图: 10x10 | 路径: 36"  # 假设路径长度为36
            self.assertIn("10x10", gui.map_info_label.cget("text"))
    
    def test_cell_selection(self):
        """测试格子选择"""
        with patch('tkinter.Tk'):
            gui = MapEditorGUI(self.editor)
            
            # 测试选择格子
            gui.select_cell(5, 5)
            self.assertEqual(gui.selected_cell, (5, 5))
            
            # 测试清除选择
            gui.select_cell(None, None)
            self.assertIsNone(gui.selected_cell)


class TestNewMapDialog(unittest.TestCase):
    """新建地图对话框测试"""
    
    def setUp(self):
        """测试前准备"""
        self.mock_parent = MagicMock()
    
    def test_dialog_creation(self):
        """测试对话框创建"""
        with patch('tkinter.Toplevel') as mock_toplevel:
            mock_dialog = MagicMock()
            mock_toplevel.return_value = mock_dialog
            
            dialog = NewMapDialog(self.mock_parent)
            
            # 验证对话框创建
            self.assertIsNotNone(dialog.dialog)
            self.assertEqual(dialog.result, None)
    
    def test_valid_input(self):
        """测试有效输入"""
        with patch('tkinter.Toplevel'):
            dialog = NewMapDialog(self.mock_parent)
            
            # 模拟有效输入
            dialog.width_var.set("15")
            dialog.height_var.set("15")
            
            with patch('tkinter.messagebox.showerror') as mock_error:
                dialog.ok()
                
                # 验证没有错误提示
                mock_error.assert_not_called()
                # 验证结果
                self.assertEqual(dialog.result, (15, 15))
    
    def test_invalid_input(self):
        """测试无效输入"""
        with patch('tkinter.Toplevel'):
            dialog = NewMapDialog(self.mock_parent)
            
            # 模拟无效输入
            dialog.width_var.set("abc")
            dialog.height_var.set("15")
            
            with patch('tkinter.messagebox.showerror') as mock_error:
                dialog.ok()
                
                # 验证错误提示
                mock_error.assert_called_once()
    
    def test_size_limits(self):
        """测试尺寸限制"""
        with patch('tkinter.Toplevel'):
            dialog = NewMapDialog(self.mock_parent)
            
            # 测试尺寸太小
            dialog.width_var.set("3")
            dialog.height_var.set("3")
            
            with patch('tkinter.messagebox.showerror') as mock_error:
                dialog.ok()
                mock_error.assert_called_once()
            
            # 测试尺寸太大
            dialog.width_var.set("60")
            dialog.height_var.set("60")
            
            with patch('tkinter.messagebox.showerror') as mock_error:
                dialog.ok()
                mock_error.assert_called_once()


class TestMapEditorIntegration(unittest.TestCase):
    """地图编辑器集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.editor = MapEditor()
    
    def test_gui_mode_switch(self):
        """测试GUI模式切换"""
        # 测试从命令行模式切换到GUI模式
        self.assertFalse(self.editor.gui_mode)
        
        # 模拟GUI启动
        with patch('src.utils.map_editor.MapEditorGUI') as mock_gui_class:
            mock_gui = MagicMock()
            mock_gui_class.return_value = mock_gui
            
            self.editor.run_gui_editor()
            
            # 验证GUI被创建和运行
            mock_gui_class.assert_called_once_with(self.editor)
            mock_gui.run.assert_called_once()
    
    def test_command_line_gui_command(self):
        """测试命令行中的GUI命令"""
        # 测试在命令行模式下输入gui命令
        with patch('src.utils.map_editor.MapEditorGUI') as mock_gui_class:
            mock_gui = MagicMock()
            mock_gui_class.return_value = mock_gui
            
            # 模拟用户输入
            with patch('builtins.input', return_value="gui"):
                with patch('builtins.print'):  # 抑制输出
                    # 这里需要模拟run_interactive_editor的循环
                    pass


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2) 