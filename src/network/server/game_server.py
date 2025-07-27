"""
游戏服务器
基于WebSocket的异步游戏服务器，支持多房间并发游戏
"""
import asyncio
import json
import time
import logging
from typing import Dict, Set, Optional
import websockets
from websockets.server import WebSocketServerProtocol

from src.network.server.room_manager import RoomManager
from src.network.protocol import NetworkProtocol, MessageType, NetworkMessage
from src.network.multiplayer_controller import MultiplayerController

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameServer:
    """游戏服务器"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        """
        初始化游戏服务器
        
        Args:
            host: 服务器主机地址
            port: 服务器端口
        """
        self.host = host
        self.port = port
        
        # 核心组件
        self.room_manager = RoomManager()
        self.game_controllers = {}  # room_id -> MultiplayerController
        
        # 连接管理
        self.connected_clients: Dict[WebSocketServerProtocol, Dict] = {}
        self.client_rooms: Dict[str, str] = {}  # client_id -> room_id
        
        # 服务器状态
        self.is_running = False
        self.server = None
        
        # 心跳检测
        self.heartbeat_interval = 10.0  # 心跳间隔（秒）
        self.heartbeat_task = None
        
        logger.info(f"🚀 游戏服务器初始化完成 - {host}:{port}")
    
    async def start(self):
        """启动服务器"""
        try:
            self.server = await websockets.serve(
                self.handle_client,
                self.host,
                self.port,
                ping_interval=20,
                ping_timeout=10
            )
            
            self.is_running = True
            
            # 启动心跳检测
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            
            logger.info(f"✅ 游戏服务器启动成功 - ws://{self.host}:{self.port}")
            
            # 保持服务器运行
            await self.server.wait_closed()
            
        except Exception as e:
            logger.error(f"❌ 服务器启动失败: {e}")
            raise
    
    async def stop(self):
        """停止服务器"""
        logger.info("🛑 正在停止游戏服务器...")
        
        self.is_running = False
        
        # 停止心跳检测
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        
        # 清理游戏控制器
        for controller in self.game_controllers.values():
            await controller.cleanup()
        self.game_controllers.clear()
        
        # 关闭所有连接
        if self.connected_clients:
            await asyncio.gather(
                *[client.close() for client in self.connected_clients.keys()],
                return_exceptions=True
            )
        
        # 关闭服务器
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        logger.info("✅ 游戏服务器已停止")
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """处理客户端连接"""
        client_id = None
        try:
            # 注册客户端
            client_id = await self._register_client(websocket)
            logger.info(f"👤 客户端连接: {client_id} ({websocket.remote_address})")
            
            # 发送连接成功消息
            await self._send_to_client(
                websocket,
                NetworkProtocol.create_success_message(
                    "连接成功",
                    {"client_id": client_id}
                )
            )
            
            # 处理消息循环
            async for raw_message in websocket:
                try:
                    # 解析消息
                    message = NetworkMessage.from_json(raw_message)
                    
                    # 处理消息
                    await self._handle_message(websocket, client_id, message)
                    
                except json.JSONDecodeError:
                    await self._send_error(websocket, "无效的JSON格式")
                except Exception as e:
                    logger.error(f"处理消息时出错: {e}")
                    await self._send_error(websocket, f"处理消息时出错: {str(e)}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"👋 客户端断开连接: {client_id}")
        except Exception as e:
            logger.error(f"处理客户端连接时出错: {e}")
        finally:
            # 清理客户端
            if client_id:
                await self._unregister_client(websocket, client_id)
    
    async def _register_client(self, websocket: WebSocketServerProtocol) -> str:
        """注册客户端"""
        import uuid
        client_id = str(uuid.uuid4())
        
        self.connected_clients[websocket] = {
            "client_id": client_id,
            "connect_time": time.time(),
            "last_heartbeat": time.time(),
            "room_id": None,
            "player_name": None
        }
        
        return client_id
    
    async def _unregister_client(self, websocket: WebSocketServerProtocol, client_id: str):
        """注销客户端"""
        try:
            # 从房间中移除玩家
            if client_id in self.client_rooms:
                room_id = self.client_rooms[client_id]
                if room_id in self.game_controllers:
                    await self.game_controllers[room_id].remove_player(client_id)
                
                # 从房间管理器中移除
                self.room_manager.leave_room(client_id, room_id)
                del self.client_rooms[client_id]
            
            # 移除客户端连接
            if websocket in self.connected_clients:
                del self.connected_clients[websocket]
        
        except Exception as e:
            logger.error(f"注销客户端时出错: {e}")
    
    async def _handle_message(self, websocket: WebSocketServerProtocol, client_id: str, message: NetworkMessage):
        """处理客户端消息"""
        try:
            message_type = message.message_type
            data = message.data
            
            logger.debug(f"📨 收到消息: {client_id} -> {message_type}")
            
            # 更新心跳时间
            if websocket in self.connected_clients:
                self.connected_clients[websocket]["last_heartbeat"] = time.time()
            
            # 根据消息类型分发处理
            if message_type == MessageType.HEARTBEAT.value:
                await self._handle_heartbeat(websocket, client_id, data)
            elif message_type == MessageType.CREATE_ROOM.value:
                await self._handle_create_room(websocket, client_id, data)
            elif message_type == MessageType.JOIN_ROOM.value:
                await self._handle_join_room(websocket, client_id, data)
            elif message_type == MessageType.LEAVE_ROOM.value:
                await self._handle_leave_room(websocket, client_id, data)
            elif message_type == MessageType.ROOM_LIST.value:
                await self._handle_room_list(websocket, client_id, data)
            elif message_type == MessageType.GAME_START.value:
                await self._handle_game_start(websocket, client_id, data)
            elif message_type == MessageType.PLAYER_ACTION.value:
                await self._handle_player_action(websocket, client_id, data)
            elif message_type == MessageType.CHAT_MESSAGE.value:
                await self._handle_chat_message(websocket, client_id, data)
            else:
                await self._send_error(websocket, f"未知的消息类型: {message_type}")
        
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            await self._send_error(websocket, f"服务器内部错误: {str(e)}")
    
    # ==================== 消息处理器 ====================
    
    async def _handle_heartbeat(self, websocket: WebSocketServerProtocol, client_id: str, data: Dict):
        """处理心跳消息"""
        response = NetworkProtocol.create_message(
            MessageType.HEARTBEAT,
            {"timestamp": time.time()},
            sender_id=client_id
        )
        await self._send_to_client(websocket, response)
    
    async def _handle_create_room(self, websocket: WebSocketServerProtocol, client_id: str, data: Dict):
        """处理创建房间"""
        try:
            room_name = data.get("room_name", f"房间_{client_id[:8]}")
            max_players = data.get("max_players", 6)
            password = data.get("password")
            
            # 创建房间
            room_id = self.room_manager.create_room(
                room_name=room_name,
                max_players=max_players,
                password=password,
                owner_id=client_id
            )
            
            # 创建游戏控制器
            self.game_controllers[room_id] = MultiplayerController(
                room_id=room_id,
                broadcast_callback=lambda msg: self._broadcast_to_room(room_id, msg)
            )
            
            # 加入房间
            self.client_rooms[client_id] = room_id
            self.connected_clients[websocket]["room_id"] = room_id
            
            logger.info(f"🏠 房间创建: {room_name} (ID: {room_id}) by {client_id}")
            
            # 发送成功响应
            await self._send_to_client(
                websocket,
                NetworkProtocol.create_success_message(
                    "房间创建成功",
                    {
                        "room_id": room_id,
                        "room_name": room_name,
                        "max_players": max_players
                    }
                )
            )
        
        except Exception as e:
            await self._send_error(websocket, f"创建房间失败: {str(e)}")
    
    async def _handle_join_room(self, websocket: WebSocketServerProtocol, client_id: str, data: Dict):
        """处理加入房间"""
        try:
            room_id = data.get("room_id")
            player_name = data.get("player_name", f"玩家_{client_id[:8]}")
            password = data.get("password")
            
            if not room_id:
                await self._send_error(websocket, "缺少房间ID")
                return
            
            # 检查房间是否存在
            if room_id not in self.game_controllers:
                await self._send_error(websocket, "房间不存在")
                return
            
            # 加入房间
            success = self.room_manager.join_room(client_id, room_id, password)
            if not success:
                await self._send_error(websocket, "加入房间失败")
                return
            
            # 添加到游戏控制器
            controller = self.game_controllers[room_id]
            result = await controller.add_player(client_id, player_name)
            
            if not result["success"]:
                await self._send_error(websocket, result["error"])
                return
            
            # 更新客户端信息
            self.client_rooms[client_id] = room_id
            self.connected_clients[websocket]["room_id"] = room_id
            self.connected_clients[websocket]["player_name"] = player_name
            
            logger.info(f"🚪 玩家加入房间: {player_name} -> {room_id}")
            
            # 发送成功响应
            await self._send_to_client(
                websocket,
                NetworkProtocol.create_success_message(
                    "加入房间成功",
                    {
                        "room_id": room_id,
                        "player_name": player_name,
                        "game_info": controller.get_game_info()
                    }
                )
            )
        
        except Exception as e:
            await self._send_error(websocket, f"加入房间失败: {str(e)}")
    
    async def _handle_leave_room(self, websocket: WebSocketServerProtocol, client_id: str, data: Dict):
        """处理离开房间"""
        try:
            if client_id not in self.client_rooms:
                await self._send_error(websocket, "您不在任何房间中")
                return
            
            room_id = self.client_rooms[client_id]
            
            # 从游戏控制器中移除
            if room_id in self.game_controllers:
                await self.game_controllers[room_id].remove_player(client_id)
            
            # 从房间管理器中移除
            self.room_manager.leave_room(client_id, room_id)
            del self.client_rooms[client_id]
            
            # 更新客户端信息
            self.connected_clients[websocket]["room_id"] = None
            self.connected_clients[websocket]["player_name"] = None
            
            logger.info(f"🚪 玩家离开房间: {client_id} <- {room_id}")
            
            # 检查是否需要清理空房间
            await self._cleanup_empty_room(room_id)
            
            # 发送成功响应
            await self._send_to_client(
                websocket,
                NetworkProtocol.create_success_message("离开房间成功")
            )
        
        except Exception as e:
            await self._send_error(websocket, f"离开房间失败: {str(e)}")
    
    async def _handle_room_list(self, websocket: WebSocketServerProtocol, client_id: str, data: Dict):
        """处理房间列表请求"""
        try:
            rooms = self.room_manager.get_room_list()
            
            # 添加游戏信息
            enhanced_rooms = []
            for room in rooms:
                room_data = room.copy()
                if room["room_id"] in self.game_controllers:
                    controller = self.game_controllers[room["room_id"]]
                    room_data.update({
                        "is_game_running": controller.is_game_running,
                        "player_count": controller.get_player_count(),
                        "can_join": not controller.is_full()
                    })
                enhanced_rooms.append(room_data)
            
            await self._send_to_client(
                websocket,
                NetworkProtocol.create_message(
                    MessageType.ROOM_LIST,
                    {"rooms": enhanced_rooms}
                )
            )
        
        except Exception as e:
            await self._send_error(websocket, f"获取房间列表失败: {str(e)}")
    
    async def _handle_game_start(self, websocket: WebSocketServerProtocol, client_id: str, data: Dict):
        """处理游戏开始请求"""
        try:
            if client_id not in self.client_rooms:
                await self._send_error(websocket, "您不在任何房间中")
                return
            
            room_id = self.client_rooms[client_id]
            
            if room_id not in self.game_controllers:
                await self._send_error(websocket, "房间不存在")
                return
            
            controller = self.game_controllers[room_id]
            
            # 检查是否为房主
            room_info = self.room_manager.get_room_info(room_id)
            if room_info and room_info["owner_id"] != client_id:
                await self._send_error(websocket, "只有房主可以开始游戏")
                return
            
            # 开始游戏
            result = await controller.start_game(data.get("map_data"))
            
            if result["success"]:
                await self._send_to_client(
                    websocket,
                    NetworkProtocol.create_success_message(
                        result["message"],
                        {"game_info": controller.get_game_info()}
                    )
                )
            else:
                await self._send_error(websocket, result["error"])
        
        except Exception as e:
            await self._send_error(websocket, f"开始游戏失败: {str(e)}")
    
    async def _handle_player_action(self, websocket: WebSocketServerProtocol, client_id: str, data: Dict):
        """处理玩家操作"""
        try:
            if client_id not in self.client_rooms:
                await self._send_error(websocket, "您不在任何房间中")
                return
            
            room_id = self.client_rooms[client_id]
            
            if room_id not in self.game_controllers:
                await self._send_error(websocket, "房间不存在")
                return
            
            controller = self.game_controllers[room_id]
            
            action = data.get("action")
            action_data = data.get("data", {})
            
            if not action:
                await self._send_error(websocket, "缺少操作类型")
                return
            
            # 处理玩家操作
            result = await controller.handle_player_action(client_id, action, action_data)
            
            # 发送结果
            if result["success"]:
                await self._send_to_client(
                    websocket,
                    NetworkProtocol.create_success_message(
                        result.get("message", "操作成功"),
                        result
                    )
                )
            else:
                await self._send_error(websocket, result["error"])
        
        except Exception as e:
            await self._send_error(websocket, f"处理玩家操作失败: {str(e)}")
    
    async def _handle_chat_message(self, websocket: WebSocketServerProtocol, client_id: str, data: Dict):
        """处理聊天消息"""
        try:
            if client_id not in self.client_rooms:
                await self._send_error(websocket, "您不在任何房间中")
                return
            
            room_id = self.client_rooms[client_id]
            
            if room_id not in self.game_controllers:
                await self._send_error(websocket, "房间不存在")
                return
            
            controller = self.game_controllers[room_id]
            
            content = data.get("content", "")
            message_type = data.get("message_type", "public")
            
            if not content.strip():
                await self._send_error(websocket, "消息内容不能为空")
                return
            
            # 处理聊天消息
            result = await controller.handle_chat_message(client_id, content, message_type)
            
            if result["success"]:
                await self._send_to_client(
                    websocket,
                    NetworkProtocol.create_success_message("消息发送成功")
                )
            else:
                await self._send_error(websocket, result["error"])
        
        except Exception as e:
            await self._send_error(websocket, f"处理聊天消息失败: {str(e)}")
    
    # ==================== 辅助方法 ====================
    
    async def _send_to_client(self, websocket: WebSocketServerProtocol, message: NetworkMessage):
        """发送消息给客户端"""
        try:
            await websocket.send(message.to_json())
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
    
    async def _send_error(self, websocket: WebSocketServerProtocol, error_msg: str):
        """发送错误消息"""
        error_message = NetworkProtocol.create_error_message(error_msg)
        await self._send_to_client(websocket, error_message)
    
    async def _broadcast_to_room(self, room_id: str, message: NetworkMessage):
        """向房间内所有客户端广播消息"""
        if room_id not in self.game_controllers:
            return
        
        # 获取房间内的所有客户端
        room_clients = [
            websocket for websocket, client_info in self.connected_clients.items()
            if client_info.get("room_id") == room_id
        ]
        
        # 并发发送消息
        if room_clients:
            await asyncio.gather(
                *[self._send_to_client(client, message) for client in room_clients],
                return_exceptions=True
            )
    
    async def _cleanup_empty_room(self, room_id: str):
        """清理空房间"""
        try:
            # 检查房间是否为空
            room_info = self.room_manager.get_room_info(room_id)
            if room_info and room_info["player_count"] == 0:
                # 清理游戏控制器
                if room_id in self.game_controllers:
                    await self.game_controllers[room_id].cleanup()
                    del self.game_controllers[room_id]
                
                # 删除房间
                self.room_manager.delete_room(room_id)
                
                logger.info(f"🧹 清理空房间: {room_id}")
        
        except Exception as e:
            logger.error(f"清理房间时出错: {e}")
    
    async def _heartbeat_loop(self):
        """心跳检测循环"""
        while self.is_running:
            try:
                current_time = time.time()
                timeout_clients = []
                
                # 检查超时的客户端
                for websocket, client_info in self.connected_clients.items():
                    last_heartbeat = client_info.get("last_heartbeat", 0)
                    if current_time - last_heartbeat > 30.0:  # 30秒超时
                        timeout_clients.append((websocket, client_info["client_id"]))
                
                # 断开超时的客户端
                for websocket, client_id in timeout_clients:
                    logger.warning(f"⏰ 客户端超时断开: {client_id}")
                    await websocket.close()
                
                await asyncio.sleep(self.heartbeat_interval)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"心跳检测出错: {e}")
                await asyncio.sleep(1.0)
    
    def get_server_stats(self) -> Dict:
        """获取服务器统计信息"""
        return {
            "is_running": self.is_running,
            "connected_clients": len(self.connected_clients),
            "active_rooms": len(self.game_controllers),
            "total_rooms": len(self.room_manager.rooms),
            "uptime": time.time() - getattr(self, "start_time", time.time())
        }

if __name__ == "__main__":
    server = GameServer()
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        asyncio.run(server.stop())
        print("服务器已关闭") 