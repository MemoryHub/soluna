#!/usr/bin/env python3
"""
情感系统基本使用示例 - 可直接运行的版本
"""

import sys
import os
import asyncio

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.service.emotion.emotion_service import EmotionService
from src.emotion.utils.emotion_utils import (
    pad_to_rgb, get_emotion_intensity, get_emotion_trend
)


def demo_basic_usage():
    """基本使用示例"""
    print("=== 情感系统基本使用示例 ===\n")
    
    # 创建情感服务
    service = EmotionService()
    
    # 示例1: 计算情绪
    print("1. 情绪计算示例:")
    character_id = "user_001"
    
    # 快乐情绪
    emotion1 = service.calculate_emotion_from_pad(
        character_id, 70, 60, 50
    )
    print(f"PAD值: (70, 60, 50)")
    print(f"情绪: {emotion1.traditional_emotion} ({emotion1.vibe_emotion})")
    print(f"表情: {emotion1.emoji}")
    print(f"颜色: {emotion1.color}")
    print(f"置信度: {emotion1.confidence}")
    print()
    
    # 悲伤情绪
    emotion2 = service.calculate_emotion_from_pad(
        character_id, -50, -30, -40
    )
    print(f"PAD值: (-50, -30, -40)")
    print(f"情绪: {emotion2.traditional_emotion} ({emotion2.vibe_emotion})")
    print(f"表情: {emotion2.emoji}")
    print(f"颜色: {emotion2.color}")
    print()
    
    # 焦虑情绪
    emotion3 = service.calculate_emotion_from_pad(
        character_id, -20, 50, -60
    )
    print(f"PAD值: (-20, 50, -60)")
    print(f"情绪: {emotion3.traditional_emotion} ({emotion3.vibe_emotion})")
    print(f"表情: {emotion3.emoji}")
    print(f"颜色: {emotion3.color}")
    print()


def demo_color_mapping():
    """颜色映射示例"""
    print("=== 颜色映射示例 ===\n")
    
    # 使用工具函数生成颜色
    colors = [
        (80, 70, 60, "极度快乐"),
        (-60, -40, -50, "极度悲伤"),
        (30, 20, 40, "平静"),
        (-10, 60, -30, "焦虑")
    ]
    
    for p, a, d, desc in colors:
        rgb_color = pad_to_rgb(p, a, d)
        intensity = get_emotion_intensity(p, a, d)
        
        print(f"{desc} (PAD: {p}, {a}, {d})")
        print(f"颜色: {rgb_color}")
        print(f"整体强度: {intensity['overall_intensity']:.1f}")
        print()


def demo_emotion_groups():
    """情绪分组示例"""
    print("=== 情绪分组示例 ===\n")
    
    service = EmotionService()
    
    emotions = ["开心", "悲伤", "焦虑", "平静", "愤怒", "恐惧"]
    
    for emotion in emotions:
        group = service.get_emotion_group(emotion)
        if group:
            print(f"情绪: {emotion}")
            print(f"分组: {group['group_name']}")
            print(f"颜色: {group['color']}")
            print(f"描述: {group['description']}")
            print()


def demo_trend_analysis():
    """趋势分析示例"""
    print("=== 趋势分析示例 ===\n")
    
    # 模拟情绪变化
    current = {"pleasure": 60, "arousal": 40, "dominance": 50}
    previous = {"pleasure": 40, "arousal": 60, "dominance": 30}
    
    trends = get_emotion_trend(current, previous)
    
    print("情绪变化趋势:")
    for dim, trend in trends.items():
        print(f"{dim}: {trend['trend']} (变化: {trend['change']})")
    print()


async def demo_async_usage():
    """异步使用示例"""
    print("=== 异步使用示例 ===\n")
    
    # 这里可以集成数据库操作
    print("异步功能已准备就绪，可集成数据库操作")
    print()


if __name__ == "__main__":
    try:
        # 运行基本示例
        demo_basic_usage()
        demo_color_mapping()
        demo_emotion_groups()
        demo_trend_analysis()
        
        # 运行异步示例
        asyncio.run(demo_async_usage())
        
        print("=== 示例运行完成 ===")
        
    except Exception as e:
        print(f"运行示例时出错: {e}")
        print("请确保项目路径设置正确")