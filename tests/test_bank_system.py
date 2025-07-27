#!/usr/bin/env python3
"""
银行系统单元测试
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import unittest
from src.models.player import Player
from src.models.map import Map
from src.systems.property_manager import PropertyManager
from src.systems.player_manager import PlayerManager
from src.systems.bank_system import BankSystem
from src.core.constants import INITIAL_MONEY, BANK_INTEREST


class TestBankSystem(unittest.TestCase):
    """测试BankSystem类"""
    
    def setUp(self):
        """测试前准备"""
        self.bank_system = BankSystem()
        self.player = Player(player_id=1, name="测试玩家")
        self.player.money = 100000
        self.player.bank_money = 50000
    
    def test_deposit(self):
        """测试存款"""
        # 正常存款
        result = self.bank_system.deposit(self.player, 20000)
        self.assertTrue(result["success"])
        self.assertEqual(self.player.money, 80000)
        self.assertEqual(self.player.bank_money, 70000)
        self.assertEqual(result["amount"], 20000)
        
        # 存款金额为0
        result = self.bank_system.deposit(self.player, 0)
        self.assertFalse(result["success"])
        self.assertIn("存款金额必须大于0", result["msg"])
        
        # 存款金额为负数
        result = self.bank_system.deposit(self.player, -1000)
        self.assertFalse(result["success"])
        self.assertIn("存款金额必须大于0", result["msg"])
        
        # 资金不足
        result = self.bank_system.deposit(self.player, 100000)
        self.assertFalse(result["success"])
        self.assertIn("身上资金不足", result["msg"])
    
    def test_withdraw(self):
        """测试取款"""
        # 正常取款
        result = self.bank_system.withdraw(self.player, 20000)
        self.assertTrue(result["success"])
        self.assertEqual(self.player.money, 120000)
        self.assertEqual(self.player.bank_money, 30000)
        self.assertEqual(result["amount"], 20000)
        
        # 取款金额为0
        result = self.bank_system.withdraw(self.player, 0)
        self.assertFalse(result["success"])
        self.assertIn("取款金额必须大于0", result["msg"])
        
        # 取款金额为负数
        result = self.bank_system.withdraw(self.player, -1000)
        self.assertFalse(result["success"])
        self.assertIn("取款金额必须大于0", result["msg"])
        
        # 银行资金不足
        result = self.bank_system.withdraw(self.player, 100000)
        self.assertFalse(result["success"])
        self.assertIn("银行资金不足", result["msg"])
    
    def test_interest_rate_calculation(self):
        """测试利息率计算"""
        # 资产<100,000：5%
        rate = self.bank_system.get_interest_rate(50000)
        self.assertEqual(rate, 0.05)
        
        # 资产≥100,000：10%
        rate = self.bank_system.get_interest_rate(150000)
        self.assertEqual(rate, 0.10)
        
        # 资产≥300,000：20%
        rate = self.bank_system.get_interest_rate(400000)
        self.assertEqual(rate, 0.20)
        
        # 资产≥500,000：30%
        rate = self.bank_system.get_interest_rate(600000)
        self.assertEqual(rate, 0.30)
    
    def test_interest_calculation(self):
        """测试利息计算"""
        # 没有银行资金
        self.player.bank_money = 0
        interest = self.bank_system.calculate_interest(self.player)
        self.assertEqual(interest, 0)
        
        # 有银行资金，总资产50000（5%利率）
        self.player.bank_money = 10000
        self.player.money = 40000  # 总资产50000
        interest = self.bank_system.calculate_interest(self.player)
        self.assertEqual(interest, 500)  # 10000 * 0.05
        
        # 总资产150000（10%利率）
        self.player.money = 140000  # 总资产150000
        interest = self.bank_system.calculate_interest(self.player)
        self.assertEqual(interest, 1000)  # 10000 * 0.10
    
    def test_pay_interest(self):
        """测试支付利息"""
        # 没有银行资金
        self.player.bank_money = 0
        result = self.bank_system.pay_interest(self.player)
        self.assertFalse(result["success"])
        self.assertIn("没有利息可支付", result["msg"])
        
        # 有银行资金
        self.player.bank_money = 10000
        self.player.money = 40000  # 总资产50000，5%利率
        result = self.bank_system.pay_interest(self.player)
        self.assertTrue(result["success"])
        self.assertEqual(result["interest"], 500)
        self.assertEqual(self.player.bank_money, 10500)
        self.assertEqual(result["interest_rate"], 0.05)
    
    def test_apply_for_loan(self):
        """测试申请贷款"""
        # 正常申请贷款
        result = self.bank_system.apply_for_loan(self.player, 50000)
        self.assertTrue(result["success"])
        self.assertEqual(self.player.money, 150000)
        self.assertEqual(result["amount"], 50000)
        self.assertIn("loan_info", result)
        
        # 贷款金额过小
        result = self.bank_system.apply_for_loan(self.player, 5000)
        self.assertFalse(result["success"])
        self.assertIn("贷款金额不能少于", result["msg"])
        
        # 贷款金额过大
        result = self.bank_system.apply_for_loan(self.player, 2000000)
        self.assertFalse(result["success"])
        self.assertIn("贷款金额不能超过", result["msg"])
        
        # 已有贷款
        result = self.bank_system.apply_for_loan(self.player, 30000)
        self.assertFalse(result["success"])
        self.assertIn("已有未还清的贷款", result["msg"])
    
    def test_repay_loan(self):
        """测试还款"""
        # 先申请贷款
        self.bank_system.apply_for_loan(self.player, 50000)
        
        # 正常还款
        result = self.bank_system.repay_loan(self.player, 20000)
        self.assertTrue(result["success"])
        self.assertEqual(self.player.money, 130000)
        
        # 还款金额为0
        result = self.bank_system.repay_loan(self.player, 0)
        self.assertFalse(result["success"])
        self.assertIn("还款金额必须大于0", result["msg"])
        
        # 还款金额为负数
        result = self.bank_system.repay_loan(self.player, -1000)
        self.assertFalse(result["success"])
        self.assertIn("还款金额必须大于0", result["msg"])
        
        # 资金不足
        result = self.bank_system.repay_loan(self.player, 200000)
        self.assertFalse(result["success"])
        self.assertIn("身上资金不足", result["msg"])
        
        # 没有贷款
        self.player.player_id = 999  # 使用不同的玩家ID
        result = self.bank_system.repay_loan(self.player, 10000)
        self.assertFalse(result["success"])
        self.assertIn("没有未还清的贷款", result["msg"])
    
    def test_loan_interest_calculation(self):
        """测试贷款利息计算"""
        # 申请贷款
        self.bank_system.apply_for_loan(self.player, 50000)
        
        # 初始利息为0
        interest = self.bank_system.calculate_loan_interest(self.player.player_id)
        self.assertEqual(interest, 0)
        
        # 更新回合数
        self.bank_system.update_loan_turns(self.player)
        interest = self.bank_system.calculate_loan_interest(self.player.player_id)
        self.assertEqual(interest, 7500)  # 50000 * 0.15 * 1
        
        # 再更新回合数
        self.bank_system.update_loan_turns(self.player)
        interest = self.bank_system.calculate_loan_interest(self.player.player_id)
        self.assertEqual(interest, 15000)  # 50000 * 0.15 * 2
    
    def test_loan_info(self):
        """测试贷款信息"""
        # 没有贷款
        info = self.bank_system.get_loan_info(self.player)
        self.assertFalse(info["has_loan"])
        
        # 申请贷款
        self.bank_system.apply_for_loan(self.player, 50000)
        info = self.bank_system.get_loan_info(self.player)
        self.assertTrue(info["has_loan"])
        self.assertEqual(info["loan_amount"], 50000)
        self.assertEqual(info["interest"], 0)
        self.assertEqual(info["turns"], 0)
        self.assertEqual(info["interest_rate"], 0.15)
    
    def test_loan_overdue(self):
        """测试贷款逾期"""
        # 申请贷款
        self.bank_system.apply_for_loan(self.player, 50000)
        
        # 初始未逾期
        self.assertFalse(self.bank_system.check_loan_overdue(self.player))
        
        # 更新11个回合（超过10回合）
        for _ in range(11):
            self.bank_system.update_loan_turns(self.player)
        
        # 检查逾期
        self.assertTrue(self.bank_system.check_loan_overdue(self.player))
    
    def test_force_repay_overdue_loan(self):
        """测试强制还款逾期贷款"""
        # 申请贷款并逾期
        self.bank_system.apply_for_loan(self.player, 50000)
        for _ in range(11):
            self.bank_system.update_loan_turns(self.player)
        
        # 资金充足，强制还款
        result = self.bank_system.force_repay_overdue_loan(self.player)
        self.assertTrue(result["success"])
        self.assertIn("强制还款成功", result["msg"])
        
        # 检查贷款已清除
        self.assertFalse(self.bank_system.check_loan_overdue(self.player))
        info = self.bank_system.get_loan_info(self.player)
        self.assertFalse(info["has_loan"])
    
    def test_interest_cycle(self):
        """测试利息周期"""
        # 重置银行系统以确保初始状态
        self.bank_system.reset_bank()
        
        # 初始状态
        self.assertFalse(self.bank_system.should_pay_interest())
        
        # 推进1个周期
        self.bank_system.advance_interest_cycle()
        self.assertFalse(self.bank_system.should_pay_interest())
        
        # 推进2个周期
        self.bank_system.advance_interest_cycle()
        self.assertFalse(self.bank_system.should_pay_interest())
        
        # 推进3个周期
        self.bank_system.advance_interest_cycle()
        self.assertTrue(self.bank_system.should_pay_interest())
    
    def test_bank_status(self):
        """测试银行状态"""
        status = self.bank_system.get_bank_status()
        self.assertIn("bank_pool", status)
        self.assertIn("total_loans", status)
        self.assertIn("active_loans", status)
        self.assertIn("current_cycle", status)
        self.assertIn("interest_cycle", status)
        self.assertIn("loan_interest_rate", status)
        self.assertIn("max_loan_amount", status)
        self.assertIn("min_loan_amount", status)
        
        # 初始状态
        self.assertEqual(status["total_loans"], 0)
        self.assertEqual(status["active_loans"], 0)
        self.assertEqual(status["current_cycle"], 0)
    
    def test_reset_bank(self):
        """测试重置银行"""
        # 申请贷款
        self.bank_system.apply_for_loan(self.player, 50000)
        self.bank_system.advance_interest_cycle()
        
        # 重置银行
        self.bank_system.reset_bank()
        
        # 检查重置结果
        status = self.bank_system.get_bank_status()
        self.assertEqual(status["total_loans"], 0)
        self.assertEqual(status["active_loans"], 0)
        self.assertEqual(status["current_cycle"], 0)
        
        # 检查贷款已清除
        info = self.bank_system.get_loan_info(self.player)
        self.assertFalse(info["has_loan"])


class TestPlayerManagerBankIntegration(unittest.TestCase):
    """测试PlayerManager中的银行集成"""
    
    def setUp(self):
        """测试前准备"""
        self.game_map = Map(5, 5)
        self.property_manager = PropertyManager(self.game_map)
        self.player_manager = PlayerManager(self.game_map, self.property_manager)
        self.player = self.player_manager.add_player("测试玩家")
        self.player.money = 100000
        self.player.bank_money = 50000
    
    def test_bank_deposit(self):
        """测试银行存款"""
        result = self.player_manager.bank_deposit(self.player, 20000)
        self.assertTrue(result["success"])
        self.assertEqual(self.player.money, 80000)
        self.assertEqual(self.player.bank_money, 70000)
    
    def test_bank_withdraw(self):
        """测试银行取款"""
        result = self.player_manager.bank_withdraw(self.player, 20000)
        self.assertTrue(result["success"])
        self.assertEqual(self.player.money, 120000)
        self.assertEqual(self.player.bank_money, 30000)
    
    def test_bank_apply_loan(self):
        """测试申请贷款"""
        result = self.player_manager.bank_apply_loan(self.player, 50000)
        self.assertTrue(result["success"])
        self.assertEqual(self.player.money, 150000)
    
    def test_bank_repay_loan(self):
        """测试还款"""
        # 先申请贷款
        self.player_manager.bank_apply_loan(self.player, 50000)
        
        # 还款
        result = self.player_manager.bank_repay_loan(self.player, 20000)
        self.assertTrue(result["success"])
        self.assertEqual(self.player.money, 130000)
    
    def test_bank_get_loan_info(self):
        """测试获取贷款信息"""
        # 没有贷款
        info = self.player_manager.bank_get_loan_info(self.player)
        self.assertFalse(info["has_loan"])
        
        # 申请贷款
        self.player_manager.bank_apply_loan(self.player, 50000)
        info = self.player_manager.bank_get_loan_info(self.player)
        self.assertTrue(info["has_loan"])
        self.assertEqual(info["loan_amount"], 50000)
    
    def test_bank_pay_interest(self):
        """测试支付利息"""
        self.player.bank_money = 10000
        result = self.player_manager.bank_pay_interest(self.player)
        self.assertTrue(result["success"])
        self.assertGreater(self.player.bank_money, 10000)
    
    def test_bank_get_status(self):
        """测试获取银行状态"""
        status = self.player_manager.bank_get_status()
        self.assertIn("bank_pool", status)
        self.assertIn("total_loans", status)
        self.assertIn("active_loans", status)
    
    def test_next_turn_with_interest(self):
        """测试回合推进时的利息计算"""
        # 设置银行资金
        self.player.bank_money = 10000
        
        # 推进3个回合（应该支付利息）
        for _ in range(3):
            self.player_manager.next_turn()
        
        # 检查是否支付了利息
        self.assertGreater(self.player.bank_money, 10000)
    
    def test_next_turn_with_loan(self):
        """测试回合推进时的贷款管理"""
        # 申请贷款
        self.player_manager.bank_apply_loan(self.player, 50000)
        
        # 推进11个回合（贷款逾期）
        for _ in range(11):
            self.player_manager.next_turn()
        
        # 检查贷款是否被强制还款
        info = self.player_manager.bank_get_loan_info(self.player)
        self.assertFalse(info["has_loan"])


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2) 