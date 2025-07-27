"""
服务器端房间管理系统
"""
import uuid
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class RoomState(Enum):
    """房间状态"""
    WAITING = "waiting"    # 等待玩家
    PLAYING = "playing"    # 游戏中
    FINISHED = "finished"  # 游戏结束

@dataclass
class Player:
    """玩家信息"""
    player_id: str
    name: str
    connection_id: str
    is_ready: bool = False
    is_host: bool = False
    join_time: float = None
    last_heartbeat: float = None
    
    def __post_init__(self):
        if self.join_time is None:
            self.join_time = time.time()
        if self.last_heartbeat is None:
            self.last_heartbeat = time.time()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    def update_heartbeat(self):
        """更新心跳时间"""
        self.last_heartbeat = time.time()
    
    def is_online(self, timeout: float = 30.0) -> bool:
        """检查玩家是否在线"""
        return time.time() - self.last_heartbeat < timeout

@dataclass
class Room:
    """游戏房间"""
    room_id: str
    name: str
    max_players: int
    password: Optional[str] = None
    state: RoomState = RoomState.WAITING
    players: Dict[str, Player] = None
    host_id: Optional[str] = None
    create_time: float = None
    game_data: Dict = None
    
    def __post_init__(self):
        if self.players is None:
            self.players = {}
        if self.create_time is None:
            self.create_time = time.time()
        if self.game_data is None:
            self.game_data = {}
    
    def add_player(self, player: Player) -> bool:
        """添加玩家到房间"""
        if len(self.players) >= self.max_players:
            return False
        
        # 如果是第一个玩家，设为房主
        if not self.players:
            player.is_host = True
            self.host_id = player.player_id
        
        self.players[player.player_id] = player
        return True
    
    def remove_player(self, player_id: str) -> bool:
        """从房间移除玩家"""
        if player_id not in self.players:
            return False
        
        player = self.players.pop(player_id)
        
        # 如果移除的是房主，选择新房主
        if player.is_host and self.players:
            new_host_id = next(iter(self.players.keys()))
            self.players[new_host_id].is_host = True
            self.host_id = new_host_id
        elif not self.players:
            self.host_id = None
        
        return True
    
    def get_player(self, player_id: str) -> Optional[Player]:
        """获取玩家信息"""
        return self.players.get(player_id)
    
    def get_player_list(self) -> List[Dict]:
        """获取玩家列表"""
        return [player.to_dict() for player in self.players.values()]
    
    def is_full(self) -> bool:
        """检查房间是否已满"""
        return len(self.players) >= self.max_players
    
    def is_empty(self) -> bool:
        """检查房间是否为空"""
        return len(self.players) == 0
    
    def can_start_game(self) -> bool:
        """检查是否可以开始游戏"""
        return len(self.players) >= 2 and self.state == RoomState.WAITING
    
    def set_ready(self, player_id: str, is_ready: bool) -> bool:
        """设置玩家准备状态"""
        if player_id in self.players:
            self.players[player_id].is_ready = is_ready
            return True
        return False
    
    def all_players_ready(self) -> bool:
        """检查所有玩家是否都已准备"""
        if not self.players:
            return False
        return all(player.is_ready for player in self.players.values())
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "room_id": self.room_id,
            "name": self.name,
            "max_players": self.max_players,
            "current_players": len(self.players),
            "state": self.state.value,
            "has_password": self.password is not None,
            "host_id": self.host_id,
            "create_time": self.create_time,
            "players": self.get_player_list(),
            "can_start": self.can_start_game(),
            "all_ready": self.all_players_ready()
        }

