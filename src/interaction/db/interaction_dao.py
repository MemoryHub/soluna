import os
import sys
from datetime import datetime, date
from typing import List, Optional, Dict, Any

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)

from src.db.mysql_client import mysql_client
from src.interaction.model.interaction_models import InteractionRecord, InteractionStats

class InteractionDAO:
    """互动功能MySQL数据访问对象"""
    
    def __init__(self):
        """初始化DAO"""
        self.client = mysql_client
    
    def create_interaction_record(self, record: InteractionRecord) -> str:
        """创建互动记录"""
        try:
            query = """
                INSERT INTO interaction_records (id, user_id, character_id, interaction_type, interaction_time)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (
                record.id,
                record.user_id,
                record.character_id,
                record.interaction_type,
                record.interaction_time
            )
            
            self.client.execute_update(query, params)
            return record.id
            
        except Exception as e:
            print(f"创建互动记录失败: {e}")
            raise
    
    def has_interaction_today(self, user_id: str, character_id: str, interaction_type: str) -> bool:
        """检查用户今日是否已与角色进行特定类型互动"""
        try:
            query = """
                SELECT COUNT(*) as count
                FROM interaction_records
                WHERE user_id = %s 
                AND character_id = %s 
                AND interaction_type = %s 
                AND DATE(interaction_time) = CURDATE()
            """
            params = (user_id, character_id, interaction_type)
            
            result = self.client.execute_query(query, params)
            return result[0]['count'] > 0 if result else False
            
        except Exception as e:
            print(f"检查今日互动失败: {e}")
            raise
    
    def get_interaction_records(self, user_id: str, character_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取用户的互动记录"""
        try:
            if character_id:
                query = """
                    SELECT * FROM interaction_records
                    WHERE user_id = %s AND character_id = %s
                    ORDER BY interaction_time DESC
                    LIMIT %s
                """
                params = (user_id, character_id, limit)
            else:
                query = """
                    SELECT * FROM interaction_records
                    WHERE user_id = %s
                    ORDER BY interaction_time DESC
                    LIMIT %s
                """
                params = (user_id, limit)
            
            records = self.client.execute_query(query, params)
            return records
            
        except Exception as e:
            print(f"获取互动记录失败: {e}")
            raise
    
    def get_interaction_stats(self, character_id: str) -> Optional[InteractionStats]:
        """获取角色的互动统计数据"""
        try:
            query = """
                SELECT * FROM interaction_stats
                WHERE character_id = %s
            """
            params = (character_id,)
            
            result = self.client.execute_query(query, params)
            if result:
                data = result[0]
                return InteractionStats.from_dict(data)
            return None
            
        except Exception as e:
            print(f"获取互动统计数据失败: {e}")
            raise
    
    def get_batch_interaction_stats(self, character_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """批量获取角色的互动统计数据"""
        try:
            if not character_ids:
                return {}
            
            placeholders = ','.join(['%s'] * len(character_ids))
            query = f"""
                SELECT * FROM interaction_stats
                WHERE character_id IN ({placeholders})
            """
            
            result = self.client.execute_query(query, character_ids)
            
            stats_dict = {character_id: None for character_id in character_ids}
            for row in result:
                stats = InteractionStats.from_dict(row)
                stats_dict[stats.character_id] = stats.to_dict()
            
            return stats_dict
            
        except Exception as e:
            print(f"批量获取互动统计数据失败: {e}")
            raise
    
    def create_interaction_stats(self, stats: InteractionStats) -> str:
        """创建互动统计数据"""
        try:
            query = """
                INSERT INTO interaction_stats (
                    id, character_id, feed_count, comfort_count, overtime_count, water_count,
                    total_count, last_interaction_time
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                stats.id,
                stats.character_id,
                stats.feed_count,
                stats.comfort_count,
                stats.overtime_count,
                stats.water_count,
                stats.total_count,
                stats.last_interaction_time
            )
            
            self.client.execute_update(query, params)
            return stats.id
            
        except Exception as e:
            print(f"创建互动统计数据失败: {e}")
            raise
    
    def update_interaction_stats(self, character_id: str, interaction_type: str) -> bool:
        """更新角色的互动统计数据"""
        try:
            # 检查统计数据是否存在
            existing_stats = self.get_interaction_stats(character_id)
            
            if existing_stats:
                # 更新现有统计数据
                query = f"""
                    UPDATE interaction_stats
                    SET {interaction_type}_count = {interaction_type}_count + 1,
                        total_count = total_count + 1,
                        last_interaction_time = NOW(),
                        updated_at = NOW()
                    WHERE character_id = %s
                """
                params = (character_id,)
                
                result = self.client.execute_update(query, params)
                return result > 0
            else:
                # 创建新的统计数据
                stats = InteractionStats(character_id)
                stats.increment_count(interaction_type)
                self.create_interaction_stats(stats)
                return True
                
        except Exception as e:
            print(f"更新互动统计数据失败: {e}")
            raise