import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from src.db.mysql_client import MySQLClient

logger = logging.getLogger(__name__)

class EventDeduplicator:
    """事件去重处理器 - 防止30分钟内重复处理同一生活轨迹事件"""
    
    def __init__(self, db_client: MySQLClient):
        self.db = db_client
        
    def is_event_processed(self, character_id: str, event_id: str) -> bool:
        """
        检查事件是否在最近30分钟内已处理
        
        Args:
            character_id: 角色ID
            event_id: 事件ID
            
        Returns:
            bool: 如果事件已处理返回True，否则返回False
        """
        try:
            query = """
                SELECT 1 FROM emotion_thirty_min_temp 
                WHERE character_id = %s 
                AND event_id = %s 
                AND processed_at > DATE_SUB(NOW(), INTERVAL 30 MINUTE)
                LIMIT 1
            """
            
            result = self.db.execute_query(query, (character_id, event_id))
            return len(result) > 0
            
        except Exception as e:
            logger.error(f"检查事件处理状态时出错: {e}")
            return False
    
    def mark_event_processed(self, character_id: str, event_id: str, event_type: str) -> bool:
        """
        标记事件为已处理
        
        Args:
            character_id: 角色ID
            event_id: 事件ID
            event_type: 事件类型
            
        Returns:
            bool: 操作是否成功
        """
        try:
            query = """
                INSERT IGNORE INTO emotion_thirty_min_temp 
                (character_id, event_id, event_type, processed_at)
                VALUES (%s, %s, %s, NOW())
            """
            
            self.db.execute_update(query, (character_id, event_id, event_type))
            return True
            
        except Exception as e:
            logger.error(f"标记事件为已处理时出错: {e}")
            return False
    
    def batch_check_events(self, events: List[Dict[str, str]]) -> Dict[str, bool]:
        """
        批量检查多个事件的处理状态
        
        Args:
            events: 事件列表，每个事件包含character_id和event_id
            
        Returns:
            Dict[str, bool]: 事件标识符到处理状态的映射
        """
        if not events:
            return {}
            
        try:
            # 构建查询条件
            conditions = []
            params = []
            
            for event in events:
                conditions.append("(character_id = %s AND event_id = %s)")
                params.extend([event['character_id'], event['event_id']])
            
            where_clause = " OR ".join(conditions)
            query = f"""
                SELECT character_id, event_id 
                FROM emotion_thirty_min_temp 
                WHERE ({where_clause}) 
                AND processed_at > DATE_SUB(NOW(), INTERVAL 30 MINUTE)
            """
            
            processed_events = self.db.execute_query(query, params)
            
            # 构建结果字典
            processed_set = {
                f"{row['character_id']}:{row['event_id']}" 
                for row in processed_events
            }
            
            result = {}
            for event in events:
                key = f"{event['character_id']}:{event['event_id']}"
                result[key] = key in processed_set
                
            return result
            
        except Exception as e:
            logger.error(f"批量检查事件状态时出错: {e}")
            return {}
    
    def batch_mark_processed(self, events: List[Dict[str, str]]) -> int:
        """
        批量标记多个事件为已处理
        
        Args:
            events: 事件列表，每个事件包含character_id, event_id, event_type
            
        Returns:
            int: 成功标记的事件数量
        """
        if not events:
            return 0
            
        try:
            values = []
            params = []
            
            for event in events:
                values.append("(%s, %s, %s, NOW())")
                params.extend([
                    event['character_id'], 
                    event['event_id'], 
                    event.get('event_type', 'unknown')
                ])
            
            query = f"""
                INSERT IGNORE INTO emotion_thirty_min_temp 
                (character_id, event_id, event_type, processed_at)
                VALUES {','.join(values)}
            """
            
            result = self.db.execute_update(query, params)
            return result
            
        except Exception as e:
            logger.error(f"批量标记事件为已处理时出错: {e}")
            return 0
    
    def cleanup_expired_records(self) -> int:
        """
        清理30分钟前的过期记录
        
        Returns:
            int: 清理的记录数量
        """
        try:
            query = """
                DELETE FROM emotion_thirty_min_temp 
                WHERE processed_at < DATE_SUB(NOW(), INTERVAL 30 MINUTE)
            """
            
            result = self.db.execute_update(query)
            logger.info(f"清理了 {result} 条过期的事件处理记录")
            return result
            
        except Exception as e:
            logger.error(f"清理过期记录时出错: {e}")
            return 0
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        获取处理统计信息
        
        Returns:
            Dict[str, Any]: 包含统计信息的字典
        """
        try:
            query = """
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT character_id) as unique_characters,
                    COUNT(CASE WHEN processed_at > DATE_SUB(NOW(), INTERVAL 30 MINUTE) 
                          THEN 1 END) as recent_records,
                    MIN(processed_at) as oldest_record,
                    MAX(processed_at) as latest_record
                FROM emotion_thirty_min_temp
            """
            
            result = self.db.execute_query(query)
            return result[0] if result else {}
            
        except Exception as e:
            logger.error(f"获取处理统计信息时出错: {e}")
            return {}