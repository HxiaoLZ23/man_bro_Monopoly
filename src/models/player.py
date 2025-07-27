"""
玩家数据模型
"""
from typing import List, Dict, Optional, Tuple
from src.core.constants import INITIAL_MONEY, INITIAL_ITEMS
from src.models.item import Item, create_item_by_id
from src.systems.dice_system import DiceSystem


class Player:
    """玩家类"""
    
    def __init__(self, player_id: int, name: str, is_ai: bool = False):
        """
        初始化玩家
        
        Args:
            player_id: 玩家ID
            name: 玩家名称
            is_ai: 是否为AI玩家
        """
        self.player_id = player_id
        self.name = name
        self.is_ai = is_ai
        
        # 基础属性
        self.money = INITIAL_MONEY  # 身上资金
        self.bank_money = 0  # 银行资金
        self.position = 0  # 当前位置（路径索引）
        self.dice = "d6"  # 当前骰子
        
        # 子系统
        self.dice_system = DiceSystem()  # 玩家自己的骰子系统
        
        # 道具和房产
        self.items = {}
        self.items[1] = 3  # 3张路障卡
        self.inventory = self.items  # inventory是items的别名，为了兼容性
        self.properties = []  # 房产列表
        
        # 状态效果
        self.status = {}  # 状态效果字典
        self.in_jail = False  # 是否在监狱
        self.jail_turns = 0  # 监狱回合数
        self.fly_mode = False  # 起飞模式
        self.protection = False  # 庇护效果
        self.next_dice_value = None  # 下次骰子点数
        
        # 移动相关
        self.movement_history = []  # 移动历史
        self.direction_choices = []  # 方向选择
        
        # 游戏统计
        self.total_income = 0  # 总收入
        self.total_expense = 0  # 总支出
        self.properties_bought = 0  # 购买的房产数
        self.items_used = 0  # 使用的道具数
    
    def add_money(self, amount: int) -> bool:
        """
        增加金钱
        
        Args:
            amount: 增加的金额
            
        Returns:
            bool: 操作是否成功
        """
        if amount >= 0:
            self.money += amount
            self.total_income += amount
            return True
        return False
    
    def remove_money(self, amount: int) -> bool:
        """
        减少金钱
        
        Args:
            amount: 减少的金额
            
        Returns:
            bool: 操作是否成功
        """
        if amount >= 0:
            self.money -= amount
            self.total_expense += amount
            return True
        return False
    
    def add_bank_money(self, amount: int) -> bool:
        """
        增加银行资金
        
        Args:
            amount: 增加的金额
            
        Returns:
            bool: 操作是否成功
        """
        if amount >= 0:
            self.bank_money += amount
            return True
        return False
    
    def remove_bank_money(self, amount: int) -> bool:
        """
        减少银行资金
        
        Args:
            amount: 减少的金额
            
        Returns:
            bool: 操作是否成功
        """
        if amount >= 0 and self.bank_money >= amount:
            self.bank_money -= amount
            return True
        return False
    
    def get_total_assets(self) -> int:
        """
        获取总资产
        
        Returns:
            int: 总资产（身上资金 + 银行资金 + 房产价值）
        """
        property_value = sum(prop.value for prop in self.properties)
        return self.money + self.bank_money + property_value
    
    def add_item(self, item_id: int, count: int = 1) -> bool:
        """
        添加道具
        Args:
            item_id: 道具ID
            count: 数量
        Returns:
            bool: 操作是否成功
        """
        if item_id <= 0 or count <= 0:
            return False
        self.items[item_id] = self.items.get(item_id, 0) + count
        return True

    def remove_item(self, item_id: int, count: int = 1) -> bool:
        """
        移除道具
        Args:
            item_id: 道具ID
            count: 数量
        Returns:
            bool: 操作是否成功
        """
        if item_id not in self.items or self.items[item_id] < count:
            return False
        self.items[item_id] -= count
        if self.items[item_id] <= 0:
            del self.items[item_id]
        return True

    def get_item_count(self, item_id: int) -> int:
        """
        获取某道具数量
        Args:
            item_id: 道具ID
        Returns:
            int: 数量
        """
        return self.items.get(item_id, 0)

    def has_item(self, item_id: int) -> bool:
        """
        检查是否有指定道具
        Args:
            item_id: 道具ID
        Returns:
            bool: 是否有该道具
        """
        return self.get_item_count(item_id) > 0

    def use_item(self, item_id: int, *args, **kwargs) -> Optional[dict]:
        """
        使用道具
        Args:
            item_id: 道具ID
            *args, **kwargs: 传递给道具use方法的参数
        Returns:
            Optional[dict]: 道具使用结果
        """
        if not self.has_item(item_id):
            return {"success": False, "msg": "没有该道具"}
        item = create_item_by_id(item_id)
        if item:
            result = item.use(self, *args, **kwargs)
            if result.get("success"):
                self.remove_item(item_id, 1)
                self.items_used += 1
            return result
        return {"success": False, "msg": "道具不存在"}
    
    def add_property(self, property_obj) -> bool:
        """
        添加房产
        
        Args:
            property_obj: 房产对象
            
        Returns:
            bool: 操作是否成功
        """
        self.properties.append(property_obj)
        self.properties_bought += 1
        return True
    
    def remove_property(self, property_obj) -> bool:
        """
        移除房产
        
        Args:
            property_obj: 房产对象
            
        Returns:
            bool: 操作是否成功
        """
        if property_obj in self.properties:
            self.properties.remove(property_obj)
            return True
        return False
    
    def get_property_at_position(self, position: int):
        """
        获取指定位置的房产
        
        Args:
            position: 位置
            
        Returns:
            房产对象或None
        """
        for prop in self.properties:
            if prop.position == position:
                return prop
        return None
    
    def add_status(self, status_name: str, duration: int = 1) -> None:
        """
        添加状态效果
        
        Args:
            status_name: 状态名称
            duration: 持续时间（回合数）
        """
        self.status[status_name] = duration
    
    def remove_status(self, status_name: str) -> bool:
        """
        移除状态效果
        
        Args:
            status_name: 状态名称
            
        Returns:
            bool: 操作是否成功
        """
        if status_name in self.status:
            del self.status[status_name]
            return True
        return False
    
    def has_status(self, status_name: str) -> bool:
        """
        检查是否有指定状态
        
        Args:
            status_name: 状态名称
            
        Returns:
            bool: 是否有该状态
        """
        return status_name in self.status
    
    def update_status_duration(self) -> None:
        """
        更新状态持续时间
        """
        expired_status = []
        for status_name, duration in self.status.items():
            self.status[status_name] = duration - 1
            if self.status[status_name] <= 0:
                expired_status.append(status_name)
        
        for status_name in expired_status:
            del self.status[status_name]
    
    def go_to_jail(self) -> None:
        """
        进入监狱
        """
        self.in_jail = True
        self.jail_turns = 0
    
    def try_escape_jail(self, dice_result: int) -> bool:
        """
        尝试越狱
        
        Args:
            dice_result: 骰子结果
            
        Returns:
            bool: 是否成功越狱
        """
        if self.in_jail and dice_result >= 6:
            self.in_jail = False
            self.jail_turns = 0
            return True
        return False
    
    def is_bankrupt(self) -> bool:
        """
        检查是否破产
        
        Returns:
            bool: 是否破产
        """
        # 当身上资金为负数时破产
        return self.money < 0
    
    def to_dict(self) -> Dict:
        """
        转换为字典格式
        
        Returns:
            Dict: 玩家数据字典
        """
        return {
            "player_id": self.player_id,
            "name": self.name,
            "is_ai": self.is_ai,
            "money": self.money,
            "bank_money": self.bank_money,
            "position": self.position,
            "dice": self.dice,
            "items": self.items.copy(),
            "properties": [prop.to_dict() for prop in self.properties],
            "status": self.status.copy(),
            "in_jail": self.in_jail,
            "jail_turns": self.jail_turns,
            "total_income": self.total_income,
            "total_expense": self.total_expense,
            "properties_bought": self.properties_bought,
            "items_used": self.items_used
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Player':
        """
        从字典创建玩家对象
        
        Args:
            data: 玩家数据字典
            
        Returns:
            Player: 玩家对象
        """
        player = cls(data["player_id"], data["name"], data["is_ai"])
        player.money = data["money"]
        player.bank_money = data["bank_money"]
        player.position = data["position"]
        player.dice = data["dice"]
        player.items = data["items"]
        player.status = data["status"]
        player.in_jail = data["in_jail"]
        player.jail_turns = data["jail_turns"]
        player.total_income = data["total_income"]
        player.total_expense = data["total_expense"]
        player.properties_bought = data["properties_bought"]
        player.items_used = data["items_used"]
        
        # 房产需要单独处理
        from src.models.property import Property
        player.properties = [Property.from_dict(prop_data) for prop_data in data["properties"]]
        
        return player
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Player({self.name}, ID:{self.player_id}, Money:{self.money}, Position:{self.position})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"Player(player_id={self.player_id}, name='{self.name}', is_ai={self.is_ai}, money={self.money}, position={self.position})"
    
    def move_along_path(self, game_map, steps: int, direction_choices: List[int] = None) -> Dict[str, any]:
        """
        沿路径移动
        
        Args:
            game_map: 游戏地图
            steps: 移动步数
            direction_choices: 方向选择列表
            
        Returns:
            Dict: 移动结果
        """
        if not game_map:
            return {"success": False, "msg": "地图无效"}
        
        # 记录移动前的位置
        old_position = self.position
        
        # 执行移动
        final_index, path_taken = game_map.move_along_path(
            self.position, steps, direction_choices
        )
        
        # 更新位置
        self.position = final_index
        
        # 记录移动历史
        self.movement_history.append({
            "from": old_position,
            "to": final_index,
            "path": path_taken,
            "steps": steps
        })
        
        # 获取最终位置的格子
        final_cell = game_map.get_cell_by_path_index(final_index)
        
        return {
            "success": True,
            "final_position": final_index,
            "path_taken": path_taken,
            "final_cell": final_cell,
            "msg": f"移动到位置 {final_index}"
        }
    
    def get_position_coordinates(self, game_map) -> Optional[Tuple[int, int]]:
        """
        获取当前位置的坐标
        
        Args:
            game_map: 游戏地图
            
        Returns:
            Optional[Tuple[int, int]]: 坐标 (x, y)
        """
        if not game_map:
            return None
        
        return game_map.get_position_by_path_index(self.position)
    
    def get_available_directions(self, game_map) -> List[int]:
        """
        获取当前位置的可用方向
        
        Args:
            game_map: 游戏地图
            
        Returns:
            List[int]: 可用方向列表
        """
        if not game_map:
            return []
        
        return game_map.get_available_directions(self.position)
    
    def set_direction_choices(self, choices: List[int]) -> None:
        """
        设置方向选择
        
        Args:
            choices: 方向选择列表
        """
        self.direction_choices = choices
    
    def clear_direction_choices(self) -> None:
        """清除方向选择"""
        self.direction_choices = []
    
    def is_at_junction(self, game_map) -> bool:
        """
        检查是否在岔路口
        
        Args:
            game_map: 游戏地图
            
        Returns:
            bool: 是否在岔路口
        """
        if not game_map:
            return False
        
        cell = game_map.get_cell_by_path_index(self.position)
        return cell.is_junction if cell else False
    
    def get_movement_history(self) -> List[Dict]:
        """
        获取移动历史
        
        Returns:
            List[Dict]: 移动历史列表
        """
        return self.movement_history.copy()
    
    def clear_movement_history(self) -> None:
        """清除移动历史"""
        self.movement_history.clear() 