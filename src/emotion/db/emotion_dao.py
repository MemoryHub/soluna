"""
情绪数据访问对象 - 核心DAO层
处理emotions表的CRUD操作，提供7个核心功能所需的数据库操作
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from src.db.mysql_client import mysql_client


class EmotionDAO:
    """情绪数据访问对象"""
    
    def __init__(self):
        self.db = mysql_client
    
    def get_emotion_by_character_id(self, character_id: str) -> Optional[Dict[str, Any]]:
        """
        根据角色ID获取情绪状态
        
        Args:
            character_id: 角色ID
            
        Returns:
            角色情绪数据或None
        """
        query = """
            SELECT character_id, pleasure_score, arousal_score, dominance_score, 
                   current_emotion_score, updated_at, created_at
            FROM emotions 
            WHERE character_id = %s
        """
        result = self.db.execute_query(query, (character_id,))
        return result[0] if result else None
    
    def create_emotion(self, emotion_data: Dict[str, Any]) -> bool:
        """
        创建新的情绪记录
        
        Args:
            emotion_data: 情绪数据字典
            
        Returns:
            是否创建成功
        """
        query = """
            INSERT INTO emotions (character_id, pleasure_score, arousal_score, 
                              dominance_score, current_emotion_score)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            emotion_data.get('character_id'),
            emotion_data.get('pleasure_score', 0),
            emotion_data.get('arousal_score', 0),
            emotion_data.get('dominance_score', 0),
            emotion_data.get('current_emotion_score', 0)
        )
        try:
            self.db.execute_update(query, params)
            return True
        except Exception as e:
            print(f"创建情绪记录失败: {e}")
            return False
    
    def update_emotion(self, character_id: str, emotion_data: Dict[str, Any]) -> bool:
        """
        更新角色情绪状态
        
        Args:
            character_id: 角色ID
            emotion_data: 情绪数据字典
            
        Returns:
            是否更新成功
        """
        set_clauses = []
        params = []
        
        valid_fields = ['pleasure_score', 'arousal_score', 'dominance_score', 'current_emotion_score']
        for field in valid_fields:
            if field in emotion_data:
                set_clauses.append(f"{field} = %s")
                params.append(emotion_data[field])
        
        if not set_clauses:
            return False
            
        params.append(character_id)
        query = f"""
            UPDATE emotions 
            SET {', '.join(set_clauses)}
            WHERE character_id = %s
        """
        
        try:
            result = self.db.execute_update(query, params)
            return result > 0
        except Exception as e:
            print(f"更新情绪状态失败: {e}")
            return False
    
    def update_emotion_from_event(self, character_id: str, pad_impact: Dict[str, int]) -> bool:
        """
        根据事件影响更新情绪状态
        
        Args:
            character_id: 角色ID
            pad_impact: PAD三维变化值
            
        Returns:
            是否更新成功
        """
        try:
            # 获取当前情绪状态
            current = self.get_emotion_by_character_id(character_id)
            if not current:
                # 如果不存在，创建新的情绪记录
                initial_data = {
                    'character_id': character_id,
                    'pleasure_score': pad_impact.get('pleasure', 0),
                    'arousal_score': pad_impact.get('arousal', 0),
                    'dominance_score': pad_impact.get('dominance', 0),
                    'current_emotion_score': self._calculate_emotion_score(pad_impact)
                }
                return self.create_emotion(initial_data)
            
            # 计算新的情绪值，限制在-100到100范围内
            new_pleasure = max(-100, min(100, current['pleasure_score'] + pad_impact.get('pleasure', 0)))
            new_arousal = max(-100, min(100, current['arousal_score'] + pad_impact.get('arousal', 0)))
            new_dominance = max(-100, min(100, current['dominance_score'] + pad_impact.get('dominance', 0)))
            
            # 计算综合情绪分数
            new_emotion_score = self._calculate_emotion_score({
                'pleasure': new_pleasure,
                'arousal': new_arousal,
                'dominance': new_dominance
            })
            
            # 更新情绪状态
            update_data = {
                'pleasure_score': new_pleasure,
                'arousal_score': new_arousal,
                'dominance_score': new_dominance,
                'current_emotion_score': new_emotion_score
            }
            
            return self.update_emotion(character_id, update_data)
            
        except Exception as e:
            print(f"根据事件更新情绪失败: {e}")
            return False
    
    def initialize_character_emotion(self, character_id: str) -> bool:
        """
        初始化角色情绪状态
        
        Args:
            character_id: 角色ID
            
        Returns:
            是否初始化成功
        """
        import random
        try:
            # 检查是否已存在
            existing = self.get_emotion_by_character_id(character_id)
            if existing:
                return True
            
            # 随机生成初始情绪值 (-50到50之间)
            initial_data = {
                'character_id': character_id,
                'pleasure_score': random.randint(-50, 50),
                'arousal_score': random.randint(-50, 50),
                'dominance_score': random.randint(-50, 50),
                'current_emotion_score': random.randint(-50, 50)
            }
            
            return self.create_emotion(initial_data)
            
        except Exception as e:
            print(f"初始化角色情绪失败: {e}")
            return False
    
    def get_emotions_batch(self, character_ids: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        批量获取角色情绪状态
        
        Args:
            character_ids: 角色ID列表
            
        Returns:
            每个角色的情绪数据字典
        """
        if not character_ids:
            return {}
        
        placeholders = ','.join(['%s'] * len(character_ids))
        query = f"""
            SELECT character_id, pleasure_score, arousal_score, dominance_score, 
                   current_emotion_score, updated_at, created_at
            FROM emotions 
            WHERE character_id IN ({placeholders})
        """
        
        try:
            results = self.db.execute_query(query, character_ids)
            emotions_dict = {}
            
            for row in results:
                emotions_dict[row['character_id']] = row
            
            # 确保返回所有请求的character_id
            for char_id in character_ids:
                if char_id not in emotions_dict:
                    emotions_dict[char_id] = None
            
            return emotions_dict
            
        except Exception as e:
            print(f"批量获取情绪状态失败: {e}")
            return {}
    
    def _calculate_emotion_score(self, pad_values: Dict[str, int]) -> int:
        """
        计算综合情绪分数
        
        Args:
            pad_values: PAD三维值
            
        Returns:
            综合情绪分数 (-100到100)
        """
        pleasure = pad_values.get('pleasure', 0)
        arousal = pad_values.get('arousal', 0)
        dominance = pad_values.get('dominance', 0)
        
        # 使用权重公式计算综合分数
        score = int(pleasure * 0.4 + arousal * 0.35 + dominance * 0.25)
        return max(-100, min(100, score))
    
    def batch_update_emotions_from_events(self, updates: List[Dict[str, Any]]) -> Dict[str, bool]:
        """
        批量更新角色情绪状态 - 数据库层面批量操作
        
        Args:
            updates: 更新数据列表，每项包含character_id和pad_impact
            
        Returns:
            每个角色的更新结果
        """
        if not updates:
            return {}
        
        try:
            # 获取所有需要更新的角色ID
            character_ids = [update['character_id'] for update in updates]
            
            # 获取当前所有角色的情绪状态
            placeholders = ','.join(['%s'] * len(character_ids))
            query = f"""
                SELECT character_id, pleasure_score, arousal_score, dominance_score
                FROM emotions 
                WHERE character_id IN ({placeholders})
            """
            current_states = {row['character_id']: row for row in self.db.execute_query(query, character_ids)}
            
            # 准备批量更新数据
            update_data = []
            results = {}
            
            # 为不存在的角色创建新记录
            new_records = []
            
            for update in updates:
                character_id = update['character_id']
                pad_impact = update.get('pad_impact', {})
                
                if character_id in current_states:
                    # 更新现有记录
                    current = current_states[character_id]
                    new_pleasure = max(-100, min(100, current['pleasure_score'] + pad_impact.get('pleasure', 0)))
                    new_arousal = max(-100, min(100, current['arousal_score'] + pad_impact.get('arousal', 0)))
                    new_dominance = max(-100, min(100, current['dominance_score'] + pad_impact.get('dominance', 0)))
                    
                    new_emotion_score = self._calculate_emotion_score({
                        'pleasure': new_pleasure,
                        'arousal': new_arousal,
                        'dominance': new_dominance
                    })
                    
                    update_data.append((new_pleasure, new_arousal, new_dominance, new_emotion_score, character_id))
                    results[character_id] = True
                else:
                    # 创建新记录
                    new_pleasure = max(-100, min(100, pad_impact.get('pleasure', 0)))
                    new_arousal = max(-100, min(100, pad_impact.get('arousal', 0)))
                    new_dominance = max(-100, min(100, pad_impact.get('dominance', 0)))
                    new_emotion_score = self._calculate_emotion_score({
                        'pleasure': new_pleasure,
                        'arousal': new_arousal,
                        'dominance': new_dominance
                    })
                    
                    new_records.append((character_id, new_pleasure, new_arousal, new_dominance, new_emotion_score))
                    results[character_id] = True
            
            # 执行批量更新
            if update_data:
                update_query = """
                    UPDATE emotions 
                    SET pleasure_score = %s, arousal_score = %s, 
                        dominance_score = %s, current_emotion_score = %s
                    WHERE character_id = %s
                """
                self.db.execute_batch_update(update_query, update_data)
            
            # 执行批量插入
            if new_records:
                insert_query = """
                    INSERT INTO emotions (character_id, pleasure_score, arousal_score, 
                                      dominance_score, current_emotion_score)
                    VALUES (%s, %s, %s, %s, %s)
                """
                self.db.execute_batch_insert(insert_query, new_records)
            
            return results
            
        except Exception as e:
            print(f"批量更新情绪状态失败: {e}")
            return {update['character_id']: False for update in updates}

    def batch_initialize_characters(self, character_ids: List[str]) -> Dict[str, bool]:
        """
        批量初始化角色情绪状态 - 数据库层面批量操作
        
        Args:
            character_ids: 角色ID列表
            
        Returns:
            每个角色的初始化结果
        """
        if not character_ids:
            return {}
        
        import random
        try:
            # 先检查哪些角色已存在
            placeholders = ','.join(['%s'] * len(character_ids))
            query = f"""
                SELECT character_id FROM emotions 
                WHERE character_id IN ({placeholders})
            """
            existing_chars = {row['character_id'] for row in self.db.execute_query(query, character_ids)}
            
            # 过滤出需要初始化的角色
            new_character_ids = [cid for cid in character_ids if cid not in existing_chars]
            
            if not new_character_ids:
                return {cid: True for cid in character_ids}
            
            # 构建批量插入数据
            insert_data = []
            for character_id in new_character_ids:
                insert_data.append((
                    character_id,
                    random.randint(-50, 50),
                    random.randint(-50, 50),
                    random.randint(-50, 50),
                    random.randint(-50, 50)
                ))
            
            # 执行批量插入
            insert_query = """
                INSERT INTO emotions (character_id, pleasure_score, arousal_score, 
                                  dominance_score, current_emotion_score)
                VALUES (%s, %s, %s, %s, %s)
            """
            self.db.execute_batch_insert(insert_query, insert_data)
            
            # 返回结果
            return {cid: True for cid in character_ids}
            
        except Exception as e:
            print(f"批量初始化角色情绪失败: {e}")
            return {cid: False for cid in character_ids}


# 创建单例实例
emotion_dao = EmotionDAO()

# 便捷函数
get_emotion_by_character_id = emotion_dao.get_emotion_by_character_id
create_emotion = emotion_dao.create_emotion
update_emotion = emotion_dao.update_emotion
update_emotion_from_event = emotion_dao.update_emotion_from_event
initialize_character_emotion = emotion_dao.initialize_character_emotion
get_emotions_batch = emotion_dao.get_emotions_batch
batch_initialize_characters = emotion_dao.batch_initialize_characters