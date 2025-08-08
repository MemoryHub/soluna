import random
import inspect
import random
from typing import List, Dict, Any
from .data import (
    daily_activities, occupations, topics, taboos, beliefs, goals, fears,
    hobbies, speech_styles, tones, response_speeds, communication_styles
)
from .model.character import Character


def generate_background(age: int, occupation: str) -> str:
    """生成角色背景故事"""
    # 根据年龄和职业生成简单的背景故事
    backgrounds = [
        f"{age}岁的{occupation}，毕业于{random.choice(['北京大学', '清华大学', '复旦大学', '上海交通大学', '浙江大学'])}"
        f"{random.choice(['计算机科学', '医学', '教育学', '设计', '文学', '音乐', '艺术', '烹饪', '新闻', '法律'])}专业。\n"
        f"毕业后一直在{random.choice(['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '西安'])}工作，现在是{occupation}。\n"
        f"{random.choice(['喜欢挑战', '热爱生活', '工作认真', '乐于助人', '积极向上'])}。",
        f"{age}岁的{occupation}，来自{random.choice(['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '西安', '农村'])}。\n"
        f"{random.choice(['从小就对这个职业感兴趣', '偶然机会进入这个行业', '家人推荐选择这个职业'])}，现在已经工作{random.randint(1, age-18)}年了。\n"
        f"{random.choice(['工作经验丰富', '充满热情', '不断学习进步', '希望做出一番成就'])}。",
        f"{age}岁的{occupation}，曾经做过{random.choice(['销售', '服务员', '教师', '程序员', '设计师', '医生', '律师', '记者'])}\n"
        f"后来{random.choice(['转行', '回到家乡', '创业失败', '继续深造'])}，现在成为了一名{occupation}。\n"
        f"{random.choice(['这段经历让我更加珍惜现在的工作', '希望在这个领域深耕细作', '期待未来有更多挑战'])}。"
    ]
    return random.choice(backgrounds)


def generate_memory(age: int, occupation: str) -> Dict:
    """生成角色记忆与经历"""
    memory = {}
    # 童年记忆 (5-12岁)
    if age >= 12:
        childhood_events = [
            f"{random.randint(5, 12)}岁时，第一次{random.choice(['骑自行车', '游泳', '获奖', '交朋友', '离开家去夏令营'])}",
            f"童年时最喜欢的{random.choice(['玩具', '游戏', '动画片', '书籍', '地方'])}是{random.choice(['变形金刚', '捉迷藏', '哆啦A梦', '安徒生童话', '外婆家'])}",
            f"小学时{random.choice(['成绩很好', '很调皮', '有很多朋友', '经常被老师表扬', '参加过很多活动'])}"
        ]
        memory['childhood'] = random.sample(childhood_events, random.randint(1, 2))

    # 青少年记忆 (13-18岁)
    if age >= 18:
        teen_events = [
            f"{random.randint(13, 18)}岁时，{random.choice(['考上理想的高中', '第一次谈恋爱', '参加重要比赛', '失去亲人', '遇到人生导师'])}",
            f"高中时{random.choice(['加入社团', '担任班干部', '学习压力很大', '开始打工', '明确了职业方向'])}",
            f"青少年时期最难忘的事情是{random.choice(['毕业旅行', '朋友聚会', '第一次独立生活', '参加演唱会', '遇到挫折'])}"
        ]
        memory['teenage'] = random.sample(teen_events, random.randint(1, 2))

    # 工作记忆
    work_years = random.randint(1, max(1, age-18))
    if work_years > 0:
        work_events = [
            f"{random.randint(1, work_years)}年前，{random.choice(['加入现在的公司', '获得晋升', '完成重要项目', '遇到职业瓶颈', '换工作'])}",
            f"工作中最有成就感的事情是{random.choice(['成功完成项目', '帮助同事解决问题', '获得奖项', '得到领导认可', '培养新人'])}",
            f"工作中遇到的挑战：{random.choice(['项目失败', '团队冲突', '技术难题', '时间压力', '客户要求'])}"
        ]
        memory['work'] = random.sample(work_events, random.randint(1, 2))

    # 最近记忆
    recent_events = [
        f"最近{random.choice(['一周', '一个月', '三个月'])}，{random.choice(['看了一场好电影', '读了一本好书', '认识了新朋友', '去了新地方', '尝试了新爱好'])}",
        f"最近在{random.choice(['学习新技能', '健身', '烹饪', '旅行', '社交'])}\方面投入了很多精力",
        f"最近的烦恼是{random.choice(['工作压力大', '人际关系问题', '健康问题', '财务问题', '生活单调'])}"
    ]
    memory['recent'] = random.sample(recent_events, random.randint(1, 2))

    return memory


def generate_daily_routine(occupation: str) -> List[Dict[str, Any]]:
    """生成日常安排"""
    # 基础日常安排
    routine = daily_activities.copy()

    # 根据职业调整日常安排
    if '工程师' in occupation or '编程' in occupation:
        routine.append({'time': '21:00', 'activity': '学习新技术', 'location': '家里'})
    elif '医生' in occupation:
        routine.append({'time': '14:00', 'activity': '午休/学习医学文献', 'location': '医院'})
    elif '教师' in occupation:
        routine.append({'time': '16:00', 'activity': '备课', 'location': '学校'})
    elif '厨师' in occupation:
        routine.append({'time': '15:00', 'activity': '准备晚餐食材', 'location': '餐厅厨房'})

    # 随机添加周末活动（20%概率）
    if random.random() < 0.2:
        weekend_activity = random.choice([
            {'time': '10:00', 'activity': '逛公园', 'location': '城市公园'},
            {'time': '14:00', 'activity': '看电影', 'location': '电影院'},
            {'time': '09:00', 'activity': '爬山', 'location': '郊外山区'},
            {'time': '13:00', 'activity': '和朋友聚餐', 'location': '餐厅'}
        ])
        routine.append(weekend_activity)

    return routine


def get_character_fields_description():
    """从Character类动态获取字段信息并生成字段描述字符串"""
    # 获取Character类的所有参数
    character_fields = inspect.signature(Character.__init__).parameters
    # 排除系统字段
    system_fields = ['self', 'character_id', 'is_preset']
    valid_fields = [field for field in character_fields if field not in system_fields]

    # 构建字段描述字符串
    fields_description = ""
    for i, field in enumerate(valid_fields, 1):
        # 从Character类的文档字符串中提取字段描述
        doc = Character.__doc__
        field_doc = ""
        if doc:
            for line in doc.split('\n'):
                if f'{field}:' in line:
                    field_doc = line.split(f'{field}:')[1].strip()
                    break
        fields_description += f"{i}. {field}: {field_doc}\n"

    return fields_description