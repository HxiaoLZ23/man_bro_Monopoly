#!/usr/bin/env python3
"""
骰子系统和骰子商店格测试脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.systems.dice_system import DiceSystem, Dice, DiceSet
from src.models.player import Player
from src.models.map import Map
from src.systems.player_manager import PlayerManager


def test_dice_system():
    """测试骰子系统"""
    print("=== 骰子系统测试 ===")
    
    # 创建骰子系统
    dice_system = DiceSystem()
    
    # 测试基础骰子
    print("\n1. 测试基础骰子")
    result = dice_system.roll_current_dice_sum()
    print(f"当前骰子(d6)投掷结果: {result}")
    assert 1 <= result <= 6
    
    # 测试添加骰子类型
    print("\n2. 测试添加骰子类型")
    dice_system.add_dice_type("d8")
    dice_system.add_dice_type("d12")
    print(f"可用骰子类型: {dice_system.get_available_dice_types()}")
    
    # 测试切换骰子
    print("\n3. 测试切换骰子")
    dice_system.set_current_dice("d8")
    result = dice_system.roll_current_dice_sum()
    print(f"d8骰子投掷结果: {result}")
    assert 1 <= result <= 8
    
    # 测试骰子价格
    print("\n4. 测试骰子价格")
    price = dice_system.get_dice_price("d8")
    print(f"d8骰子价格: {price}")
    assert price["money"] == 10000
    assert price["items"] == 1
    
    # 测试购买能力检查
    print("\n5. 测试购买能力检查")
    can_afford = dice_system.can_afford_dice("d8", 15000, 2)
    print(f"能否购买d8骰子: {can_afford}")
    assert can_afford == True
    
    print("骰子系统测试通过！")


def test_dice_shop():
    """测试骰子商店功能"""
    print("\n=== 骰子商店测试 ===")
    
    # 创建玩家
    player = Player(1, "测试玩家")
    player.add_money(50000)  # 给玩家一些钱
    player.add_item(1, 5)    # 给玩家一些道具
    
    # 创建骰子系统
    dice_system = DiceSystem()
    
    # 测试购买骰子
    print("\n1. 测试购买骰子")
    result = dice_system.buy_dice("d8", player)
    print(f"购买d8骰子结果: {result}")
    assert result["success"] == True
    
    # 检查玩家状态
    print(f"玩家金钱: {player.money}")
    print(f"玩家道具: {player.items}")
    print(f"可用骰子: {dice_system.get_available_dice_types()}")
    
    # 测试重复购买
    print("\n2. 测试重复购买")
    result = dice_system.buy_dice("d8", player)
    print(f"重复购买d8骰子结果: {result}")
    assert result["success"] == False
    
    # 测试购买更贵的骰子
    print("\n3. 测试购买d12骰子")
    result = dice_system.buy_dice("d12", player)
    print(f"购买d12骰子结果: {result}")
    assert result["success"] == True
    
    print("骰子商店测试通过！")


def test_dice_shop_cell():
    """测试骰子商店格"""
    print("\n=== 骰子商店格测试 ===")
    
    # 创建地图
    game_map = Map(10, 10)
    
    # 设置骰子商店格
    game_map.set_cell_type((5, 5), "dice_shop")
    
    # 创建玩家管理器
    player_manager = PlayerManager(game_map)
    player = player_manager.add_player("测试玩家")
    
    # 移动玩家到骰子商店格
    player.position = game_map.get_path_index_by_coordinates((5, 5))
    
    # 测试格子效果
    cell = game_map.get_cell_by_path_index(player.position)
    effect = player_manager._handle_cell_effect(player, cell)
    print(f"骰子商店格效果: {effect}")
    assert effect["type"] == "dice_shop"
    
    # 测试购买骰子
    print("\n1. 测试在骰子商店格购买骰子")
    player.add_money(50000)
    player.add_item(1, 5)
    
    result = player_manager.buy_dice(player, "d8")
    print(f"购买结果: {result}")
    assert result["success"] == True
    
    # 测试获取可用骰子
    print("\n2. 测试获取可用骰子")
    dice_info = player_manager.get_available_dice(player)
    print(f"骰子信息: {dice_info}")
    assert "d8" in dice_info["available_dice"]
    
    # 测试切换骰子
    print("\n3. 测试切换骰子")
    result = player_manager.set_player_dice(player, "d8")
    print(f"切换骰子结果: {result}")
    assert result["success"] == True
    assert player.dice == "d8"
    
    print("骰子商店格测试通过！")


def test_map_editor_dice_shop():
    """测试地图编辑器中的骰子商店格"""
    print("\n=== 地图编辑器骰子商店格测试 ===")
    
    from src.utils.map_editor import MapEditor
    
    # 创建地图编辑器
    editor = MapEditor()
    editor.create_new_map(10, 10)
    
    # 测试设置骰子商店格
    print("\n1. 测试设置骰子商店格")
    editor.set_cell_type(5, 5, "dice_shop")
    
    # 检查格子类型
    cell = editor.current_map.get_cell_at((5, 5))
    print(f"格子类型: {cell.cell_type}")
    assert cell.cell_type == "dice_shop"
    
    # 测试显示字符
    char = editor._get_cell_char(cell)
    print(f"显示字符: {char}")
    assert char == "D"
    
    # 测试保存和加载
    print("\n2. 测试保存和加载")
    editor.save_map("test_dice_shop_map.json")
    
    # 创建新编辑器加载地图
    editor2 = MapEditor()
    editor2.load_map("test_dice_shop_map.json")
    
    # 检查加载的格子
    cell2 = editor2.current_map.get_cell_at((5, 5))
    print(f"加载的格子类型: {cell2.cell_type}")
    assert cell2.cell_type == "dice_shop"
    
    print("地图编辑器骰子商店格测试通过！")


def main():
    """主测试函数"""
    print("开始骰子系统和骰子商店格测试...")
    
    try:
        test_dice_system()
        test_dice_shop()
        test_dice_shop_cell()
        test_map_editor_dice_shop()
        
        print("\n🎉 所有测试通过！骰子系统和骰子商店格功能正常。")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 