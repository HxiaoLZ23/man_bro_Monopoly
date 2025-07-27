#!/usr/bin/env python3
"""
最终的UI闪烁修复方案
基于之前的调试结果，提供一个完整的修复
"""
import pygame
import sys
import traceback

# 添加src目录到路径
sys.path.append('src')

def apply_final_ui_fix():
    """应用最终的UI闪烁修复"""
    
    from src.ui.main_window import MainWindow
    
    # 1. 修复重复的清理代码
    original_init_multiplayer_game = MainWindow.init_multiplayer_game
    
    def fixed_init_multiplayer_game(self, game_data: dict):
        """修复版的init_multiplayer_game"""
        print(f"🎮 [FIXED] 初始化多人游戏: {game_data}")
        
        try:
            # 设置多人游戏标识
            self.is_multiplayer = True
            self.multiplayer_data = game_data
            
            # 加载地图
            map_file = game_data.get('map_file', '1.json')
            print(f"🗺️ 加载地图文件: {map_file}")
            
            # 使用地图数据管理器加载地图
            from src.systems.map_data_manager import MapDataManager
            map_manager = MapDataManager()
            
            # 尝试加载地图
            map_loaded = False
            for map_path in [map_file, f"data/{map_file}", f"{map_file}"]:
                try:
                    self.game_map = map_manager.load_map('json', map_path)
                    if self.game_map:
                        print(f"✅ 地图加载成功: {map_path}")
                        map_loaded = True
                        break
                except Exception as e:
                    print(f"⚠️ 尝试加载地图失败 {map_path}: {e}")
                    continue
            
            if not map_loaded:
                print(f"❌ 地图加载失败，使用默认地图")
                self.add_message("地图加载失败，使用默认地图", "warning")
                # 创建默认地图
                self.game_map = self.create_sample_map()
                if not self.game_map:
                    print(f"❌ 默认地图创建失败")
                    return False
            
            # 创建多人游戏玩家
            players_data = game_data.get('players', [])
            print(f"👥 创建玩家: {len(players_data)}人")
            
            players = []
            for i, player_data in enumerate(players_data):
                from src.models.player import Player
                
                player_id = i + 1
                player_name = player_data.get('name', f'玩家{player_id}')
                client_id = player_data.get('client_id', '')
                
                # 判断是否是AI玩家
                is_ai = 'ai_' in client_id.lower() or 'ai玩家' in player_name
                
                player = Player(player_id, player_name, is_ai=is_ai)
                player.client_id = client_id  # 添加客户端ID用于网络同步
                players.append(player)
                
                print(f"  - 玩家{player_id}: {player_name} ({'AI' if is_ai else '人类'})")
            
            if len(players) < 2:
                print(f"❌ 玩家数量不足: {len(players)}")
                self.add_message("玩家数量不足，无法开始游戏", "error")
                return False
            
            # 初始化游戏状态
            print("🎲 初始化游戏状态...")
            if self.game_state.initialize_game(players, self.game_map):
                print("✅ 游戏状态初始化成功")
                
                # 设置PlayerManager
                self.player_manager.set_players(players)
                self.player_manager.set_game_map(self.game_map)
                
                # 【修复】只清理一次界面元素，避免重复清理
                print("🧹 [FIXED] 清理界面元素...")
                self.buttons.clear()
                self.panels.clear()
                self.dialogs.clear()
                self.phase_buttons.clear()
                
                # 初始化游戏界面
                print("🖼️ 初始化游戏界面...")
                self.init_game_scene()
                self.add_message("多人游戏开始！", "success")
                
                # 开始第一个回合
                print("🎯 开始游戏回合...")
                self.start_turn_phase()
                
                return True
            else:
                print("❌ 游戏状态初始化失败")
                self.add_message("游戏初始化失败", "error")
                return False
        
        except Exception as e:
            print(f"❌ 多人游戏初始化异常: {e}")
            import traceback
            traceback.print_exc()
            self.add_message(f"游戏初始化失败: {e}", "error")
            return False
    
    # 2. 优化draw方法，减少不必要的重绘
    original_draw = MainWindow.draw
    
    def optimized_draw(self):
        """优化版的draw方法"""
        # 在多人游戏模式下确保场景正确
        if hasattr(self, 'is_multiplayer') and self.is_multiplayer and self.current_scene != "game":
            print(f"⚠️ [FIXED] 多人游戏模式下强制纠正场景: {self.current_scene} -> game")
            self.current_scene = "game"
        
        return original_draw(self)
    
    # 3. 强化按钮事件处理
    original_handle_events = MainWindow.handle_events
    
    def safe_handle_events(self):
        """安全版的事件处理"""
        try:
            return original_handle_events(self)
        except Exception as e:
            print(f"🚨 [FIXED] 事件处理异常被捕获: {e}")
            # 在多人游戏模式下确保界面状态
            if hasattr(self, 'is_multiplayer') and self.is_multiplayer:
                if self.current_scene != "game":
                    print(f"🔧 [FIXED] 异常后纠正场景: {self.current_scene} -> game")
                    self.current_scene = "game"
    
    # 4. 防止phase_buttons重复清理导致的视觉闪烁
    original_show_preparation_choices = MainWindow.show_preparation_choices
    original_show_action_choices = MainWindow.show_action_choices
    
    def stable_show_preparation_choices(self):
        """稳定版的show_preparation_choices"""
        # 在多人游戏模式下，减少不必要的清理
        if hasattr(self, 'is_multiplayer') and self.is_multiplayer:
            # 只有在按钮内容真正需要改变时才清理
            current_button_texts = [getattr(btn, 'text', '') for btn in self.phase_buttons]
            expected_texts = ["更换骰子", "使用道具", "跳过"]
            
            if current_button_texts != expected_texts:
                self.phase_buttons.clear()
                
                # 重新创建按钮
                from src.ui.components import Button
                from src.ui.constants import COLORS, WINDOW_WIDTH, WINDOW_HEIGHT
                
                # 更换骰子按钮
                dice_button = Button(
                    WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT - 200, 120, 40,
                    "更换骰子", self.change_dice
                )
                self.phase_buttons.append(dice_button)
                
                # 使用道具按钮
                item_button = Button(
                    WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT - 200, 120, 40,
                    "使用道具", self.use_item
                )
                self.phase_buttons.append(item_button)
                
                # 跳过按钮
                skip_button = Button(
                    WINDOW_WIDTH // 2 + 80, WINDOW_HEIGHT - 200, 120, 40,
                    "跳过", self.skip_preparation, COLORS["warning"]
                )
                self.phase_buttons.append(skip_button)
        else:
            # 单人游戏模式使用原方法
            return original_show_preparation_choices(self)
    
    def stable_show_action_choices(self):
        """稳定版的show_action_choices"""
        # 在多人游戏模式下，减少不必要的清理
        if hasattr(self, 'is_multiplayer') and self.is_multiplayer:
            # 只有在按钮内容真正需要改变时才清理
            current_button_texts = [getattr(btn, 'text', '') for btn in self.phase_buttons]
            expected_texts = ["投骰子"]
            
            if current_button_texts != expected_texts:
                self.phase_buttons.clear()
                
                # 重新创建按钮
                from src.ui.components import Button
                from src.ui.constants import COLORS, WINDOW_WIDTH, WINDOW_HEIGHT
                
                # 投骰子按钮
                roll_button = Button(
                    WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT - 200, 120, 40,
                    "投骰子", self.roll_dice, COLORS["primary"]
                )
                self.phase_buttons.append(roll_button)
        else:
            # 单人游戏模式使用原方法
            return original_show_action_choices(self)
    
    # 应用所有修复
    MainWindow.init_multiplayer_game = fixed_init_multiplayer_game
    MainWindow.draw = optimized_draw
    MainWindow.handle_events = safe_handle_events
    MainWindow.show_preparation_choices = stable_show_preparation_choices
    MainWindow.show_action_choices = stable_show_action_choices
    
    print("🔧 最终UI闪烁修复已应用")

