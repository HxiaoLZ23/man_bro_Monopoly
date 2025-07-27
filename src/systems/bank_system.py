"""
银行系统
"""
from typing import Dict, List, Optional
from src.models.player import Player
from src.core.constants import BANK_INTEREST, INITIAL_BANK_MONEY


class BankSystem:
    """银行系统"""
    
    def __init__(self):
        """
        初始化银行系统
        """
        self.interest_rates = BANK_INTEREST
        self.interest_cycle = 3  # 每3轮计算一次利息
        self.current_cycle = 0   # 当前轮数（从0开始）
        self.loan_interest_rate = 0.15  # 贷款年利率15%
        self.max_loan_amount = 1000000  # 最大贷款额度
        self.min_loan_amount = 10000    # 最小贷款额度
        
        # 贷款记录：{player_id: {"amount": int, "turns": int, "interest_paid": int}}
        self.loans = {}
        
        # 银行资金池（用于贷款）
        self.bank_pool = INITIAL_BANK_MONEY * 10  # 银行资金池
    
    def deposit(self, player: Player, amount: int) -> Dict[str, any]:
        """
        存款
        
        Args:
            player: 玩家
            amount: 存款金额
            
        Returns:
            Dict: 存款结果
        """
        if amount <= 0:
            return {"success": False, "msg": "存款金额必须大于0"}
        
        if player.money < amount:
            return {"success": False, "msg": "身上资金不足"}
        
        # 执行存款
        if player.remove_money(amount) and player.add_bank_money(amount):
            return {
                "success": True,
                "msg": f"存款成功，金额：{amount}",
                "amount": amount,
                "new_money": player.money,
                "new_bank_money": player.bank_money
            }
        else:
            return {"success": False, "msg": "存款操作失败"}
    
    def withdraw(self, player: Player, amount: int) -> Dict[str, any]:
        """
        取款
        
        Args:
            player: 玩家
            amount: 取款金额
            
        Returns:
            Dict: 取款结果
        """
        if amount <= 0:
            return {"success": False, "msg": "取款金额必须大于0"}
        
        if player.bank_money < amount:
            return {"success": False, "msg": "银行资金不足"}
        
        # 执行取款
        if player.remove_bank_money(amount) and player.add_money(amount):
            return {
                "success": True,
                "msg": f"取款成功，金额：{amount}",
                "amount": amount,
                "new_money": player.money,
                "new_bank_money": player.bank_money
            }
        else:
            return {"success": False, "msg": "取款操作失败"}
    
    def get_interest_rate(self, total_assets: int) -> float:
        """
        根据总资产获取利息率
        
        Args:
            total_assets: 总资产
            
        Returns:
            float: 利息率
        """
        for threshold, rate in sorted(self.interest_rates.items()):
            if total_assets < threshold:
                return rate
        return 0.30  # 默认最高利率
    
    def calculate_interest(self, player: Player) -> int:
        """
        计算玩家应得的利息
        
        Args:
            player: 玩家
            
        Returns:
            int: 利息金额
        """
        if player.bank_money <= 0:
            return 0
        
        total_assets = player.get_total_assets()
        interest_rate = self.get_interest_rate(total_assets)
        interest = int(player.bank_money * interest_rate)
        
        return interest
    
    def pay_interest(self, player: Player) -> Dict[str, any]:
        """
        支付利息
        
        Args:
            player: 玩家
            
        Returns:
            Dict: 利息结果
        """
        if not self.should_pay_interest():
            return {"success": False, "msg": "不是利息支付周期"}
        
        total_assets = player.get_total_assets()
        interest_rate = self.get_interest_rate(total_assets)
        interest_amount = int(player.bank_money * interest_rate)
        
        # d20神力效果
        d20_power = player.status.get("d20_power")
        if d20_power == "max":
            # 利息翻倍
            interest_amount *= 2
            player.add_bank_money(interest_amount)
            return {
                "success": True,
                "msg": f"d20神力加持！获得利息{interest_amount:,}元（翻倍）",
                "interest": interest_amount,
                "rate": interest_rate
            }
        elif d20_power == "min":
            # 收益清零
            return {
                "success": True,
                "msg": "d20神力诅咒，利息收益清零！",
                "interest": 0,
                "rate": interest_rate
            }
        else:
            # 正常利息
            player.add_bank_money(interest_amount)
            return {
                "success": True,
                "msg": f"获得利息{interest_amount:,}元",
                "interest": interest_amount,
                "rate": interest_rate
            }
    
    def apply_for_loan(self, player: Player, amount: int) -> Dict[str, any]:
        """
        申请贷款
        
        Args:
            player: 玩家
            amount: 贷款金额
            
        Returns:
            Dict: 贷款申请结果
        """
        if amount < self.min_loan_amount:
            return {"success": False, "msg": f"贷款金额不能少于{self.min_loan_amount}"}
        
        if amount > self.max_loan_amount:
            return {"success": False, "msg": f"贷款金额不能超过{self.max_loan_amount}"}
        
        if player.player_id in self.loans:
            return {"success": False, "msg": "已有未还清的贷款"}
        
        if self.bank_pool < amount:
            return {"success": False, "msg": "银行资金不足，无法提供贷款"}
        
        # 批准贷款
        self.loans[player.player_id] = {
            "amount": amount,
            "turns": 0,
            "interest_paid": 0
        }
        
        # 将贷款金额给玩家
        player.add_money(amount)
        
        # 从银行资金池扣除
        self.bank_pool -= amount
        
        return {
            "success": True,
            "msg": f"贷款申请成功，金额：{amount}",
            "amount": amount,
            "new_money": player.money,
            "loan_info": self.loans[player.player_id]
        }
    
    def repay_loan(self, player: Player, amount: int) -> Dict[str, any]:
        """
        还款
        
        Args:
            player: 玩家
            amount: 还款金额
            
        Returns:
            Dict: 还款结果
        """
        if player.player_id not in self.loans:
            return {"success": False, "msg": "没有未还清的贷款"}
        
        loan = self.loans[player.player_id]
        if amount <= 0:
            return {"success": False, "msg": "还款金额必须大于0"}
        
        if player.money < amount:
            return {"success": False, "msg": "身上资金不足"}
        
        # 计算利息
        interest = self.calculate_loan_interest(player.player_id)
        total_owed = loan["amount"] + interest
        
        # 如果还款金额超过应还总额，只还应还的部分
        if amount > total_owed:
            amount = total_owed
        
        # 执行还款
        player.remove_money(amount)
        
        # 更新贷款记录
        if amount <= interest:
            # 只还利息
            loan["interest_paid"] += amount
        else:
            # 还本金和利息
            remaining_interest = interest - loan["interest_paid"]
            if amount > remaining_interest:
                principal_paid = amount - remaining_interest
                loan["amount"] -= principal_paid
                loan["interest_paid"] = interest
            else:
                loan["interest_paid"] += amount
        
        # 如果贷款还清，删除贷款记录
        if loan["amount"] <= 0 and loan["interest_paid"] >= interest:
            del self.loans[player.player_id]
            msg = "贷款已全部还清"
        else:
            msg = f"还款成功，金额：{amount}"
        
        # 将还款金额加入银行资金池
        self.bank_pool += amount
        
        return {
            "success": True,
            "msg": msg,
            "amount": amount,
            "new_money": player.money,
            "loan_info": self.loans.get(player.player_id, None)
        }
    
    def calculate_loan_interest(self, player_id: int) -> int:
        """
        计算贷款利息
        
        Args:
            player_id: 玩家ID
            
        Returns:
            int: 利息金额
        """
        if player_id not in self.loans:
            return 0
        
        loan = self.loans[player_id]
        # 按回合计算利息（每回合15%）
        interest = int(loan["amount"] * self.loan_interest_rate * loan["turns"])
        return interest
    
    def get_loan_info(self, player: Player) -> Dict[str, any]:
        """
        获取贷款信息
        
        Args:
            player: 玩家
            
        Returns:
            Dict: 贷款信息
        """
        if player.player_id not in self.loans:
            return {"has_loan": False}
        
        loan = self.loans[player.player_id]
        interest = self.calculate_loan_interest(player.player_id)
        total_owed = loan["amount"] + interest
        
        return {
            "has_loan": True,
            "loan_amount": loan["amount"],
            "interest": interest,
            "interest_paid": loan["interest_paid"],
            "total_owed": total_owed,
            "turns": loan["turns"],
            "interest_rate": self.loan_interest_rate
        }
    
    def update_loan_turns(self, player: Player) -> None:
        """
        更新贷款回合数（每回合调用一次）
        
        Args:
            player: 玩家
        """
        if player.player_id in self.loans:
            self.loans[player.player_id]["turns"] += 1
    
    def check_loan_overdue(self, player: Player) -> bool:
        """
        检查贷款是否逾期（超过10回合）
        
        Args:
            player: 玩家
            
        Returns:
            bool: 是否逾期
        """
        if player.player_id not in self.loans:
            return False
        
        return self.loans[player.player_id]["turns"] > 10
    
    def force_repay_overdue_loan(self, player: Player) -> Dict[str, any]:
        """
        强制还款逾期贷款
        
        Args:
            player: 玩家
            
        Returns:
            Dict: 强制还款结果
        """
        if not self.check_loan_overdue(player):
            return {"success": False, "msg": "贷款未逾期"}
        
        loan = self.loans[player.player_id]
        interest = self.calculate_loan_interest(player.player_id)
        total_owed = loan["amount"] + interest
        
        # 强制扣除玩家资金
        if player.money >= total_owed:
            player.remove_money(total_owed)
            del self.loans[player.player_id]
            self.bank_pool += total_owed
            
            return {
                "success": True,
                "msg": f"强制还款成功，金额：{total_owed}",
                "amount": total_owed,
                "new_money": player.money
            }
        else:
            # 资金不足，破产处理
            player.money -= total_owed
            del self.loans[player.player_id]
            self.bank_pool += player.money + total_owed
            
            return {
                "success": True,
                "msg": f"强制还款导致破产，金额：{total_owed}",
                "amount": total_owed,
                "new_money": player.money,
                "bankrupt": True
            }
    
    def advance_interest_cycle(self) -> None:
        """
        推进利息周期
        """
        self.current_cycle += 1
    
    def should_pay_interest(self) -> bool:
        """
        检查是否应该支付利息
        
        Returns:
            bool: 是否应该支付利息
        """
        return self.current_cycle > 0 and self.current_cycle % self.interest_cycle == 0
    
    def get_bank_status(self) -> Dict[str, any]:
        """
        获取银行状态
        
        Returns:
            Dict: 银行状态信息
        """
        total_loans = sum(loan["amount"] for loan in self.loans.values())
        active_loans = len(self.loans)
        
        return {
            "bank_pool": self.bank_pool,
            "total_loans": total_loans,
            "active_loans": active_loans,
            "current_cycle": self.current_cycle,
            "interest_cycle": self.interest_cycle,
            "loan_interest_rate": self.loan_interest_rate,
            "max_loan_amount": self.max_loan_amount,
            "min_loan_amount": self.min_loan_amount
        }
    
    def reset_bank(self) -> None:
        """
        重置银行系统
        """
        self.current_cycle = 0
        self.loans.clear()
        self.bank_pool = INITIAL_BANK_MONEY * 10 