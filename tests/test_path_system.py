"""
路径系统测试脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

from src.models.map import Map
from src.models.player import Player
from src.utils.map_editor import MapEditor


def test_basic_path_system():
    """测试基本路径系统"""
    print("=== 测试基本路径系统 ===")
    
    # 创建地图
    game_map = Map(10, 10)
    print(f"地图大小: {game_map.width}x{game_map.height}")
    print(f"路径长度: {game_map.path_length}")
    
    # 显示路径信息
    print("\n路径信息:")
    for i, (x, y) in enumerate(game_map.path):
        cell = game_map.get_cell_by_path_index(i)
        connections = list(cell.connections) if cell else []
        print(f"  索引 {i}: 位置 ({x}, {y}), 连接: {connections}")
    
    # 测试移动
    print("\n=== 测试基本移动 ===")
    player = Player(1, "测试玩家")
    player.position = 0
    
    # 移动3步
    result = player.move_along_path(game_map, 3)
    print(f"移动结果: {result}")
    print(f"玩家位置: {player.position}")
    
    # 移动5步
    result = player.move_along_path(game_map, 5)
    print(f"移动结果: {result}")
    print(f"玩家位置: {player.position}")


def test_junction_system():
    """测试岔路口系统"""
    print("\n=== 测试岔路口系统 ===")
    
    # 创建地图
    game_map = Map(10, 10)
    
    # 添加一个岔路连接（从索引0到索引20）
    success = game_map.add_path_connection(0, 20)
    print(f"添加岔路连接 0->20: {success}")
    
    # 显示岔路口信息
    print(f"岔路口数量: {len(game_map.junctions)}")
    for junction_index in game_map.junctions:
        pos = game_map.get_position_by_path_index(junction_index)
        cell = game_map.get_cell_by_path_index(junction_index)
        connections = list(cell.connections) if cell else []
        print(f"  岔路口 {junction_index}: 位置 {pos}, 连接: {connections}")
    
    # 测试在岔路口的移动
    player = Player(1, "测试玩家")
    player.position = 0
    
    # 获取可用方向
    directions = player.get_available_directions(game_map)
    print(f"位置0的可用方向: {directions}")
    
    # 选择方向移动
    result = player.move_along_path(game_map, 1, [20])  # 选择方向20
    print(f"选择方向20移动: {result}")
    print(f"玩家位置: {player.position}")


def test_path_editor():
    """测试路径编辑器"""
    print("\n=== 测试路径编辑器 ===")
    
    # 创建编辑器
    editor = MapEditor()
    editor.create_new_map(8, 8)
    
    # 显示地图
    print("初始地图:")
    editor.display_map()
    
    # 显示路径信息
    editor.display_path_info()
    
    # 添加岔路连接
    print("\n添加岔路连接:")
    editor.add_path_connection(5, 15)
    
    # 显示更新后的地图
    print("\n更新后的地图:")
    editor.display_map()
    
    # 测试路径移动
    print("\n测试路径移动:")
    editor.test_path_movement(0, 3, [5])  # 从位置0移动3步，选择方向5


def test_player_movement():
    """测试玩家移动"""
    print("\n=== 测试玩家移动 ===")
    
    # 创建地图和玩家
    game_map = Map(8, 8)
    player = Player(1, "测试玩家")
    
    # 设置玩家位置
    player.position = 0
    print(f"玩家初始位置: {player.position}")
    
    # 获取位置坐标
    coords = player.get_position_coordinates(game_map)
    print(f"玩家坐标: {coords}")
    
    # 移动玩家
    result = player.move_along_path(game_map, 4)
    print(f"移动结果: {result}")
    print(f"玩家新位置: {player.position}")
    
    # 获取新位置坐标
    coords = player.get_position_coordinates(game_map)
    print(f"玩家新坐标: {coords}")
    
    # 显示移动历史
    history = player.get_movement_history()
    print(f"移动历史: {history}")


def test_roadblock_system():
    """测试路障系统"""
    print("\n=== 测试路障系统 ===")
    
    # 创建地图
    game_map = Map(8, 8)
    
    # 在路径上放置路障
    success = game_map.place_roadblock((2, 0))  # 在索引2的位置放置路障
    print(f"在位置(2,0)放置路障: {success}")
    
    # 测试移动（应该被路障阻挡）
    player = Player(1, "测试玩家")
    player.position = 0
    
    result = player.move_along_path(game_map, 5)
    print(f"移动5步结果: {result}")
    print(f"玩家最终位置: {player.position}")
    
    # 移除路障
    success = game_map.remove_roadblock((2, 0))
    print(f"移除路障: {success}")
    
    # 再次测试移动
    player.position = 0
    result = player.move_along_path(game_map, 5)
    print(f"移除路障后移动5步结果: {result}")
    print(f"玩家最终位置: {player.position}")


def test_complex_path():
    """测试复杂路径"""
    print("\n=== 测试复杂路径 ===")
    
    # 创建地图
    game_map = Map(8, 8)
    
    # 添加多个岔路连接
    connections = [(0, 10), (5, 15), (10, 20)]
    for from_idx, to_idx in connections:
        success = game_map.add_path_connection(from_idx, to_idx)
        print(f"添加连接 {from_idx}->{to_idx}: {success}")
    
    # 显示岔路口信息
    print(f"岔路口数量: {len(game_map.junctions)}")
    for junction_idx in sorted(game_map.junctions):
        pos = game_map.get_position_by_path_index(junction_idx)
        cell = game_map.get_cell_by_path_index(junction_idx)
        connections = list(cell.connections) if cell else []
        print(f"  岔路口 {junction_idx}: 位置 {pos}, 连接: {connections}")
    
    # 测试复杂路径移动
    player = Player(1, "测试玩家")
    player.position = 0
    
    # 测试不同方向的移动
    test_cases = [
        (3, [1, 2, 3]),  # 正常移动
        (5, [10, 11, 12]),  # 通过岔路
        (2, [5, 15, 16]),  # 另一个岔路
    ]
    
    for steps, expected_path in test_cases:
        player.position = 0
        result = player.move_along_path(game_map, steps)
        print(f"移动{steps}步: 路径={result['path_taken']}, 最终位置={result['final_position']}")


def main():
    """主函数"""
    print("开始测试路径系统...")
    
    try:
        test_basic_path_system()
        test_junction_system()
        test_roadblock_system()
        test_complex_path()
        test_path_editor()
        test_player_movement()
        
        print("\n=== 所有测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 