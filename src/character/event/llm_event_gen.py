# llm_event_gen.py文件，作为整合和导出的入口

# 导入必要的模块
from .event_profile_generator import (
    EventProfileLLMGenerator
)
from .life_path_manager import (
    LifePathManager,
    add_event_to_life_path,
    remove_event_from_life_path
)
from .prompts import (
    GENERATOR_SYSTEM_MESSAGE_TEMPLATE,
    REVIEWER_SYSTEM_MESSAGE,
    DAILY_EVENT_GENERATOR_SYSTEM_MESSAGE_TEMPLATE,
    LIFE_PATH_REVIEWER_SYSTEM_MESSAGE
)

# 保持向后兼容性的导出
# 创建生成器和管理器实例
profile_generator = EventProfileLLMGenerator()
lifepath_manager = LifePathManager()

# 导出便捷函数
async def create_event_profile(character_id: str, language: str = "Chinese"):
    return await profile_generator.create_event_profile(character_id, language)

async def update_event_profile(profile_id: str, updates: dict):
    return await profile_generator.update_event_profile(profile_id, updates)

def get_event_profiles(character_id: str):
    return profile_generator.get_event_profiles(character_id)

def get_event_profile(profile_id: str):
    return profile_generator.get_event_profile(profile_id)

def delete_event_profile(profile_id: str):
    return profile_generator.delete_event_profile(profile_id)

async def generate_event_profile(character_id: str, language: str = "Chinese"):
    return await profile_generator.generate_event_profile(character_id, language)

# 提供一个版本信息，方便追踪
VERSION = "1.0.0"