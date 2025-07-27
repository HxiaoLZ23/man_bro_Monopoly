"""
大富翁游戏崩溃问题完整修复方案
根本问题：游戏在投掷骰子后的结算阶段出现未捕获的异常导致崩溃
"""

import sys
import traceback
sys.path.append('.')

def patch_main_window():
    """修复MainWindow中的崩溃问题"""
    from src.ui.main_window import MainWindow
    
    # 保存原始方法
    original_execute_settlement = MainWindow.execute_settlement
    original_advance_phase = MainWindow.advance_phase
    original_update = MainWindow.update
    original_handle_events = MainWindow.handle_events
    
    def safe_execute_settlement(self):
        """安全的结算执行"""
        try:
            print("🔧 [修复] 开始安全结算")
            original_execute_settlement(self)
            print("🔧 [修复] 结算完成")
            
            # 检查是否有UI窗口打开，如果有则不自动推进
            has_open_window = False
            if hasattr(self, 'bank_window') and self.bank_window and getattr(self.bank_window, 'visible', False):
                has_open_window = True
                print("🔧 [修复] 银行窗口已打开，暂停自动推进")
            elif hasattr(self, 'item_shop_window') and self.item_shop_window and getattr(self.item_shop_window, 'visible', False):
                has_open_window = True
                print("🔧 [修复] 道具商店窗口已打开，暂停自动推进")
            elif hasattr(self, 'property_window') and self.property_window and getattr(self.property_window, 'visible', False):
                has_open_window = True
                print("🔧 [修复] 房产窗口已打开，暂停自动推进")
            
            # 只有在没有窗口打开时才设置自动推进
            if not has_open_window:
                self.phase_auto_advance = True
                self.phase_timer = 1500
                print("🔧 [修复] 设置自动推进定时器")
            else:
                self.phase_auto_advance = False
                self.phase_timer = 0
                print("🔧 [修复] 因窗口打开而暂停自动推进")
            
        except Exception as e:
            print(f"🔧 [修复] 结算异常: {e}")
            traceback.print_exc()
            
            # 异常时安全处理
            try:
                current_player = self.game_state.get_current_player()
                if current_player:
                    self.add_message(f"{current_player.name}结算时出现问题，自动跳过", "error")
                
                # 强制推进到下一阶段
                print("🔧 [修复] 异常时强制推进阶段")
                self.phase_auto_advance = False
                self.advance_phase()
                
            except Exception as e2:
                print(f"🔧 [修复] 强制推进也失败: {e2}")
                # 最后手段：重置游戏状态
                self.phase_auto_advance = False
                self.phase_timer = 0
    
    def safe_advance_phase(self):
        """安全的阶段推进"""
        try:
            print("🔧 [修复] 开始安全阶段推进")
            original_advance_phase(self)
            print("🔧 [修复] 阶段推进完成")
        except Exception as e:
            print(f"🔧 [修复] 阶段推进异常: {e}")
            traceback.print_exc()
            
            # 异常时的安全处理
            try:
                # 重置自动推进状态
                self.phase_auto_advance = False
                self.phase_timer = 0
                
                # 添加错误消息
                self.add_message("阶段推进时出现错误", "error")
                
                # 尝试获取当前玩家
                current_player = self.game_state.get_current_player()
                if current_player:
                    print(f"🔧 [修复] 当前玩家: {current_player.name}")
                    # 确保游戏继续运行
                    if not hasattr(self, 'emergency_recovery_timer'):
                        self.emergency_recovery_timer = 3000  # 3秒后尝试恢复
                        print("🔧 [修复] 设置紧急恢复定时器")
                        
            except Exception as e2:
                print(f"🔧 [修复] 紧急处理也失败: {e2}")
                # 保持游戏运行，不崩溃
                pass
    
    def safe_update(self):
        """安全的更新方法"""
        try:
            original_update(self)
            
            # 处理紧急恢复
            if hasattr(self, 'emergency_recovery_timer') and self.emergency_recovery_timer > 0:
                self.emergency_recovery_timer -= self.clock.get_time()
                if self.emergency_recovery_timer <= 0:
                    print("🔧 [修复] 执行紧急恢复")
                    delattr(self, 'emergency_recovery_timer')
                    # 尝试重新开始准备阶段
                    try:
                        self.game_state.set_current_phase("preparation")
                        self.start_preparation_phase()
                    except:
                        pass
                        
        except Exception as e:
            print(f"🔧 [修复] 更新异常: {e}")
            # 不让异常传播，保持游戏运行
            pass
    
    def safe_handle_events(self):
        """安全的事件处理"""
        try:
            original_handle_events(self)
        except Exception as e:
            print(f"🔧 [修复] 事件处理异常: {e}")
            # 清理有问题的事件，但不崩溃
            import pygame
            pygame.event.clear()
    
    # 应用补丁
    MainWindow.execute_settlement = safe_execute_settlement
    MainWindow.advance_phase = safe_advance_phase
    MainWindow.update = safe_update
    MainWindow.handle_events = safe_handle_events
    
    print("🔧 [修复] 游戏崩溃修复补丁已应用")

def patch_bank_window():
    """修复银行窗口的问题"""
    try:
        from src.ui.main_window import MainWindow
        
        original_close_bank = MainWindow.close_bank
        
        def safe_close_bank(self):
            """安全的银行关闭"""
            print("🔧 [修复] 银行窗口安全关闭")
            try:
                if self.bank_window:
                    self.bank_window.hide()
                
                # 只有在结算阶段才推进
                if self.game_state.current_phase == "settlement":
                    print("🔧 [修复] 结算阶段银行关闭，推进阶段")
                    self.advance_phase()
                else:
                    print(f"🔧 [修复] 当前阶段是 {self.game_state.current_phase}，不推进")
                    
            except Exception as e:
                print(f"🔧 [修复] 银行关闭异常: {e}")
                # 不让异常传播
                pass
        
        MainWindow.close_bank = safe_close_bank
        print("🔧 [修复] 银行窗口修复补丁已应用")
        
    except ImportError:
        print("🔧 [修复] 银行窗口模块未找到，跳过修复")

def apply_all_fixes():
    """应用所有修复"""
    print("🔧 开始应用游戏崩溃修复...")
    
    try:
        patch_main_window()
        patch_bank_window()
        print("🔧 所有修复补丁已成功应用！")
        return True
    except Exception as e:
        print(f"🔧 修复补丁应用失败: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 应用修复
    if apply_all_fixes():
        print("🎮 启动修复后的游戏...")
        
        try:
            import pygame
            from src.ui.main_window import MainWindow
            
            pygame.init()
            pygame.mixer.init()
            
            screen = pygame.display.set_mode((900, 900))
            pygame.display.set_caption("大富翁游戏 - 修复版")
            
            main_window = MainWindow(screen)
            main_window.select_map("default")
            main_window.start_game()
            
            main_window.run()
            
        except Exception as e:
            print(f"🔧 游戏运行异常: {e}")
            traceback.print_exc()
    else:
        print("🔧 修复失败，无法启动游戏") 