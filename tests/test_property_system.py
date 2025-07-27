#!/usr/bin/env python3
"""
房产系统单元测试
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import unittest
from src.models.property import Property
from src.models.player import Player
from src.models.map import Map
from src.systems.property_manager import PropertyManager
from src.core.constants import PROPERTY_LEVELS


class TestProperty(unittest.TestCase):
    """测试Property类"""
    
    def setUp(self):
        """测试前准备"""
        self.property = Property(position=100, owner_id=1, level=2)
    
    def test_property_initialization(self):
        """测试房产初始化"""
        self.assertEqual(self.property.position, 100)
        self.assertEqual(self.property.owner_id, 1)
        self.assertEqual(self.property.level, 2)
        self.assertEqual(self.property.value, PROPERTY_LEVELS[1]["cost"] + PROPERTY_LEVELS[2]["cost"])
    
    def test_empty_property(self):
        """测试空地房产"""
        empty_property = Property(position=200, level=0)
        self.assertEqual(empty_property.level, 0)
        self.assertEqual(empty_property.value, 0)
        self.assertEqual(empty_property.get_rent(), 0)
        self.assertTrue(empty_property.is_empty())
        self.assertFalse(empty_property.is_owned())
    
    def test_property_rent_calculation(self):
        """测试租金计算"""
        # 测试不同等级的租金
        for level in range(1, 5):
            prop = Property(position=level, level=level)
            expected_rent = PROPERTY_LEVELS[level]["rent"]
            self.assertEqual(prop.get_rent(), expected_rent)
    
    def test_property_upgrade_cost(self):
        """测试升级费用计算"""
        # 测试不同等级的升级费用
        for level in range(1, 4):
            prop = Property(position=level, level=level)
            expected_cost = PROPERTY_LEVELS[level + 1]["cost"]
            self.assertEqual(prop.get_upgrade_cost(), expected_cost)
        
        # 测试四级房产无法升级
        max_prop = Property(position=4, level=4)
        self.assertEqual(max_prop.get_upgrade_cost(), 0)
        self.assertFalse(max_prop.can_upgrade())
    
    def test_property_upgrade(self):
        """测试房产升级"""
        prop = Property(position=1, level=1)
        initial_value = prop.value
        
        # 测试正常升级
        self.assertTrue(prop.can_upgrade())
        self.assertTrue(prop.upgrade())
        self.assertEqual(prop.level, 2)
        self.assertGreater(prop.value, initial_value)
        
        # 测试升级到最高级
        prop.upgrade()  # 到3级
        prop.upgrade()  # 到4级
        self.assertFalse(prop.can_upgrade())
        self.assertFalse(prop.upgrade())
    
    def test_property_downgrade(self):
        """测试房产降级"""
        prop = Property(position=1, level=3)
        initial_value = prop.value
        
        # 测试正常降级
        self.assertTrue(prop.downgrade())
        self.assertEqual(prop.level, 2)
        self.assertLess(prop.value, initial_value)
        
        # 测试降级为空地
        prop.downgrade()  # 到1级
        prop.downgrade()  # 到0级
        self.assertTrue(prop.is_empty())
        self.assertFalse(prop.downgrade())
    
    def test_property_ownership(self):
        """测试房产所有权"""
        prop = Property(position=1, level=1)
        
        # 测试设置所有者
        prop.set_owner(5)
        self.assertEqual(prop.owner_id, 5)
        self.assertTrue(prop.is_owned())
        
        # 测试移除所有者
        prop.remove_owner()
        self.assertIsNone(prop.owner_id)
        self.assertFalse(prop.is_owned())
    
    def test_property_serialization(self):
        """测试房产序列化"""
        prop = Property(position=100, owner_id=1, level=3)
        
        # 测试转换为字典
        data = prop.to_dict()
        self.assertEqual(data["position"], 100)
        self.assertEqual(data["owner_id"], 1)
        self.assertEqual(data["level"], 3)
        self.assertEqual(data["value"], prop.value)
        
        # 测试从字典创建
        new_prop = Property.from_dict(data)
        self.assertEqual(new_prop.position, prop.position)
        self.assertEqual(new_prop.owner_id, prop.owner_id)
        self.assertEqual(new_prop.level, prop.level)
        self.assertEqual(new_prop.value, prop.value)


class TestPropertyManager(unittest.TestCase):
    """测试PropertyManager类"""
    
    def setUp(self):
        """测试前准备"""
        self.game_map = Map(5, 5)
        self.property_manager = PropertyManager(self.game_map)
        self.player1 = Player(player_id=1, name="玩家1")
        self.player2 = Player(player_id=2, name="玩家2")
        
        # 设置一些测试房产
        self.setup_test_properties()
    
    def setup_test_properties(self):
        """设置测试房产"""
        # 在坐标(1,1)设置空地
        cell = self.game_map.get_cell_at((1, 1))
        if cell:
            cell.cell_type = "empty"
            property_obj = Property(position=1 * 5 + 1, level=0)
            cell.set_property(property_obj)
        
        # 在坐标(2,2)设置有主房产
        cell = self.game_map.get_cell_at((2, 2))
        if cell:
            cell.cell_type = "empty"
            property_obj = Property(position=2 * 5 + 2, owner_id=1, level=2)
            cell.set_property(property_obj)
        
        # 重新初始化房产管理器
        self.property_manager._initialize_properties()
    
    def test_property_manager_initialization(self):
        """测试房产管理器初始化"""
        self.assertEqual(len(self.property_manager.properties), 2)
        self.assertIsNotNone(self.property_manager.get_property_at_position(6))  # (1,1)
        self.assertIsNotNone(self.property_manager.get_property_at_position(12))  # (2,2)
    
    def test_get_property_at_coordinates(self):
        """测试通过坐标获取房产"""
        prop = self.property_manager.get_property_at_coordinates(1, 1)
        self.assertIsNotNone(prop)
        self.assertEqual(prop.position, 6)
        
        prop = self.property_manager.get_property_at_coordinates(2, 2)
        self.assertIsNotNone(prop)
        self.assertEqual(prop.level, 2)
        self.assertEqual(prop.owner_id, 1)
    
    def test_get_properties_by_owner(self):
        """测试获取指定玩家的房产"""
        player1_properties = self.property_manager.get_properties_by_owner(1)
        self.assertEqual(len(player1_properties), 1)
        self.assertEqual(player1_properties[0].position, 12)
        
        player2_properties = self.property_manager.get_properties_by_owner(2)
        self.assertEqual(len(player2_properties), 0)
    
    def test_buy_property_success(self):
        """测试成功购买房产"""
        # 设置玩家资金
        self.player1.money = 50000
        
        # 购买空地
        result = self.property_manager.buy_property(self.player1, 6)  # (1,1)
        
        self.assertTrue(result["success"])
        self.assertIn("成功购买房产", result["msg"])
        self.assertEqual(result["cost"], PROPERTY_LEVELS[1]["cost"])
        
        # 检查房产状态
        prop = self.property_manager.get_property_at_position(6)
        self.assertEqual(prop.owner_id, 1)
        self.assertEqual(prop.level, 1)
        
        # 检查玩家状态
        self.assertIn(prop, self.player1.properties)
        self.assertEqual(self.player1.money, 50000 - PROPERTY_LEVELS[1]["cost"])
    
    def test_buy_property_failures(self):
        """测试购买房产的各种失败情况"""
        # 测试购买不存在的房产
        result = self.property_manager.buy_property(self.player1, 999)
        self.assertFalse(result["success"])
        self.assertIn("没有房产", result["msg"])
        
        # 测试购买已有所有者的房产
        result = self.property_manager.buy_property(self.player1, 12)  # (2,2)
        self.assertFalse(result["success"])
        self.assertIn("已有所有者", result["msg"])
        
        # 测试资金不足
        self.player1.money = 5000  # 少于购买费用
        result = self.property_manager.buy_property(self.player1, 6)
        self.assertFalse(result["success"])
        self.assertIn("资金不足", result["msg"])
    
    def test_upgrade_property_success(self):
        """测试成功升级房产"""
        # 设置玩家资金
        self.player1.money = 50000
        
        # 升级房产
        result = self.property_manager.upgrade_property(self.player1, 12)  # (2,2)
        
        self.assertTrue(result["success"])
        self.assertIn("成功升级房产", result["msg"])
        
        # 检查房产状态
        prop = self.property_manager.get_property_at_position(12)
        self.assertEqual(prop.level, 3)
    
    def test_upgrade_property_failures(self):
        """测试升级房产的各种失败情况"""
        # 测试升级不存在的房产
        result = self.property_manager.upgrade_property(self.player1, 999)
        self.assertFalse(result["success"])
        
        # 测试升级非自己的房产
        result = self.property_manager.upgrade_property(self.player2, 12)
        self.assertFalse(result["success"])
        self.assertIn("不是该房产的所有者", result["msg"])
        
        # 测试升级已满级的房产
        prop = self.property_manager.get_property_at_position(12)
        prop.level = 4
        result = self.property_manager.upgrade_property(self.player1, 12)
        self.assertFalse(result["success"])
        self.assertIn("已达到最高等级", result["msg"])
    
    def test_pay_rent(self):
        """测试支付租金"""
        # 设置支付者资金
        self.player2.money = 20000
        
        # 支付租金
        result = self.property_manager.pay_rent(self.player2, 12)  # (2,2)
        
        self.assertTrue(result["success"])
        self.assertIn("支付租金", result["msg"])
        
        # 检查支付者资金减少
        expected_rent = PROPERTY_LEVELS[2]["rent"]
        self.assertEqual(self.player2.money, 20000 - expected_rent)
    
    def test_pay_rent_failures(self):
        """测试支付租金的各种失败情况"""
        # 测试支付不存在的房产租金
        result = self.property_manager.pay_rent(self.player2, 999)
        self.assertFalse(result["success"])
        
        # 测试支付无主房产租金
        prop = self.property_manager.get_property_at_position(6)
        prop.remove_owner()
        result = self.property_manager.pay_rent(self.player2, 6)
        self.assertFalse(result["success"])
        self.assertIn("无主", result["msg"])
        
        # 测试向自己支付租金
        result = self.property_manager.pay_rent(self.player1, 12)
        self.assertFalse(result["success"])
        self.assertIn("无需向自己支付", result["msg"])
    
    def test_transfer_property(self):
        """测试转移房产"""
        # 转移房产
        result = self.property_manager.transfer_property(self.player1, self.player2, 12)
        
        self.assertTrue(result["success"])
        self.assertIn("成功转移房产", result["msg"])
        
        # 检查房产所有者变更
        prop = self.property_manager.get_property_at_position(12)
        self.assertEqual(prop.owner_id, 2)
        
        # 检查玩家房产列表更新
        self.assertNotIn(prop, self.player1.properties)
        self.assertIn(prop, self.player2.properties)
    
    def test_demolish_property(self):
        """测试拆除房产"""
        # 拆除房产
        result = self.property_manager.demolish_property(self.player1, 12)
        
        self.assertTrue(result["success"])
        self.assertIn("成功拆除", result["msg"])
        
        # 检查房产状态
        prop = self.property_manager.get_property_at_position(12)
        self.assertEqual(prop.level, 0)
        self.assertIsNone(prop.owner_id)
        
        # 检查从玩家房产列表移除
        self.assertNotIn(prop, self.player1.properties)
    
    def test_force_upgrade_downgrade(self):
        """测试强制升级和降级"""
        # 强制升级
        result = self.property_manager.force_upgrade_property(12)
        self.assertTrue(result["success"])
        
        prop = self.property_manager.get_property_at_position(12)
        self.assertEqual(prop.level, 3)
        
        # 强制降级
        result = self.property_manager.force_downgrade_property(12)
        self.assertTrue(result["success"])
        
        prop = self.property_manager.get_property_at_position(12)
        self.assertEqual(prop.level, 2)
    
    def test_property_statistics(self):
        """测试房产统计"""
        stats = self.property_manager.get_property_statistics()
        
        self.assertEqual(stats["total_properties"], 2)
        self.assertEqual(stats["owned_properties"], 1)
        self.assertEqual(stats["empty_properties"], 1)
        self.assertEqual(stats["level_statistics"][0], 1)  # 空地
        self.assertEqual(stats["level_statistics"][2], 1)  # 2级房产
        self.assertEqual(stats["owner_statistics"][1], 1)  # 玩家1有1个房产


class TestPlayerPropertyMethods(unittest.TestCase):
    """测试Player类的房产相关方法"""
    
    def setUp(self):
        """测试前准备"""
        self.player = Player(player_id=1, name="测试玩家")
        self.property1 = Property(position=100, owner_id=1, level=2)
        self.property2 = Property(position=200, owner_id=1, level=3)
    
    def test_add_property(self):
        """测试添加房产"""
        self.assertEqual(len(self.player.properties), 0)
        
        self.player.add_property(self.property1)
        self.assertEqual(len(self.player.properties), 1)
        self.assertIn(self.property1, self.player.properties)
        
        self.player.add_property(self.property2)
        self.assertEqual(len(self.player.properties), 2)
    
    def test_remove_property(self):
        """测试移除房产"""
        self.player.add_property(self.property1)
        self.player.add_property(self.property2)
        
        self.player.remove_property(self.property1)
        self.assertEqual(len(self.player.properties), 1)
        self.assertNotIn(self.property1, self.player.properties)
        self.assertIn(self.property2, self.player.properties)
    
    def test_get_property_at_position(self):
        """测试获取指定位置的房产"""
        self.player.add_property(self.property1)
        self.player.add_property(self.property2)
        
        prop = self.player.get_property_at_position(100)
        self.assertEqual(prop, self.property1)
        
        prop = self.player.get_property_at_position(200)
        self.assertEqual(prop, self.property2)
        
        prop = self.player.get_property_at_position(999)
        self.assertIsNone(prop)
    
    def test_get_total_assets(self):
        """测试总资产计算"""
        self.player.money = 50000
        self.player.bank_money = 30000
        
        self.player.add_property(self.property1)
        self.player.add_property(self.property2)
        
        total_assets = self.player.get_total_assets()
        expected_assets = 50000 + 30000 + self.property1.value + self.property2.value
        self.assertEqual(total_assets, expected_assets)


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2) 