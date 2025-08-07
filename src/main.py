import os
from character import CharacterGenerator


def display_character_info(character):
    """显示角色信息"""
    print(f"\n=== 角色信息: {character.name} ===")
    print(f"ID: {character.character_id}")
    print(f"年龄: {character.age}")
    print(f"性别: {character.gender}")
    print(f"职业: {character.occupation}")
    print(f"背景: {character.background}")
    print(f"性格: {', '.join(character.personality)}")
    print(f"爱好: {', '.join(character.hobbies)}")

    # 对话相关特性
    print(f"语气风格: {character.speech_style}")
    print(f"语调: {character.tone}")
    print(f"回应速度: {character.response_speed}")
    print(f"沟通风格: {character.communication_style}")

    # 话题偏好与禁忌
    print(f"偏好话题: {', '.join(character.favored_topics)}")
    print(f"不喜欢话题: {', '.join(character.disliked_topics) if character.disliked_topics else '无'}")
    print(f"禁忌话题: {', '.join(character.taboos)}")

    # 深层人格特质
    print(f"信仰: {', '.join(character.beliefs)}")
    print(f"目标: {', '.join(character.goals)}")
    print(f"恐惧: {', '.join(character.fears)}")
    print(f"秘密: {', '.join(character.secrets)}")
    print(f"习惯: {', '.join(character.habits)}")

    # 人格模型
    print(f"MBTI类型: {character.mbti_type}")
    print("大五人格特质:")
    print(f"  开放性: {character.big5['开放性']}")
    print(f"  尽责性: {character.big5['尽责性']}")
    print(f"  外倾性: {character.big5['外倾性']}")
    print(f"  宜人性: {character.big5['宜人性']}")
    print(f"  神经质: {character.big5['神经质']}")
    print(f"核心动机: {character.motivation}")
    print(f"主要冲突: {character.conflict}")
    print(f"主要缺陷: {character.flaw}")
    print(f"成长弧光: {character.character_arc}")

    # 情绪相关
    print(f"当前心情: {character.mood}")
    print(f"情绪波动: {character.mood_swings}")

    # 记忆与经历
    print("记忆与经历:")
    if 'childhood' in character.memory:
        print(f"  童年: {', '.join(character.memory['childhood'])}")
    if 'teenage' in character.memory:
        print(f"  青少年: {', '.join(character.memory['teenage'])}")
    if 'work' in character.memory:
        print(f"  工作: {', '.join(character.memory['work'])}")
    if 'recent' in character.memory:
        print(f"  最近: {', '.join(character.memory['recent'])}")

    # 日常安排
    print("日常安排:")
    for item in character.daily_routine:
        print(f"  {item['time']}: {item['activity']} (地点: {item['location']})")
    print("=======================")


def main():
    print("欢迎使用 Soluna AI人格生成器!")
    
    # 创建角色生成器实例
    preset_dir = os.path.join(os.path.dirname(__file__), 'character', 'preset_characters')
    generator = CharacterGenerator(preset_dir)
    
    while True:
        print("\n请选择操作:")
        print("1. 生成随机角色")
        print("2. 查看预设角色")
        print("3. 退出")
        
        choice = input("请输入选项编号: ")
        
        if choice == '1':
            # 生成随机角色
            random_char = generator.generate_random_character()
            display_character_info(random_char)
            
            # 询问是否保存
            save_choice = input("是否保存此角色? (y/n): ")
            if save_choice.lower() == 'y':
                save_dir = os.path.join(os.path.dirname(__file__), 'character', 'user_characters')
                if generator.save_character(random_char, save_dir):
                    print(f"角色已保存到: {save_dir}/{random_char.character_id}.json")
                else:
                    print("保存失败!")
        
        elif choice == '2':
            # 查看预设角色
            preset_chars = generator.preset_characters
            if not preset_chars:
                print("没有找到预设角色!")
                continue
            
            print("可用的预设角色:")
            for i, char_id in enumerate(preset_chars.keys()):
                print(f"{i+1}. {preset_chars[char_id].name} (ID: {char_id})")
            
            char_choice = input("请选择角色编号 (输入0随机选择): ")
            try:
                char_choice = int(char_choice)
                if char_choice == 0:
                    # 随机选择
                    random_preset = generator.get_random_preset_character()
                    display_character_info(random_preset)
                elif 1 <= char_choice <= len(preset_chars):
                    # 按编号选择
                    char_id = list(preset_chars.keys())[char_choice - 1]
                    display_character_info(preset_chars[char_id])
                else:
                    print("无效的选择!")
            except ValueError:
                print("请输入有效的数字!")
        
        elif choice == '3':
            print("谢谢使用，再见!")
            break
        
        else:
            print("无效的选项，请重新输入!")


if __name__ == "__main__":
    main()