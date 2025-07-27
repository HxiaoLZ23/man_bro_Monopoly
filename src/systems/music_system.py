import pygame
import os
import random
from typing import List, Optional

class MusicSystem:
    """音乐播放器系统"""
    
    def __init__(self):
        # 初始化pygame mixer
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # 当前播放状态
        self.current_playlist: List[str] = []
        self.current_track_index: int = 0
        self.is_playing: bool = False
        self.volume: float = 0.5  # 降低默认音量
        self.current_scene: str = ""  # 当前场景
        self.is_destroyed: bool = False  # 销毁状态标记
        
        # 音频文件路径
        self.index_music_path = "assets/sounds/background/index"
        self.main_music_path = "assets/sounds/background/main1"
        
        # 设置音量
        pygame.mixer.music.set_volume(self.volume)
        
        # 使用不同的事件ID，避免与游戏逻辑冲突
        self.MUSIC_END_EVENT = pygame.USEREVENT + 20
        pygame.mixer.music.set_endevent(self.MUSIC_END_EVENT)
    
    def cleanup(self):
        """清理音乐系统资源"""
        if self.is_destroyed:
            return
            
        self.is_destroyed = True
        print("🎵 正在清理音乐系统...")
        
        try:
            # 停止音乐播放
            pygame.mixer.music.stop()
            
            # 清除事件监听
            pygame.mixer.music.set_endevent()
            
            # 卸载当前音乐
            try:
                pygame.mixer.music.unload()
            except:
                pass  # 忽略卸载错误
            
            # 重置状态
            self.is_playing = False
            self.current_playlist.clear()
            self.current_track_index = 0
            self.current_scene = ""
            
            print("✅ 音乐系统清理完成")
        except Exception as e:
            print(f"⚠️ 音乐系统清理时出现错误: {e}")
    
    def get_audio_files(self, directory: str) -> List[str]:
        """获取目录下的所有音频文件"""
        if self.is_destroyed:
            return []
            
        audio_files = []
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.lower().endswith(('.wav', '.mp3', '.ogg')):
                    audio_files.append(os.path.join(directory, file))
        return audio_files
    
    def play_index_music(self):
        """播放开始界面音乐"""
        if self.is_destroyed:
            return
            
        if self.current_scene == "index":
            return  # 已经在播放开始界面音乐
            
        self.current_scene = "index"
        audio_files = self.get_audio_files(self.index_music_path)
        if audio_files:
            self.current_playlist = audio_files
            self.current_track_index = 0
            self._play_current_track()
            print(f"🎵 开始播放开始界面音乐: {len(audio_files)} 首")
    
    def play_main_music(self):
        """播放游戏界面音乐"""
        if self.is_destroyed:
            return
            
        if self.current_scene == "main":
            return  # 已经在播放游戏界面音乐
            
        self.current_scene = "main"
        audio_files = self.get_audio_files(self.main_music_path)
        if audio_files:
            self.current_playlist = audio_files
            self.current_track_index = 0
            # 随机打乱播放列表
            random.shuffle(self.current_playlist)
            self._play_current_track()
            print(f"🎵 开始播放游戏界面音乐: {len(audio_files)} 首")
    
    def _play_current_track(self):
        """播放当前曲目"""
        if self.is_destroyed or not self.current_playlist:
            return
            
        if 0 <= self.current_track_index < len(self.current_playlist):
            try:
                # 检查mixer是否仍然初始化
                if not pygame.mixer.get_init():
                    return
                    
                track_path = self.current_playlist[self.current_track_index]
                pygame.mixer.music.load(track_path)
                pygame.mixer.music.play()
                self.is_playing = True
                print(f"🎵 正在播放: {os.path.basename(track_path)}")
            except pygame.error as e:
                if not self.is_destroyed:  # 只在未销毁时记录错误
                    print(f"❌ 播放音乐失败: {e}")
                    self._next_track()
            except Exception as e:
                if not self.is_destroyed:
                    print(f"❌ 播放音乐时发生未知错误: {e}")
    
    def _next_track(self):
        """播放下一首"""
        if self.is_destroyed:
            return
            
        if self.current_playlist:
            self.current_track_index = (self.current_track_index + 1) % len(self.current_playlist)
            self._play_current_track()
    
    def handle_music_event(self, event):
        """处理音乐相关事件"""
        if self.is_destroyed:
            return False
            
        if event.type == self.MUSIC_END_EVENT:
            if self.is_playing and not self.is_destroyed:
                self._next_track()
            return True
        return False
    
    def stop_music(self):
        """停止音乐播放"""
        if self.is_destroyed:
            return
            
        try:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.current_scene = ""
            print("🎵 音乐已停止")
        except pygame.error:
            pass  # 忽略停止时的错误
    
    def pause_music(self):
        """暂停音乐"""
        if self.is_destroyed:
            return
            
        if self.is_playing:
            try:
                pygame.mixer.music.pause()
                print("🎵 音乐已暂停")
            except pygame.error:
                pass
    
    def resume_music(self):
        """恢复音乐播放"""
        if self.is_destroyed:
            return
            
        if self.is_playing:
            try:
                pygame.mixer.music.unpause()
                print("🎵 音乐已恢复")
            except pygame.error:
                pass
    
    def set_volume(self, volume: float):
        """设置音量 (0.0 - 1.0)"""
        if self.is_destroyed:
            return
            
        self.volume = max(0.0, min(1.0, volume))
        try:
            pygame.mixer.music.set_volume(self.volume)
            print(f"🔊 音量设置为: {self.volume:.1f}")
        except pygame.error:
            pass
    
    def get_volume(self) -> float:
        """获取当前音量"""
        return self.volume
    
    def is_music_playing(self) -> bool:
        """检查音乐是否正在播放"""
        if self.is_destroyed:
            return False
            
        try:
            return pygame.mixer.music.get_busy() and self.is_playing
        except pygame.error:
            return False 