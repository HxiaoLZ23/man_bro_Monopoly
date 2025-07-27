"""
银行界面
"""
import pygame
from typing import Callable, Optional
from src.ui.components import Button
from src.ui.constants import COLORS
from src.ui.font_manager import get_font, render_text


class BankWindow:
    """银行窗口"""
    
    def __init__(self, on_close: Callable = None, on_deposit: Callable = None, on_withdraw: Callable = None):
        """初始化银行窗口"""
        self.on_close = on_close
        self.on_deposit = on_deposit
        self.on_withdraw = on_withdraw
        self.visible = False
        
        # 窗口属性
        self.width = 600
        self.height = 450
        self.x = 0
        self.y = 0
        
        # 按钮
        self.close_button = None
        self.deposit_buttons = []
        self.withdraw_buttons = []
        
        # 当前玩家信息（由外部设置）
        self.player_cash = 0  # 身上现金
        self.player_bank = 0  # 银行存款
        self.total_bank_assets = 0  # 银行总资产
        self.rounds_until_interest = 0  # 距离下次利息的轮数
        
        # 存取金额选项
        self.amount_options = [1000, 5000, 10000, 50000, 100000]
        
    def show(self, screen_width: int, screen_height: int, player_cash: int, 
             player_bank: int, total_bank_assets: int, rounds_until_interest: int):
        """显示窗口"""
        self.visible = True
        self.player_cash = player_cash
        self.player_bank = player_bank
        self.total_bank_assets = total_bank_assets
        self.rounds_until_interest = rounds_until_interest
        
        # 居中显示
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        
        # 创建按钮
        self._create_buttons()
    
    def hide(self):
        """隐藏窗口"""
        self.visible = False
        
    def _create_buttons(self):
        """创建按钮"""
        # 关闭按钮
        self.close_button = Button(
            self.x + self.width - 100, self.y + 10, 80, 40,
            "关闭", lambda: self._handle_close(),
            font_size="normal"
        )
        
        # 存款按钮
        self.deposit_buttons = []
        start_x = self.x + 50
        start_y = self.y + 200
        
        for i, amount in enumerate(self.amount_options):
            can_deposit = self.player_cash >= amount
            
            button = Button(
                start_x + (i % 3) * 160, start_y + (i // 3) * 50, 140, 40,
                f"存入 ${amount:,}",
                lambda amt=amount: self._handle_deposit(amt),
                font_size="small",
                color=COLORS["success"] if can_deposit else COLORS["disabled"]
            )
            button.enabled = can_deposit
            self.deposit_buttons.append(button)
        
        # 全部存入按钮
        if self.player_cash > 0:
            all_deposit_button = Button(
                start_x + 320, start_y, 140, 40,
                f"全部存入",
                lambda: self._handle_deposit(self.player_cash),
                font_size="small",
                color=COLORS["success"]
            )
            self.deposit_buttons.append(all_deposit_button)
        
        # 取款按钮
        self.withdraw_buttons = []
        start_y = self.y + 320
        
        for i, amount in enumerate(self.amount_options):
            can_withdraw = self.player_bank >= amount
            
            button = Button(
                start_x + (i % 3) * 160, start_y + (i // 3) * 50, 140, 40,
                f"取${amount:,}" if can_withdraw else "余额不足",
                lambda amt=amount: self._handle_withdraw(amt),
                font_size="small",
                color=COLORS["success"] if can_withdraw else COLORS["disabled"]
            )
            button.enabled = can_withdraw
            self.withdraw_buttons.append(button)
        
        # 全部取出按钮
        if self.player_bank > 0:
            all_withdraw_button = Button(
                start_x + 320, start_y, 140, 40,
                f"全部取出",
                lambda: self._handle_withdraw(self.player_bank),
                font_size="small",
                color=COLORS["primary"]
            )
            self.withdraw_buttons.append(all_withdraw_button)
    
    def _handle_close(self):
        """处理关闭"""
        self.hide()
        if self.on_close:
            self.on_close()
    
    def _handle_deposit(self, amount: int):
        """处理存款"""
        if self.on_deposit:
            self.on_deposit(amount)
    
    def _handle_withdraw(self, amount: int):
        """处理取款"""
        if self.on_withdraw:
            self.on_withdraw(amount)
    
    def _get_interest_rate(self) -> float:
        """获取当前利息率"""
        if self.total_bank_assets < 100000:
            return 0.05  # 5%
        elif self.total_bank_assets < 300000:
            return 0.10  # 10%
        elif self.total_bank_assets < 500000:
            return 0.20  # 20%
        else:
            return 0.30  # 30%
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件"""
        if not self.visible:
            return False
            
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 检查关闭按钮
            if self.close_button.rect.collidepoint(mouse_pos):
                self.close_button.callback()
                return True
            
            # 检查存款按钮
            for button in self.deposit_buttons:
                if hasattr(button, 'enabled') and button.enabled and button.rect.collidepoint(mouse_pos):
                    if button.callback:
                        button.callback()
                    return True
                elif not hasattr(button, 'enabled') and button.rect.collidepoint(mouse_pos):
                    if button.callback:
                        button.callback()
                    return True
            
            # 检查取款按钮
            for button in self.withdraw_buttons:
                if hasattr(button, 'enabled') and button.enabled and button.rect.collidepoint(mouse_pos):
                    if button.callback:
                        button.callback()
                    return True
                elif not hasattr(button, 'enabled') and button.rect.collidepoint(mouse_pos):
                    if button.callback:
                        button.callback()
                    return True
        
        return True  # 消费所有事件
    
    def draw(self, surface: pygame.Surface):
        """绘制窗口"""
        if not self.visible:
            return
            
        # 绘制半透明背景
        overlay = pygame.Surface((surface.get_width(), surface.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # 绘制窗口背景
        window_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, COLORS["background"], window_rect)
        pygame.draw.rect(surface, COLORS["primary"], window_rect, 3)
        
        # 绘制银行图标（如果有的话）
        try:
            bank_image = pygame.image.load("assets/images/building/bank.jpeg")
            bank_image = pygame.transform.scale(bank_image, (60, 60))
            surface.blit(bank_image, (self.x + 20, self.y + 20))
        except:
            pass
        
        # 绘制标题
        title_surface = render_text("银行", "large", COLORS["text_primary"], True)
        title_x = self.x + (self.width - title_surface.get_width()) // 2
        surface.blit(title_surface, (title_x, self.y + 20))
        
        # 绘制玩家资产信息
        info_y = self.y + 70
        
        cash_text = f"身上现金: ${self.player_cash:,}"
        cash_surface = render_text(cash_text, "normal", COLORS["text_primary"])
        surface.blit(cash_surface, (self.x + 50, info_y))
        
        bank_text = f"银行存款: ${self.player_bank:,}"
        bank_surface = render_text(bank_text, "normal", COLORS["text_primary"])
        surface.blit(bank_surface, (self.x + 50, info_y + 25))
        
        total_text = f"总资产: ${self.player_cash + self.player_bank:,}"
        total_surface = render_text(total_text, "normal", COLORS["success"], True)
        surface.blit(total_surface, (self.x + 50, info_y + 50))
        
        # 绘制银行信息
        bank_info_y = info_y + 80
        
        total_bank_text = f"银行总资产: ${self.total_bank_assets:,}"
        total_bank_surface = render_text(total_bank_text, "small", COLORS["text_secondary"])
        surface.blit(total_bank_surface, (self.x + 50, bank_info_y))
        
        interest_rate = self._get_interest_rate()
        interest_text = f"当前利息率: {interest_rate*100:.0f}%"
        interest_surface = render_text(interest_text, "small", COLORS["success"])
        surface.blit(interest_surface, (self.x + 250, bank_info_y))
        
        rounds_text = f"距离下次利息: {self.rounds_until_interest}轮"
        rounds_surface = render_text(rounds_text, "small", COLORS["text_secondary"])
        surface.blit(rounds_surface, (self.x + 400, bank_info_y))
        
        # 绘制利息说明
        interest_info_y = bank_info_y + 25
        interest_info_text = "利息每3轮发放一次，基于银行总资产计算"
        interest_info_surface = render_text(interest_info_text, "tiny", COLORS["text_secondary"])
        surface.blit(interest_info_surface, (self.x + 50, interest_info_y))
        
        # 绘制存款区域标题
        deposit_title_y = self.y + 175
        deposit_title_surface = render_text("存款", "subtitle", COLORS["success"], True)
        surface.blit(deposit_title_surface, (self.x + 50, deposit_title_y))
        
        # 绘制取款区域标题  
        withdraw_title_y = self.y + 295
        withdraw_title_surface = render_text("取款", "subtitle", COLORS["primary"], True)
        surface.blit(withdraw_title_surface, (self.x + 50, withdraw_title_y))
        
        # 绘制按钮
        self.close_button.draw(surface, {})
        for button in self.deposit_buttons:
            button.draw(surface, {})
        for button in self.withdraw_buttons:
            button.draw(surface, {}) 