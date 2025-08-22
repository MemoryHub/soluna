import os
import sys
from fastapi import APIRouter
from src.api.models.character import GenerateCharacterRequest, SaveCharacterRequest, CharacterListRequest

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)

from src.service.character.service import character_service
from src.api.responds.base_response import ApiResponse


# 创建路由
router = APIRouter(prefix="/api/characters", tags=["characters"])




@router.post("/generate", response_model=ApiResponse)
async def generate_character(
    request_data: GenerateCharacterRequest
):
    """生成角色"""
    # 从请求体中提取参数
    name = request_data.name
    age = request_data.age
    gender = request_data.gender
    occupation = request_data.occupation
    language = request_data.language
    
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

@router.post("/save", response_model=ApiResponse)
async def save_character(request: SaveCharacterRequest):
    """保存角色到数据库（加密版）"""
    try:
        # 从加密请求中获取角色对象
        character = request.get_character()
        
        # 提交角色到服务层
        result = character_service.submit_character(character)
        if not result:
            return ApiResponse.error(recode=500, msg="角色保存失败")
        
        # 将保存后的Character对象转换为字典返回
        return ApiResponse.success(data=character.to_dict(), msg="角色保存成功")
    except Exception as e:
        # 捕获并记录详细错误信息，但向客户端返回更通用的错误消息
        print(f"保存角色时发生错误: {str(e)}")
        return ApiResponse.error(recode=400, msg="角色数据无效或保存失败")

@router.post("/get/{character_id}", response_model=ApiResponse)
async def get_character(character_id: str):
    """根据ID获取角色详情"""
    character = character_service.get_character_by_id(character_id)
    if not character:
        return ApiResponse.not_found(msg="角色未找到")
    return ApiResponse.success(data=character, msg="获取角色详情成功")

@router.post("/list", response_model=ApiResponse)
async def get_all_characters(request: CharacterListRequest):
    """获取所有角色列表"""
    characters = character_service.get_all_characters(request.limit, request.offset, request.first_letter)
    return ApiResponse.success(data=characters, msg="获取角色列表成功")

@router.post("/delete/{character_id}", response_model=ApiResponse)
async def delete_character(character_id: str):
    """删除角色及其关联事件"""
    success = character_service.delete_character(character_id)
    if not success:
        return ApiResponse.not_found(msg="角色未找到")
    return ApiResponse.success(data={"success": True}, msg="角色及其关联事件已删除")