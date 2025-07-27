"""
全局字体管理器
统一管理所有界面的中文字体配置，避免重复设置和显示异常
"""

import pygame
import os
import sys
from typing import Dict, Optional, List


class FontManager:
    """全局字体管理器"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FontManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not FontManager._initialized:
            self._fonts = {}
            self._font_path = None
            self._backup_fonts = {}
            # 延迟初始化，等待pygame初始化
            FontManager._initialized = True
    
    def _ensure_initialized(self):
        """确保字体已经初始化"""
        if not self._fonts:
            # 检查pygame是否已初始化
            if not pygame.get_init():
                print("⚠️ pygame未初始化，正在初始化...")
                pygame.init()
            self._init_fonts()
    
    def _get_font_paths(self) -> List[str]:
        """获取中文字体路径列表（按优先级排序）"""
        font_paths = []
        
        # Windows字体路径
        if sys.platform == "win32":
            windir = os.environ.get("WINDIR", "C:\\Windows")
            font_dir = os.path.join(windir, "Fonts")
            
            # 按优先级排序的中文字体
            windows_fonts = [
                "msyh.ttc",      # 微软雅黑
                "msyhbd.ttc",    # 微软雅黑 Bold
                "simhei.ttf",    # 黑体
                "simsun.ttc",    # 宋体
                "simkai.ttf",    # 楷体
                "simfang.ttf",   # 仿宋
                "STXIHEI.TTF",   # 华文细黑
                "STZHONGS.TTF",  # 华文中宋
            ]
            
            for font_file in windows_fonts:
                path = os.path.join(font_dir, font_file)
                if os.path.exists(path):
                    font_paths.append(path)
        
        # macOS字体路径
        elif sys.platform == "darwin":
            mac_fonts = [
                "/System/Library/Fonts/PingFang.ttc",           # 苹方
                "/System/Library/Fonts/Helvetica.ttc",         # Helvetica
                "/Library/Fonts/Arial Unicode MS.ttf",         # Arial Unicode MS
                "/System/Library/Fonts/STHeiti Light.ttc",     # 华文黑体
                "/System/Library/Fonts/STSong.ttf",            # 华文宋体
            ]
            
            for path in mac_fonts:
                if os.path.exists(path):
                    font_paths.append(path)
        
        # Linux字体路径
        else:
            linux_fonts = [
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",           # 文泉驿正黑
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",        # 文泉驿微米黑
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",       # DejaVu Sans
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Liberation Sans
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", # Noto Sans CJK
            ]
            
            for path in linux_fonts:
                if os.path.exists(path):
                    font_paths.append(path)
        
        return font_paths
    
    def _get_system_fonts(self) -> List[str]:
        """获取系统字体名称列表"""
        system_fonts = []
        
        if sys.platform == "win32":
            # Windows系统字体
            system_fonts = [
                'microsoftyaheimicrosoftyaheiui',  # 微软雅黑
                'simhei',                          # 黑体
                'simsun',                          # 宋体
                'kaiti',                           # 楷体
                'fangsong',                        # 仿宋
            ]
        elif sys.platform == "darwin":
            # macOS系统字体
            system_fonts = [
                'pingfangsc',      # 苹方简
                'pingfangtc',      # 苹方繁
                'stheitisc',       # 华文黑体简
                'stheititc',       # 华文黑体繁
                'arial',           # Arial
                'helvetica',       # Helvetica
            ]
        else:
            # Linux系统字体
            system_fonts = [
                'wqyzenhei',       # 文泉驿正黑
                'wqymicrohei',     # 文泉驿微米黑
                'notosanscjk',     # Noto Sans CJK
                'dejavusans',      # DejaVu Sans
                'liberationsans',  # Liberation Sans
            ]
        
        return system_fonts
    
    def _init_fonts(self):
        """初始化字体"""
        print("🔤 初始化全局字体管理器...")
        
        # 确保pygame已经初始化
        if not pygame.get_init():
            pygame.init()
        
        # 字体大小配置
        font_sizes = {
            "tiny": 12,
            "small": 16,
            "normal": 24,
            "subtitle": 32,
            "title": 48,
            "large": 64,
            "body": 16,
            "heading": 24,
            "subheading": 18,
        }
        
        # 尝试加载文件字体
        font_paths = self._get_font_paths()
        
        for font_path in font_paths:
            try:
                # 测试加载字体
                test_font = pygame.font.Font(font_path, 24)
                self._font_path = font_path
                print(f"✅ 成功加载字体文件: {os.path.basename(font_path)}")
                break
            except Exception as e:
                print(f"❌ 字体加载失败 {os.path.basename(font_path)}: {e}")
                continue
        
        # 如果文件字体加载失败，尝试系统字体
        if not self._font_path:
            system_fonts = self._get_system_fonts()
            
            for font_name in system_fonts:
                try:
                    test_font = pygame.font.SysFont(font_name, 24)
                    if test_font:
                        self._font_path = font_name
                        print(f"✅ 成功加载系统字体: {font_name}")
                        break
                except Exception as e:
                    print(f"❌ 系统字体加载失败 {font_name}: {e}")
                    continue
        
        # 创建所有大小的字体对象
        for name, size in font_sizes.items():
            try:
                if self._font_path and os.path.exists(self._font_path):
                    # 使用文件字体
                    self._fonts[name] = pygame.font.Font(self._font_path, size)
                elif self._font_path:
                    # 使用系统字体
                    self._fonts[name] = pygame.font.SysFont(self._font_path, size)
                else:
                    # 使用默认字体
                    self._fonts[name] = pygame.font.Font(None, size)
                    
                # 创建备用字体（默认字体）
                self._backup_fonts[name] = pygame.font.Font(None, size)
                
            except Exception as e:
                print(f"❌ 创建字体 {name}({size}) 失败: {e}")
                # 使用默认字体作为备选
                self._fonts[name] = pygame.font.Font(None, size)
                self._backup_fonts[name] = pygame.font.Font(None, size)
        
        if self._font_path:
            print(f"✅ 字体管理器初始化完成，使用字体: {os.path.basename(self._font_path) if os.path.exists(self._font_path or '') else self._font_path}")
        else:
            print("⚠️ 未找到合适的中文字体，使用默认字体")
    
    def get_font(self, size_name: str = "normal") -> pygame.font.Font:
        """
        获取指定大小的字体
        
        Args:
            size_name: 字体大小名称 ("tiny", "small", "normal", "subtitle", "title", "large", 
                      "body", "heading", "subheading")
        
        Returns:
            pygame.font.Font对象
        """
        self._ensure_initialized()
        return self._fonts.get(size_name, self._fonts.get("normal"))
    
    def get_font_by_size(self, size: int) -> pygame.font.Font:
        """
        根据像素大小获取字体
        
        Args:
            size: 字体大小（像素）
        
        Returns:
            pygame.font.Font对象
        """
        self._ensure_initialized()
        try:
            if self._font_path and os.path.exists(self._font_path):
                return pygame.font.Font(self._font_path, size)
            elif self._font_path:
                return pygame.font.SysFont(self._font_path, size)
            else:
                return pygame.font.Font(None, size)
        except Exception:
            return pygame.font.Font(None, size)
    
    def render_text(self, text: str, size_name: str = "normal", 
                    color: tuple = (255, 255, 255), antialias: bool = True) -> pygame.Surface:
        """
        渲染文本
        
        Args:
            text: 要渲染的文本
            size_name: 字体大小名称
            color: 文本颜色 (R, G, B)
            antialias: 是否开启抗锯齿
        
        Returns:
            渲染后的Surface对象
        """
        self._ensure_initialized()
        font = self.get_font(size_name)
        try:
            return font.render(text, antialias, color)
        except Exception as e:
            print(f"⚠️ 文本渲染失败，使用备用字体: {e}")
            backup_font = self._backup_fonts.get(size_name, self._backup_fonts.get("normal"))
            return backup_font.render(text, antialias, color)
    
    def get_text_size(self, text: str, size_name: str = "normal") -> tuple:
        """
        获取文本尺寸
        
        Args:
            text: 文本内容
            size_name: 字体大小名称
        
        Returns:
            (width, height) 元组
        """
        self._ensure_initialized()
        font = self.get_font(size_name)
        return font.size(text)
    
    def get_font_path(self) -> Optional[str]:
        """获取当前使用的字体路径"""
        self._ensure_initialized()
        return self._font_path
    
    def get_available_sizes(self) -> List[str]:
        """获取可用的字体大小名称列表"""
        self._ensure_initialized()
        return list(self._fonts.keys())
    
    def reload_fonts(self):
        """重新加载字体（用于调试或配置更改后）"""
        print("🔄 重新加载字体...")
        self._fonts.clear()
        self._backup_fonts.clear()
        self._font_path = None
        self._init_fonts()


# 创建全局字体管理器实例
font_manager = FontManager()


def get_font(size_name: str = "normal") -> pygame.font.Font:
    """快捷方式：获取字体"""
    return font_manager.get_font(size_name)


def get_font_by_size(size: int) -> pygame.font.Font:
    """快捷方式：根据大小获取字体"""
    return font_manager.get_font_by_size(size)


def render_text(text: str, size_name: str = "normal", 
                color: tuple = (255, 255, 255), antialias: bool = True) -> pygame.Surface:
    """快捷方式：渲染文本"""
    return font_manager.render_text(text, size_name, color, antialias)


def get_text_size(text: str, size_name: str = "normal") -> tuple:
    """快捷方式：获取文本尺寸"""
    return font_manager.get_text_size(text, size_name) 