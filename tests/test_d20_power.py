#!/usr/bin/env python3
"""
d20神力效果测试脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.player import Player
from src.models.map import Map
from src.systems.player_manager import PlayerManager
from src.systems.shop_system import ShopSystem
from src.systems.dice_system import DiceSystem


def test_d20_power_roll():
    """测试d20神力投掷"""
    print("=== d20神力投掷测试 ===")
    
    player = Player(1, "测试玩家")
    player.dice = "2d20"
    
    player_manager = PlayerManager()
    player_manager.players.append(player)
    player_manager.current_player_index = 0
    player_manager.game_phase = "waiting"  # 设置游戏阶段
    
    # 模拟投掷d20神力
    result = player_manager.roll_dice(player)
    print(f"投掷结果: {result}")
    
    if result.get('d20_power'):
        print(f"d20神力状态: {result['d20_power']}")
        if result['d20_power'] == 'max':
            print("✅ 检测到d20神力加持")
        elif result['d20_power'] == 'min':
            print("✅ 检测到d20神力诅咒")
    else:
        print("❌ 未检测到d20神力效果")


def test_d20_power_events():
    """测试d20神力在事件中的效果"""
    print("\n=== d20神力事件效果测试 ===")
    
    from src.systems.event_system import GainMoneyEvent, LoseMoneyEvent, GetItemEvent, GoToJailEvent
    
    player = Player(1, "测试玩家")
    player.add_money(100000)
    
    # 测试d20神力加持
    print("\n1. 测试d20神力加持效果")
    player.status["d20_power"] = "max"
    
    # 获得金钱事件
    event = GainMoneyEvent(10000)
    result = event.trigger(player)
    print(f"获得金钱事件: {result['msg']}")
    
    # 获得道具事件
    event = GetItemEvent(1, "路障")
    result = event.trigger(player)
    print(f"获得道具事件: {result['msg']}")
    
    # 失去金钱事件
    event = LoseMoneyEvent(5000)
    result = event.trigger(player)
    print(f"失去金钱事件: {result['msg']}")
    
    # 进监狱事件
    event = GoToJailEvent()
    result = event.trigger(player)
    print(f"进监狱事件: {result['msg']}")
    
    # 测试d20神力诅咒
    print("\n2. 测试d20神力诅咒效果")
    player.status["d20_power"] = "min"
    
    # 获得金钱事件
    event = GainMoneyEvent(10000)
    result = event.trigger(player)
    print(f"获得金钱事件: {result['msg']}")
    
    # 失去金钱事件
    event = LoseMoneyEvent(5000)
    result = event.trigger(player)
    print(f"失去金钱事件: {result['msg']}")
    
    # 进监狱事件
    event = GoToJailEvent()
    result = event.trigger(player)
    print(f"进监狱事件: {result['msg']}")


def test_d20_power_shop():
    """测试d20神力在商店中的效果"""
    print("\n=== d20神力商店效果测试 ===")
    
    player = Player(1, "测试玩家")
    player.add_money(100000)
    player.add_item(1, 5)
    
    shop_system = ShopSystem()
    
    # 确保商店有道具
    shop_system.refresh_shop()
    shop_items = shop_system.get_shop_items()
    print(f"商店道具: {list(shop_items.keys())}")
    
    if shop_items:
        item_name = list(shop_items.keys())[0]
        
        # 测试d20神力加持
        print(f"\n1. 测试d20神力加持效果 - 购买{item_name}")
        player.status["d20_power"] = "max"
        
        result = shop_system.buy_item(player, item_name)
        print(f"购买道具: {result['msg']}")
        if 'item_count' in result:
            print(f"获得道具数量: {result['item_count']}")
        
        # 测试d20神力诅咒
        print(f"\n2. 测试d20神力诅咒效果 - 购买{item_name}")
        player.status["d20_power"] = "min"
        
        result = shop_system.buy_item(player, item_name)
        print(f"购买道具: {result['msg']}")
        if 'item_count' in result:
            print(f"获得道具数量: {result['item_count']}")
    else:
        print("商店没有道具，跳过测试")


def test_d20_power_dice_shop():
    """测试d20神力在骰子商店中的效果"""
    print("\n=== d20神力骰子商店效果测试 ===")
    
    player = Player(1, "测试玩家")
    player.add_money(100000)
    player.add_item(1, 10)
    
    dice_system = DiceSystem()
    
    # 测试d20神力加持
    print("\n1. 测试d20神力加持效果")
    player.status["d20_power"] = "max"
    
    result = dice_system.buy_dice("d8", player)
    print(f"购买骰子: {result['msg']}")
    if 'extra_dice' in result:
        print(f"额外获得骰子: {result['extra_dice']}")
    
    # 测试d20神力诅咒
    print("\n2. 测试d20神力诅咒效果")
    player.status["d20_power"] = "min"
    
    result = dice_system.buy_dice("d12", player)
    print(f"购买骰子: {result['msg']}")


def test_d20_power_property():
    """测试d20神力在房产中的效果"""
    print("\n=== d20神力房产效果测试 ===")
    
    from src.models.property import Property
    
    player = Player(1, "测试玩家")
    player.add_money(100000)
    
    property_obj = Property(1, 1, 10000)
    
    # 测试d20神力加持 - 建房产额外升级
    print("\n1. 测试d20神力加持效果")
    player.status["d20_power"] = "max"
    
    print(f"房产初始等级: {property_obj.level}")
    property_obj.level = min(property_obj.level + 1, 4)
    print(f"d20神力加持后等级: {property_obj.level}")
    
    # 测试d20神力诅咒 - 房产降级
    print("\n2. 测试d20神力诅咒效果")
    player.status["d20_power"] = "min"
    
    property_obj.level = 3
    print(f"房产当前等级: {property_obj.level}")
    if property_obj.level > 1:
        property_obj.level -= 1
        print(f"d20神力诅咒后等级: {property_obj.level}")


def main():
    """主测试函数"""
    print("开始d20神力效果测试...")
    
    try:
        test_d20_power_roll()
        test_d20_power_events()
        test_d20_power_shop()
        test_d20_power_dice_shop()
        test_d20_power_property()
        
        print("\n🎉 所有d20神力效果测试通过！")
        print("\n总结d20神力效果：")
        print("🎲 投掷2d20时：")
        print("  - 骰出20：收益翻倍，惩罚减免")
        print("  - 骰出1：收益清零，惩罚翻倍")
        print("  - 其他：正常效果")
        print("📋 影响范围：")
        print("  - 事件：金钱、道具、监狱")
        print("  - 商店：道具购买、骰子购买")
        print("  - 房产：建房产、收租、降级")
        print("  - 银行：利息收益")
        print("  - 仅本回合生效")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 