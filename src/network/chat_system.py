"""
聊天系统
"""
import time
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from src.network.protocol import NetworkProtocol, MessageType


class ChatMessageType(Enum):
    """聊天消息类型"""
    PUBLIC = "public"      # 公共聊天
    PRIVATE = "private"    # 私聊
    SYSTEM = "system"      # 系统消息
    GAME = "game"          # 游戏消息
    NOTIFICATION = "notification"  # 通知消息


@dataclass
class ChatMessage:
    """聊天消息数据类"""
    message_id: str
    sender_id: Optional[str]
    sender_name: str
    content: str
    message_type: ChatMessageType
    timestamp: float
    room_id: Optional[str] = None
    target_id: Optional[str] = None  # 私聊目标ID
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "sender_name": self.sender_name,
            "content": self.content,
            "message_type": self.message_type.value,
            "timestamp": self.timestamp,
            "room_id": self.room_id,
            "target_id": self.target_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """从字典创建消息"""
        return cls(
            message_id=data["message_id"],
            sender_id=data.get("sender_id"),
            sender_name=data["sender_name"],
            content=data["content"],
            message_type=ChatMessageType(data["message_type"]),
            timestamp=data["timestamp"],
            room_id=data.get("room_id"),
            target_id=data.get("target_id")
        )


class ChatFilter:
    """聊天过滤器"""
    
    def __init__(self):
        """初始化过滤器"""
        # 敏感词列表（可以从配置文件加载）
        self.banned_words = [
            # 可以添加需要过滤的词汇
        ]
        
        # 消息长度限制
        self.max_message_length = 200
        
        # 消息频率限制（每分钟最多发送消息数）
        self.max_messages_per_minute = 30
        
        # 用户消息历史（用于频率限制）
        self.user_message_history = {}
    
    def filter_message(self, sender_id: str, content: str) -> Dict[str, Any]:
        """
        过滤消息
        
        Args:
            sender_id: 发送者ID
            content: 消息内容
            
        Returns:
            Dict: 过滤结果
        """
        # 检查消息长度
        if len(content) > self.max_message_length:
            return {
                "allowed": False,
                "reason": f"消息长度超过限制（{self.max_message_length}字符）"
            }
        
        # 检查消息频率
        if not self._check_message_frequency(sender_id):
            return {
                "allowed": False,
                "reason": "发送消息过于频繁，请稍后再试"
            }
        
        # 检查敏感词
        filtered_content = self._filter_banned_words(content)
        
        return {
            "allowed": True,
            "filtered_content": filtered_content
        }
    
    def _check_message_frequency(self, sender_id: str) -> bool:
        """检查消息发送频率"""
        current_time = time.time()
        
        if sender_id not in self.user_message_history:
            self.user_message_history[sender_id] = []
        
        # 清理一分钟前的记录
        self.user_message_history[sender_id] = [
            msg_time for msg_time in self.user_message_history[sender_id]
            if current_time - msg_time < 60
        ]
        
        # 检查是否超过频率限制
        if len(self.user_message_history[sender_id]) >= self.max_messages_per_minute:
            return False
        
        # 记录当前消息时间
        self.user_message_history[sender_id].append(current_time)
        return True
    
    def _filter_banned_words(self, content: str) -> str:
        """过滤敏感词"""
        filtered_content = content
        for word in self.banned_words:
            if word in filtered_content:
                filtered_content = filtered_content.replace(word, "*" * len(word))
        return filtered_content


