import sys
import os
import json
import uuid
from datetime import datetime, timedelta
from bson import ObjectId
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from src.character.model.event_profile import EventProfile, Event
from src.character.db.character_dao import get_character_by_id
from src.character.db.event_profile_dao import (
    save_event_profile,
    get_event_profiles_by_character_id,
    get_event_profile_by_id,
    delete_event_profile,
    add_event_to_profile,
    remove_event_from_profile
)
from dotenv import load_dotenv

# 转换MongoDB ObjectId和datetime为可JSON序列化的类型
def convert_object_id(obj):
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

# 事件配置生成提示词模板 (用于初始化eventProfile)
GENERATOR_SYSTEM_MESSAGE_TEMPLATE = """
你是一个事件配置生成专家，负责为AI角色生成详细的事件配置(EventProfile)。
请根据以下角色信息和EventProfile类的字段结构，生成合理的事件配置：

角色信息:
{character_info}

生成时请注意：
- 确保每个字段的内容符合角色设定和逻辑
- life_path中的事件需要前后连贯，时间顺序合理，避免出现矛盾的时间和地点
- 事件类型(type)应多样化，包括但不限于工作、学习、社交、健康、娱乐等
- 每个事件的location、participants、outcome等字段应与事件类型和角色背景相符
- 事件的emotion_score应根据事件的性质和对角色的影响合理设置(-1.0到1.0之间)
- 当前生活阶段(current_stage)应与角色年龄和背景相符
- 未来趋势(next_trend)应基于角色当前状态和背景进行合理预测
- 事件触发条件(event_triggers)应具体、可操作。返回格式为{{"关键事件1": "触发条件1的具体描述", "关键事件2": "触发条件2的具体描述"}}
- 生成的内容要有细节，使其更加真实
- 确保life_path中的事件按时间顺序排列
- 特别注意：请根据角色的年龄，生成从角色出生到现在的合理事件时间线，事件的start_time应分散在角色的不同生命阶段，避免所有事件都集中在同一时间
- 为每个事件生成**极其合理**的开始时间和结束时间（如果适用），要根据事件内容、角色年龄和背景进行精确设定
  - 考虑角色的当前年龄，确保事件时间线从角色出生到现在是连贯的
  - 关键事件应发生在角色人生的重要阶段
  - 日常事件应分散在不同时间段
- 对于人生关键节点、里程碑、转折点或重要记忆等事件，请将is_key_event设置为true，其他日常事件设置为false

请以JSON格式输出完整的EventProfile对象。特别注意，每个事件必须有明确且合理的start_time！
"""

# 事件配置审查提示词
REVIEWER_SYSTEM_MESSAGE = """
你是一个事件配置审查专家，负责检查生成的EventProfile是否自洽合理。
请仔细审查以下各个字段之间的关系以及与角色信息的匹配性：

角色信息:
{character_info}

审查条件：
- 与角色的匹配性：事件配置应与角色的年龄、职业、背景、性格等相符
- life_path的连贯性：事件之间应具有时间和逻辑上的连贯性，避免出现矛盾
- 事件细节的合理性：每个事件的location、participants、outcome等字段应合理
- 情绪影响的合理性：emotion_score应与事件的性质和影响相符
- 当前阶段和未来趋势的合理性：current_stage和next_trend应基于角色背景和事件发展合理设置
- 事件触发条件的合理性：event_triggers应具体、可操作且与角色相关
- 所有字段不要涉及任何政治因素
- 确保每个字段都有内容，不能为空。如果明确说明过的不用生成哪些字段除外。
- 如果某个字段需要特定的输出格式，要符合要求
- 开始时间和结束时间要真实，要与角色的年龄，背景相符，通过年龄可以反推出生时间，可以完成life_path初始化的时间判断。

请指出任何不一致或不合理的地方，并提供修改建议。如果没有问题，请确认事件配置自洽。
"""

# 日常事件生成提示词模板 (用于add_event_to_life_path)
DAILY_EVENT_GENERATOR_SYSTEM_MESSAGE_TEMPLATE = """
你是一位角色日常事件生成专家。你的任务是为虚构角色创建真实、合理的日常事件。

角色信息如下:
{character_info}

现有事件配置:
{existing_profile}

请根据以上信息，在指定时间段内生成合理的日常事件:
- 时间范围: {start_time} 至 {end_time}
- 最多生成 {max_events} 个事件
- 事件类型应以日常活动为主，如工作、学习、社交、健康、娱乐等
- 对于特别重要的日常事件，可以将is_key_event设置为true
- 为每个事件生成合理的开始时间和结束时间（格式: YYYY-MM-DD HH:MM:SS），确保时间线连贯
- 事件应符合角色的性格、背景和已有经历
- 确保事件之间有合理的间隔和多样性

请严格按照以下JSON格式输出生成的事件列表，确保格式正确，不包含任何解释性文字、注释或多余空格。你的回答必须只包含JSON数据，不能有任何前缀或后缀：
[
  {{
    "id": "事件唯一ID",
    "title": "事件标题",
    "description": "事件详细描述",
    "start_time": "开始时间 (YYYY-MM-DD HH:MM:SS)",
    "end_time": "结束时间 (YYYY-MM-DD HH:MM:SS)",
    "event_type": "事件类型",
    "location": "事件地点 (可选)",
    "participants": ["参与者1", "参与者2" (可选)],
    "is_key_event": false,
    "emotional_impact": "情绪影响 (可选)",
    "outcome": "事件结果 (可选)"
  }}
]
"""

