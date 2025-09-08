"""
情感API路由
提供情绪状态的RESTful API接口
"""

from fastapi import APIRouter, Body
from typing import List, Dict, Any

from src.service.emotion.service import emotion_service
from src.service.emotion.emotion_update_service import emotion_update_service
from src.api.responds.base_response import ApiResponse
from datetime import datetime

router = APIRouter(prefix="/api/emotion", tags=["emotion"])


@router.post("/character/init/{character_id}")
async def initialize_character_emotion(character_id: str):
    """
    1. 初始化角色情绪状态
    
    - **character_id**: 角色唯一标识
    
    返回初始化结果
    """
    try:
        # 使用业务服务层初始化情绪
        success = emotion_service.initialize_character_emotion(character_id)
        
        if success:
            # 获取初始化后的情绪状态
            emotion_result = emotion_service.calculate_and_get_emotion(character_id)
            if emotion_result:
                emotion_data = emotion_result["database_data"]
                return ApiResponse.success(
                    data={
                        "character_id": emotion_data["character_id"],
                        "pleasure": emotion_data["pleasure_score"],
                        "arousal": emotion_data["arousal_score"],
                        "dominance": emotion_data["dominance_score"],
                        "current_emotion_score": emotion_data["current_emotion_score"]
                    },
                    msg="角色情绪初始化成功"
                )
            else:
                return ApiResponse.not_found(msg="初始化后无法获取情绪状态")
        else:
            return ApiResponse.error(code=500, msg="初始化失败")
        
    except Exception as e:
        return ApiResponse.error(code=500, msg=str(e))


@router.post("/characters/init/batch")
async def batch_initialize_characters(
    character_ids: List[str] = Body(..., description="角色ID列表")
):
    """
    1. 批量初始化角色情绪
    
    请求体:
    {
        "character_ids": ["角色ID1", "角色ID2", ...]
    }
    
    返回初始化结果
    """
    try:
        results = emotion_service.batch_initialize_characters(character_ids)
        return ApiResponse.success(data=results, msg="批量初始化完成")
        
    except Exception as e:
        return ApiResponse.error(code=500, msg=str(e))


@router.post("/character/update")
async def update_emotion_from_event(request_data: dict):
    """
    3. 更新角色情绪状态
    
    - **character_id**: 角色唯一标识
    - **pleasure_change**: 愉悦度变化值
    - **arousal_change**: 激活度变化值
    - **dominance_change**: 支配感变化值
    
    返回更新后的情绪状态
    """
    try:
        character_id = request_data.get("character_id")
        pleasure_change = request_data.get("pleasure_change", 0)
        arousal_change = request_data.get("arousal_change", 0)
        dominance_change = request_data.get("dominance_change", 0)
        
        if not character_id:
            return ApiResponse.bad_request(msg="缺少character_id参数")
            
        # 使用业务服务层更新情绪
        success = emotion_service.update_emotion_from_event(
            character_id, pleasure_change, arousal_change, dominance_change
        )
        
        if success:
            # 获取更新后的情绪状态
            emotion_result = emotion_service.calculate_and_get_emotion(character_id)
            if emotion_result:
                emotion_data = emotion_result["database_data"]
                return ApiResponse.success(
                    data={
                        "character_id": emotion_data["character_id"],
                        "pleasure": emotion_data["pleasure_score"],
                        "arousal": emotion_data["arousal_score"],
                        "dominance": emotion_data["dominance_score"],
                        "current_emotion_score": emotion_data["current_emotion_score"]
                    },
                    msg="情绪更新成功"
                )
            else:
                return ApiResponse.not_found(msg="角色情绪状态不存在")
        else:
            return ApiResponse.error(code=500, msg="情绪更新失败")
        
    except Exception as e:
        return ApiResponse.error(code=500, msg=str(e))


@router.post("/characters/update/batch")
async def batch_update_emotions(
    updates: List[Dict[str, Any]] = Body(..., description="更新数据列表")
):
    """
    4. 批量更新角色情绪状态
    
    请求体:
    [
        {
            "character_id": "char1",
            "pad_impact": {"pleasure": 10, "arousal": -5, "dominance": 15}
        },
        {
            "character_id": "char2", 
            "pad_impact": {"pleasure": -10, "arousal": 20, "dominance": -15}
        }
    ]
    
    返回每个角色的更新结果
    """
    try:
            
        results = emotion_service.batch_update_emotions(updates)
        
        return ApiResponse.success(data=results, msg="批量更新完成")
        
    except Exception as e:
        return ApiResponse.error(code=500, msg=str(e))


@router.post("/character/get")
async def get_character_emotion(request_data: dict):
    """
    5. 获取角色情绪完整信息
    
    - **character_id**: 角色唯一标识
    
    返回角色的情绪数据
    """
    try:
        character_id = request_data.get("character_id")
        if not character_id:
            return ApiResponse.bad_request(msg="缺少character_id参数")
            
        emotion_data = emotion_service.get_character_emotion(character_id)
        
        if emotion_data:
            return ApiResponse.success(data=emotion_data, msg="获取情绪信息成功")
        else:
            return ApiResponse.not_found(msg="角色情绪状态不存在")
            
    except Exception as e:
        return ApiResponse.error(code=500, msg=str(e))


@router.post("/characters/get/batch")
async def get_characters_emotion_batch(character_ids: list[str] = Body(...)):
    """
    6. 批量获取角色情绪完整信息
    
    - **character_ids**: 角色ID列表
    
    返回每个角色的情绪数据
    """
    try:
        if not character_ids:
            return ApiResponse.bad_request(msg="缺少character_ids参数")
            
        emotions = emotion_service.get_characters_emotion_batch(character_ids)
        
        return ApiResponse.success(data=emotions, msg="批量获取情绪信息成功")
        
    except Exception as e:
        return ApiResponse.error(code=500, msg=str(e))


@router.post("/character/calculate")
async def calculate_and_get_emotion(request_data: dict):
    """
    7. 计算并获取完整的情绪状态
    
    - **character_id**: 角色唯一标识
    
    返回包含计算结果的情绪状态数据
    """
    try:
        character_id = request_data.get("character_id")
        if not character_id:
            return ApiResponse.bad_request(msg="缺少character_id参数")
            
        result = emotion_service.calculate_and_get_emotion(character_id)
        
        if result:
            return ApiResponse.success(data=result, msg="情绪计算成功")
        else:
            return ApiResponse.not_found(msg="角色情绪状态不存在")
            
    except Exception as e:
        return ApiResponse.error(code=500, msg=str(e))

@router.post("/characters/update/thirty-minutes")
async def update_emotions_from_recent_events(
    request_data: dict = Body(..., description="可选参数")
):
    """
    8. 批量更新所有角色最近30分钟内的情绪
    
    根据最近30分钟内的生活轨迹事件，计算并更新所有角色的情绪状态
    
    请求体(可选):
    {
        "current_time": "2024-01-01 14:30:00"  # 如不传则使用当前时间
    }
    
    返回更新统计信息
    """
    try:

        current_time_str = request_data.get("current_time")
        if current_time_str:
            current_time = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S")
        else:
            current_time = datetime.now()
        
        # 获取并更新所有角色30分钟内的情绪
        result = await emotion_update_service.update_emotions_from_recent_events(current_time)
        
        return ApiResponse.success(data=result, msg=f"成功更新{result.get('updated_count', 0)}个角色的情绪")
        
    except Exception as e:
        return ApiResponse.error(code=500, msg=str(e))