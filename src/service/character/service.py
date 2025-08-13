import os
import sys
import asyncio
from typing import List, Optional
from src.character.model.character import Character
from src.character.llm_gen import CharacterLLMGenerator
from src.character.db.character_dao import save_character, get_character_by_id as get_character_by_id_dao, get_all_characters as get_all_characters_dao, delete_character as delete_character_dao
from src.character.db.event_profile_dao import delete_event_profile_by_character_id
from src.service.event.service import event_service

class CharacterService:
    @staticmethod
    async def generate_character(name: str = None, age: int = None, gender: str = None, occupation: str = None, language: str = "Chinese"):
        """使用LLM生成角色并保存到数据库"""
        generator = CharacterLLMGenerator()
        try:
            # 生成角色
            character = await generator.generate_character(
                name=name, 
                age=age, 
                gender=gender, 
                occupation=occupation, 
                language=language
            )
            
            # 保存角色到数据库
            if character:
                save_character(character)
            return character
        except Exception as e:
            print(f"生成角色时出错: {e}")
            return None

    @staticmethod
    def get_character_by_id(character_id: str) -> Optional[Character]:
        """根据ID获取角色详情"""
        return get_character_by_id_dao(character_id)

    @staticmethod
    def get_all_characters(limit: int = 10, offset: int = 0) -> List[dict]:
        """获取所有角色列表"""
        all_characters = get_all_characters_dao()
        # 应用分页
        return all_characters[offset:offset+limit]

    @staticmethod
    def delete_character(character_id: str) -> bool:
        """删除角色及其关联事件"""
        # 先检查角色是否存在
        character = get_character_by_id_dao(character_id)
        if not character:
            return False

        # 删除角色
        if not delete_character_dao(character_id):
            return False

        # 删除关联的事件配置
        delete_event_profile_by_character_id(character_id)

        return True

# 创建服务实例
character_service = CharacterService()