import asyncio
import sys
import os
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from src.character.model.character import Character
from dotenv import load_dotenv
import json
from src.character.prompts import GENERATOR_SYSTEM_MESSAGE_TEMPLATE, REVIEWER_SYSTEM_MESSAGE
from src.character.utils import get_character_fields_description

load_dotenv()

class CharacterLLMGenerator:
    def __init__(self):
        # 初始化模型客户端
        # 初始化模型客户端，添加超时设置
        self.model_client = OpenAIChatCompletionClient(
            model="qwen-plus",
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("BASE_URL"),
            model_info={
                "vision": False,
                "function_calling": True,
                "json_output": False,
                "family": "unknown",
                "structured_output": True
            }
        )
        # 初始化两个agent
        self.generator_agent = self._create_generator_agent()
        self.reviewer_agent = self._create_reviewer_agent()
        # 创建团队
        self.team = RoundRobinGroupChat(
            [self.generator_agent, self.reviewer_agent],
            termination_condition=MaxMessageTermination(2)
        )

    def _create_generator_agent(self):
        """创建用于生成角色字段的agent"""
        # 获取字段描述
        fields_description = get_character_fields_description()
        # 生成系统消息
        system_message = GENERATOR_SYSTEM_MESSAGE_TEMPLATE.format(fields_description=fields_description)

        return AssistantAgent(
            "CharacterGenerator",
            model_client=self.model_client,
            system_message=system_message
        )

    def _create_reviewer_agent(self):
        """创建用于审查角色自洽性的agent"""
        return AssistantAgent(
            "CharacterReviewer",
            model_client=self.model_client,
            system_message=REVIEWER_SYSTEM_MESSAGE
        )

    async def generate_character(self, name: str = None, age: int = None, gender: str = None, occupation: str = None, language: str = "Chinese") -> Character:
        """生成角色并审查其自洽性"""
        # 准备初始提示
        initial_task = "生成一个详细的AI角色。"
        # 添加语言控制指令
        if language == "English":
            initial_task += " 请确保所有字段内容都使用英文输出。"
        else:
            initial_task += " 请确保所有字段内容都使用中文输出。"

        if name:
            initial_task += f" 角色姓名为{name}。"
        if age:
            initial_task += f" 年龄为{age}岁。"
        if gender:
            initial_task += f" 性别为{gender}。"
        if occupation:
            initial_task += f" 职业为{occupation}。"

        # 运行团队生成人格
        result = await self.team.run(task=initial_task)

        # 解析结果中的JSON
        character_data = None
        # 检查所有消息以寻找JSON
        for message in result.messages:
            if message.content and isinstance(message.content, str) and '{' in message.content:
                try:
                    # 提取JSON部分
                    start_idx = message.content.find('{')
                    end_idx = message.content.rfind('}') + 1
                    json_str = message.content[start_idx:end_idx]
                    character_data = json.loads(json_str)
                    break  # 找到有效JSON后跳出循环
                except json.JSONDecodeError:
                    pass

        if not character_data:
            raise ValueError("未能从生成结果中提取有效的角色数据")

        # 创建Character对象
        return Character(**character_data)