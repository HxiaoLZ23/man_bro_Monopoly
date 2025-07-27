"""
测试商店功能
"""
import pygame
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ui.dice_shop_window import DiceShopWindow
from src.ui.item_shop_window import ItemShopWindow  
from src.ui.bank_window import BankWindow

def test_dice_shop():
    """测试骰子商店"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("测试骰子商店")
    clock = pygame.time.Clock()
    
    def on_close():
        print("关闭骰子商店")
    
    def on_purchase(product):
        print(f"购买骰子: {product['name']}, 价格: ${product['price']}")
    
    shop = DiceShopWindow(on_close=on_close, on_purchase=on_purchase)
    shop.show(1200, 800, 100000, 5)  # 玩家有10万金钱，5张道具卡
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if shop.handle_event(event):
                continue
        
        screen.fill((50, 50, 50))
        shop.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

def test_item_shop():
    """测试道具商店"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("测试道具商店")
    clock = pygame.time.Clock()
    
    def on_close():
        print("关闭道具商店")
    
    def on_purchase(item):
        print(f"购买道具: {item['name']}, 价格: ${item['price']}")
    
    shop = ItemShopWindow(on_close=on_close, on_purchase=on_purchase)
    shop.show(1200, 800, 50000)  # 玩家有5万金钱
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if shop.handle_event(event):
                continue
        
        screen.fill((50, 50, 50))
        shop.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

def test_bank():
    """测试银行"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("测试银行")
    clock = pygame.time.Clock()
    
    def on_close():
        print("关闭银行")
    
    def on_deposit(amount):
        print(f"存款: ${amount}")
    
    def on_withdraw(amount):
        print(f"取款: ${amount}")
    
    bank = BankWindow(on_close=on_close, on_deposit=on_deposit, on_withdraw=on_withdraw)
    bank.show(1200, 800, 30000, 50000, 200000, 2)  # 现金3万，银行存款5万，总资产20万，2轮后利息
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if bank.handle_event(event):
                continue
        
        screen.fill((50, 50, 50))
        bank.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    print("选择要测试的商店:")
    print("1. 骰子商店")
    print("2. 道具商店") 
    print("3. 银行")
    
    choice = input("请输入选择 (1-3): ")
    
    if choice == "1":
        test_dice_shop()
    elif choice == "2":
        test_item_shop()
    elif choice == "3":
        test_bank()
    else:
        print("无效选择") 