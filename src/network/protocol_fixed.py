"""
网络协议定义
"""
import json
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

class MessageType(Enum):
    """消息类型枚举"""
    # 连接相关
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    HEARTBEAT = "heartbeat"
    
    # 房间管理
    CREATE_ROOM = "create_room"
    JOIN_ROOM = "join_room"
    LEAVE_ROOM = "leave_room"
    ROOM_LIST = "room_list"
    ROOM_INFO = "room_info"
    
    # AI玩家管理
    ADD_AI_PLAYER = "add_ai_player"
    REMOVE_AI_PLAYER = "remove_ai_player"
    AI_PLAYER_ADDED = "ai_player_added"
    AI_PLAYER_REMOVED = "ai_player_removed"
    
    # 玩家状态管理
    PLAYER_READY = "player_ready"
    PLAYER_NOT_READY = "player_not_ready"
    
    # 游戏状态同步
    GAME_START = "game_start"
    GAME_STATE = "game_state"
    GAME_STATE_SYNC = "game_state_sync"
    PLAYER_STATE_UPDATE = "player_state_update"
    MAP_STATE_UPDATE = "map_state_update"
    GAME_END = "game_end"
    
    # 回合制管理
    TURN_START = "turn_start"
    TURN_END = "turn_end"
    TURN_CHANGE = "turn_change"
    PHASE_CHANGE = "phase_change"
    TURN_TIMEOUT = "turn_timeout"
    
    # 玩家操作
    PLAYER_ACTION = "player_action"
    ROLL_DICE = "roll_dice"
    DICE_RESULT = "dice_result"
    MOVE_PLAYER = "move_player"
    PLAYER_MOVED = "player_moved"
    BUY_PROPERTY = "buy_property"
    PROPERTY_BOUGHT = "property_bought"
    UPGRADE_PROPERTY = "upgrade_property"
    PROPERTY_UPGRADED = "property_upgraded"
    USE_ITEM = "use_item"
    ITEM_USED = "item_used"
    
    # 银行操作
    BANK_DEPOSIT = "bank_deposit"
    BANK_WITHDRAW = "bank_withdraw"
    BANK_INTEREST = "bank_interest"
    
    # 商店操作
    SHOP_BUY_ITEM = "shop_buy_item"
    SHOP_BUY_DICE = "shop_buy_dice"
    
    # 聊天系统
    CHAT_MESSAGE = "chat_message"
    CHAT_HISTORY = "chat_history"
    PLAYER_TYPING = "player_typing"
    
    # 系统消息
    ERROR = "error"
    SUCCESS = "success"
    NOTIFICATION = "notification"
    WARNING = "warning"
    WELCOME = "welcome"
    RESPONSE = "response"

@dataclass
class NetworkMessage:
    """网络消息基类"""
    message_type: str
    data: Dict[str, Any]
    timestamp: float
    sender_id: Optional[str] = None
    room_id: Optional[str] = None
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(asdict(self), ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'NetworkMessage':
        """从JSON字符串创建消息"""
        data = json.loads(json_str)
        return cls(**data)
    
    def to_bytes(self) -> bytes:
        """转换为字节数据"""
        json_str = self.to_json()
        # 添加消息长度前缀
        length = len(json_str.encode('utf-8'))
        return length.to_bytes(4, 'big') + json_str.encode('utf-8')
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'NetworkMessage':
        """从字节数据创建消息"""
        # 解析消息长度
        if len(data) < 4:
            raise ValueError("数据长度不足")
        
        length = int.from_bytes(data[:4], 'big')
        if len(data) < 4 + length:
            raise ValueError("数据不完整")
        
        json_str = data[4:4+length].decode('utf-8')
        return cls.from_json(json_str)

class NetworkProtocol:
    """网络协议处理器"""
    
    @staticmethod
    def create_message(msg_type: MessageType, data: Dict[str, Any], 
                      sender_id: str = None, room_id: str = None) -> NetworkMessage:
        """创建网络消息"""
        import time
        return NetworkMessage(
            message_type=msg_type.value,
            data=data,
            timestamp=time.time(),
            sender_id=sender_id,
            room_id=room_id
        )
    
    @staticmethod
    def create_error_message(error_msg: str, sender_id: str = None) -> NetworkMessage:
        """创建错误消息"""
        return NetworkProtocol.create_message(
            MessageType.ERROR,
            {"error": error_msg},
            sender_id=sender_id
        )
    
    @staticmethod
    def create_success_message(msg: str, data: Dict[str, Any] = None, 
                              sender_id: str = None) -> NetworkMessage:
        """创建成功消息"""
        message_data = {"message": msg}
        if data:
            message_data.update(data)
        return NetworkProtocol.create_message(
            MessageType.SUCCESS,
            message_data,
            sender_id=sender_id
        )

# 消息验证器
class MessageValidator:
    """消息验证器"""
    
    @staticmethod
    def validate_message(message: NetworkMessage) -> bool:
        """验证消息格式"""
        try:
            # 检查必要字段
            if not message.message_type or not isinstance(message.data, dict):
                return False
            
            # 检查消息类型是否有效
            valid_types = [msg_type.value for msg_type in MessageType]
            if message.message_type not in valid_types:
                return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_room_data(data: Dict[str, Any]) -> bool:
        """验证房间数据"""
        required_fields = ["room_name", "max_players"]
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_player_data(data: Dict[str, Any]) -> bool:
        """验证玩家数据"""
        required_fields = ["player_name"]
        return all(field in data for field in required_fields) 