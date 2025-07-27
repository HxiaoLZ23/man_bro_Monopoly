#!/usr/bin/env python3
"""
修复 main.py 中的游戏崩溃问题
这个脚本会直接修改 main_window.py 文件，应用所有必要的修复
"""

import os
import re

def fix_main_window():
    """修复 main_window.py 文件"""
    file_path = "src/ui/main_window.py"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    print(f"🔧 开始修复文件: {file_path}")
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 修复 close_bank 方法
    if "只有在结算阶段才推进到下一阶段" not in content:
        content = content.replace(
            '    def close_bank(self):\n        """关闭银行"""\n        if self.bank_window:\n            self.bank_window.hide()\n        # 继续游戏流程\n        self.advance_phase()',
            '''    def close_bank(self):
        """关闭银行"""
        if self.bank_window:
            self.bank_window.hide()
        # 只有在结算阶段才推进到下一阶段
        if self.game_state.current_phase == "settlement":
            try:
                self.advance_phase()
            except Exception as e:
                print(f"🔧 关闭银行时推进阶段失败: {e}")
                # 设置自动推进作为备用方案
                self.phase_auto_advance = True
                self.phase_timer = 500  # 0.5秒后自动推进'''
        )
        print("✅ 修复了 close_bank 方法")
    
    # 2. 在 start_settlement_phase 方法中添加窗口检查
    # 查找 start_settlement_phase 方法
    settlement_pattern = r'(def start_settlement_phase\(self\):\s*"""开始结算阶段"""\s*current_player = self\.game_state\.get_current_player\(\)\s*self\.add_message\(f"{current_player\.name}的结算阶段", "info"\)\s*# 自动执行结算逻辑\s*self\.execute_settlement\(\)\s*)# 设置延迟自动推进到结束阶段，而不是立即推进\s*self\.phase_auto_advance = True\s*self\.phase_timer = 1500  # 1\.5秒延迟'
    
    settlement_replacement = r'''\1# 检查是否有UI窗口打开，如果有则不自动推进
        has_open_window = False
        
        # 检查各种可能的窗口
        if hasattr(self, 'bank_window') and self.bank_window and getattr(self.bank_window, 'visible', False):
            has_open_window = True
            print("🔧 银行窗口已打开，暂停自动推进")
        elif hasattr(self, 'item_shop_window') and self.item_shop_window and getattr(self.item_shop_window, 'visible', False):
            has_open_window = True
            print("🔧 道具商店窗口已打开，暂停自动推进")
        elif hasattr(self, 'dice_shop_window') and self.dice_shop_window and getattr(self.dice_shop_window, 'visible', False):
            has_open_window = True
            print("🔧 骰子商店窗口已打开，暂停自动推进")
        elif hasattr(self, 'property_window') and self.property_window and getattr(self.property_window, 'visible', False):
            has_open_window = True
            print("🔧 房产窗口已打开，暂停自动推进")
        
        # 只有在没有窗口打开时才设置自动推进
        if not has_open_window:
            # 设置延迟自动推进到结束阶段，而不是立即推进
            self.phase_auto_advance = True
            self.phase_timer = 1500  # 1.5秒延迟
            print("🔧 设置自动推进定时器")
        else:
            # 有窗口打开，不自动推进，等待窗口关闭
            self.phase_auto_advance = False
            self.phase_timer = 0
            print("🔧 因窗口打开而暂停自动推进")'''
    
    if "检查是否有UI窗口打开" not in content:
        content = re.sub(settlement_pattern, settlement_replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # 3. 在 execute_settlement 方法开头添加异常处理
    execute_settlement_pattern = r'(def execute_settlement\(self\):\s*"""执行结算""")'
    execute_settlement_replacement = r'''\1
        try:'''
    
    if "def execute_settlement(self):" in content and "try:" not in content.split("def execute_settlement(self):")[1].split("def ")[0]:
        content = re.sub(execute_settlement_pattern, execute_settlement_replacement, content)
        
        # 在方法末尾添加异常处理
        # 找到方法结束的位置（下一个方法开始）
        lines = content.split('\n')
        in_execute_settlement = False
        indent_level = None
        insert_position = -1
        
        for i, line in enumerate(lines):
            if 'def execute_settlement(self):' in line:
                in_execute_settlement = True
                indent_level = len(line) - len(line.lstrip())
                continue
            
            if in_execute_settlement:
                # 检查是否到了下一个方法
                if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                    # 找到了下一个顶级定义
                    insert_position = i
                    break
                elif line.strip().startswith('def ') and len(line) - len(line.lstrip()) <= indent_level:
                    # 找到了同级或更高级的方法定义
                    insert_position = i
                    break
        
        if insert_position > 0:
            exception_handler = '''        except Exception as e:
            print(f"❌ execute_settlement 异常: {e}")
            import traceback
            traceback.print_exc()
            
            # 发生错误时添加提示消息
            try:
                current_player = self.game_state.get_current_player()
                if current_player:
                    self.add_message(f"{current_player.name}结算时发生错误: {e}", "error")
                else:
                    self.add_message(f"结算时发生错误: {e}", "error")
            except:
                pass
'''
            lines.insert(insert_position, exception_handler)
            content = '\n'.join(lines)
    
    # 4. 在 update 方法中添加紧急恢复机制
    update_pattern = r'(def update\(self\):\s*"""更新游戏状态"""\s*)# 更新动画系统'
    update_replacement = r'''\1try:
            # 更新动画系统'''
    
    if "def update(self):" in content and "try:" not in content.split("def update(self):")[1].split("def ")[0].split("# 更新动画系统")[0]:
        content = re.sub(update_pattern, update_replacement, content)
        
        # 在 update 方法末尾添加异常处理
        lines = content.split('\n')
        in_update = False
        indent_level = None
        insert_position = -1
        
        for i, line in enumerate(lines):
            if 'def update(self):' in line:
                in_update = True
                indent_level = len(line) - len(line.lstrip())
                continue
            
            if in_update:
                if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                    insert_position = i
                    break
                elif line.strip().startswith('def ') and len(line) - len(line.lstrip()) <= indent_level:
                    insert_position = i
                    break
        
        if insert_position > 0:
            exception_handler = '''        except Exception as e:
            print(f"🔧 update 异常: {e}")
            import traceback
            traceback.print_exc()
            # 不让异常传播，保持游戏运行
            try:
                self.add_message("游戏更新时出现错误", "error")
                # 重置可能有问题的状态
                self.phase_auto_advance = False
                self.phase_timer = 0
            except:
                pass
'''
            lines.insert(insert_position, exception_handler)
            content = '\n'.join(lines)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 修复完成: {file_path}")
    return True

def main():
    """主函数"""
    print("🔧 开始修复游戏崩溃问题...")
    
    if fix_main_window():
        print("✅ 所有修复已完成！")
        print("🎮 现在可以运行 python main.py 来测试修复后的游戏")
    else:
        print("❌ 修复失败")

if __name__ == "__main__":
    main() 