import os
import sys
import os
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) 
sys.path.append(project_root)

from src.character.model.event_profile import Event, EventProfile
from src.service.event.service import event_service
from src.api.responds.base_response import ApiResponse


# 创建事件配置路由
profile_router = APIRouter(prefix="/api/characters/{character_id}/event-profiles", tags=["event-profiles"])
# 创建生活轨迹路由
life_path_router = APIRouter(prefix="/api/characters/{character_id}/life-paths", tags=["life-paths"])


# 事件配置相关接口
@profile_router.post("", response_model=ApiResponse)
async def create_event_profile(character_id: str, language: str = "Chinese"):
    """新建事件配置"""
    result = await event_service.create_event_profile(character_id, language)
    if not result:
        return ApiResponse.error(recode=500, msg="事件配置创建失败")
    return ApiResponse.success(data={"profile_id": result}, msg="事件配置创建成功")

@profile_router.post("/delete/{profile_id}", response_model=ApiResponse)
async def delete_event_profile(character_id: str, profile_id: str):
    """删除事件配置"""
    success = await event_service.delete_event_profile(profile_id)
    if not success:
        return ApiResponse.not_found(msg="事件配置未找到或删除失败")
    return ApiResponse.success(data={"success": True}, msg="事件配置已删除")

@profile_router.post("/delete-by-character", response_model=ApiResponse)
async def delete_event_profile_by_character(character_id: str):
    """根据角色ID删除事件配置"""
    success = await event_service.delete_event_profile_by_character_id(character_id)
    if not success:
        return ApiResponse.not_found(msg="未找到角色或事件配置删除失败")
    return ApiResponse.success(data={"success": True}, msg="事件配置已删除")


# 生活轨迹相关接口
@life_path_router.post("", response_model=ApiResponse)
async def create_life_path(character_id: str, profile_id: str, start_time: str, end_time: str, max_events: int = 3):
    """新建生活轨迹"""
    success = await event_service.generate_life_path(character_id, profile_id, start_time, end_time, max_events)
    if not success:
        return ApiResponse.error(recode=500, msg="生活轨迹创建失败")
    return ApiResponse.success(data={"success": True}, msg="生活轨迹创建成功")

# 将子路由添加到主路由
router.include_router(profile_router)
router.include_router(life_path_router)