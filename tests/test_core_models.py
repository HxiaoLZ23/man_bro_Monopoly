"""
核心模型测试
"""
import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.player import Player
from src.models.property import Property
from src.models.map import Map, Cell
from src.models.game_state import GameState
from src.systems.dice_system import DiceSystem, Dice, DiceSet


class TestPlayer(unittest.TestCase):
    """玩家类测试"""
    
    def setUp(self):
        """测试前准备"""
        self.player = Player(1, "测试玩家", False)
    
    def test_player_initialization(self):
        """测试玩家初始化"""
        self.assertEqual(self.player.player_id, 1)
        self.assertEqual(self.player.name, "测试玩家")
        self.assertFalse(self.player.is_ai)
        self.assertEqual(self.player.money, 200000)
        self.assertEqual(self.player.position, 0)
        self.assertEqual(self.player.dice, "d6")
        self.assertEqual(len(self.player.items), 3)
        self.assertIn("路障", self.player.items)
    
    def test_money_operations(self):
        """测试金钱操作"""
        # 测试增加金钱
        self.assertTrue(self.player.add_money(50000))
        self.assertEqual(self.player.money, 250000)
        self.assertEqual(self.player.total_income, 50000)
        
        # 测试减少金钱
        self.assertTrue(self.player.remove_money(30000))
        self.assertEqual(self.player.money, 220000)
        self.assertEqual(self.player.total_expense, 30000)
        
        # 测试减少超过余额，money允许为负
        self.assertTrue(self.player.remove_money(300000))
        self.assertEqual(self.player.money, -80000)
    
    def test_item_operations(self):
        """测试道具操作"""
        # 测试添加道具
        self.assertTrue(self.player.add_item("庇护术"))
        self.assertIn("庇护术", self.player.items)
        
        # 测试使用道具
        item_name = self.player.use_item(0)
        self.assertEqual(item_name, "路障")
        self.assertEqual(len(self.player.items), 3)
        
        # 测试检查道具
        self.assertTrue(self.player.has_item("路障"))
        self.assertFalse(self.player.has_item("不存在的道具"))
    
    def test_property_operations(self):
        """测试房产操作"""
        property_obj = Property(5, 1, 1)
        
        # 测试添加房产
        self.assertTrue(self.player.add_property(property_obj))
        self.assertEqual(len(self.player.properties), 1)
        
        # 测试获取房产
        found_property = self.player.get_property_at_position(5)
        self.assertEqual(found_property, property_obj)
        
        # 测试移除房产
        self.assertTrue(self.player.remove_property(property_obj))
        self.assertEqual(len(self.player.properties), 0)
    
    def test_status_operations(self):
        """测试状态操作"""
        # 测试添加状态
        self.player.add_status("飞行", 3)
        self.assertTrue(self.player.has_status("飞行"))
        self.assertEqual(self.player.status["飞行"], 3)
        
        # 测试更新状态持续时间
        self.player.update_status_duration()
        self.assertEqual(self.player.status["飞行"], 2)
        
        # 测试移除状态
        self.assertTrue(self.player.remove_status("飞行"))
        self.assertFalse(self.player.has_status("飞行"))
    
    def test_jail_operations(self):
        """测试监狱操作"""
        # 测试进入监狱
        self.player.go_to_jail()
        self.assertTrue(self.player.in_jail)
        self.assertEqual(self.player.jail_turns, 0)
        
        # 测试越狱失败
        self.assertFalse(self.player.try_escape_jail(3))
        self.assertTrue(self.player.in_jail)
        
        # 测试越狱成功
        self.assertTrue(self.player.try_escape_jail(6))
        self.assertFalse(self.player.in_jail)
    
    def test_bankruptcy_check(self):
        """测试破产检查"""
        # 正常情况
        self.assertFalse(self.player.is_bankrupt())
        
        # 破产情况
        self.player.remove_money(200000)
        self.player.remove_money(50000)
        self.assertTrue(self.player.is_bankrupt())


class TestProperty(unittest.TestCase):
    """房产类测试"""
    
    def setUp(self):
        """测试前准备"""
        self.property = Property(10, 1, 2)
    
    def test_property_initialization(self):
        """测试房产初始化"""
        self.assertEqual(self.property.position, 10)
        self.assertEqual(self.property.owner_id, 1)
        self.assertEqual(self.property.level, 2)
        self.assertEqual(self.property.value, 30000)  # 10000 + 20000
    
    def test_rent_calculation(self):
        """测试租金计算"""
        self.assertEqual(self.property.get_rent(), 10000)
        
        # 测试不同等级的租金
        property_lv1 = Property(5, 1, 1)
        self.assertEqual(property_lv1.get_rent(), 5000)
        
        property_lv4 = Property(15, 1, 4)
        self.assertEqual(property_lv4.get_rent(), 50000)
    
    def test_upgrade_operations(self):
        """测试升级操作"""
        # 测试升级
        self.assertTrue(self.property.upgrade())
        self.assertEqual(self.property.level, 3)
        self.assertEqual(self.property.value, 60000)  # 10000 + 20000 + 30000
        
        # 测试升级费用
        self.assertEqual(self.property.get_upgrade_cost(), 0)  # 四级房产无法通过金钱升级
        
        # 测试降级
        self.assertTrue(self.property.downgrade())
        self.assertEqual(self.property.level, 2)
        self.assertEqual(self.property.value, 30000)
    
    def test_owner_operations(self):
        """测试所有者操作"""
        # 测试设置所有者
        self.property.set_owner(2)
        self.assertEqual(self.property.owner_id, 2)
        self.assertTrue(self.property.is_owned())
        
        # 测试移除所有者
        self.property.remove_owner()
        self.assertIsNone(self.property.owner_id)
        self.assertFalse(self.property.is_owned())


