"""
互动操作情绪调整配置
用于存储不同互动操作对应的PAD情绪变化值
"""

from typing import Dict, Tuple

# 互动操作类型映射
class InteractionEmotionConfig:
    """互动情绪配置类"""
    
    # 互动操作对应的PAD情绪变化值 (pleasure, arousal, dominance)
    EMOTION_ADJUSTMENTS: Dict[str, Tuple[int, int, int]] = {
        # 安慰一下 - 显著增加愉悦度和安心感，降低精力消耗
        "comfort": (25, -5, 10),
        
        # 拉去加班 - 大幅降低愉悦度，增加精力消耗，降低掌控感
        "overtime": (-30, 15, -20),
        
        # 投喂食物 - 增加愉悦度和满足感，提升掌控感
        "feed": (20, 3, 8),
        
        # 泼冷水 - 降低愉悦度，轻微增加焦虑，降低掌控感
        "water": (-15, 8, -12)
    }
    
    @classmethod
    def get_emotion_adjustment(cls, interaction_type: str) -> Tuple[int, int, int]:
        """
        获取指定互动类型的情绪调整值
        
        Args:
            interaction_type: 互动类型
            
        Returns:
            Tuple[int, int, int]: (pleasure_change, arousal_change, dominance_change)
        """
        return cls.EMOTION_ADJUSTMENTS.get(interaction_type, (0, 0, 0))
    
    @classmethod
    def get_all_adjustments(cls) -> Dict[str, Tuple[int, int, int]]:
        """
        获取所有互动类型的情绪调整配置
        
        Returns:
            Dict[str, Tuple[int, int, int]]: 所有情绪调整配置
        """
        return cls.EMOTION_ADJUSTMENTS.copy()
    
    @classmethod
    def validate_interaction_type(cls, interaction_type: str) -> bool:
        """
        验证互动类型是否有效
        
        Args:
            interaction_type: 互动类型
            
        Returns:
            bool: 是否有效
        """
        return interaction_type in cls.EMOTION_ADJUSTMENTS