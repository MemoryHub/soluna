"""
情感工具函数
提供情绪相关的辅助功能
"""

import colorsys
from typing import Dict, Tuple


def pad_to_rgb(pleasure: float, arousal: float, dominance: float) -> str:
    """
    将PAD三维值转换为RGB颜色
    
    Args:
        pleasure: 愉悦度 (-100 to 100)
        arousal: 激活度 (-100 to 100)
        dominance: 支配感 (-100 to 100)
        
    Returns:
        str: RGB颜色值 (#RRGGBB)
    """
    # 将PAD值标准化到0-1范围
    p_norm = (pleasure + 100) / 200
    a_norm = (arousal + 100) / 200
    d_norm = (dominance + 100) / 200
    
    # 使用HSV颜色空间
    # 色调：愉悦度决定（红色=痛苦，绿色=愉悦）
    hue = (120 + p_norm * 120) / 360  # 0-1范围，从红色到绿色
    
    # 饱和度：激活度决定
    saturation = a_norm
    
    # 亮度：支配感决定
    value = 0.3 + d_norm * 0.7  # 确保不会太暗
    
    # 转换为RGB
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    
    # 转换为十六进制
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def get_emotion_intensity(pleasure: float, arousal: float, 
                         dominance: float) -> Dict[str, float]:
    """
    计算情绪的强度分布
    
    Returns:
        Dict包含各个维度的强度
    """
    # 计算绝对强度（0-100）
    pleasure_intensity = abs(pleasure)
    arousal_intensity = abs(arousal)
    dominance_intensity = abs(dominance)
    
    # 计算综合强度
    overall_intensity = (pleasure_intensity + arousal_intensity + dominance_intensity) / 3
    
    return {
        "pleasure_intensity": pleasure_intensity,
        "arousal_intensity": arousal_intensity,
        "dominance_intensity": dominance_intensity,
        "overall_intensity": overall_intensity,
        "emotion_stability": 100 - overall_intensity  # 稳定性与强度成反比
    }


def normalize_emotion_value(value: float, min_val: float = -100, 
                          max_val: float = 100) -> float:
    """标准化情绪值到0-100范围"""
    return max(0, min(100, (value - min_val) / (max_val - min_val) * 100))


def get_emotion_trend(current: Dict[str, float], 
                     previous: Dict[str, float]) -> Dict[str, str]:
    """
    分析情绪趋势变化
    
    Args:
        current: 当前PAD值 {"pleasure": x, "arousal": y, "dominance": z}
        previous: 之前PAD值
        
    Returns:
        Dict包含趋势描述
    """
    trends = {}
    
    for dim in ["pleasure", "arousal", "dominance"]:
        change = current[dim] - previous[dim]
        
        if abs(change) < 5:
            trend = "稳定"
        elif change > 15:
            trend = "大幅上升"
        elif change > 5:
            trend = "小幅上升"
        elif change < -15:
            trend = "大幅下降"
        else:
            trend = "小幅下降"
        
        trends[dim] = {
            "trend": trend,
            "change": round(change, 2)
        }
    
    return trends


def generate_emotion_summary(emotions: list) -> Dict:
    """
    生成情绪摘要
    
    Args:
        emotions: 情绪状态列表
        
    Returns:
        Dict包含情绪摘要信息
    """
    if not emotions:
        return {"message": "暂无情绪数据"}
    
    # 计算平均值
    avg_pleasure = sum(e["pleasure"] for e in emotions) / len(emotions)
    avg_arousal = sum(e["arousal"] for e in emotions) / len(emotions)
    avg_dominance = sum(e["dominance"] for e in emotions) / len(emotions)
    
    # 情绪分布
    emotion_counts = {}
    for e in emotions:
        emotion = e["traditional_emotion"]
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    # 主要情绪
    main_emotion = max(emotion_counts.items(), key=lambda x: x[1])
    
    # 情绪稳定性
    stability = 100 - (
        sum(abs(e["pleasure"] - avg_pleasure) for e in emotions) +
        sum(abs(e["arousal"] - avg_arousal) for e in emotions) +
        sum(abs(e["dominance"] - avg_dominance) for e in emotions)
    ) / (len(emotions) * 3)
    
    return {
        "summary": {
            "total_records": len(emotions),
            "main_emotion": main_emotion[0],
            "main_emotion_percentage": round(main_emotion[1] / len(emotions) * 100, 1),
            "average_pleasure": round(avg_pleasure, 2),
            "average_arousal": round(avg_arousal, 2),
            "average_dominance": round(avg_dominance, 2),
            "emotional_stability": round(stability, 2)
        },
        "emotion_distribution": emotion_counts
    }