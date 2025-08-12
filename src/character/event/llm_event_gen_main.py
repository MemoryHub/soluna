import sys
import os
import sys
import asyncio
from datetime import datetime, timedelta
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from src.character.event.llm_event_gen import EventProfileLLMGenerator, LifePathManager
from src.character.db.event_profile_dao import (
    save_event_profile,
    get_event_profiles_by_character_id,
    get_event_profile_by_id,
    delete_event_profile
)
from src.character.db.character_dao import get_character_by_id
from src.character.utils import convert_object_id

async def initialize_event_profile(generator):
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
        event_profile = await generator.create_event_profile(character_id=character_id, language="Chinese")

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
    except ValueError as ve:
        if "已存在事件配置" in str(ve):
            print(f"错误: {ve}")
        else:
            print(f"生成事件配置时出错: {ve}")
    except Exception as e:
        print(f"生成事件配置时出现未知错误: {e}")

async def add_event_to_life_path(life_path_manager):
    try:
        # 获取用户输入的角色ID
        character_id = input("请输入角色ID: ")
        
        # 验证角色是否存在
        character = get_character_by_id(character_id)
        if not character:
            print(f"未找到角色ID为{character_id}的角色")
            return
        
        # 获取用户输入的事件配置ID
        event_profile_id = input("请输入事件配置ID: ")
        
        # 获取事件配置
        event_profile = get_event_profile_by_id(event_profile_id)
        if not event_profile:
            print(f"未找到事件配置ID为{event_profile_id}的事件配置")
            return
        
        # 获取用户输入的时间范围
        start_date_str = input("请输入开始日期 (格式: YYYY-MM-DD): ")
        end_date_str = input("请输入结束日期 (格式: YYYY-MM-DD): ")
        
        # 解析日期
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        
        # 确保结束日期不早于开始日期
        if end_date < start_date:
            print("结束日期不能早于开始日期")
            return
        
        # 获取用户输入的最大事件数
        max_events_str = input("请输入最大事件数: ")
        max_events = int(max_events_str)
        
        print(f"为角色 {character.name} 的事件配置 {event_profile_id} 添加日常事件...")
        print(f"时间范围: {start_date_str} 至 {end_date_str}")
        print(f"最大事件数: {max_events}")
        
        # 添加事件到生活轨迹
        success = await life_path_manager.add_event_to_life_path(
            profile_id=event_profile_id,
            start_time=start_date.strftime("%Y-%m-%d"),
            end_time=end_date.strftime("%Y-%m-%d"),
            max_events=max_events
        )
        
        # 重新获取最新的事件配置
        if success:
            event_profile = get_event_profile_by_id(event_profile_id)
            print("添加生活轨迹成功!")
        else:
            print("添加生活轨迹失败。")
    except ValueError as ve:
        print(f"输入格式错误: {ve}")
    except Exception as e:
        print(f"添加事件到人生路径时出错: {e}")

async def main():
    generator = EventProfileLLMGenerator()
    life_path_manager = LifePathManager()
    
    while True:
        print("\n===== 角色事件系统测试 =====")
        print("1. 初始化角色事件配置 (eventProfile)")
        print("2. 向人生路径 (life_path) 添加事件")
        print("3. 退出")
        
        choice = input("请选择操作 (1/2/3): ")
        
        if choice == '1':
            await initialize_event_profile(generator)
        elif choice == '2':
            await add_event_to_life_path(life_path_manager)
        elif choice == '3':
            print("感谢使用角色事件系统测试工具，再见！")
            break
        else:
            print("无效的选择，请重新输入。")

if __name__ == "__main__":
    asyncio.run(main())