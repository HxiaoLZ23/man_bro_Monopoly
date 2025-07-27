#!/usr/bin/env python3
"""
背包和骰子系统测试脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.player import Player
from src.models.map import Map
from src.systems.player_manager import PlayerManager
from src.ui.inventory_window import InventoryWindow
from src.ui.dice_window import DiceWindow
from src.ui.target_selection_window import TargetSelectionWindow


def test_inventory_system():
    """测试背包系统"""
    print("=== 背包系统测试 ===")
    
    # 创建玩家
    player = Player(1, "测试玩家")
    
    # 给玩家一些道具
    player.add_item(1, 3)  # 3个路障
    player.add_item(2, 2)  # 2个飞行道具
    player.add_item(3, 1)  # 1个庇护术
    player.add_item(4, 2)  # 2个六百六十六
    
    print(f"玩家道具: {player.items}")
    
    # 测试道具使用
    print("\n1. 测试使用路障")
    result = player.use_item(1, target_pos=(5, 5), game=None)
    print(f"使用路障结果: {result}")
    
    print("\n2. 测试使用飞行道具")
    result = player.use_item(2, target_player=player)
    print(f"使用飞行道具结果: {result}")
    
    print("\n3. 测试使用庇护术")
    result = player.use_item(3)
    print(f"使用庇护术结果: {result}")
    
    print(f"剩余道具: {player.items}")
    print("背包系统测试完成！")


def test_dice_system():
    """测试骰子系统"""
    print("\n=== 骰子系统测试 ===")
    
    # 创建玩家
    player = Player(1, "测试玩家")
    
    # 给玩家一些骰子
    player.dice_system.add_dice_type("d8")
    player.dice_system.add_dice_type("d12")
    player.dice_system.add_dice_type("2d6")
    
    print(f"可用骰子: {player.dice_system.get_available_dice_types()}")
    print(f"当前骰子: {player.dice_system.get_current_dice_type()}")
    
    # 测试切换骰子
    print("\n1. 测试切换到d8")
    success = player.dice_system.set_current_dice("d8")
    print(f"切换结果: {success}")
    print(f"当前骰子: {player.dice_system.get_current_dice_type()}")
    
    # 测试投骰子
    print("\n2. 测试投骰子")
    result = player.dice_system.roll_current_dice_sum()
    print(f"投骰结果: {result}")
    
    print("\n3. 测试d12骰子")
    player.dice_system.set_current_dice("d12")
    result = player.dice_system.roll_current_dice_sum()
    print(f"d12投骰结果: {result}")
    
    print("骰子系统测试完成！")


def test_target_selection():
    """测试目标选择系统"""
    print("\n=== 目标选择系统测试 ===")
    
    # 创建地图
    game_map = Map(10, 10)
    
    # 创建玩家
    player = Player(1, "测试玩家")
    player.position = 5  # 设置玩家位置
    
    print(f"玩家位置: {player.position}")
    print(f"地图尺寸: {game_map.width}x{game_map.height}")
    
    # 测试路障目标选择
    print("\n1. 测试路障目标选择")
    target_window = TargetSelectionWindow(
        player, game_map, 1,  # 路障道具
        on_target_select=lambda info: print(f"选择目标: {info}")
    )
    
    # 测试飞行道具目标选择
    print("\n2. 测试飞行道具目标选择")
    fly_window = TargetSelectionWindow(
        player, game_map, 2,  # 飞行道具
        on_target_select=lambda info: print(f"选择目标: {info}")
    )
    
    print("目标选择系统测试完成！")


def test_integration():
    """测试集成功能"""
    print("\n=== 集成功能测试 ===")
    
    # 创建游戏管理器
    game_map = Map(10, 10)
    player_manager = PlayerManager(game_map)
    
    # 创建玩家
    player = player_manager.add_player("测试玩家")
    
    # 给玩家道具和骰子
    player.add_item(1, 2)  # 路障
    player.add_item(2, 1)  # 飞行道具
    player.add_item(3, 1)  # 庇护术
    
    player.dice_system.add_dice_type("d8")
    player.dice_system.add_dice_type("d12")
    
    print(f"玩家道具: {player.items}")
    print(f"可用骰子: {player.dice_system.get_available_dice_types()}")
    
    # 测试道具使用流程
    print("\n1. 测试路障使用流程")
    if player.has_item(1):
        # 模拟选择目标位置
        target_info = {
            "type": "roadblock",
            "position": (5, 5),
            "distance": 3.0
        }
        result = player.use_item(1, target_position=25, game=player_manager)
        print(f"路障使用结果: {result}")
    
    # 测试骰子切换流程
    print("\n2. 测试骰子切换流程")
    success = player.dice_system.set_current_dice("d8")
    if success:
        player.dice = "d8"
        print(f"成功切换到d8骰子")
    
    print("集成功能测试完成！")


def main():
    """主函数"""
    print("开始测试背包和骰子系统...")
    
    try:
        test_inventory_system()
        test_dice_system()
        test_target_selection()
        test_integration()
        
        print("\n✅ 所有测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 