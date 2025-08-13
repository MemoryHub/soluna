import os
import sys
import os
from fastapi import APIRouter, HTTPException
from typing import List, Optional

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) 
sys.path.append(project_root)

from src.character.model.character import Character
from src.service.character.service import character_service
from src.api.responds.base_response import ApiResponse


# 创建路由
router = APIRouter(prefix="/api/characters", tags=["characters"])


@router.post("/generate", response_model=ApiResponse)
async def generate_character(
    name: Optional[str] = None,
    age: Optional[int] = None,
    gender: Optional[str] = None,
    occupation: Optional[str] = None,
    language: str = "Chinese"
):
    """生成角色"""
    character = await character_service.generate_character(
        name=name,
        age=age,
        gender=gender,
        occupation=occupation,
        language=language
    )
    if not character:
        return ApiResponse.error(recode=500, msg="角色生成失败")
    return ApiResponse.success(data=character, msg="角色生成成功")

@router.post("/{character_id}", response_model=ApiResponse)
async def get_character(character_id: str):
    """根据ID获取角色详情"""
    character = character_service.get_character_by_id(character_id)
    if not character:
        return ApiResponse.not_found(msg="角色未找到")
    return ApiResponse.success(data=character, msg="获取角色详情成功")

@router.post("/list", response_model=ApiResponse)
async def get_all_characters(limit: int = 10, offset: int = 0):
    """获取所有角色列表"""
    characters = character_service.get_all_characters(limit, offset)
    return ApiResponse.success(data=characters, msg="获取角色列表成功")

@router.post("/delete/{character_id}", response_model=ApiResponse)
async def delete_character(character_id: str):
    """删除角色及其关联事件"""
    success = character_service.delete_character(character_id)
    if not success:
        return ApiResponse.not_found(msg="角色未找到")
    return ApiResponse.success(data={"success": True}, msg="角色及其关联事件已删除")