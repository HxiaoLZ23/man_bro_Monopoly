"""
网络系统测试脚本
测试服务器端和客户端的核心功能
"""
import asyncio
import sys
import json
import time
import logging
from typing import List

# 添加项目路径
sys.path.append('.')

try:
    from src.network.client.network_client import NetworkClient
    from src.network.protocol import MessageType
    from src.network.server.enhanced_game_server import EnhancedGameServer
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保项目路径正确")
    sys.exit(1)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NetworkTestClient:
    """网络测试客户端"""
    
    def __init__(self, client_name: str, server_host: str = "localhost", server_port: int = 8765):
        self.client_name = client_name
        self.client = NetworkClient(server_host, server_port)
        self.messages_received = []
        self.connected = False
        
        # 设置消息处理器
        self._setup_message_handlers()
    
    def _setup_message_handlers(self):
        """设置消息处理器"""
        self.client.set_message_handler(MessageType.SUCCESS, self._handle_success)
        self.client.set_message_handler(MessageType.ERROR, self._handle_error)
        self.client.set_message_handler(MessageType.ROOM_LIST, self._handle_room_list)
        self.client.set_message_handler(MessageType.CHAT_MESSAGE, self._handle_chat_message)
        self.client.set_message_handler(MessageType.NOTIFICATION, self._handle_notification)
        
        # 设置连接状态处理器
        self.client.add_connection_handler(self._handle_connection_change)
        self.client.add_error_handler(self._handle_client_error)
    
    def _handle_success(self, message):
        """处理成功消息"""
        logger.info(f"[{self.client_name}] 成功: {message.data.get('message', 'N/A')}")
        self.messages_received.append(('success', message.data))
    
    def _handle_error(self, message):
        """处理错误消息"""
        logger.error(f"[{self.client_name}] 错误: {message.data.get('error', 'N/A')}")
        self.messages_received.append(('error', message.data))
    
    def _handle_room_list(self, message):
        """处理房间列表"""
        rooms = message.data.get('rooms', [])
        logger.info(f"[{self.client_name}] 房间列表: {len(rooms)} 个房间")
        for room in rooms:
            logger.info(f"  - {room['name']} ({room['current_players']}/{room['max_players']})")
        self.messages_received.append(('room_list', message.data))
    
    def _handle_chat_message(self, message):
        """处理聊天消息"""
        sender = message.data.get('sender_name', 'Unknown')
        content = message.data.get('content', '')
        logger.info(f"[{self.client_name}] 聊天 {sender}: {content}")
        self.messages_received.append(('chat', message.data))
    
    def _handle_notification(self, message):
        """处理通知消息"""
        logger.info(f"[{self.client_name}] 通知: {message.data}")
        self.messages_received.append(('notification', message.data))
    
    def _handle_connection_change(self, connected: bool):
        """处理连接状态变化"""
        self.connected = connected
        status = "已连接" if connected else "已断开"
        logger.info(f"[{self.client_name}] 连接状态: {status}")
    
    def _handle_client_error(self, error_msg: str):
        """处理客户端错误"""
        logger.error(f"[{self.client_name}] 客户端错误: {error_msg}")
    
    async def start(self):
        """启动客户端"""
        self.client.start_client(self.client_name)
        
        # 等待连接建立
        for _ in range(10):
            if self.connected:
                break
            await asyncio.sleep(0.5)
        
        if not self.connected:
            raise Exception(f"客户端 {self.client_name} 连接失败")
        
        logger.info(f"[{self.client_name}] 客户端启动成功")
    
    async def stop(self):
        """停止客户端"""
        self.client.stop_client()
        logger.info(f"[{self.client_name}] 客户端已停止")
    
    async def create_room(self, room_name: str, max_players: int = 4, password: str = None):
        """创建房间"""
        return await self.client.create_room(room_name, max_players, password)
    
    async def join_room(self, room_id: str, password: str = None):
        """加入房间"""
        return await self.client.join_room(room_id, password)
    
    async def leave_room(self):
        """离开房间"""
        return await self.client.leave_room()
    
    async def request_room_list(self):
        """请求房间列表"""
        return await self.client.request_room_list()
    
    async def send_chat(self, content: str):
        """发送聊天消息"""
        return await self.client.send_chat_message(content)
    
    def get_last_message(self, message_type: str = None):
        """获取最后一条消息"""
        if not self.messages_received:
            return None
        
        if message_type:
            for msg_type, data in reversed(self.messages_received):
                if msg_type == message_type:
                    return data
            return None
        
        return self.messages_received[-1][1]


