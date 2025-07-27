"""
房产数据模型
"""
from typing import Dict, Optional
from src.core.constants import PROPERTY_LEVELS


class Property:
    """房产类"""
    
    def __init__(self, position: int, owner_id: Optional[int] = None, level: int = 0):
        """
        初始化房产
        
        Args:
            position: 房产位置
            owner_id: 所有者ID，None表示无主
            level: 房产等级（0-4，0表示空地）
        """
        self.position = position
        self.owner_id = owner_id
        self.level = level
        self.value = self._calculate_value()
    
    def _calculate_value(self) -> int:
        """
        计算房产价值
        
        Returns:
            int: 房产价值
        """
        if self.level == 0:
            return 0
        
        # 房产价值 = 所有升级费用的总和
        total_value = 0
        for i in range(1, self.level + 1):
            total_value += PROPERTY_LEVELS[i]["cost"]
        
        return total_value
    
    def get_rent(self) -> int:
        """
        获取租金
        
        Returns:
            int: 租金金额
        """
        if self.level == 0:
            return 0
        return PROPERTY_LEVELS[self.level]["rent"]
    
    def get_upgrade_cost(self) -> int:
        """
        获取升级费用
        
        Returns:
            int: 升级费用，如果无法升级返回0
        """
        if self.level >= 4:
            return 0  # 四级房产无法通过金钱升级
        return PROPERTY_LEVELS[self.level + 1]["cost"]
    
    def can_upgrade(self) -> bool:
        """
        检查是否可以升级
        
        Returns:
            bool: 是否可以升级
        """
        return self.level < 4
    
    def upgrade(self) -> bool:
        """
        升级房产
        
        Returns:
            bool: 升级是否成功
        """
        if self.can_upgrade():
            self.level += 1
            self.value = self._calculate_value()
            return True
        return False
    
    def downgrade(self) -> bool:
        """
        降级房产
        
        Returns:
            bool: 降级是否成功
        """
        if self.level > 0:
            self.level -= 1
            self.value = self._calculate_value()
            return True
        return False
    
    def set_owner(self, owner_id: int) -> None:
        """
        设置所有者
        
        Args:
            owner_id: 所有者ID
        """
        self.owner_id = owner_id
    
    def remove_owner(self) -> None:
        """
        移除所有者
        """
        self.owner_id = None
    
    def is_owned(self) -> bool:
        """
        检查是否有所有者
        
        Returns:
            bool: 是否有所有者
        """
        return self.owner_id is not None
    
    def is_empty(self) -> bool:
        """
        检查是否为空地
        
        Returns:
            bool: 是否为空地
        """
        return self.level == 0
    
    def get_level_name(self) -> str:
        """
        获取等级名称
        
        Returns:
            str: 等级名称
        """
        level_names = {
            0: "空地",
            1: "一级房产",
            2: "二级房产", 
            3: "三级房产",
            4: "四级房产"
        }
        return level_names.get(self.level, "未知")
    
    def to_dict(self) -> Dict:
        """
        转换为字典格式
        
        Returns:
            Dict: 房产数据字典
        """
        return {
            "position": self.position,
            "owner_id": self.owner_id,
            "level": self.level,
            "value": self.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Property':
        """
        从字典创建房产对象
        
        Args:
            data: 房产数据字典
            
        Returns:
            Property: 房产对象
        """
        property_obj = cls(data["position"], data["owner_id"], data["level"])
        property_obj.value = data["value"]
        return property_obj
    
    def __str__(self) -> str:
        """字符串表示"""
        owner_info = f"所有者:{self.owner_id}" if self.owner_id else "无主"
        return f"Property(位置:{self.position}, {self.get_level_name()}, {owner_info})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"Property(position={self.position}, owner_id={self.owner_id}, level={self.level}, value={self.value})" 