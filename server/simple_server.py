#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大富翁联机游戏服务器 - 简化实现
"""
import asyncio
import json
import websockets
import logging
from typing import Dict, Set

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleGameServer:
    """简化游戏服务器"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Dict = {}
        self.rooms: Dict = {}
        self.is_running = False
    
    async def start(self):
        """启动服务器"""
        port = self.port
        max_retries = 5
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🚀 启动简化游戏服务器 - {self.host}:{port}")
                
                async with websockets.serve(
                    self.handle_client,
                    self.host,
                    port,
                    ping_interval=20,
                    ping_timeout=10
                ):
                    self.is_running = True
                    self.port = port  # 更新实际使用的端口
                    logger.info(f"✅ 服务器启动成功 - {self.host}:{port}")
                    
                    # 保持服务器运行
                    await asyncio.Future()  # run forever
                    
            except OSError as e:
                if e.errno == 10048:  # 端口被占用
                    port += 1
                    print(f"⚠️ 端口 {port-1} 被占用，尝试端口 {port}")
                    if attempt == max_retries - 1:
                        raise Exception(f"无法找到可用端口（尝试了 {self.port} 到 {port}）")
                else:
                    raise
            except Exception as e:
                logger.error(f"❌ 服务器启动失败: {e}")
                raise
    
    async def handle_client(self, websocket):
        """处理客户端连接"""
        client_id = None
        try:
            # 生成客户端ID
            import uuid
            client_id = str(uuid.uuid4())[:8]
            
            # 注册客户端
            self.clients[client_id] = {
                "websocket": websocket,
                "room_id": None,
                "player_name": None
            }
            
            logger.info(f"👤 客户端连接: {client_id}")
            
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
                    logger.error(f"处理消息错误: {e}")
                    await self.send_error(client_id, str(e))
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"👋 客户端断开: {client_id}")
        except Exception as e:
            logger.error(f"客户端处理错误: {e}")
        finally:
            # 清理客户端
            if client_id and client_id in self.clients:
                del self.clients[client_id]
    
    async def handle_message(self, client_id: str, data: dict):
        """处理客户端消息"""
        message_type = data.get("type", "")
        
        if message_type == "heartbeat":
            await self.send_to_client(client_id, {"type": "heartbeat", "status": "ok"})
        
        elif message_type == "room_list":
            await self.send_room_list(client_id)
        
        elif message_type == "create_room":
            await self.create_room(client_id, data)
        
        elif message_type == "join_room":
            await self.join_room(client_id, data)
        
        elif message_type == "chat_message":
            await self.handle_chat(client_id, data)
        
        else:
            await self.send_error(client_id, f"未知消息类型: {message_type}")
    
    async def send_room_list(self, client_id: str):
        """发送房间列表"""
        rooms_info = []
        for room_id, room_data in self.rooms.items():
            rooms_info.append({
                "room_id": room_id,
                "room_name": room_data["name"],
                "player_count": len(room_data["players"]),
                "max_players": room_data["max_players"],
                "is_game_running": room_data.get("game_running", False)
            })
        
        await self.send_to_client(client_id, {
            "type": "room_list",
            "rooms": rooms_info
        })
    
    async def create_room(self, client_id: str, data: dict):
        """创建房间"""
        import uuid
        room_id = str(uuid.uuid4())[:8]
        room_name = data.get("room_name", f"房间{room_id}")
        max_players = data.get("max_players", 4)
        
        self.rooms[room_id] = {
            "id": room_id,
            "name": room_name,
            "max_players": max_players,
            "players": [client_id],
            "owner": client_id,
            "game_running": False
        }
        
        # 更新客户端房间信息
        if client_id in self.clients:
            self.clients[client_id]["room_id"] = room_id
        
        await self.send_to_client(client_id, {
            "type": "success",
            "message": f"房间 '{room_name}' 创建成功",
            "room_id": room_id
        })
        
        logger.info(f"🏠 房间创建: {room_name} (ID: {room_id})")
    
    async def join_room(self, client_id: str, data: dict):
        """加入房间"""
        room_id = data.get("room_id")
        player_name = data.get("player_name", f"玩家{client_id}")
        
        if room_id not in self.rooms:
            await self.send_error(client_id, "房间不存在")
            return
        
        room = self.rooms[room_id]
        
        if len(room["players"]) >= room["max_players"]:
            await self.send_error(client_id, "房间已满")
            return
        
        if client_id not in room["players"]:
            room["players"].append(client_id)
        
        # 更新客户端信息
        if client_id in self.clients:
            self.clients[client_id]["room_id"] = room_id
            self.clients[client_id]["player_name"] = player_name
        
        await self.send_to_client(client_id, {
            "type": "success",
            "message": f"成功加入房间 '{room['name']}'",
            "room_id": room_id
        })
        
        # 广播给房间内其他玩家
        await self.broadcast_to_room(room_id, {
            "type": "chat_message",
            "sender_name": "系统",
            "content": f"{player_name} 加入了房间",
            "message_type": "system"
        }, exclude_client=client_id)
        
        logger.info(f"👤 玩家 {player_name} 加入房间 {room['name']}")
    
    async def handle_chat(self, client_id: str, data: dict):
        """处理聊天消息"""
        if client_id not in self.clients:
            return
        
        client = self.clients[client_id]
        room_id = client.get("room_id")
        
        if not room_id:
            await self.send_error(client_id, "您不在任何房间中")
            return
        
        content = data.get("content", "")
        sender_name = client.get("player_name", f"玩家{client_id}")
        
        # 广播聊天消息
        await self.broadcast_to_room(room_id, {
            "type": "chat_message",
            "sender_name": sender_name,
            "content": content,
            "message_type": "public"
        })
        
        logger.info(f"💬 聊天: {sender_name}: {content}")
    
    async def send_to_client(self, client_id: str, message: dict):
        """发送消息给客户端"""
        if client_id in self.clients:
            websocket = self.clients[client_id]["websocket"]
            try:
                await websocket.send(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
    
    async def send_error(self, client_id: str, error_msg: str):
        """发送错误消息"""
        await self.send_to_client(client_id, {
            "type": "error",
            "message": error_msg
        })
    
    async def broadcast_to_room(self, room_id: str, message: dict, exclude_client: str = None):
        """广播消息到房间"""
        if room_id not in self.rooms:
            return
        
        room = self.rooms[room_id]
        for player_id in room["players"]:
            if player_id != exclude_client and player_id in self.clients:
                await self.send_to_client(player_id, message)


async def main():
    """主函数"""
    print("=" * 60)
    print("🎮 大富翁联机游戏服务器 - 简化版")
    print("=" * 60)
    
    try:
        print("🔧 正在检查依赖...")
        import websockets
        print(f"✅ websockets {websockets.__version__}")
        
        print("📍 服务器地址: localhost:8765")
        print("💡 使用 Ctrl+C 停止服务器")
        print("🔧 支持功能: 房间管理、聊天系统")
        print("=" * 60)
        
        # 创建并启动服务器
        server = SimpleGameServer("localhost", 8765)
        await server.start()
        
    except KeyboardInterrupt:
        print("\n⌨️ 收到停止信号")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n👋 服务器已退出")
        input("按 Enter 键关闭...")


def main_wrapper():
    """主函数包装器，处理错误并防止窗口秒关"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 用户取消")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            input("按 Enter 键关闭...")
        except (EOFError, KeyboardInterrupt):
            print("\n程序退出")

if __name__ == "__main__":
    main_wrapper() 