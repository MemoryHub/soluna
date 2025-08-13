import os
import json
import uuid
from datetime import datetime, timedelta
from bson import ObjectId
from src.character.utils import convert_object_id
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from src.character.model.event_profile import EventProfile, Event
from src.character.db.character_dao import get_character_by_id
from src.character.db.event_profile_dao import (
    save_event_profile,
    get_event_profiles_by_character_id,
    get_event_profile_by_id,
    delete_event_profile
)
from dotenv import load_dotenv
from .prompts import (
    GENERATOR_SYSTEM_MESSAGE_TEMPLATE,
    REVIEWER_SYSTEM_MESSAGE
)

load_dotenv()

class EventProfileLLMGenerator:
    """事件配置生成器类，负责为角色生成详细的事件配置(EventProfile)

    使用大语言模型和Agent系统生成和审查角色的事件配置，确保配置的合理性和连贯性
    """
    def __init__(self):
        """初始化事件配置生成器

        设置模型客户端、初始化agent和团队
        """
        # 初始化模型客户端
        self.model_client = OpenAIChatCompletionClient(
            model="qwen-plus",
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("BASE_URL"),
            model_info={
                "vision": False,
                "function_calling": False,
                "json_output": True,
                "family": "qwen",
                "structured_output": True
            }
        )
        # 初始化两个agent
        self.generator_agent = None
        self.reviewer_agent = None
        # 创建团队
        self.team = None

    def _create_generator_agent(self, character_info):
        """创建用于生成事件配置字段的agent

        根据角色信息创建事件配置生成agent，使用预设的提示词模板

        Args:
            character_info: 角色信息JSON字符串

        Returns:
            AssistantAgent: 事件配置生成agent实例
        """
        # 生成系统消息
        system_message = GENERATOR_SYSTEM_MESSAGE_TEMPLATE.format(character_info=character_info)

        return AssistantAgent(
            "EventProfileGenerator",
            model_client=self.model_client,
            system_message=system_message
        )

    def _create_reviewer_agent(self, character_info):
        """创建用于审查事件配置自洽性的agent

        根据角色信息创建事件配置审查agent，使用预设的提示词模板

        Args:
            character_info: 角色信息JSON字符串

        Returns:
            AssistantAgent: 事件配置审查agent实例
        """
        system_message = REVIEWER_SYSTEM_MESSAGE.format(character_info=character_info)

        return AssistantAgent(
            "EventProfileReviewer",
            model_client=self.model_client,
            system_message=system_message
        )

    async def generate_event_profile(self, character_id: str, language: str = "Chinese") -> EventProfile:
        """生成事件配置并审查其自洽性

        使用生成器agent和审查器agent协作，为指定角色生成详细的事件配置
        包括当前阶段、未来趋势、事件触发条件和生活轨迹事件等

        Args:
            character_id: 角色ID，用于获取角色信息
            language: 生成语言，默认为Chinese

        Returns:
            EventProfile: 生成的事件配置对象，包含完整的事件配置信息

        Raises:
            ValueError: 当角色不存在或无法解析生成结果时抛出
        """
        # 获取角色信息
        character = get_character_by_id(character_id)
        if not character:
            raise ValueError(f"未找到角色ID为{character_id}的角色")

        # 准备角色信息字符串，转换可能的ObjectId和datetime类型
        character_dict = convert_object_id(character.to_dict())
        character_info = json.dumps(character_dict, ensure_ascii=False)

        # 初始化agents
        self.generator_agent = self._create_generator_agent(character_info)
        self.reviewer_agent = self._create_reviewer_agent(character_info)

        # 创建团队
        self.team = RoundRobinGroupChat(
            [self.generator_agent, self.reviewer_agent],
            termination_condition=MaxMessageTermination(3)
        )

        # 准备初始提示
        initial_task = "为角色生成一个详细的事件配置(EventProfile)。"
        # 添加语言控制指令
        if language == "English":
            initial_task += " 请确保所有字段内容都使用英文输出。"
        else:
            initial_task += " 请确保所有字段内容都使用中文输出。"

        # 运行团队生成事件配置
        result = await self.team.run(task=initial_task)

        # 解析结果中的JSON
        event_profile_data = None
        original_result = result
        result_message = None
        
        # 查找EventProfileGenerator的消息
        if original_result and hasattr(original_result, 'messages') and original_result.messages:
            for message in original_result.messages:
                if hasattr(message, 'source') and message.source == 'EventProfileGenerator':
                    result_message = message
                    break
            # 如果没找到，使用最后一条消息
            if not result_message:
                result_message = original_result.messages[-1]
        
        # 从找到的消息中提取JSON
        if result_message and hasattr(result_message, 'content') and result_message.content:
            if isinstance(result_message.content, str) and '{' in result_message.content:
                try:
                    # 提取JSON部分
                    start_idx = result_message.content.find('{')
                    end_idx = result_message.content.rfind('}') + 1
                    json_str = result_message.content[start_idx:end_idx]
                    event_profile_data = json.loads(json_str)
                except json.JSONDecodeError:
                    pass

        # 错误处理和日志记录
        error_message = None
        if not event_profile_data:
            if result_message and hasattr(result_message, 'content'):
                error_message = f"无法从EventProfileGenerator的响应中解析出有效的JSON。响应内容: {str(result_message.content)[:200]}..."
            else:
                error_message = "未收到EventProfileGenerator的有效响应"
            raise ValueError(error_message)

        # 创建EventProfile对象
        event_profile = EventProfile(character_id=character_id)

        # 填充字段
        if 'id' in event_profile_data:
            event_profile.id = event_profile_data['id']
        else:
            event_profile.id = str(uuid.uuid4())

        if 'current_stage' in event_profile_data:
            event_profile.current_stage = event_profile_data['current_stage']

        if 'next_trend' in event_profile_data:
            event_profile.next_trend = event_profile_data['next_trend']

        if 'event_triggers' in event_profile_data:
            event_profile.event_triggers = event_profile_data['event_triggers']

        # 处理life_path
        if 'life_path' in event_profile_data and event_profile_data['life_path']:
            for event_data in event_profile_data['life_path']:
                # 确保event_id存在
                if 'event_id' not in event_data:
                    event_data['event_id'] = str(uuid.uuid4())
                # 转换时间字符串为datetime对象
                if 'start_time' in event_data and isinstance(event_data['start_time'], str):
                    try:
                        event_data['start_time'] = datetime.fromisoformat(event_data['start_time'])
                    except ValueError:
                        # 如果格式不正确且角色信息中包含年龄，则根据年龄生成合理的时间
                        try:
                            # 保留原始代码结构，但不生成随机时间
                            # 时间应该由大模型在生成事件时就确定
                            pass
                        except:
                            # 如果无法获取年龄信息，设置为当前时间
                            event_data['start_time'] = datetime.now()
                if 'end_time' in event_data and event_data['end_time'] and isinstance(event_data['end_time'], str):
                    try:
                        event_data['end_time'] = datetime.fromisoformat(event_data['end_time'])
                    except ValueError:
                        # 确保start_time是datetime对象
                        if not isinstance(event_data.get('start_time'), datetime):
                            event_data['start_time'] = datetime.now()
                        # 设置为开始时间后一小时
                        event_data['end_time'] = event_data['start_time'] + timedelta(hours=1)
                # 创建Event对象
                event = Event(
                    event_id=event_data['event_id'],
                    type=event_data.get('type', ''),
                    description=event_data.get('description', ''),
                    start_time=event_data.get('start_time', datetime.now()),
                    status=event_data.get('status', 'completed'),
                    is_key_event=event_data.get('is_key_event', False),
                    impact=event_data.get('impact', ''),
                    location=event_data.get('location', ''),
                    participants=event_data.get('participants', []),
                    outcome=event_data.get('outcome', ''),
                    emotion_score=event_data.get('emotion_score', 0.0),
                    end_time=event_data.get('end_time'),
                    dependencies=event_data.get('dependencies', [])
                )
                # 添加到life_path
                event_profile.life_path.append(event)

        # 按时间排序life_path
        event_profile.life_path.sort(key=lambda x: x.start_time)

        return event_profile

    async def create_event_profile(self, character_id: str, language: str = "Chinese") -> str:
        """创建事件配置

        检查角色是否已存在事件配置，如果不存在则生成并保存新的事件配置

        Args:
            character_id: 角色ID
            language: 生成语言，默认为Chinese

        Returns:
            str: 事件配置ID，如果已存在则返回第一个配置ID

        Raises:
            ValueError: 当角色不存在时抛出
        """
        # 检查是否已存在事件配置
        existing_profiles = get_event_profiles_by_character_id(character_id)
        if existing_profiles and len(existing_profiles) > 0:
            print(f"角色{character_id}已存在事件配置，返回第一个配置ID")
            return str(existing_profiles[0])

        # 生成新的事件配置
        event_profile = await self.generate_event_profile(character_id, language)

        # 返回生成的事件配置对象，不保存到数据库
        return event_profile

    async def update_event_profile(self, profile_id: str, updates: dict) -> str:
        """更新事件配置

        根据提供的更新需求，更新现有事件配置并保存

        Args:
            profile_id: 事件配置ID
            updates: 要更新的字段和值的字典

        Returns:
            str: 更新后的事件配置ID

        Raises:
            ValueError: 当事件配置不存在、角色不存在或无法解析更新结果时抛出
        """
        # 获取现有的事件配置
        existing_profile = get_event_profile_by_id(profile_id)
        if not existing_profile:
            raise ValueError(f"未找到事件配置ID为{profile_id}的配置")

        # 获取关联的角色信息
        character = get_character_by_id(existing_profile['character_id'])
        if not character:
            raise ValueError(f"未找到角色ID为{existing_profile['character_id']}的角色")

        # 准备角色信息字符串，转换可能的ObjectId和datetime类型
        character_dict = convert_object_id(character.to_dict())
        character_info = json.dumps(character_dict, ensure_ascii=False)

        # 初始化agents
        self.generator_agent = self._create_generator_agent(character_info)
        self.reviewer_agent = self._create_reviewer_agent(character_info)

        # 创建团队
        self.team = RoundRobinGroupChat(
            [self.generator_agent, self.reviewer_agent],
            termination_condition=MaxMessageTermination(3)
        )

        # 准备更新提示 - 转换ObjectId
        existing_profile_dict = convert_object_id(existing_profile)
        update_task = f"请根据以下更新需求修改事件配置：\n{json.dumps(updates, ensure_ascii=False)}\n\n当前事件配置：\n{json.dumps(existing_profile_dict, ensure_ascii=False)}"

        # 运行团队更新事件配置
        result = await self.team.run(task=update_task)

        # 解析结果中的JSON
        updated_profile_data = None
        for message in result.messages:
            if message.content and isinstance(message.content, str) and '{' in message.content:
                try:
                    start_idx = message.content.find('{')
                    end_idx = message.content.rfind('}') + 1
                    json_str = message.content[start_idx:end_idx]
                    updated_profile_data = json.loads(json_str)
                    break
                except json.JSONDecodeError:
                    pass

        if not updated_profile_data:
            raise ValueError("无法从更新结果中解析出有效的EventProfile JSON")

        # 创建更新后的EventProfile对象
        event_profile = EventProfile(character_id=existing_profile['character_id'])
        event_profile.id = profile_id

        # 合并更新字段
        for key, value in updated_profile_data.items():
            if hasattr(event_profile, key) and key != 'id' and key != 'character_id':
                setattr(event_profile, key, value)

        # 特别处理life_path
        if 'life_path' in updated_profile_data and updated_profile_data['life_path']:
            event_profile.life_path = []
            for event_data in updated_profile_data['life_path']:
                # 转换时间格式
                if 'start_time' in event_data and isinstance(event_data['start_time'], str):
                    try:
                        event_data['start_time'] = datetime.fromisoformat(event_data['start_time'])
                    except ValueError:
                        # 如果格式不正确且角色信息中包含年龄，则根据年龄生成合理的时间
                        try:
                            # 保留原始代码结构，但不生成随机时间
                            # 时间应该由大模型在生成事件时就确定
                            pass
                        except:
                            # 如果无法获取年龄信息，设置为当前时间
                            event_data['start_time'] = datetime.now()
                if 'end_time' in event_data and event_data['end_time'] and isinstance(event_data['end_time'], str):
                    try:
                        event_data['end_time'] = datetime.fromisoformat(event_data['end_time'])
                    except ValueError:
                        # 确保start_time是datetime对象
                        if not isinstance(event_data.get('start_time'), datetime):
                            event_data['start_time'] = datetime.now()
                        event_data['end_time'] = event_data['start_time'] + timedelta(hours=1)
                # 创建Event对象
                event = Event(
                    event_id=event_data.get('event_id', str(uuid.uuid4())),
                    type=event_data.get('type', ''),
                    description=event_data.get('description', ''),
                    start_time=event_data.get('start_time', datetime.now()),
                    status=event_data.get('status', 'completed'),
                    is_key_event=event_data.get('is_key_event', False),
                    impact=event_data.get('impact', ''),
                    location=event_data.get('location', ''),
                    participants=event_data.get('participants', []),
                    outcome=event_data.get('outcome', ''),
                    emotion_score=event_data.get('emotion_score', 0.0),
                    end_time=event_data.get('end_time'),
                    dependencies=event_data.get('dependencies', [])
                )
                event_profile.life_path.append(event)

        # 按时间排序
        event_profile.life_path.sort(key=lambda x: x.start_time)

        # 保存更新后的事件配置
        return save_event_profile(event_profile)

    def get_event_profiles(self, character_id: str) -> list:
        """根据角色ID获取事件配置列表

        查询指定角色的所有事件配置

        Args:
            character_id: 角色ID

        Returns:
            list: 事件配置列表
        """
        return get_event_profiles_by_character_id(character_id)

    def get_event_profile(self, profile_id: str) -> dict:
        """根据ID获取事件配置

        查询指定ID的事件配置详情

        Args:
            profile_id: 事件配置ID

        Returns:
            dict: 事件配置数据，如果不存在则返回None
        """
        return get_event_profile_by_id(profile_id)

    def delete_event_profile_by_id(self, profile_id: str) -> bool:
        """删除事件配置

        删除指定ID的事件配置

        Args:
            profile_id: 事件配置ID

        Returns:
            bool: 是否删除成功
        """
        return delete_event_profile(profile_id)

