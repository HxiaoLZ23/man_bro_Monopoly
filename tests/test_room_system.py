#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试房间系统
"""

import pygame
import sys
import os

# 添加src路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.enhanced_multiplayer_window import EnhancedMultiplayerWindow

def main():
    """主函数"""
    print("🚀 启动房间系统测试...")
    
    try:
        # 创建并运行增强版多人游戏窗口
        window = EnhancedMultiplayerWindow()
        window.run()
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        print("✅ 测试结束")

if __name__ == "__main__":
    main() 