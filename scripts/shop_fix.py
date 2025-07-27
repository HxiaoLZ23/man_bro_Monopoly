"""简单修复商店问题"""
import os

# 读取文件
with open("src/ui/main_window.py", 'r', encoding='utf-8') as f:
    content = f.read()

# 修复1: 商店格子类型
content = content.replace(
    'elif current_cell.cell_type == "item_shop":',
    'elif current_cell.cell_type == "shop":'
)

# 修复2: 窗口属性检查
content = content.replace(
    'self.dice_shop_window.is_open',
    'getattr(self.dice_shop_window, "visible", False)'
)

content = content.replace(
    'self.item_shop_window.is_open',
    'getattr(self.item_shop_window, "visible", False)'
)

# 修复3: 绘制方法调用
content = content.replace(
    'self.dice_shop_window.draw()',
    'self.dice_shop_window.draw(self.screen)'
)

content = content.replace(
    'self.item_shop_window.draw()',
    'self.item_shop_window.draw(self.screen)'
)

# 写入文件
with open("src/ui/main_window.py", 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 商店修复完成！")
print("修复内容:")
print("1. 商店格子类型: item_shop -> shop") 
print("2. 窗口属性: is_open -> visible")
print("3. 绘制方法: 添加screen参数") 