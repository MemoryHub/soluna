"""
情感服务核心类
提供情绪映射、计算和管理功能
"""

from typing import Dict, Optional, List
from datetime import datetime

from src.emotion.model.emotion_state import EmotionState
from src.emotion.model.emotion_mapping import EmotionMappings


class EmotionService:
    """情感服务类"""
    
    def __init__(self):
        """初始化情感服务"""
        self.mappings = EmotionMappings()
    
    def calculate_emotion_from_pad(self, character_id: str, 
                                 pleasure: float, arousal: float, 
                                 dominance: float) -> EmotionState:
        """
        根据PAD三维值计算情感状态
        
        Args:
            character_id: 角色ID
            pleasure: 愉悦度 (-100 to 100)
            arousal: 激活度 (-100 to 100)  
            dominance: 支配感 (-100 to 100)
            
        Returns:
            EmotionState: 完整的情感状态对象
        """
        
        # 验证输入范围
        pleasure = max(-100, min(100, pleasure))
        arousal = max(-100, min(100, arousal))
        dominance = max(-100, min(100, dominance))
        
        # 计算综合分数
        composite_score = pleasure * 0.4 + arousal * 0.35 + dominance * 0.25
        
        # 找到最匹配的情绪
        emotion_mapping = self.mappings.find_matching_emotion(
            pleasure, arousal, dominance
        )
        
        # 计算置信度（基于距离的倒数）
        confidence = self._calculate_confidence(
            pleasure, arousal, dominance, emotion_mapping
        )
        
        return EmotionState(
            character_id=character_id,
            timestamp=datetime.now(),
            pleasure=pleasure,
            arousal=arousal,
            dominance=dominance,
            traditional_emotion=emotion_mapping.traditional,
            vibe_emotion=emotion_mapping.vibe,
            emoji=emotion_mapping.emoji,
            color=emotion_mapping.color,
            emotion_description=emotion_mapping.description,
            emotion_type=emotion_mapping.emotion_type,  # 新增情绪类型字段
            confidence=confidence,
            composite_score=composite_score
        )
    
    def _calculate_confidence(self, pleasure: float, arousal: float, 
                            dominance: float, mapping) -> float:
        """计算情绪识别的置信度"""
        
        # 计算每个维度的中心点
        p_center = (mapping.pleasure_range[0] + mapping.pleasure_range[1]) / 2
        a_center = (mapping.arousal_range[0] + mapping.arousal_range[1]) / 2
        d_center = (mapping.dominance_range[0] + mapping.dominance_range[1]) / 2
        
        # 计算标准化距离（0-1范围）
        p_dist = abs(pleasure - p_center) / 100
        a_dist = abs(arousal - a_center) / 100
        d_dist = abs(dominance - d_center) / 100
        
        # 平均距离
        avg_distance = (p_dist + a_dist + d_dist) / 3
        
        # 置信度 = 1 - 平均距离（但最小为0.3）
        confidence = max(0.3, 1 - avg_distance)
        
        return round(confidence, 3)
    
    def get_emotion_group(self, emotion: str) -> Optional[Dict]:
        """获取情绪所属的分组信息"""
        
        emotion_groups = {
            "高唤醒积极": {
                "color": "#FFD700",
                "description": "快乐、成就、阳光般的温暖",
                "emotions": ["狂喜", "兴奋", "骄傲"]
            },
            "中等唤醒积极": {
                "color": "#FFA500", 
                "description": "温暖、活力、友好的社交",
                "emotions": ["开心", "满足", "期待"]
            },
            "低唤醒积极": {
                "color": "#90EE90",
                "description": "平静、治愈、自然的放松", 
                "emotions": ["平静", "放松", "感动"]
            },
            "惊喜状态": {
                "color": "#DDA0DD",
                "description": "好奇、神秘、探索的欲望",
                "emotions": ["惊喜", "好奇"]
            },
            "害羞状态": {
                "color": "#FFB6C1",
                "description": "羞涩、温柔、内敛的情感",
                "emotions": ["害羞", "尴尬"]
            },
            "中性状态": {
                "color": "#B0C4DE",
                "description": "中性、思考、理性的状态",
                "emotions": ["无聊", "困惑", "发呆"]
            },
            "社恐状态": {
                "color": "#D3D3D3",
                "description": "退缩、防御、社交回避",
                "emotions": ["社恐"]
            },
            "低唤醒消极": {
                "color": "#87CEEB",
                "description": "悲伤、忧郁、安静的低落",
                "emotions": ["悲伤", "沮丧", "疲惫", "悔恨"]
            },
            "中等唤醒消极": {
                "color": "#FF8C00",
                "description": "紧张、焦虑、不安的担忧",
                "emotions": ["焦虑", "担忧", "烦躁"]
            },
            "高唤醒消极": {
                "color": "#8B0000",
                "description": "愤怒、恐惧、强烈的威胁",
                "emotions": ["愤怒", "恐惧", "惊恐"]
            }
        }
        
        for group_name, group_info in emotion_groups.items():
            if emotion in group_info["emotions"]:
                return {
                    "group_name": group_name,
                    "color": group_info["color"],
                    "description": group_info["description"]
                }
        
        return None
    
    def get_emotion_history_summary(self, emotions: List[EmotionState]) -> Dict:
        """分析情绪历史摘要"""
        if not emotions:
            return {"message": "暂无情绪数据"}
        
        # 计算平均情绪
        avg_pleasure = sum(e.pleasure for e in emotions) / len(emotions)
        avg_arousal = sum(e.arousal for e in emotions) / len(emotions)
        avg_dominance = sum(e.dominance for e in emotions) / len(emotions)
        
        # 统计情绪分布
        emotion_counts = {}
        for emotion in emotions:
            key = emotion.traditional_emotion
            emotion_counts[key] = emotion_counts.get(key, 0) + 1
        
        # 找出最频繁的情绪
        most_frequent = max(emotion_counts.items(), key=lambda x: x[1])
        
        return {
            "total_records": len(emotions),
            "average_emotion": {
                "pleasure": round(avg_pleasure, 2),
                "arousal": round(avg_arousal, 2),
                "dominance": round(avg_dominance, 2)
            },
            "most_frequent_emotion": {
                "emotion": most_frequent[0],
                "count": most_frequent[1],
                "percentage": round(most_frequent[1] / len(emotions) * 100, 1)
            },
            "emotion_distribution": emotion_counts
        }