class ChatSystem:
    """聊天系统"""
    
    def __init__(self, broadcast_callback: Callable = None):
        """
        初始化聊天系统
        
        Args:
            broadcast_callback: 广播消息的回调函数
        """
        self.broadcast_callback = broadcast_callback
        self.chat_filter = ChatFilter()
        
        # 消息存储
        self.message_history = []  # 全局消息历史
        self.room_messages = {}    # 房间消息历史
        self.private_messages = {} # 私聊消息历史
        
        # 配置
        self.config = {
            "max_history_size": 1000,      # 最大历史消息数
            "max_room_history_size": 500,  # 最大房间历史消息数
            "enable_private_chat": True,   # 是否启用私聊
            "save_chat_history": True,     # 是否保存聊天记录
        }
        
        # 在线用户状态
        self.online_users = {}  # user_id -> user_info
        self.typing_users = {}  # user_id -> timestamp
    
    def set_broadcast_callback(self, callback: Callable):
        """设置广播回调函数"""
        self.broadcast_callback = callback
    
    async def send_message(self, sender_id: str, sender_name: str, content: str, 
                          message_type: ChatMessageType = ChatMessageType.PUBLIC,
                          room_id: str = None, target_id: str = None) -> Dict[str, Any]:
        """
        发送消息
        
        Args:
            sender_id: 发送者ID
            sender_name: 发送者名称
            content: 消息内容
            message_type: 消息类型
            room_id: 房间ID（用于房间消息）
            target_id: 目标用户ID（用于私聊）
            
        Returns:
            Dict: 发送结果
        """
        # 过滤消息
        filter_result = self.chat_filter.filter_message(sender_id, content)
        if not filter_result["allowed"]:
            return {
                "success": False,
                "error": filter_result["reason"]
            }
        
        # 创建消息
        message = ChatMessage(
            message_id=self._generate_message_id(),
            sender_id=sender_id,
            sender_name=sender_name,
            content=filter_result["filtered_content"],
            message_type=message_type,
            timestamp=time.time(),
            room_id=room_id,
            target_id=target_id
        )
        
        # 存储消息
        await self._store_message(message)
        
        # 广播消息
        await self._broadcast_message(message)
        
        return {
            "success": True,
            "message_id": message.message_id,
            "timestamp": message.timestamp
        }
    
    async def send_system_message(self, content: str, room_id: str = None) -> Dict[str, Any]:
        """
        发送系统消息
        
        Args:
            content: 消息内容
            room_id: 房间ID
            
        Returns:
            Dict: 发送结果
        """
        return await self.send_message(
            sender_id=None,
            sender_name="系统",
            content=content,
            message_type=ChatMessageType.SYSTEM,
            room_id=room_id
        )
    
    async def send_game_message(self, content: str, room_id: str = None) -> Dict[str, Any]:
        """
        发送游戏消息
        
        Args:
            content: 消息内容
            room_id: 房间ID
            
        Returns:
            Dict: 发送结果
        """
        return await self.send_message(
            sender_id=None,
            sender_name="游戏",
            content=content,
            message_type=ChatMessageType.GAME,
            room_id=room_id
        )
    
    async def send_notification(self, content: str, room_id: str = None) -> Dict[str, Any]:
        """
        发送通知消息
        
        Args:
            content: 消息内容
            room_id: 房间ID
            
        Returns:
            Dict: 发送结果
        """
        return await self.send_message(
            sender_id=None,
            sender_name="通知",
            content=content,
            message_type=ChatMessageType.NOTIFICATION,
            room_id=room_id
        )
    
    async def _store_message(self, message: ChatMessage):
        """存储消息"""
        if not self.config["save_chat_history"]:
            return
        
        # 存储到全局历史
        self.message_history.append(message)
        if len(self.message_history) > self.config["max_history_size"]:
            self.message_history.pop(0)
        
        # 存储到房间历史
        if message.room_id:
            if message.room_id not in self.room_messages:
                self.room_messages[message.room_id] = []
            
            self.room_messages[message.room_id].append(message)
            if len(self.room_messages[message.room_id]) > self.config["max_room_history_size"]:
                self.room_messages[message.room_id].pop(0)
        
        # 存储私聊消息
        if message.message_type == ChatMessageType.PRIVATE and message.target_id:
            chat_key = self._get_private_chat_key(message.sender_id, message.target_id)
            if chat_key not in self.private_messages:
                self.private_messages[chat_key] = []
            
            self.private_messages[chat_key].append(message)
            if len(self.private_messages[chat_key]) > self.config["max_room_history_size"]:
                self.private_messages[chat_key].pop(0)
    
    async def _broadcast_message(self, message: ChatMessage):
        """广播消息"""
        if not self.broadcast_callback:
            return
        
        # 创建网络消息
        network_message = NetworkProtocol.create_message(
            MessageType.CHAT_MESSAGE,
            message.to_dict(),
            sender_id=message.sender_id,
            room_id=message.room_id
        )
        
        # 广播消息
        await self.broadcast_callback(network_message)
    
    def get_chat_history(self, room_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取聊天历史
        
        Args:
            room_id: 房间ID，如果为None则获取全局历史
            limit: 获取消息数量限制
            
        Returns:
            List: 消息列表
        """
        if room_id:
            messages = self.room_messages.get(room_id, [])
        else:
            messages = self.message_history
        
        # 获取最新的消息
        recent_messages = messages[-limit:] if len(messages) > limit else messages
        
        return [msg.to_dict() for msg in recent_messages]
    
    def get_private_chat_history(self, user1_id: str, user2_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取私聊历史
        
        Args:
            user1_id: 用户1 ID
            user2_id: 用户2 ID
            limit: 获取消息数量限制
            
        Returns:
            List: 私聊消息列表
        """
        if not self.config["enable_private_chat"]:
            return []
        
        chat_key = self._get_private_chat_key(user1_id, user2_id)
        messages = self.private_messages.get(chat_key, [])
        
        # 获取最新的消息
        recent_messages = messages[-limit:] if len(messages) > limit else messages
        
        return [msg.to_dict() for msg in recent_messages]
    
    async def set_user_typing(self, user_id: str, user_name: str, room_id: str = None):
        """
        设置用户正在输入状态
        
        Args:
            user_id: 用户ID
            user_name: 用户名称
            room_id: 房间ID
        """
        self.typing_users[user_id] = time.time()
        
        if self.broadcast_callback:
            message = NetworkProtocol.create_message(
                MessageType.PLAYER_TYPING,
                {
                    "user_id": user_id,
                    "user_name": user_name,
                    "is_typing": True,
                    "timestamp": time.time()
                },
                sender_id=user_id,
                room_id=room_id
            )
            await self.broadcast_callback(message)
    
    async def clear_user_typing(self, user_id: str, user_name: str, room_id: str = None):
        """
        清除用户正在输入状态
        
        Args:
            user_id: 用户ID
            user_name: 用户名称
            room_id: 房间ID
        """
        if user_id in self.typing_users:
            del self.typing_users[user_id]
        
        if self.broadcast_callback:
            message = NetworkProtocol.create_message(
                MessageType.PLAYER_TYPING,
                {
                    "user_id": user_id,
                    "user_name": user_name,
                    "is_typing": False,
                    "timestamp": time.time()
                },
                sender_id=user_id,
                room_id=room_id
            )
            await self.broadcast_callback(message)
    
    def get_typing_users(self) -> List[str]:
        """获取正在输入的用户列表"""
        current_time = time.time()
        # 清理超时的输入状态（5秒超时）
        expired_users = [
            user_id for user_id, timestamp in self.typing_users.items()
            if current_time - timestamp > 5.0
        ]
        
        for user_id in expired_users:
            del self.typing_users[user_id]
        
        return list(self.typing_users.keys())
    
    def _generate_message_id(self) -> str:
        """生成消息ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _get_private_chat_key(self, user1_id: str, user2_id: str) -> str:
        """获取私聊键（确保顺序一致）"""
        if user1_id < user2_id:
            return f"{user1_id}_{user2_id}"
        else:
            return f"{user2_id}_{user1_id}"
    
    def add_online_user(self, user_id: str, user_name: str, room_id: str = None):
        """添加在线用户"""
        self.online_users[user_id] = {
            "user_id": user_id,
            "user_name": user_name,
            "room_id": room_id,
            "online_time": time.time()
        }
    
    def remove_online_user(self, user_id: str):
        """移除在线用户"""
        if user_id in self.online_users:
            del self.online_users[user_id]
        
        if user_id in self.typing_users:
            del self.typing_users[user_id]
    
    def get_online_users(self, room_id: str = None) -> List[Dict[str, Any]]:
        """获取在线用户列表"""
        if room_id:
            return [
                user_info for user_info in self.online_users.values()
                if user_info["room_id"] == room_id
            ]
        else:
            return list(self.online_users.values())
    
    def get_chat_statistics(self) -> Dict[str, Any]:
        """获取聊天统计信息"""
        return {
            "total_messages": len(self.message_history),
            "room_count": len(self.room_messages),
            "online_users": len(self.online_users),
            "typing_users": len(self.typing_users),
            "private_chats": len(self.private_messages)
        } 