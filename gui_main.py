"""
大富翁游戏 - 图形界面主程序
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

from src.ui.main_window import MainWindow


def main():
    """主函数"""
    try:
        print("🎲 启动大富翁游戏图形界面...")
        
        # 创建并运行主窗口
        window = MainWindow()
        window.run()
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")
        sys.exit(1)


if __name__ == "__main__":
    main() 