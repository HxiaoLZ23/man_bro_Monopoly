#!/usr/bin/env python3
"""
测试改进后的地图编辑器
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.map_editor import MapEditor


def test_improved_editor():
    """测试改进后的编辑器"""
    print("=== 测试改进后的地图编辑器 ===")
    print("启动图形化编辑器...")
    print()
    print("测试步骤：")
    print("1. 点击 '文件' -> '新建地图' 或按 Ctrl+N")
    print("2. 在对话框中输入地图尺寸（如 15x15）")
    print("3. 点击确定")
    print("4. 应该会看到：")
    print("   - 状态栏显示创建进度")
    print("   - 成功消息弹窗")
    print("   - 地图显示在画布上")
    print("   - 工具栏显示地图信息")
    print()
    print("如果一切正常，说明新建地图功能已修复！")
    
    try:
        editor = MapEditor()
        editor.run_gui_editor()
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_improved_editor() 