import sys
import os
import asyncio
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from src.character.event.llm_event_gen import EventProfileLLMGenerator
from src.character.db.event_profile_dao import (
    save_event_profile,
    get_event_profiles_by_character_id,
    get_event_profile_by_id,
    delete_event_profile
)
from src.character.db.character_dao import get_character_by_id

async def main():
    generator = EventProfileLLMGenerator()
    try:
        # 获取用户输入的角色ID
        character_id = input("请输入要生成事件配置的角色ID: ")
        
        # 验证角色是否存在
        character = get_character_by_id(character_id)
        if not character:
            print(f"未找到角色ID为{character_id}的角色")
            return
        
        print(f"为角色 {character.name} 生成事件配置...")
        # 生成事件配置
        event_profile = await generator.generate_event_profile(character_id=character_id, language="Chinese")

        print(f"生成的事件配置ID: {event_profile.id}")
        print(f"当前生活阶段: {event_profile.current_stage}")
        print(f"未来趋势: {event_profile.next_trend}")
        print(f"事件触发条件: {event_profile.event_triggers}")
        print(f"人生路径事件数量: {len(event_profile.life_path)}")
        
        # 打印完整的人生路径事件信息
        print("\n人生路径事件详情:")
        for i, event in enumerate(event_profile.life_path, 1):
            print(f"\n事件 {i}: {event.type}")
            print(f"描述: {event.description}")
            print(f"开始时间: {event.start_time}")
            print(f"状态: {event.status}")
            print(f"是否关键事件: {'是' if event.is_key_event else '否'}")
            print(f"影响: {event.impact}")
            print(f"地点: {event.location}")
            print(f"参与者: {', '.join(event.participants)}")
            print(f"结果: {event.outcome}")
            print(f"情绪评分: {event.emotion_score}")
            if event.end_time:
                print(f"结束时间: {event.end_time}")
        
        # 询问是否保存事件配置
        save_choice = input("是否保存此事件配置到MongoDB? (y/n): ")
        if save_choice.lower() == 'y':
            save_event_profile(event_profile)
            print("事件配置已保存到MongoDB!")
        else:
            print("事件配置未保存。")
    except Exception as e:
        print(f"生成事件配置时出错: {e}")

if __name__ == "__main__":
    asyncio.run(main())