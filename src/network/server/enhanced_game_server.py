"""
增强版游戏服务器
集成房间管理、玩家连接管理、数据同步、断线重连等核心功能
"""
import asyncio
import json
import time
import logging
import signal
import sys
from typing import Dict, Set, Optional, List
import websockets
from websockets.server import WebSocketServerProtocol

from .room_manager import RoomManager, Player as RoomPlayer
from ..protocol import NetworkProtocol, MessageType, NetworkMessage, MessageValidator
from ..multiplayer_controller import MultiplayerController

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnhancedGameServer:
    """增强版游戏服务器"""
    
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
        self.game_controllers: Dict[str, MultiplayerController] = {}
        
        # 连接管理
        self.connected_clients: Dict[WebSocketServerProtocol, Dict] = {}
        self.client_connections: Dict[str, WebSocketServerProtocol] = {}  # client_id -> websocket
        
        # 服务器状态
        self.is_running = False
        self.server = None
        self.start_time = None
        
        # 性能监控
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "total_messages": 0,
            "messages_per_second": 0,
            "rooms_created": 0,
            "games_played": 0,
            "uptime": 0,
            "last_stats_update": time.time()
        }
        
        # 心跳和清理任务
        self.heartbeat_task = None
        self.cleanup_task = None
        self.stats_task = None
        
        # 配置
        self.config = {
            "max_connections": 1000,
            "heartbeat_interval": 30.0,
            "cleanup_interval": 60.0,
            "client_timeout": 60.0,
            "room_cleanup_delay": 300.0,  # 5分钟后清理空房间
            "max_rooms": 100,
            "enable_compression": True,
            "enable_ping_pong": True
        }
        
        logger.info(f"🚀 增强版游戏服务器初始化完成 - {host}:{port}")
    
    async def start(self):
        """启动服务器"""
        try:
            # 启动WebSocket服务器
            self.server = await websockets.serve(
                self.handle_client,
                self.host,
                self.port,
                ping_interval=20 if self.config["enable_ping_pong"] else None,
                ping_timeout=10 if self.config["enable_ping_pong"] else None,
                compression="deflate" if self.config["enable_compression"] else None,
                max_size=1024*1024,  # 1MB max message size
                max_queue=32  # Max queued messages
            )
            
            self.is_running = True
            self.start_time = time.time()
            
            # 启动后台任务
            await self._start_background_tasks()
            
            logger.info(f"✅ 增强版游戏服务器启动成功")
            logger.info(f"🌐 服务器地址: ws://{self.host}:{self.port}")
            logger.info(f"📊 最大连接数: {self.config['max_connections']}")
            logger.info(f"🏠 最大房间数: {self.config['max_rooms']}")
            
            # 保持服务器运行
            await self.server.wait_closed()
            
        except Exception as e:
            logger.error(f"❌ 服务器启动失败: {e}")
            raise
    
    async def stop(self):
        """停止服务器"""
        logger.info("🛑 正在停止游戏服务器...")
        
        self.is_running = False
        
        # 停止后台任务
        await self._stop_background_tasks()
        
        # 清理游戏控制器
        for room_id, controller in self.game_controllers.items():
            try:
                await controller.cleanup()
            except Exception as e:
                logger.error(f"清理游戏控制器失败 {room_id}: {e}")
        self.game_controllers.clear()
        
        # 广播服务器关闭消息
        await self._broadcast_server_shutdown()
        
        # 关闭所有连接
        if self.connected_clients:
            await asyncio.gather(
                *[self._close_client_connection(websocket) for websocket in list(self.connected_clients.keys())],
                return_exceptions=True
            )
        
        # 关闭服务器
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        logger.info("✅ 游戏服务器已停止")
    
    async def _start_background_tasks(self):
        """启动后台任务"""
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.stats_task = asyncio.create_task(self._stats_loop())
        logger.info("📋 后台任务已启动")
    
    async def _stop_background_tasks(self):
        """停止后台任务"""
        tasks = [self.heartbeat_task, self.cleanup_task, self.stats_task]
        for task in tasks:
            if task:
                task.cancel()
        
        # 等待任务完成
        await asyncio.gather(*[task for task in tasks if task], return_exceptions=True)
        logger.info("📋 后台任务已停止")
    
    # ==================== 客户端连接处理 ====================
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """处理客户端连接"""
        client_id = None
        client_ip = websocket.remote_address[0] if websocket.remote_address else "unknown"
        
        try:
            # 检查连接数限制
            if len(self.connected_clients) >= self.config["max_connections"]:
                await websocket.close(code=1013, reason="服务器连接已满")
                return
            
            # 注册客户端
            client_id = await self._register_client(websocket)
            
            logger.info(f"👤 新客户端连接: {client_id} ({client_ip})")
            self.stats["total_connections"] += 1
            
            # 发送连接成功消息
            await self._send_to_client(
                websocket,
                NetworkProtocol.create_success_message(
                    "连接成功",
                    {
                        "client_id": client_id,
                        "server_time": time.time(),
                        "server_version": "1.0.0"
                    }
                )
            )
            
            # 处理消息循环
            await self._client_message_loop(websocket, client_id)
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"👋 客户端正常断开: {client_id} ({client_ip})")
        except Exception as e:
            logger.error(f"❌ 处理客户端连接时出错 {client_id}: {e}")
        finally:
            # 清理客户端
            if client_id:
                await self._unregister_client(websocket, client_id)
    
    async def _client_message_loop(self, websocket: WebSocketServerProtocol, client_id: str):
        """客户端消息处理循环"""
        try:
            async for raw_message in websocket:
                try:
                    # 更新统计
                    self.stats["total_messages"] += 1
                    
                    # 解析消息
                    message = NetworkMessage.from_json(raw_message)
                    
                    # 验证消息
                    if not MessageValidator.validate_message(message):
                        await self._send_error(websocket, "无效的消息格式")
                        continue
                    
                    # 更新心跳时间
                    self._update_client_heartbeat(client_id)
                    
                    # 处理消息
                    await self._handle_message(websocket, client_id, message)
                    
                except json.JSONDecodeError:
                    await self._send_error(websocket, "无效的JSON格式")
                except Exception as e:
                    logger.error(f"处理消息时出错 {client_id}: {e}")
                    await self._send_error(websocket, f"处理消息时出错: {str(e)}")
        
        except websockets.exceptions.ConnectionClosed:
            pass  # 正常断开连接
    
    async def _register_client(self, websocket: WebSocketServerProtocol) -> str:
        """注册客户端"""
        import uuid
        client_id = str(uuid.uuid4())
        
        self.connected_clients[websocket] = {
            "client_id": client_id,
            "connect_time": time.time(),
            "last_heartbeat": time.time(),
            "room_id": None,
            "player_name": None,
            "message_count": 0,
            "ip_address": websocket.remote_address[0] if websocket.remote_address else "unknown"
        }
        
        self.client_connections[client_id] = websocket
        
        return client_id
    
    async def _unregister_client(self, websocket: WebSocketServerProtocol, client_id: str):
        """注销客户端"""
        try:
            # 从房间中移除玩家
            client_info = self.connected_clients.get(websocket, {})
            room_id = client_info.get("room_id")
            
            if room_id:
                # 从游戏控制器中移除
                if room_id in self.game_controllers:
                    await self.game_controllers[room_id].remove_player(client_id)
                
                # 从房间管理器中移除
                self.room_manager.leave_room(client_id)
            
            # 移除客户端连接
            if websocket in self.connected_clients:
                del self.connected_clients[websocket]
            
            if client_id in self.client_connections:
                del self.client_connections[client_id]
        
        except Exception as e:
            logger.error(f"注销客户端时出错: {e}")
    
    def _update_client_heartbeat(self, client_id: str):
        """更新客户端心跳时间"""
        websocket = self.client_connections.get(client_id)
        if websocket and websocket in self.connected_clients:
            self.connected_clients[websocket]["last_heartbeat"] = time.time()
            self.connected_clients[websocket]["message_count"] += 1
    
    # ==================== 消息处理 ====================
    
    async def _handle_message(self, websocket: WebSocketServerProtocol, client_id: str, message: NetworkMessage):
        """处理客户端消息"""
        try:
            message_type = message.message_type
            data = message.data
            
            logger.debug(f"📨 处理消息: {client_id} -> {message_type}")
            
            # 根据消息类型分发处理
            handlers = {
                MessageType.HEARTBEAT.value: self._handle_heartbeat,
                MessageType.CREATE_ROOM.value: self._handle_create_room,
                MessageType.JOIN_ROOM.value: self._handle_join_room,
                MessageType.LEAVE_ROOM.value: self._handle_leave_room,
                MessageType.ROOM_LIST.value: self._handle_room_list,
                MessageType.GAME_START.value: self._handle_game_start,
                MessageType.PLAYER_ACTION.value: self._handle_player_action,
                MessageType.CHAT_MESSAGE.value: self._handle_chat_message,
            }
            
            handler = handlers.get(message_type)
            if handler:
                await handler(websocket, client_id, data)
            else:
                await self._send_error(websocket, f"未知的消息类型: {message_type}")
        
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            await self._send_error(websocket, f"服务器内部错误")
    
    async def _handle_heartbeat(self, websocket: WebSocketServerProtocol, client_id: str, data: Dict):
        """处理心跳消息"""
        response = NetworkProtocol.create_message(
            MessageType.HEARTBEAT,
            {
                "timestamp": time.time(),
                "server_time": time.time()
            },
            sender_id="server"
        )
        await self._send_to_client(websocket, response)
    
    async def _handle_create_room(self, websocket: WebSocketServerProtocol, client_id: str, data: Dict):
        """处理创建房间"""
        try:
            # 检查房间数量限制
            if len(self.room_manager.rooms) >= self.config["max_rooms"]:
                await self._send_error(websocket, "服务器房间已满")
                return
            
            room_name = data.get("room_name", f"房间_{client_id[:8]}")
            max_players = min(data.get("max_players", 6), 6)  # 最大6人
            password = data.get("password")
            player_name = data.get("player_name", f"玩家_{client_id[:8]}")
            
            # 创建房间
            room_id = self.room_manager.create_room(
                room_name=room_name,
                max_players=max_players,
                password=password,
                owner_id=client_id
            )
            
            # 玩家加入房间
            success = self.room_manager.join_room(
                player_id=client_id,
                room_id=room_id,
                player_name=player_name,
                connection_id=client_id
            )
            
            if not success:
                await self._send_error(websocket, "加入房间失败")
                return
            
            # 创建游戏控制器
            self.game_controllers[room_id] = MultiplayerController(
                room_id=room_id,
                broadcast_callback=lambda msg_type, msg_data: self._broadcast_to_room(room_id, msg_type, msg_data)
            )
            
            # 添加玩家到游戏控制器
            await self.game_controllers[room_id].add_player(client_id, player_name)
            
            # 更新客户端信息
            self.connected_clients[websocket]["room_id"] = room_id
            self.connected_clients[websocket]["player_name"] = player_name
            
            self.stats["rooms_created"] += 1
            logger.info(f"🏠 房间创建成功: {room_name} (ID: {room_id}) by {player_name}")
            
            # 发送成功响应
            await self._send_to_client(
                websocket,
                NetworkProtocol.create_success_message(
                    "房间创建成功",
                    {
                        "room_id": room_id,
                        "room_name": room_name,
                        "max_players": max_players,
                        "is_host": True
                    }
                )
            )
        
        except Exception as e:
            logger.error(f"创建房间失败: {e}")
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
            
            # 加入房间
            success = self.room_manager.join_room(
                player_id=client_id,
                room_id=room_id,
                player_name=player_name,
                connection_id=client_id,
                password=password
            )
            
            if not success:
                await self._send_error(websocket, "加入房间失败")
                return
            
            # 更新客户端信息
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
                        "player_name": player_name
                    }
                )
            )
        
        except Exception as e:
            logger.error(f"加入房间失败: {e}")
            await self._send_error(websocket, f"加入房间失败: {str(e)}")
    
    async def _handle_leave_room(self, websocket: WebSocketServerProtocol, client_id: str, data: Dict):
        """处理离开房间"""
        try:
            client_info = self.connected_clients.get(websocket, {})
            room_id = client_info.get("room_id")
            
            if not room_id:
                await self._send_error(websocket, "您不在任何房间中")
                return
            
            # 从房间管理器中移除
            self.room_manager.leave_room(client_id)
            
            # 更新客户端信息
            self.connected_clients[websocket]["room_id"] = None
            self.connected_clients[websocket]["player_name"] = None
            
            logger.info(f"🚪 玩家离开房间: {client_id} <- {room_id}")
            
            # 发送成功响应
            await self._send_to_client(
                websocket,
                NetworkProtocol.create_success_message("离开房间成功")
            )
        
        except Exception as e:
            logger.error(f"离开房间失败: {e}")
            await self._send_error(websocket, f"离开房间失败: {str(e)}")
    
    async def _handle_room_list(self, websocket: WebSocketServerProtocol, client_id: str, data: Dict):
        """处理房间列表请求"""
        try:
            rooms = self.room_manager.get_room_list()
            
            await self._send_to_client(
                websocket,
                NetworkProtocol.create_message(
                    MessageType.ROOM_LIST,
                    {"rooms": rooms}
                )
            )
        
        except Exception as e:
            logger.error(f"获取房间列表失败: {e}")
            await self._send_error(websocket, f"获取房间列表失败: {str(e)}")
    
    async def _handle_game_start(self, websocket: WebSocketServerProtocol, client_id: str, data: Dict):
        """处理游戏开始请求"""
        await self._send_error(websocket, "游戏开始功能待实现")
    
    async def _handle_player_action(self, websocket: WebSocketServerProtocol, client_id: str, data: Dict):
        """处理玩家操作"""
        await self._send_error(websocket, "玩家操作功能待实现")
    
    async def _handle_chat_message(self, websocket: WebSocketServerProtocol, client_id: str, data: Dict):
        """处理聊天消息"""
        await self._send_error(websocket, "聊天功能待实现")
    
    # ==================== 消息发送 ====================
    
    async def _send_to_client(self, websocket: WebSocketServerProtocol, message: NetworkMessage):
        """发送消息给客户端"""
        try:
            await websocket.send(message.to_json())
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
    
    async def _send_error(self, websocket: WebSocketServerProtocol, error_msg: str):
        """发送错误消息"""
        error_message = NetworkProtocol.create_error_message(error_msg)
        await self._send_to_client(websocket, error_message)
    
    async def _broadcast_to_room(self, room_id: str, message_type: MessageType, data: Dict):
        """向房间内所有客户端广播消息"""
        message = NetworkProtocol.create_message(
            message_type,
            data,
            room_id=room_id
        )
        
        # 获取房间内的所有客户端
        room_clients = []
        for websocket, client_info in self.connected_clients.items():
            if client_info.get("room_id") == room_id:
                room_clients.append(websocket)
        
        # 并发发送消息
        if room_clients:
            await asyncio.gather(
                *[self._send_to_client(client, message) for client in room_clients],
                return_exceptions=True
            )
    
    async def _broadcast_server_shutdown(self):
        """广播服务器关闭消息"""
        if not self.connected_clients:
            return
        
        message = NetworkProtocol.create_message(
            MessageType.NOTIFICATION,
            {
                "type": "server_shutdown",
                "message": "服务器即将关闭，请保存进度"
            }
        )
        
        await asyncio.gather(
            *[self._send_to_client(websocket, message) for websocket in self.connected_clients.keys()],
            return_exceptions=True
        )
    
    async def _close_client_connection(self, websocket: WebSocketServerProtocol):
        """关闭客户端连接"""
        try:
            await websocket.close()
        except Exception:
            pass
    
    # ==================== 后台任务 ====================
    
    async def _heartbeat_loop(self):
        """心跳检测循环"""
        while self.is_running:
            try:
                current_time = time.time()
                timeout_clients = []
                
                # 检查超时的客户端
                for websocket, client_info in self.connected_clients.items():
                    last_heartbeat = client_info.get("last_heartbeat", 0)
                    if current_time - last_heartbeat > self.config["client_timeout"]:
                        timeout_clients.append((websocket, client_info["client_id"]))
                
                # 断开超时的客户端
                for websocket, client_id in timeout_clients:
                    logger.warning(f"⏰ 客户端超时断开: {client_id}")
                    await self._close_client_connection(websocket)
                
                await asyncio.sleep(self.config["heartbeat_interval"])
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"心跳检测出错: {e}")
                await asyncio.sleep(5.0)
    
    async def _cleanup_loop(self):
        """清理循环"""
        while self.is_running:
            try:
                # 清理离线玩家
                offline_count = self.room_manager.cleanup_offline_players(
                    timeout=self.config["client_timeout"]
                )
                
                if offline_count > 0:
                    logger.info(f"🧹 清理了 {offline_count} 个离线玩家")
                
                await asyncio.sleep(self.config["cleanup_interval"])
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"清理任务出错: {e}")
                await asyncio.sleep(10.0)
    
    async def _stats_loop(self):
        """统计循环"""
        while self.is_running:
            try:
                current_time = time.time()
                
                # 更新统计信息
                self.stats["active_connections"] = len(self.connected_clients)
                self.stats["uptime"] = current_time - (self.start_time or current_time)
                
                # 记录统计信息
                if self.stats["active_connections"] > 0:
                    logger.info(f"📊 服务器状态: 连接数={self.stats['active_connections']}, "
                              f"房间数={len(self.room_manager.rooms)}")
                
                await asyncio.sleep(60.0)  # 每分钟更新一次
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"统计任务出错: {e}")
                await asyncio.sleep(10.0)
    
    def get_server_stats(self) -> Dict:
        """获取服务器统计信息"""
        return {
            **self.stats,
            "rooms": len(self.room_manager.rooms),
            "config": self.config.copy()
        }


# ==================== 入口点 ====================

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="增强版游戏服务器")
    parser.add_argument("--host", default="localhost", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=8765, help="服务器端口")
    parser.add_argument("--max-connections", type=int, default=1000, help="最大连接数")
    parser.add_argument("--max-rooms", type=int, default=100, help="最大房间数")
    
    args = parser.parse_args()
    
    # 创建服务器
    server = EnhancedGameServer(args.host, args.port)
    server.config["max_connections"] = args.max_connections
    server.config["max_rooms"] = args.max_rooms
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("收到中断信号")
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main()) 