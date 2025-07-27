#!/usr/bin/env python3
"""
事件系统单元测试
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import unittest
from src.models.player import Player
from src.models.map import Map
from src.systems.property_manager import PropertyManager
from src.systems.player_manager import PlayerManager
from src.systems.event_system import EventManager

class TestEventManager(unittest.TestCase):
    def setUp(self):
        self.map_size = 20
        self.event_manager = EventManager(self.map_size)
        self.player = Player(player_id=1, name="测试玩家")

    def test_luck_event(self):
        result = self.event_manager.trigger_luck_event(self.player)
        self.assertTrue(result["success"])
        self.assertIn("msg", result)

    def test_bad_luck_event(self):
        result = self.event_manager.trigger_bad_luck_event(self.player)
        self.assertIn("msg", result)

    def test_event_history(self):
        self.event_manager.trigger_luck_event(self.player)
        self.event_manager.trigger_bad_luck_event(self.player)
        history = self.event_manager.get_history()
        self.assertEqual(len(history), 2)
        self.assertIn("event", history[0])

class TestPlayerManagerEventIntegration(unittest.TestCase):
    def setUp(self):
        self.game_map = Map(5, 5)
        self.property_manager = PropertyManager(self.game_map)
        self.player_manager = PlayerManager(self.game_map, self.property_manager)
        self.player = self.player_manager.add_player("测试玩家")

    def test_luck_cell_triggers_event(self):
        # 构造一个好运格
        cell = self.game_map.get_cell_at((1, 1))
        cell.cell_type = "luck"
        # 玩家移动到该格
        result = self.player_manager._handle_cell_effect(self.player, cell)
        self.assertEqual(result["type"], "luck")
        self.assertIn("event", result)
        self.assertTrue(result["event"]["success"])

    def test_bad_luck_cell_triggers_event(self):
        # 构造一个厄运格
        cell = self.game_map.get_cell_at((2, 2))
        cell.cell_type = "bad_luck"
        # 玩家移动到该格
        result = self.player_manager._handle_cell_effect(self.player, cell)
        self.assertEqual(result["type"], "bad_luck")
        self.assertIn("event", result)
        self.assertIn("msg", result["event"])

if __name__ == "__main__":
    unittest.main(verbosity=2) 