"""
骰子系统
"""
import random
from typing import List, Tuple, Dict
from src.core.constants import DICE_TYPES, DICE_PRICES


class Dice:
    """骰子类"""
    
    def __init__(self, sides: int):
        """
        初始化骰子
        
        Args:
            sides: 骰子面数
        """
        self.sides = sides
    
    def roll(self) -> int:
        """
        投掷骰子
        
        Returns:
            int: 骰子结果
        """
        return random.randint(1, self.sides)


class DiceSet:
    """骰子组合类"""
    
    def __init__(self, dice_type: str):
        """
        初始化骰子组合
        
        Args:
            dice_type: 骰子类型（如"d6", "2d6", "d20"等）
        """
        self.dice_type = dice_type
        self.dice_config = DICE_TYPES.get(dice_type, {"sides": 6, "count": 1})
        self.dice_list = [Dice(self.dice_config["sides"]) for _ in range(self.dice_config["count"])]
    
    def roll(self) -> List[int]:
        """
        投掷所有骰子
        
        Returns:
            List[int]: 所有骰子的结果
        """
        return [dice.roll() for dice in self.dice_list]
    
    def roll_sum(self) -> int:
        """
        投掷并返回总和
        
        Returns:
            int: 骰子结果总和
        """
        return sum(self.roll())
    
    def roll_max(self) -> int:
        """
        投掷并返回最大值
        
        Returns:
            int: 骰子结果最大值
        """
        return max(self.roll())
    
    def get_description(self) -> str:
        """
        获取骰子描述
        
        Returns:
            str: 骰子描述
        """
        count = self.dice_config["count"]
        sides = self.dice_config["sides"]
        
        if count == 1:
            return f"d{sides}骰子"
        else:
            return f"{count}d{sides}骰子"


