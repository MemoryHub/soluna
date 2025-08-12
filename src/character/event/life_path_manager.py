import os
import json
import uuid
import re
from datetime import datetime, timedelta
from bson import ObjectId
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from src.character.model.event_profile import EventProfile, Event
from src.character.db.character_dao import get_character_by_id
from src.character.db.event_profile_dao import (
    get_event_profile_by_id,
    add_event_to_profile,
    remove_event_from_profile
)
from dotenv import load_dotenv
from .prompts import (
    DAILY_EVENT_GENERATOR_SYSTEM_MESSAGE_TEMPLATE,
    LIFE_PATH_REVIEWER_SYSTEM_MESSAGE
)

def convert_object_id(obj):
    """转换MongoDB ObjectId和datetime为可JSON序列化的类型

    递归处理嵌套对象，将MongoDB的ObjectId转换为字符串，datetime转换为ISO格式字符串

    Args:
        obj: 要转换的对象，可以是字典、列表、ObjectId、datetime或其他类型

    Returns:
        转换后的可JSON序列化对象
    """
    if isinstance(obj, dict):
        return {k: convert_object_id(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_object_id(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()  # 转换为ISO格式字符串
    else:
        return obj

load_dotenv()

class LifePathManager:
    """生活轨迹管理器类，负责为角色的事件配置添加和管理生活轨迹事件

    使用大语言模型和Agent系统生成和审查角色的日常事件，确保事件的合理性和连贯性
    """
    def __init__(self):
        """初始化生活轨迹管理器

        设置模型客户端、初始化agent
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
        # 初始化agents
        self.daily_event_agent = None
        self.daily_event_reviewer_agent = None

    def _create_daily_event_generator_agent(self, character_info, existing_profile, start_time, end_time, max_events, existing_events_info=""):
        """创建用于生成日常事件的agent

        根据角色信息、现有事件配置和时间范围创建日常事件生成agent，使用预设的提示词模板

        Args:
            character_info: 角色信息JSON字符串
            existing_profile: 现有事件配置JSON字符串
            start_time: 事件开始时间 (格式: YYYY-MM-DD)
            end_time: 事件结束时间 (格式: YYYY-MM-DD)
            max_events: 最大事件数量
            existing_events_info: 已有事件信息字符串

        Returns:
            AssistantAgent: 日常事件生成agent实例
        """
        system_message = DAILY_EVENT_GENERATOR_SYSTEM_MESSAGE_TEMPLATE.format(
            character_info=character_info,
            existing_profile=existing_profile,
            existing_events_info=existing_events_info,
            start_time=start_time,
            end_time=end_time,
            max_events=max_events
        )

        return AssistantAgent(
            "DailyEventGenerator",
            model_client=self.model_client,
            system_message=system_message
        )

    def _create_life_path_reviewer_agent(self, character_info, existing_profile):
        """创建生活轨迹审查agent

        根据角色信息和现有事件配置创建生活轨迹审查agent，使用预设的提示词模板

        Args:
            character_info: 角色信息JSON字符串
            existing_profile: 现有事件配置JSON字符串

        Returns:
            AssistantAgent: 生活轨迹审查agent实例
        """
        # 生成系统消息
        system_message = LIFE_PATH_REVIEWER_SYSTEM_MESSAGE.format(
            character_info=character_info,
            existing_profile=existing_profile
        )

        return AssistantAgent(
            "LifePathReviewer",
            model_client=self.model_client,
            system_message=system_message
        )

    async def add_event_to_life_path(self, profile_id: str, start_time: str, end_time: str, max_events: int = 3) -> bool:
        """向事件配置的life_path添加事件

        为指定的事件配置在指定时间范围内生成并添加日常事件

        Args:
            profile_id: 事件配置ID
            start_time: 事件开始时间 (格式: YYYY-MM-DD)
            end_time: 事件结束时间 (格式: YYYY-MM-DD)
            max_events: 最大事件数量 (默认: 3)

        Returns:
            bool: 是否添加成功，如果至少添加一个事件则返回True

        Raises:
            ValueError: 当事件配置不存在、角色不存在或无法解析生成结果时抛出
            TypeError: 当事件配置类型不正确时抛出
        """
        # 验证并获取事件配置
        profile = self._validate_and_get_profile(profile_id)

        # 筛选和排序指定日期范围内的已有事件
        existing_events = self._filter_and_sort_existing_events(profile, start_time, end_time)

        # 准备agent上下文信息
        character_info, existing_profile, existing_events_info = self._prepare_agent_context(
            profile, existing_events
        )

        # 初始化agent并生成事件
        events_json = await self._generate_events_with_agents(
            character_info, existing_profile, start_time, end_time, max_events, existing_events_info
        )

        # 处理并添加生成的事件
        success_count = await self._process_and_add_events(profile_id, events_json, max_events)

        return success_count > 0  # 如果至少添加成功一个事件，则返回True

    def _validate_and_get_profile(self, profile_id: str) -> dict:
        """验证并获取事件配置

        Args:
            profile_id: 事件配置ID

        Returns:
            dict: 事件配置字典

        Raises:
            ValueError: 当事件配置不存在时抛出
            TypeError: 当事件配置类型不正确时抛出
        """
        profile = get_event_profile_by_id(profile_id)
        if not profile:
            raise ValueError(f"未找到事件配置ID为{profile_id}的配置")

        # 确保profile是字典类型
        if not isinstance(profile, dict):
            print(f"警告: 预期profile为字典，但得到{type(profile)}")
            # 尝试转换为字典
            try:
                profile = profile.to_dict() if hasattr(profile, 'to_dict') else profile.__dict__
            except Exception as e:
                raise TypeError("事件配置必须是字典类型")

        return profile

    def _filter_and_sort_existing_events(self, profile: dict, start_time: str, end_time: str) -> list:
        """筛选和排序指定日期范围内的已有事件

        Args:
            profile: 事件配置字典
            start_time: 事件开始时间 (格式: YYYY-MM-DD)
            end_time: 事件结束时间 (格式: YYYY-MM-DD)

        Returns:
            list: 筛选并排序后的事件列表
        """
        existing_events = []
        if 'life_path' in profile and profile['life_path']:
            start_date = datetime.strptime(start_time, "%Y-%m-%d")
            end_date = datetime.strptime(end_time, "%Y-%m-%d")
            for event_dict in profile['life_path']:
                # 解析事件开始时间
                if 'start_time' in event_dict:
                    try:
                        # 确保start_time是字符串类型
                        start_time_str = event_dict['start_time']
                        if not isinstance(start_time_str, str):
                            start_time_str = str(start_time_str)
                        event_start = datetime.fromisoformat(start_time_str)
                        # 检查事件是否在指定日期范围内
                        if start_date.date() <= event_start.date() <= end_date.date():
                            existing_events.append(event_dict)
                    except ValueError:
                        pass

        # 按时间顺序排序已有事件
        existing_events.sort(key=lambda x: x.get('start_time', ''))
        return existing_events

    def _prepare_agent_context(self, profile: dict, existing_events: list) -> tuple:
        """准备agent上下文信息

        Args:
            profile: 事件配置字典
            existing_events: 已有事件列表

        Returns:
            tuple: (角色信息字符串, 现有配置字符串, 已有事件信息字符串)

        Raises:
            ValueError: 当角色不存在时抛出
        """
        # 获取关联的角色信息
        character = get_character_by_id(profile['character_id'])
        if not character:
            raise ValueError(f"未找到角色ID为{profile['character_id']}的角色")

        # 准备角色信息字符串
        character_info = json.dumps(character.to_dict(), ensure_ascii=False)

        # 使用模块级函数转换ObjectId
        profile_dict = convert_object_id(profile)
        existing_profile = json.dumps(profile_dict, ensure_ascii=False)

        # 准备已有事件信息
        existing_events_info = ""
        if existing_events:
            existing_events_info = "以下是该角色在此日期范围内已有的事件，请注意避免时间冲突，并保持事件的连贯性：\n"
            for event in existing_events:
                event_time = event.get('start_time', '未知时间')
                event_desc = event.get('description', '无描述')
                existing_events_info += f"- {event_time}: {event_desc}\n"

        return character_info, existing_profile, existing_events_info

    async def _generate_events_with_agents(self, character_info: str, existing_profile: str, start_time: str, end_time: str, max_events: int, existing_events_info: str) -> list:
        """使用agent生成事件

        Args:
            character_info: 角色信息字符串
            existing_profile: 现有配置字符串
            start_time: 事件开始时间
            end_time: 事件结束时间
            max_events: 最大事件数量
            existing_events_info: 已有事件信息字符串

        Returns:
            list: 生成的事件列表

        Raises:
            ValueError: 当无法解析生成结果时抛出
        """
        # 初始化日常事件生成agent和审查agent
        self.daily_event_agent = self._create_daily_event_generator_agent(
            character_info, existing_profile, start_time, end_time, max_events, existing_events_info
        )
        self.daily_event_reviewer_agent = self._create_life_path_reviewer_agent(character_info, existing_profile)

        # 准备提示，添加具体时间信息
        task = f"请在{start_time} 00:00:00至{end_time} 23:59:59期间为角色生成最多{max_events}个合理的日常事件。"

        # 运行agent生成事件
        team = RoundRobinGroupChat(
            [self.daily_event_agent, self.daily_event_reviewer_agent],
            termination_condition=MaxMessageTermination(3)
        )
        result = await team.run(task=task)

        # 获取DailyEventGenerator的回复
        original_result = result
        result = None
        if original_result and hasattr(original_result, 'messages') and original_result.messages:
            # 查找DailyEventGenerator的消息
            for message in original_result.messages:
                if hasattr(message, 'source') and message.source == 'DailyEventGenerator':
                    result = message
                    break
            # 如果没找到，使用最后一条消息
            if not result:
                result = original_result.messages[-1]
        else:
            result = None

        # 解析结果中的事件数据列表
        events_json = None
        error_message = None

        if result and hasattr(result, 'content') and result.content:
            # 尝试提取JSON内容
            try:
                # 寻找JSON开始和结束位置
                if '[' in result.content and ']' in result.content:
                    start_idx = result.content.find('[')
                    end_idx = result.content.rfind(']') + 1
                    json_str = result.content[start_idx:end_idx]
                    events_json = json.loads(json_str)
                    # 验证是否为列表
                    if not isinstance(events_json, list):
                        error_message = "解析结果不是有效的列表"
                        events_json = None
                elif '{' in result.content and '}' in result.content:
                    start_idx = result.content.find('{')
                    end_idx = result.content.rfind('}') + 1
                    json_str = result.content[start_idx:end_idx]
                    single_event = json.loads(json_str)
                    events_json = [single_event]
                else:
                    # 尝试直接解析整个content
                    try:
                        events_json = json.loads(result.content)
                        if not isinstance(events_json, list):
                            events_json = [events_json]
                    except json.JSONDecodeError:
                        error_message = "响应中未找到有效的JSON数据"
            except json.JSONDecodeError as e:
                error_message = f"解析JSON失败: {str(e)}"
            except Exception as e:
                error_message = f"处理响应时发生错误: {str(e)}"
        else:
            error_message = "未收到agent的有效响应"

        # 确保events_json始终是列表
        events_json = events_json if isinstance(events_json, list) else []

        # 如果解析失败，打印错误信息并抛出异常
        if not events_json:
            print(f"解析事件数据失败: {error_message}")
            # 尝试从result.content中提取可能的JSON（更加宽松的方式）
            if result and hasattr(result, 'content') and result.content:
                try:
                    # 移除所有非JSON字符
                    json_str = re.search(r'\{.*\}|\[.*\]', result.content, re.DOTALL)
                    if json_str:
                        events_json = json.loads(json_str.group())
                        if not isinstance(events_json, list):
                            events_json = [events_json]
                except Exception as e:
                    pass
            if not events_json:
                raise ValueError(f"无法从生成结果中解析出有效的事件数据: {error_message}")

        return events_json

    async def _process_and_add_events(self, profile_id: str, events_json: list, max_events: int) -> int:
        """处理并添加生成的事件

        Args:
            profile_id: 事件配置ID
            events_json: 事件JSON列表
            max_events: 最大事件数量

        Returns:
            int: 成功添加的事件数量
        """
        success_count = 0
        for event_json in events_json[:max_events]:  # 确保不超过最大事件数
            # 确保event_id存在
            if 'event_id' not in event_json:
                event_json['event_id'] = str(uuid.uuid4())

            # 转换时间格式
            if 'start_time' in event_json and isinstance(event_json['start_time'], str):
                try:
                    # 确保start_time是字符串类型
                    start_time_str = event_json['start_time']
                    if not isinstance(start_time_str, str):
                        start_time_str = str(start_time_str)
                    start_time_event = datetime.fromisoformat(start_time_str)
                except ValueError:
                    # 如果格式不正确，设置为当前时间
                    start_time_event = datetime.now()
            else:
                start_time_event = datetime.now()

            if 'end_time' in event_json and event_json['end_time']:
                if isinstance(event_json['end_time'], str):
                    try:
                        # 确保end_time是字符串类型
                        end_time_str = event_json['end_time']
                        if not isinstance(end_time_str, str):
                            end_time_str = str(end_time_str)
                        end_time_event = datetime.fromisoformat(end_time_str)
                    except ValueError:
                        end_time_event = start_time_event + timedelta(hours=1)
                else:
                    end_time_event = event_json['end_time']
            else:
                end_time_event = None

            # 创建Event对象
            event = Event(
                event_id=event_json['event_id'],
                type=event_json.get('type', ''),
                description=event_json.get('description', ''),
                start_time=start_time_event,
                status=event_json.get('status', 'completed'),
                is_key_event=event_json.get('is_key_event', False),
                impact=event_json.get('impact', ''),
                location=event_json.get('location', ''),
                participants=event_json.get('participants', []),
                outcome=event_json.get('outcome', ''),
                emotion_score=event_json.get('emotion_score', 0.0),
                end_time=end_time_event,
                dependencies=event_json.get('dependencies', [])
            )

            # 添加到事件配置
            if add_event_to_profile(profile_id, event):
                success_count += 1
                # 更新内存中的事件配置
                await self._update_event_profile(profile_id)

        return success_count

    async def _update_event_profile(self, profile_id: str) -> None:
        """更新内存中的事件配置

        Args:
            profile_id: 事件配置ID
        """
        profile = get_event_profile_by_id(profile_id)
        if profile:
            # 确保profile是字典类型
            if isinstance(profile, dict):
                # 从字典创建EventProfile对象
                event_profile = EventProfile(character_id=profile['character_id'])
                event_profile.id = profile_id
                # 验证event_profile类型
                if not isinstance(event_profile, EventProfile):
                    print(f"错误: 创建的event_profile不是EventProfile类型，而是{type(event_profile)}")
                    return
                # 确保life_path属性已初始化
                if not hasattr(event_profile, 'life_path'):
                    print("警告: event_profile缺少life_path属性，正在初始化...")
                    event_profile.life_path = []
                else:
                    event_profile.life_path = []  # 重置为避免重复添加
            else:
                print(f"警告: 预期profile为字典，但得到{type(profile)}")
                return
            # 验证event_profile类型和life_path属性
            if not isinstance(event_profile, EventProfile):
                print(f"错误: event_profile不是EventProfile类型，而是{type(event_profile)}")
                return
            if not hasattr(event_profile, 'life_path'):
                print("错误: event_profile缺少life_path属性")
                return
            if not isinstance(event_profile.life_path, list):
                print(f"错误: event_profile.life_path不是列表类型，而是{type(event_profile.life_path)}")
                event_profile.life_path = []
            for event_dict in profile.get('life_path', []):
                # 转换时间字段
                if 'start_time' in event_dict and isinstance(event_dict['start_time'], str):
                    try:
                        start_time = datetime.fromisoformat(event_dict['start_time'])
                    except ValueError:
                        start_time = datetime.now()
                else:
                    start_time = datetime.now()

                if 'end_time' in event_dict and event_dict['end_time']:
                    if isinstance(event_dict['end_time'], str):
                        try:
                            end_time = datetime.fromisoformat(event_dict['end_time'])
                        except ValueError:
                            end_time = start_time + timedelta(hours=1)
                    else:
                        end_time = event_dict['end_time']
                else:
                    end_time = None

                # 创建Event对象
                event = Event(
                    event_id=event_dict.get('event_id', str(uuid.uuid4())),
                    type=event_dict.get('type', ''),
                    description=event_dict.get('description', ''),
                    start_time=start_time,
                    status=event_dict.get('status', 'completed'),
                    is_key_event=event_dict.get('is_key_event', False),
                    impact=event_dict.get('impact', ''),
                    location=event_dict.get('location', ''),
                    participants=event_dict.get('participants', []),
                    outcome=event_dict.get('outcome', ''),
                    emotion_score=event_dict.get('emotion_score', 0.0),
                    end_time=end_time,
                    dependencies=event_dict.get('dependencies', [])
                )
                # 确保event_profile是EventProfile对象且有life_path属性
                if isinstance(event_profile, EventProfile) and hasattr(event_profile, 'life_path'):
                    event_profile.life_path.append(event)
                else:
                    pass

    def remove_event_from_life_path(self, profile_id: str, event_id: str) -> bool:
        """从事件配置的life_path移除事件

        从指定的事件配置中移除特定ID的事件

        Args:
            profile_id: 事件配置ID
            event_id: 事件ID

        Returns:
            bool: 是否移除成功
        """
        return remove_event_from_profile(profile_id, event_id)

# 创建管理器实例
manager = LifePathManager()

async def add_event_to_life_path(profile_id: str, start_time: str, end_time: str, max_events: int = 3) -> bool:
    """向life_path添加事件的便捷函数

    便捷函数，调用manager实例的add_event_to_life_path方法

    Args:
        profile_id: 事件配置ID
        start_time: 事件开始时间 (格式: YYYY-MM-DD)
        end_time: 事件结束时间 (格式: YYYY-MM-DD)
        max_events: 最大事件数量 (默认: 3)

    Returns:
        bool: 是否添加成功
    """
    return await manager.add_event_to_life_path(profile_id, start_time, end_time, max_events)

async def remove_event_from_life_path(profile_id: str, event_id: str) -> bool:
    """从life_path移除事件的便捷函数

    便捷函数，调用manager实例的remove_event_from_life_path方法

    Args:
        profile_id: 事件配置ID
        event_id: 事件ID

    Returns:
        bool: 是否移除成功
    """
    return manager.remove_event_from_life_path(profile_id, event_id)