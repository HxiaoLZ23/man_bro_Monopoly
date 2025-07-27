"""
动画系统
支持玩家移动、骰子投掷、特效等动画
"""
import pygame
import math
import random
from typing import List, Dict, Any, Optional, Callable, Tuple
from enum import Enum


class AnimationType(Enum):
    """动画类型"""
    PLAYER_MOVE = "player_move"
    DICE_ROLL = "dice_roll" 
    PARTICLE_EFFECT = "particle_effect"
    UI_FADE = "ui_fade"
    SCALE_BOUNCE = "scale_bounce"
    ROTATION = "rotation"
    SHAKE = "shake"


class EaseType(Enum):
    """缓动类型"""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    BOUNCE = "bounce"
    ELASTIC = "elastic"


class Animation:
    """动画基类"""
    
    def __init__(self, duration: float, ease_type: EaseType = EaseType.LINEAR, 
                 on_complete: Optional[Callable] = None, delay: float = 0):
        """
        初始化动画
        
        Args:
            duration: 动画持续时间（秒）
            ease_type: 缓动类型
            on_complete: 完成回调函数
            delay: 延迟时间（秒）
        """
        self.duration = duration * 1000  # 转换为毫秒
        self.ease_type = ease_type
        self.on_complete = on_complete
        self.delay = delay * 1000
        
        self.start_time = 0
        self.current_time = 0
        self.is_playing = False
        self.is_complete = False
        self.progress = 0.0
        
    def start(self):
        """开始动画"""
        self.start_time = pygame.time.get_ticks()
        self.is_playing = True
        self.is_complete = False
        
    def update(self):
        """更新动画"""
        if not self.is_playing or self.is_complete:
            return
            
        current_ticks = pygame.time.get_ticks()
        elapsed = current_ticks - self.start_time
        
        # 处理延迟
        if elapsed < self.delay:
            return
            
        # 计算进度
        actual_elapsed = elapsed - self.delay
        self.progress = min(actual_elapsed / self.duration, 1.0)
        
        # 应用缓动
        eased_progress = self._apply_easing(self.progress)
        
        # 更新动画
        self._update_animation(eased_progress)
        
        # 检查是否完成
        if self.progress >= 1.0:
            self.is_complete = True
            self.is_playing = False
            if self.on_complete:
                self.on_complete()
    
    def _apply_easing(self, t: float) -> float:
        """应用缓动函数"""
        if self.ease_type == EaseType.LINEAR:
            return t
        elif self.ease_type == EaseType.EASE_IN:
            return t * t
        elif self.ease_type == EaseType.EASE_OUT:
            return 1 - (1 - t) * (1 - t)
        elif self.ease_type == EaseType.EASE_IN_OUT:
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 2 * (1 - t) * (1 - t)
        elif self.ease_type == EaseType.BOUNCE:
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 2 * (1 - t) * (1 - t) * abs(math.sin(t * math.pi * 4))
        elif self.ease_type == EaseType.ELASTIC:
            if t == 0 or t == 1:
                return t
            return -(2 ** (10 * (t - 1))) * math.sin((t - 1.1) * 5 * math.pi)
        
        return t
    
    def _update_animation(self, progress: float):
        """更新动画状态 - 子类重写"""
        pass


class PlayerMoveAnimation(Animation):
    """玩家移动动画"""
    
    def __init__(self, player, start_pos: Tuple[int, int], end_pos: Tuple[int, int], 
                 duration: float = 0.5, on_complete: Optional[Callable] = None):
        super().__init__(duration, EaseType.EASE_OUT, on_complete)
        self.player = player
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.current_pos = start_pos
        
    def _update_animation(self, progress: float):
        """更新玩家位置"""
        x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * progress
        y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * progress
        self.current_pos = (x, y)


