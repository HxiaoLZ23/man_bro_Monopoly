"""
玩家管理器
"""
import random
from typing import List, Dict, Optional, Tuple
from src.models.player import Player
from src.models.map import Map
from src.systems.property_manager import PropertyManager
from src.systems.bank_system import BankSystem
from src.systems.event_system import EventManager
from src.systems.shop_system import ShopSystem
from src.core.constants import INITIAL_MONEY, INITIAL_ITEMS
from src.systems.dice_system import DiceSystem


class PlayerManager:
    """玩家管理器"""
    
    def __init__(self):
        """
        初始化玩家管理器
        """
        self.players = []
        self.game_map = None
        
        # 初始化子系统
        self.bank_system = BankSystem()
        self.event_manager = None  # 延迟初始化
        self.dice_system = DiceSystem()
        self.shop_system = ShopSystem()
        self.property_manager = None  # 延迟初始化
        
        # 游戏配置
        self.bankruptcy_threshold = -50000  # 破产阈值
        
    def set_players(self, players: List[Player]):
        """设置玩家列表"""
        self.players = players
        
    def set_game_map(self, game_map: Map):
        """设置游戏地图"""
        self.game_map = game_map
        # 延迟初始化依赖地图的子系统
        if self.game_map:
            self.event_manager = EventManager(self.game_map.width * self.game_map.height)
            self.property_manager = PropertyManager(self.game_map)
        
    def add_player(self, name: str, is_ai: bool = False) -> Player:
        """
        添加玩家
        
        Args:
            name: 玩家名称
            is_ai: 是否为AI玩家
            
        Returns:
            Player: 创建的玩家对象
        """
        player_id = len(self.players) + 1
        player = Player(name, player_id, is_ai)
        
        # 设置初始道具
        for item_name in INITIAL_ITEMS:
            item_id = self._get_item_id_by_name(item_name)
            if item_id:
                player.add_item(item_id, 1)
        
        self.players.append(player)
        return player
    
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
    
    def remove_player(self, player_id: int) -> bool:
        """
        移除玩家
        
        Args:
            player_id: 玩家ID
            
        Returns:
            bool: 操作是否成功
        """
        for i, player in enumerate(self.players):
            if player.player_id == player_id:
                # 处理玩家房产（归还为空地）
                for prop in player.properties[:]:
                    prop.remove_owner()
                    prop.level = 0
                    prop.value = 0
                
                self.players.pop(i)
                return True
        return False
    
    def get_current_player(self) -> Optional[Player]:
        """
        获取当前玩家（已废弃，使用GameState）
        
        Returns:
            Optional[Player]: 当前玩家对象
        """
        if not self.players:
            return None
        return self.players[0]  # 默认返回第一个玩家
    
    def get_player_by_id(self, player_id: int) -> Optional[Player]:
        """
        根据ID获取玩家
        
        Args:
            player_id: 玩家ID
            
        Returns:
            Optional[Player]: 玩家对象
        """
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None
    
    def get_active_players(self) -> List[Player]:
        """
        获取活跃玩家（未破产）
        
        Returns:
            List[Player]: 活跃玩家列表
        """
        return [player for player in self.players if not player.is_bankrupt()]
    
    def roll_dice(self, player: Player) -> Dict[str, any]:
        """
        投掷骰子
        
        Args:
            player: 玩家对象
            
        Returns:
            Dict: 投骰结果
        """
        if not player:
            return {"success": False, "msg": "玩家不存在"}
        
        if player.is_bankrupt():
            return {"success": False, "msg": "玩家已破产"}
        
        # 使用骰子系统投骰子
        dice_result = self.dice_system.roll_dice(player.dice_group)
        
        return {
            "success": True,
            "dice_result": dice_result,
            "msg": f"投掷结果：{dice_result}"
        }
    
    def move_player(self, player: Player, steps: int) -> Dict[str, any]:
        """
        移动玩家
        
        Args:
            player: 玩家对象
            steps: 移动步数
            
        Returns:
            Dict: 移动结果
        """
        if not player or not self.game_map:
            return {"success": False, "msg": "玩家或地图不存在"}
        
        if player.is_bankrupt():
            return {"success": False, "msg": "玩家已破产"}
        
        # 计算新位置
        new_position = (player.position + steps) % self.game_map.get_path_length()
        old_position = player.position
        player.position = new_position
        
        # 处理移动过程中的格子效果
        result = self._handle_movement_effects(player, old_position, new_position)
        
        return {
            "success": True,
            "old_position": old_position,
            "new_position": new_position,
            "steps": steps,
            "effects": result,
            "msg": f"从位置 {old_position} 移动到位置 {new_position}"
        }
    
    def _handle_movement_effects(self, player: Player, old_position: int, new_position: int) -> List[Dict]:
        """处理移动过程中的格子效果"""
        effects = []
        
        # 计算移动路径
        path_length = self.game_map.get_path_length()
        if old_position <= new_position:
            path = list(range(old_position + 1, new_position + 1))
        else:
            path = list(range(old_position + 1, path_length)) + list(range(0, new_position + 1))
        
        # 处理路径上的每个格子
        for pos in path:
            cell = self.game_map.get_cell_at_path_index(pos)
            if cell:
                effect = self._handle_cell_effect(player, cell)
                if effect:
                    effects.append(effect)
        
        return effects
    
    def _handle_cell_effect(self, player: Player, cell) -> Optional[Dict]:
        """处理格子效果"""
        if not cell:
            return None
        
        effect = {
            "position": cell.path_index,
            "cell_type": cell.cell_type,
            "description": ""
        }
        
        # 根据格子类型处理效果
        if cell.cell_type == "luck":
            # 好运格子
            money_gain = random.randint(100, 1000)
            player.money += money_gain
            effect["description"] = f"获得好运奖金 {money_gain}"
            effect["money_change"] = money_gain
            
        elif cell.cell_type == "bad_luck":
            # 厄运格子
            money_loss = random.randint(100, 500)
            player.money -= money_loss
            effect["description"] = f"遭遇厄运损失 {money_loss}"
            effect["money_change"] = -money_loss
            
        elif cell.cell_type == "jail":
            # 监狱格子
            player.jail_turns = 3
            effect["description"] = "进入监狱，停留3回合"
            effect["jail"] = True
            
        elif cell.money > 0:
            # 金钱格子
            player.money += cell.money
            effect["description"] = f"获得金钱 {cell.money}"
            effect["money_change"] = cell.money
            
        elif cell.has_property():
            # 房产格子
            effect.update(self._handle_property_cell(player, cell))
            
        return effect
    
    def _handle_property_cell(self, player: Player, cell) -> Dict:
        """处理房产格子"""
        property_obj = cell.property
        
        if property_obj.is_owned():
            if property_obj.owner_id != player.player_id:
                # 支付租金 - 需要找到房产所有者
                rent = property_obj.get_rent()
                player.money -= rent
                
                # 找到房产所有者并给予租金
                owner = self.get_player_by_id(property_obj.owner_id)
                if owner:
                    owner.money += rent
                    owner_name = owner.name
                else:
                    owner_name = f"玩家{property_obj.owner_id}"
                
                return {
                    "description": f"支付租金 {rent} 给 {owner_name}",
                    "rent_paid": rent,
                    "owner": owner_name
                }
        else:
            # 可购买房产
            return {
                "description": f"可以购买房产，价格 {property_obj.get_upgrade_cost()}",
                "can_buy": True,
                "price": property_obj.get_upgrade_cost()
            }
        
        return {"description": "自己的房产"}
    
    def buy_property(self, player: Player, position: int) -> Dict[str, any]:
        """
        购买房产
        
        Args:
            player: 玩家对象
            position: 位置
            
        Returns:
            Dict: 购买结果
        """
        if not self.game_map:
            return {"success": False, "msg": "地图不存在"}
        
        cell = self.game_map.get_cell_at_path_index(position)
        if not cell or not cell.has_property():
            return {"success": False, "msg": "该位置没有房产"}
        
        property_obj = cell.property
        if property_obj.is_owned():
            return {"success": False, "msg": "该房产已被购买"}
        
        if player.money < property_obj.base_value:
            return {"success": False, "msg": "资金不足"}
        
        # 购买房产
        player.money -= property_obj.base_value
        property_obj.set_owner(player)
        player.properties.append(property_obj)
        
        return {
            "success": True,
            "msg": f"成功购买房产，花费 {property_obj.base_value}",
            "property": property_obj
        }
    
    def upgrade_property(self, player: Player, position: int) -> Dict[str, any]:
        """
        升级房产
        
        Args:
            player: 玩家对象
            position: 位置
            
        Returns:
            Dict: 升级结果
        """
        if not self.game_map:
            return {"success": False, "msg": "地图不存在"}
        
        cell = self.game_map.get_cell_at_path_index(position)
        if not cell or not cell.has_property():
            return {"success": False, "msg": "该位置没有房产"}
        
        property_obj = cell.property
        if not property_obj.is_owned() or property_obj.owner_id != player.player_id:
            return {"success": False, "msg": "该房产不属于你"}
        
        if property_obj.level >= 4:
            return {"success": False, "msg": "房产已达到最高等级"}
        
        upgrade_cost = property_obj.get_upgrade_cost()
        if player.money < upgrade_cost:
            return {"success": False, "msg": "资金不足"}
        
        # 升级房产
        player.money -= upgrade_cost
        property_obj.upgrade()
        
        return {
            "success": True,
            "msg": f"成功升级房产，花费 {upgrade_cost}",
            "new_level": property_obj.level
        }
    
    def use_item(self, player: Player, item_id: int, target_position: int = None) -> Dict[str, any]:
        """
        使用道具
        
        Args:
            player: 玩家对象
            item_id: 道具ID
            target_position: 目标位置（可选）
            
        Returns:
            Dict: 使用结果
        """
        if not player:
            return {"success": False, "msg": "玩家不存在"}
        
        if player.is_bankrupt():
            return {"success": False, "msg": "玩家已破产"}
        
        if item_id not in player.items or player.items[item_id] <= 0:
            return {"success": False, "msg": "道具不足"}
        
        # 使用道具
        player.items[item_id] -= 1
        
        # 根据道具类型执行效果
        item_effects = {
            1: self._use_obstacle_item,
            2: self._use_fly_item,
            3: self._use_protection_item,
            4: self._use_special_item,
            5: self._use_illegal_build_item
        }
        
        effect_func = item_effects.get(item_id)
        if effect_func:
            return effect_func(player, target_position)
        else:
            return {"success": False, "msg": "未知道具"}
    
    def _use_obstacle_item(self, player: Player, target_position: int) -> Dict[str, any]:
        """使用路障道具"""
        if not target_position or not self.game_map:
            return {"success": False, "msg": "需要指定目标位置"}
        
        cell = self.game_map.get_cell_at_path_index(target_position)
        if not cell:
            return {"success": False, "msg": "目标位置无效"}
        
        if cell.has_obstacle():
            return {"success": False, "msg": "该位置已有路障"}
        
        cell.add_obstacle()
        return {"success": True, "msg": f"在位置 {target_position} 放置路障"}
    
    def _use_fly_item(self, player: Player, target_position: int) -> Dict[str, any]:
        """使用飞行道具"""
        if not target_position or not self.game_map:
            return {"success": False, "msg": "需要指定目标位置"}
        
        old_position = player.position
        player.position = target_position
        
        return {
            "success": True,
            "msg": f"从位置 {old_position} 飞到位置 {target_position}",
            "old_position": old_position,
            "new_position": target_position
        }
    
    def _use_protection_item(self, player: Player, target_position: int) -> Dict[str, any]:
        """使用庇护道具"""
        player.protection_turns = 3
        return {"success": True, "msg": "获得3回合庇护"}
    
    def _use_special_item(self, player: Player, target_position: int) -> Dict[str, any]:
        """使用特殊道具"""
        money_gain = 666
        player.money += money_gain
        return {"success": True, "msg": f"获得特殊奖励 {money_gain}"}
    
    def _use_illegal_build_item(self, player: Player, target_position: int) -> Dict[str, any]:
        """使用违规建筑道具"""
        if not target_position or not self.game_map:
            return {"success": False, "msg": "需要指定目标位置"}
        
        cell = self.game_map.get_cell_at_path_index(target_position)
        if not cell or not cell.has_property():
            return {"success": False, "msg": "目标位置没有房产"}
        
        property_obj = cell.property
        if property_obj.owner_id == player.player_id:
            return {"success": False, "msg": "不能对自己的房产使用"}
        
        # 强制升级房产
        property_obj.upgrade()
        return {"success": True, "msg": f"强制升级位置 {target_position} 的房产"}
    
    def ai_decision(self, player: Player) -> Dict[str, any]:
        """
        AI决策
        
        Args:
            player: AI玩家对象
            
        Returns:
            Dict: AI决策结果
        """
        if not player.is_ai:
            return {"success": False, "msg": "不是AI玩家"}
        
        decisions = {}
        
        # AI投骰子决策
        dice_result = self.dice_system.roll_dice(player.dice_group)
        decisions["dice"] = dice_result
        
        # AI购买房产决策
        current_cell = self.game_map.get_cell_at_path_index(player.position)
        if current_cell and current_cell.has_property():
            property_obj = current_cell.property
            if not property_obj.is_owned() and player.money >= property_obj.base_value:
                # 简单AI：有钱就买
                buy_result = self.buy_property(player, player.position)
                if buy_result["success"]:
                    decisions["buy_property"] = True
        
        # AI升级房产决策
        if current_cell and current_cell.has_property():
            property_obj = current_cell.property
            if property_obj.owner_id == player.player_id and property_obj.level < 4:
                upgrade_cost = property_obj.get_upgrade_cost()
                if player.money >= upgrade_cost:
                    # 简单AI：有钱就升级
                    upgrade_result = self.upgrade_property(player, player.position)
                    if upgrade_result["success"]:
                        decisions["upgrade_property"] = True
        
        return {
            "success": True,
            "decisions": decisions,
            "msg": f"AI决策完成：{decisions}"
        }
    
    def get_game_status(self) -> Dict[str, any]:
        """
        获取游戏状态
        
        Returns:
            Dict: 游戏状态信息
        """
        active_players = self.get_active_players()
        
        return {
            "total_players": len(self.players),
            "active_players": len(active_players),
            "game_ended": len(active_players) <= 1,
            "winner": active_players[0] if len(active_players) == 1 else None
        }
    
    def get_player_rankings(self) -> List[Dict[str, any]]:
        """
        获取玩家排名
        
        Returns:
            List[Dict]: 玩家排名列表
        """
        # 按资金排序
        sorted_players = sorted(self.players, key=lambda p: p.money, reverse=True)
        
        rankings = []
        for i, player in enumerate(sorted_players):
            rankings.append({
                "rank": i + 1,
                "player_id": player.player_id,
                "name": player.name,
                "money": player.money,
                "properties": len(player.properties),
                "is_bankrupt": player.is_bankrupt()
            })
        
        return rankings 