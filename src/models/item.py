"""
道具系统
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple, List


class Item(ABC):
    """道具基类"""
    
    def __init__(self, item_id: int, name: str, desc: str, 
                 stackable: bool = True, max_count: int = 99):
        self.item_id = item_id
        self.name = name
        self.desc = desc
        self.stackable = stackable
        self.max_count = max_count
    
    @abstractmethod
    def use(self, player, *args, **kwargs) -> Dict[str, Any]:
        """使用道具"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "item_id": self.item_id,
            "name": self.name,
            "desc": self.desc,
            "stackable": self.stackable,
            "max_count": self.max_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        """从字典反序列化。对于道具子类，直接返回无参构造实例。"""
        return cls()


class RoadblockItem(Item):
    """路障道具"""
    
    def __init__(self):
        super().__init__(
            item_id=1,
            name="路障",
            desc="在距自身直线距离不超过14的格子上放置一个路障，当有玩家在移动时碰到该路障，则立即停止移动。",
            stackable=True,
            max_count=10
        )
    
    def use(self, player, target_pos: Tuple[int, int], game) -> Dict[str, Any]:
        """使用路障"""
        if not game or not hasattr(game, 'map'):
            return {"success": False, "msg": "地图无效"}
        
        try:
            cell = game.map.get_cell_at(target_pos)
            if cell:
                cell.roadblock = True
                return {"success": True, "msg": f"在位置{target_pos}放置了路障"}
            else:
                return {"success": False, "msg": "目标位置无效"}
        except Exception as e:
            return {"success": False, "msg": f"放置路障失败: {str(e)}"}


class FlyItem(Item):
    """再装逼让你飞起来!!道具"""
    
    def __init__(self):
        super().__init__(
            item_id=2,
            name="再装逼让你飞起来!!",
            desc="可以对自身或对与自身处在同一格的玩家使用，使其获得【起飞】。下次移动可以无视地图限制，但落地后身上的所有钱平均散落在周围的格子上。",
            stackable=True,
            max_count=5
        )
    
    def use(self, player, target_player=None) -> Dict[str, Any]:
        """使用起飞道具"""
        if target_player is None:
            target_player = player
        
        if not target_player:
            return {"success": False, "msg": "目标玩家无效"}
        
        target_player.fly_mode = True
        return {"success": True, "msg": f"{target_player.name}获得了【起飞】效果"}


class ProtectionItem(Item):
    """庇护术道具"""
    
    def __init__(self):
        super().__init__(
            item_id=3,
            name="庇护术",
            desc="直到你下次使用道具卡为止，你不会受到任何道具的影响。",
            stackable=True,
            max_count=5
        )
    
    def use(self, player) -> Dict[str, Any]:
        """使用庇护术"""
        if not player:
            return {"success": False, "msg": "玩家无效"}
        
        player.protection = True
        return {"success": True, "msg": f"{player.name}获得了【庇护】效果"}


class SixSixSixItem(Item):
    """六百六十六道具"""
    
    def __init__(self):
        super().__init__(
            item_id=4,
            name="六百六十六",
            desc="你下次投掷时每个骰子的结果总为6。",
            stackable=True,
            max_count=5
        )
    
    def use(self, player) -> Dict[str, Any]:
        """使用六百六十六"""
        if not player:
            return {"success": False, "msg": "玩家无效"}
        
        player.next_dice_value = 6
        return {"success": True, "msg": f"{player.name}下次投掷结果将固定为6"}


class PropertyUpgradeItem(Item):
    """违规爆建道具"""
    
    def __init__(self):
        super().__init__(
            item_id=5,
            name="违规爆建",
            desc="可以使自身的一处房产升一级或使别人的一处房产降一级（无法降级四级房产。房产若降为零级则重新成为空地）。",
            stackable=True,
            max_count=3
        )
    
    def use(self, player, target_property, upgrade: bool = True) -> Dict[str, Any]:
        """使用违规爆建"""
        if not player or not target_property:
            return {"success": False, "msg": "目标无效"}
        
        try:
            if upgrade:
                # 升级房产
                if target_property.level < 4:
                    target_property.level += 1
                    return {"success": True, "msg": f"{target_property.name}升级到{target_property.level}级"}
                else:
                    return {"success": False, "msg": "房产已达到最高等级"}
            else:
                # 降级房产
                if target_property.level > 0:
                    target_property.level -= 1
                    if target_property.level == 0:
                        target_property.owner = None
                        return {"success": True, "msg": f"{target_property.name}降级为空地"}
                    else:
                        return {"success": True, "msg": f"{target_property.name}降级到{target_property.level}级"}
                else:
                    return {"success": False, "msg": "房产已经是空地"}
        except Exception as e:
            return {"success": False, "msg": f"操作失败: {str(e)}"}


# 道具工厂函数
def create_item_by_id(item_id: int) -> Optional[Item]:
    """通过ID创建道具"""
    item_map = {
        1: RoadblockItem,
        2: FlyItem,
        3: ProtectionItem,
        4: SixSixSixItem,
        5: PropertyUpgradeItem
    }
    
    item_class = item_map.get(item_id)
    if item_class:
        return item_class()
    return None 