# 创建生成器实例
generator = EventProfileLLMGenerator()

async def update_event_profile(profile_id: str, updates: dict) -> str:
    """更新事件配置的便捷函数

    便捷函数，调用generator实例的update_event_profile方法

    Args:
        profile_id: 事件配置ID
        updates: 要更新的字段和值的字典

    Returns:
        str: 更新后的事件配置ID
    """
    return await generator.update_event_profile(profile_id, updates)

def get_event_profiles(character_id: str) -> list:
    """获取事件配置列表的便捷函数

    便捷函数，调用generator实例的get_event_profiles方法

    Args:
        character_id: 角色ID

    Returns:
        list: 事件配置列表
    """
    return generator.get_event_profiles(character_id)

def get_event_profile(profile_id: str) -> dict:
    """获取事件配置的便捷函数

    便捷函数，调用generator实例的get_event_profile方法

    Args:
        profile_id: 事件配置ID

    Returns:
        dict: 事件配置数据
    """
    return generator.get_event_profile(profile_id)

def delete_event_profile(profile_id: str) -> bool:
    """删除事件配置的便捷函数

    便捷函数，调用generator实例的delete_event_profile_by_id方法

    Args:
        profile_id: 事件配置ID

    Returns:
        bool: 是否删除成功
    """
    return generator.delete_event_profile_by_id(profile_id)