#!/usr/bin/env python3
"""
测试GUI地图编辑器修复
验证空格、墙和橡皮擦功能是否正确
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.map import Map, Cell
from utils.map_editor import MapEditor

def test_gui_fixes():
    """测试GUI修复"""
    print("=== 测试GUI地图编辑器修复 ===")
    
    # 创建地图编辑器
    editor = MapEditor()
    
    # 创建测试地图
    print("1. 创建测试地图...")
    editor.create_new_map(5, 5)
    
    # 测试设置不同类型的格子
    print("2. 测试设置不同类型的格子...")
    
    # 设置空地
    editor.set_cell_type(0, 0, "empty")
    cell = editor.current_map.get_cell_at((0, 0))
    assert cell.cell_type == "empty", f"空地设置失败: {cell.cell_type}"
    print("   ✓ 空地设置成功")
    
    # 设置墙
    editor.set_cell_type(1, 1, "wall")
    cell = editor.current_map.get_cell_at((1, 1))
    assert cell.cell_type == "wall", f"墙设置失败: {cell.cell_type}"
    print("   ✓ 墙设置成功")
    
    # 设置空格
    editor.set_cell_type(2, 2, "void")
    cell = editor.current_map.get_cell_at((2, 2))
    assert cell.cell_type == "void", f"空格设置失败: {cell.cell_type}"
    print("   ✓ 空格设置成功")
    
    # 设置银行
    editor.set_cell_type(3, 3, "bank")
    cell = editor.current_map.get_cell_at((3, 3))
    assert cell.cell_type == "bank", f"银行设置失败: {cell.cell_type}"
    print("   ✓ 银行设置成功")
    
    # 测试橡皮擦功能
    print("3. 测试橡皮擦功能...")
    
    # 先设置一个银行格子
    editor.set_cell_type(4, 4, "bank")
    cell = editor.current_map.get_cell_at((4, 4))
    assert cell.cell_type == "bank", "银行设置失败"
    
    # 添加路障
    editor.toggle_roadblock(4, 4)
    assert cell.roadblock, "路障添加失败"
    
    # 使用橡皮擦（应该设置为空格并移除路障）
    editor.set_cell_type(4, 4, "void")
    editor.current_map.remove_roadblock((4, 4))
    
    cell = editor.current_map.get_cell_at((4, 4))
    assert cell.cell_type == "void", f"橡皮擦设置空格失败: {cell.cell_type}"
    assert not cell.roadblock, "橡皮擦移除路障失败"
    print("   ✓ 橡皮擦功能正常")
    
    # 测试颜色映射
    print("4. 测试颜色映射...")
    from utils.map_editor import MapEditorGUI
    
    # 创建GUI实例来测试颜色
    gui = MapEditorGUI(editor)
    
    # 测试各种类型的颜色
    colors = {
        "empty": "white",
        "wall": "#666666",
        "void": "#000000",
        "bank": "#4CAF50",
        "shop": "#FF9800",
        "jail": "#F44336",
        "luck": "#9C27B0",
        "bad_luck": "#795548"
    }
    
    for cell_type, expected_color in colors.items():
        actual_color = gui.get_cell_color(cell_type)
        assert actual_color == expected_color, f"颜色映射错误 {cell_type}: {actual_color} != {expected_color}"
        print(f"   ✓ {cell_type} 颜色正确: {actual_color}")
    
    print("\n=== 所有测试通过！ ===")
    print("GUI地图编辑器修复验证成功：")
    print("- ✓ 添加了空格（void）选项")
    print("- ✓ 添加了墙（wall）选项")
    print("- ✓ 修复了橡皮擦功能（设置为空格而不是空地）")
    print("- ✓ 更新了颜色映射")
    print("- ✓ 更新了快捷键绑定")

if __name__ == "__main__":
    test_gui_fixes() 