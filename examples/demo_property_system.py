#!/usr/bin/env python3
"""
房产系统演示脚本
展示房产购买、升级、收租、转移等功能
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.map import Map
from models.player import Player
from models.property import Property
from systems.property_manager import PropertyManager
from core.constants import PROPERTY_LEVELS


def demo_property_system():
    """演示房产系统功能"""
    print("=== 房产系统演示 ===\n")
    
    # 1. 创建游戏地图和房产管理器
    print("1. 创建游戏地图和房产管理器...")
    game_map = Map(5, 5)
    property_manager = PropertyManager(game_map)
    
    # 2. 创建玩家
    print("2. 创建玩家...")
    player1 = Player(player_id=1, name="张三")
    player2 = Player(player_id=2, name="李四")
    
    # 设置初始资金
    player1.money = 100000
    player2.money = 80000
    
    print(f"   {player1.name}: {player1.money}元")
    print(f"   {player2.name}: {player2.money}元\n")
    
    # 3. 设置测试房产
    print("3. 设置测试房产...")
    setup_demo_properties(game_map, property_manager)
    
    # 4. 演示购买房产
    print("4. 演示购买房产...")
    demo_buy_property(property_manager, player1, player2)
    
    # 5. 演示升级房产
    print("\n5. 演示升级房产...")
    demo_upgrade_property(property_manager, player1)
    
    # 6. 演示支付租金
    print("\n6. 演示支付租金...")
    demo_pay_rent(property_manager, player1, player2)
    
    # 7. 演示转移房产
    print("\n7. 演示转移房产...")
    demo_transfer_property(property_manager, player1, player2)
    
    # 8. 演示强制升级/降级（道具效果）
    print("\n8. 演示强制升级/降级（道具效果）...")
    demo_force_upgrade_downgrade(property_manager)
    
    # 9. 演示房产统计
    print("\n9. 演示房产统计...")
    demo_property_statistics(property_manager)
    
    # 10. 演示玩家资产
    print("\n10. 演示玩家资产...")
    demo_player_assets(player1, player2)
    
    print("\n=== 演示完成 ===")


def setup_demo_properties(game_map, property_manager):
    """设置演示用的房产"""
    # 在坐标(1,1)设置空地
    cell = game_map.get_cell_at((1, 1))
    if cell:
        cell.cell_type = "empty"
        property_obj = Property(position=1 * 5 + 1, level=0)
        cell.set_property(property_obj)
    
    # 在坐标(2,2)设置空地
    cell = game_map.get_cell_at((2, 2))
    if cell:
        cell.cell_type = "empty"
        property_obj = Property(position=2 * 5 + 2, level=0)
        cell.set_property(property_obj)
    
    # 在坐标(3,3)设置有主房产
    cell = game_map.get_cell_at((3, 3))
    if cell:
        cell.cell_type = "empty"
        property_obj = Property(position=3 * 5 + 3, owner_id=1, level=2)
        cell.set_property(property_obj)
    
    # 重新初始化房产管理器
    property_manager._initialize_properties()
    
    print(f"   创建了 {len(property_manager.properties)} 个房产")
    print(f"   空地: {len(property_manager.get_empty_properties())} 个")
    print(f"   有主房产: {len(property_manager.get_owned_properties())} 个")


def demo_buy_property(property_manager, player1, player2):
    """演示购买房产"""
    print(f"   {player1.name} 尝试购买房产...")
    
    # 购买第一个空地
    result = property_manager.buy_property(player1, 6)  # (1,1)
    if result["success"]:
        print(f"   ✓ {result['msg']}")
        print(f"   花费: {result['cost']}元")
        print(f"   剩余资金: {player1.money}元")
    else:
        print(f"   ✗ {result['msg']}")
    
    # 尝试购买已有所有者的房产
    print(f"\n   {player2.name} 尝试购买已有所有者的房产...")
    result = property_manager.buy_property(player2, 18)  # (3,3)
    if result["success"]:
        print(f"   ✓ {result['msg']}")
    else:
        print(f"   ✗ {result['msg']}")
    
    # 尝试购买不存在的房产
    print(f"\n   {player2.name} 尝试购买不存在的房产...")
    result = property_manager.buy_property(player2, 999)
    if result["success"]:
        print(f"   ✓ {result['msg']}")
    else:
        print(f"   ✗ {result['msg']}")


def demo_upgrade_property(property_manager, player1):
    """演示升级房产"""
    print(f"   {player1.name} 尝试升级房产...")
    
    # 升级自己的房产
    result = property_manager.upgrade_property(player1, 18)  # (3,3)
    if result["success"]:
        print(f"   ✓ {result['msg']}")
        print(f"   花费: {result['cost']}元")
        print(f"   剩余资金: {player1.money}元")
    else:
        print(f"   ✗ {result['msg']}")
    
    # 尝试升级不存在的房产
    print(f"\n   {player1.name} 尝试升级不存在的房产...")
    result = property_manager.upgrade_property(player1, 999)
    if result["success"]:
        print(f"   ✓ {result['msg']}")
    else:
        print(f"   ✗ {result['msg']}")


def demo_pay_rent(property_manager, player1, player2):
    """演示支付租金"""
    print(f"   {player2.name} 经过 {player1.name} 的房产，需要支付租金...")
    
    # 支付租金
    result = property_manager.pay_rent(player2, 18)  # (3,3)
    if result["success"]:
        print(f"   ✓ {result['msg']}")
        print(f"   租金: {result['rent']}元")
        print(f"   {player2.name} 剩余资金: {player2.money}元")
    else:
        print(f"   ✗ {result['msg']}")
    
    # 尝试向自己支付租金
    print(f"\n   {player1.name} 尝试向自己支付租金...")
    result = property_manager.pay_rent(player1, 18)
    if result["success"]:
        print(f"   ✓ {result['msg']}")
    else:
        print(f"   ✗ {result['msg']}")


def demo_transfer_property(property_manager, player1, player2):
    """演示转移房产"""
    print(f"   {player1.name} 将房产转移给 {player2.name}...")
    
    # 转移房产
    result = property_manager.transfer_property(player1, player2, 18)
    if result["success"]:
        print(f"   ✓ {result['msg']}")
        
        # 检查转移结果
        prop = property_manager.get_property_at_position(18)
        print(f"   房产新所有者: {prop.owner_id}")
        print(f"   {player1.name} 房产数量: {len(player1.properties)}")
        print(f"   {player2.name} 房产数量: {len(player2.properties)}")
    else:
        print(f"   ✗ {result['msg']}")


def demo_force_upgrade_downgrade(property_manager):
    """演示强制升级/降级"""
    print("   使用道具强制升级房产...")
    
    # 强制升级
    result = property_manager.force_upgrade_property(18)
    if result["success"]:
        print(f"   ✓ {result['msg']}")
        
        prop = property_manager.get_property_at_position(18)
        print(f"   房产等级: {prop.level}")
    else:
        print(f"   ✗ {result['msg']}")
    
    print("\n   使用道具强制降级房产...")
    
    # 强制降级
    result = property_manager.force_downgrade_property(18)
    if result["success"]:
        print(f"   ✓ {result['msg']}")
        
        prop = property_manager.get_property_at_position(18)
        print(f"   房产等级: {prop.level}")
    else:
        print(f"   ✗ {result['msg']}")


def demo_property_statistics(property_manager):
    """演示房产统计"""
    stats = property_manager.get_property_statistics()
    
    print(f"   总房产数: {stats['total_properties']}")
    print(f"   有主房产: {stats['owned_properties']}")
    print(f"   空地: {stats['empty_properties']}")
    
    print("\n   按等级统计:")
    for level, count in stats['level_statistics'].items():
        level_name = {0: "空地", 1: "一级", 2: "二级", 3: "三级", 4: "四级"}[level]
        print(f"     {level_name}: {count} 个")
    
    print("\n   按所有者统计:")
    for owner_id, count in stats['owner_statistics'].items():
        print(f"     玩家{owner_id}: {count} 个")


def demo_player_assets(player1, player2):
    """演示玩家资产"""
    print(f"   {player1.name} 资产情况:")
    print(f"     现金: {player1.money}元")
    print(f"     银行: {player1.bank_money}元")
    print(f"     房产: {len(player1.properties)} 个")
    total_assets1 = player1.get_total_assets()
    print(f"     总资产: {total_assets1}元")
    
    print(f"\n   {player2.name} 资产情况:")
    print(f"     现金: {player2.money}元")
    print(f"     银行: {player2.bank_money}元")
    print(f"     房产: {len(player2.properties)} 个")
    total_assets2 = player2.get_total_assets()
    print(f"     总资产: {total_assets2}元")
    
    print(f"\n   资产对比:")
    if total_assets1 > total_assets2:
        print(f"     {player1.name} 更富有")
    elif total_assets2 > total_assets1:
        print(f"     {player2.name} 更富有")
    else:
        print("     两人资产相等")


if __name__ == "__main__":
    demo_property_system() 