class DiceSystem:
    """骰子系统"""
    
    def __init__(self):
        """初始化骰子系统"""
        self.available_dice_types = ["d6"]  # 默认只有d6骰子
        self.current_dice_type = "d6"
        self.dice_set = DiceSet("d6")
    
    def get_available_dice_types(self) -> List[str]:
        """
        获取可用的骰子类型
        
        Returns:
            List[str]: 可用骰子类型列表
        """
        return self.available_dice_types.copy()
    
    def add_dice_type(self, dice_type: str) -> bool:
        """
        添加骰子类型
        
        Args:
            dice_type: 骰子类型
            
        Returns:
            bool: 添加是否成功
        """
        if dice_type in DICE_TYPES and dice_type not in self.available_dice_types:
            self.available_dice_types.append(dice_type)
            return True
        return False
    
    def remove_dice_type(self, dice_type: str) -> bool:
        """
        移除骰子类型
        
        Args:
            dice_type: 骰子类型
            
        Returns:
            bool: 移除是否成功
        """
        if dice_type in self.available_dice_types and dice_type != "d6":
            self.available_dice_types.remove(dice_type)
            if self.current_dice_type == dice_type:
                self.set_current_dice("d6")
            return True
        return False
    
    def set_current_dice(self, dice_type: str) -> bool:
        """
        设置当前骰子
        
        Args:
            dice_type: 骰子类型
            
        Returns:
            bool: 设置是否成功
        """
        if dice_type in self.available_dice_types:
            self.current_dice_type = dice_type
            self.dice_set = DiceSet(dice_type)
            return True
        return False
    
    def get_current_dice_type(self) -> str:
        """
        获取当前骰子类型
        
        Returns:
            str: 当前骰子类型
        """
        return self.current_dice_type
    
    def roll_current_dice(self) -> List[int]:
        """
        投掷当前骰子
        
        Returns:
            List[int]: 骰子结果列表
        """
        return self.dice_set.roll()
    
    def roll_current_dice_sum(self) -> int:
        """
        投掷当前骰子并返回总和
        
        Returns:
            int: 骰子结果总和
        """
        return self.dice_set.roll_sum()
    
    def roll_current_dice_max(self) -> int:
        """
        投掷当前骰子并返回最大值
        
        Returns:
            int: 骰子结果最大值
        """
        return self.dice_set.roll_max()
    
    def roll_specific_dice(self, dice_type: str) -> List[int]:
        """
        投掷指定类型的骰子
        
        Args:
            dice_type: 骰子类型
            
        Returns:
            List[int]: 骰子结果列表
        """
        if dice_type in DICE_TYPES:
            dice_set = DiceSet(dice_type)
            return dice_set.roll()
        return []
    
    def get_dice_price(self, dice_type: str) -> Dict:
        """
        获取骰子价格
        
        Args:
            dice_type: 骰子类型
            
        Returns:
            Dict: 价格信息 {"money": int, "items": int}
        """
        return DICE_PRICES.get(dice_type, {"money": 0, "items": 0})
    
    def can_afford_dice(self, dice_type: str, money: int, item_count: int) -> bool:
        """
        检查是否可以购买骰子
        
        Args:
            dice_type: 骰子类型
            money: 可用金钱
            item_count: 可用道具数量
            
        Returns:
            bool: 是否可以购买
        """
        price = self.get_dice_price(dice_type)
        return money >= price["money"] and item_count >= price["items"]
    
    def get_dice_description(self, dice_type: str) -> str:
        """
        获取骰子描述
        
        Args:
            dice_type: 骰子类型
            
        Returns:
            str: 骰子描述
        """
        if dice_type in DICE_TYPES:
            dice_set = DiceSet(dice_type)
            return dice_set.get_description()
        return "未知骰子"
    
    def get_all_dice_types(self) -> List[str]:
        """
        获取所有可用的骰子类型
        
        Returns:
            List[str]: 所有骰子类型列表
        """
        return list(DICE_TYPES.keys())
    
    def get_dice_info(self, dice_type: str) -> Dict:
        """
        获取骰子信息
        
        Args:
            dice_type: 骰子类型
            
        Returns:
            Dict: 骰子信息
        """
        if dice_type in DICE_TYPES:
            config = DICE_TYPES[dice_type]
            price = DICE_PRICES.get(dice_type, {"money": 0, "items": 0})
            
            return {
                "type": dice_type,
                "sides": config["sides"],
                "count": config["count"],
                "description": self.get_dice_description(dice_type),
                "price": price,
                "available": dice_type in self.available_dice_types
            }
        return {}
    
    def to_dict(self) -> Dict:
        """
        转换为字典格式
        
        Returns:
            Dict: 骰子系统数据字典
        """
        return {
            "available_dice_types": self.available_dice_types.copy(),
            "current_dice_type": self.current_dice_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DiceSystem':
        """
        从字典创建骰子系统对象
        
        Args:
            data: 骰子系统数据字典
            
        Returns:
            DiceSystem: 骰子系统对象
        """
        dice_system = cls()
        dice_system.available_dice_types = data["available_dice_types"]
        dice_system.set_current_dice(data["current_dice_type"])
        return dice_system
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"DiceSystem(当前骰子:{self.current_dice_type}, 可用骰子:{len(self.available_dice_types)})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"DiceSystem(available_dice_types={self.available_dice_types}, current_dice_type='{self.current_dice_type}')"
    
    def buy_dice(self, dice_type: str, player) -> Dict[str, any]:
        """
        购买骰子
        
        Args:
            dice_type: 骰子类型
            player: 购买玩家
            
        Returns:
            Dict: 购买结果
        """
        if dice_type not in DICE_TYPES:
            return {"success": False, "msg": "无效的骰子类型"}
        
        if dice_type in self.available_dice_types:
            return {"success": False, "msg": "已经拥有该骰子"}
        
        price = self.get_dice_price(dice_type)
        
        # 检查玩家是否有足够的金钱和道具
        if not self.can_afford_dice(dice_type, player.money, len(player.items)):
            return {"success": False, "msg": "金钱或道具不足"}
        
        # 扣除金钱和道具
        player.remove_money(price["money"])
        
        # 扣除道具（随机选择）
        for _ in range(price["items"]):
            if player.items:
                # 随机选择一个道具移除
                item_id = random.choice(list(player.items.keys()))
                if player.items[item_id] > 1:
                    player.items[item_id] -= 1
                else:
                    del player.items[item_id]
        
        # d20神力效果
        d20_power = player.status.get("d20_power")
        if d20_power == "max":
            # 收益翻倍，获得2个骰子类型
            self.add_dice_type(dice_type)
            # 额外获得一个随机骰子类型
            available_dice = [d for d in DICE_TYPES.keys() if d not in self.available_dice_types]
            if available_dice:
                extra_dice = random.choice(available_dice)
                self.add_dice_type(extra_dice)
                return {
                    "success": True,
                    "msg": f"d20神力加持！成功购买{dice_type}骰子，额外获得{extra_dice}骰子！",
                    "dice_type": dice_type,
                    "extra_dice": extra_dice,
                    "cost": price
                }
        elif d20_power == "min":
            # 收益清零，不获得骰子
            return {
                "success": True,
                "msg": f"d20神力诅咒，购买失败，收益清零！",
                "dice_type": dice_type,
                "cost": price
            }
        
        # 正常购买
        self.add_dice_type(dice_type)
        
        return {
            "success": True,
            "msg": f"成功购买{dice_type}骰子",
            "dice_type": dice_type,
            "cost": price
        }
    
    def get_shop_dice_list(self) -> List[Dict]:
        """
        获取商店可购买的骰子列表
        
        Returns:
            List[Dict]: 可购买的骰子列表
        """
        shop_dice = []
        for dice_type in DICE_TYPES:
            if dice_type not in self.available_dice_types:
                info = self.get_dice_info(dice_type)
                shop_dice.append(info)
        return shop_dice 