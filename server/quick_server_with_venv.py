# -*- coding: utf-8 -*-
"""
大富翁快速服务器 - 自动激活虚拟环境版本
"""

import os
import sys
import subprocess

def activate_venv_and_run():
    """激活虚拟环境并运行服务器"""
    print("🔧 正在激活虚拟环境...")
    
    # 检查是否已在虚拟环境中
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 已在虚拟环境中")
    else:
        print("⚠️ 不在虚拟环境中，尝试激活...")
        
        # 尝试激活虚拟环境
        venv_path = os.path.join(os.getcwd(), "DaFuWeng")
        if os.path.exists(venv_path):
            # Windows环境下激活虚拟环境并运行服务器
            python_exe = os.path.join(venv_path, "Scripts", "python.exe")
            if os.path.exists(python_exe):
                print(f"🚀 使用虚拟环境Python: {python_exe}")
                # 使用虚拟环境中的Python运行服务器
                subprocess.run([python_exe, "quick_server.py"])
                return
            else:
                print("❌ 虚拟环境Python不存在")
        else:
            print("❌ 虚拟环境目录不存在")
    
    # 如果已在虚拟环境中或无法激活，直接运行
    import quick_server
    
def safe_input(prompt="按 Enter 键继续..."):
    try:
        return input(prompt)
    except:
        print("\n程序退出")
        return ""

if __name__ == "__main__":
    try:
        activate_venv_and_run()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
    finally:
        safe_input("按 Enter 键关闭...") 