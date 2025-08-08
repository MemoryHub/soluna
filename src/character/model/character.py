import json
import uuid
import random
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from .event_profile import EventProfile


@dataclass
class Character:
    """AI角色类，包含角色的基本属性、行为特征和对话特性，使其更具真实人类特质"""
    name: str  # 角色姓名
    age: int  # 角色年龄
    gender: str  # 角色性别，可选值：'male', 'female', 'neutral'
    occupation: str  # 角色职业
    background: str  # 角色背景故事，包括成长经历、教育背景、重要人生事件等
    # 人格相关字段
    mbti_type: str  # MBTI人格类型，如'INTJ', 'ESFP'
    personality: List[str]  # 基于MBTI类型的具体性格特征，如['开朗', '乐观', '细心']
    big5: Dict[str, float]  # 大五人格特质得分，包含开放性、尽责性、外倾性、宜人性、神经质
    motivation: str  # 角色核心动机
    conflict: str  # 角色面临的主要冲突
    flaw: str  # 角色的主要缺陷
    character_arc: str  # 角色的成长弧光描述
    hobbies: List[str]  # 角色爱好列表，如['读书', '旅行', '摄影']
    relationships: Dict[str, str]  # 角色关系字典，key: 其他角色ID, value: 关系描述
    daily_routine: List[Dict[str, Any]]  # 角色日常安排列表，每个元素包含时间、活动描述、地点等

    # 对话相关特性
    speech_style: str  # 语言风格，如'正式', '口语化', '幽默', '严肃'
    tone: str  # 语气，如'友好', '傲慢', '温柔', '冷漠'
    response_speed: str  # 回应速度，如'快速', '中等', '缓慢'
    communication_style: str  # 沟通风格，如'直接', '委婉', '幽默', '理性'

    # 话题偏好与禁忌
    favored_topics: List[str]  # 喜欢的话题列表
    disliked_topics: List[str]  # 不喜欢的话题列表
    taboos: List[str]  # 禁忌话题列表，如['政治', '宗教', '隐私']

    # 深层人格特质
    beliefs: List[str]  # 信仰或价值观
    goals: List[str]  # 人生目标
    fears: List[str]  # 恐惧或害怕的事物
    secrets: List[str]  # 秘密
    habits: List[str]  # 习惯

    # 情绪相关
    mood: str  # 当前心情
    mood_swings: str  # 情绪波动情况，如'稳定', '多变', '敏感'

    # 记忆与经历
    memory: Dict[str, str]  # 角色记忆，key: 事件ID, value: 事件描述

    # 事件相关字段
    event_profile: EventProfile = None  # 角色事件配置

    # 系统字段
    character_id: str = None  # 角色唯一标识符，如不提供则自动生成
    is_preset: bool = False  # 是否为预设角色，预设角色为系统提供的示例角色

    def __post_init__(self):
        # 生成唯一ID
        if self.character_id is None:
            self.character_id = f"{self.name.lower().replace(' ', '_')}_{random.randint(1000, 9999)}"
        
        # 初始化事件配置
        if self.event_profile is None:
            self.event_profile = EventProfile(self.character_id)

    def to_dict(self) -> Dict[str, Any]:
        """将角色转换为字典"""
        return asdict(self)

    def to_json(self) -> str:
        """将角色转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)