class TestMap(unittest.TestCase):
    """地图类测试"""
    
    def setUp(self):
        """测试前准备"""
        self.map = Map(10, 10)  # 使用较小的地图进行测试
    
    def test_map_initialization(self):
        """测试地图初始化"""
        self.assertEqual(self.map.width, 10)
        self.assertEqual(self.map.height, 10)
        self.assertEqual(len(self.map.cells), 100)
        self.assertGreater(len(self.map.path), 0)
    
    def test_cell_operations(self):
        """测试格子操作"""
        # 测试获取格子
        cell = self.map.get_cell_at((5, 5))
        self.assertIsNotNone(cell)
        self.assertEqual(cell.position, (5, 5))
        
        # 测试设置格子类型
        self.assertTrue(self.map.set_cell_type((5, 5), "bank"))
        cell = self.map.get_cell_at((5, 5))
        self.assertEqual(cell.cell_type, "bank")
    
    def test_path_operations(self):
        """测试路径操作"""
        # 测试路径索引
        path_index = self.map.get_path_index((0, 0))
        self.assertGreaterEqual(path_index, 0)
        
        # 测试根据路径索引获取位置
        position = self.map.get_position_by_path_index(0)
        self.assertIsNotNone(position)
        
        # 测试根据路径索引获取格子
        cell = self.map.get_cell_by_path_index(0)
        self.assertIsNotNone(cell)
    
    def test_distance_calculation(self):
        """测试距离计算"""
        distance = self.map.calculate_distance((0, 0), (3, 4))
        self.assertEqual(distance, 7)  # 3 + 4 = 7
    
    def test_roadblock_operations(self):
        """测试路障操作"""
        # 测试放置路障
        self.assertTrue(self.map.place_roadblock((5, 5)))
        self.assertTrue(self.map.has_roadblock((5, 5)))
        
        # 测试移除路障
        self.assertTrue(self.map.remove_roadblock((5, 5)))
        self.assertFalse(self.map.has_roadblock((5, 5)))


class TestGameState(unittest.TestCase):
    """游戏状态类测试"""
    
    def setUp(self):
        """测试前准备"""
        self.game_state = GameState()
        self.players = [
            Player(1, "玩家1", False),
            Player(2, "玩家2", True),
            Player(3, "玩家3", False)
        ]
        self.map = Map(10, 10)
    
    def test_game_state_initialization(self):
        """测试游戏状态初始化"""
        self.assertEqual(self.game_state.game_state, "waiting")
        self.assertEqual(self.game_state.current_phase, "preparation")
        self.assertEqual(self.game_state.current_player_index, 0)
        self.assertEqual(self.game_state.turn_count, 0)
    
    def test_game_initialization(self):
        """测试游戏初始化"""
        self.assertTrue(self.game_state.initialize_game(self.players, self.map))
        self.assertEqual(self.game_state.game_state, "playing")
        self.assertEqual(len(self.game_state.players), 3)
        self.assertIsNotNone(self.game_state.map)
    
    def test_player_management(self):
        """测试玩家管理"""
        self.game_state.initialize_game(self.players, self.map)
        
        # 测试获取当前玩家
        current_player = self.game_state.get_current_player()
        self.assertEqual(current_player.player_id, 1)
        
        # 测试切换到下一个玩家
        next_player = self.game_state.next_player()
        self.assertEqual(next_player.player_id, 2)
        self.assertEqual(self.game_state.turn_count, 1)
        
        # 测试根据ID获取玩家
        player = self.game_state.get_player_by_id(3)
        self.assertEqual(player.name, "玩家3")
    
    def test_game_over_check(self):
        """测试游戏结束检查"""
        self.game_state.initialize_game(self.players, self.map)
        
        # 正常情况
        self.assertFalse(self.game_state.check_game_over())
        
        # 模拟玩家破产
        self.players[1].remove_money(200001)
        self.players[2].remove_money(200001)
        # 确认money为负
        self.assertTrue(self.players[1].is_bankrupt())
        self.assertTrue(self.players[2].is_bankrupt())
        self.assertTrue(self.game_state.check_game_over())
        self.assertEqual(self.game_state.winner.player_id, 1)


class TestDiceSystem(unittest.TestCase):
    """骰子系统测试"""
    
    def setUp(self):
        """测试前准备"""
        self.dice_system = DiceSystem()
    
    def test_dice_system_initialization(self):
        """测试骰子系统初始化"""
        self.assertEqual(self.dice_system.current_dice_type, "d6")
        self.assertIn("d6", self.dice_system.available_dice_types)
    
    def test_dice_operations(self):
        """测试骰子操作"""
        # 测试投掷d6
        result = self.dice_system.roll_current_dice_sum()
        self.assertGreaterEqual(result, 1)
        self.assertLessEqual(result, 6)
        
        # 测试添加骰子类型
        self.assertTrue(self.dice_system.add_dice_type("d8"))
        self.assertIn("d8", self.dice_system.available_dice_types)
        
        # 测试切换骰子
        self.assertTrue(self.dice_system.set_current_dice("d8"))
        self.assertEqual(self.dice_system.current_dice_type, "d8")
    
    def test_dice_price(self):
        """测试骰子价格"""
        price = self.dice_system.get_dice_price("d8")
        self.assertEqual(price["money"], 10000)
        self.assertEqual(price["items"], 1)
        
        # 测试购买能力检查
        self.assertTrue(self.dice_system.can_afford_dice("d8", 15000, 2))
        self.assertFalse(self.dice_system.can_afford_dice("d8", 5000, 2))


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2) 