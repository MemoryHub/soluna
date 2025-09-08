import os
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)

from src.interaction.db.interaction_dao import InteractionDAO
from src.interaction.model.interaction_models import InteractionRecord, InteractionStats, InteractionType
from src.emotion.config.interaction_emotion_config import InteractionEmotionConfig
from src.service.emotion.service import emotion_service
from src.emotion.model.emotion_mapping import EmotionMappings

# 初始化DAO
interaction_dao = InteractionDAO()

class InteractionService:
    """互动功能服务类"""
    
    @staticmethod
    def perform_interaction(user_id: str, character_id: str, interaction_type: str) -> Dict[str, Any]:
        """执行互动操作
        
        Args:
            user_id: 用户ID
            character_id: 角色ID
            interaction_type: 互动类型
            
        Returns:
            Dict[str, Any]: 包含操作结果的字典
        """
        try:
            # 验证互动类型
            if interaction_type not in [t.value for t in InteractionType]:
                return {
                    "success": False,
                    "message": f"无效的互动类型: {interaction_type}"
                }
            
            # 检查今日是否已互动
            if interaction_dao.has_interaction_today(user_id, character_id, interaction_type):
                return {
                    "success": False,
                    "message": f"今日已对该角色进行过{interaction_type}互动"
                }
            
            # 创建互动记录
            record = InteractionRecord(user_id, character_id, interaction_type)
            record_id = interaction_dao.create_interaction_record(record)
            
            # 更新互动统计
            interaction_dao.update_interaction_stats(character_id, interaction_type)
            
            # 获取互动操作的情绪调整值
            pleasure_change, arousal_change, dominance_change = InteractionEmotionConfig.get_emotion_adjustment(interaction_type)
            
            # 更新角色情绪状态
            emotion_updated = False
            if any([pleasure_change, arousal_change, dominance_change]):
                try:
                    emotion_updated = emotion_service.update_emotion_from_event(
                        character_id=character_id,
                        pleasure_change=pleasure_change,
                        arousal_change=arousal_change,
                        dominance_change=dominance_change
                    )
                    print(f"角色 {character_id} 情绪更新结果: {emotion_updated}, 调整值: P={pleasure_change}, A={arousal_change}, D={dominance_change}")
                except Exception as e:
                    print(f"更新角色情绪时出错: {e}")
                    # 情绪更新失败不影响互动成功
            
            # 获取更新后的统计数据
            stats = interaction_dao.get_interaction_stats(character_id)
            
            # 获取完整的情绪信息
            current_emotion = None
            if emotion_updated:
                try:
                    current_emotion = emotion_service.get_character_emotion(character_id)
                    if current_emotion:
                        # 获取情绪映射信息
                        emotion_calc_service = emotion_service.emotion_service
                        emotion_state = emotion_calc_service.calculate_emotion_from_pad(
                            character_id,
                            current_emotion["pleasure_score"],
                            current_emotion["arousal_score"],
                            current_emotion["dominance_score"]
                        )
                        
                        # 获取对应的EmotionMapping
                        mappings = EmotionMappings()
                        emotion_mapping = mappings.find_matching_emotion(
                            emotion_state.pleasure,
                            emotion_state.arousal,
                            emotion_state.dominance
                        )
                        
                        # 添加完整的情绪信息
                        current_emotion.update({
                            "traditional": emotion_mapping.traditional,
                            "vibe": emotion_mapping.vibe,
                            "emoji": emotion_mapping.emoji,
                            "color": emotion_mapping.color,
                            "description": emotion_mapping.description,
                            "emotion_type": emotion_mapping.emotion_type
                        })
                except Exception as e:
                    print(f"获取完整情绪信息失败: {e}")
                    current_emotion = None
            
            return {
                "success": True,
                "message": "互动成功",
                "record_id": record_id,
                "stats": stats.to_dict() if stats else None,
                "emotion_updated": emotion_updated,
                "emotion_adjustment": {
                    "pleasure_change": pleasure_change,
                    "arousal_change": arousal_change,
                    "dominance_change": dominance_change
                },
                "current_emotion": current_emotion
            }
            
        except Exception as e:
            print(f"执行互动操作失败: {e}")
            return {
                "success": False,
                "message": f"互动失败: {str(e)}"
            }
    
    @staticmethod
    def get_interaction_stats(character_id: str, user_id: str = None) -> Dict[str, Any]:
        """获取角色的互动统计数据
        
        Args:
            character_id: 角色ID
            user_id: 用户ID（可选，用于检查今日互动状态）
            
        Returns:
            Dict[str, Any]: 统计数据
        """
        try:
            stats = interaction_dao.get_interaction_stats(character_id)
            
            if not stats:
                # 如果统计数据不存在，返回默认值
                stats_data = {
                    "character_id": character_id,
                    "feed_count": 0,
                    "comfort_count": 0,
                    "overtime_count": 0,
                    "water_count": 0,
                    "total_count": 0,
                    "last_interaction_time": None,
                    "updated_at": datetime.now()
                }
            else:
                stats_data = stats.to_dict()
            
            # 如果提供了用户ID，检查今日互动状态
            if user_id:
                today_interactions = {}
                for interaction_type in [t.value for t in InteractionType]:
                    has_interacted = interaction_dao.has_interaction_today(
                        user_id, character_id, interaction_type
                    )
                    today_interactions[interaction_type] = has_interacted
                
                stats_data["today_interactions"] = today_interactions
            
            return stats_data
            
        except Exception as e:
            print(f"获取互动统计数据失败: {e}")
            return {
                "error": str(e)
            }
    
    @staticmethod
    def get_batch_interaction_stats(character_ids: List[str]) -> Dict[str, Any]:
        """批量获取角色的互动统计数据
        
        Args:
            character_ids: 角色ID列表

        Returns:
            Dict[str, Any]: 批量统计数据
        """
        try:
            batch_stats = interaction_dao.get_batch_interaction_stats(character_ids)

            # 确保所有角色都有数据
            result = {}
            for character_id in character_ids:
                if character_id in batch_stats and batch_stats[character_id]:
                    result[character_id] = batch_stats[character_id]
                else:
                    # 提供默认值
                    result[character_id] = {
                        "character_id": character_id,
                        "feed_count": 0,
                        "comfort_count": 0,
                        "overtime_count": 0,
                        "water_count": 0,
                        "total_count": 0,
                        "last_interaction_time": None,
                        "updated_at": datetime.now()
                    }

            return result
        except Exception as e:
            print(f"批量获取互动统计数据失败: {e}")
            return {
                "error": str(e)
            }
    
    @staticmethod
    def check_today_interaction(user_id: str, character_id: str, interaction_type: str = None) -> Dict[str, Any]:
        """检查用户今日是否已与角色互动
        
        Args:
            user_id: 用户ID
            character_id: 角色ID
            interaction_type: 互动类型（可选，如果为None则检查所有类型）
            
        Returns:
            Dict[str, Any]: 检查结果
        """
        try:
            if interaction_type:
                # 检查特定互动类型
                has_interacted = interaction_dao.has_interaction_today(
                    user_id, character_id, interaction_type
                )
                return {
                    "has_interacted": has_interacted,
                    "interaction_type": interaction_type
                }
            else:
                # 检查所有互动类型
                today_interactions = {}
                for interaction_type in [t.value for t in InteractionType]:
                    has_interacted = interaction_dao.has_interaction_today(
                        user_id, character_id, interaction_type
                    )
                    today_interactions[interaction_type] = has_interacted
                
                return {
                    "today_interactions": today_interactions,
                    "has_any_interaction": any(today_interactions.values())
                }
                
        except Exception as e:
            print(f"检查今日互动状态失败: {e}")
            return {
                "error": str(e)
            }
    
    @staticmethod
    def get_user_interaction_history(user_id: str, limit: int = 100) -> Dict[str, Any]:
        """获取用户的互动历史
        
        Args:
            user_id: 用户ID
            limit: 返回记录数量限制
            
        Returns:
            Dict[str, Any]: 互动历史数据
        """
        try:
            records = interaction_dao.get_interaction_records(user_id, limit=limit)
            
            return {
                "records": records,
                "count": len(records),
                "user_id": user_id
            }
            
        except Exception as e:
            print(f"获取用户互动历史失败: {e}")
            return {
                "error": str(e)
            }

# 创建服务实例
interaction_service = InteractionService()