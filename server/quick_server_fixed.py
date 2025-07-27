#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大富翁快速服务器 - 修复版本
"""

import asyncio
import json
import sys
import traceback
import time

def safe_input(prompt="按 Enter 键继续..."):
    """安全的输入函数，防止EOFError"""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\n程序退出")
        return ""

def find_available_port(host="localhost", start_port=8765):
    """查找可用端口"""
    import socket
    
    for port in range(start_port, start_port + 20):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                return port
        except OSError:
            print(f"端口 {port} 被占用，尝试下一个...")
    
    return None

async def simple_server(host="localhost", port=8765):
    """简单的websocket服务器"""
    try:
        import websockets
        print(f"✅ websockets版本: {websockets.__version__}")
    except ImportError:
        print("❌ 缺少websockets模块")
        print("请运行: pip install websockets")
        print("")
        print("💡 提示：如果您使用的是虚拟环境，请确保：")
        print("1. 激活虚拟环境: DaFuWeng\\Scripts\\activate")
        print("2. 在虚拟环境中安装: pip install websockets")
        print("3. 在虚拟环境中运行服务器")
        print("")
        print("🔍 当前Python环境信息：")
        print(f"Python路径: {sys.executable}")
        print(f"Python版本: {sys.version}")
        
        # 尝试自动安装websockets
        print("\n🚀 尝试自动安装websockets...")
        try:
            import subprocess
            result = subprocess.run([sys.executable, "-m", "pip", "install", "websockets"], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✅ websockets安装成功！正在重新启动服务器...")
                # 重新导入websockets
                import importlib
                import websockets
                print(f"✅ websockets版本: {websockets.__version__}")
            else:
                print(f"❌ 自动安装失败: {result.stderr}")
                safe_input()
                return
        except Exception as e:
            print(f"❌ 自动安装出错: {e}")
            safe_input()
            return
    
    # 查找可用端口
    available_port = find_available_port(host, port)
    if not available_port:
        print("❌ 无法找到可用端口")
        safe_input()
        return
    
    print(f"🚀 启动服务器: {host}:{available_port}")
    
    async def handle_client(websocket, path=None):
        """处理客户端连接"""
        client_id = f"client_{id(websocket)}"
        print(f"👤 客户端连接: {client_id}")
        
        try:
            # 发送欢迎消息 - 使用正确的NetworkMessage格式
            welcome_message = {
                "message_type": "success",
                "data": {
                    "message": "欢迎连接大富翁服务器！",
                    "client_id": client_id
                },
                "timestamp": time.time(),
                "sender_id": "server"
            }
            await websocket.send(json.dumps(welcome_message, ensure_ascii=False))
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    print(f"📨 收到消息: {data}")
                    
                    # 简单回应 - 使用正确的NetworkMessage格式
                    response = {
                        "message_type": "success",
                        "data": {
                            "message": "服务器收到消息",
                            "received": data
                        },
                        "timestamp": time.time(),
                        "sender_id": "server"
                    }
                    await websocket.send(json.dumps(response, ensure_ascii=False))
                    
                except json.JSONDecodeError:
                    error_message = {
                        "message_type": "error",
                        "data": {
                            "error": "无效的JSON格式"
                        },
                        "timestamp": time.time(),
                        "sender_id": "server"
                    }
                    await websocket.send(json.dumps(error_message, ensure_ascii=False))
        
        except websockets.exceptions.ConnectionClosed:
            print(f"👋 客户端断开: {client_id}")
        except Exception as e:
            print(f"❌ 处理客户端错误: {e}")
    
    try:
        print("🎮 服务器启动中...")
        async with websockets.serve(handle_client, host, available_port):
            print(f"✅ 服务器运行在 {host}:{available_port}")
            print("💡 按 Ctrl+C 停止服务器")
            print("🔗 客户端可以连接到: ws://localhost:" + str(available_port))
            
            # 保持运行
            await asyncio.Future()  # run forever
    
    except Exception as e:
        print(f"❌ 服务器错误: {e}")
        traceback.print_exc()

def main():
    """主函数"""
    print("=" * 50)
    print("🎮 大富翁快速服务器 - 修复版")
    print("=" * 50)
    
    try:
        asyncio.run(simple_server())
    except KeyboardInterrupt:
        print("\n⌨️ 用户停止服务器")
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        traceback.print_exc()
    finally:
        print("\n🔚 服务器已停止")
        safe_input("按 Enter 键关闭...")

if __name__ == "__main__":
    main() 