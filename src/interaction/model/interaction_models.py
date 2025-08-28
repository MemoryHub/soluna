import uuid
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

class InteractionType(Enum):
    """互动类型枚举"""
    FEED = "feed"
    COMFORT = "comfort"
    OVERTIME = "overtime"
    WATER = "water"

@dataclass
class InteractionRecord:
    """互动记录类"""
    id: str
    user_id: str
    character_id: str
    interaction_type: str
    interaction_time: datetime
    created_at: datetime

    def __init__(self, user_id: str, character_id: str, interaction_type: str):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.character_id = character_id
        self.interaction_type = interaction_type
        self.interaction_time = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

@dataclass
class InteractionStats:
    """互动统计类"""
    id: str
    character_id: str
    feed_count: int
    comfort_count: int
    overtime_count: int
    water_count: int
    total_count: int
    last_interaction_time: Optional[datetime]
    updated_at: datetime

    def __init__(self, character_id: str):
        self.id = str(uuid.uuid4())
        self.character_id = character_id
        self.feed_count = 0
        self.comfort_count = 0
        self.overtime_count = 0
        self.water_count = 0
        self.total_count = 0
        self.last_interaction_time = None

    def increment_count(self, interaction_type: str) -> None:
        """根据互动类型增加计数"""
        if interaction_type == InteractionType.FEED.value:
            self.feed_count += 1
        elif interaction_type == InteractionType.COMFORT.value:
            self.comfort_count += 1
        elif interaction_type == InteractionType.OVERTIME.value:
            self.overtime_count += 1
        elif interaction_type == InteractionType.WATER.value:
            self.water_count += 1
        
        self.total_count += 1
        self.last_interaction_time = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InteractionStats':
        """从字典创建实例"""
        stats = cls(data['character_id'])
        stats.id = data['id']
        stats.feed_count = data.get('feed_count', 0)
        stats.comfort_count = data.get('comfort_count', 0)
        stats.overtime_count = data.get('overtime_count', 0)
        stats.water_count = data.get('water_count', 0)
        stats.total_count = data.get('total_count', 0)
        stats.last_interaction_time = data.get('last_interaction_time')
        stats.updated_at = data.get('updated_at', datetime.now())
        return stats