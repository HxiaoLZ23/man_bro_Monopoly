#!/usr/bin/env python3
"""
大富翁游戏主程序
"""
import sys
import os
import random

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.map import Map
from src.systems.player_manager import PlayerManager


def display_player_status(player):
    """显示玩家状态"""
    print(f"\n=== {player.name} 状态 ===")
    print(f"金钱: {player.money:,} 银行: {player.bank_money:,}")
    print(f"位置: {player.position} 骰子: {player.dice}")
    print(f"道具: {player.items}")
    print(f"房产数: {len(player.properties)}")


def handle_item_shop(player_manager, player):
    """处理道具商店"""
    print(f"\n🏪 欢迎来到道具商店！")
    print(f"你的金钱: {player.money:,}")
    
    shop_items = player_manager.get_shop_items()
    
    if not shop_items:
        print("商店暂时没有道具...")
        return
    
    print("\n当前商店道具:")
    for i, (item_name, item_info) in enumerate(shop_items.items(), 1):
        affordable = player_manager.shop_system.can_afford_item(player, item_name)
        status = "✅ 可购买" if affordable else "❌ 金钱不足"
        print(f"{i}. {item_name} - {item_info['price']:,}元 ({item_info['stock']}个库存) {status}")
        print(f"   描述: {item_info['description']}")
    
    while True:
        print("\n选择操作:")
        print("1-2: 购买对应道具")
        print("r: 刷新商店")
        print("q: 离开商店")
        
        choice = input("请输入选择: ").strip().lower()
        
        if choice == 'q':
            print("离开商店")
            break
        elif choice == 'r':
            result = player_manager.refresh_shop()
            print(result["msg"])
            return handle_item_shop(player_manager, player)
        elif choice in ['1', '2']:
            item_names = list(shop_items.keys())
            if 1 <= int(choice) <= len(item_names):
                item_name = item_names[int(choice) - 1]
                result = player_manager.buy_shop_item(player, item_name)
                print(result["msg"])
                if result["success"]:
                    print(f"剩余库存: {result['remaining_stock']}")
                    display_player_status(player)
            else:
                print("无效选择")
        else:
            print("无效选择")


def handle_dice_shop(player_manager, player):
    """处理骰子商店"""
    print(f"\n🎲 欢迎来到骰子商店！")
    print(f"你的金钱: {player.money:,} 道具数: {len(player.items)}")
    
    dice_info = player_manager.get_available_dice(player)
    
    print(f"\n当前骰子: {dice_info['current_dice']}")
    print(f"已拥有骰子: {dice_info['available_dice']}")
    
    shop_dice = dice_info['shop_dice']
    if not shop_dice:
        print("没有可购买的骰子...")
        return
    
    print("\n可购买的骰子:")
    for i, dice in enumerate(shop_dice, 1):
        can_afford = player_manager.dice_system.can_afford_dice(
            dice["type"], player.money, len(player.items)
        )
        status = "✅ 可购买" if can_afford else "❌ 资源不足"
        print(f"{i}. {dice['description']} - {dice['price']['money']:,}元 + {dice['price']['items']}个道具 {status}")
    
    while True:
        print("\n选择操作:")
        print("1-6: 购买对应骰子")
        print("s: 切换当前骰子")
        print("q: 离开商店")
        
        choice = input("请输入选择: ").strip().lower()
        
        if choice == 'q':
            print("离开商店")
            break
        elif choice == 's':
            handle_dice_switch(player_manager, player)
        elif choice in ['1', '2', '3', '4', '5', '6']:
            if 1 <= int(choice) <= len(shop_dice):
                dice = shop_dice[int(choice) - 1]
                result = player_manager.buy_dice(player, dice["type"])
                print(result["msg"])
                if result["success"]:
                    display_player_status(player)
            else:
                print("无效选择")
        else:
            print("无效选择")


def handle_dice_switch(player_manager, player):
    """处理骰子切换"""
    dice_info = player_manager.get_available_dice(player)
    available_dice = dice_info['available_dice']
    
    if len(available_dice) <= 1:
        print("没有其他骰子可切换")
        return
    
    print(f"\n当前骰子: {dice_info['current_dice']}")
    print("可切换的骰子:")
    for i, dice_type in enumerate(available_dice, 1):
        if dice_type == dice_info['current_dice']:
            print(f"{i}. {dice_type} (当前使用)")
        else:
            print(f"{i}. {dice_type}")
    
    choice = input("选择要切换的骰子 (1-{}): ".format(len(available_dice)))
    try:
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(available_dice):
            dice_type = available_dice[choice_idx]
            result = player_manager.set_player_dice(player, dice_type)
            print(result["msg"])
        else:
            print("无效选择")
    except ValueError:
        print("无效输入")


def handle_shop_interaction(player_manager, player):
    """处理商店交互"""
    cell = player_manager.game_map.get_cell_by_path_index(player.position)
    
    if cell.cell_type == "shop":
        return handle_item_shop(player_manager, player)
    elif cell.cell_type == "dice_shop":
        return handle_dice_shop(player_manager, player)
    
    return None


