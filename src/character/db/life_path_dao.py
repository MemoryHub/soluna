from datetime import datetime
from typing import List, Dict, Any
from src.character.db.event_profile_dao import EventProfileDAO
from src.db.mongo_client import mongo_client

class LifePathDAO:
    """生活轨迹数据访问对象，负责从MongoDB中获取生活轨迹数据"""
    
    def __init__(self):
        """初始化生活轨迹DAO"""
        self.db = mongo_client.get_database()
        self.event_profiles_collection = self.db['event_profiles']
    
    def _parse_time_string(self, time_str: str) -> datetime:
        """
        解析时间字符串，支持多种格式
        
        Args:
            time_str: 时间字符串
            
        Returns:
            datetime: 解析后的datetime对象
            
        Raises:
            ValueError: 当无法解析时间字符串时
        """
        formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',      # ISO 8601格式 (UTC)
            '%Y-%m-%dT%H:%M:%S.%f%z',    # ISO 8601格式 (带时区)
            '%Y-%m-%dT%H:%M:%S%z',       # ISO 8601格式 (无毫秒)
            '%Y-%m-%dT%H:%M:%S',         # ISO 8601格式 (无时区)
            '%Y-%m-%d %H:%M:%S',         # 标准格式
            '%Y-%m-%d %H:%M',            # 无秒格式
            '%Y/%m/%d %H:%M:%S',         # 斜杠分隔格式
            '%Y/%m/%d %H:%M',            # 斜杠分隔无秒格式
            '%d/%m/%Y %H:%M:%S',         # 欧洲格式
            '%d/%m/%Y %H:%M',            # 欧洲格式无秒
            '%Y-%m-%d',                  # 仅日期
        ]
        
        # 首先尝试标准格式
        for fmt in formats:
            try:
                return datetime.strptime(time_str, fmt)
            except ValueError:
                continue
        
        # 如果标准格式都失败，尝试使用dateutil作为后备
        try:
            from dateutil.parser import parse
            return parse(time_str)
        except Exception:
            raise ValueError(f"无法解析时间字符串: {time_str}")
    
    def get_life_paths_by_time_range(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """
        获取指定时间范围内的所有生活轨迹事件
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            List[Dict[str, Any]]: 包含角色ID和事件信息的生活轨迹列表
        """
        try:
            # 创建EventProfileDAO实例
            event_profile_dao = EventProfileDAO()
            
            # 查询所有事件配置
            profiles = list(event_profile_dao.event_profiles_collection.find({}))
            
            # 提取生活轨迹事件
            events = []
            for profile in profiles:
                character_id = profile.get('character_id')
                life_path = profile.get('life_path', [])
                
                # 筛选在指定时间范围内的事件
                for event in life_path:
                    event_start_time = event.get('start_time')
                    if event_start_time:
                        # 处理多种时间格式
                            try:
                                if isinstance(event_start_time, str):
                                    # 使用多种格式尝试解析时间字符串
                                    event_start_time = self._parse_time_string(event_start_time)
                                elif isinstance(event_start_time, int):
                                    # 处理Unix时间戳（毫秒或秒）
                                    if event_start_time > 1000000000000:  # 毫秒
                                        event_start_time = datetime.fromtimestamp(event_start_time / 1000)
                                    else:  # 秒
                                        event_start_time = datetime.fromtimestamp(event_start_time)
                                elif not isinstance(event_start_time, datetime):
                                    # 其他格式，跳过
                                    continue
                                
                                # 直接比较时间，不进行时区处理
                                if start_time <= event_start_time <= end_time:
                                    # 添加角色ID到事件中
                                    event_with_character = dict(event)
                                    event_with_character['character_id'] = character_id
                                    events.append(event_with_character)
                            except (ValueError, TypeError) as e:
                                # 处理时间解析错误，跳过无效格式
                                continue
            
            return events
            
        except Exception as e:
            print(f"获取生活轨迹失败: {e}")
            return []
    
    def get_life_paths_by_character_and_time_range(self, character_ids: List[str], 
                                                   start_time: datetime, end_time: datetime) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取指定角色在指定时间范围内的生活轨迹事件
        
        Args:
            character_ids: 角色ID列表
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 以角色ID为键，事件列表为值的字典
        """
        try:
            # 创建EventProfileDAO实例
            event_profile_dao = EventProfileDAO()
            
            # 获取指定角色的事件配置
            profiles = event_profile_dao.get_event_profiles_by_character_ids(character_ids)
            
            # 构建结果字典
            result = {character_id: [] for character_id in character_ids}
            
            for character_id, profile_list in profiles.items():
                for profile in profile_list:
                    life_path = profile.get('life_path', [])
                    
                    # 筛选在指定时间范围内的事件
                    filtered_events = []
                    for event in life_path:
                        event_start_time = event.get('start_time')
                        if event_start_time:
                            # 处理多种时间格式
                            try:
                                if isinstance(event_start_time, str):
                                    # 使用自定义的时间解析方法
                                    event_start_time = self._parse_time_string(event_start_time)
                                elif isinstance(event_start_time, int):
                                    # 处理Unix时间戳（毫秒或秒）
                                    if event_start_time > 1000000000000:  # 毫秒
                                        event_start_time = datetime.fromtimestamp(event_start_time / 1000)
                                    else:  # 秒
                                        event_start_time = datetime.fromtimestamp(event_start_time)
                                elif not isinstance(event_start_time, datetime):
                                    # 其他格式，跳过
                                    continue
                                
                                # 直接比较时间，不进行时区处理
                                if start_time <= event_start_time <= end_time:
                                    filtered_events.append(event)
                            except (ValueError, TypeError) as e:
                                # 处理时间解析错误，跳过无效格式
                                continue
                    
                    result[character_id].extend(filtered_events)
            
            return result
            
        except Exception as e:
            print(f"获取角色生活轨迹失败: {e}")
            return {character_id: [] for character_id in character_ids}

# 创建DAO实例
DAO = LifePathDAO()

def get_life_paths_by_time_range(start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
    """获取指定时间范围内的所有生活轨迹事件的便捷函数"""
    return DAO.get_life_paths_by_time_range(start_time, end_time)

def get_life_paths_by_character_and_time_range(character_ids: List[str], 
                                             start_time: datetime, 
                                             end_time: datetime) -> Dict[str, List[Dict[str, Any]]]:
    """获取指定角色在指定时间范围内的生活轨迹事件的便捷函数"""
    return DAO.get_life_paths_by_character_and_time_range(character_ids, start_time, end_time)