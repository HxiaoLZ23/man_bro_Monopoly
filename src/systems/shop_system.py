"""
道具商店系统
"""
import random
from typing import List, Dict, Optional
from src.core.constants import ITEMS
from src.models.player import Player


class ShopSystem:
    """道具商店系统"""
    
    def __init__(self):
        """初始化道具商店"""
        self.shop_items = {}  # 当前商店道具
        self.refresh_shop()
    
    def refresh_shop(self) -> Dict[str, any]:
        """
        刷新商店道具
        
        Returns:
            Dict: 刷新结果
        """
        # 从所有道具中随机选择2个
        all_items = list(ITEMS.keys())
        if len(all_items) >= 2:
            selected_items = random.sample(all_items, 2)
        else:
            selected_items = all_items
        
        self.shop_items = {}
        for item_name in selected_items:
            item_info = ITEMS[item_name]
            self.shop_items[item_name] = {
                "name": item_name,
                "price": item_info["price"],
                "description": item_info["description"],
                "stock": 3  # 每个道具库存3个
            }
        
        return {
            "success": True,
            "msg": "商店已刷新",
            "items": self.get_shop_items()
        }
    
    def get_shop_items(self) -> Dict[str, any]:
        """
        获取商店道具列表
        
        Returns:
            Dict: 商店道具信息
        """
        return self.shop_items.copy()
    
    def buy_item(self, player: Player, item_name: str) -> Dict[str, any]:
        """
        购买道具
        
        Args:
            player: 购买玩家
            item_name: 道具名称
            
        Returns:
            Dict: 购买结果
        """
        if item_name not in self.shop_items:
            return {"success": False, "msg": "道具不存在"}
        
        item_info = self.shop_items[item_name]
        
        # 检查库存
        if item_info["stock"] <= 0:
            return {"success": False, "msg": "道具库存不足"}
        
        # 检查玩家金钱
        if player.money < item_info["price"]:
            return {"success": False, "msg": "金钱不足"}
        
        # 获取道具ID
        item_id = self._get_item_id_by_name(item_name)
        if not item_id:
            return {"success": False, "msg": "道具ID无效"}
        
        # 扣除金钱
        player.remove_money(item_info["price"])
        
        # d20神力效果
        d20_power = player.status.get("d20_power")
        if d20_power == "max":
            # 收益翻倍，获得2个道具
            player.add_item(item_id, 2)
            item_count = 2
            msg = f"d20神力加持！成功购买{item_name} x2"
        elif d20_power == "min":
            # 收益清零，不获得道具
            item_count = 0
            msg = f"d20神力诅咒，购买失败，收益清零！"
        else:
            # 正常购买
            player.add_item(item_id, 1)
            item_count = 1
            msg = f"成功购买{item_name}"
        
        # 减少库存
        item_info["stock"] -= 1
        
        return {
            "success": True,
            "msg": msg,
            "item_name": item_name,
            "price": item_info["price"],
            "remaining_stock": item_info["stock"],
            "item_count": item_count
        }
    
    def _get_item_id_by_name(self, item_name: str) -> Optional[int]:
        """根据道具名称获取道具ID"""
        item_map = {
            "路障": 1,
            "再装逼让你飞起来!!": 2,
            "庇护术": 3,
            "六百六十六": 4,
            "违规爆建": 5
        }
        return item_map.get(item_name)
    
    def get_item_info(self, item_name: str) -> Optional[Dict]:
        """
        获取道具详细信息
        
        Args:
            item_name: 道具名称
            
        Returns:
            Optional[Dict]: 道具信息
        """
        if item_name in self.shop_items:
            return self.shop_items[item_name].copy()
        return None
    
    def can_afford_item(self, player: Player, item_name: str) -> bool:
        """
        检查玩家是否可以购买道具
        
        Args:
            player: 玩家
            item_name: 道具名称
            
        Returns:
            bool: 是否可以购买
        """
        if item_name not in self.shop_items:
            return False
        
        item_info = self.shop_items[item_name]
        return player.money >= item_info["price"] and item_info["stock"] > 0
    
    def get_affordable_items(self, player: Player) -> List[str]:
        """
        获取玩家可以购买的道具列表
        
        Args:
            player: 玩家
            
        Returns:
            List[str]: 可购买道具列表
        """
        affordable = []
        for item_name in self.shop_items:
            if self.can_afford_item(player, item_name):
                affordable.append(item_name)
        return affordable 