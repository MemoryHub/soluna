"""
情绪实时更新服务
负责根据最近30分钟的生活轨迹事件批量更新角色情绪
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from src.emotion.db.emotion_dao import emotion_dao
from src.character.db.life_path_dao import get_life_paths_by_time_range
from src.emotion.utils.event_deduplicator import EventDeduplicator
from src.db.mysql_client import MySQLClient


class EmotionUpdateService:
    """情绪实时更新服务"""
    
    def __init__(self):
        self.db = MySQLClient.get_instance()
        self.deduplicator = EventDeduplicator(self.db)
    
    async def update_emotions_from_recent_events(self, current_time: datetime) -> Dict[str, Any]:
        """
        根据最近30分钟的生活轨迹事件更新所有角色情绪
        
        Args:
            current_time: 当前时间
            
        Returns:
            更新统计信息
        """
        try:
            # 计算30分钟前的时间
            thirty_minutes_ago = current_time - timedelta(minutes=30)
            
            print(f"开始更新{thirty_minutes_ago}到{current_time}的情绪数据")
            
            # 获取所有角色30分钟内的生活轨迹
            recent_events = await self._get_recent_life_paths(thirty_minutes_ago, current_time)
            
            if not recent_events:
                print("30分钟内没有生活轨迹事件需要处理")
                return {
                    "updated_count": 0,
                    "total_events": 0,
                    "affected_characters": 0,
                    "message": "没有需要处理的事件"
                }
            
            # 过滤已处理的事件
            unprocessed_events = await self._filter_unprocessed_events(recent_events)
            
            if not unprocessed_events:
                print("所有生活轨迹事件都已在30分钟内处理过")
                return {
                    "updated_count": 0,
                    "total_events": len(recent_events),
                    "unprocessed_events": 0,
                    "affected_characters": 0,
                    "message": "所有事件都已处理过，跳过更新"
                }
            
            # 按角色分组事件
            character_events = self._group_events_by_character(unprocessed_events)
            
            # 准备情绪更新数据
            updates = []
            events_to_mark = []
            
            for character_id, events in character_events.items():
                pad_impact = self._calculate_cumulative_pad_impact(events)
                if pad_impact:
                    updates.append({
                        "character_id": character_id,
                        "pad_impact": pad_impact
                    })
                    
                    # 收集需要标记的事件
                    for event in events:
                        events_to_mark.append({
                            'character_id': character_id,
                            'event_id': event.get('event_id'),
                            'event_type': event.get('event_type', 'unknown')
                        })
            
            if not updates:
                print("没有有效的情绪更新数据")
                return {
                    "updated_count": 0,
                    "total_events": len(recent_events),
                    "affected_characters": len(character_events),
                    "message": "没有有效的情绪更新"
                }
            
            # 批量更新情绪
            update_results = emotion_dao.batch_update_emotions_from_events(updates)
            
            # 标记已处理的事件
            marked_count = self.deduplicator.batch_mark_processed(events_to_mark)
            
            # 清理过期记录（也可通过定时任务清理）
            self.deduplicator.cleanup_expired_records()
            
            # 统计结果
            success_count = sum(1 for result in update_results.values() if result)
            failed_count = len(update_results) - success_count
            
            print(
                f"情绪更新完成: 成功{success_count}个角色, 失败{failed_count}个角色, "
                f"处理了{len(unprocessed_events)}个新事件, 标记了{marked_count}个事件"
            )
            
            return {
                "updated_count": success_count,
                "failed_count": failed_count,
                "total_events": len(recent_events),
                "unprocessed_events": len(unprocessed_events),
                "marked_events": marked_count,
                "affected_characters": len(character_events),
                "skipped_events": len(recent_events) - len(unprocessed_events),
                "update_results": update_results,
                "message": f"成功更新{success_count}个角色的情绪，处理了{len(unprocessed_events)}个新事件"
            }
            
        except Exception as e:
            print(f"情绪更新失败: {str(e)}")
            raise
    
    async def _get_recent_life_paths(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """获取指定时间范围内的生活轨迹"""
        try:
            # 调用life_path_dao获取时间段内的事件
            events = get_life_paths_by_time_range(start_time, end_time)
            return events or []
        except Exception as e:
            print(f"获取生活轨迹失败: {str(e)}")
            return []
    
    def _group_events_by_character(self, events: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """按角色ID分组事件"""
        character_events = {}
        for event in events:
            character_id = event.get('character_id')
            if character_id:
                if character_id not in character_events:
                    character_events[character_id] = []
                character_events[character_id].append(event)
        return character_events
    
    async def _filter_unprocessed_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        过滤掉已处理过的事件
        
        Args:
            events: 原始事件列表
            
        Returns:
            List[Dict[str, Any]]: 未处理的事件列表
        """
        if not events:
            return []
        
        # 准备检查的事件数据
        events_to_check = []
        for event in events:
            character_id = event.get('character_id')
            event_id = event.get('event_id')
            if character_id and event_id:
                events_to_check.append({
                    'character_id': character_id,
                    'event_id': event_id
                })
        
        if not events_to_check:
            return events
        
        # 批量检查处理状态
        processed_status = self.deduplicator.batch_check_events(events_to_check)
        
        # 过滤未处理的事件
        unprocessed_events = []
        for event in events:
            character_id = event.get('character_id')
            event_id = event.get('event_id')
            key = f"{character_id}:{event_id}"
            
            if not processed_status.get(key, False):
                unprocessed_events.append(event)
        
        print(f"过滤事件: 原始{len(events)}个，未处理{len(unprocessed_events)}个")
        return unprocessed_events
    
    def _calculate_cumulative_pad_impact(self, events: List[Dict[str, Any]]) -> Dict[str, int]:
        """计算累积的PAD情绪影响"""
        if not events:
            return {}
        
        total_pleasure = 0
        total_arousal = 0
        total_dominance = 0
        
        for event in events:
            # 直接从事件数据中提取PAD数值
            # 根据数据样例，PAD数值直接在事件根级别
            pleasure = event.get('pleasure_score', 0)
            arousal = event.get('arousal_score', 0)
            dominance = event.get('dominance_score', 0)
            
            # 确保数值为整数
            try:
                total_pleasure += int(pleasure)
                total_arousal += int(arousal)
                total_dominance += int(dominance)
            except (ValueError, TypeError):
                # 如果转换失败，跳过这个事件
                print(f"跳过无效PAD数值的事件: {event.get('event_id', 'unknown')}")
                continue
        
        # 限制数值范围在合理范围内，避免极端值
        return {
            "pleasure": max(-80, min(80, total_pleasure)),
            "arousal": max(-80, min(80, total_arousal)),
            "dominance": max(-80, min(80, total_dominance))
        }


# 创建服务实例
emotion_update_service = EmotionUpdateService()