def handle_player_turn(player_manager, player):
    """处理玩家回合"""
    print(f"\n=== {player.name} 的回合 ===")
    display_player_status(player)
    
    if player.in_jail:
        print(f"你在监狱中，剩余回合: {3 - player.jail_turns}")
        input("按回车投掷骰子尝试越狱...")
        dice_result = player_manager.roll_dice(player)
        print(f"投掷结果: {dice_result['dice_result']}")
        if dice_result.get('escaped'):
            print("成功越狱！")
        else:
            print("越狱失败，继续关押")
        return
    
    input("按回车投掷骰子...")
    dice_result = player_manager.roll_dice(player)
    print(f"投掷结果: {dice_result['dice_result']}")
    
    # 显示d20神力效果
    if dice_result.get('d20_power'):
        if dice_result['d20_power'] == 'max':
            print("🎉 d20神力加持！本回合收益翻倍，惩罚减免！")
        elif dice_result['d20_power'] == 'min':
            print("💀 d20神力诅咒！本回合收益清零，惩罚翻倍！")
    
    move_result = player_manager.move_player(player, dice_result["dice_result"])
    print(f"移动结果: {move_result['msg']}")
    
    if "cell_effect" in move_result:
        cell_effect = move_result["cell_effect"]
        print(f"格子效果: {cell_effect['msg']}")
        
        if cell_effect["type"] in ["shop", "dice_shop"]:
            handle_shop_interaction(player_manager, player)
        
        if "event" in cell_effect:
            event = cell_effect["event"]
            print(f"事件: {event['msg']}")
    
    if "property" in move_result:
        property_obj = move_result["property"]
        if not property_obj.is_owned():
            print(f"发现空地，购买价格: {property_obj.get_cost():,}")
            buy = input("是否购买? (y/n): ").strip().lower() == 'y'
            if buy:
                result = player_manager.buy_property_decision(player, player.position, True)
                print(result["msg"])
        elif property_obj.owner_id == player.player_id:
            print("到达自己的房产")
            if property_obj.can_upgrade():
                upgrade = input("是否升级? (y/n): ").strip().lower() == 'y'
                if upgrade:
                    result = player_manager.upgrade_property_decision(player, player.position, True)
                    print(result["msg"])
    
    if player.items:
        print(f"\n你的道具: {player.items}")
        use_item = input("是否使用道具? (y/n): ").strip().lower() == 'y'
        if use_item:
            item_id = input("选择道具ID: ")
            try:
                item_id = int(item_id)
                if item_id in player.items:
                    result = player_manager.use_item_decision(player, item_id)
                    print(result["msg"])
                else:
                    print("无效的道具ID")
            except ValueError:
                print("无效输入")


def handle_ai_shop_decision(player_manager, player, shop_type):
    """处理AI商店决策"""
    if shop_type == "shop":
        affordable_items = player_manager.get_affordable_items(player)
        if affordable_items and random.random() < 0.5:
            item_name = random.choice(affordable_items)
            result = player_manager.buy_shop_item(player, item_name)
            print(f"AI购买道具：{result['msg']}")
    
    elif shop_type == "dice_shop":
        dice_info = player_manager.get_available_dice(player)
        shop_dice = dice_info['shop_dice']
        
        if shop_dice and random.random() < 0.3:
            affordable_dice = []
            for dice in shop_dice:
                if player_manager.dice_system.can_afford_dice(
                    dice["type"], player.money, len(player.items)
                ):
                    affordable_dice.append(dice)
            
            if affordable_dice:
                dice = random.choice(affordable_dice)
                result = player_manager.buy_dice(player, dice["type"])
                print(f"AI购买骰子：{result['msg']}")


def main():
    """主函数"""
    print("🎲 欢迎来到大富翁游戏！")
    
    game_map = Map(20, 20)
    player_manager = PlayerManager()
    player_manager.set_game_map(game_map)
    
    print("\n设置玩家:")
    player_count = int(input("玩家数量 (3-6): "))
    for i in range(player_count):
        name = input(f"玩家{i+1}名称: ")
        is_ai = input(f"玩家{i+1}是否为AI? (y/n): ").strip().lower() == 'y'
        player_manager.add_player(name, is_ai)
    
    print(f"\n游戏开始！地图大小: {game_map.width}x{game_map.height}")
    print("每个玩家初始资金: 200,000元")

    while True:
        status = player_manager.get_game_status()
        if status["game_ended"]:
            print("游戏结束！胜者：", player_manager.winner.name)
            break
        
        player = player_manager.get_current_player()
        
        if player.is_ai:
            print(f"\n--- 回合 {status['turn_count']+1} --- 当前玩家：{player.name} (AI)")
            print("AI正在行动...")
            
            ai_result = player_manager.ai_decision(player)
            if ai_result["success"]:
                decisions = ai_result["decisions"]
                
                if "dice" in decisions:
                    dice_result = decisions["dice"]
                    print(f"AI投掷骰子：{dice_result}")
                    move_result = player_manager.move_player(player, dice_result)
                    print(f"AI移动结果：{move_result['msg']}")
                    
                    if "cell_effect" in move_result:
                        cell_effect = move_result["cell_effect"]
                        print(f"格子效果：{cell_effect['msg']}")
                        
                        if cell_effect["type"] in ["shop", "dice_shop"]:
                            handle_ai_shop_decision(player_manager, player, cell_effect["type"])
                        
                        if "event" in cell_effect:
                            print(f"事件：{cell_effect['event']['msg']}")
                
                if "buy_property" in decisions:
                    result = player_manager.buy_property_decision(player, player.position, True)
                    print(f"AI购买房产：{result['msg']}")
                
                if "use_item" in decisions:
                    item_id = decisions["use_item"]
                    result = player_manager.use_item_decision(player, item_id)
                    print(f"AI使用道具：{result['msg']}")
            
            player_manager.end_turn()
            continue
        
        print(f"\n--- 回合 {status['turn_count']+1} --- 当前玩家：{player.name}")
        handle_player_turn(player_manager, player)
        
        input("按回车结束回合...")
        player_manager.end_turn()


if __name__ == "__main__":
    main() 