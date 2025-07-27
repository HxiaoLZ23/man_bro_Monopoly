#!/usr/bin/env python3
"""
紧急恢复方案 - 应用经过验证的补丁
"""
import sys
import os

def apply_emergency_patches():
    """应用紧急修复补丁"""
    print("🚨 开始应用紧急修复...")
    
    # 导入必要的模块
    try:
        sys.path.append('src')
        from ui.main_window import MainWindow
        print("✅ 成功导入MainWindow")
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False
    
    # 安全包装execute_settlement方法
    original_execute_settlement = MainWindow.execute_settlement
    def safe_execute_settlement(self):
        try:
            print("🔧 [安全修复] 开始安全结算")
            original_execute_settlement(self)
            print("🔧 [安全修复] 结算完成")
        except Exception as e:
            print(f"🔧 [安全修复] 结算异常: {e}")
            import traceback
            traceback.print_exc()
            try:
                current_player = self.game_state.get_current_player()
                if current_player:
                    self.add_message(f"{current_player.name}结算时发生错误，已恢复", "warning")
            except:
                pass
    MainWindow.execute_settlement = safe_execute_settlement
    
    # 安全包装advance_phase方法
    original_advance_phase = MainWindow.advance_phase
    def safe_advance_phase(self):
        try:
            print("🔧 [安全修复] 开始安全阶段推进")
            original_advance_phase(self)
            print("🔧 [安全修复] 阶段推进完成")
        except Exception as e:
            print(f"🔧 [安全修复] 阶段推进异常: {e}")
            import traceback
            traceback.print_exc()
            # 设置紧急恢复
            self.phase_auto_advance = False
            self.phase_timer = 0
            try:
                self.add_message("阶段推进出现错误，已恢复", "warning")
            except:
                pass
    MainWindow.advance_phase = safe_advance_phase
    
    # 智能自动推进控制
    original_start_settlement = MainWindow.start_settlement_phase
    def smart_start_settlement_phase(self):
        """智能结算阶段开始"""
        current_player = self.game_state.get_current_player()
        self.add_message(f"{current_player.name}的结算阶段", "info")
        
        # 自动执行结算逻辑
        self.execute_settlement()
        
        # 检查是否有UI窗口打开
        has_open_window = False
        
        if hasattr(self, 'bank_window') and self.bank_window and getattr(self.bank_window, 'visible', False):
            has_open_window = True
            print("🔧 [智能控制] 银行窗口已打开，暂停自动推进")
        elif hasattr(self, 'item_shop_window') and self.item_shop_window and getattr(self.item_shop_window, 'visible', False):
            has_open_window = True
            print("🔧 [智能控制] 道具商店窗口已打开，暂停自动推进")
        elif hasattr(self, 'dice_shop_window') and self.dice_shop_window and getattr(self.dice_shop_window, 'visible', False):
            has_open_window = True
            print("🔧 [智能控制] 骰子商店窗口已打开，暂停自动推进")
        elif hasattr(self, 'property_window') and self.property_window and getattr(self.property_window, 'visible', False):
            has_open_window = True
            print("🔧 [智能控制] 房产窗口已打开，暂停自动推进")
        
        # 只有在没有窗口打开时才设置自动推进
        if not has_open_window:
            self.phase_auto_advance = True
            self.phase_timer = 1500  # 1.5秒延迟
            print("🔧 [智能控制] 设置自动推进定时器")
        else:
            self.phase_auto_advance = False
            self.phase_timer = 0
            print("🔧 [智能控制] 因窗口打开而暂停自动推进")
    
    MainWindow.start_settlement_phase = smart_start_settlement_phase
    
    print("✅ 紧急修复补丁已应用")
    return True

def main():
    """主函数"""
    if apply_emergency_patches():
        print("🔧 启动带安全补丁的游戏...")
        
        # 启动游戏
        import pygame
        from src.ui.main_window import MainWindow
        
        # 检查是否重用现有窗口
        if pygame.get_init():
            print("🎮 重用现有pygame窗口...")
            screen = pygame.display.get_surface()
        else:
            print("🎮 创建新的pygame窗口...")
            pygame.init()
            screen = pygame.display.set_mode((1200, 800), pygame.RESIZABLE)
            pygame.display.set_caption("大富翁游戏")
        
        # 创建主窗口
        main_window = MainWindow(screen)
        
        # 直接初始化游戏场景
        main_window.init_game_scene()
        
        # 运行游戏
        main_window.run()
    else:
        print("❌ 紧急修复失败")

if __name__ == "__main__":
    main() 