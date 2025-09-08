"""
情绪业务服务
提供情绪相关的业务逻辑，集成DAO层
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from src.emotion.db.emotion_dao import emotion_dao
from src.service.emotion.emotion_service import EmotionService
from src.emotion.model.emotion_mapping import EmotionMappings
from src.service.emotion.emotion_service import EmotionService

class EmotionBusinessService:
    """情绪业务服务类 - 集成DAO层和业务逻辑"""
    
    def __init__(self):
        self.emotion_service = EmotionService()
    
    def initialize_character_emotion(self, character_id: str) -> bool:
        """
        1. 初始化角色情绪状态
        
        Args:
            character_id: 角色ID
            
        Returns:
            是否初始化成功
        """
        try:
            return emotion_dao.initialize_character_emotion(character_id)
        except Exception as e:
            raise Exception(f"初始化角色情绪失败: {e}")
    
    def batch_initialize_characters(self, character_ids: List[str]) -> Dict[str, bool]:
        """
        2. 批量初始化角色情绪 - 数据库层面批量操作
        
        Args:
            character_ids: 角色ID列表
            
        Returns:
            每个角色的初始化结果
        """
        try:
            return emotion_dao.batch_initialize_characters(character_ids)
        except Exception as e:
            raise Exception(f"批量初始化角色情绪失败: {e}")
    
    def update_emotion_from_event(self, character_id: str, 
                                pleasure_change: int,
                                arousal_change: int,
                                dominance_change: int) -> bool:
        """
        3. 更新角色情绪状态
        
        Args:
            character_id: 角色ID
            pleasure_change: 愉悦度变化
            arousal_change: 激活度变化
            dominance_change: 支配感变化
            
        Returns:
            是否更新成功
        """
        try:
            pad_impact = {
                "pleasure": pleasure_change,
                "arousal": arousal_change,
                "dominance": dominance_change
            }
            
            return emotion_dao.update_emotion_from_event(character_id, pad_impact)
            
        except Exception as e:
            raise Exception(f"更新角色情绪失败: {e}")
    
    def batch_update_emotions(self, updates: List[Dict[str, Any]]) -> Dict[str, bool]:
        """
        4. 批量更新角色情绪状态 - 数据库层面批量操作
        
        Args:
            updates: 更新数据列表，每项包含character_id和pad_impact
            
        Returns:
            每个角色的更新结果
        """
        try:
            return emotion_dao.batch_update_emotions_from_events(updates)
        except Exception as e:
            raise Exception(f"批量更新角色情绪失败: {e}")
    
    def get_character_emotion(self, character_id: str) -> Optional[Dict[str, Any]]:
        """
        5. 获取角色情绪完整信息
        
        Args:
            character_id: 角色ID
            
        Returns:
            角色情绪数据
        """
        try:
            emotion_data = emotion_dao.get_emotion_by_character_id(character_id)
            return emotion_data
            
        except Exception as e:
            raise Exception(f"获取角色情绪失败: {e}")
    
    def get_characters_emotion_batch(self, character_ids: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        6. 批量获取角色情绪完整信息
        
        Args:
            character_ids: 角色ID列表
            
        Returns:
            每个角色的情绪数据，包含EmotionMapping映射信息
        """
        try:
            emotion_calc_service = EmotionService()
            
            # 获取原始情绪数据
            raw_emotions = emotion_dao.get_emotions_batch(character_ids)
            
            # 为每个角色添加EmotionMapping映射信息
            enriched_emotions = {}
            for character_id, emotion_data in raw_emotions.items():
                if emotion_data:
                    # 计算情绪映射
                    emotion_state = emotion_calc_service.calculate_emotion_from_pad(
                        character_id,
                        emotion_data["pleasure_score"],
                        emotion_data["arousal_score"],
                        emotion_data["dominance_score"]
                    )
                    
                    # 获取对应的EmotionMapping
                    mappings = EmotionMappings()
                    emotion_mapping = mappings.find_matching_emotion(
                        emotion_state.pleasure,
                        emotion_state.arousal,
                        emotion_state.dominance
                    )
                    
                    # 添加映射信息到返回数据
                    enriched_emotions[character_id] = {
                        **emotion_data,
                        "traditional": emotion_mapping.traditional,
                        "vibe": emotion_mapping.vibe,
                        "emoji": emotion_mapping.emoji,
                        "color": emotion_mapping.color,
                        "description": emotion_mapping.description,
                        "emotion_type": emotion_mapping.emotion_type
                    }
                else:
                    enriched_emotions[character_id] = emotion_data
            
            return enriched_emotions
            
        except Exception as e:
            raise Exception(f"批量获取角色情绪失败: {e}")
    
    def calculate_and_get_emotion(self, character_id: str) -> Optional[Dict[str, Any]]:
        """
        7. 计算并获取完整的情绪状态
        
        Args:
            character_id: 角色ID
            
        Returns:
            包含计算结果的完整情绪状态
        """
        try:
            # 获取数据库中的情绪数据
            emotion_data = self.get_character_emotion(character_id)
            if not emotion_data:
                return None
            
            # 使用服务层计算完整情绪状态
            emotion_state = self.emotion_service.calculate_emotion_from_pad(
                character_id,
                emotion_data["pleasure_score"],
                emotion_data["arousal_score"],
                emotion_data["dominance_score"]
            )
            
            return {
                "character_id": character_id,
                "database_data": emotion_data,
                "calculated_emotion": emotion_state.to_dict(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"计算情绪状态失败: {e}")


# 创建全局服务实例
emotion_service = EmotionBusinessService()