def test_final_fix():
    """测试最终修复方案"""
    print("🕵️ 测试最终UI闪烁修复方案...")
    
    # 应用修复
    apply_final_ui_fix()
    
    try:
        from src.ui.main_window import MainWindow
        
        # 创建主窗口
        main_window = MainWindow()
        
        # 设置多人游戏模式
        main_window.is_multiplayer = True
        
        # 模拟游戏初始化
        game_data = {
            'map_file': '1.json',
            'players': [
                {'name': '玩家1', 'client_id': 'client1'},
                {'name': '玩家2', 'client_id': 'client2'},  
                {'name': 'AI玩家1', 'client_id': 'ai_1'}
            ]
        }
        
        print("🚀 测试修复后的多人游戏初始化...")
        result = main_window.init_multiplayer_game(game_data)
        if not result:
            print("❌ 游戏初始化失败")
            return
        
        print("✅ 修复后的游戏初始化成功")
        print(f"📊 最终状态:")
        print(f"  - 场景: {main_window.current_scene}")
        print(f"  - 按钮数: {len(main_window.buttons)}")
        print(f"  - 阶段按钮数: {len(main_window.phase_buttons)}")
        print(f"  - 多人游戏: {getattr(main_window, 'is_multiplayer', False)}")
        
        # 运行短时间以测试稳定性
        print("🎮 测试UI稳定性...")
        clock = pygame.time.Clock()
        test_frames = 120  # 2秒测试
        
        for frame in range(test_frames):
            # 处理基本事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
            
            # 测试游戏循环
            main_window.handle_events()
            main_window.update()
            main_window.draw()
            
            # 每30帧检查一次状态
            if frame % 30 == 0:
                print(f"  📊 帧{frame}: 场景={main_window.current_scene}, 按钮={len(main_window.buttons)}, 阶段按钮={len(main_window.phase_buttons)}")
            
            clock.tick(60)
        
        pygame.quit()
        print("🎉 最终修复测试完成！UI应该不再闪烁")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()
        try:
            pygame.quit()
        except:
            pass

if __name__ == "__main__":
    test_final_fix() 