async def test_basic_connection():
    """测试基本连接功能"""
    logger.info("🧪 测试基本连接功能")
    
    # 创建测试客户端
    client = NetworkTestClient("TestClient1")
    
    try:
        # 启动客户端
        await client.start()
        
        # 等待一秒让连接稳定
        await asyncio.sleep(1.0)
        
        # 检查连接状态
        assert client.connected, "客户端应该已连接"
        
        # 检查是否收到连接成功消息
        success_msg = client.get_last_message('success')
        assert success_msg is not None, "应该收到连接成功消息"
        assert 'client_id' in success_msg, "成功消息应该包含客户端ID"
        
        logger.info("✅ 基本连接测试通过")
        
    finally:
        await client.stop()


async def test_room_management():
    """测试房间管理功能"""
    logger.info("🧪 测试房间管理功能")
    
    # 创建两个测试客户端
    client1 = NetworkTestClient("Host")
    client2 = NetworkTestClient("Guest")
    
    try:
        # 启动客户端
        await client1.start()
        await client2.start()
        
        await asyncio.sleep(1.0)
        
        # 测试房间列表（应该为空）
        await client1.request_room_list()
        await asyncio.sleep(0.5)
        
        room_list = client1.get_last_message('room_list')
        assert room_list is not None, "应该收到房间列表"
        assert len(room_list['rooms']) == 0, "初始房间列表应该为空"
        
        # 测试创建房间
        await client1.create_room("测试房间", 4)
        await asyncio.sleep(0.5)
        
        success_msg = client1.get_last_message('success')
        assert success_msg is not None, "创建房间应该成功"
        assert 'room_id' in success_msg, "成功消息应该包含房间ID"
        
        room_id = success_msg['room_id']
        logger.info(f"创建房间成功，房间ID: {room_id}")
        
        # 测试房间列表（应该有一个房间）
        await client2.request_room_list()
        await asyncio.sleep(0.5)
        
        room_list = client2.get_last_message('room_list')
        assert len(room_list['rooms']) == 1, "应该有一个房间"
        assert room_list['rooms'][0]['name'] == "测试房间", "房间名称应该正确"
        
        # 测试加入房间
        await client2.join_room(room_id)
        await asyncio.sleep(0.5)
        
        success_msg = client2.get_last_message('success')
        assert success_msg is not None, "加入房间应该成功"
        
        # 测试离开房间
        await client2.leave_room()
        await asyncio.sleep(0.5)
        
        success_msg = client2.get_last_message('success')
        assert success_msg is not None, "离开房间应该成功"
        
        logger.info("✅ 房间管理测试通过")
        
    finally:
        await client1.stop()
        await client2.stop()


async def run_server_only():
    """只启动服务器"""
    logger.info("🖥️ 启动游戏服务器")
    
    server = EnhancedGameServer("localhost", 8765)
    server.config["max_connections"] = 1000
    server.config["max_rooms"] = 100
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("收到中断信号")
    finally:
        await server.stop()


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="网络系统测试")
    parser.add_argument("--server-only", action="store_true", help="只启动服务器")
    parser.add_argument("--test", action="store_true", help="运行简单测试")
    
    args = parser.parse_args()
    
    if args.server_only:
        await run_server_only()
    elif args.test:
        logger.info("🧪 运行基本测试")
        try:
            await test_basic_connection()
            logger.info("🎉 测试完成！")
        except Exception as e:
            logger.error(f"❌ 测试失败: {e}")
            sys.exit(1)
    else:
        await run_server_only()


if __name__ == "__main__":
    asyncio.run(main()) 