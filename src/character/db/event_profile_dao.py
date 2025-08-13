from src.character.model.event_profile import EventProfile, Event
from src.db.mongo_client import mongo_client
import os
from src.character.utils import convert_object_id

class EventProfileDAO:
    def __init__(self):
        # 获取数据库连接
        self.db = mongo_client.get_database()
        # 获取事件配置集合
        self.event_profiles_collection = self.db['event_profiles']

    def save_event_profile(self, event_profile):
        """保存事件配置到MongoDB

        Args:
            event_profile: 事件配置对象或字典

        Returns:
            str: 保存后的事件配置ID
        """
        try:
            # 检查是否为字典
            if isinstance(event_profile, dict):
                event_profile_dict = event_profile
            else:
                # 尝试调用to_dict方法，否则使用__dict__
                event_profile_dict = event_profile.to_dict() if hasattr(event_profile, 'to_dict') else event_profile.__dict__

            # 转换嵌套的Event对象为字典
            if 'life_path' in event_profile_dict and event_profile_dict['life_path']:
                event_profile_dict['life_path'] = [
                    event.to_dict() if hasattr(event, 'to_dict') else (event.__dict__ if not isinstance(event, dict) else event)
                    for event in event_profile_dict['life_path']
                ]


            
            event_profile_dict = convert_object_id(event_profile_dict)

            # 检查是否已存在此事件配置
            existing_profile = self.event_profiles_collection.find_one({'id': event_profile_dict.get('id')})

            if existing_profile:
                # 更新现有事件配置
                result = self.event_profiles_collection.update_one(
                    {'id': event_profile_dict.get('id')},
                    {'$set': event_profile_dict}
                )
                print(f"更新事件配置成功: {event_profile_dict.get('id')}")
                return event_profile_dict.get('id')
            else:
                # 插入新事件配置
                result = self.event_profiles_collection.insert_one(event_profile_dict)
                print(f"插入事件配置成功: {event_profile_dict.get('id')}")
                return event_profile_dict.get('id')
        except Exception as e:
            print(f"保存事件配置失败: {e}")
            raise

    def get_event_profile_by_id(self, profile_id):
        """根据ID获取事件配置

        Args:
            profile_id: 事件配置ID

        Returns:
            dict: 事件配置数据
        """
        try:
            return self.event_profiles_collection.find_one({'id': profile_id})
        except Exception as e:
            print(f"获取事件配置失败: {e}")
            raise

    def get_event_profiles_by_character_id(self, character_id):
        """根据角色ID获取事件配置

        Args:
            character_id: 角色ID

        Returns:
            list: 事件配置列表
        """
        try:
            return list(self.event_profiles_collection.find({'character_id': character_id}))
        except Exception as e:
            print(f"获取事件配置列表失败: {e}")
            raise

    def delete_event_profile_by_character_id(self, character_id):
        """根据角色ID删除事件配置

        Args:
            character_id: 角色ID

        Returns:
            bool: 是否删除成功
        """
        try:
            result = self.event_profiles_collection.delete_many({"character_id": character_id})
            print(f"删除角色 {character_id} 的事件配置成功，共删除 {result.deleted_count} 条记录")
            return result.deleted_count > 0
        except Exception as e:
            print(f"删除事件配置失败: {e}")
            return False

    def get_event_profile_by_event_id(self, event_id):
        """根据事件ID获取包含该事件的事件配置

        Args:
            event_id: 事件ID

        Returns:
            dict: 事件配置数据
        """
        try:
            return self.event_profiles_collection.find_one({'life_path.event_id': event_id})
        except Exception as e:
            print(f"根据事件ID获取事件配置失败: {e}")
            raise

    def delete_event_profile(self, profile_id):
        """删除事件配置

        Args:
            profile_id: 事件配置ID

        Returns:
            bool: 是否删除成功
        """
        try:
            result = self.event_profiles_collection.delete_one({'id': profile_id})
            success = result.deleted_count > 0
            if success:
                print(f"删除事件配置成功: {profile_id}")
            else:
                print(f"未找到要删除的事件配置: {profile_id}")
            return success
        except Exception as e:
            print(f"删除事件配置失败: {e}")
            raise

    def add_event_to_profile(self, profile_id, event):
        """向事件配置中添加事件

        Args:
            profile_id: 事件配置ID
            event: 事件对象

        Returns:
            bool: 是否添加成功
        """
        try:
            event_dict = event.to_dict() if hasattr(event, 'to_dict') else event.__dict__
            result = self.event_profiles_collection.update_one(
                {'id': profile_id},
                {'$push': {'life_path': event_dict}}
            )
            success = result.modified_count > 0
            if success:
                print(f"向事件配置添加事件成功: {event_dict.get('event_id')}")
            else:
                print(f"添加事件失败，未找到事件配置: {profile_id}")
            return success
        except Exception as e:
            print(f"添加事件失败: {e}")
            raise

    def remove_event_from_profile(self, profile_id, event_id):
        """从事件配置中移除事件

        Args:
            profile_id: 事件配置ID
            event_id: 事件ID

        Returns:
            bool: 是否移除成功
        """
        try:
            result = self.event_profiles_collection.update_one(
                {'id': profile_id},
                {'$pull': {'life_path': {'event_id': event_id}}}
            )
            success = result.modified_count > 0
            if success:
                print(f"从事件配置移除事件成功: {event_id}")
            else:
                print(f"移除事件失败，未找到事件或事件配置")
            return success
        except Exception as e:
            print(f"移除事件失败: {e}")
            raise

# 创建DAO实例
DAO = EventProfileDAO()

def save_event_profile(event_profile):
    """保存事件配置的便捷函数"""
    return DAO.save_event_profile(event_profile)

def get_event_profile_by_id(profile_id):
    """根据ID获取事件配置的便捷函数"""
    return DAO.get_event_profile_by_id(profile_id)

def get_event_profiles_by_character_id(character_id):
    """根据角色ID获取事件配置的便捷函数"""
    return DAO.get_event_profiles_by_character_id(character_id)

def delete_event_profile(profile_id):
    """删除事件配置的便捷函数"""
    return DAO.delete_event_profile(profile_id)

def add_event_to_profile(profile_id, event):
    """向事件配置中添加事件的便捷函数"""
    return DAO.add_event_to_profile(profile_id, event)

def remove_event_from_profile(profile_id, event_id):
    """从事件配置中移除事件的便捷函数"""
    return DAO.remove_event_from_profile(profile_id, event_id)

def delete_event_profile_by_character_id(character_id):
    """根据角色ID删除事件配置的便捷函数"""
    return DAO.delete_event_profile_by_character_id(character_id)