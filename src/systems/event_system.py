"""
事件系统
"""
import random
from typing import List, Dict, Optional, Any
from src.models.player import Player


class GameEvent:
    """事件基类"""
    def __init__(self, name: str, description: str, event_type: str = "neutral"):
        self.name = name
        self.description = description
        self.event_type = event_type  # luck, bad_luck, neutral

    def trigger(self, player: Player, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        触发事件
        Args:
            player: 触发事件的玩家
            context: 额外上下文
        Returns:
            Dict: 事件结果
        """
        return {"success": True, "msg": self.description}


# 常见事件实现
class GainMoneyEvent(GameEvent):
    def __init__(self, amount: int):
        super().__init__(name="获得金钱", description=f"获得{amount}元", event_type="luck")
        self.amount = amount

    def trigger(self, player: Player, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        d20_power = player.status.get("d20_power")
        
        if d20_power == "max":
            # 收益翻倍
            final_amount = self.amount * 2
            player.add_money(final_amount)
            return {"success": True, "msg": f"d20神力加持！获得{final_amount}元（翻倍）", "amount": final_amount}
        elif d20_power == "min":
            # 收益清零
            return {"success": True, "msg": "d20神力诅咒，收益清零！", "amount": 0}
        else:
            # 正常收益
            player.add_money(self.amount)
            return {"success": True, "msg": f"获得{self.amount}元", "amount": self.amount}

class LoseMoneyEvent(GameEvent):
    def __init__(self, amount: int):
        super().__init__(name="失去金钱", description=f"失去{amount}元", event_type="bad_luck")
        self.amount = amount

    def trigger(self, player: Player, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        d20_power = player.status.get("d20_power")
        
        if d20_power == "max":
            # 惩罚减免
            return {"success": True, "msg": "d20神力加持，免于失去金钱！", "amount": 0}
        elif d20_power == "min":
            # 惩罚翻倍
            final_amount = self.amount * 2
            player.remove_money(final_amount)
            return {"success": True, "msg": f"d20神力诅咒，失去{final_amount}元（翻倍）", "amount": -final_amount}
        else:
            # 正常惩罚
            player.remove_money(self.amount)
            return {"success": True, "msg": f"失去{self.amount}元", "amount": -self.amount}

class GetItemEvent(GameEvent):
    def __init__(self, item_id: int, item_name: str):
        super().__init__(name="获得道具", description=f"获得道具：{item_name}", event_type="luck")
        self.item_id = item_id
        self.item_name = item_name

    def trigger(self, player: Player, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        d20_power = player.status.get("d20_power")
        
        if d20_power == "max":
            # 收益翻倍
            player.add_item(self.item_id, 2)
            return {"success": True, "msg": f"d20神力加持！获得2个道具：{self.item_name}", "item_id": self.item_id, "count": 2}
        elif d20_power == "min":
            # 收益清零
            return {"success": True, "msg": "d20神力诅咒，收益清零！", "item_id": self.item_id, "count": 0}
        else:
            # 正常收益
            player.add_item(self.item_id, 1)
            return {"success": True, "msg": f"获得道具：{self.item_name}", "item_id": self.item_id, "count": 1}

class GoToJailEvent(GameEvent):
    def __init__(self):
        super().__init__(name="进监狱", description="被送进监狱", event_type="bad_luck")

    def trigger(self, player: Player, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        d20_power = player.status.get("d20_power")
        
        if d20_power == "max":
            # 惩罚减免
            return {"success": True, "msg": "d20神力加持，免于进监狱！"}
        elif d20_power == "min":
            # 惩罚翻倍（监狱时间延长）
            player.go_to_jail()
            player.jail_turns = 6  # 翻倍监狱时间
            return {"success": True, "msg": "d20神力诅咒，监狱时间翻倍！"}
        else:
            # 正常惩罚
            player.go_to_jail()
            return {"success": True, "msg": "被送进监狱"}

class RandomTeleportEvent(GameEvent):
    def __init__(self, map_size: int):
        super().__init__(name="随机传送", description="被随机传送到地图其他位置", event_type="bad_luck")
        self.map_size = map_size

    def trigger(self, player: Player, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if context and "game_map" in context:
            import random
            new_pos = random.randint(0, self.map_size - 1)
            player.position = new_pos
            return {"success": True, "msg": f"被传送到位置{new_pos}", "new_position": new_pos}
        return {"success": False, "msg": "地图信息缺失"}


class EventManager:
    """事件管理器"""
    def __init__(self, map_size: int):
        self.map_size = map_size
        self.luck_events: List[GameEvent] = [
            GainMoneyEvent(10000),
            GainMoneyEvent(20000),
            GetItemEvent(1, "路障"),
            GetItemEvent(2, "再装逼让你飞起来!!")
        ]
        self.bad_luck_events: List[GameEvent] = [
            LoseMoneyEvent(10000),
            LoseMoneyEvent(20000),
            GoToJailEvent(),
            RandomTeleportEvent(map_size)
        ]
        self.history: List[Dict[str, Any]] = []

    def trigger_luck_event(self, player: Player, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        event = random.choice(self.luck_events)
        result = event.trigger(player, context)
        self.history.append({"player": player.player_id, "event": event.name, "result": result})
        return result

    def trigger_bad_luck_event(self, player: Player, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        event = random.choice(self.bad_luck_events)
        result = event.trigger(player, context)
        self.history.append({"player": player.player_id, "event": event.name, "result": result})
        return result

    def get_history(self) -> List[Dict[str, Any]]:
        return self.history 