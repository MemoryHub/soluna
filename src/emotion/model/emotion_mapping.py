"""
情绪映射模型
基于README_EMOTION.md的完整情绪映射表
"""

from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class EmotionMapping:
    """情绪映射实体"""
    
    # 情绪标签
    traditional: str
    vibe: str
    emoji: str
    color: str
    description: str
    
    # PAD范围
    pleasure_range: Tuple[float, float]
    arousal_range: Tuple[float, float]
    dominance_range: Tuple[float, float]
    
    # 综合分数范围
    composite_score_range: Tuple[float, float]
    emotion_type: str  # 情绪类型：兴奋、快乐、愤怒、焦虑、无聊、平静


class EmotionMappings:
    """情绪映射集合 - 26种情绪重新分为6大类"""
    
    # 6大情绪分类对应-100到100分的6个区间（基于PAD三维度综合评分）
    EMOTION_CATEGORIES = {
        "兴奋": {"range": (80, 100), "color": "#FFD700", "description": "极度积极兴奋状态"},
        "快乐": {"range": (40, 79), "color": "#32CD32", "description": "积极愉悦状态"},
        "平静": {"range": (10, 39), "color": "#4169E1", "description": "中性平和状态"},
        "无聊": {"range": (-10, 9), "color": "#808080", "description": "低唤醒中性状态"},
        "焦虑": {"range": (-50, -11), "color": "#FF6347", "description": "消极紧张状态"},
        "愤怒": {"range": (-100, -51), "color": "#DC143C", "description": "高度消极爆发状态"}
    }
    
    MAPPINGS = [
        # 🌟 兴奋喜类 (80-100分) - 金色系渐变 - 极难获得
        EmotionMapping("狂喜", "原地升天", "🚀", "#FFD700", 
                      "现在的我充满能量✨",
                      (80, 100), (80, 100), (60, 100), (80, 100), "兴奋"),
        
        EmotionMapping("兴奋", "鸡叫预警", "🐔", "#FFC700", 
                      "开心到飞起～",
                      (60, 100), (60, 100), (20, 60), (85, 99), "兴奋"),
        
        EmotionMapping("骄傲", "叉腰炫耀", "🦚", "#FFB000", 
                      "我超厉害的对吧？",
                      (60, 100), (40, 80), (70, 100), (82, 95), "兴奋"),
        
        # 😊 快乐类 (40-79分) - 绿色系渐变 - 较难获得
        EmotionMapping("开心", "嘴角AK47", "😏", "#32CD32", 
                      "这样真好",
                      (40, 80), (20, 60), (20, 60), (65, 79), "快乐"),
        
        EmotionMapping("满足", "被治愈了", "🥹", "#2ECC71", 
                      "好幸福呀...💖",
                      (60, 100), (-20, 20), (40, 80), (70, 78), "快乐"),
        
        EmotionMapping("期待", "小鹿乱撞", "🦌", "#27AE60", 
                      "等不及了！",
                      (30, 70), (50, 90), (-20, 20), (60, 74), "快乐"),
        
        EmotionMapping("惊喜", "瞳孔地震", "👁️", "#58D68D", 
                      "哇！给我的吗？",
                      (30, 70), (60, 100), (-30, 30), (55, 69), "快乐"),
        
        EmotionMapping("感动", "破防了", "🥺", "#52C41A", 
                      "你真好...",
                      (50, 90), (-10, 30), (30, 70), (45, 64), "快乐"),
        
        # 😐 无聊类 (-10-9分) - 灰色系渐变 - 容易获得
        EmotionMapping("无聊", "长蘑菇了", "🍄", "#808080", 
                      "陪我玩嘛...",
                      (-30, 30), (-40, 20), (-40, 40), (-5, 9), "无聊"),
        
        EmotionMapping("困惑", "CPU烧了", "🔥", "#A9A9A9", 
                      "这是啥？",
                      (-30, 30), (-10, 30), (-50, 0), (-8, 5), "无聊"),
        
        EmotionMapping("发呆", "人间不值得", "🕳️", "#C0C0C0", 
                      "发呆中...",
                      (-20, 30), (-30, 20), (-30, 30), (-10, 8), "无聊"),
        
        EmotionMapping("社恐", "社恐发作", "🫣", "#D3D3D3", 
                      "别盯着我看啦⁄(⁄ ⁄•⁄ω⁄•⁄ ⁄)⁄",
                      (-40, 20), (0, 40), (-70, -20), (-6, 6), "无聊"),
        
        EmotionMapping("尴尬", "脚趾抠地", "🏗️", "#696969", 
                      "别笑我...",
                      (-30, 10), (30, 70), (-50, -10), (-9, 4), "无聊"),
        
        # 😰 焦虑类 (-50--11分) - 橙色系暗调 - 容易获得
        EmotionMapping("焦虑", "心慌慌", "💔", "#FF6347", 
                      "会好吗？",
                      (-40, 0), (20, 60), (-80, -30), (-45, -12), "焦虑"),
        
        EmotionMapping("担忧", "妈妈担心", "👵", "#FF7F50", 
                      "怎么办...😰",
                      (-20, 20), (10, 50), (-70, -20), (-40, -15), "焦虑"),
        
        EmotionMapping("悲伤", "暴风哭泣", "😭", "#FF4500", 
                      "抱抱我...",
                      (-80, -40), (-60, -20), (-80, -20), (-48, -20), "焦虑"),
        
        EmotionMapping("沮丧", "人间不值得", "🕳️", "#E74C3C", 
                      "我不行了...",
                      (-60, -20), (-40, 0), (-60, -10), (-49, -25), "焦虑"),
        
        EmotionMapping("疲惫", "电量告急", "🔋", "#CD5C5C", 
                      "让我歇会...",
                      (-30, 10), (-80, -40), (-60, -10), (-42, -21), "焦虑"),
        
        EmotionMapping("悔恨", "肠子悔青", "🥀", "#B22222", 
                      "我错了...💔",
                      (-60, -20), (-30, 10), (-70, -20), (-50, -26), "焦虑"),
        
        # 😌 平静类 (10-39分) - 蓝色系渐变 - 中等获得
        EmotionMapping("平静", "岁月静好", "🍃", "#4169E1", 
                      "这样刚好",
                      (20, 60), (-40, 10), (10, 50), (15, 39), "平静"),
        
        EmotionMapping("放松", "已躺平", "🛏️", "#3498DB", 
                      "好舒服呀～",
                      (10, 50), (-60, -20), (20, 60), (20, 38), "平静"),
        
        EmotionMapping("好奇", "吃瓜状态", "🍉", "#5DADE2", 
                      "这是什么呀？🤔",
                      (20, 60), (40, 80), (-20, 20), (12, 35), "平静"),
        
        EmotionMapping("害羞", "小脸通红", "🍅", "#85C1E9", 
                      "别看人家啦",
                      (40, 80), (30, 70), (-70, -20), (11, 28), "平静"),
        
        # 😡 愤怒类 (-100--51分) - 红色系暗调 - 极难获得
        EmotionMapping("愤怒", "原地爆炸", "💥", "#DC143C", 
                      "太过分了！😡",
                      (-100, -40), (50, 100), (40, 100), (-85, -51), "愤怒"),
        
        EmotionMapping("恐惧", "背后发凉", "👻", "#8B0000", 
                      "别吓我...😨",
                      (-80, -40), (60, 100), (-100, -50), (-100, -70), "愤怒"),
        
        EmotionMapping("惊恐", "当场去世", "⚰️", "#A52A2A", 
                      "救命！呜呜...",
                      (-100, -60), (70, 100), (-100, -60), (-95, -75), "愤怒"),
        
        EmotionMapping("烦躁", "想骂人", "🤬", "#FF0000", 
                      "别吵我！",
                      (-60, -20), (30, 70), (-20, 30), (-75, -52), "愤怒"),
      ]
    
    @classmethod
    def get_all_mappings(cls) -> List[EmotionMapping]:
        """获取所有情绪映射"""
        return cls.MAPPINGS
    
    @classmethod
    def find_matching_emotion(cls, pleasure: float, arousal: float, 
                            dominance: float) -> EmotionMapping:
        """根据PAD值找到最匹配的情绪"""
        
        def calculate_score(mapping: EmotionMapping) -> float:
            """计算匹配分数，分数越高越匹配"""
            
            def in_range_score(value: float, range_tuple: Tuple[float, float]) -> float:
                """计算在范围内的匹配分数"""
                min_val, max_val = range_tuple
                if min_val <= value <= max_val:
                    # 在范围内，计算到中心点的距离（越接近中心分数越高）
                    center = (min_val + max_val) / 2
                    distance = abs(value - center)
                    range_width = max_val - min_val
                    return 1.0 - (distance / (range_width / 2)) * 0.5
                else:
                    # 不在范围内，计算到最近边界的距离
                    if value < min_val:
                        distance = min_val - value
                    else:
                        distance = value - max_val
                    # 距离越远，分数越低
                    return max(0, 1.0 - distance / 50)
            
            # 计算三个维度的匹配分数
            p_score = in_range_score(pleasure, mapping.pleasure_range)
            a_score = in_range_score(arousal, mapping.arousal_range)
            d_score = in_range_score(dominance, mapping.dominance_range)
            
            # 加权平均，与emotion_state.py中的权重保持一致
            return (p_score * 0.4 + a_score * 0.35 + d_score * 0.25)
        
        # 找到匹配分数最高的情绪
        best_match = max(cls.MAPPINGS, key=calculate_score)
        
        # 如果没有好的匹配，根据愉悦度进行回退匹配
        if calculate_score(best_match) < 0.3:
            if pleasure >= 60:
                # 高愉悦度 → 快乐类
                return next(m for m in cls.MAPPINGS if m.traditional == "开心")
            elif pleasure >= 20:
                # 中等愉悦度 → 平静类
                return next(m for m in cls.MAPPINGS if m.traditional == "平静")
            elif pleasure >= -20:
                # 低愉悦度 → 无聊类
                return next(m for m in cls.MAPPINGS if m.traditional == "无聊")
            elif pleasure >= -50:
                # 负愉悦度 → 焦虑类
                return next(m for m in cls.MAPPINGS if m.traditional == "焦虑")
            else:
                # 极低愉悦度 → 愤怒类
                return next(m for m in cls.MAPPINGS if m.traditional == "愤怒")
        
        return best_match