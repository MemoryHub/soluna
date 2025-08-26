# 邀请码API路由模块
import os
import sys
from fastapi import APIRouter, Depends
from src.api.responds.base_response import ApiResponse
from src.service.invited_code.service import invite_code_service
from src.api.models.invite_code import (
    VerifyInviteCodeRequest,
    BindInviteCodeRequest,
    GetUserInviteStatusRequest,
    GenerateInviteCodesRequest,
    GetProjectInviteCodesRequest
)

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# 创建路由
router = APIRouter(prefix="/api/invite-code", tags=["invite-code"])

@router.post("/verify", response_model=ApiResponse)
async def verify_invite_code(request: VerifyInviteCodeRequest):
    """验证邀请码是否有效"""
    try:
        result = invite_code_service.verify_invite_code(request.code)
        
        if result['is_valid']:
            # 只返回必要的信息，不包含敏感数据
            safe_code_info = {
                'code': result['code_info']['code'],
                'project_name': result['code_info']['project_name']
            }
            return ApiResponse.success(data=safe_code_info, msg="邀请码有效")
        else:
            return ApiResponse.error(recode=400, msg=result['reason'])
    except Exception as e:
        print(f"验证邀请码时发生错误: {str(e)}")
        return ApiResponse.error(recode=500, msg="验证邀请码失败")

@router.post("/bind", response_model=ApiResponse)
async def bind_invite_code(request: BindInviteCodeRequest):
    """将邀请码绑定到用户"""
    try:
        success = invite_code_service.bind_invite_code(request.code, request.user_id)
        
        if success:
            return ApiResponse.success(msg="邀请码绑定成功")
        else:
            return ApiResponse.error(recode=400, msg="邀请码无效或已被使用")
    except Exception as e:
        print(f"绑定邀请码时发生错误: {str(e)}")
        return ApiResponse.error(recode=500, msg="绑定邀请码失败")

@router.post("/user-status", response_model=ApiResponse)
async def get_user_invite_status(request: GetUserInviteStatusRequest):
    """获取用户的邀请状态"""
    try:
        status = invite_code_service.get_user_invite_status(request.user_id)
        return ApiResponse.success(data=status, msg="获取邀请状态成功")
    except Exception as e:
        print(f"获取用户邀请状态时发生错误: {str(e)}")
        return ApiResponse.error(recode=500, msg="获取邀请状态失败")

# @router.post("/generate", response_model=ApiResponse)
async def generate_invite_codes(request: GenerateInviteCodesRequest):
    """生成邀请码（管理功能）"""
    try:
        # 检查参数有效性
        if request.count <= 0:
            return ApiResponse.bad_request(msg="生成数量必须大于0")
        
        if not request.project_name or len(request.project_name.strip()) == 0:
            return ApiResponse.bad_request(msg="项目名称不能为空")
        
        codes = invite_code_service.generate_and_save_codes(
            request.count,
            request.project_name,
            request.created_by
        )
        
        # 只返回邀请码本身，不包含所有细节
        code_list = [code['code'] for code in codes]
        return ApiResponse.success(data=code_list, msg=f"成功生成{len(codes)}个邀请码")
    except Exception as e:
        print(f"生成邀请码时发生错误: {str(e)}")
        return ApiResponse.error(recode=500, msg="生成邀请码失败")

# @router.post("/project-codes", response_model=ApiResponse)
async def get_project_invite_codes(request: GetProjectInviteCodesRequest):
    """获取指定项目的邀请码列表（管理功能）"""
    try:
        if not request.project_name or len(request.project_name.strip()) == 0:
            return ApiResponse.bad_request(msg="项目名称不能为空")
        
        codes = invite_code_service.get_codes_by_project(
            request.project_name,
            request.include_used
        )
        
        # 对返回的数据进行处理，只包含必要信息
        processed_codes = []
        for code in codes:
            processed_code = {
                'code': code['code'],
                'is_used': code['is_used'],
                'project_name': code['project_name'],
                'created_at': code['created_at'].strftime('%Y-%m-%d %H:%M:%S') if code['created_at'] else None
            }
            
            # 如果已使用，添加使用信息
            if code['is_used']:
                processed_code['used_by'] = code['used_by']
                processed_code['used_at'] = code['used_at'].strftime('%Y-%m-%d %H:%M:%S') if code['used_at'] else None
            
            # 如果有过期时间，添加过期信息
            if code['expires_at']:
                processed_code['expires_at'] = code['expires_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            processed_codes.append(processed_code)
        
        return ApiResponse.success(data=processed_codes, msg=f"获取到{len(processed_codes)}个邀请码")
    except Exception as e:
        print(f"获取项目邀请码时发生错误: {str(e)}")
        return ApiResponse.error(recode=500, msg="获取邀请码失败")