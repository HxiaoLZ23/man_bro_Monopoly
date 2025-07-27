#!/usr/bin/env python3
"""
为位置3添加真正的分支路径
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def add_branch_path():
    """为位置3添加分支路径"""
    print("=== 为位置3添加分支路径 ===")
    
    try:
        from src.utils.map_editor import MapEditor
        
        # 创建地图编辑器
        editor = MapEditor()
        
        # 加载当前地图
        success = editor.load_map("2.json")
        if not success:
            print("❌ 加载地图失败")
            return
        
        print("✅ 成功加载地图")
        
        # 显示当前路径信息
        print("\n--- 修改前的路径信息 ---")
        editor.display_path_info()
        
        # 为位置3添加分支路径
        # 我们可以连接到地图中的其他位置，比如位置10（右下角）
        print("\n--- 添加分支路径 ---")
        
        # 方案1：连接位置3到位置15（地图右边中间位置）
        success1 = editor.add_path_connection(3, 15)
        print(f"添加连接 3->15: {success1}")
        
        # 方案2：连接位置3到位置25（地图下边中间位置）  
        success2 = editor.add_path_connection(3, 25)
        print(f"添加连接 3->25: {success2}")
        
        # 显示修改后的路径信息
        print("\n--- 修改后的路径信息 ---")
        editor.display_path_info()
        
        # 测试从位置3的可用方向
        print("\n--- 测试位置3的可用方向 ---")
        directions = editor.get_available_directions(3)
        print(f"位置3的可用方向: {directions}")
        
        # 保存修改后的地图
        backup_success = editor.save_map("2_with_branches.json")
        if backup_success:
            print("✅ 已保存修改后的地图到: 2_with_branches.json")
        
        print("\n=== 完成 ===")
        print("现在位置3有了真正的分支路径：")
        print("- 方向2：回到上一个位置（回头路）")
        print("- 方向4：继续主路径")
        print("- 方向15：分支路径1")
        print("- 方向25：分支路径2")
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_branch_path() 