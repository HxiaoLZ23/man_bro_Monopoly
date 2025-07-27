"""
地图格子数据模型
"""
from typing import Tuple, Dict, Optional
from src.core.constants import CELL_COLORS
from src.models.property import Property


class Cell:
    """地图格子类"""
    
    def __init__(self, x: int, y: int, cell_type: str = "empty", name: str = ""):
        """
        初始化格子
        
        Args:
            x: X坐标
            y: Y坐标
            cell_type: 格子类型
            name: 格子名称
        """
        self.x = x
        self.y = y
        self.position = (x, y)
        self.cell_type = cell_type
        self.name = name
        self.path_index = -1  # 在路径中的索引，-1表示不在路径上
        self.property = None  # 房产对象
        self.roadblock = False  # 是否有路障
        self.money_on_ground = 0  # 地上的钱
        self.connections = set()  # 连接的路径点（路径索引）
        self.is_junction = False  # 是否为岔路口
    
    def is_movable(self) -> bool:
        """
        检查格子是否可移动
        
        Returns:
            bool: 是否可移动
        """
        return self.cell_type not in ["wall", "void"]
    
    def is_path_cell(self) -> bool:
        """
        检查是否为路径格子
        
        Returns:
            bool: 是否为路径格子
        """
        return self.path_index >= 0
    
    def get_color(self) -> Tuple[int, int, int]:
        """
        获取格子颜色
        
        Returns:
            Tuple[int, int, int]: RGB颜色值
        """
        return CELL_COLORS.get(self.cell_type, CELL_COLORS["empty"])
    
    def get_name(self) -> str:
        """
        获取格子名称
        
        Returns:
            str: 格子名称
        """
        if self.name:
            return self.name
            
        type_names = {
            "empty": "空地",
            "wall": "墙",
            "void": "空格",
            "bank": "银行",
            "shop": "道具商店",
            "dice_shop": "骰子商店",
            "jail": "监狱",
            "luck": "好运格",
            "bad_luck": "厄运格",
            "start": "起点",
            "property": "房产"
        }
        return type_names.get(self.cell_type, "未知")
    
    def set_property(self, property_obj: Property) -> None:
        """
        设置房产
        
        Args:
            property_obj: 房产对象
        """
        self.property = property_obj
    
    def remove_property(self) -> None:
        """
        移除房产
        """
        self.property = None
    
    def has_property(self) -> bool:
        """
        检查是否有房产
        
        Returns:
            bool: 是否有房产
        """
        return self.property is not None
    
    def set_roadblock(self, has_roadblock: bool) -> None:
        """
        设置路障
        
        Args:
            has_roadblock: 是否有路障
        """
        self.roadblock = has_roadblock
    
    def add_money_on_ground(self, amount: int) -> None:
        """
        在地上添加钱
        
        Args:
            amount: 金额
        """
        self.money_on_ground += amount
    
    def collect_money_on_ground(self) -> int:
        """
        收集地上的钱
        
        Returns:
            int: 收集到的金额
        """
        money = self.money_on_ground
        self.money_on_ground = 0
        return money
    
    def to_dict(self) -> Dict:
        """
        转换为字典格式
        
        Returns:
            Dict: 格子数据字典
        """
        return {
            "x": self.x,
            "y": self.y,
            "cell_type": self.cell_type,
            "name": self.name,
            "path_index": self.path_index,
            "property": self.property.to_dict() if self.property else None,
            "roadblock": self.roadblock,
            "money_on_ground": self.money_on_ground,
            "connections": list(self.connections),
            "is_junction": self.is_junction
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Cell':
        """
        从字典创建格子对象
        
        Args:
            data: 格子数据字典
            
        Returns:
            Cell: 格子对象
        """
        cell = cls(data["x"], data["y"], data["cell_type"], data.get("name", ""))
        cell.path_index = data.get("path_index", -1)
        cell.roadblock = data.get("roadblock", False)
        cell.money_on_ground = data.get("money_on_ground", 0)
        cell.connections = set(data.get("connections", []))
        cell.is_junction = data.get("is_junction", False)
        
        if data.get("property"):
            cell.property = Property.from_dict(data["property"])
        
        return cell
    
    def __str__(self) -> str:
        return f"Cell({self.x}, {self.y}, {self.cell_type})"
    
    def __repr__(self) -> str:
        return self.__str__() 