import os
import json
import random
import uuid
from typing import List, Dict, Optional, Any
from character import Character

from .data import (
    mbti_types, mbti_personality_map, big5_traits, motivations, conflicts,
    flaws, character_arcs, first_names, last_names, occupations, hobbies,
    speech_styles, tones, response_speeds, communication_styles, topics,
    taboos, beliefs, goals, fears, habits, moods, mood_swings
)
from .utils import generate_background, generate_memory, generate_daily_routine


class CharacterGenerator:
    """AI角色生成器类"""
    def __init__(self, preset_chars_dir: str = None):
        self.preset_chars_dir = preset_chars_dir
        # 在定义完所有属性后再加载预设角色
        self.preset_characters = self._load_preset_characters()

    def _load_preset_characters(self) -> Dict[str, Character]:
        """加载预设角色"""
        preset_chars = {}
        if self.preset_chars_dir and os.path.exists(self.preset_chars_dir):
            for filename in os.listdir(self.preset_chars_dir):
                if filename.endswith('.json'):
                    with open(os.path.join(self.preset_chars_dir, filename), 'r', encoding='utf-8') as f:
                        char_data = json.load(f)
                        # 为新字段提供默认值
                        speech_style = char_data.get('speech_style', random.choice(speech_styles))
                        tone = char_data.get('tone', random.choice(tones))
                        response_speed = char_data.get('response_speed', random.choice(response_speeds))
                        communication_style = char_data.get('communication_style', random.choice(communication_styles))
                        favored_topics = char_data.get('favored_topics', random.sample(topics, random.randint(3, 5)))
                        disliked_topics = char_data.get('disliked_topics', [])
                        taboos_selected = char_data.get('taboos', random.sample(taboos, random.randint(1, 3)))
                        beliefs_selected = char_data.get('beliefs', random.sample(beliefs, random.randint(2, 4)))
                        goals_selected = char_data.get('goals', random.sample(goals, random.randint(2, 4)))
                        fears_selected = char_data.get('fears', random.sample(fears, random.randint(1, 3)))
                        secrets = char_data.get('secrets', [f"隐藏了自己曾经{random.choice(['失败的经历', '尴尬的事情', '过去的感情', '家庭背景'])}"])
                        habits_selected = char_data.get('habits', random.sample(habits, random.randint(2, 4)))
                        mood = char_data.get('mood', random.choice(moods))
                        mood_swings_selected = char_data.get('mood_swings', random.choice(mood_swings))
                        memory = char_data.get('memory', {})

                        # 生成或使用预设的MBTI类型
                        mbti_type = char_data.get('mbti_type', random.choice(mbti_types))

                        # 根据MBTI类型生成对应的性格特征
                        personality = random.sample(mbti_personality_map[mbti_type], random.randint(3, 5))

                        character = Character(
                            name=char_data['name'],
                            age=char_data['age'],
                            gender=char_data['gender'],
                            occupation=char_data['occupation'],
                            background=char_data['background'],
                            personality=personality,
                            hobbies=char_data['hobbies'],
                            relationships=char_data['relationships'],
                            daily_routine=char_data['daily_routine'],
                            character_id=char_data.get('character_id', str(uuid.uuid4())),
                            is_preset=True,
                            speech_style=speech_style,
                            tone=tone,
                            response_speed=response_speed,
                            communication_style=communication_style,
                            favored_topics=favored_topics,
                            disliked_topics=disliked_topics,
                            taboos=taboos_selected,
                            beliefs=beliefs_selected,
                            goals=goals_selected,
                            fears=fears_selected,
                            secrets=secrets,
                            habits=habits_selected,
                            mood=mood,
                            mood_swings=mood_swings_selected,
                            memory=memory,
                            mbti_type=mbti_type,
                            big5={trait: round(random.uniform(0.1, 0.9), 2) for trait in big5_traits},
                            motivation=random.choice(motivations),
                            conflict=random.choice(conflicts),
                            flaw=random.choice(flaws),
                            character_arc=random.choice(character_arcs)
                            )
                        preset_chars[character.character_id] = character
        return preset_chars

    def generate_random_character(self) -> Character:
        """生成随机角色"""
        # 随机选择性别
        gender = random.choice(['male', 'female', 'neutral'])
        # 随机选择姓名
        if gender == 'neutral':
            name = random.choice(first_names['neutral'])
        else:
            name = f"{random.choice(last_names)}{random.choice(first_names[gender])}"

        # 生成MBTI类型
        mbti_type = random.choice(mbti_types)

        # 生成Big 5人格特质得分
        big5 = {
            trait: round(random.uniform(0.1, 0.9), 2) 
            for trait in big5_traits
        }

        # 生成其他新增字段
        motivation = random.choice(motivations)
        conflict = random.choice(conflicts)
        flaw = random.choice(flaws)
        character_arc = random.choice(character_arcs)
        # 随机选择年龄（18-65岁）
        age = random.randint(18, 65)
        # 随机选择职业
        occupation = random.choice(occupations)
        # 生成背景故事
        background = generate_background(age, occupation)

        # 生成记忆
        memory = generate_memory(age, occupation)
        # 根据MBTI类型生成对应的性格特征
        personality = random.sample(mbti_personality_map[mbti_type], random.randint(3, 5))
        # 随机选择爱好（2-4个）
        hobbies_selected = random.sample(hobbies, random.randint(2, 4))
        # 初始化关系
        relationships = {}
        # 生成日常安排
        daily_routine = generate_daily_routine(occupation)

        # 对话相关特性
        speech_style = random.choice(speech_styles)
        tone = random.choice(tones)
        response_speed = random.choice(response_speeds)
        communication_style = random.choice(communication_styles)

        # 话题偏好与禁忌
        # 随机选择喜欢的话题（3-5个）
        favored_topics = random.sample(topics, random.randint(3, 5))
        # 从剩下的话题中选择不喜欢的话题（2-3个）
        remaining_topics = [topic for topic in topics if topic not in favored_topics]
        disliked_topics = random.sample(remaining_topics, random.randint(2, 3)) if remaining_topics else []
        # 随机选择禁忌话题（1-3个）
        taboos_selected = random.sample(taboos, random.randint(1, 3))

        # 深层人格特质
        beliefs_selected = random.sample(beliefs, random.randint(2, 4))
        goals_selected = random.sample(goals, random.randint(2, 4))
        fears_selected = random.sample(fears, random.randint(1, 3))
        # 生成简单的秘密
        secrets = [f"隐藏了自己曾经{random.choice(['失败的经历', '尴尬的事情', '过去的感情', '家庭背景'])}"]
        habits_selected = random.sample(habits, random.randint(2, 4))

        # 情绪相关
        current_mood = random.choice(moods)
        mood_swings_selected = random.choice(mood_swings)

        return Character(
            name=name,
            age=age,
            gender=gender,
            occupation=occupation,
            background=background,
            personality=personality,
            hobbies=hobbies_selected,
            relationships=relationships,
            daily_routine=daily_routine,
            speech_style=speech_style,
            tone=tone,
            response_speed=response_speed,
            communication_style=communication_style,
            favored_topics=favored_topics,
            disliked_topics=disliked_topics,
            taboos=taboos_selected,
            beliefs=beliefs_selected,
            goals=goals_selected,
            fears=fears_selected,
            secrets=secrets,
            habits=habits_selected,
            mood=current_mood,
            mood_swings=mood_swings_selected,
            memory=memory,
            mbti_type=mbti_type,
            big5=big5,
            motivation=motivation,
            conflict=conflict,
            flaw=flaw,
            character_arc=character_arc
        )

    def get_preset_character(self, character_id: str) -> Optional[Character]:
        """获取预设角色"""
        return self.preset_characters.get(character_id)

    def get_random_preset_character(self) -> Optional[Character]:
        """随机获取一个预设角色"""
        if self.preset_characters:
            return random.choice(list(self.preset_characters.values()))
        return None

    def save_character(self, character: Character, save_dir: str) -> bool:
        """保存角色到文件"""
        try:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            file_path = os.path.join(save_dir, f"{character.character_id}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(character.to_json())
            return True
        except Exception as e:
            print(f"保存角色失败: {e}")
            return False