import os
import sys

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)

from fastapi import APIRouter, Body
from typing import List, Optional

from src.service.interaction.service import interaction_service
from src.api.responds.base_response import ApiResponse

# 创建互动功能路由
router = APIRouter(prefix="/api/interaction", tags=["interaction"])

@router.post("/perform", response_model=ApiResponse)
async def perform_interaction(
    user_id: str = Body(...),
    character_id: str = Body(...),
    interaction_type: str = Body(...)
):
    """执行互动操作
    
    请求体:
    {
        "user_id": "用户ID",
        "character_id": "角色ID",
        "interaction_type": "feed|comfort|overtime|water"
    }
    """
    try:
        result = interaction_service.perform_interaction(user_id, character_id, interaction_type)
        if result["success"]:
            return ApiResponse.success(
                data=result,
                msg=result.get("message", "互动成功")
            )
        else:
            # 今日已互动的情况返回403
            if "今日已" in result.get("message", ""):
                return ApiResponse.error(recode=403, msg=result["message"])
            else:
                return ApiResponse.error(recode=400, msg=result["message"])
                
    except Exception as e:
        return ApiResponse.error(recode=500, msg=f"互动操作失败: {str(e)}")

@router.post("/stats/get/{character_id}", response_model=ApiResponse)
async def get_interaction_stats(
    character_id: str,
    user_id: Optional[str] = Body(None)
):
    """获取角色的互动统计数据
    
    可选请求体:
    {
        "user_id": "用户ID" (用于检查今日互动状态)
    }
    """
    try:
        result = interaction_service.get_interaction_stats(character_id, user_id)
        
        if "error" in result:
            return ApiResponse.error(recode=500, msg=result["error"])
        
        return ApiResponse.success(data=result, msg="统计数据获取成功")
        
    except Exception as e:
        return ApiResponse.error(recode=500, msg=f"获取统计数据失败: {str(e)}")

@router.post("/stats/batch", response_model=ApiResponse)
async def get_batch_interaction_stats(character_ids: list[str] = Body(...)):
    """批量获取角色的互动统计数据
    
    请求体:
    {
        "character_ids": ["角色ID1", "角色ID2", ...]
    }
    """
    try:
        if not character_ids:
            return ApiResponse.error(recode=400, msg="缺少必要参数: character_ids")
        result = interaction_service.get_batch_interaction_stats(character_ids)
        if "error" in result:
            return ApiResponse.error(recode=500, msg=result["error"])
        
        return ApiResponse.success(data=result, msg="批量统计数据获取成功")
        
    except Exception as e:
        return ApiResponse.error(recode=500, msg=f"批量获取统计数据失败: {str(e)}")

@router.post("/check-today", response_model=ApiResponse)
async def check_today_interaction(
    user_id: str = Body(...),
    character_id: str = Body(...),
    interaction_type: Optional[str] = Body(None)
):
    """检查用户今日是否已与角色互动
    
    请求体:
    {
        "user_id": "用户ID",
        "character_id": "角色ID",
        "interaction_type": "feed|comfort|overtime|water" (可选)
    }
    """
    try:
        result = interaction_service.check_today_interaction(user_id, character_id, interaction_type)
        
        if "error" in result:
            return ApiResponse.error(recode=500, msg=result["error"])
        
        return ApiResponse.success(data=result, msg="今日互动状态检查成功")
        
    except Exception as e:
        return ApiResponse.error(recode=500, msg=f"检查今日互动状态失败: {str(e)}")

@router.post("/user/history", response_model=ApiResponse)
async def get_user_interaction_history(
    user_id: str = Body(...),
    limit: int = Body(100)
):
    """获取用户的互动历史
    
    请求体:
    {
        "user_id": "用户ID",
        "limit": 100 (可选，默认100)
    }
    """
    try:
        result = interaction_service.get_user_interaction_history(user_id, limit)
        
        if "error" in result:
            return ApiResponse.error(recode=500, msg=result["error"])
        
        return ApiResponse.success(data=result, msg="用户互动历史获取成功")
        
    except Exception as e:
        return ApiResponse.error(recode=500, msg=f"获取用户互动历史失败: {str(e)}")

# 健康检查端点
@router.get("/health", response_model=ApiResponse)
async def health_check():
    """互动服务健康检查"""
    return ApiResponse.success(data={"status": "healthy", "service": "interaction"})