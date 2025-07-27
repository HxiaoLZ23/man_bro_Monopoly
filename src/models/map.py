"""
地图数据模型
"""
from typing import List, Dict, Tuple, Optional, Set
from src.core.constants import MAP_WIDTH, MAP_HEIGHT, CELL_TYPES, CELL_COLORS
from src.models.property import Property


class Cell:
    """地图格子类"""
    
    def __init__(self, cell_type: str, position: Tuple[int, int]):
        """
        初始化格子
        
        Args:
            cell_type: 格子类型
            position: 格子位置 (x, y)
        """
        self.cell_type = cell_type
        self.position = position
        self.x, self.y = position
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
        type_names = {
            "empty": "空地",
            "wall": "墙",
            "void": "空格",
            "bank": "银行",
            "shop": "道具商店",
            "dice_shop": "骰子商店",
            "jail": "监狱",
            "luck": "好运格",
            "bad_luck": "厄运格"
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
            "cell_type": self.cell_type,
            "position": self.position,
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
        cell = cls(data["cell_type"], data["position"])
        cell.path_index = data["path_index"]
        cell.roadblock = data["roadblock"]
        cell.money_on_ground = data["money_on_ground"]
        cell.connections = set(data.get("connections", []))
        cell.is_junction = data.get("is_junction", False)
        
        if data["property"]:
            cell.property = Property.from_dict(data["property"])
        
        return cell


class Map:
    """地图类"""
    
    def __init__(self, width: int = MAP_WIDTH, height: int = MAP_HEIGHT):
        """
        初始化地图
        
        Args:
            width: 地图宽度
            height: 地图高度
        """
        self.width = width
        self.height = height
        self.cells = []  # 所有格子
        self.path = []   # 路径点列表
        self.path_length = 0  # 路径总长度
        self.junctions = set()  # 岔路口集合
        
        self._initialize_map()
        self._setup_path()
        self._setup_special_cells()
    
    def _initialize_map(self) -> None:
        """初始化地图格子"""
        self.cells = []
        for y in range(self.height):
            for x in range(self.width):
                # 默认内部为空格，边缘为墙
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    cell_type = "wall"
                else:
                    cell_type = "void"
                cell = Cell(cell_type, (x, y))
                self.cells.append(cell)
    
    def _setup_path(self) -> None:
        """设置地图路径"""
        self.path = []
        
        # 外圈路径：顺时针方向
        # 上边
        for x in range(self.width):
            self.path.append((x, 0))
        
        # 右边
        for y in range(1, self.height):
            self.path.append((self.width - 1, y))
        
        # 下边
        for x in range(self.width - 2, -1, -1):
            self.path.append((x, self.height - 1))
        
        # 左边
        for y in range(self.height - 2, 0, -1):
            self.path.append((0, y))
        
        self.path_length = len(self.path)
        
        # 设置每个格子的路径索引和连接
        for i, (x, y) in enumerate(self.path):
            cell = self.get_cell_at((x, y))
            if cell:
                cell.cell_type = "empty"  # 路径格子设为空地
                cell.path_index = i
                # 设置连接（环形路径）
                prev_index = (i - 1) % self.path_length
                next_index = (i + 1) % self.path_length
                cell.connections = {prev_index, next_index}
        
        # 检测岔路口
        self._detect_junctions()
        
        # 创建path_cells属性（为了兼容性）
        self.path_cells = []
        for i in range(self.path_length):
            self.path_cells.append(self.get_cell_by_path_index(i))
    
    def _detect_junctions(self) -> None:
        """检测岔路口"""
        self.junctions.clear()
        
        for i, (x, y) in enumerate(self.path):
            cell = self.get_cell_at((x, y))
            if cell and len(cell.connections) > 2:
                cell.is_junction = True
                self.junctions.add(i)
    
    def add_path_connection(self, from_index: int, to_index: int) -> bool:
        """
        添加路径连接（创建岔路）
        
        Args:
            from_index: 起始路径索引
            to_index: 目标路径索引
            
        Returns:
            bool: 是否成功添加连接
        """
        if not (0 <= from_index < self.path_length and 0 <= to_index < self.path_length):
            return False
        
        from_cell = self.get_cell_by_path_index(from_index)
        to_cell = self.get_cell_by_path_index(to_index)
        
        if from_cell and to_cell:
            from_cell.connections.add(to_index)
            to_cell.connections.add(from_index)
            
            # 重新检测岔路口
            self._detect_junctions()
            return True
        
        return False
    
    def remove_path_connection(self, from_index: int, to_index: int) -> bool:
        """
        移除路径连接
        
        Args:
            from_index: 起始路径索引
            to_index: 目标路径索引
            
        Returns:
            bool: 是否成功移除连接
        """
        if not (0 <= from_index < self.path_length and 0 <= to_index < self.path_length):
            return False
        
        from_cell = self.get_cell_by_path_index(from_index)
        to_cell = self.get_cell_by_path_index(to_index)
        
        if from_cell and to_cell:
            from_cell.connections.discard(to_index)
            to_cell.connections.discard(from_index)
            
            # 重新检测岔路口
            self._detect_junctions()
            return True
        
        return False
    
    def get_available_directions(self, path_index: int) -> List[int]:
        """
        获取当前位置可用的移动方向
        
        Args:
            path_index: 当前路径索引
            
        Returns:
            List[int]: 可用的路径索引列表
        """
        cell = self.get_cell_by_path_index(path_index)
        if not cell:
            return []
        
        # 返回所有连接的方向，不过滤路障
        # 路障的处理应该在实际移动时进行
        available = []
        for next_index in cell.connections:
            next_cell = self.get_cell_by_path_index(next_index)
            if next_cell:  # 只检查格子是否存在，不检查路障
                available.append(next_index)
        
        return available
    
    def find_path_to_target(self, start_index: int, target_index: int, 
                           max_steps: int) -> Optional[List[int]]:
        """
        寻找从起点到目标的路径
        
        Args:
            start_index: 起始路径索引
            target_index: 目标路径索引
            max_steps: 最大步数
            
        Returns:
            Optional[List[int]]: 路径索引列表，如果找不到则返回None
        """
        if start_index == target_index:
            return [start_index]
        
        # 使用BFS寻找最短路径
        visited = set()
        queue = [(start_index, [start_index])]
        
        while queue:
            current_index, path = queue.pop(0)
            
            if current_index == target_index:
                return path
            
            if len(path) > max_steps:
                continue
            
            if current_index in visited:
                continue
            
            visited.add(current_index)
            
            for next_index in self.get_available_directions(current_index):
                if next_index not in visited:
                    new_path = path + [next_index]
                    queue.append((next_index, new_path))
        
        return None
    
    def _choose_forward_direction(self, current_index: int, available: List[int], path_taken: List[int]) -> int:
        """
        选择前进方向，避免回头路
        
        Args:
            current_index: 当前位置索引
            available: 可用方向列表
            path_taken: 已走过的路径
            
        Returns:
            int: 选择的下一个位置索引
        """
        if len(available) == 1:
            return available[0]
        
        # 计算期望的下一个位置（顺时针方向）
        next_expected = (current_index + 1) % self.path_length
        
        # 如果期望的顺时针方向可用，优先选择它
        if next_expected in available:
            return next_expected
        
        # 如果路径长度大于1，避免回到上一个位置
        if len(path_taken) > 1:
            previous_index = path_taken[-2]
            forward_directions = [idx for idx in available if idx != previous_index]
            if forward_directions:
                # 选择最接近顺时针方向的选项
                forward_directions.sort()
                
                # 对于环形路径，处理跨越边界的情况
                if current_index >= self.path_length - 5:  # 接近路径末尾
                    # 优先选择小索引（跨越到路径开始）
                    for direction in forward_directions:
                        if direction < current_index:
                            return direction
                
                # 否则选择大于当前索引的方向
                for direction in forward_directions:
                    if direction > current_index:
                        return direction
                
                # 如果没有找到合适的方向，选择第一个可用的非回头方向
                return forward_directions[0]
        
        # 默认选择第一个可用方向
        return available[0]

    def move_along_path(self, start_index: int, steps: int, 
                       direction_choices: List[int] = None) -> Tuple[int, List[int]]:
        """
        沿路径移动
        
        Args:
            start_index: 起始路径索引
            steps: 移动步数
            direction_choices: 方向选择列表（用于岔路口）
            
        Returns:
            Tuple[int, List[int]]: (最终位置索引, 移动路径)
        """
        if steps <= 0:
            return start_index, [start_index]
        
        current_index = start_index
        path_taken = [current_index]
        direction_index = 0
        
        for step in range(steps):
            available = self.get_available_directions(current_index)
            
            if not available:
                break  # 无法继续移动
            
            # 如果有多个方向且提供了方向选择
            if len(available) > 1 and direction_choices and direction_index < len(direction_choices):
                chosen_index = direction_choices[direction_index]
                if chosen_index in available:
                    next_index = chosen_index
                    direction_index += 1
                else:
                    # 选择无效，选择前进方向
                    next_index = self._choose_forward_direction(current_index, available, path_taken)
            else:
                # 只有一个方向或没有提供选择，选择前进方向
                next_index = self._choose_forward_direction(current_index, available, path_taken)
            
            # 移动到下一个位置
            current_index = next_index
            path_taken.append(current_index)
            
            # 移动后检查当前位置是否有路障
            current_cell = self.get_cell_by_path_index(current_index)
            if current_cell and current_cell.roadblock:
                # 到达路障格子，停止移动（路障的移除由上层逻辑处理）
                break
        
        return current_index, path_taken
    
    def _setup_special_cells(self) -> None:
        """设置特殊格子"""
        # 设置银行（在路径上随机选择几个位置）
        bank_positions = [(5, 0), (15, 0), (19, 5), (19, 15), (15, 19), (5, 19), (0, 15), (0, 5)]
        for pos in bank_positions:
            if 0 <= pos[0] < self.width and 0 <= pos[1] < self.height:
                self.set_cell_type(pos, "bank")
        
        # 设置道具商店
        shop_positions = [(10, 0), (19, 10), (10, 19), (0, 10)]
        for pos in shop_positions:
            if 0 <= pos[0] < self.width and 0 <= pos[1] < self.height:
                self.set_cell_type(pos, "shop")
        
        # 设置骰子商店
        dice_shop_positions = [(8, 0), (12, 0), (19, 8), (19, 12), (12, 19), (8, 19), (0, 12), (0, 8)]
        for pos in dice_shop_positions:
            if 0 <= pos[0] < self.width and 0 <= pos[1] < self.height:
                self.set_cell_type(pos, "dice_shop")
        
        # 设置监狱
        jail_positions = [(3, 0), (17, 0), (19, 3), (19, 17), (17, 19), (3, 19), (0, 17), (0, 3)]
        for pos in jail_positions:
            if 0 <= pos[0] < self.width and 0 <= pos[1] < self.height:
                self.set_cell_type(pos, "jail")
        
        # 设置好运格和厄运格
        luck_positions = [(7, 0), (13, 0), (19, 7), (19, 13), (13, 19), (7, 19), (0, 13), (0, 7)]
        for i, pos in enumerate(luck_positions):
            if 0 <= pos[0] < self.width and 0 <= pos[1] < self.height:
                cell_type = "luck" if i % 2 == 0 else "bad_luck"
                self.set_cell_type(pos, cell_type)
    
    def get_cell_at(self, position: Tuple[int, int]) -> Optional[Cell]:
        """
        获取指定位置的格子
        
        Args:
            position: 位置坐标 (x, y)
            
        Returns:
            Optional[Cell]: 格子对象，如果位置无效则返回None
        """
        x, y = position
        if 0 <= x < self.width and 0 <= y < self.height:
            index = y * self.width + x
            return self.cells[index]
        return None
    
    def set_cell_type(self, position: Tuple[int, int], cell_type: str) -> bool:
        """
        设置格子类型
        
        Args:
            position: 位置坐标 (x, y)
            cell_type: 格子类型
            
        Returns:
            bool: 操作是否成功
        """
        cell = self.get_cell_at(position)
        if cell:
            cell.cell_type = cell_type
            return True
        return False
    
    def get_cell_by_path_index(self, path_index: int) -> Optional[Cell]:
        """
        通过路径索引获取格子
        
        Args:
            path_index: 路径索引
            
        Returns:
            Optional[Cell]: 格子对象
        """
        if 0 <= path_index < len(self.path):
            position = self.path[path_index]
            return self.get_cell_at(position)
        return None
    
    def get_path_index(self, position: Tuple[int, int]) -> int:
        """
        获取位置的路径索引
        
        Args:
            position: 位置坐标 (x, y)
            
        Returns:
            int: 路径索引，-1表示不在路径上
        """
        cell = self.get_cell_at(position)
        if cell:
            return cell.path_index
        return -1
    
    def get_position_by_path_index(self, path_index: int) -> Optional[Tuple[int, int]]:
        """
        通过路径索引获取位置
        
        Args:
            path_index: 路径索引
            
        Returns:
            Optional[Tuple[int, int]]: 位置坐标
        """
        if 0 <= path_index < len(self.path):
            return self.path[path_index]
        return None
    
    def calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """
        计算两点间的曼哈顿距离
        
        Args:
            pos1: 位置1 (x, y)
            pos2: 位置2 (x, y)
            
        Returns:
            int: 距离
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def get_cells_in_range(self, center: Tuple[int, int], max_distance: int) -> List[Cell]:
        """
        获取指定范围内的格子
        
        Args:
            center: 中心位置 (x, y)
            max_distance: 最大距离
            
        Returns:
            List[Cell]: 范围内的格子列表
        """
        cells = []
        center_x, center_y = center
        
        for y in range(max(0, center_y - max_distance), min(self.height, center_y + max_distance + 1)):
            for x in range(max(0, center_x - max_distance), min(self.width, center_x + max_distance + 1)):
                if self.calculate_distance(center, (x, y)) <= max_distance:
                    cell = self.get_cell_at((x, y))
                    if cell:
                        cells.append(cell)
        
        return cells
    
    def place_roadblock(self, position: Tuple[int, int]) -> bool:
        """
        放置路障
        
        Args:
            position: 位置坐标 (x, y)
            
        Returns:
            bool: 操作是否成功
        """
        cell = self.get_cell_at(position)
        if cell and cell.is_path_cell():
            cell.set_roadblock(True)
            return True
        return False
    
    def remove_roadblock(self, position: Tuple[int, int]) -> bool:
        """
        移除路障
        
        Args:
            position: 位置坐标 (x, y)
            
        Returns:
            bool: 操作是否成功
        """
        cell = self.get_cell_at(position)
        if cell:
            cell.set_roadblock(False)
            return True
        return False
    
    def has_roadblock(self, position: Tuple[int, int]) -> bool:
        """
        检查是否有路障
        
        Args:
            position: 位置坐标 (x, y)
            
        Returns:
            bool: 是否有路障
        """
        cell = self.get_cell_at(position)
        if cell:
            return cell.roadblock
        return False
    
    def to_dict(self) -> Dict:
        """
        转换为字典格式
        
        Returns:
            Dict: 地图数据字典
        """
        return {
            "width": self.width,
            "height": self.height,
            "cells": [cell.to_dict() for cell in self.cells],
            "path": self.path,
            "path_length": self.path_length,
            "junctions": list(self.junctions)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Map':
        """
        从字典创建地图对象
        """
        map_obj = cls(data["width"], data["height"])
        map_obj.path = data["path"]
        # 兼容无path_length和junctions字段的老地图
        map_obj.path_length = data.get("path_length", len(map_obj.path) if map_obj.path else 0)
        map_obj.junctions = set(data.get("junctions", []))
        # 重建格子
        for cell_data in data["cells"]:
            # 兼容老格式：如果没有position字段，则用x/y
            if "position" not in cell_data and "x" in cell_data and "y" in cell_data:
                cell_data["position"] = (cell_data["x"], cell_data["y"])
            cell = Cell.from_dict(cell_data)
            x, y = cell.position
            index = y * map_obj.width + x
            map_obj.cells[index] = cell
        return map_obj
    
    def __str__(self) -> str:
        return f"Map({self.width}x{self.height}, path_length={self.path_length})"
    
    def __repr__(self) -> str:
        return self.__str__() 