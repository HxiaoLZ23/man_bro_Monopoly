#!/usr/bin/env python3
"""
地图编辑器演示脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.map_editor import MapEditor


def demo_command_line_editor():
    """演示命令行编辑器"""
    print("=== 命令行地图编辑器演示 ===")
    editor = MapEditor()
    
    # 创建新地图
    print("\n1. 创建新地图 (15x15)")
    editor.create_new_map(15, 15)
    
    # 设置一些格子
    print("\n2. 设置特殊格子")
    editor.set_cell_type(2, 2, "bank")
    editor.set_cell_type(4, 4, "shop")
    editor.set_cell_type(7, 7, "jail")
    editor.set_cell_type(10, 10, "luck")
    editor.set_cell_type(12, 12, "bad_luck")
    
    # 放置路障
    print("\n3. 放置路障")
    editor.toggle_roadblock(5, 5)
    editor.toggle_roadblock(8, 8)
    
    # 设置房产
    print("\n4. 设置房产")
    editor.set_property(3, 3, 2, 1)
    editor.set_property(6, 6, 3, 2)
    
    # 显示地图
    print("\n5. 显示地图")
    editor.display_map()
    
    # 验证地图
    print("\n6. 验证地图")
    editor.validate_current_map()
    
    # 保存地图
    print("\n7. 保存地图")
    editor.save_map("demo_map.json")
    
    print("\n演示完成！")
    print("你可以运行以下命令启动图形化编辑器：")
    print("python src/utils/map_editor.py")
    print("然后在命令行中输入 'gui' 启动图形界面")


def demo_gui_editor():
    """演示图形化编辑器"""
    print("=== 图形化地图编辑器演示 ===")
    print("启动图形化编辑器...")
    
    try:
        editor = MapEditor()
        editor.run_gui_editor()
    except Exception as e:
        print(f"启动图形化编辑器失败: {e}")
        print("请确保系统支持tkinter")


def main():
    """主函数"""
    print("大富翁地图编辑器演示")
    print("=" * 50)
    
    while True:
        print("\n请选择演示模式：")
        print("1. 命令行编辑器演示")
        print("2. 图形化编辑器演示")
        print("3. 退出")
        
        choice = input("\n请输入选择 (1-3): ").strip()
        
        if choice == "1":
            demo_command_line_editor()
        elif choice == "2":
            demo_gui_editor()
        elif choice == "3":
            print("再见！")
            break
        else:
            print("无效选择，请重新输入")


if __name__ == "__main__":
    main() 