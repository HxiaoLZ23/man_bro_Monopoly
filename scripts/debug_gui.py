#!/usr/bin/env python3
"""
调试GUI启动脚本
"""
import sys
import os
import traceback

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

def main():
    """主函数"""
    print("🎲 启动大富翁游戏图形界面...")
    
    try:
        print("📦 导入模块...")
        from src.ui.main_window import MainWindow
        print("✅ 模块导入成功")
        
        print("🏗️ 创建主窗口...")
        window = MainWindow()
        print("✅ 主窗口创建成功")
        
        print("🚀 开始运行游戏循环...")
        window.run()
        print("✅ 游戏循环结束")
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        input("按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main() 