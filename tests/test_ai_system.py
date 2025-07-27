"""
AI系统测试脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

from src.systems.player_manager import PlayerManager
from src.models.map import Map
from src.models.player import Player


def test_ai_basic_decision():
    """测试AI基础决策"""
    print("=== 测试AI基础决策 ===")
    
    # 创建游戏地图和玩家管理器
    game_map = Map(5, 5)
    player_manager = PlayerManager(game_map)
    
    # 创建AI玩家
    ai_player = player_manager.add_player("AI测试", is_ai=True)
    print(f"创建AI玩家: {ai_player.name}")
    print(f"AI玩家初始资金: {ai_player.money}")
    print(f"AI玩家初始道具: {ai_player.items}")
    
    # 测试AI决策
    result = player_manager.ai_decision(ai_player)
    print(f"AI决策结果: {result}")
    
    if result["success"]:
        decisions = result["decisions"]
        print("\nAI决策详情:")
        for key, value in decisions.items():
            print(f"  {key}: {value}")
    else:
        print(f"AI决策失败: {result['msg']}")


def test_ai_property_decision():
    """测试AI房产决策"""
    print("\n=== 测试AI房产决策 ===")
    
    game_map = Map(5, 5)
    player_manager = PlayerManager(game_map)
    ai_player = player_manager.add_player("AI测试", is_ai=True)
    
    # 给AI玩家一些资金
    ai_player.money = 50000
    
    # 测试购买房产决策
    result = player_manager.buy_property_decision(ai_player, 0, True)
    print(f"AI购买房产决策: {result}")
    
    # 测试升级房产决策
    result = player_manager.upgrade_property_decision(ai_player, 0, True)
    print(f"AI升级房产决策: {result}")


def test_ai_item_decision():
    """测试AI道具决策"""
    print("\n=== 测试AI道具决策 ===")
    
    game_map = Map(5, 5)
    player_manager = PlayerManager(game_map)
    ai_player = player_manager.add_player("AI测试", is_ai=True)
    
    # 给AI玩家一些道具
    ai_player.add_item(1, 2)  # 路障
    ai_player.add_item(2, 1)  # 飞行卡
    
    print(f"AI玩家道具: {ai_player.items}")
    
    # 测试使用道具决策
    result = player_manager.use_item_decision(ai_player, 1)
    print(f"AI使用道具决策: {result}")


def test_ai_shop_decision():
    """测试AI商店决策"""
    print("\n=== 测试AI商店决策 ===")
    
    game_map = Map(5, 5)
    player_manager = PlayerManager(game_map)
    ai_player = player_manager.add_player("AI测试", is_ai=True)
    
    # 给AI玩家一些资金
    ai_player.money = 50000
    
    # 测试道具商店决策
    affordable_items = player_manager.get_affordable_items(ai_player)
    print(f"AI可购买道具: {affordable_items}")
    
    if affordable_items:
        # 模拟AI购买决策
        import random
        if random.random() < 0.5:
            item_name = random.choice(affordable_items)
            result = player_manager.buy_shop_item(ai_player, item_name)
            print(f"AI购买道具: {result}")


def test_ai_movement():
    """测试AI移动"""
    print("\n=== 测试AI移动 ===")
    
    game_map = Map(5, 5)
    player_manager = PlayerManager(game_map)
    ai_player = player_manager.add_player("AI测试", is_ai=True)
    
    print(f"AI初始位置: {ai_player.position}")
    
    # 测试AI投掷骰子
    dice_result = player_manager.roll_dice(ai_player)
    print(f"AI投掷骰子: {dice_result}")
    
    # 测试AI移动
    if "dice_result" in dice_result:
        move_result = player_manager.move_player(ai_player, dice_result["dice_result"])
        print(f"AI移动结果: {move_result}")
        print(f"AI最终位置: {ai_player.position}")


def test_ai_comprehensive():
    """综合测试AI系统"""
    print("\n=== 综合测试AI系统 ===")
    
    game_map = Map(5, 5)
    player_manager = PlayerManager(game_map)
    
    # 创建多个AI玩家
    ai_players = []
    for i in range(3):
        ai = player_manager.add_player(f"AI{i+1}", is_ai=True)
        ai_players.append(ai)
    
    print(f"创建了 {len(ai_players)} 个AI玩家")
    
    # 模拟几个回合的AI行为
    for round_num in range(3):
        print(f"\n--- 第 {round_num + 1} 回合 ---")
        
        for ai in ai_players:
            print(f"\n{ai.name} 的回合:")
            
            # AI决策
            ai_result = player_manager.ai_decision(ai)
            if ai_result["success"]:
                decisions = ai_result["decisions"]
                
                # 执行移动
                if "dice" in decisions:
                    dice_result = decisions["dice"]
                    print(f"  投掷骰子: {dice_result}")
                    
                    move_result = player_manager.move_player(ai, dice_result)
                    print(f"  移动结果: {move_result['msg']}")
                    print(f"  当前位置: {ai.position}")
                
                # 执行购买决策
                if "buy_property" in decisions:
                    result = player_manager.buy_property_decision(ai, ai.position, True)
                    print(f"  购买房产: {result['msg']}")
                
                # 执行道具使用决策
                if "use_item" in decisions:
                    item_id = decisions["use_item"]
                    result = player_manager.use_item_decision(ai, item_id)
                    print(f"  使用道具: {result['msg']}")
            
            # 结束回合
            player_manager.end_turn()
    
    # 显示最终状态
    print(f"\n=== 最终状态 ===")
    for ai in ai_players:
        print(f"{ai.name}: 位置={ai.position}, 资金={ai.money}, 道具={ai.items}, 房产数={len(ai.properties)}")


if __name__ == "__main__":
    print("🎲 AI系统测试开始")
    
    try:
        test_ai_basic_decision()
        test_ai_property_decision()
        test_ai_item_decision()
        test_ai_shop_decision()
        test_ai_movement()
        test_ai_comprehensive()
        
        print("\n✅ AI系统测试完成")
        
    except Exception as e:
        print(f"\n❌ AI系统测试失败: {e}")
        import traceback
        traceback.print_exc() 