class EventProfileLLMGenerator:
    def __init__(self):
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
        """创建用于生成事件配置字段的agent"""
        # 生成系统消息
        system_message = GENERATOR_SYSTEM_MESSAGE_TEMPLATE.format(character_info=character_info)

        return AssistantAgent(
            "EventProfileGenerator",
            model_client=self.model_client,
            system_message=system_message
        )

    def _create_reviewer_agent(self, character_info):
        """创建用于审查事件配置自洽性的agent"""
        system_message = REVIEWER_SYSTEM_MESSAGE.format(character_info=character_info)

        return AssistantAgent(
            "EventProfileReviewer",
            model_client=self.model_client,
            system_message=system_message
        )

    async def generate_event_profile(self, character_id: str, language: str = "Chinese") -> EventProfile:
        """生成事件配置并审查其自洽性

        Args:
            character_id: 角色ID
            language: 生成语言

        Returns:
            EventProfile: 生成的事件配置对象
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
        # 检查所有消息以寻找JSON
        for message in result.messages:
            if message.content and isinstance(message.content, str) and '{' in message.content:
                try:
                    # 提取JSON部分
                    start_idx = message.content.find('{')
                    end_idx = message.content.rfind('}') + 1
                    json_str = message.content[start_idx:end_idx]
                    event_profile_data = json.loads(json_str)
                    break  # 找到有效JSON后跳出循环
                except json.JSONDecodeError:
                    pass

        if not event_profile_data:
            raise ValueError("无法从生成结果中解析出有效的EventProfile JSON")

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

        Args:
            character_id: 角色ID
            language: 生成语言

        Returns:
            str: 事件配置ID
        """
        # 检查是否已存在事件配置
        existing_profiles = get_event_profiles_by_character_id(character_id)
        if existing_profiles and len(existing_profiles) > 0:
            print(f"角色{character_id}已存在事件配置，返回第一个配置ID")
            return existing_profiles[0]['id']

        # 生成新的事件配置
        event_profile = await self.generate_event_profile(character_id, language)

        # 保存到数据库
        return save_event_profile(event_profile)

    async def update_event_profile(self, profile_id: str, updates: dict) -> str:
        """更新事件配置

        Args:
            profile_id: 事件配置ID
            updates: 要更新的字段和值

        Returns:
            str: 更新后的事件配置ID
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

    def _create_daily_event_generator_agent(self, character_info, existing_profile, start_time, end_time, max_events):
        """创建用于生成日常事件的agent

        Args:
            character_info: 角色信息
            existing_profile: 现有事件配置
            start_time: 事件开始时间
            end_time: 事件结束时间
            max_events: 最大事件数量

        Returns:
            AssistantAgent: 日常事件生成agent
        """
        # 生成系统消息
        system_message = DAILY_EVENT_GENERATOR_SYSTEM_MESSAGE_TEMPLATE.format(
            character_info=character_info,
            existing_profile=existing_profile,
            start_time=start_time,
            end_time=end_time,
            max_events=max_events
        )

        return AssistantAgent(
            "DailyEventGenerator",
            model_client=self.model_client,
            system_message=system_message
        )

    async def add_event_to_life_path(self, profile_id: str, start_time: str, end_time: str, max_events: int = 3) -> bool:
        """向事件配置的life_path添加事件

        Args:
            profile_id: 事件配置ID
            start_time: 事件开始时间 (格式: YYYY-MM-DD)
            end_time: 事件结束时间 (格式: YYYY-MM-DD)
            max_events: 最大事件数量 (默认: 3)

        Returns:
            bool: 是否添加成功
        """
        # 获取事件配置
        profile = get_event_profile_by_id(profile_id)
        if not profile:
            raise ValueError(f"未找到事件配置ID为{profile_id}的配置")

        # 获取关联的角色信息
        character = get_character_by_id(profile['character_id'])
        if not character:
            raise ValueError(f"未找到角色ID为{profile['character_id']}的角色")

        # 准备角色信息字符串
        character_info = json.dumps(character.to_dict(), ensure_ascii=False)

        # 使用模块级函数转换ObjectId
        profile_dict = convert_object_id(profile)
        existing_profile = json.dumps(profile_dict, ensure_ascii=False)

        # 初始化日常事件生成agent
        self.daily_event_agent = self._create_daily_event_generator_agent(
            character_info, existing_profile, start_time, end_time, max_events
        )

        # 准备提示，添加具体时间信息
        task = f"请在{start_time} 00:00:00至{end_time} 23:59:59期间为角色生成最多{max_events}个合理的日常事件。"

        # 运行agent生成事件
        # 使用create_team和run方法，这是autogen-agentchat 0.7.2的正确用法
        team = RoundRobinGroupChat(
            [self.daily_event_agent],
            termination_condition=MaxMessageTermination(1)
        )
        result = await team.run(task=task)
        # 获取agent的回复
        result = result.messages[-1] if result and result.messages else None

        # 解析结果中的事件数据列表
        events_json = None
        error_message = None

        # 记录原始响应以便调试
        print(f"Agent response: {result.content if result and result.content else 'Empty'}")

        if result and result.content:
            if '[' in result.content and ']' in result.content:
                try:
                    start_idx = result.content.find('[')
                    end_idx = result.content.rfind(']') + 1
                    json_str = result.content[start_idx:end_idx]
                    events_json = json.loads(json_str)
                    # 验证是否为列表
                    if not isinstance(events_json, list):
                        error_message = "解析结果不是有效的列表"
                        events_json = None
                except json.JSONDecodeError as e:
                    error_message = f"解析JSON数组失败: {str(e)}"
            elif '{' in result.content and '}' in result.content:
                try:
                    start_idx = result.content.find('{')
                    end_idx = result.content.rfind('}') + 1
                    json_str = result.content[start_idx:end_idx]
                    single_event = json.loads(json_str)
                    events_json = [single_event]
                except json.JSONDecodeError as e:
                    error_message = f"解析单个事件失败: {str(e)}"
            else:
                error_message = "响应中未找到有效的JSON数据"
        else:
            error_message = "未收到agent的有效响应"

        # 确保events_json始终是列表
        events_json = events_json if isinstance(events_json, list) else []

        # 如果解析失败，打印错误信息并抛出异常
        if not events_json:
            print(f"解析事件数据失败: {error_message}")
            raise ValueError(f"无法从生成结果中解析出有效的事件数据: {error_message}")

        # 处理每个事件并添加到life_path
        success_count = 0
        for event_json in events_json[:max_events]:  # 确保不超过最大事件数
            # 确保event_id存在
            if 'event_id' not in event_json:
                event_json['event_id'] = str(uuid.uuid4())

            # 转换时间格式
            if 'start_time' in event_json and isinstance(event_json['start_time'], str):
                try:
                    start_time_event = datetime.fromisoformat(event_json['start_time'])
                except ValueError:
                    # 如果格式不正确，设置为当前时间
                    start_time_event = datetime.now()
            else:
                start_time_event = datetime.now()

            if 'end_time' in event_json and event_json['end_time']:
                if isinstance(event_json['end_time'], str):
                    try:
                        end_time_event = datetime.fromisoformat(event_json['end_time'])
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

        return success_count > 0  # 如果至少添加成功一个事件，则返回True

    def remove_event_from_life_path(self, profile_id: str, event_id: str) -> bool:
        """从事件配置的life_path移除事件

        Args:
            profile_id: 事件配置ID
            event_id: 事件ID

        Returns:
            bool: 是否移除成功
        """
        return remove_event_from_profile(profile_id, event_id)

    def get_event_profiles(self, character_id: str) -> list:
        """根据角色ID获取事件配置列表

        Args:
            character_id: 角色ID

        Returns:
            list: 事件配置列表
        """
        return get_event_profiles_by_character_id(character_id)

    def get_event_profile(self, profile_id: str) -> dict:
        """根据ID获取事件配置

        Args:
            profile_id: 事件配置ID

        Returns:
            dict: 事件配置数据
        """
        return get_event_profile_by_id(profile_id)

    def delete_event_profile_by_id(self, profile_id: str) -> bool:
        """删除事件配置

        Args:
            profile_id: 事件配置ID

        Returns:
            bool: 是否删除成功
        """
        return delete_event_profile(profile_id)

# 创建生成器实例
generator = EventProfileLLMGenerator()

async def create_event_profile(character_id: str, language: str = "Chinese") -> str:
    """创建事件配置的便捷函数"""
    return await generator.create_event_profile(character_id, language)

async def update_event_profile(profile_id: str, updates: dict) -> str:
    """更新事件配置的便捷函数"""
    return await generator.update_event_profile(profile_id, updates)

async def add_event_to_life_path(profile_id: str, start_time: str, end_time: str, max_events: int = 3) -> bool:
    """向life_path添加事件的便捷函数

    Args:
        profile_id: 事件配置ID
        start_time: 事件开始时间 (格式: YYYY-MM-DD)
        end_time: 事件结束时间 (格式: YYYY-MM-DD)
        max_events: 最大事件数量 (默认: 3)

    Returns:
        bool: 是否添加成功
    """
    return await generator.add_event_to_life_path(profile_id, start_time, end_time, max_events)

async def remove_event_from_life_path(profile_id: str, event_id: str) -> bool:
    """从life_path移除事件的便捷函数"""
    return generator.remove_event_from_life_path(profile_id, event_id)

def get_event_profiles(character_id: str) -> list:
    """获取事件配置列表的便捷函数"""
    return generator.get_event_profiles(character_id)

def get_event_profile(profile_id: str) -> dict:
    """获取事件配置的便捷函数"""
    return generator.get_event_profile(profile_id)

def delete_event_profile(profile_id: str) -> bool:
    """删除事件配置的便捷函数"""
    return generator.delete_event_profile_by_id(profile_id)