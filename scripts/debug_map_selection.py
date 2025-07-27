#!/usr/bin/env python3
"""
地图选择功能调试脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

def test_map_selection():
    """测试地图选择功能"""
    print("🔍 测试地图选择功能...")
    
    try:
        from src.ui.main_window import MainWindow
        print("✅ MainWindow 导入成功")
        
        # 创建主窗口实例
        window = MainWindow()
        print("✅ MainWindow 实例创建成功")
        
        # 测试默认地图选择
        print("\n📋 测试默认地图选择...")
        print(f"初始 selected_map: {window.selected_map}")
        print(f"初始 game_map: {window.game_map}")
        
        # 选择默认地图
        window.select_map("default")
        print(f"选择默认地图后 selected_map: {window.selected_map}")
        print(f"选择默认地图后 game_map: {window.game_map}")
        
        # 测试自定义地图加载
        print("\n📋 测试自定义地图加载...")
        
        # 检查demo_map.json是否存在
        if os.path.exists("demo_map.json"):
            print("✅ demo_map.json 文件存在")
            
            # 模拟加载自定义地图
            from src.systems.map_data_manager import MapDataManager
            map_manager = MapDataManager()
            
            try:
                loaded_map = map_manager.load_map('json', "demo_map.json")
                print("✅ 地图加载成功")
                
                # 手动设置地图状态
                window.game_map = loaded_map
                window.selected_map = "custom"
                window.custom_map_path = "demo_map.json"
                
                print(f"设置自定义地图后 selected_map: {window.selected_map}")
                print(f"设置自定义地图后 game_map: {window.game_map}")
                print(f"设置自定义地图后 custom_map_path: {window.custom_map_path}")
                
                # 重新初始化设置场景
                window.init_game_setup_scene()
                print("✅ 重新初始化设置场景完成")
                
            except Exception as e:
                print(f"❌ 地图加载失败: {e}")
        else:
            print("❌ demo_map.json 文件不存在")
        
        print("\n✅ 地图选择功能测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_map_selection() 