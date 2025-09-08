"""
情感状态模型
定义PAD三维情绪状态和情感实体
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class PADDimensions:
    """PAD三维情绪维度"""
    pleasure: float  # 愉悦度: -100到+100
    arousal: float   # 激活度: -100到+100  
    dominance: float # 支配感: -100到+100
    
    def __post_init__(self):
        """验证数值范围"""
        for attr_name, value in {
            'pleasure': self.pleasure,
            'arousal': self.arousal,
            'dominance': self.dominance
        }.items():
            if not -100 <= value <= 100:
                raise ValueError(f"{attr_name}必须在-100到100之间，当前值: {value}")
    
    @property
    def composite_score(self) -> float:
        """综合情绪分数 = P*0.4 + A*0.35 + D*0.25"""
        return (self.pleasure * 0.4 + 
                self.arousal * 0.35 + 
                self.dominance * 0.25)


@dataclass
class EmotionState:
    """情感状态实体"""
    
    character_id: str
    timestamp: datetime
    pleasure: float
    arousal: float
    dominance: float
    
    # 映射结果
    traditional_emotion: str
    vibe_emotion: str
    emoji: str
    color: str
    emotion_description: str
    emotion_type: str  # 情绪类型：兴奋、快乐、愤怒、焦虑、无聊、平静
    
    # 元数据
    confidence: float
    composite_score: float
    duration: Optional[int] = None
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'character_id': self.character_id,
            'timestamp': self.timestamp.isoformat(),
            'pleasure': self.pleasure,
            'arousal': self.arousal,
            'dominance': self.dominance,
            'composite_score': self.composite_score,
            'traditional_emotion': self.traditional_emotion,
            'vibe_emotion': self.vibe_emotion,
            'emoji': self.emoji,
            'color': self.color,
            'emotion_description': self.emotion_description,
            'emotion_type': self.emotion_type,
            'confidence': self.confidence,
            'duration': self.duration
        }