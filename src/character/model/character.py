import json
import uuid
import random
import time
from pypinyin import lazy_pinyin
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from .event_profile import EventProfile


@dataclass
class Character:
    """AI角色类，包含角色的基本属性、行为特征和对话特性，使其更具真实人类特质"""
    name: str  # 角色姓名 此字段数据类型为str
    age: int  # 角色年龄 此字段数据类型为int
    gender: str  # 角色性别，此字段数据类型为str
    occupation: str  # 角色职业 此字段数据类型为str
    background: str  # 角色背景故事，包括成长经历、教育背景、重要人生事件等 此字段数据类型为str
    # 人格相关字段
    mbti_type: str  # MBTI人格类型，此字段数据类型为str
    personality: List[str]  # 基于MBTI类型的具体性格特征  此字段数据类型为List[str]
    big5: Dict[str, float]  # 大五人格特质得分 此字段数据类型为Dict[str, float]
    motivation: str  # 角色核心动机 此字段数据类型为str
    conflict: str  # 角色面临的主要冲突 此字段数据类型为str
    flaw: str  # 角色的主要缺陷 此字段数据类型为str
    character_arc: str  # 角色的成长弧光描述 此字段数据类型为str
    hobbies: List[str]  # 角色爱好列表 此字段数据类型为List[str]
    relationships: Dict[str, str]  # 角色关系字典，key: 其他角色ID, value: 关系描述 此字段数据类型为Dict[str, str]
    daily_routine: List[Dict[str, Any]]  # 角色日常安排列表，每个元素包含时间、活动描述、地点等 此字段数据类型为List[Dict[str, Any]]

    # 对话相关特性
    speech_style: str  # 语言风格 此字段数据类型为str
    tone: str  # 语气 此字段数据类型为str
    response_speed: str  # 回应速度 此字段数据类型为str
    communication_style: str  # 沟通风格 此字段数据类型为str

    # 话题偏好与禁忌
    favored_topics: List[str]  # 喜欢的话题列表 此字段数据类型为List[str]
    disliked_topics: List[str]  # 不喜欢的话题列表 此字段数据类型为List[str]
    taboos: List[str]  # 禁忌话题列表 此字段数据类型为List[str]

    # 深层人格特质
    beliefs: List[str]  # 信仰或价值观 此字段数据类型为List[str]
    goals: List[str]  # 人生目标 此字段数据类型为List[str]
    fears: List[str]  # 恐惧或害怕的事物 此字段数据类型为List[str]
    secrets: List[str]  # 秘密 此字段数据类型为List[str]
    habits: List[str]  # 习惯 此字段数据类型为List[str]

    # 情绪相关
    mood: str  # 当前心情 此字段数据类型为str
    mood_swings: str  # 情绪波动情况，如'稳定', '多变', '敏感' 此字段数据类型为str

    # 记忆与经历
    memory: Dict[str, str]  # 角色记忆，key: 事件ID, value: 事件描述 此字段数据类型为Dict[str, str]

    # 事件相关字段
    event_profile: EventProfile = None  # 角色事件配置 此字段数据类型为EventProfile

    # 系统字段
    character_id: str = None  # 角色唯一标识符，如不提供则自动生成 此字段数据类型为str
    is_preset: bool = False  # 是否为预设角色，预设角色为系统提供的示例角色 此字段数据类型为bool
    created_at: float = None  # 角色创建时间戳，此字段数据类型为float
    updated_at: float = None  # 角色最后更新时间戳，此字段数据类型为float

    def __post_init__(self):
        # 生成唯一ID
        if self.character_id is None:
            # 将中文名字转换为拼音
            pinyin_name = ''.join(lazy_pinyin(self.name))
            # 使用时间戳生成唯一标识
            timestamp = int(time.time())
            self.character_id = f"{pinyin_name.lower().replace(' ', '_')}_{timestamp}"
        
        # 设置创建时间和更新时间
        current_time = time.time()
        if self.created_at is None:
            self.created_at = current_time
        # 无论是否是新角色，都更新updated_at
        self.updated_at = current_time
        
        # 初始化事件配置
        if self.event_profile is None:
            self.event_profile = EventProfile(self.character_id)

    def to_dict(self) -> Dict[str, Any]:
        """将角色转换为字典"""
        return asdict(self)

    def to_json(self) -> str:
        """将角色转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)