import uuid
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime

@dataclass
class Event:
    """事件类，表示生活轨迹中的一个事件"""
    event_id: str  # 事件唯一ID
    type: str  # 事件类型
    description: str  # 事件描述
    start_time: datetime  # 开始时间
    status: str  # 事件状态：'not_started'(未发生), 'in_progress'(正在发生), 'completed'(已完成)
    is_key_event: bool  # 是否为关键节点事件
    impact: str  # 事件影响
    end_time: Optional[datetime] = None  # 结束时间
    dependencies: List[str] = None  # 依赖的事件ID列表

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

@dataclass
class EventProfile:
    """角色事件配置类，存储角色的事件相关属性"""
    character_id: str  # 关联的角色ID
    life_path: List[Event]  # 生活轨迹表，由事件组成的数组
    current_stage: str  # 当前生活阶段
    next_trend: str  # 未来趋势
    event_triggers: Dict[str, Any]  # 事件触发条件

    def __init__(self, character_id: str):
        self.character_id = character_id
        self.life_path = []
        self.current_stage = ''
        self.next_trend = ''
        self.event_triggers = {}

    def add_event(self, event: Event) -> None:
        """添加事件到生活轨迹"""
        self.life_path.append(event)
        # 按时间排序
        self.life_path.sort(key=lambda x: x.start_time)

    def update_event_status(self, event_id: str, status: str) -> bool:
        """更新事件状态"""
        for event in self.life_path:
            if event.event_id == event_id:
                event.status = status
                return True
        return False

    def get_current_events(self) -> List[Event]:
        """获取当前正在发生的事件"""
        now = datetime.now()
        return [event for event in self.life_path
                if event.status == 'in_progress' or 
                (event.start_time <= now and (event.end_time is None or event.end_time >= now))]

    def get_completed_events(self) -> List[Event]:
        """获取已完成的事件"""
        return [event for event in self.life_path if event.status == 'completed']

    def get_key_events(self) -> List[Event]:
        """获取关键节点事件"""
        return [event for event in self.life_path if event.is_key_event]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = asdict(self)
        # 转换life_path中的Event对象为字典
        result['life_path'] = [event.to_dict() for event in self.life_path]
        return result

    def to_json(self) -> str:
        """转换为JSON字符串"""
        import json
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2, default=str)