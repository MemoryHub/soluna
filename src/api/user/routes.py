import os
import sys
from fastapi import APIRouter, Depends, Request
from src.api.models.user import SendVerificationCodeRequest, LoginRequest, AutoLoginRequest, LogoutRequest, UserInfoRequest
from src.api.responds.base_response import ApiResponse
from src.service.user.service import user_service

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# 创建路由
router = APIRouter(prefix="/api/user", tags=["user"])

@router.post("/send-verification-code", response_model=ApiResponse)
async def send_verification_code(fastapi_request: Request, request: SendVerificationCodeRequest):
    """发送验证码"""
    try:
        # 获取客户端IP地址
        client_ip = fastapi_request.client.host if fastapi_request.client else "unknown"
        # 调用服务层发送验证码
        result = user_service.send_verification_code(request.phone_number, client_ip)
        
        if result:
            return ApiResponse.success(data="", msg="验证码发送成功")
        else:
            return ApiResponse.error(recode=500, msg="验证码发送失败")
    except Exception as e:
        print(f"发送验证码时发生错误: {str(e)}")
        return ApiResponse.error(recode=500, msg="验证码发送失败")

@router.post("/login", response_model=ApiResponse)
async def login(request: LoginRequest):
    """用户登录接口"""
    try:
        # 调用服务层进行登录
        result = user_service.login(request.phone_number, request.verification_code)
        
        if result:
            return ApiResponse.success(data=result, msg="登录成功")
        else:
            return ApiResponse.error(recode=400, msg="验证码错误、已过期或已使用")
    except Exception as e:
        print(f"登录时发生错误: {str(e)}")
        return ApiResponse.error(recode=500, msg="登录失败")

@router.post("/auto-login", response_model=ApiResponse)
async def auto_login(request: AutoLoginRequest):
    """自动登录"""
    try:
        # 调用服务层进行自动登录
        result = user_service.auto_login(request.token)
        
        if result:
            return ApiResponse.success(data=result, msg="自动登录成功")
        else:
            return ApiResponse.error(recode=401, msg="令牌无效或已过期")
    except Exception as e:
        print(f"自动登录时发生错误: {str(e)}")
        return ApiResponse.error(recode=500, msg="自动登录失败")

@router.post("/logout", response_model=ApiResponse)
async def logout(request: LogoutRequest):
    """用户登出"""
    try:
        # 调用服务层进行登出
        user_service.logout(request.token)
        # 无论服务层返回什么，都返回成功
        # 因为用户的登出意图应该被尊重
        return ApiResponse.success(msg="登出成功")
        
    except Exception as e:
        print(f"登出时发生错误: {str(e)}")
        # 即使出现异常，也返回成功，避免前端显示错误
        return ApiResponse.success(msg="登出成功")



@router.post("/info", response_model=ApiResponse)
async def get_user_info(request: UserInfoRequest):
    """获取用户信息"""
    try:
        # 调用服务层获取用户信息
        user_info = user_service.get_user_info(request.user_id)
        
        if user_info:
            return ApiResponse.success(data=user_info, msg="获取用户信息成功")
        else:
            return ApiResponse.not_found(msg="用户不存在")
    except Exception as e:
        print(f"获取用户信息时发生错误: {str(e)}")
        return ApiResponse.error(recode=500, msg="获取用户信息失败")