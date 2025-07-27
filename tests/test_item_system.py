"""
道具系统测试
"""
import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.item import Item, RoadblockItem, FlyItem, ProtectionItem, SixSixSixItem, PropertyUpgradeItem, create_item_by_id
from src.systems.item_manager import ItemManager
from src.models.player import Player


class TestItemBase(unittest.TestCase):
    """道具基类测试"""
    
    def test_item_creation(self):
        """测试道具创建"""
        item = RoadblockItem()  # 使用具体道具类而不是抽象基类
        self.assertEqual(item.item_id, 1)
        self.assertEqual(item.name, "路障")
        self.assertTrue(item.stackable)
        self.assertEqual(item.max_count, 10)
    
    def test_item_serialization(self):
        """测试道具序列化"""
        item = RoadblockItem()  # 使用具体道具类
        data = item.to_dict()                                 
        
        self.assertEqual(data["item_id"], 1)
        self.assertEqual(data["name"], "路障")
        self.assertEqual(data["desc"], "在距自身直线距离不超过14的格子上放置一个路障，当有玩家在移动时碰到该路障，则立即停止移动。")
        self.assertTrue(data["stackable"])
        self.assertEqual(data["max_count"], 10)
        
        # 测试反序列化
        new_item = RoadblockItem.from_dict(data)
        self.assertEqual(new_item.item_id, item.item_id)
        self.assertEqual(new_item.name, item.name)
        self.assertEqual(new_item.desc, item.desc)
        self.assertEqual(new_item.stackable, item.stackable)
        self.assertEqual(new_item.max_count, item.max_count)
    
    def test_item_use_not_implemented(self):
        """测试道具使用方法已实现"""
        item = RoadblockItem()
        # 现在道具基类有抽象方法，具体类必须实现
        self.assertTrue(hasattr(item, 'use'))
        self.assertTrue(callable(item.use))


class TestRoadblockItem(unittest.TestCase):
    """路障道具测试"""
    
    def setUp(self):
        """测试前准备"""
        self.item = RoadblockItem()
        self.mock_game = type('MockGame', (), {
            'map': type('MockMap', (), {
                'get_cell_at': lambda pos: type('MockCell', (), {
                    'roadblock': False
                })()
            })()
        })()
    
    def test_roadblock_creation(self):
        """测试路障创建"""
        self.assertEqual(self.item.item_id, 1)
        self.assertEqual(self.item.name, "路障")
        self.assertTrue(self.item.stackable)
        self.assertEqual(self.item.max_count, 10)
    
    def test_roadblock_use_success(self):
        """测试路障使用成功"""
        # 修复lambda函数参数问题
        mock_cell = type('MockCell', (), {'roadblock': False})()
        self.mock_game.map.get_cell_at = lambda pos: mock_cell
        
        result = self.item.use(None, (5, 5), self.mock_game)
        self.assertTrue(result["success"])
        self.assertIn("放置了路障", result["msg"])
    
    def test_roadblock_use_failure(self):
        """测试路障使用失败"""
        # 测试无效地图
        result = self.item.use(None, (5, 5), None)
        self.assertFalse(result["success"])
        self.assertEqual(result["msg"], "地图无效")


class TestFlyItem(unittest.TestCase):
    """再装逼让你飞起来!!道具测试"""
    
    def setUp(self):
        """测试前准备"""
        self.item = FlyItem()
        self.mock_player = type('MockPlayer', (), {
            'name': '测试玩家',
            'fly_mode': False
        })()
    
    def test_fly_creation(self):
        """测试起飞道具创建"""
        self.assertEqual(self.item.item_id, 2)
        self.assertEqual(self.item.name, "再装逼让你飞起来!!")
        self.assertTrue(self.item.stackable)
        self.assertEqual(self.item.max_count, 5)
    
    def test_fly_use_self(self):
        """测试起飞道具对自己使用"""
        result = self.item.use(self.mock_player)
        self.assertTrue(result["success"])
        self.assertTrue(self.mock_player.fly_mode)
        self.assertIn("获得了【起飞】效果", result["msg"])
    
    def test_fly_use_target(self):
        """测试起飞道具对目标使用"""
        target_player = type('MockPlayer', (), {
            'name': '目标玩家',
            'fly_mode': False
        })()
        
        result = self.item.use(self.mock_player, target_player)
        self.assertTrue(result["success"])
        self.assertTrue(target_player.fly_mode)
        self.assertIn("获得了【起飞】效果", result["msg"])


class TestProtectionItem(unittest.TestCase):
    """庇护术道具测试"""
    
    def setUp(self):
        """测试前准备"""
        self.item = ProtectionItem()
        self.mock_player = type('MockPlayer', (), {
            'name': '测试玩家',
            'protection': False
        })()
    
    def test_protection_creation(self):
        """测试庇护术创建"""
        self.assertEqual(self.item.item_id, 3)
        self.assertEqual(self.item.name, "庇护术")
        self.assertTrue(self.item.stackable)
        self.assertEqual(self.item.max_count, 5)
    
    def test_protection_use(self):
        """测试庇护术使用"""
        result = self.item.use(self.mock_player)
        self.assertTrue(result["success"])
        self.assertTrue(self.mock_player.protection)
        self.assertIn("获得了【庇护】效果", result["msg"])


