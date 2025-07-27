"""
游戏状态同步管理器
"""
import asyncio
import time
import json
import hashlib
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import asdict

from src.network.protocol import NetworkProtocol, MessageType
from src.models.game_state import GameState
from src.models.player import Player
from src.models.map import Map


class GameStateSyncManager:
    """游戏状态同步管理器"""
    
    def __init__(self, broadcast_callback: Callable = None):
        """
        初始化同步管理器
        
        Args:
            broadcast_callback: 广播消息的回调函数
        """
        self.broadcast_callback = broadcast_callback
        self.game_state: Optional[GameState] = None
        self.last_sync_time = 0
        self.sync_interval = 0.5  # 同步间隔（秒）
        self.force_sync = False  # 强制同步标志
        
        # 状态缓存，用于检测变化
        self.last_game_state_hash = None
        self.last_players_hash = {}
        self.last_map_hash = None
        
        # 同步配置
        self.sync_config = {
            "full_sync_interval": 10.0,  # 完整同步间隔
            "delta_sync_interval": 0.5,  # 增量同步间隔
            "player_sync_interval": 0.3,  # 玩家状态同步间隔
            "map_sync_interval": 1.0,    # 地图同步间隔
        }
        
        # 同步统计
        self.sync_stats = {
            "full_syncs": 0,
            "delta_syncs": 0,
            "player_syncs": 0,
            "map_syncs": 0,
            "bytes_sent": 0,
            "last_sync_duration": 0
        }
        
        # 同步队列和控制
        self.sync_queue = asyncio.Queue() if asyncio else None
        self.sync_task = None
        self.is_syncing = False
        
        # 订阅者管理
        self.subscribers: Set[str] = set()  # 订阅同步的客户端ID
        
    def set_game_state(self, game_state: GameState):
        """设置游戏状态"""
        self.game_state = game_state
        self.force_sync = True
    
    def set_broadcast_callback(self, callback: Callable):
        """设置广播回调函数"""
        self.broadcast_callback = callback
    
    def add_subscriber(self, client_id: str):
        """添加同步订阅者"""
        self.subscribers.add(client_id)
    
    def remove_subscriber(self, client_id: str):
        """移除同步订阅者"""
        self.subscribers.discard(client_id)
    
    def start_sync_loop(self):
        """启动同步循环"""
        if self.sync_task is None:
            self.sync_task = asyncio.create_task(self._sync_loop())
    
    def stop_sync_loop(self):
        """停止同步循环"""
        if self.sync_task:
            self.sync_task.cancel()
            self.sync_task = None
    
    async def _sync_loop(self):
        """同步循环"""
        while True:
            try:
                await self._perform_sync()
                await asyncio.sleep(self.sync_config["delta_sync_interval"])
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"同步循环错误: {e}")
                await asyncio.sleep(1.0)
    
    async def _perform_sync(self):
        """执行同步"""
        if not self.game_state or not self.broadcast_callback or self.is_syncing:
            return
        
        start_time = time.time()
        self.is_syncing = True
        
        try:
            current_time = time.time()
            
            # 检查是否需要完整同步
            if (self.force_sync or 
                current_time - self.last_sync_time > self.sync_config["full_sync_interval"]):
                await self._full_sync()
                self.force_sync = False
                self.last_sync_time = current_time
            else:
                # 增量同步
                await self._delta_sync()
        
        finally:
            self.is_syncing = False
            self.sync_stats["last_sync_duration"] = time.time() - start_time
    
    async def _full_sync(self):
        """完整同步"""
        if not self.game_state:
            return
        
        # 构建完整游戏状态
        game_data = {
            "type": "full",
            "timestamp": time.time(),
            "game_state": {
                "players": [self._serialize_player(player) for player in self.game_state.players],
                "current_player_index": self.game_state.current_player_index,
                "turn_phase": self.game_state.turn_phase,
                "game_status": self.game_state.game_status,
                "turn_count": self.game_state.turn_count,
                "round_count": self.game_state.round_count
            },
            "map_state": self._serialize_map() if self.game_state.map else None
        }
        
        await self._broadcast_sync_message(MessageType.GAME_STATE_SYNC, game_data)
        
        # 更新缓存
        self._update_state_cache()
        self.sync_stats["full_syncs"] += 1
    
    async def _delta_sync(self):
        """增量同步"""
        if not self.game_state:
            return
        
        changes = []
        
        # 检查玩家状态变化
        player_changes = self._check_player_changes()
        if player_changes:
            changes.extend(player_changes)
        
        # 检查游戏状态变化
        game_state_changes = self._check_game_state_changes()
        if game_state_changes:
            changes.extend(game_state_changes)
        
        # 检查地图状态变化
        map_changes = self._check_map_changes()
        if map_changes:
            changes.extend(map_changes)
        
        # 如果有变化，发送增量同步
        if changes:
            delta_data = {
                "type": "delta",
                "timestamp": time.time(),
                "changes": changes
            }
            
            await self._broadcast_sync_message(MessageType.GAME_STATE_SYNC, delta_data)
            self._update_state_cache()
            self.sync_stats["delta_syncs"] += 1
    
    def _check_player_changes(self) -> List[Dict]:
        """检查玩家状态变化"""
        changes = []
        
        if not self.game_state.players:
            return changes
        
        for player in self.game_state.players:
            player_data = self._serialize_player(player)
            player_hash = self._calculate_hash(player_data)
            
            last_hash = self.last_players_hash.get(player.player_id)
            
            if last_hash != player_hash:
                changes.append({
                    "type": "player_update",
                    "player_id": player.player_id,
                    "data": player_data
                })
                self.last_players_hash[player.player_id] = player_hash
        
        return changes
    
    def _check_game_state_changes(self) -> List[Dict]:
        """检查游戏状态变化"""
        changes = []
        
        # 构建当前游戏状态快照
        current_state = {
            "current_player_index": self.game_state.current_player_index,
            "turn_phase": self.game_state.turn_phase,
            "game_status": self.game_state.game_status,
            "turn_count": self.game_state.turn_count,
            "round_count": self.game_state.round_count
        }
        
        current_hash = self._calculate_hash(current_state)
        
        if self.last_game_state_hash != current_hash:
            changes.append({
                "type": "game_state_update",
                "data": current_state
            })
            self.last_game_state_hash = current_hash
        
        return changes
    
    def _check_map_changes(self) -> List[Dict]:
        """检查地图状态变化"""
        changes = []
        
        if not self.game_state.map:
            return changes
        
        map_data = self._serialize_map()
        map_hash = self._calculate_hash(map_data)
        
        if self.last_map_hash != map_hash:
            changes.append({
                "type": "map_update",
                "data": map_data
            })
            self.last_map_hash = map_hash
        
        return changes
    
    def _serialize_player(self, player: Player) -> Dict:
        """序列化玩家数据"""
        return {
            "player_id": player.player_id,
            "name": player.name,
            "money": player.money,
            "position": player.position,
            "properties": [prop.to_dict() if hasattr(prop, 'to_dict') else str(prop) 
                          for prop in player.properties],
            "items": [item.to_dict() if hasattr(item, 'to_dict') else str(item) 
                     for item in player.items],
            "is_ai": player.is_ai,
            "is_active": not player.is_bankrupt()
        }
    
    def _serialize_map(self) -> Dict:
        """序列化地图数据"""
        if not self.game_state.map:
            return {}
        
        return {
            "width": self.game_state.map.width,
            "height": self.game_state.map.height,
            "cells": [
                {
                    "x": cell.x,
                    "y": cell.y,
                    "cell_type": cell.cell_type,
                    "value": cell.value,
                    "owner_id": cell.owner_id,
                    "building_level": cell.building_level
                }
                for cell in self.game_state.map.cells
                if hasattr(cell, 'x')  # 确保是有效的格子
            ]
        }
    
    def _calculate_hash(self, data: Dict) -> str:
        """计算数据哈希值"""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(json_str.encode()).hexdigest()
    
    def _update_state_cache(self):
        """更新状态缓存"""
        if not self.game_state:
            return
        
        # 更新玩家哈希
        for player in self.game_state.players:
            player_data = self._serialize_player(player)
            self.last_players_hash[player.player_id] = self._calculate_hash(player_data)
        
        # 更新游戏状态哈希
        game_state_data = {
            "current_player_index": self.game_state.current_player_index,
            "turn_phase": self.game_state.turn_phase,
            "game_status": self.game_state.game_status,
            "turn_count": self.game_state.turn_count,
            "round_count": self.game_state.round_count
        }
        self.last_game_state_hash = self._calculate_hash(game_state_data)
        
        # 更新地图哈希
        if self.game_state.map:
            map_data = self._serialize_map()
            self.last_map_hash = self._calculate_hash(map_data)
    
    async def _broadcast_sync_message(self, message_type: MessageType, data: Dict):
        """广播同步消息"""
        if not self.broadcast_callback:
            return
        
        try:
            # 计算数据大小
            json_data = json.dumps(data)
            self.sync_stats["bytes_sent"] += len(json_data.encode())
            
            # 广播消息
            await self.broadcast_callback(message_type, data)
            
        except Exception as e:
            print(f"广播同步消息失败: {e}")
    
    # ==================== 特定同步方法 ====================
    
    async def sync_player_position(self, player_id: int, position: int):
        """同步玩家位置"""
        if not self.broadcast_callback:
            return
        
        data = {
            "type": "player_position",
            "player_id": player_id,
            "position": position,
            "timestamp": time.time()
        }
        
        await self._broadcast_sync_message(MessageType.PLAYER_MOVED, data)
        self.sync_stats["player_syncs"] += 1
    
    async def sync_player_money(self, player_id: int, money: int, change: int = 0):
        """同步玩家金钱"""
        data = {
            "type": "player_money",
            "player_id": player_id,
            "money": money,
            "change": change,
            "timestamp": time.time()
        }
        
        await self._broadcast_sync_message(MessageType.PLAYER_STATE_UPDATE, data)
        self.sync_stats["player_syncs"] += 1
    
    async def sync_dice_result(self, player_id: int, dice_values: List[int], total: int):
        """同步投骰子结果"""
        data = {
            "type": "dice_result",
            "player_id": player_id,
            "dice_values": dice_values,
            "total": total,
            "timestamp": time.time()
        }
        
        await self._broadcast_sync_message(MessageType.DICE_RESULT, data)
    
    async def sync_property_purchase(self, player_id: int, property_id: int, price: int):
        """同步房产购买"""
        data = {
            "type": "property_purchase",
            "player_id": player_id,
            "property_id": property_id,
            "price": price,
            "timestamp": time.time()
        }
        
        await self._broadcast_sync_message(MessageType.PROPERTY_BOUGHT, data)
    
    async def sync_turn_change(self, current_player_id: int, next_player_id: int, turn_phase: str):
        """同步回合切换"""
        data = {
            "type": "turn_change",
            "current_player_id": current_player_id,
            "next_player_id": next_player_id,
            "turn_phase": turn_phase,
            "timestamp": time.time()
        }
        
        await self._broadcast_sync_message(MessageType.TURN_CHANGE, data)
    
    async def sync_game_event(self, event_type: str, event_data: Dict):
        """同步游戏事件"""
        data = {
            "type": "game_event",
            "event_type": event_type,
            "event_data": event_data,
            "timestamp": time.time()
        }
        
        await self._broadcast_sync_message(MessageType.NOTIFICATION, data)
    
    # ==================== 管理方法 ====================
    
    def force_full_sync(self):
        """强制进行完整同步"""
        self.force_sync = True
    
    def get_sync_stats(self) -> Dict:
        """获取同步统计信息"""
        return self.sync_stats.copy()
    
    def reset_sync_stats(self):
        """重置同步统计"""
        self.sync_stats = {
            "full_syncs": 0,
            "delta_syncs": 0,
            "player_syncs": 0,
            "map_syncs": 0,
            "bytes_sent": 0,
            "last_sync_duration": 0
        }
    
    def update_sync_config(self, config: Dict):
        """更新同步配置"""
        self.sync_config.update(config)
    
    def get_sync_status(self) -> Dict:
        """获取同步状态"""
        return {
            "is_syncing": self.is_syncing,
            "last_sync_time": self.last_sync_time,
            "subscribers_count": len(self.subscribers),
            "sync_interval": self.sync_config["delta_sync_interval"],
            "stats": self.get_sync_stats()
        } 