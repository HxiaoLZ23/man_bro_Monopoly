"""
游戏存档系统
"""
import json
import os
import time
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from src.models.game_state import GameState
from src.models.player import Player
from src.models.map import Map


class SaveSystem:
    """游戏存档系统"""
    
    def __init__(self, save_directory: str = "saves"):
        """
        初始化存档系统
        
        Args:
            save_directory: 存档目录
        """
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(exist_ok=True)
        
        # 存档格式支持
        self.supported_formats = ["json", "db"]
        self.default_format = "json"
        
        # 存档文件扩展名
        self.format_extensions = {
            "json": ".save",
            "db": ".savedb"
        }
        
        # 自动保存配置
        self.auto_save_enabled = True
        self.auto_save_interval = 300  # 5分钟
        self.auto_save_count = 5  # 保留5个自动存档
        self.last_auto_save_time = 0
        
        # 存档元数据缓存
        self.save_metadata_cache = {}
        self._load_metadata_cache()
    
    def save_game(self, game_state: GameState, save_name: str, 
                  description: str = "", format_type: str = None) -> Dict[str, Any]:
        """
        保存游戏
        
        Args:
            game_state: 游戏状态
            save_name: 存档名称
            description: 存档描述
            format_type: 保存格式（json/db）
            
        Returns:
            Dict[str, Any]: 保存结果
        """
        try:
            if format_type is None:
                format_type = self.default_format
            
            if format_type not in self.supported_formats:
                return {"success": False, "error": f"不支持的格式: {format_type}"}
            
            # 生成文件路径
            ext = self.format_extensions[format_type]
            file_path = self.save_directory / f"{save_name}{ext}"
            
            # 创建存档数据
            save_data = self._create_save_data(game_state, save_name, description)
            
            # 根据格式保存
            if format_type == "json":
                success = self._save_to_json(save_data, file_path)
            elif format_type == "db":
                success = self._save_to_database(save_data, file_path)
            else:
                return {"success": False, "error": f"未实现的格式: {format_type}"}
            
            if success:
                # 更新元数据缓存
                self._update_metadata_cache(save_name, save_data["metadata"])
                
                return {
                    "success": True,
                    "save_name": save_name,
                    "file_path": str(file_path),
                    "size": file_path.stat().st_size if file_path.exists() else 0
                }
            else:
                return {"success": False, "error": "保存失败"}
                
        except Exception as e:
            return {"success": False, "error": f"保存异常: {e}"}
    
    def load_game(self, save_name: str, format_type: str = None) -> Dict[str, Any]:
        """
        加载游戏
        
        Args:
            save_name: 存档名称
            format_type: 文件格式（自动检测如果为None）
            
        Returns:
            Dict[str, Any]: 加载结果
        """
        try:
            # 查找存档文件
            file_path = self._find_save_file(save_name, format_type)
            if not file_path:
                return {"success": False, "error": "存档文件不存在"}
            
            # 确定格式
            if format_type is None:
                format_type = self._detect_format(file_path)
            
            # 根据格式加载
            if format_type == "json":
                save_data = self._load_from_json(file_path)
            elif format_type == "db":
                save_data = self._load_from_database(file_path)
            else:
                return {"success": False, "error": f"不支持的格式: {format_type}"}
            
            if not save_data:
                return {"success": False, "error": "存档数据损坏"}
            
            # 重建游戏状态
            game_state = self._restore_game_state(save_data)
            if not game_state:
                return {"success": False, "error": "无法恢复游戏状态"}
            
            return {
                "success": True,
                "game_state": game_state,
                "metadata": save_data["metadata"],
                "save_name": save_name
            }
            
        except Exception as e:
            return {"success": False, "error": f"加载异常: {e}"}
    
    def delete_save(self, save_name: str) -> Dict[str, Any]:
        """
        删除存档
        
        Args:
            save_name: 存档名称
            
        Returns:
            Dict[str, Any]: 删除结果
        """
        try:
            # 查找所有格式的存档文件
            deleted_files = []
            for format_type in self.supported_formats:
                file_path = self._find_save_file(save_name, format_type)
                if file_path and file_path.exists():
                    file_path.unlink()
                    deleted_files.append(str(file_path))
            
            if deleted_files:
                # 从元数据缓存中移除
                if save_name in self.save_metadata_cache:
                    del self.save_metadata_cache[save_name]
                self._save_metadata_cache()
                
                return {
                    "success": True,
                    "deleted_files": deleted_files
                }
            else:
                return {"success": False, "error": "存档不存在"}
                
        except Exception as e:
            return {"success": False, "error": f"删除异常: {e}"}
    
    def list_saves(self) -> List[Dict[str, Any]]:
        """
        列出所有存档
        
        Returns:
            List[Dict[str, Any]]: 存档列表
        """
        saves = []
        
        try:
            # 扫描存档目录
            for file_path in self.save_directory.iterdir():
                if file_path.is_file():
                    # 检查是否是存档文件
                    format_type = None
                    save_name = None
                    
                    for fmt, ext in self.format_extensions.items():
                        if file_path.suffix == ext:
                            format_type = fmt
                            save_name = file_path.stem
                            break
                    
                    if format_type and save_name:
                        # 获取文件信息
                        stat = file_path.stat()
                        
                        # 尝试从缓存获取元数据
                        metadata = self.save_metadata_cache.get(save_name)
                        if not metadata:
                            # 快速读取元数据
                            metadata = self._read_metadata_only(file_path, format_type)
                        
                        save_info = {
                            "save_name": save_name,
                            "file_path": str(file_path),
                            "format": format_type,
                            "size": stat.st_size,
                            "created_time": datetime.fromtimestamp(stat.st_ctime),
                            "modified_time": datetime.fromtimestamp(stat.st_mtime),
                            "metadata": metadata or {}
                        }
                        
                        saves.append(save_info)
            
            # 按修改时间排序（最新的在前）
            saves.sort(key=lambda x: x["modified_time"], reverse=True)
            
        except Exception as e:
            print(f"列出存档失败: {e}")
        
        return saves
    
    def auto_save(self, game_state: GameState) -> Dict[str, Any]:
        """
        自动保存
        
        Args:
            game_state: 游戏状态
            
        Returns:
            Dict[str, Any]: 保存结果
        """
        if not self.auto_save_enabled:
            return {"success": False, "error": "自动保存已禁用"}
        
        current_time = time.time()
        if current_time - self.last_auto_save_time < self.auto_save_interval:
            return {"success": False, "error": "自动保存间隔未到"}
        
        try:
            # 生成自动保存名称
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            auto_save_name = f"auto_save_{timestamp}"
            
            # 执行保存
            result = self.save_game(
                game_state, 
                auto_save_name, 
                "自动保存", 
                self.default_format
            )
            
            if result["success"]:
                self.last_auto_save_time = current_time
                
                # 清理旧的自动保存
                self._cleanup_auto_saves()
            
            return result
            
        except Exception as e:
            return {"success": False, "error": f"自动保存异常: {e}"}
    
    def quick_save(self, game_state: GameState) -> Dict[str, Any]:
        """
        快速保存
        
        Args:
            game_state: 游戏状态
            
        Returns:
            Dict[str, Any]: 保存结果
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        quick_save_name = f"quick_save_{timestamp}"
        
        return self.save_game(
            game_state,
            quick_save_name,
            "快速保存",
            self.default_format
        )
    
    def export_save(self, save_name: str, export_path: str, 
                   format_type: str = "json") -> Dict[str, Any]:
        """
        导出存档
        
        Args:
            save_name: 存档名称
            export_path: 导出路径
            format_type: 导出格式
            
        Returns:
            Dict[str, Any]: 导出结果
        """
        try:
            # 加载存档
            load_result = self.load_game(save_name)
            if not load_result["success"]:
                return load_result
            
            # 重新创建存档数据
            save_data = self._create_save_data(
                load_result["game_state"],
                save_name,
                load_result["metadata"].get("description", "")
            )
            
            # 导出到指定路径
            export_file = Path(export_path)
            if format_type == "json":
                success = self._save_to_json(save_data, export_file)
            elif format_type == "db":
                success = self._save_to_database(save_data, export_file)
            else:
                return {"success": False, "error": f"不支持的导出格式: {format_type}"}
            
            if success:
                return {
                    "success": True,
                    "export_path": str(export_file),
                    "size": export_file.stat().st_size
                }
            else:
                return {"success": False, "error": "导出失败"}
                
        except Exception as e:
            return {"success": False, "error": f"导出异常: {e}"}
    
    def import_save(self, import_path: str, save_name: str = None) -> Dict[str, Any]:
        """
        导入存档
        
        Args:
            import_path: 导入文件路径
            save_name: 新的存档名称（如果为None则使用原名称）
            
        Returns:
            Dict[str, Any]: 导入结果
        """
        try:
            import_file = Path(import_path)
            if not import_file.exists():
                return {"success": False, "error": "导入文件不存在"}
            
            # 检测格式
            format_type = self._detect_format(import_file)
            if not format_type:
                return {"success": False, "error": "无法识别文件格式"}
            
            # 加载数据
            if format_type == "json":
                save_data = self._load_from_json(import_file)
            elif format_type == "db":
                save_data = self._load_from_database(import_file)
            else:
                return {"success": False, "error": f"不支持的格式: {format_type}"}
            
            if not save_data:
                return {"success": False, "error": "导入文件损坏"}
            
            # 确定存档名称
            if save_name is None:
                save_name = save_data["metadata"].get("save_name", "imported_save")
            
            # 重建游戏状态
            game_state = self._restore_game_state(save_data)
            if not game_state:
                return {"success": False, "error": "无法恢复游戏状态"}
            
            # 保存导入的存档
            result = self.save_game(
                game_state,
                save_name,
                save_data["metadata"].get("description", "导入的存档")
            )
            
            if result["success"]:
                return {
                    "success": True,
                    "save_name": save_name,
                    "original_name": save_data["metadata"].get("save_name", "未知")
                }
            else:
                return result
                
        except Exception as e:
            return {"success": False, "error": f"导入异常: {e}"}
    
    def _create_save_data(self, game_state: GameState, save_name: str, 
                         description: str) -> Dict[str, Any]:
        """创建存档数据"""
        current_time = datetime.now()
        
        metadata = {
            "save_name": save_name,
            "description": description,
            "created_time": current_time.isoformat(),
            "version": "1.0",
            "game_version": "1.0.0",
            "save_format_version": "1.0",
            "total_players": len(game_state.players),
            "turn_count": game_state.turn_count,
            "game_duration": game_state.get_game_duration(),
            "current_player": game_state.get_current_player().name if game_state.get_current_player() else None
        }
        
        return {
            "metadata": metadata,
            "game_state": game_state.to_dict(),
            "checksum": self._calculate_checksum(game_state.to_dict())
        }
    
    def _restore_game_state(self, save_data: Dict[str, Any]) -> Optional[GameState]:
        """从存档数据恢复游戏状态"""
        try:
            # 验证校验和
            game_data = save_data["game_state"]
            expected_checksum = save_data.get("checksum")
            if expected_checksum:
                actual_checksum = self._calculate_checksum(game_data)
                if actual_checksum != expected_checksum:
                    print("警告: 存档校验和不匹配，数据可能已损坏")
            
            # 重建游戏状态
            game_state = GameState.from_dict(game_data)
            return game_state
            
        except Exception as e:
            print(f"恢复游戏状态失败: {e}")
            return None
    
    def _save_to_json(self, save_data: Dict[str, Any], file_path: Path) -> bool:
        """保存为JSON格式"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存JSON失败: {e}")
            return False
    
    def _load_from_json(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """从JSON格式加载"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载JSON失败: {e}")
            return None
    
    def _save_to_database(self, save_data: Dict[str, Any], file_path: Path) -> bool:
        """保存到数据库"""
        try:
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            
            # 创建表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS save_data (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            
            # 保存元数据
            for key, value in save_data["metadata"].items():
                cursor.execute(
                    'INSERT OR REPLACE INTO save_data VALUES (?, ?)',
                    (f"metadata_{key}", json.dumps(value))
                )
            
            # 保存游戏状态
            cursor.execute(
                'INSERT OR REPLACE INTO save_data VALUES (?, ?)',
                ("game_state", json.dumps(save_data["game_state"]))
            )
            
            # 保存校验和
            if "checksum" in save_data:
                cursor.execute(
                    'INSERT OR REPLACE INTO save_data VALUES (?, ?)',
                    ("checksum", save_data["checksum"])
                )
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"保存数据库失败: {e}")
            return False
    
    def _load_from_database(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """从数据库加载"""
        try:
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            
            # 读取所有数据
            cursor.execute('SELECT key, value FROM save_data')
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return None
            
            # 重建数据结构
            save_data = {
                "metadata": {},
                "game_state": {},
                "checksum": None
            }
            
            for key, value in rows:
                if key.startswith("metadata_"):
                    meta_key = key[9:]  # 移除 "metadata_" 前缀
                    save_data["metadata"][meta_key] = json.loads(value)
                elif key == "game_state":
                    save_data["game_state"] = json.loads(value)
                elif key == "checksum":
                    save_data["checksum"] = value
            
            return save_data
            
        except Exception as e:
            print(f"加载数据库失败: {e}")
            return None
    
    def _find_save_file(self, save_name: str, format_type: str = None) -> Optional[Path]:
        """查找存档文件"""
        if format_type:
            # 指定格式
            ext = self.format_extensions.get(format_type)
            if ext:
                file_path = self.save_directory / f"{save_name}{ext}"
                return file_path if file_path.exists() else None
        else:
            # 尝试所有格式
            for fmt, ext in self.format_extensions.items():
                file_path = self.save_directory / f"{save_name}{ext}"
                if file_path.exists():
                    return file_path
        
        return None
    
    def _detect_format(self, file_path: Path) -> Optional[str]:
        """检测文件格式"""
        suffix = file_path.suffix
        for fmt, ext in self.format_extensions.items():
            if suffix == ext:
                return fmt
        return None
    
    def _read_metadata_only(self, file_path: Path, format_type: str) -> Optional[Dict[str, Any]]:
        """仅读取存档元数据"""
        try:
            if format_type == "json":
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("metadata", {})
            
            elif format_type == "db":
                conn = sqlite3.connect(file_path)
                cursor = conn.cursor()
                cursor.execute('SELECT key, value FROM save_data WHERE key LIKE "metadata_%"')
                rows = cursor.fetchall()
                conn.close()
                
                metadata = {}
                for key, value in rows:
                    meta_key = key[9:]  # 移除 "metadata_" 前缀
                    metadata[meta_key] = json.loads(value)
                
                return metadata
                
        except Exception as e:
            print(f"读取元数据失败: {e}")
            return None
    
    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """计算数据校验和"""
        import hashlib
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(json_str.encode()).hexdigest()
    
    def _cleanup_auto_saves(self):
        """清理旧的自动保存"""
        try:
            # 获取所有自动保存
            auto_saves = [
                save for save in self.list_saves()
                if save["save_name"].startswith("auto_save_")
            ]
            
            # 按创建时间排序（最新的在前）
            auto_saves.sort(key=lambda x: x["created_time"], reverse=True)
            
            # 删除超出数量限制的自动保存
            for save in auto_saves[self.auto_save_count:]:
                self.delete_save(save["save_name"])
                
        except Exception as e:
            print(f"清理自动保存失败: {e}")
    
    def _load_metadata_cache(self):
        """加载元数据缓存"""
        cache_file = self.save_directory / "metadata_cache.json"
        try:
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.save_metadata_cache = json.load(f)
        except Exception as e:
            print(f"加载元数据缓存失败: {e}")
            self.save_metadata_cache = {}
    
    def _save_metadata_cache(self):
        """保存元数据缓存"""
        cache_file = self.save_directory / "metadata_cache.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.save_metadata_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存元数据缓存失败: {e}")
    
    def _update_metadata_cache(self, save_name: str, metadata: Dict[str, Any]):
        """更新元数据缓存"""
        self.save_metadata_cache[save_name] = metadata
        self._save_metadata_cache()
    
    def get_save_info(self, save_name: str) -> Optional[Dict[str, Any]]:
        """
        获取存档信息
        
        Args:
            save_name: 存档名称
            
        Returns:
            Optional[Dict[str, Any]]: 存档信息
        """
        saves = self.list_saves()
        for save in saves:
            if save["save_name"] == save_name:
                return save
        return None
    
    def set_auto_save_config(self, enabled: bool = True, interval: int = 300, 
                           count: int = 5):
        """
        设置自动保存配置
        
        Args:
            enabled: 是否启用自动保存
            interval: 自动保存间隔（秒）
            count: 保留的自动保存数量
        """
        self.auto_save_enabled = enabled
        self.auto_save_interval = interval
        self.auto_save_count = count
    
    def get_save_statistics(self) -> Dict[str, Any]:
        """
        获取存档统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        saves = self.list_saves()
        
        total_size = sum(save["size"] for save in saves)
        auto_saves = [save for save in saves if save["save_name"].startswith("auto_save_")]
        quick_saves = [save for save in saves if save["save_name"].startswith("quick_save_")]
        manual_saves = [save for save in saves if not (
            save["save_name"].startswith("auto_save_") or 
            save["save_name"].startswith("quick_save_")
        )]
        
        return {
            "total_saves": len(saves),
            "auto_saves": len(auto_saves),
            "quick_saves": len(quick_saves),
            "manual_saves": len(manual_saves),
            "total_size": total_size,
            "save_directory": str(self.save_directory),
            "auto_save_enabled": self.auto_save_enabled,
            "auto_save_interval": self.auto_save_interval
        } 