class TestSixSixSixItem(unittest.TestCase):
    """六百六十六道具测试"""
    
    def setUp(self):
        """测试前准备"""
        self.item = SixSixSixItem()
        self.mock_player = type('MockPlayer', (), {
            'name': '测试玩家',
            'next_dice_value': None
        })()
    
    def test_sixsixsix_creation(self):
        """测试六百六十六创建"""
        self.assertEqual(self.item.item_id, 4)
        self.assertEqual(self.item.name, "六百六十六")
        self.assertTrue(self.item.stackable)
        self.assertEqual(self.item.max_count, 5)
    
    def test_sixsixsix_use(self):
        """测试六百六十六使用"""
        result = self.item.use(self.mock_player)
        self.assertTrue(result["success"])
        self.assertEqual(self.mock_player.next_dice_value, 6)
        self.assertIn("下次投掷结果将固定为6", result["msg"])


class TestPropertyUpgradeItem(unittest.TestCase):
    """违规爆建道具测试"""
    
    def setUp(self):
        """测试前准备"""
        self.item = PropertyUpgradeItem()
        self.mock_player = type('MockPlayer', (), {
            'name': '测试玩家'
        })()
        self.mock_property = type('MockProperty', (), {
            'name': '测试房产',
            'level': 1,
            'owner': type('MockOwner', (), {'name': '房主'})()
        })()
    
    def test_property_upgrade_creation(self):
        """测试违规爆建创建"""
        self.assertEqual(self.item.item_id, 5)
        self.assertEqual(self.item.name, "违规爆建")
        self.assertTrue(self.item.stackable)
        self.assertEqual(self.item.max_count, 3)
    
    def test_property_upgrade_success(self):
        """测试房产升级成功"""
        result = self.item.use(self.mock_player, self.mock_property, upgrade=True)
        self.assertTrue(result["success"])
        self.assertEqual(self.mock_property.level, 2)
        self.assertIn("升级到2级", result["msg"])
    
    def test_property_upgrade_max_level(self):
        """测试房产已达到最高等级"""
        self.mock_property.level = 4
        result = self.item.use(self.mock_player, self.mock_property, upgrade=True)
        self.assertFalse(result["success"])
        self.assertEqual(result["msg"], "房产已达到最高等级")
    
    def test_property_downgrade_success(self):
        """测试房产降级成功"""
        self.mock_property.level = 2
        result = self.item.use(self.mock_player, self.mock_property, upgrade=False)
        self.assertTrue(result["success"])
        self.assertEqual(self.mock_property.level, 1)
        self.assertIn("降级到1级", result["msg"])
    
    def test_property_downgrade_to_empty(self):
        """测试房产降级为空地"""
        self.mock_property.level = 1
        result = self.item.use(self.mock_player, self.mock_property, upgrade=False)
        self.assertTrue(result["success"])
        self.assertEqual(self.mock_property.level, 0)
        self.assertIsNone(self.mock_property.owner)
        self.assertIn("降级为空地", result["msg"])


class TestItemFactory(unittest.TestCase):
    """道具工厂测试"""
    
    def test_create_item_by_id_valid(self):
        """测试通过ID创建有效道具"""
        item = create_item_by_id(1)
        self.assertIsInstance(item, RoadblockItem)
        
        item = create_item_by_id(2)
        self.assertIsInstance(item, FlyItem)
        
        item = create_item_by_id(3)
        self.assertIsInstance(item, ProtectionItem)
        
        item = create_item_by_id(4)
        self.assertIsInstance(item, SixSixSixItem)
        
        item = create_item_by_id(5)
        self.assertIsInstance(item, PropertyUpgradeItem)
    
    def test_create_item_by_id_invalid(self):
        """测试通过ID创建无效道具"""
        item = create_item_by_id(999)
        self.assertIsNone(item)


