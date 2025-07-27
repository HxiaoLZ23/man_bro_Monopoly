"""
道具管理器
"""
from typing import Dict, List, Optional
from src.models.item import (
    Item, RoadblockItem, FlyItem, ProtectionItem, 
    SixSixSixItem, PropertyUpgradeItem, create_item_by_id
)


class ItemManager:
    """道具管理器"""
    
    def __init__(self):
        # 道具类映射
        self.item_class_map = {
            1: RoadblockItem,
            2: FlyItem,
            3: ProtectionItem,
            4: SixSixSixItem,
            5: PropertyUpgradeItem
        }
        
        # 道具名称映射
        self.item_name_map = {
            "路障": RoadblockItem,
            "再装逼让你飞起来!!": FlyItem,
            "庇护术": ProtectionItem,
            "六百六十六": SixSixSixItem,
            "违规爆建": PropertyUpgradeItem
        }
    
    def get_item_by_id(self, item_id: int) -> Optional[Item]:
        """通过ID获取道具"""
        return create_item_by_id(item_id)
    
    def get_item_by_name(self, name: str) -> Optional[Item]:
        """通过名称获取道具"""
        item_class = self.item_name_map.get(name)
        if item_class:
            return item_class()
        return None
    
    def create_items(self, item_id: int, count: int) -> List[Item]:
        """批量创建道具"""
        items = []
        for _ in range(count):
            item = create_item_by_id(item_id)
            if item:
                items.append(item)
        return items
    
    def list_all_items(self) -> List[Item]:
        """列出所有道具类型"""
        items = []
        for item_class in self.item_class_map.values():
            items.append(item_class())
        return items
    
    def get_item_price(self, item_id: int) -> int:
        """获取道具价格"""
        price_map = {
            1: 10000,  # 路障
            2: 20000,  # 再装逼让你飞起来!!
            3: 20000,  # 庇护术
            4: 15000,  # 六百六十六
            5: 25000   # 违规爆建
        }
        return price_map.get(item_id, 0)
    
    def get_item_price_by_name(self, name: str) -> int:
        """通过名称获取道具价格"""
        item = self.get_item_by_name(name)
        if item:
            return self.get_item_price(item.item_id)
        return 0 