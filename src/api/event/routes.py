import os
import sys
import os
from fastapi import APIRouter, Body
from typing import Optional

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) 
sys.path.append(project_root)

from src.service.event.service import event_service
from src.api.responds.base_response import ApiResponse

# 创建主路由
router = APIRouter()

# 创建事件配置路由
profile_router = APIRouter(prefix="/api/event-profiles", tags=["event-profiles"])
# 创建生活轨迹路由
life_path_router = APIRouter(prefix="/api/life-paths", tags=["life-paths"])


# 事件配置相关接口
@profile_router.post("/get-by-character-id", response_model=ApiResponse) 
async def get_event_profiles_by_character(character_id: str):
    """根据角色ID获取事件配置列表"""
    result = event_service.get_event_profiles_by_character_id(character_id)
    if result is None:
        return ApiResponse.not_found(msg="未找到该角色的事件配置")
    return ApiResponse.success(data=result, msg="事件配置获取成功")

@profile_router.post("/get-by-character-ids", response_model=ApiResponse) 
async def get_event_profiles_by_character_ids(character_ids: list[str] = Body(...)):
    """根据角色ID数组批量获取事件配置列表"""
    result = event_service.get_event_profiles_by_character_ids(character_ids)
    if result is None:
        return ApiResponse.not_found(msg="未找到事件配置")
    return ApiResponse.success(data=result, msg="事件配置批量获取成功")

@profile_router.post("/generate", response_model=ApiResponse)
async def generate_event_profile(character_id: str, language: str = "Chinese"):
    """生成事件配置"""
    result = await event_service.generate_event_profile(character_id, language)
    if not result:
        return ApiResponse.error(recode=500, msg="事件配置生成失败")
    return ApiResponse.success(data=result, msg="事件配置生成成功")

@profile_router.post("/save", response_model=ApiResponse)
async def save_event_profile(event_profile: dict):
    """保存事件配置"""
    result = event_service.save_event_profile(event_profile)
    if not result:
        return ApiResponse.error(recode=500, msg="事件配置保存失败")
    return ApiResponse.success(data={"profile_id": result}, msg="事件配置保存成功")

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


@life_path_router.post("/generate", response_model=ApiResponse)
async def create_life_path(
    character_id: str = Body(...), 
    start_date: str = Body(...), 
    end_date: str = Body(...), 
    max_events: int = Body(3)
):
    """新建生活轨迹"""
    success = await event_service.generate_life_path(character_id, start_date, end_date, max_events)
    if not success:
        return ApiResponse.error(recode=500, msg="生活轨迹创建失败")
    return ApiResponse.success(data={"success": True}, msg="生活轨迹创建成功")

@life_path_router.post("/batch-generate-all", response_model=ApiResponse)
async def batch_create_life_paths(start_date: str = Body(...), end_date: str = Body(...), max_events: int = Body(3), limit: int = Body(0)):
    """批量生成所有角色生活轨迹（用于定时任务）
    
    参数:
    - start_date: 开始时间 (格式: YYYY-MM-DD)
    - end_date: 结束时间 (格式: YYYY-MM-DD)
    - max_events: 每个角色生成的最大事件数 (默认: 3)
    - limit: 限制处理的角色数量 (默认: 0，表示处理所有角色)
    
    返回:
    - 处理成功的角色数量
    - 处理失败的角色数量
    - 失败角色的详细信息
    """
    try:
        # 调用服务层的批量生成方法
        result = await event_service.batch_generate_life_paths(start_date, end_date, max_events, limit)
        
        # 检查结果是否包含错误信息
        if result.get("success") is False:
            return ApiResponse.error(recode=500, msg=result.get("message", "批量生成生活轨迹失败"))
        
        return ApiResponse.success(
            data=result,
            msg=f"批量生成所有角色生活轨迹完成，成功{result.get('success_count', 0)}个，失败{result.get('failed_count', 0)}个"
        )
    except Exception as e:
        return ApiResponse.error(recode=500, msg=f"批量生成生活轨迹失败: {str(e)}")

# 将子路由添加到主路由
router.include_router(profile_router)
router.include_router(life_path_router)