"""
地图系统测试
"""
import unittest
import sys
import os
import tempfile
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.map import Map, Cell
from src.systems.map_data_manager import MapDataManager
from src.utils.map_editor import MapEditor


class TestMapDataManager(unittest.TestCase):
    """地图数据管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.map_data_manager = MapDataManager()
        self.test_map = Map(10, 10)
    
    def test_supported_formats(self):
        """测试支持的格式"""
        formats = self.map_data_manager.get_supported_formats()
        self.assertIn('json', formats)
        self.assertIn('db', formats)
    
    def test_save_and_load_json(self):
        """测试JSON格式保存和加载"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            # 保存地图
            success = self.map_data_manager.save_map(self.test_map, 'json', temp_file)
            self.assertTrue(success)
            
            # 加载地图
            loaded_map = self.map_data_manager.load_map('json', temp_file)
            self.assertIsNotNone(loaded_map)
            self.assertEqual(loaded_map.width, self.test_map.width)
            self.assertEqual(loaded_map.height, self.test_map.height)
            self.assertEqual(loaded_map.path_length, self.test_map.path_length)
        
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_save_and_load_database(self):
        """测试数据库格式保存和加载"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            temp_file = f.name
        
        try:
            # 保存地图
            success = self.map_data_manager.save_map(self.test_map, 'db', temp_file)
            self.assertTrue(success)
            
            # 加载地图
            loaded_map = self.map_data_manager.load_map('db', temp_file)
            self.assertIsNotNone(loaded_map)
            self.assertEqual(loaded_map.width, self.test_map.width)
            self.assertEqual(loaded_map.height, self.test_map.height)
        
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_map_validation(self):
        """测试地图验证"""
        # 测试正常地图
        result = self.map_data_manager.validate_map(self.test_map)
        self.assertEqual(len(result["errors"]), 0)
        
        # 测试小地图
        small_map = Map(3, 3)
        result = self.map_data_manager.validate_map(small_map)
        self.assertGreater(len(result["errors"]), 0)
        
        # 测试大地图
        large_map = Map(60, 60)
        result = self.map_data_manager.validate_map(large_map)
        self.assertGreater(len(result["warnings"]), 0)


class TestMapEditor(unittest.TestCase):
    """地图编辑器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.editor = MapEditor()
    
    def test_create_new_map(self):
        """测试创建新地图"""
        map_obj = self.editor.create_new_map(15, 15)
        self.assertIsNotNone(map_obj)
        self.assertEqual(map_obj.width, 15)
        self.assertEqual(map_obj.height, 15)
        self.assertEqual(self.editor.current_map, map_obj)
    
    def test_set_cell_type(self):
        """测试设置格子类型"""
        self.editor.create_new_map(10, 10)
        
        # 测试设置银行
        success = self.editor.set_cell_type(5, 5, "bank")
        self.assertTrue(success)
        
        cell = self.editor.current_map.get_cell_at((5, 5))
        self.assertEqual(cell.cell_type, "bank")
        
        # 测试无效类型
        success = self.editor.set_cell_type(5, 5, "invalid_type")
        self.assertFalse(success)
    
    def test_toggle_roadblock(self):
        """测试切换路障"""
        self.editor.create_new_map(10, 10)
        
        # 测试放置路障
        success = self.editor.toggle_roadblock(5, 5)
        self.assertTrue(success)
        
        cell = self.editor.current_map.get_cell_at((5, 5))
        self.assertTrue(cell.roadblock)
        
        # 测试移除路障
        success = self.editor.toggle_roadblock(5, 5)
        self.assertTrue(success)
        
        cell = self.editor.current_map.get_cell_at((5, 5))
        self.assertFalse(cell.roadblock)
    
    def test_set_property(self):
        """测试设置房产"""
        self.editor.create_new_map(10, 10)
        
        # 测试设置房产
        success = self.editor.set_property(5, 5, 2, 1)
        self.assertTrue(success)
        
        cell = self.editor.current_map.get_cell_at((5, 5))
        self.assertIsNotNone(cell.property)
        self.assertEqual(cell.property.level, 2)
        self.assertEqual(cell.property.owner_id, 1)
        
        # 测试无效等级
        success = self.editor.set_property(5, 5, 5, 1)
        self.assertFalse(success)
    
    def test_save_and_load_map(self):
        """测试保存和加载地图"""
        self.editor.create_new_map(10, 10)
        self.editor.set_cell_type(5, 5, "bank")
        self.editor.toggle_roadblock(5, 5)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            # 保存地图
            success = self.editor.save_map(temp_file)
            self.assertTrue(success)
            
            # 创建新编辑器加载地图
            new_editor = MapEditor()
            success = new_editor.load_map(temp_file)
            self.assertTrue(success)
            
            # 验证加载的地图
            cell = new_editor.current_map.get_cell_at((5, 5))
            self.assertEqual(cell.cell_type, "bank")
            self.assertTrue(cell.roadblock)
        
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestMapAdvancedFeatures(unittest.TestCase):
    """地图高级功能测试"""
    
    def setUp(self):
        """测试前准备"""
        self.map_obj = Map(15, 15)
    
    def test_path_operations(self):
        """测试路径操作"""
        # 测试路径索引
        path_index = self.map_obj.get_path_index((0, 0))
        self.assertGreaterEqual(path_index, 0)
        
        # 测试根据路径索引获取位置
        position = self.map_obj.get_position_by_path_index(0)
        self.assertIsNotNone(position)
        
        # 测试根据路径索引获取格子
        cell = self.map_obj.get_cell_by_path_index(0)
        self.assertIsNotNone(cell)
    
    def test_distance_calculation(self):
        """测试距离计算"""
        distance = self.map_obj.calculate_distance((0, 0), (3, 4))
        self.assertEqual(distance, 7)  # 3 + 4 = 7
        
        distance = self.map_obj.calculate_distance((1, 1), (1, 1))
        self.assertEqual(distance, 0)
    
    def test_cells_in_range(self):
        """测试范围内格子获取"""
        cells = self.map_obj.get_cells_in_range((5, 5), 2)
        self.assertGreater(len(cells), 0)
        
        # 检查是否都在范围内
        for cell in cells:
            distance = self.map_obj.calculate_distance((5, 5), cell.position)
            self.assertLessEqual(distance, 2)
    
    def test_money_on_ground(self):
        """测试地上金钱功能"""
        cell = self.map_obj.get_cell_at((5, 5))
        
        # 测试添加金钱
        cell.add_money_on_ground(1000)
        self.assertEqual(cell.money_on_ground, 1000)
        
        # 测试收集金钱
        money = cell.collect_money_on_ground()
        self.assertEqual(money, 1000)
        self.assertEqual(cell.money_on_ground, 0)
    
    def test_cell_serialization(self):
        """测试格子序列化"""
        cell = self.map_obj.get_cell_at((5, 5))
        cell.cell_type = "bank"
        cell.roadblock = True
        cell.add_money_on_ground(1000)
        
        # 测试转换为字典
        cell_dict = cell.to_dict()
        self.assertEqual(cell_dict["cell_type"], "bank")
        self.assertEqual(cell_dict["roadblock"], True)
        self.assertEqual(cell_dict["money_on_ground"], 1000)
        
        # 测试从字典创建
        new_cell = Cell.from_dict(cell_dict)
        self.assertEqual(new_cell.cell_type, "bank")
        self.assertEqual(new_cell.roadblock, True)
        self.assertEqual(new_cell.money_on_ground, 1000)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2) 