class DiceRollAnimation(Animation):
    """骰子投掷动画"""
    
    def __init__(self, dice_count: int = 1, duration: float = 2.0, 
                 dice_sides: int = 6, dice_type: str = "d6",
                 on_complete: Optional[Callable] = None):
        super().__init__(duration, EaseType.EASE_OUT, on_complete)
        self.dice_count = dice_count
        self.dice_sides = dice_sides
        self.dice_type = dice_type
        self.dice_states = []
        self.final_values = []
        self.shake_intensity = 10
        
        # 初始化骰子状态
        for i in range(dice_count):
            self.dice_states.append({
                'value': 1,
                'rotation': 0,
                'scale': 1.0,
                'offset_x': 0,
                'offset_y': 0,
                'spin_speed': random.uniform(5, 15),
                'position_x': 0,  # 多个骰子的位置偏移
                'position_y': 0
            })
            
        # 如果有多个骰子，设置它们的相对位置
        if dice_count > 1:
            for i, dice in enumerate(self.dice_states):
                # 计算骰子在圆形或线性排列中的位置
                if dice_count == 2:
                    dice['position_x'] = (-40 if i == 0 else 40)
                    dice['position_y'] = 0
                elif dice_count == 3:
                    angle = i * (2 * math.pi / 3) - math.pi / 2
                    dice['position_x'] = math.cos(angle) * 50
                    dice['position_y'] = math.sin(angle) * 50
                else:
                    # 更多骰子时排成网格
                    cols = 2 if dice_count <= 4 else 3
                    row = i // cols
                    col = i % cols
                    dice['position_x'] = (col - (cols - 1) / 2) * 70
                    dice['position_y'] = (row - (dice_count // cols - 1) / 2) * 70
    
    def set_final_values(self, values: List[int]):
        """设置最终结果"""
        self.final_values = values[:self.dice_count]
        
    def _update_animation(self, progress: float):
        """更新骰子动画"""
        for i, dice in enumerate(self.dice_states):
            if progress < 0.8:  # 前80%时间进行投掷动画
                # 快速变换数字 - 根据骰子面数随机
                if random.random() < 0.3:
                    dice['value'] = random.randint(1, self.dice_sides)
                
                # 旋转
                dice['rotation'] += dice['spin_speed']
                
                # 震动
                shake = self.shake_intensity * (1 - progress / 0.8)
                dice['offset_x'] = random.uniform(-shake, shake)
                dice['offset_y'] = random.uniform(-shake, shake)
                
                # 缩放效果
                dice['scale'] = 1.0 + 0.2 * math.sin(progress * math.pi * 10)
                
            else:  # 最后20%时间稳定到最终结果
                if self.final_values and i < len(self.final_values):
                    dice['value'] = self.final_values[i]
                
                # 停止震动
                settle_progress = (progress - 0.8) / 0.2
                dice['offset_x'] *= (1 - settle_progress)
                dice['offset_y'] *= (1 - settle_progress)
                dice['scale'] = 1.0 + 0.1 * (1 - settle_progress)


class ParticleEffect(Animation):
    """粒子特效"""
    
    def __init__(self, x: int, y: int, particle_count: int = 20, 
                 duration: float = 1.0, effect_type: str = "explosion"):
        super().__init__(duration, EaseType.LINEAR)
        self.x = x
        self.y = y
        self.effect_type = effect_type
        self.particles = []
        
        # 创建粒子
        for _ in range(particle_count):
            if effect_type == "explosion":
                self.particles.append({
                    'x': x,
                    'y': y,
                    'vx': random.uniform(-5, 5),
                    'vy': random.uniform(-5, 5),
                    'life': 1.0,
                    'size': random.uniform(2, 6),
                    'color': random.choice([(255, 255, 0), (255, 165, 0), (255, 0, 0)])
                })
            elif effect_type == "sparkle":
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1, 3)
                self.particles.append({
                    'x': x,
                    'y': y,
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed,
                    'life': 1.0,
                    'size': random.uniform(1, 3),
                    'color': random.choice([(255, 255, 255), (255, 255, 0), (0, 255, 255)])
                })
    
    def _update_animation(self, progress: float):
        """更新粒子"""
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2  # 重力
            particle['life'] = 1.0 - progress
            
            # 减小速度
            particle['vx'] *= 0.98
            particle['vy'] *= 0.98


class UIFadeAnimation(Animation):
    """UI淡入淡出动画"""
    
    def __init__(self, target_alpha: int, duration: float = 0.3, 
                 ease_type: EaseType = EaseType.EASE_IN_OUT, on_complete: Optional[Callable] = None):
        super().__init__(duration, ease_type, on_complete)
        self.start_alpha = 0
        self.target_alpha = target_alpha
        self.current_alpha = 0
        
    def set_start_alpha(self, alpha: int):
        """设置起始透明度"""
        self.start_alpha = alpha
        self.current_alpha = alpha
        
    def _update_animation(self, progress: float):
        """更新透明度"""
        self.current_alpha = int(self.start_alpha + (self.target_alpha - self.start_alpha) * progress)


class ScaleBounceAnimation(Animation):
    """缩放弹跳动画"""
    
    def __init__(self, start_scale: float = 1.0, target_scale: float = 1.2, 
                 duration: float = 0.3, on_complete: Optional[Callable] = None):
        super().__init__(duration, EaseType.BOUNCE, on_complete)
        self.start_scale = start_scale
        self.target_scale = target_scale
        self.current_scale = start_scale
        
    def _update_animation(self, progress: float):
        """更新缩放"""
        if progress < 0.5:
            # 放大阶段
            scale_progress = progress * 2
            self.current_scale = self.start_scale + (self.target_scale - self.start_scale) * scale_progress
        else:
            # 缩小阶段
            scale_progress = (progress - 0.5) * 2
            self.current_scale = self.target_scale - (self.target_scale - self.start_scale) * scale_progress


class ShakeAnimation(Animation):
    """震动动画"""
    
    def __init__(self, intensity: float = 5.0, duration: float = 0.5):
        super().__init__(duration, EaseType.LINEAR)
        self.intensity = intensity
        self.offset_x = 0
        self.offset_y = 0
        
    def _update_animation(self, progress: float):
        """更新震动偏移"""
        current_intensity = self.intensity * (1 - progress)
        self.offset_x = random.uniform(-current_intensity, current_intensity)
        self.offset_y = random.uniform(-current_intensity, current_intensity)


class AnimationManager:
    """动画管理器"""
    
    def __init__(self):
        self.animations: List[Animation] = []
        self.particle_effects: List[ParticleEffect] = []
        
    def add_animation(self, animation: Animation):
        """添加动画"""
        self.animations.append(animation)
        animation.start()
        
    def create_player_move_animation(self, player, start_pos: Tuple[int, int], 
                                   end_pos: Tuple[int, int], duration: float = 0.5,
                                   on_complete: Optional[Callable] = None) -> PlayerMoveAnimation:
        """创建玩家移动动画"""
        anim = PlayerMoveAnimation(player, start_pos, end_pos, duration, on_complete)
        self.add_animation(anim)
        return anim
    
    def create_dice_roll_animation(self, dice_count: int = 1, duration: float = 2.0,
                                 dice_sides: int = 6, dice_type: str = "d6",
                                 final_values: Optional[List[int]] = None,
                                 on_complete: Optional[Callable] = None) -> DiceRollAnimation:
        """创建骰子投掷动画"""
        anim = DiceRollAnimation(dice_count, duration, dice_sides, dice_type, on_complete)
        if final_values:
            anim.set_final_values(final_values)
        self.add_animation(anim)
        return anim
    
    def create_particle_effect(self, x: int, y: int, effect_type: str = "explosion",
                             particle_count: int = 20, duration: float = 1.0) -> ParticleEffect:
        """创建粒子特效"""
        effect = ParticleEffect(x, y, particle_count, duration, effect_type)
        self.particle_effects.append(effect)
        effect.start()
        return effect
    
    def create_ui_fade(self, target_alpha: int, duration: float = 0.3,
                      start_alpha: int = 0, on_complete: Optional[Callable] = None) -> UIFadeAnimation:
        """创建UI淡入淡出动画"""
        anim = UIFadeAnimation(target_alpha, duration, EaseType.EASE_IN_OUT, on_complete)
        anim.set_start_alpha(start_alpha)
        self.add_animation(anim)
        return anim
    
    def create_scale_bounce(self, target_scale: float = 1.2, duration: float = 0.3,
                          on_complete: Optional[Callable] = None) -> ScaleBounceAnimation:
        """创建缩放弹跳动画"""
        anim = ScaleBounceAnimation(1.0, target_scale, duration, on_complete)
        self.add_animation(anim)
        return anim
    
    def create_shake_effect(self, intensity: float = 5.0, duration: float = 0.5) -> ShakeAnimation:
        """创建震动效果"""
        anim = ShakeAnimation(intensity, duration)
        self.add_animation(anim)
        return anim
    
    def update(self):
        """更新所有动画"""
        # 更新普通动画
        self.animations = [anim for anim in self.animations if not anim.is_complete]
        for animation in self.animations:
            animation.update()
            
        # 更新粒子效果
        self.particle_effects = [effect for effect in self.particle_effects if not effect.is_complete]
        for effect in self.particle_effects:
            effect.update()
    
    def draw_particles(self, screen: pygame.Surface):
        """绘制粒子效果"""
        for effect in self.particle_effects:
            for particle in effect.particles:
                if particle['life'] > 0:
                    alpha = int(255 * particle['life'])
                    size = int(particle['size'] * particle['life'])
                    if size > 0:
                        # 创建带透明度的表面
                        particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                        color = (*particle['color'], alpha)
                        pygame.draw.circle(particle_surface, color, (size, size), size)
                        screen.blit(particle_surface, (int(particle['x'] - size), int(particle['y'] - size)))
    
    def clear_animations(self):
        """清除所有动画"""
        self.animations.clear()
        self.particle_effects.clear()
    
    def has_active_animations(self) -> bool:
        """检查是否有活跃的动画"""
        return len(self.animations) > 0 or len(self.particle_effects) > 0 