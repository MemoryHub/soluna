import os
import sys
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.character.model.event_profile import EventProfile, Event
from src.character.event.life_path_manager import manager as life_path_manager
from src.character.event.event_profile_generator import EventProfileLLMGenerator
from src.character.db.event_profile_dao import EventProfileDAO
from src.character.db.character_dao import get_character_by_id
from src.character.db.character_dao import get_character_by_id


# 初始化DAO
event_profile_dao = EventProfileDAO()
# 初始化生成器（只创建一次，避免重复初始化）
generator = EventProfileLLMGenerator()

class EventService:
    @staticmethod
    async def generate_life_path(character_id: str, start_date: str, end_date: str, max_events: int = 3) -> Dict[str, Any]:
        """生成life_path"""
        try:
            # 验证角色是否存在
            character = get_character_by_id(character_id)
            if not character:
                print(f"未找到角色ID为{character_id}的角色")
                return {"success": False, "message": "角色不存在"}

            # 检查事件配置是否存在
            event_profiles = event_profile_dao.get_event_profiles_by_character_id(character_id)
            if not event_profiles or len(event_profiles) == 0:
                print(f"未找到角色{character.name}的事件配置，请先创建事件配置")
                return {"success": False, "message": "事件配置不存在，请先创建"}
            else:
                event_profile = EventProfile(**event_profiles[0])
                print(f"找到角色{character.name}的事件配置: {event_profile.id}")

            success = await life_path_manager.add_event_to_life_path(
                profile_id=event_profile.id,
                start_time=start_date,
                end_time=end_date,
                max_events=max_events
            )

            if success:
                print("添加生活轨迹成功!")
                return {"success": True, "message": "事件生成成功", "event_count": max_events}
            else:
                print("添加生活轨迹失败。")
                return {"success": False, "message": "事件生成失败"}
        except ValueError as ve:
            print(f"输入格式错误: {ve}")
            return {"success": False, "message": f"输入格式错误: {str(ve)}"}
        except Exception as e:
            print(f"生成事件时出错: {e}")
            return {"success": False, "message": f"生成事件时出错: {str(e)}"}

    @staticmethod
    def get_character_events(character_id: str) -> List[Event]:
        """获取角色的所有事件"""
        event_profiles = event_profile_dao.get_event_profiles_by_character_id(character_id)
        if not event_profiles or len(event_profiles) == 0:
            return []
        
        # 从事件配置中提取事件列表
        events = event_profiles[0].get("life_path", [])
        # 将事件字典转换为Event对象
        return [Event(**event) for event in events]

    @staticmethod
    async def create_event_profile(character_id: str, language: str = "Chinese") -> str:
        """创建事件配置"""
        try:
            # 验证角色是否存在
            character = get_character_by_id(character_id)
            if not character:
                print(f"未找到角色ID为{character_id}的角色")
                return None
            # 生成事件配置（不生成life_path）
            event_profile = await generator.create_event_profile(character_id=character_id, language=language)

            return event_profile.id
        except ValueError as ve:
            if "已存在事件配置" in str(ve):
                print(f"错误: {ve}")
            else:
                print(f"生成事件配置时出错: {ve}")
            return None
        except Exception as e:
            print(f"生成事件配置时出现未知错误: {e}")
            return None

    @staticmethod
    async def delete_event_profile(profile_id: str) -> bool:
        """删除事件配置"""
        try:
            # 调用DAO层删除事件配置
            return event_profile_dao.delete_event_profile(profile_id)
        except Exception as e:
            print(f"删除事件配置时出错: {e}")
            return False

    @staticmethod
    async def delete_event_profile_by_character_id(character_id: str) -> bool:
        """根据角色ID删除事件配置"""
        try:
            # 验证角色是否存在
            character = get_character_by_id(character_id)
            if not character:
                print(f"未找到角色ID为{character_id}的角色")
                return False

            # 获取角色关联的所有事件配置
            event_profiles = event_profile_dao.get_event_profiles_by_character_id(character_id)
            if not event_profiles or len(event_profiles) == 0:
                print(f"未找到角色{character.name}的事件配置")
                return False

            # 逐个删除事件配置
            deleted_count = 0
            for profile in event_profiles:
                profile_id = profile.get('id')
                if event_profile_dao.delete_event_profile(profile_id):
                    deleted_count += 1
                    print(f"成功删除事件配置: {profile_id}")
                else:
                    print(f"删除事件配置失败: {profile_id}")

            print(f"共删除{deleted_count}个事件配置")
            return deleted_count > 0
        except Exception as e:
            print(f"根据角色ID删除事件配置时出错: {e}")
            return False


# 创建服务实例
event_service = EventService()