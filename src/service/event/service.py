import os
import sys
import asyncio
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.character.model.event_profile import EventProfile, Event
from src.character.event.life_path_manager import manager as life_path_manager
from src.character.event.event_profile_generator import EventProfileLLMGenerator
from src.character.db.event_profile_dao import EventProfileDAO
from src.character.db.character_dao import get_character_by_id, get_all_characters
from src.character.utils import convert_object_id


# 初始化DAO
event_profile_dao = EventProfileDAO()
# 初始化生成器（只创建一次，避免重复初始化）
generator = EventProfileLLMGenerator()
# 初始化logger
logger = logging.getLogger(__name__)

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
                profile_data = event_profiles[0]
                profile_id = profile_data['id']
                print(f"找到角色{character.name}的事件配置: {profile_id}")

            success = await life_path_manager.add_event_to_life_path(
                profile_id=profile_id,
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
    async def generate_event_profile(character_id: str, language: str = "Chinese") -> dict:
        """生成事件配置"""
        try:
            # 验证角色是否存在
            character = get_character_by_id(character_id)
            if not character:
                print(f"未找到角色ID为{character_id}的角色")
                return None
            # 生成事件配置（不生成life_path）
            event_profile = await generator.create_event_profile(character_id=character_id, language=language)

            # 转换为字典返回
            return event_profile.to_dict() if hasattr(event_profile, 'to_dict') else event_profile.__dict__
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
    def save_event_profile(event_profile: dict) -> str:
        """保存事件配置到数据库"""
        try:
            # 调用DAO层保存事件配置
            return event_profile_dao.save_event_profile(event_profile)
        except Exception as e:
            print(f"保存事件配置时出错: {e}")
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
    def get_event_profiles_by_character_id(character_id: str) -> Optional[List[dict]]:
        """根据角色ID获取事件配置列表"""
        try:
            # 调用DAO层获取事件配置
            return event_profile_dao.get_event_profiles_by_character_id(character_id)
        except Exception as e:
            print(f"获取事件配置时出错: {e}")
            return None

    @staticmethod
    def get_event_profiles_by_character_ids(character_ids: List[str]) -> Optional[Dict[str, List[dict]]]:
        """根据角色ID数组批量获取事件配置列表"""
        try:
            # 调用DAO层的批量查询方法
            result = event_profile_dao.get_event_profiles_by_character_ids(character_ids)
            # 使用convert_object_id函数处理结果中的ObjectId
            if result:
                result = convert_object_id(result)
            return result
        except Exception as e:
            print(f"批量获取事件配置时出错: {e}")
            return None

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
                if event_profile_dao.delete_event_profile_by_character_id(character_id):
                    deleted_count += 1
                    print(f"成功删除事件配置: {profile_id}")
                else:
                    print(f"删除事件配置失败: {profile_id}")

            print(f"共删除{deleted_count}个事件配置")
            return deleted_count > 0
        except Exception as e:
            print(f"根据角色ID删除事件配置时出错: {e}")
            return False


    @staticmethod
    async def batch_generate_life_paths(start_date: str, end_date: str, max_events: int = 3, limit: int = 0) -> Dict[str, Any]:
        """批量为多个角色生成生活轨迹

        Args:
            start_date: 开始日期
            end_date: 结束日期
            max_events: 每个角色的最大事件数
            limit: 处理的角色数量限制，0表示不限制

        Returns:
            Dict[str, Any]: 包含成功/失败统计的结果
        """
        try:
            logger.info(f"开始批量生成角色生活轨迹: 开始日期={start_date}, 结束日期={end_date}, 最大事件数={max_events}, 限制数量={limit}")
            start_time = time.time()

            # 获取所有角色
            all_characters = []
            batch_size = 100  # 每次获取的角色数量
            offset = 0
            
            while True:
                result = get_all_characters(limit=batch_size, offset=offset)
                if not result or not result.get('data'):
                    break
                
                batch_characters = result.get('data', [])
                all_characters.extend(batch_characters)
                
                # 应用限制
                if limit > 0 and len(all_characters) >= limit:
                    all_characters = all_characters[:limit]
                    break
                
                # 如果没有更多角色，退出循环
                if len(batch_characters) < batch_size:
                    break
                
                offset += batch_size
                await asyncio.sleep(0.1)  # 避免请求过于频繁

            total_characters = len(all_characters)
            logger.info(f"共获取到{total_characters}个角色")
            
            # 初始化结果统计
            success_count = 0
            failed_count = 0
            failed_characters = []
            
            # 使用ThreadPoolExecutor进行多线程处理
            with ThreadPoolExecutor(max_workers=10) as executor:
                # 创建任务列表
                loop = asyncio.get_event_loop()
                tasks = []
                
                for character in all_characters:
                    # 为每个角色创建一个异步任务
                    tasks.append(
                        loop.run_in_executor(
                            executor,
                            lambda c=character: EventService._process_character_life_path(
                                c.get('character_id'), start_date, end_date, max_events
                            )
                        )
                    )
                
                # 等待所有任务完成
                results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            for i, result in enumerate(results):
                character = all_characters[i]
                character_id = character.get('character_id')
                
                if isinstance(result, Exception):
                    failed_count += 1
                    failed_characters.append({
                        "character_id": character_id,
                        "character_name": character.get('name', '未知'),
                        "error": str(result)
                    })
                    logger.error(f"角色{character.get('name', '未知')}({character_id})生成生活轨迹失败: {str(result)}")
                else:
                    if result.get('success', False):
                        success_count += 1
                        logger.info(f"角色{character.get('name', '未知')}({character_id})生成生活轨迹成功")
                    else:
                        failed_count += 1
                        failed_characters.append({
                            "character_id": character_id,
                            "character_name": character.get('name', '未知'),
                            "error": result.get('message', '未知错误')
                        })
                        logger.error(f"角色{character.get('name', '未知')}({character_id})生成生活轨迹失败: {result.get('message', '未知错误')}")
            
            end_time = time.time()
            logger.info(f"批量生成角色生活轨迹完成: 成功{success_count}个, 失败{failed_count}个, 耗时{end_time - start_time:.2f}秒")
            
            return {
                "total_characters": total_characters,
                "success_count": success_count,
                "failed_count": failed_count,
                "failed_characters": failed_characters
            }
        except Exception as e:
            logger.error(f"批量生成生活轨迹时发生异常: {str(e)}")
            return {
                "success": False,
                "message": f"批量生成生活轨迹失败: {str(e)}"
            }

    @staticmethod
    def _process_character_life_path(character_id: str, start_date: str, end_date: str, max_events: int) -> Dict[str, Any]:
        """处理单个角色的生活轨迹生成（在线程池中执行）"""
        try:
            # 在子线程中运行异步函数
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                EventService._generate_character_life_path(character_id, start_date, end_date, max_events)
            )
            loop.close()
            return result
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    async def _generate_character_life_path(character_id: str, start_date: str, end_date: str, max_events: int) -> Dict[str, Any]:
        """生成单个角色的生活轨迹"""
        try:
            # 验证角色是否存在
            character = get_character_by_id(character_id)
            if not character:
                return {"success": False, "message": "角色不存在"}

            # 检查事件配置是否存在
            event_profiles = event_profile_dao.get_event_profiles_by_character_id(character_id)
            if not event_profiles or len(event_profiles) == 0:
                return {"success": False, "message": "事件配置不存在，请先创建"}
            else:
                # 取第一个事件配置
                event_profile = event_profiles[0]

            # 生成生活轨迹事件
            success = await life_path_manager.add_event_to_life_path(
                profile_id=event_profile.get('id'),
                start_time=start_date,
                end_time=end_date,
                max_events=max_events
            )

            if success:
                return {"success": True, "message": "事件生成成功"}
            else:
                return {"success": False, "message": "事件生成失败"}
        except Exception as e:
            return {"success": False, "message": str(e)}

# 创建服务实例
event_service = EventService()