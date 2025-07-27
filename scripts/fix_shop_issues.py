"""
修复商店相关问题：
1. 商店格子类型匹配错误（item_shop -> shop）
2. 商店窗口属性检查错误（is_open -> visible）
3. 添加崩溃安全处理
"""

import re
import os

def fix_shop_issues():
    """修复商店相关问题"""
    main_window_path = "src/ui/main_window.py"
    
    if not os.path.exists(main_window_path):
        print(f"❌ 文件不存在: {main_window_path}")
        return False
    
    print("🔧 开始修复商店问题...")
    
    try:
        # 读取文件
        with open(main_window_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. 修复商店格子类型匹配（item_shop -> shop）
        print("🔧 修复商店格子类型匹配...")
        content = content.replace(
            'elif current_cell.cell_type == "item_shop":',
            'elif current_cell.cell_type == "shop":'
        )
        
        # 2. 修复商店窗口属性检查（is_open -> visible）
        print("🔧 修复商店窗口属性检查...")
        
        # 修复骰子商店窗口检查
        content = content.replace(
            'if not handled and self.dice_shop_window and self.dice_shop_window.is_open:',
            'if not handled and self.dice_shop_window and getattr(self.dice_shop_window, "visible", False):'
        )
        
        # 修复道具商店窗口检查
        content = content.replace(
            'if not handled and self.item_shop_window and self.item_shop_window.is_open:',
            'if not handled and self.item_shop_window and getattr(self.item_shop_window, "visible", False):'
        )
        
        # 修复骰子商店ESC关闭检查
        content = content.replace(
            'elif self.dice_shop_window and self.dice_shop_window.is_open:',
            'elif self.dice_shop_window and getattr(self.dice_shop_window, "visible", False):'
        )
        
        # 修复道具商店ESC关闭检查
        content = content.replace(
            'elif self.item_shop_window and self.item_shop_window.is_open:',
            'elif self.item_shop_window and getattr(self.item_shop_window, "visible", False):'
        )
        
        # 修复绘制检查
        content = content.replace(
            'if self.dice_shop_window and self.dice_shop_window.is_open:',
            'if self.dice_shop_window and getattr(self.dice_shop_window, "visible", False):'
        )
        
        content = content.replace(
            'if self.item_shop_window and self.item_shop_window.is_open:',
            'if self.item_shop_window and getattr(self.item_shop_window, "visible", False):'
        )
        
        # 3. 为商店窗口添加安全的 draw 方法调用
        print("🔧 添加安全的绘制方法...")
        
        # 修复骰子商店绘制
        draw_dice_shop_pattern = r'if self\.dice_shop_window and getattr\(self\.dice_shop_window, "visible", False\):\s*self\.dice_shop_window\.draw\(\)'
        draw_dice_shop_replacement = '''if self.dice_shop_window and getattr(self.dice_shop_window, "visible", False):
            try:
                self.dice_shop_window.draw(self.screen)
            except Exception as e:
                print(f"🔧 骰子商店绘制错误: {e}")'''
        
        content = re.sub(draw_dice_shop_pattern, draw_dice_shop_replacement, content)
        
        # 修复道具商店绘制
        draw_item_shop_pattern = r'if self\.item_shop_window and getattr\(self\.item_shop_window, "visible", False\):\s*self\.item_shop_window\.draw\(\)'
        draw_item_shop_replacement = '''if self.item_shop_window and getattr(self.item_shop_window, "visible", False):
            try:
                self.item_shop_window.draw(self.screen)
            except Exception as e:
                print(f"🔧 道具商店绘制错误: {e}")'''
        
        content = re.sub(draw_item_shop_pattern, draw_item_shop_replacement, content)
        
        # 4. 为使用道具添加安全处理
        print("🔧 为使用道具添加安全处理...")
        
        # 找到 execute_item_use 方法并添加安全包装
        execute_item_pattern = r'(def execute_item_use\(self, item_id: int, target_info: dict\):)'
        execute_item_replacement = r'''\1
        """执行道具使用"""
        try:'''
        
        if "def execute_item_use(self, item_id: int, target_info: dict):" in content:
            # 添加异常处理
            lines = content.split('\n')
            new_lines = []
            in_execute_item = False
            indent_level = 0
            
            for line in lines:
                if 'def execute_item_use(self, item_id: int, target_info: dict):' in line:
                    in_execute_item = True
                    indent_level = len(line) - len(line.lstrip())
                    new_lines.append(line)
                    continue
                    
                if in_execute_item:
                    if line.strip() and not line.startswith(' ' * (indent_level + 1)) and 'def ' in line:
                        # 到了下一个方法，结束
                        # 在前面添加异常处理结束
                        new_lines.append(' ' * (indent_level + 4) + 'except Exception as e:')
                        new_lines.append(' ' * (indent_level + 8) + 'print(f"🔧 道具使用错误: {e}")')
                        new_lines.append(' ' * (indent_level + 8) + 'import traceback')
                        new_lines.append(' ' * (indent_level + 8) + 'traceback.print_exc()')
                        new_lines.append(' ' * (indent_level + 8) + 'try:')
                        new_lines.append(' ' * (indent_level + 12) + 'self.add_message("道具使用失败", "error")')
                        new_lines.append(' ' * (indent_level + 12) + 'self.close_inventory_window()')
                        new_lines.append(' ' * (indent_level + 8) + 'except:')
                        new_lines.append(' ' * (indent_level + 12) + 'pass')
                        in_execute_item = False
                        new_lines.append(line)
                    elif line.strip().startswith('"""') and line.strip().endswith('"""'):
                        # 文档字符串后添加try
                        new_lines.append(line)
                        new_lines.append(' ' * (indent_level + 4) + 'try:')
                    else:
                        # 缩进所有内容
                        if line.strip():
                            new_lines.append(' ' * 4 + line)
                        else:
                            new_lines.append(line)
                else:
                    new_lines.append(line)
                    
            content = '\n'.join(new_lines)
        
        # 检查是否有修改
        if content != original_content:
            # 写入文件
            with open(main_window_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ 商店问题修复完成！")
            print("🔧 修复内容:")
            print("  - 商店格子类型: item_shop -> shop")
            print("  - 窗口属性检查: is_open -> visible") 
            print("  - 添加了安全的绘制方法")
            print("  - 为道具使用添加了异常处理")
            return True
        else:
            print("ℹ️ 没有发现需要修复的问题")
            return True
            
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 商店问题修复工具")
    print("=" * 50)
    
    if fix_shop_issues():
        print("\n✅ 修复成功！现在商店应该可以正常打开了")
        print("🎮 重新启动游戏测试商店功能")
    else:
        print("\n❌ 修复失败，请检查错误信息") 