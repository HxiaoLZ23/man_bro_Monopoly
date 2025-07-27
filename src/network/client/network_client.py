"""
网络客户端
"""
import asyncio
import websockets
import json
import time
import threading
import logging
from typing import Dict, Optional, Callable, Any, List
from enum import Enum

try:
    from websockets.client import WebSocketClientProtocol
    from websockets.exceptions import ConnectionClosed, InvalidURI, WebSocketException
except ImportError:
    # 如果websockets未安装，定义一个占位符
    WebSocketClientProtocol = object
    ConnectionClosed = Exception
    InvalidURI = Exception
    WebSocketException = Exception

from ..protocol import NetworkMessage, NetworkProtocol, MessageType, MessageValidator

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionState(Enum):
    """连接状态"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"

class NetworkClient:
    """网络客户端"""
    
    def __init__(self, server_host: str = "localhost", server_port: int = 8766):
        self.server_host = server_host
        self.server_port = server_port
        self.server_url = f"ws://{server_host}:{server_port}"
        
        # 连接相关
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.connection_state = ConnectionState.DISCONNECTED
        self.running = False
        
        # 消息处理器
        self.message_handlers: Dict[str, Callable[[NetworkMessage], None]] = {}
        self.error_handlers: List[Callable[[str], None]] = []
        self.connection_handlers: List[Callable[[bool], None]] = []
        
        # 玩家信息
        self.client_id: Optional[str] = None
        self.player_id: Optional[str] = None
        self.player_name: Optional[str] = None
        self.current_room_id: Optional[str] = None
        
        # 心跳相关
        self.last_heartbeat_sent = 0
        self.last_heartbeat_received = 0
        self.heartbeat_interval = 10.0  # 10秒发送一次心跳
        self.heartbeat_timeout = 30.0   # 30秒心跳超时
        self.heartbeat_task = None
        
        # 断线重连
        self.auto_reconnect = True
        self.reconnect_delay = 5.0  # 5秒后重连
        self.max_reconnect_attempts = 10
        self.reconnect_attempts = 0
        self.reconnect_task = None
        
        # 事件循环和线程
        self.event_loop = None
        self.network_thread = None
        self.message_queue = asyncio.Queue() if asyncio else None
        
        # 房间信息缓存
        self.room_list_cache: List[Dict] = []
        self.current_room_info: Optional[Dict] = None
        
        logger.info(f"🔗 网络客户端初始化完成 - {self.server_url}")
    
    # ==================== 连接管理 ====================
    
    async def start_client(self, player_name: str) -> bool:
        """启动客户端并等待连接完成"""
        self.player_name = player_name
        
        if self.network_thread and self.network_thread.is_alive():
            logger.warning("客户端已在运行中")
            return self.connection_state == ConnectionState.CONNECTED
        
        self.running = True
        
        # 创建一个Future来等待连接结果
        connection_future = asyncio.Future()
        
        def connection_callback(connected: bool):
            if not connection_future.done():
                connection_future.set_result(connected)
        
        # 添加连接回调
        self.add_connection_handler(connection_callback)
        
        # 启动网络线程
        self.network_thread = threading.Thread(
            target=self._run_event_loop,
            name="NetworkClientThread",
            daemon=True
        )
        self.network_thread.start()
        logger.info(f"🚀 网络客户端启动中，玩家: {player_name}")
        
        # 等待连接结果，最多等待10秒
        try:
            result = await asyncio.wait_for(connection_future, timeout=10.0)
            return result
        except asyncio.TimeoutError:
            logger.error("连接超时")
            return False
        finally:
            # 移除连接回调
            if connection_callback in self.connection_handlers:
                self.connection_handlers.remove(connection_callback)
    
    def stop_client(self):
        """停止客户端"""
        self.running = False
        self.auto_reconnect = False
        
        if self.event_loop:
            asyncio.run_coroutine_threadsafe(self._disconnect(), self.event_loop)
        
        # 等待线程结束
        if self.network_thread and self.network_thread.is_alive():
            self.network_thread.join(timeout=5.0)
        
        logger.info("🛑 网络客户端已停止")
    
    def _run_event_loop(self):
        """在线程中运行事件循环"""
        try:
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)
            self.message_queue = asyncio.Queue()
            
            # 启动客户端任务
            self.event_loop.run_until_complete(self._client_main())
        except Exception as e:
            logger.error(f"事件循环错误: {e}")
        finally:
            if self.event_loop:
                self.event_loop.close()
    
    async def _client_main(self):
        """客户端主循环"""
        try:
            # 首次连接
            await self._connect()
            
            # 启动心跳任务
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            
            # 消息处理循环
            while self.running:
                try:
                    if self.connection_state == ConnectionState.CONNECTED:
                        await self._message_loop()
                    else:
                        await asyncio.sleep(1.0)
                except Exception as e:
                    logger.error(f"消息循环错误: {e}")
                    if self.auto_reconnect:
                        await self._reconnect()
                    else:
                        break
        
        except Exception as e:
            logger.error(f"客户端主循环错误: {e}")
        finally:
            await self._cleanup()
    
    async def _connect(self) -> bool:
        """连接到服务器"""
        if self.connection_state in [ConnectionState.CONNECTED, ConnectionState.CONNECTING]:
            return True
        
        try:
            self.connection_state = ConnectionState.CONNECTING
            logger.info(f"🔗 正在连接服务器: {self.server_url}")
            
            self.websocket = await websockets.connect(
                self.server_url,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=10
            )
            
            self.connection_state = ConnectionState.CONNECTED
            self.reconnect_attempts = 0
            
            logger.info("✅ 连接服务器成功")
            self._notify_connection_handlers(True)
            
            return True
            
        except (ConnectionClosed, InvalidURI, WebSocketException) as e:
            logger.error(f"❌ 连接服务器失败: {e}")
            self.connection_state = ConnectionState.ERROR
            self._notify_error_handlers(f"连接失败: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ 连接时发生未知错误: {e}")
            self.connection_state = ConnectionState.ERROR
            return False
    
    async def _disconnect(self):
        """断开连接"""
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                logger.warning(f"断开连接时出错: {e}")
        
        self.websocket = None
        self.connection_state = ConnectionState.DISCONNECTED
        self._notify_connection_handlers(False)
        logger.info("🔌 已断开服务器连接")
    
    async def _reconnect(self):
        """重新连接"""
        if not self.auto_reconnect or self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error("❌ 达到最大重连次数，停止重连")
            self.running = False
            return
        
        self.reconnect_attempts += 1
        self.connection_state = ConnectionState.RECONNECTING
        
        logger.info(f"🔄 重连第 {self.reconnect_attempts} 次，{self.reconnect_delay} 秒后重试...")
        
        await asyncio.sleep(self.reconnect_delay)
        
        if await self._connect():
            logger.info("✅ 重连成功")
            # 如果之前在房间中，尝试重新加入
            if self.current_room_id:
                await self._rejoin_room()
        else:
            # 递增重连延迟
            self.reconnect_delay = min(self.reconnect_delay * 1.5, 60.0)
    
    async def _rejoin_room(self):
        """重新加入房间"""
        if self.current_room_id and self.player_name:
            logger.info(f"🏠 尝试重新加入房间: {self.current_room_id}")
            await self.join_room(self.current_room_id)
    
    # ==================== 消息处理 ====================
    
    async def _message_loop(self):
        """消息处理循环"""
        try:
            async for raw_message in self.websocket:
                try:
                    message = NetworkMessage.from_json(raw_message)
                    
                    # 验证消息
                    if not MessageValidator.validate_message(message):
                        logger.warning(f"收到无效消息: {raw_message}")
                        continue
                    
                    # 更新心跳时间
                    if message.message_type == MessageType.HEARTBEAT.value:
                        self.last_heartbeat_received = time.time()
                    
                    # 处理消息
                    await self._handle_message(message)
                    
                except json.JSONDecodeError:
                    logger.warning(f"收到无效JSON消息: {raw_message}")
                except Exception as e:
                    logger.error(f"处理消息时出错: {e}")
        
        except ConnectionClosed:
            logger.warning("🔌 连接被服务器关闭")
            self.connection_state = ConnectionState.DISCONNECTED
        except Exception as e:
            logger.error(f"消息循环错误: {e}")
            self.connection_state = ConnectionState.ERROR
    
    async def _handle_message(self, message: NetworkMessage):
        """处理收到的消息"""
        message_type = message.message_type
        
        # 处理连接成功消息
        if message_type == MessageType.SUCCESS.value and "client_id" in message.data:
            self.client_id = message.data["client_id"]
            logger.info(f"📝 获得客户端ID: {self.client_id}")
        
        # 处理房间列表
        elif message_type == MessageType.ROOM_LIST.value:
            self.room_list_cache = message.data.get("rooms", [])
        
        # 处理房间信息更新
        elif message_type == MessageType.ROOM_INFO.value:
            self.current_room_info = message.data
            # 从房间信息中提取房间ID并设置
            room_data = message.data.get("room", {})
            if room_data and "room_id" in room_data:
                self.current_room_id = room_data["room_id"]
                logger.info(f"🏠 更新房间ID: {self.current_room_id}")
        
        # 调用注册的处理器
        if message_type in self.message_handlers:
            try:
                handler = self.message_handlers[message_type]
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            except Exception as e:
                logger.error(f"消息处理器错误: {e}")
        
        logger.debug(f"📨 收到消息: {message_type}")
    
    async def _send_message(self, message: NetworkMessage) -> bool:
        """发送消息"""
        if self.connection_state != ConnectionState.CONNECTED or not self.websocket:
            logger.warning("未连接到服务器，无法发送消息")
            return False
        
        try:
            await self.websocket.send(message.to_json())
            logger.debug(f"📤 发送消息: {message.message_type}")
            return True
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return False
    
    # ==================== 心跳管理 ====================
    
    async def _heartbeat_loop(self):
        """心跳循环"""
        while self.running:
            try:
                if self.connection_state == ConnectionState.CONNECTED:
                    current_time = time.time()
                    
                    # 发送心跳
                    if current_time - self.last_heartbeat_sent >= self.heartbeat_interval:
                        await self._send_heartbeat()
                    
                    # 检查心跳超时
                    if (self.last_heartbeat_received > 0 and 
                        current_time - self.last_heartbeat_received > self.heartbeat_timeout):
                        logger.warning("⏰ 心跳超时，连接可能断开")
                        self.connection_state = ConnectionState.ERROR
                
                await asyncio.sleep(5.0)  # 每5秒检查一次
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"心跳循环错误: {e}")
    
    async def _send_heartbeat(self):
        """发送心跳"""
        message = NetworkProtocol.create_message(
            MessageType.HEARTBEAT,
            {"timestamp": time.time()},
            sender_id=self.client_id
        )
        
        if await self._send_message(message):
            self.last_heartbeat_sent = time.time()
    
    # ==================== 房间管理 ====================
    
    async def create_room(self, room_name: str, max_players: int = 4, password: str = None) -> bool:
        """创建房间"""
        if not self.is_connected():
            logger.warning("未连接到服务器")
            return False
        
        message = NetworkProtocol.create_message(
            MessageType.CREATE_ROOM,
            {
                "room_name": room_name,
                "max_players": max_players,
                "password": password,
                "player_name": self.player_name
            },
            sender_id=self.client_id
        )
        
        return await self._send_message(message)
    
    async def join_room(self, room_id: str, password: str = None) -> bool:
        """加入房间"""
        if not self.is_connected():
            logger.warning("未连接到服务器")
            return False
        
        message = NetworkProtocol.create_message(
            MessageType.JOIN_ROOM,
            {
                "room_id": room_id,
                "player_name": self.player_name,
                "password": password
            },
            sender_id=self.client_id
        )
        
        result = await self._send_message(message)
        if result:
            self.current_room_id = room_id
        return result
    
    async def leave_room(self) -> bool:
        """离开房间"""
        if not self.is_connected():
            return False
        
        message = NetworkProtocol.create_message(
            MessageType.LEAVE_ROOM,
            {},
            sender_id=self.client_id
        )
        
        result = await self._send_message(message)
        if result:
            self.current_room_id = None
            self.current_room_info = None
        return result
    
    async def request_room_list(self) -> bool:
        """请求房间列表"""
        if not self.is_connected():
            return False
        
        message = NetworkProtocol.create_message(
            MessageType.ROOM_LIST,
            {},
            sender_id=self.client_id
        )
        
        return await self._send_message(message)
    
    async def send_chat_message(self, content: str, message_type: str = "public") -> bool:
        """发送聊天消息"""
        if not self.is_connected() or not self.current_room_id:
            return False
        
        message = NetworkProtocol.create_message(
            MessageType.CHAT_MESSAGE,
            {
                "content": content,
                "message_type": message_type
            },
            sender_id=self.client_id,
            room_id=self.current_room_id
        )
        
        return await self._send_message(message)
    
    async def send_player_action(self, action: str, data: Dict[str, Any] = None) -> bool:
        """发送玩家操作"""
        if not self.is_connected() or not self.current_room_id:
            return False
        
        message = NetworkProtocol.create_message(
            MessageType.PLAYER_ACTION,
            {
                "action": action,
                "data": data or {}
            },
            sender_id=self.client_id,
            room_id=self.current_room_id
        )
        
        return await self._send_message(message)
    
    # ==================== 事件处理器 ====================
    
    def set_message_handler(self, message_type: MessageType, handler: Callable[[NetworkMessage], None]):
        """设置消息处理器"""
        self.message_handlers[message_type.value] = handler
    
    def add_error_handler(self, handler: Callable[[str], None]):
        """添加错误处理器"""
        self.error_handlers.append(handler)
    
    def add_connection_handler(self, handler: Callable[[bool], None]):
        """添加连接状态处理器"""
        self.connection_handlers.append(handler)
    
    def _notify_error_handlers(self, error_msg: str):
        """通知错误处理器"""
        for handler in self.error_handlers:
            try:
                handler(error_msg)
            except Exception as e:
                logger.error(f"错误处理器异常: {e}")
    
    def _notify_connection_handlers(self, connected: bool):
        """通知连接状态处理器"""
        for handler in self.connection_handlers:
            try:
                handler(connected)
            except Exception as e:
                logger.error(f"连接处理器异常: {e}")
    
    # ==================== 状态查询 ====================
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self.connection_state == ConnectionState.CONNECTED
    
    def is_in_room(self) -> bool:
        """检查是否在房间中"""
        return self.current_room_id is not None
    
    def get_connection_state(self) -> ConnectionState:
        """获取连接状态"""
        return self.connection_state
    
    def get_room_list(self) -> List[Dict]:
        """获取房间列表缓存"""
        return self.room_list_cache.copy()
    
    def get_current_room_info(self) -> Optional[Dict]:
        """获取当前房间信息"""
        return self.current_room_info
    
    def get_client_info(self) -> Dict[str, Any]:
        """获取客户端信息"""
        return {
            "client_id": self.client_id,
            "player_name": self.player_name,
            "current_room_id": self.current_room_id,
            "connection_state": self.connection_state.value,
            "reconnect_attempts": self.reconnect_attempts,
            "last_heartbeat": self.last_heartbeat_received
        }
    
    # ==================== 清理 ====================
    
    async def _cleanup(self):
        """清理资源"""
        try:
            # 取消心跳任务
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
                try:
                    await self.heartbeat_task
                except asyncio.CancelledError:
                    pass
            
            # 断开连接
            await self._disconnect()
            
            logger.info("🧹 客户端资源清理完成")
        
        except Exception as e:
            logger.error(f"清理资源时出错: {e}")