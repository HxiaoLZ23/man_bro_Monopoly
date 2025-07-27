"""
游戏状态数据模型
"""
from typing import List, Dict, Optional
from src.core.constants import GAME_STATES, TURN_PHASES, MIN_PLAYERS, MAX_PLAYERS
from src.models.player import Player
from src.models.map import Map


class GameState:
    """游戏状态类"""
    
    def __init__(self):
        """初始化游戏状态"""
        # 基础状态
        self.game_state = GAME_STATES["WAITING"]  # 游戏状态
        self.current_phase = TURN_PHASES["PREPARATION"]  # 当前回合阶段
        self.current_player_index = 0  # 当前玩家索引
        self.turn_count = 0  # 回合数
        self.round_count = 0  # 轮数（所有玩家都行动一次为一轮）
        
        # 游戏对象
        self.players = []  # 玩家列表
        self.map = None  # 地图对象
        self.winner = None  # 获胜者
        
        # 游戏设置
        self.min_players = MIN_PLAYERS
        self.max_players = MAX_PLAYERS
        self.auto_save_interval = 5  # 自动保存间隔（回合数）
        
        # 游戏统计
        self.game_start_time = None  # 游戏开始时间
        self.game_end_time = None  # 游戏结束时间
        self.total_turns = 0  # 总回合数
        self.bankrupt_players = []  # 破产玩家列表
    
    def initialize_game(self, players: List[Player], map_obj: Map) -> bool:
        """
        初始化游戏
        
        Args:
            players: 玩家列表
            map_obj: 地图对象
            
        Returns:
            bool: 初始化是否成功
        """
        if not self._validate_players(players):
            return False
        
        self.players = players
        self.map = map_obj
        self.game_state = GAME_STATES["PLAYING"]
        self.current_player_index = 0
        self.turn_count = 0
        self.round_count = 0
        self.winner = None
        self.bankrupt_players = []
        
        # 设置游戏开始时间
        import time
        self.game_start_time = time.time()
        
        return True
    
    def _validate_players(self, players: List[Player]) -> bool:
        """
        验证玩家列表
        
        Args:
            players: 玩家列表
            
        Returns:
            bool: 验证是否通过
        """
        if not players:
            return False
        
        if len(players) < self.min_players or len(players) > self.max_players:
            return False
        
        # 检查玩家ID是否唯一
        player_ids = [p.player_id for p in players]
        if len(player_ids) != len(set(player_ids)):
            return False
        
        return True
    
    def get_current_player(self) -> Optional[Player]:
        """
        获取当前玩家
        
        Returns:
            Optional[Player]: 当前玩家对象
        """
        if 0 <= self.current_player_index < len(self.players):
            return self.players[self.current_player_index]
        return None
    
    def next_player(self) -> Optional[Player]:
        """
        切换到下一个玩家
        
        Returns:
            Optional[Player]: 下一个玩家对象
        """
        if not self.players:
            return None
        
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.turn_count += 1
        
        # 检查是否完成一轮
        if self.current_player_index == 0:
            self.round_count += 1
        
        return self.get_current_player()
    
    def get_player_by_id(self, player_id: int) -> Optional[Player]:
        """
        根据ID获取玩家
        
        Args:
            player_id: 玩家ID
            
        Returns:
            Optional[Player]: 玩家对象
        """
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None
    
    def get_active_players(self) -> List[Player]:
        """
        获取活跃玩家列表（未破产的玩家）
        
        Returns:
            List[Player]: 活跃玩家列表
        """
        return [player for player in self.players if not player.is_bankrupt()]
    
    def check_game_over(self) -> bool:
        """
        检查游戏是否结束
        
        Returns:
            bool: 游戏是否结束
        """
        active_players = self.get_active_players()
        
        # 如果只有一个或没有活跃玩家，游戏结束
        if len(active_players) <= 1:
            self.game_state = GAME_STATES["FINISHED"]
            if len(active_players) == 1:
                self.winner = active_players[0]
            
            # 设置游戏结束时间
            import time
            self.game_end_time = time.time()
            
            return True
        
        return False
    
    def mark_player_bankrupt(self, player: Player) -> None:
        """
        标记玩家破产
        
        Args:
            player: 破产的玩家
        """
        if player not in self.bankrupt_players:
            self.bankrupt_players.append(player)
    
    def set_game_state(self, state: str) -> bool:
        """
        设置游戏状态
        
        Args:
            state: 游戏状态
            
        Returns:
            bool: 设置是否成功
        """
        if state in GAME_STATES.values():
            self.game_state = state
            return True
        return False
    
    def set_current_phase(self, phase: str) -> bool:
        """
        设置当前回合阶段
        
        Args:
            phase: 回合阶段
            
        Returns:
            bool: 设置是否成功
        """
        if phase in TURN_PHASES.values():
            self.current_phase = phase
            return True
        return False
    
    def advance_phase(self) -> None:
        """
        推进到下一个阶段
        """
        if self.current_phase == TURN_PHASES["PREPARATION"]:
            self.current_phase = TURN_PHASES["ACTION"]
        elif self.current_phase == TURN_PHASES["ACTION"]:
            self.current_phase = TURN_PHASES["SETTLEMENT"]
        elif self.current_phase == TURN_PHASES["SETTLEMENT"]:
            self.current_phase = TURN_PHASES["END"]
        elif self.current_phase == TURN_PHASES["END"]:
            # 结束阶段后，切换到下一个玩家，并重置为准备阶段
            self.next_player()
            self.current_phase = TURN_PHASES["PREPARATION"]
    
    def get_game_duration(self) -> Optional[float]:
        """
        获取游戏持续时间（秒）
        
        Returns:
            Optional[float]: 游戏持续时间，如果游戏未开始或未结束返回None
        """
        if self.game_start_time is None:
            return None
        
        end_time = self.game_end_time
        if end_time is None:
            import time
            end_time = time.time()
        
        return end_time - self.game_start_time
    
    def get_game_statistics(self) -> Dict:
        """
        获取游戏统计信息
        
        Returns:
            Dict: 游戏统计信息
        """
        stats = {
            "total_players": len(self.players),
            "active_players": len(self.get_active_players()),
            "bankrupt_players": len(self.bankrupt_players),
            "turn_count": self.turn_count,
            "round_count": self.round_count,
            "game_state": self.game_state,
            "current_phase": self.current_phase,
            "winner": self.winner.name if self.winner else None,
            "game_duration": self.get_game_duration()
        }
        
        # 玩家统计
        player_stats = []
        for player in self.players:
            player_stat = {
                "name": player.name,
                "is_ai": player.is_ai,
                "is_bankrupt": player.is_bankrupt(),
                "total_assets": player.get_total_assets(),
                "money": player.money,
                "bank_money": player.bank_money,
                "properties_count": len(player.properties),
                "items_count": len(player.items),
                "total_income": player.total_income,
                "total_expense": player.total_expense
            }
            player_stats.append(player_stat)
        
        stats["players"] = player_stats
        
        return stats
    
    def to_dict(self) -> Dict:
        """
        转换为字典格式
        
        Returns:
            Dict: 游戏状态数据字典
        """
        return {
            "game_state": self.game_state,
            "current_phase": self.current_phase,
            "current_player_index": self.current_player_index,
            "turn_count": self.turn_count,
            "round_count": self.round_count,
            "players": [player.to_dict() for player in self.players],
            "map": self.map.to_dict() if self.map else None,
            "winner": self.winner.to_dict() if self.winner else None,
            "min_players": self.min_players,
            "max_players": self.max_players,
            "auto_save_interval": self.auto_save_interval,
            "game_start_time": self.game_start_time,
            "game_end_time": self.game_end_time,
            "total_turns": self.total_turns,
            "bankrupt_players": [p.player_id for p in self.bankrupt_players]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GameState':
        """
        从字典创建游戏状态对象
        
        Args:
            data: 游戏状态数据字典
            
        Returns:
            GameState: 游戏状态对象
        """
        game_state = cls()
        game_state.game_state = data["game_state"]
        game_state.current_phase = data["current_phase"]
        game_state.current_player_index = data["current_player_index"]
        game_state.turn_count = data["turn_count"]
        game_state.round_count = data["round_count"]
        game_state.min_players = data["min_players"]
        game_state.max_players = data["max_players"]
        game_state.auto_save_interval = data["auto_save_interval"]
        game_state.game_start_time = data["game_start_time"]
        game_state.game_end_time = data["game_end_time"]
        game_state.total_turns = data["total_turns"]
        
        # 重建玩家
        game_state.players = [Player.from_dict(p_data) for p_data in data["players"]]
        
        # 重建地图
        if data["map"]:
            game_state.map = Map.from_dict(data["map"])
        
        # 重建获胜者
        if data["winner"]:
            game_state.winner = Player.from_dict(data["winner"])
        
        # 重建破产玩家列表
        game_state.bankrupt_players = [
            game_state.get_player_by_id(pid) for pid in data["bankrupt_players"]
        ]
        
        return game_state
    
    def __str__(self) -> str:
        """字符串表示"""
        current_player = self.get_current_player()
        player_name = current_player.name if current_player else "无"
        return f"GameState(状态:{self.game_state}, 当前玩家:{player_name}, 回合:{self.turn_count})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"GameState(game_state='{self.game_state}', current_player_index={self.current_player_index}, turn_count={self.turn_count})" 