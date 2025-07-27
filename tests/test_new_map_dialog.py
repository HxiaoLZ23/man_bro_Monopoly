#!/usr/bin/env python3
"""
测试新建地图对话框功能
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.map_editor import MapEditor


def test_new_map_dialog():
    """测试新建地图对话框"""
    print("测试新建地图对话框功能...")
    
    try:
        # 创建编辑器
        editor = MapEditor()
        
        # 启动图形化编辑器
        print("启动图形化编辑器...")
        print("请点击 '文件' -> '新建地图' 来测试对话框功能")
        print("或者按 Ctrl+N 快捷键")
        print("输入地图尺寸后点击确定，应该会创建新地图并显示在画布上")
        
        editor.run_gui_editor()
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_new_map_dialog() 