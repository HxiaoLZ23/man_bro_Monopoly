#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大富翁联机游戏服务器 - 修复版
防止控制台窗口秒关
"""

import asyncio
import json
import logging
import uuid
import traceback

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import websockets
    print(f"✅ websockets {websockets.__version__} 加载成功")
except ImportError:
    print("❌ websockets 模块未安装")
    print("请运行: pip install websockets")
    input("按 Enter 键关闭...")
    exit(1)

class SimpleGameServer:
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients = {}
        self.rooms = {}
        self.is_running = False
    
    async def find_available_port(self, start_port: int = 8765, max_tries: int = 10):
        """寻找可用端口"""
        import socket
        
        for i in range(max_tries):
            test_port = start_port + i
            try:
                # 测试端口是否可用
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind((self.host, test_port))
                return test_port
            except OSError:
                print(f"⚠️ 端口 {test_port} 被占用，尝试下一个...")
                continue
        
        raise Exception(f"无法找到可用端口（尝试了 {start_port} 到 {start_port + max_tries - 1}）")
    
    async def start(self):
        """启动服务器"""
        try:
            # 寻找可用端口
            available_port = await self.find_available_port(self.port)
            self.port = available_port
            
            print(f"🚀 启动服务器 - {self.host}:{self.port}")
            
            # 启动websocket服务器
            server = await websockets.serve(
                self.handle_client,
                self.host,
                self.port,
                ping_interval=20,
                ping_timeout=10
            )
            
            self.is_running = True
            print(f"✅ 服务器启动成功 - {self.host}:{self.port}")
            print("🎮 等待客户端连接...")
            print("💡 按 Ctrl+C 停止服务器")
            
            # 保持服务器运行
            await server.wait_closed()
            
        except Exception as e:
            print(f"❌ 服务器启动失败: {e}")
            raise

    async def handle_client(self, websocket):
        """处理客户端连接"""
        client_id = str(uuid.uuid4())[:8]
        
        try:
            # 注册客户端
            self.clients[client_id] = {
                "websocket": websocket,
                "room_id": None,
                "player_name": None
            }
            
            print(f"👤 客户端连接: {client_id}")
            
            # 发送连接成功消息
            await self.send_to_client(client_id, {
                "type": "success",
                "message": "连接成功",
                "client_id": client_id
            })
            
            # 处理消息
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(client_id, data)
                except json.JSONDecodeError:
                    await self.send_error(client_id, "无效的JSON格式")
                except Exception as e:
                    print(f"处理消息错误: {e}")
                    await self.send_error(client_id, str(e))
        
        except websockets.exceptions.ConnectionClosed:
            print(f"👋 客户端断开: {client_id}")
        except Exception as e:
            print(f"客户端处理错误: {e}")
        finally:
            # 清理客户端
            if client_id in self.clients:
                del self.clients[client_id]

    async def handle_message(self, client_id: str, data: dict):
        """处理客户端消息"""
        message_type = data.get("type", "")
        
        if message_type == "heartbeat":
            await self.send_to_client(client_id, {"type": "heartbeat", "status": "ok"})
        elif message_type == "test":
            await self.send_to_client(client_id, {"type": "test_response", "message": "服务器连接正常"})
        else:
            await self.send_error(client_id, f"未知消息类型: {message_type}")

    async def send_to_client(self, client_id: str, message: dict):
        """发送消息给客户端"""
        if client_id in self.clients:
            websocket = self.clients[client_id]["websocket"]
            try:
                await websocket.send(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                print(f"发送消息失败: {e}")

    async def send_error(self, client_id: str, error_msg: str):
        """发送错误消息"""
        await self.send_to_client(client_id, {
            "type": "error",
            "message": error_msg
        })

async def main():
    """主函数"""
    print("=" * 60)
    print("🎮 大富翁联机游戏服务器 - 修复版")
    print("=" * 60)
    
    server = SimpleGameServer()
    
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n⌨️ 收到停止信号")
    except Exception as e:
        print(f"❌ 服务器运行错误: {e}")
        traceback.print_exc()
    finally:
        print("\n👋 服务器已退出")

def main_wrapper():
    """主函数包装器，防止控制台窗口秒关"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 用户手动停止")
    except Exception as e:
        print(f"❌ 程序错误: {e}")
        traceback.print_exc()
    finally:
        print("\n" + "=" * 40)
        print("程序已结束")
        try:
            input("按 Enter 键关闭窗口...")
        except (EOFError, KeyboardInterrupt):
            print("强制退出")

if __name__ == "__main__":
    main_wrapper() 