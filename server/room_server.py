#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大富翁房间管理服务器
"""

import asyncio
import json
import sys
import traceback
import time
import uuid
from typing import Dict, List, Set

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

class GameRoom:
    """游戏房间类"""
    def __init__(self, room_id: str, name: str, max_players: int = 4, password: str = None):
        self.room_id = room_id
        self.name = name
        self.max_players = max_players
        self.password = password
        self.players: Dict[str, dict] = {}  # client_id -> player_info
        self.ai_players: Dict[str, dict] = {}  # ai_id -> ai_player_info
        self.ai_counter = 0  # AI玩家计数器
        self.created_time = time.time()
        self.host_id = None
    
    def add_player(self, client_id: str, player_name: str) -> bool:
        """添加玩家"""
        if len(self.players) + len(self.ai_players) >= self.max_players:
            return False
        
        if not self.host_id:
            self.host_id = client_id
        
        self.players[client_id] = {
            "client_id": client_id,
            "name": player_name,
            "is_ready": False,
            "is_host": client_id == self.host_id,
            "is_ai": False,
            "join_time": time.time()
        }
        return True
    
    def add_ai_player(self, difficulty: str = "简单") -> str:
        """添加AI玩家"""
        if len(self.players) + len(self.ai_players) >= self.max_players:
            return None
        
        self.ai_counter += 1
        ai_id = f"ai_{self.room_id}_{self.ai_counter}"
        ai_name = f"AI玩家{self.ai_counter}({difficulty})"
        
        self.ai_players[ai_id] = {
            "client_id": ai_id,
            "name": ai_name,
            "is_ready": True,  # AI玩家总是准备状态
            "is_host": False,
            "is_ai": True,
            "difficulty": difficulty,
            "join_time": time.time()
        }
        
        return ai_id
    
    def remove_player(self, client_id: str):
        """移除玩家"""
        if client_id in self.players:
            del self.players[client_id]
            
            # 如果房主离开，选择新房主
            if client_id == self.host_id and self.players:
                self.host_id = next(iter(self.players.keys()))
                self.players[self.host_id]["is_host"] = True
        elif client_id in self.ai_players:
            del self.ai_players[client_id]
    
    def remove_ai_player(self, ai_id: str) -> bool:
        """移除AI玩家"""
        if ai_id in self.ai_players:
            del self.ai_players[ai_id]
            return True
        return False
    
    def get_all_players(self) -> List[dict]:
        """获取所有玩家（包括AI）"""
        all_players = list(self.players.values()) + list(self.ai_players.values())
        return all_players
    
    def to_dict(self) -> dict:
        """转换为字典"""
        all_players = self.get_all_players()
        return {
            "room_id": self.room_id,
            "name": self.name,
            "current_players": len(all_players),
            "max_players": self.max_players,
            "has_password": bool(self.password),
            "players": all_players,
            "ai_count": len(self.ai_players)
        }

class RoomServer:
    """房间管理服务器"""
    def __init__(self):
        self.clients: Dict[str, dict] = {}  # client_id -> client_info
        self.rooms: Dict[str, GameRoom] = {}  # room_id -> GameRoom
        self.websockets: Dict[str, object] = {}  # client_id -> websocket
    
    async def handle_client(self, websocket, path=None):
        """处理客户端连接"""
        client_id = f"client_{id(websocket)}"
        print(f"👤 客户端连接: {client_id}")
        
        # 注册客户端
        self.clients[client_id] = {
            "client_id": client_id,
            "websocket": websocket,
            "player_name": None,
            "room_id": None,
            "connect_time": time.time()
        }
        self.websockets[client_id] = websocket
        
        try:
            # 发送欢迎消息
            await self.send_message(client_id, {
                "message_type": "success",
                "data": {
                    "message": "欢迎连接大富翁服务器！",
                    "client_id": client_id
                },
                "timestamp": time.time(),
                "sender_id": "server"
            })
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(client_id, data)
                except json.JSONDecodeError:
                    await self.send_error(client_id, "无效的JSON格式")
                except Exception as e:
                    print(f"处理消息错误: {e}")
                    await self.send_error(client_id, f"处理消息失败: {e}")
        
        except Exception as e:
            print(f"客户端 {client_id} 连接错误: {e}")
        finally:
            await self.cleanup_client(client_id)
            print(f"👋 客户端断开: {client_id}")
    
    async def handle_message(self, client_id: str, data: dict):
        """处理客户端消息"""
        message_type = data.get("message_type")
        message_data = data.get("data", {})
        
        print(f"📨 收到消息 [{client_id}]: {message_type}")
        
        if message_type == "heartbeat":
            await self.handle_heartbeat(client_id)
        elif message_type == "create_room":
            await self.handle_create_room(client_id, message_data)
        elif message_type == "join_room":
            await self.handle_join_room(client_id, message_data)
        elif message_type == "leave_room":
            await self.handle_leave_room(client_id)
        elif message_type == "room_list":
            await self.handle_room_list(client_id)
        elif message_type == "add_ai_player":
            await self.handle_add_ai_player(client_id, message_data)
        elif message_type == "remove_ai_player":
            await self.handle_remove_ai_player(client_id, message_data)
        elif message_type == "player_ready":
            await self.handle_player_ready(client_id, message_data)
        elif message_type == "player_action":
            await self.handle_player_action(client_id, message_data)
        else:
            await self.send_response(client_id, f"收到消息类型: {message_type}")
    
    async def handle_heartbeat(self, client_id: str):
        """处理心跳"""
        await self.send_message(client_id, {
            "message_type": "heartbeat",
            "data": {"timestamp": time.time()},
            "timestamp": time.time(),
            "sender_id": "server"
        })
    
    async def handle_create_room(self, client_id: str, data: dict):
        """处理创建房间"""
        room_name = data.get("room_name", "").strip()
        max_players = data.get("max_players", 4)
        password = data.get("password")
        player_name = data.get("player_name", "未知玩家")
        
        if not room_name:
            await self.send_error(client_id, "房间名称不能为空")
            return
        
        if max_players < 2 or max_players > 6:
            await self.send_error(client_id, "最大玩家数必须在2-6之间")
            return
        
        # 创建房间
        room_id = str(uuid.uuid4())[:8]
        room = GameRoom(room_id, room_name, max_players, password)
        
        # 添加创建者为第一个玩家
        if room.add_player(client_id, player_name):
            self.rooms[room_id] = room
            self.clients[client_id]["room_id"] = room_id
            self.clients[client_id]["player_name"] = player_name
            
            await self.send_success(client_id, f"成功创建房间: {room_name}")
            await self.send_room_info(room_id)
            print(f"🏠 房间创建成功: {room_name} (ID: {room_id})")
        else:
            await self.send_error(client_id, "创建房间失败")
    
    async def handle_join_room(self, client_id: str, data: dict):
        """处理加入房间"""
        room_id = data.get("room_id")
        password = data.get("password")
        player_name = data.get("player_name", "未知玩家")
        
        if not room_id or room_id not in self.rooms:
            await self.send_error(client_id, "房间不存在")
            return
        
        room = self.rooms[room_id]
        
        # 检查密码
        if room.password and room.password != password:
            await self.send_error(client_id, "房间密码错误")
            return
        
        # 加入房间
        if room.add_player(client_id, player_name):
            self.clients[client_id]["room_id"] = room_id
            self.clients[client_id]["player_name"] = player_name
            
            await self.send_success(client_id, f"成功加入房间: {room.name}")
            await self.send_room_info(room_id)
            print(f"👥 玩家 {player_name} 加入房间: {room.name}")
        else:
            await self.send_error(client_id, "房间已满")
    
    async def handle_leave_room(self, client_id: str):
        """处理离开房间"""
        room_id = self.clients[client_id].get("room_id")
        if not room_id or room_id not in self.rooms:
            await self.send_error(client_id, "不在任何房间中")
            return
        
        room = self.rooms[room_id]
        room.remove_player(client_id)
        self.clients[client_id]["room_id"] = None
        
        # 如果房间为空，删除房间
        if not room.players:
            del self.rooms[room_id]
            print(f"🗑️ 房间已删除: {room.name}")
        else:
            await self.send_room_info(room_id)
        
        await self.send_success(client_id, "已离开房间")
    
    async def handle_room_list(self, client_id: str):
        """处理房间列表请求"""
        room_list = [room.to_dict() for room in self.rooms.values()]
        await self.send_message(client_id, {
            "message_type": "room_list",
            "data": {"rooms": room_list},
            "timestamp": time.time(),
            "sender_id": "server"
        })
    
    async def send_room_info(self, room_id: str):
        """向房间所有玩家发送房间信息"""
        if room_id not in self.rooms:
            return
        
        room = self.rooms[room_id]
        room_info = room.to_dict()
        
        for player_id in room.players:
            await self.send_message(player_id, {
                "message_type": "room_info",
                "data": {"room": room_info},
                "timestamp": time.time(),
                "sender_id": "server"
            })
    
    async def send_message(self, client_id: str, message: dict):
        """发送消息给客户端"""
        if client_id in self.websockets:
            try:
                await self.websockets[client_id].send(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                print(f"发送消息失败 [{client_id}]: {e}")
    
    async def send_success(self, client_id: str, message: str):
        """发送成功消息"""
        await self.send_message(client_id, {
            "message_type": "success",
            "data": {"message": message},
            "timestamp": time.time(),
            "sender_id": "server"
        })
    
    async def send_error(self, client_id: str, error: str):
        """发送错误消息"""
        await self.send_message(client_id, {
            "message_type": "error",
            "data": {"error": error},
            "timestamp": time.time(),
            "sender_id": "server"
        })
    
    async def send_response(self, client_id: str, message: str):
        """发送响应消息"""
        await self.send_message(client_id, {
            "message_type": "response",
            "data": {"message": message},
            "timestamp": time.time(),
            "sender_id": "server"
        })
    
    async def cleanup_client(self, client_id: str):
        """清理客户端"""
        # 离开房间
        if client_id in self.clients:
            room_id = self.clients[client_id].get("room_id")
            if room_id and room_id in self.rooms:
                room = self.rooms[room_id]
                room.remove_player(client_id)
                
                if not room.players:
                    del self.rooms[room_id]
                    print(f"🗑️ 房间已删除: {room.name}")
                else:
                    await self.send_room_info(room_id)
        
        # 清理客户端信息
        if client_id in self.clients:
            del self.clients[client_id]
        if client_id in self.websockets:
            del self.websockets[client_id]
    
    async def handle_add_ai_player(self, client_id: str, data: dict):
        """处理添加AI玩家请求"""
        # 检查客户端是否在房间中
        room_id = self.clients[client_id].get("room_id")
        if not room_id or room_id not in self.rooms:
            await self.send_error(client_id, "不在任何房间中")
            return
        
        room = self.rooms[room_id]
        
        # 检查是否是房主
        if room.host_id != client_id:
            await self.send_error(client_id, "只有房主可以添加AI玩家")
            return
        
        # 添加AI玩家
        difficulty = data.get("difficulty", "简单")
        ai_id = room.add_ai_player(difficulty)
        
        if ai_id:
            await self.send_success(client_id, f"AI玩家添加成功 (难度: {difficulty})")
            await self.send_room_info(room_id)
            print(f"🤖 AI玩家添加到房间 {room.name}: {ai_id}")
        else:
            await self.send_error(client_id, "房间已满，无法添加AI玩家")
    
    async def handle_remove_ai_player(self, client_id: str, data: dict):
        """处理移除AI玩家请求"""
        # 检查客户端是否在房间中
        room_id = self.clients[client_id].get("room_id")
        if not room_id or room_id not in self.rooms:
            await self.send_error(client_id, "不在任何房间中")
            return
        
        room = self.rooms[room_id]
        
        # 检查是否是房主
        if room.host_id != client_id:
            await self.send_error(client_id, "只有房主可以移除AI玩家")
            return
        
        # 移除AI玩家
        ai_id = data.get("ai_id")
        if ai_id and room.remove_ai_player(ai_id):
            await self.send_success(client_id, "AI玩家移除成功")
            await self.send_room_info(room_id)
            print(f"🗑️ AI玩家从房间移除: {ai_id}")
        else:
            await self.send_error(client_id, "移除AI玩家失败")
    
    async def handle_player_ready(self, client_id: str, data: dict):
        """处理玩家准备状态"""
        # 检查客户端是否在房间中
        room_id = self.clients[client_id].get("room_id")
        if not room_id or room_id not in self.rooms:
            await self.send_error(client_id, "不在任何房间中")
            return
        
        room = self.rooms[room_id]
        
        # 更新玩家准备状态
        if client_id in room.players:
            is_ready = data.get("ready", True)
            room.players[client_id]["is_ready"] = is_ready
            
            await self.send_success(client_id, f"准备状态更新: {'已准备' if is_ready else '未准备'}")
            await self.send_room_info(room_id)
            print(f"🎮 玩家准备状态更新 [{client_id}]: {is_ready}")
        else:
            await self.send_error(client_id, "玩家不在房间中")

    async def handle_player_action(self, client_id: str, data: dict):
        """处理玩家操作"""
        # 检查客户端是否在房间中
        room_id = self.clients[client_id].get("room_id")
        if not room_id or room_id not in self.rooms:
            await self.send_error(client_id, "不在任何房间中")
            return
        
        room = self.rooms[room_id]
        action = data.get("action")
        action_data = data.get("data", {})
        
        print(f"🎯 处理玩家操作 [{client_id}]: {action}")
        
        if action == "start_game":
            await self.handle_start_game(client_id, room, action_data)
        elif action == "toggle_ready":
            # 处理准备状态切换
            ready = action_data.get("ready", True)
            if client_id in room.players:
                room.players[client_id]["is_ready"] = ready
                await self.send_success(client_id, f"准备状态更新: {'已准备' if ready else '未准备'}")
                await self.send_room_info(room_id)
                print(f"🎮 玩家准备状态更新 [{client_id}]: {ready}")
            else:
                await self.send_error(client_id, "玩家不在房间中")
        else:
            await self.send_error(client_id, f"未知操作: {action}")

    async def handle_start_game(self, client_id: str, room: GameRoom, game_data: dict):
        """处理开始游戏请求"""
        # 检查是否是房主
        if room.host_id != client_id:
            await self.send_error(client_id, "只有房主可以开始游戏")
            return
        
        # 检查所有玩家是否都已准备
        all_players = room.get_all_players()
        ready_count = sum(1 for player in all_players if player.get("is_ready", False) or player.get("is_host", False))
        total_players = len(all_players)
        
        if ready_count < total_players:
            await self.send_error(client_id, f"还有 {total_players - ready_count} 名玩家未准备")
            return
        
        if total_players < 2:
            await self.send_error(client_id, "至少需要2名玩家才能开始游戏")
            return
        
        # 获取地图文件
        map_file = game_data.get("map_file", "1.json")
        print(f"🗺️ 开始游戏，地图文件: {map_file}")
        
        # 向房间所有玩家发送游戏开始消息
        game_start_data = {
            "map_file": map_file,
            "players": game_data.get("players", []),
            "room_id": room.room_id,
            "game_mode": "multiplayer"
        }
        
        for player_id in room.players:
            await self.send_message(player_id, {
                "message_type": "game_start",
                "data": game_start_data,
                "timestamp": time.time(),
                "sender_id": "server"
            })
        
        print(f"🎮 房间 {room.name} 开始游戏！玩家数: {total_players}, 地图: {map_file}")
        await self.send_success(client_id, "游戏开始！")

async def run_server(host="localhost", port=8765):
    """运行服务器"""
    try:
        import websockets
        print(f"✅ websockets版本: {websockets.__version__}")
    except ImportError:
        print("❌ 缺少websockets模块")
        print("请运行: pip install websockets")
        return
    
    # 查找可用端口
    available_port = find_available_port(host, port)
    if not available_port:
        print("❌ 无法找到可用端口")
        return
    
    print(f"🚀 启动房间管理服务器: {host}:{available_port}")
    
    server = RoomServer()
    
    try:
        print("🎮 服务器启动中...")
        async with websockets.serve(server.handle_client, host, available_port):
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
    print("🎮 大富翁房间管理服务器")
    print("=" * 50)
    
    try:
        asyncio.run(run_server())
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