class RoomManager:
    """房间管理器"""
    
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.player_room_map: Dict[str, str] = {}  # player_id -> room_id
        self.connection_player_map: Dict[str, str] = {}  # connection_id -> player_id
    
    def create_room(self, room_name: str, max_players: int, password: str = None, 
                   owner_id: str = None) -> str:
        """创建房间"""
        room_id = str(uuid.uuid4())
        room = Room(
            room_id=room_id,
            name=room_name,
            max_players=max_players,
            password=password
        )
        
        # 如果有房主，设置房主信息
        if owner_id:
            room.host_id = owner_id
            
        self.rooms[room_id] = room
        return room_id
    
    def delete_room(self, room_id: str) -> bool:
        """删除房间"""
        if room_id in self.rooms:
            # 清理所有相关玩家映射
            room = self.rooms[room_id]
            for player_id in list(room.players.keys()):
                self.leave_room(player_id)
            del self.rooms[room_id]
            return True
        return False
    
    def get_room(self, room_id: str) -> Optional[Room]:
        """获取房间"""
        return self.rooms.get(room_id)
    
    def get_room_info(self, room_id: str) -> Optional[Dict]:
        """获取房间信息"""
        room = self.get_room(room_id)
        if room:
            return room.to_dict()
        return None
    
    def get_room_list(self) -> List[Dict]:
        """获取房间列表"""
        return [room.to_dict() for room in self.rooms.values() 
                if room.state != RoomState.FINISHED]
    
    def join_room(self, player_id: str, room_id: str, player_name: str, 
                 connection_id: str, password: str = None) -> bool:
        """加入房间"""
        room = self.get_room(room_id)
        if not room:
            return False
        
        # 检查密码
        if room.password and room.password != password:
            return False
        
        # 检查房间是否已满
        if room.is_full():
            return False
        
        # 检查玩家是否已在其他房间
        if player_id in self.player_room_map:
            self.leave_room(player_id)
        
        # 创建玩家对象
        player = Player(
            player_id=player_id,
            name=player_name,
            connection_id=connection_id
        )
        
        # 添加玩家到房间
        if room.add_player(player):
            self.player_room_map[player_id] = room_id
            self.connection_player_map[connection_id] = player_id
            return True
        
        return False
    
    def leave_room(self, player_id: str) -> bool:
        """离开房间"""
        if player_id not in self.player_room_map:
            return False
        
        room_id = self.player_room_map.pop(player_id)
        room = self.get_room(room_id)
        
        if room:
            player = room.get_player(player_id)
            if player:
                # 移除连接映射
                if player.connection_id in self.connection_player_map:
                    del self.connection_player_map[player.connection_id]
            
            room.remove_player(player_id)
            
            # 如果房间为空，删除房间
            if room.is_empty():
                del self.rooms[room_id]
            
            return True
        
        return False
    
    def set_player_ready(self, player_id: str, is_ready: bool) -> bool:
        """设置玩家准备状态"""
        room = self.get_player_room(player_id)
        if room:
            return room.set_ready(player_id, is_ready)
        return False
    
    def start_game(self, room_id: str) -> bool:
        """开始游戏"""
        room = self.get_room(room_id)
        if room and room.can_start_game():
            room.state = RoomState.PLAYING
            return True
        return False
    
    def end_game(self, room_id: str) -> bool:
        """结束游戏"""
        room = self.get_room(room_id)
        if room:
            room.state = RoomState.FINISHED
            return True
        return False
    
    def get_player_room(self, player_id: str) -> Optional[Room]:
        """获取玩家所在房间"""
        room_id = self.player_room_map.get(player_id)
        if room_id:
            return self.get_room(room_id)
        return None
    
    def get_player_by_connection(self, connection_id: str) -> Optional[Player]:
        """通过连接ID获取玩家"""
        player_id = self.connection_player_map.get(connection_id)
        if player_id:
            room = self.get_player_room(player_id)
            if room:
                return room.get_player(player_id)
        return None
    
    def update_player_heartbeat(self, connection_id: str):
        """更新玩家心跳"""
        player = self.get_player_by_connection(connection_id)
        if player:
            player.update_heartbeat()
    
    def cleanup_offline_players(self, timeout: float = 30.0):
        """清理离线玩家"""
        offline_players = []
        
        for room in self.rooms.values():
            for player in room.players.values():
                if not player.is_online(timeout):
                    offline_players.append(player.player_id)
        
        # 移除离线玩家
        for player_id in offline_players:
            self.leave_room(player_id)
        
        return len(offline_players)
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total_players = sum(len(room.players) for room in self.rooms.values())
        rooms_by_state = {}
        
        for state in RoomState:
            rooms_by_state[state.value] = len([
                room for room in self.rooms.values() 
                if room.state == state
            ])
        
        return {
            "total_rooms": len(self.rooms),
            "total_players": total_players,
            "rooms_by_state": rooms_by_state,
            "active_connections": len(self.connection_player_map)
        }