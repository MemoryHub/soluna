import os
import sys
from fastapi import APIRouter
from src.api.models.character import GenerateCharacterRequest, SaveCharacterRequest, CharacterListRequest
import json

# 先将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)

# 然后再导入其他模块
from src.service.character.service import character_service
from src.api.responds.base_response import ApiResponse
from src.utils.security import security_utils
from src.db.mongo_client import mongo_client
from src.service.character.service import character_service as verify_service
from src.service.emotion.service import emotion_service
from src.service.event.service import EventService
import asyncio

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
        
        # 强制刷新数据库连接以确保数据一致性
        try:
            # 强制刷新连接状态
            mongo_client.get_database().command('ping')
        except Exception as e:
            print(f"数据库连接检查失败: {str(e)}")
            return ApiResponse.error(recode=500, msg="数据库连接异常")
        
        # 验证角色是否真正保存到数据库（添加重试机制确保数据一致性）
        # 重试验证角色是否真正写入数据库
        max_retries = 3
        retry_delay = 0.1  # 100ms
        
        saved_character = None
        for attempt in range(max_retries):
            saved_character = verify_service.get_character_by_id(character.character_id)
            if saved_character:
                # 验证关键字段一致性
                if (saved_character.character_id == character.character_id and 
                    saved_character.name == character.name):
                    break
                else:
                    print(f"角色数据验证失败，第{attempt+1}次重试")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
        
        if not saved_character:
            return ApiResponse.error(recode=500, msg="角色保存后验证失败，数据库写入可能存在延迟")
        
        # 只有在角色真正保存成功后，才生成事件配置
        if request.is_with_event:
            try:
                # 生成事件配置
                event_profile = await EventService.generate_event_profile(
                    character_id=character.character_id,
                    language="Chinese"
                )
                
                if not event_profile:
                    return ApiResponse.error(recode=500, msg="事件配置生成失败")
                
                # 保存事件配置到数据库
                saved_event_id = EventService.save_event_profile(event_profile)
                if not saved_event_id:
                    return ApiResponse.error(recode=500, msg="事件配置保存失败")
                
                print(f"成功为角色 {character.character_id} 生成并保存事件配置，事件ID: {saved_event_id}")
                
                # 第三步：初始化角色情绪并存入数据库
                try:
                    # 初始化角色情绪状态（包含随机PAD打分）
                    emotion_init_result = emotion_service.initialize_character_emotion(character.character_id)
                    
                    if emotion_init_result:
                        print(f"成功为角色 {character.character_id} 初始化情绪状态（包含随机PAD打分）")
                    else:
                        print(f"为角色 {character.character_id} 初始化情绪状态失败")
                        
                except Exception as e:
                    # 情绪初始化失败时不中断主流程，仅记录错误
                    print(f"初始化角色情绪状态时出错: {str(e)}")
                
            except Exception as e:
                # 事件配置生成或保存失败时返回错误
                print(f"生成或保存事件配置时出错: {str(e)}")
                return ApiResponse.error(recode=500, msg=f"事件配置处理失败: {str(e)}")
        
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
    
    # 对角色列表数据进行加密
    # 先将数据转换为JSON字符串
    characters_json = json.dumps(characters, ensure_ascii=False, default=str)
    # 加密数据
    encrypted_data = security_utils.encrypt(characters_json)
    
    # 返回加密后的数据
    return ApiResponse.success(data={"encrypted_characters_data": encrypted_data}, msg="获取角色列表成功")

@router.post("/delete/{character_id}", response_model=ApiResponse)
async def delete_character(character_id: str):
    """删除角色及其关联事件"""
    success = character_service.delete_character(character_id)
    if not success:
        return ApiResponse.not_found(msg="角色未找到")
    return ApiResponse.success(data={"success": True}, msg="角色及其关联事件已删除")