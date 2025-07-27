"""
存档管理UI窗口
使用pygame实现，避免tkinter多线程问题
"""
import pygame
import os
import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

from src.systems.save_system import SaveSystem
from src.models.game_state import GameState


class SaveLoadWindow:
    """存档管理窗口（使用pygame实现）"""
    
    def __init__(self, screen, parent_window=None):
        """
        初始化存档管理窗口
        
        Args:
            screen: pygame显示表面
            parent_window: 父窗口
        """
        self.screen = screen
        self.parent_window = parent_window
        self.save_system = SaveSystem()
        
        # 窗口设置
        self.is_open = False
        self.mode = "load"  # "save" 或 "load"
        
        # 回调函数
        self.on_save_callback = None
        self.on_load_callback = None
        self.on_close_callback = None
        
        # 界面设置
        self.window_rect = pygame.Rect(100, 50, 1000, 700)
        
        # 使用全局字体管理器
        try:
            from src.ui.font_manager import get_font
            self.font_large = get_font("heading")      # 24px
            self.font_medium = get_font("normal")      # 24px  
            self.font_small = get_font("small")        # 16px
            print("✅ 存档窗口成功加载中文字体")
        except Exception as e:
            print(f"⚠️ 存档窗口字体加载失败，使用默认字体: {e}")
            # 备用方案：使用默认字体
            self.font_large = pygame.font.Font(None, 28)
            self.font_medium = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 20)
        
        # 颜色定义
        self.colors = {
            'background': (45, 45, 45),
            'window': (60, 60, 60),
            'button': (80, 80, 80),
            'button_hover': (100, 100, 100),
            'button_active': (120, 120, 120),
            'text': (255, 255, 255),
            'text_dim': (180, 180, 180),
            'border': (120, 120, 120),
            'selected': (70, 130, 180),
            'success': (46, 125, 50),
            'error': (183, 28, 28),
            'warning': (255, 152, 0)
        }
        
        # 存档列表和选择
        self.saves_list = []
        self.selected_index = -1
        self.scroll_offset = 0
        self.max_visible_saves = 15
        
        # 按钮
        self.buttons = []
        self.close_button = None
        
        # 输入状态
        self.input_active = False
        self.input_text = ""
        self.input_prompt = ""
        
        # 加载存档列表
        self.refresh_saves_list()
    
    def show_save_dialog(self, game_state: GameState, callback: Callable = None):
        """显示保存对话框"""
        self.mode = "save"
        self.current_game_state = game_state
        self.on_save_callback = callback
        self.is_open = True
        self.create_buttons()
    
    def show_load_dialog(self, callback: Callable = None):
        """显示加载对话框"""
        self.mode = "load"
        self.current_game_state = None
        self.on_load_callback = callback
        self.is_open = True
        self.create_buttons()
    
    def create_buttons(self):
        """创建按钮"""
        self.buttons = []
        button_y = self.window_rect.bottom - 60
        
        if self.mode == "save":
            # 保存模式按钮
            self.buttons.append({
                'rect': pygame.Rect(self.window_rect.right - 450, button_y, 100, 30),
                'text': '新建存档',
                'action': 'new_save',
                'enabled': True
            })
            self.buttons.append({
                'rect': pygame.Rect(self.window_rect.right - 340, button_y, 100, 30),
                'text': '覆盖存档',
                'action': 'save_game',
                'enabled': self.selected_index >= 0
            })
        else:
            # 加载模式按钮
            self.buttons.append({
                'rect': pygame.Rect(self.window_rect.right - 450, button_y, 100, 30),
                'text': '加载游戏',
                'action': 'load_game',
                'enabled': self.selected_index >= 0
            })
        
        # 通用按钮
        self.buttons.append({
            'rect': pygame.Rect(self.window_rect.right - 230, button_y, 80, 30),
            'text': '删除',
            'action': 'delete_save',
            'enabled': self.selected_index >= 0
        })
        self.buttons.append({
            'rect': pygame.Rect(self.window_rect.right - 140, button_y, 60, 30),
            'text': '刷新',
            'action': 'refresh',
            'enabled': True
        })
        self.buttons.append({
            'rect': pygame.Rect(self.window_rect.right - 70, button_y, 50, 30),
            'text': '关闭',
            'action': 'close',
            'enabled': True
        })
    
    def refresh_saves_list(self):
        """刷新存档列表"""
        try:
            self.saves_list = self.save_system.list_saves()
            self.selected_index = -1
            self.scroll_offset = 0
        except Exception as e:
            print(f"刷新存档列表失败: {e}")
            self.saves_list = []
    
    def handle_event(self, event):
        """处理事件"""
        if not self.is_open:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
                return True
            elif self.input_active:
                return self.handle_input_event(event)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键
                if self.window_rect.collidepoint(event.pos):
                    return self.handle_click(event.pos)
        
        elif event.type == pygame.MOUSEWHEEL:
            if self.window_rect.collidepoint(pygame.mouse.get_pos()):
                self.handle_scroll(event.y)
                return True
        
        return True  # 拦截所有事件
    
    def handle_input_event(self, event):
        """处理输入事件"""
        if event.key == pygame.K_RETURN:
            self.finish_input()
        elif event.key == pygame.K_ESCAPE:
            self.cancel_input()
        elif event.key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]
        else:
            if event.unicode.isprintable():
                self.input_text += event.unicode
        return True
    
    def handle_click(self, pos):
        """处理点击事件"""
        # 检查输入对话框按钮
        if self.input_active:
            return self.handle_input_click(pos)
        
        # 检查存档列表点击
        list_rect = pygame.Rect(
            self.window_rect.x + 20,
            self.window_rect.y + 80,
            self.window_rect.width - 300,
            self.window_rect.height - 180
        )
        
        if list_rect.collidepoint(pos):
            # 计算点击的存档索引
            relative_y = pos[1] - list_rect.y
            item_height = 35
            clicked_index = (relative_y // item_height) + self.scroll_offset
            
            if 0 <= clicked_index < len(self.saves_list):
                self.selected_index = clicked_index
                self.create_buttons()  # 更新按钮状态
            return True
        
        # 检查按钮点击
        for button in self.buttons:
            if button['rect'].collidepoint(pos) and button['enabled']:
                self.handle_button_click(button['action'])
                return True
        
        return True
    
    def handle_input_click(self, pos):
        """处理输入对话框点击"""
        dialog_rect = pygame.Rect(
            self.window_rect.centerx - 200,
            self.window_rect.centery - 80,
            400,
            160
        )
        
        confirm_rect = pygame.Rect(dialog_rect.x + 80, dialog_rect.y + 110, 80, 30)
        cancel_rect = pygame.Rect(dialog_rect.x + 240, dialog_rect.y + 110, 80, 30)
        
        if confirm_rect.collidepoint(pos):
            self.finish_input()
            return True
        elif cancel_rect.collidepoint(pos):
            self.cancel_input()
            return True
        
        return True
    
    def handle_scroll(self, scroll_y):
        """处理滚动事件"""
        max_scroll = max(0, len(self.saves_list) - self.max_visible_saves)
        self.scroll_offset = max(0, min(max_scroll, self.scroll_offset - scroll_y))
    
    def handle_button_click(self, action):
        """处理按钮点击"""
        if action == 'close':
            self.close()
        elif action == 'refresh':
            self.refresh_saves_list()
            self.create_buttons()
        elif action == 'new_save':
            self.start_input("请输入存档名称:", f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        elif action == 'save_game':
            if self.selected_index >= 0:
                save_info = self.saves_list[self.selected_index]
                self.save_game(save_info['save_name'])
        elif action == 'load_game':
            if self.selected_index >= 0:
                save_info = self.saves_list[self.selected_index]
                self.load_game(save_info['save_name'])
        elif action == 'delete_save':
            if self.selected_index >= 0:
                save_info = self.saves_list[self.selected_index]
                self.delete_save(save_info['save_name'])
    
    def start_input(self, prompt, default_text=""):
        """开始输入"""
        self.input_active = True
        self.input_prompt = prompt
        self.input_text = default_text
    
    def finish_input(self):
        """完成输入"""
        if self.input_text.strip():
            if "存档名称" in self.input_prompt:
                self.save_game(self.input_text.strip())
        self.cancel_input()
    
    def cancel_input(self):
        """取消输入"""
        self.input_active = False
        self.input_prompt = ""
        self.input_text = ""
    
    def save_game(self, save_name):
        """保存游戏"""
        try:
            result = self.save_system.save_game(self.current_game_state, save_name, "")
            if result["success"]:
                print(f"✅ 保存成功: {save_name}")
                if self.on_save_callback:
                    self.on_save_callback(result)
                self.close()
            else:
                print(f"❌ 保存失败: {result['error']}")
        except Exception as e:
            print(f"❌ 保存异常: {e}")
    
    def load_game(self, save_name):
        """加载游戏"""
        try:
            result = self.save_system.load_game(save_name)
            if result["success"]:
                print(f"✅ 加载成功: {save_name}")
                if self.on_load_callback:
                    self.on_load_callback(result)
                self.close()
            else:
                print(f"❌ 加载失败: {result['error']}")
        except Exception as e:
            print(f"❌ 加载异常: {e}")
    
    def delete_save(self, save_name):
        """删除存档"""
        try:
            result = self.save_system.delete_save(save_name)
            if result["success"]:
                print(f"✅ 删除成功: {save_name}")
                self.refresh_saves_list()
                self.create_buttons()
            else:
                print(f"❌ 删除失败: {result['error']}")
        except Exception as e:
            print(f"❌ 删除异常: {e}")
    
    def draw(self):
        """绘制窗口"""
        if not self.is_open:
            return
        
        # 绘制半透明背景
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # 绘制窗口背景
        pygame.draw.rect(self.screen, self.colors['window'], self.window_rect)
        pygame.draw.rect(self.screen, self.colors['border'], self.window_rect, 2)
        
        # 绘制标题
        title = "保存游戏" if self.mode == "save" else "加载存档"
        title_text = self.font_large.render(title, True, self.colors['text'])
        title_rect = title_text.get_rect(centerx=self.window_rect.centerx, y=self.window_rect.y + 20)
        self.screen.blit(title_text, title_rect)
        
        # 绘制存档列表
        self.draw_saves_list()
        
        # 绘制存档详情
        self.draw_save_details()
        
        # 绘制按钮
        self.draw_buttons()
        
        # 绘制输入框
        if self.input_active:
            self.draw_input_dialog()
    
    def draw_saves_list(self):
        """绘制存档列表"""
        list_rect = pygame.Rect(
            self.window_rect.x + 20,
            self.window_rect.y + 80,
            self.window_rect.width - 300,
            self.window_rect.height - 180
        )
        
        # 绘制列表背景
        pygame.draw.rect(self.screen, self.colors['background'], list_rect)
        pygame.draw.rect(self.screen, self.colors['border'], list_rect, 1)
        
        # 绘制列表标题
        title_text = self.font_medium.render("存档列表", True, self.colors['text'])
        self.screen.blit(title_text, (list_rect.x + 10, list_rect.y - 25))
        
        # 绘制存档项
        item_height = 35
        visible_saves = self.saves_list[self.scroll_offset:self.scroll_offset + self.max_visible_saves]
        
        for i, save_info in enumerate(visible_saves):
            actual_index = i + self.scroll_offset
            item_rect = pygame.Rect(
                list_rect.x + 5,
                list_rect.y + 5 + i * item_height,
                list_rect.width - 10,
                item_height - 2
            )
            
            # 绘制选中背景
            if actual_index == self.selected_index:
                pygame.draw.rect(self.screen, self.colors['selected'], item_rect)
            
            # 绘制存档信息
            save_name = save_info['save_name']
            created_time = save_info['created_time'].strftime("%Y-%m-%d %H:%M:%S")
            size_kb = save_info['size'] // 1024
            
            name_text = self.font_small.render(save_name, True, self.colors['text'])
            info_text = self.font_small.render(
                f"{created_time} | {size_kb}KB", 
                True, self.colors['text_dim']
            )
            
            self.screen.blit(name_text, (item_rect.x + 5, item_rect.y + 2))
            self.screen.blit(info_text, (item_rect.x + 5, item_rect.y + 18))
        
        # 绘制滚动条
        if len(self.saves_list) > self.max_visible_saves:
            self.draw_scrollbar(list_rect)
    
    def draw_scrollbar(self, list_rect):
        """绘制滚动条"""
        scrollbar_rect = pygame.Rect(
            list_rect.right - 15,
            list_rect.y,
            15,
            list_rect.height
        )
        
        pygame.draw.rect(self.screen, self.colors['background'], scrollbar_rect)
        
        # 计算滚动条位置
        total_items = len(self.saves_list)
        visible_items = self.max_visible_saves
        scroll_ratio = self.scroll_offset / max(1, total_items - visible_items)
        
        handle_height = max(20, int(scrollbar_rect.height * visible_items / total_items))
        handle_y = scrollbar_rect.y + int((scrollbar_rect.height - handle_height) * scroll_ratio)
        
        handle_rect = pygame.Rect(
            scrollbar_rect.x + 2,
            handle_y,
            scrollbar_rect.width - 4,
            handle_height
        )
        
        pygame.draw.rect(self.screen, self.colors['button'], handle_rect)
    
    def draw_save_details(self):
        """绘制存档详情"""
        details_rect = pygame.Rect(
            self.window_rect.right - 270,
            self.window_rect.y + 80,
            250,
            self.window_rect.height - 180
        )
        
        pygame.draw.rect(self.screen, self.colors['background'], details_rect)
        pygame.draw.rect(self.screen, self.colors['border'], details_rect, 1)
        
        # 绘制详情标题
        title_text = self.font_medium.render("存档详情", True, self.colors['text'])
        self.screen.blit(title_text, (details_rect.x + 10, details_rect.y - 25))
        
        if self.selected_index >= 0 and self.selected_index < len(self.saves_list):
            save_info = self.saves_list[self.selected_index]
            y_offset = details_rect.y + 10
            
            # 显示详细信息
            details = [
                f"名称: {save_info['save_name']}",
                f"创建时间:",
                f"  {save_info['created_time'].strftime('%Y-%m-%d %H:%M:%S')}",
                f"文件大小: {save_info['size'] // 1024}KB",
                f"玩家数量: {save_info.get('player_count', '未知')}",
                f"当前回合: {save_info.get('turn_count', '未知')}",
                f"当前玩家: {save_info.get('current_player', '未知')}"
            ]
            
            for detail in details:
                if y_offset < details_rect.bottom - 20:
                    text_surface = self.font_small.render(detail, True, self.colors['text'])
                    self.screen.blit(text_surface, (details_rect.x + 10, y_offset))
                    y_offset += 18
    
    def draw_buttons(self):
        """绘制按钮"""
        mouse_pos = pygame.mouse.get_pos()
        
        for button in self.buttons:
            # 确定按钮颜色
            if not button['enabled']:
                color = self.colors['button']
                text_color = self.colors['text_dim']
            elif button['rect'].collidepoint(mouse_pos):
                color = self.colors['button_hover']
                text_color = self.colors['text']
            else:
                color = self.colors['button']
                text_color = self.colors['text']
            
            # 绘制按钮
            pygame.draw.rect(self.screen, color, button['rect'])
            pygame.draw.rect(self.screen, self.colors['border'], button['rect'], 1)
            
            # 绘制按钮文字
            text_surface = self.font_small.render(button['text'], True, text_color)
            text_rect = text_surface.get_rect(center=button['rect'].center)
            self.screen.blit(text_surface, text_rect)
    
    def draw_input_dialog(self):
        """绘制输入对话框"""
        dialog_rect = pygame.Rect(
            self.window_rect.centerx - 200,
            self.window_rect.centery - 80,
            400,
            160
        )
        
        # 绘制对话框背景
        pygame.draw.rect(self.screen, self.colors['window'], dialog_rect)
        pygame.draw.rect(self.screen, self.colors['border'], dialog_rect, 2)
        
        # 绘制提示文字
        prompt_text = self.font_medium.render(self.input_prompt, True, self.colors['text'])
        prompt_rect = prompt_text.get_rect(centerx=dialog_rect.centerx, y=dialog_rect.y + 20)
        self.screen.blit(prompt_text, prompt_rect)
        
        # 绘制输入框
        input_rect = pygame.Rect(
            dialog_rect.x + 20,
            dialog_rect.y + 60,
            dialog_rect.width - 40,
            30
        )
        pygame.draw.rect(self.screen, self.colors['background'], input_rect)
        pygame.draw.rect(self.screen, self.colors['border'], input_rect, 1)
        
        # 绘制输入文字和光标
        cursor = "|" if (pygame.time.get_ticks() // 500) % 2 else ""
        input_surface = self.font_medium.render(self.input_text + cursor, True, self.colors['text'])
        self.screen.blit(input_surface, (input_rect.x + 5, input_rect.y + 5))
        
        # 绘制确认和取消按钮
        confirm_rect = pygame.Rect(dialog_rect.x + 80, dialog_rect.y + 110, 80, 30)
        cancel_rect = pygame.Rect(dialog_rect.x + 240, dialog_rect.y + 110, 80, 30)
        
        mouse_pos = pygame.mouse.get_pos()
        
        # 确认按钮
        confirm_color = self.colors['button_hover'] if confirm_rect.collidepoint(mouse_pos) else self.colors['button']
        pygame.draw.rect(self.screen, confirm_color, confirm_rect)
        pygame.draw.rect(self.screen, self.colors['border'], confirm_rect, 1)
        confirm_text = self.font_small.render("确认", True, self.colors['text'])
        confirm_text_rect = confirm_text.get_rect(center=confirm_rect.center)
        self.screen.blit(confirm_text, confirm_text_rect)
        
        # 取消按钮
        cancel_color = self.colors['button_hover'] if cancel_rect.collidepoint(mouse_pos) else self.colors['button']
        pygame.draw.rect(self.screen, cancel_color, cancel_rect)
        pygame.draw.rect(self.screen, self.colors['border'], cancel_rect, 1)
        cancel_text = self.font_small.render("取消", True, self.colors['text'])
        cancel_text_rect = cancel_text.get_rect(center=cancel_rect.center)
        self.screen.blit(cancel_text, cancel_text_rect)
    
    def close(self):
        """关闭窗口"""
        self.is_open = False
        if self.on_close_callback:
            self.on_close_callback()
    
    def set_callbacks(self, on_save=None, on_load=None, on_close=None):
        """设置回调函数"""
        if on_save:
            self.on_save_callback = on_save
        if on_load:
            self.on_load_callback = on_load
        if on_close:
            self.on_close_callback = on_close 