class TestItemManager(unittest.TestCase):
    """道具管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.manager = ItemManager()
    
    def test_manager_initialization(self):
        """测试管理器初始化"""
        self.assertIsNotNone(self.manager.item_class_map)
        self.assertIsNotNone(self.manager.item_name_map)
        self.assertEqual(len(self.manager.item_class_map), 5)
    
    def test_get_item_by_id(self):
        """测试通过ID获取道具"""
        item = self.manager.get_item_by_id(1)
        self.assertIsInstance(item, RoadblockItem)
        
        item = self.manager.get_item_by_id(2)
        self.assertIsInstance(item, FlyItem)
        
        item = self.manager.get_item_by_id(999)
        self.assertIsNone(item)
    
    def test_get_item_by_name(self):
        """测试通过名称获取道具"""
        item = self.manager.get_item_by_name("路障")
        self.assertIsInstance(item, RoadblockItem)
        
        item = self.manager.get_item_by_name("再装逼让你飞起来!!")
        self.assertIsInstance(item, FlyItem)
        
        item = self.manager.get_item_by_name("不存在的道具")
        self.assertIsNone(item)
    
    def test_create_items(self):
        """测试批量创建道具"""
        items = self.manager.create_items(1, 3)
        self.assertEqual(len(items), 3)
        for item in items:
            self.assertIsInstance(item, RoadblockItem)
    
    def test_list_all_items(self):
        """测试列出所有道具"""
        items = self.manager.list_all_items()
        self.assertEqual(len(items), 5)
        for item in items:
            self.assertIsInstance(item, Item)
    
    def test_get_item_price(self):
        """测试获取道具价格"""
        self.assertEqual(self.manager.get_item_price(1), 10000)  # 路障
        self.assertEqual(self.manager.get_item_price(2), 20000)  # 再装逼让你飞起来!!
        self.assertEqual(self.manager.get_item_price(3), 20000)  # 庇护术
        self.assertEqual(self.manager.get_item_price(4), 15000)  # 六百六十六
        self.assertEqual(self.manager.get_item_price(5), 25000)  # 违规爆建
        self.assertEqual(self.manager.get_item_price(999), 0)    # 无效道具
    
    def test_get_item_price_by_name(self):
        """测试通过名称获取道具价格"""
        self.assertEqual(self.manager.get_item_price_by_name("路障"), 10000)
        self.assertEqual(self.manager.get_item_price_by_name("再装逼让你飞起来!!"), 20000)
        self.assertEqual(self.manager.get_item_price_by_name("不存在的道具"), 0)


class TestPlayerInventory(unittest.TestCase):
    """玩家背包测试"""
    
    def setUp(self):
        """测试前准备"""
        self.player = Player(1, "测试玩家")
    
    def test_initial_inventory(self):
        """测试初始背包"""
        self.assertEqual(len(self.player.items), 0)
    
    def test_add_item(self):
        """测试添加道具"""
        # 添加路障
        success = self.player.add_item(1, 3)
        self.assertTrue(success)
        self.assertEqual(self.player.get_item_count(1), 3)
        
        # 添加更多路障
        success = self.player.add_item(1, 2)
        self.assertTrue(success)
        self.assertEqual(self.player.get_item_count(1), 5)
    
    def test_add_item_invalid(self):
        """测试添加无效道具"""
        success = self.player.add_item(0, 1)
        self.assertFalse(success)
        
        success = self.player.add_item(1, 0)
        self.assertFalse(success)
        
        success = self.player.add_item(1, -1)
        self.assertFalse(success)
    
    def test_remove_item(self):
        """测试移除道具"""
        # 先添加道具
        self.player.add_item(1, 5)
        
        # 移除部分道具
        success = self.player.remove_item(1, 2)
        self.assertTrue(success)
        self.assertEqual(self.player.get_item_count(1), 3)
        
        # 移除所有道具
        success = self.player.remove_item(1, 3)
        self.assertTrue(success)
        self.assertEqual(self.player.get_item_count(1), 0)
        self.assertNotIn(1, self.player.items)
    
    def test_remove_item_invalid(self):
        """测试移除无效道具"""
        # 移除不存在的道具
        success = self.player.remove_item(1, 1)
        self.assertFalse(success)
        
        # 移除数量超过拥有的
        self.player.add_item(1, 2)
        success = self.player.remove_item(1, 3)
        self.assertFalse(success)
        self.assertEqual(self.player.get_item_count(1), 2)
    
    def test_has_item(self):
        """测试检查道具"""
        self.assertFalse(self.player.has_item(1))
        
        self.player.add_item(1, 1)
        self.assertTrue(self.player.has_item(1))
        
        self.player.remove_item(1, 1)
        self.assertFalse(self.player.has_item(1))
    
    def test_use_item_success(self):
        """测试使用道具成功"""
        self.player.add_item(4, 1)  # 添加六百六十六
        
        # 模拟玩家对象
        self.player.next_dice_value = None
        
        result = self.player.use_item(4)
        self.assertTrue(result["success"])
        self.assertEqual(self.player.next_dice_value, 6)
        self.assertEqual(self.player.get_item_count(4), 0)
        self.assertEqual(self.player.items_used, 1)
    
    def test_use_item_failure(self):
        """测试使用道具失败"""
        # 使用不存在的道具
        result = self.player.use_item(1)
        self.assertFalse(result["success"])
        self.assertEqual(result["msg"], "没有该道具")
        
        # 使用无效道具ID
        result = self.player.use_item(999)
        self.assertFalse(result["success"])
        self.assertEqual(result["msg"], "没有该道具")


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2) 