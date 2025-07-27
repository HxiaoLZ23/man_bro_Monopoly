"""
房产管理器
"""
from typing import Dict, List, Optional, Tuple
from src.models.property import Property
from src.models.player import Player
from src.models.map import Map, Cell
from src.core.constants import PROPERTY_LEVELS


class PropertyManager:
    """房产管理器"""
    
    def __init__(self, game_map: Map):
        """
        初始化房产管理器
        
        Args:
            game_map: 游戏地图
        """
        self.game_map = game_map
        self.properties: Dict[int, Property] = {}  # 位置 -> 房产对象
        self._initialize_properties()
    
    def _initialize_properties(self) -> None:
        """初始化房产数据"""
        self.properties.clear()
        for cell in self.game_map.cells:
            if cell.property:
                self.properties[cell.property.position] = cell.property
    
    def get_property_at_position(self, position: int) -> Optional[Property]:
        """
        获取指定位置的房产
        
        Args:
            position: 位置
            
        Returns:
            Optional[Property]: 房产对象，如果不存在返回None
        """
        return self.properties.get(position)
    
    def get_property_at_coordinates(self, x: int, y: int) -> Optional[Property]:
        """
        获取指定坐标的房产
        
        Args:
            x: X坐标
            y: Y坐标
            
        Returns:
            Optional[Property]: 房产对象，如果不存在返回None
        """
        position = x * self.game_map.width + y
        return self.get_property_at_position(position)
    
    def get_properties_by_owner(self, owner_id: int) -> List[Property]:
        """
        获取指定玩家的所有房产
        
        Args:
            owner_id: 玩家ID
            
        Returns:
            List[Property]: 房产列表
        """
        return [prop for prop in self.properties.values() if prop.owner_id == owner_id]
    
    def get_all_properties(self) -> List[Property]:
        """
        获取所有房产
        
        Returns:
            List[Property]: 所有房产列表
        """
        return list(self.properties.values())
    
    def get_owned_properties(self) -> List[Property]:
        """
        获取所有有主的房产
        
        Returns:
            List[Property]: 有主房产列表
        """
        return [prop for prop in self.properties.values() if prop.is_owned()]
    
    def get_empty_properties(self) -> List[Property]:
        """
        获取所有空地
        
        Returns:
            List[Property]: 空地列表
        """
        return [prop for prop in self.properties.values() if prop.is_empty()]
    
    def buy_property(self, player: Player, position: int) -> Dict[str, any]:
        """
        购买房产
        
        Args:
            player: 购买者
            position: 房产位置
            
        Returns:
            Dict: 购买结果
        """
        # 检查房产是否存在
        property_obj = self.get_property_at_position(position)
        if not property_obj:
            return {"success": False, "msg": "该位置没有房产"}
        
        # 检查是否已有所有者
        if property_obj.is_owned():
            return {"success": False, "msg": "该房产已有所有者"}
        
        # 检查是否为空地
        if not property_obj.is_empty():
            return {"success": False, "msg": "该位置不是空地"}
        
        # 检查玩家资金
        purchase_cost = PROPERTY_LEVELS[1]["cost"]  # 一级房产价格
        if player.money < purchase_cost:
            return {"success": False, "msg": f"资金不足，需要{purchase_cost}，当前{player.money}"}
        
        # 执行购买
        player.remove_money(purchase_cost)
        property_obj.set_owner(player.player_id)
        property_obj.level = 1
        property_obj.value = property_obj._calculate_value()
        
        # 添加到玩家房产列表
        player.add_property(property_obj)
        
        return {
            "success": True, 
            "msg": f"成功购买房产，花费{purchase_cost}",
            "property": property_obj,
            "cost": purchase_cost
        }
    
    def upgrade_property(self, player: Player, position: int) -> Dict[str, any]:
        """
        升级房产
        
        Args:
            player: 升级者
            position: 房产位置
            
        Returns:
            Dict: 升级结果
        """
        # 检查房产是否存在
        property_obj = self.get_property_at_position(position)
        if not property_obj:
            return {"success": False, "msg": "该位置没有房产"}
        
        # 检查是否为所有者
        if property_obj.owner_id != player.player_id:
            return {"success": False, "msg": "你不是该房产的所有者"}
        
        # 检查是否可以升级
        if not property_obj.can_upgrade():
            return {"success": False, "msg": "房产已达到最高等级"}
        
        # 检查升级费用
        upgrade_cost = property_obj.get_upgrade_cost()
        if player.money < upgrade_cost:
            return {"success": False, "msg": f"资金不足，需要{upgrade_cost}，当前{player.money}"}
        
        # 执行升级
        player.remove_money(upgrade_cost)
        property_obj.upgrade()
        
        return {
            "success": True, 
            "msg": f"成功升级房产到{property_obj.level}级，花费{upgrade_cost}",
            "property": property_obj,
            "cost": upgrade_cost
        }
    
    def collect_rent(self, player: Player, position: int) -> Dict[str, any]:
        """
        收租
        
        Args:
            player: 收租者（房产所有者）
            position: 房产位置
            
        Returns:
            Dict: 收租结果
        """
        # 检查房产是否存在
        property_obj = self.get_property_at_position(position)
        if not property_obj:
            return {"success": False, "msg": "该位置没有房产"}
        
        # 检查是否为所有者
        if property_obj.owner_id != player.player_id:
            return {"success": False, "msg": "你不是该房产的所有者"}
        
        # 检查是否有租金
        rent = property_obj.get_rent()
        if rent <= 0:
            return {"success": False, "msg": "该房产没有租金"}
        
        # 执行收租
        player.add_money(rent)
        
        return {
            "success": True, 
            "msg": f"成功收取租金{rent}",
            "property": property_obj,
            "rent": rent
        }
    
    def pay_rent(self, payer: Player, position: int) -> Dict[str, any]:
        """
        支付租金
        
        Args:
            payer: 支付者
            position: 房产位置
            
        Returns:
            Dict: 支付结果
        """
        # 检查房产是否存在
        property_obj = self.get_property_at_position(position)
        if not property_obj:
            return {"success": False, "msg": "该位置没有房产"}
        
        # 检查是否有所有者
        if not property_obj.is_owned():
            return {"success": False, "msg": "该房产无主"}
        
        # 检查是否为所有者本人
        if property_obj.owner_id == payer.player_id:
            return {"success": False, "msg": "无需向自己支付租金"}
        
        # 检查租金
        rent = property_obj.get_rent()
        if rent <= 0:
            return {"success": False, "msg": "该房产没有租金"}
        
        # 检查支付者资金
        if payer.money < rent:
            return {"success": False, "msg": f"资金不足，需要支付{rent}，当前{payer.money}"}
        
        # 执行支付
        payer.remove_money(rent)
        
        # 找到所有者并给予租金
        # 注意：这里需要从外部传入所有者玩家对象
        # 在实际游戏中，应该通过游戏管理器找到所有者
        
        return {
            "success": True, 
            "msg": f"支付租金{rent}",
            "property": property_obj,
            "rent": rent,
            "owner_id": property_obj.owner_id
        }
    
    def transfer_property(self, from_player: Player, to_player: Player, position: int) -> Dict[str, any]:
        """
        转移房产所有权
        
        Args:
            from_player: 原所有者
            to_player: 新所有者
            position: 房产位置
            
        Returns:
            Dict: 转移结果
        """
        # 检查房产是否存在
        property_obj = self.get_property_at_position(position)
        if not property_obj:
            return {"success": False, "msg": "该位置没有房产"}
        
        # 检查原所有者
        if property_obj.owner_id != from_player.player_id:
            return {"success": False, "msg": "你不是该房产的所有者"}
        
        # 执行转移
        property_obj.set_owner(to_player.player_id)
        
        # 更新玩家房产列表
        from_player.remove_property(property_obj)
        to_player.add_property(property_obj)
        
        return {
            "success": True, 
            "msg": f"成功转移房产给{to_player.name}",
            "property": property_obj
        }
    
    def demolish_property(self, player: Player, position: int) -> Dict[str, any]:
        """
        拆除房产（降级为空地）
        
        Args:
            player: 拆除者
            position: 房产位置
            
        Returns:
            Dict: 拆除结果
        """
        # 检查房产是否存在
        property_obj = self.get_property_at_position(position)
        if not property_obj:
            return {"success": False, "msg": "该位置没有房产"}
        
        # 检查是否为所有者
        if property_obj.owner_id != player.player_id:
            return {"success": False, "msg": "你不是该房产的所有者"}
        
        # 检查是否为空地
        if property_obj.is_empty():
            return {"success": False, "msg": "该位置已经是空地"}
        
        # 执行拆除
        old_level = property_obj.level
        property_obj.level = 0
        property_obj.value = 0
        property_obj.remove_owner()
        
        # 从玩家房产列表移除
        player.remove_property(property_obj)
        
        return {
            "success": True, 
            "msg": f"成功拆除{old_level}级房产",
            "property": property_obj
        }
    
    def force_downgrade_property(self, position: int) -> Dict[str, any]:
        """
        强制降级房产（如使用道具）
        
        Args:
            position: 房产位置
            
        Returns:
            Dict: 降级结果
        """
        # 检查房产是否存在
        property_obj = self.get_property_at_position(position)
        if not property_obj:
            return {"success": False, "msg": "该位置没有房产"}
        
        # 检查是否为空地
        if property_obj.is_empty():
            return {"success": False, "msg": "该位置已经是空地"}
        
        # 执行降级
        old_level = property_obj.level
        property_obj.downgrade()
        
        # 如果降级为空地，移除所有者
        if property_obj.is_empty():
            property_obj.remove_owner()
        
        return {
            "success": True, 
            "msg": f"成功降级房产从{old_level}级到{property_obj.level}级",
            "property": property_obj
        }
    
    def force_upgrade_property(self, position: int) -> Dict[str, any]:
        """
        强制升级房产（如使用道具）
        
        Args:
            position: 房产位置
            
        Returns:
            Dict: 升级结果
        """
        # 检查房产是否存在
        property_obj = self.get_property_at_position(position)
        if not property_obj:
            return {"success": False, "msg": "该位置没有房产"}
        
        # 检查是否可以升级
        if not property_obj.can_upgrade():
            return {"success": False, "msg": "房产已达到最高等级"}
        
        # 执行升级
        old_level = property_obj.level
        property_obj.upgrade()
        
        return {
            "success": True, 
            "msg": f"成功升级房产从{old_level}级到{property_obj.level}级",
            "property": property_obj
        }
    
    def get_property_statistics(self) -> Dict[str, any]:
        """
        获取房产统计信息
        
        Returns:
            Dict: 统计信息
        """
        total_properties = len(self.properties)
        owned_properties = len(self.get_owned_properties())
        empty_properties = len(self.get_empty_properties())
        
        # 按等级统计
        level_stats = {}
        for i in range(5):  # 0-4级
            level_stats[i] = len([p for p in self.properties.values() if p.level == i])
        
        # 按所有者统计
        owner_stats = {}
        for prop in self.properties.values():
            if prop.owner_id is not None:
                owner_stats[prop.owner_id] = owner_stats.get(prop.owner_id, 0) + 1
        
        return {
            "total_properties": total_properties,
            "owned_properties": owned_properties,
            "empty_properties": empty_properties,
            "level_statistics": level_stats,
            "owner_statistics": owner_stats
        }
    
    def validate_properties(self) -> List[str]:
        """
        验证房产数据一致性
        
        Returns:
            List[str]: 错误信息列表
        """
        errors = []
        
        for position, property_obj in self.properties.items():
            # 检查位置一致性
            if property_obj.position != position:
                errors.append(f"房产位置不一致: {position} vs {property_obj.position}")
            
            # 检查等级范围
            if not (0 <= property_obj.level <= 4):
                errors.append(f"房产等级超出范围: {property_obj.level}")
            
            # 检查价值计算
            expected_value = property_obj._calculate_value()
            if property_obj.value != expected_value:
                errors.append(f"房产价值计算错误: {property_obj.value} vs {expected_value}")
        
        return errors 