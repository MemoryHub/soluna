from pydantic import BaseModel, validator
from typing import Optional
import re

class SendVerificationCodeRequest(BaseModel):
    """发送验证码请求模型"""
    phone_number: str
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """验证手机号格式是否正确"""
        # 简单的手机号格式验证（中国大陆手机号）
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError("手机号格式不正确")
        return v

class LoginRequest(BaseModel):
    """登录请求模型"""
    phone_number: str
    verification_code: str
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """验证手机号格式是否正确"""
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError("手机号格式不正确")
        return v
    
    @validator('verification_code')
    def validate_verification_code(cls, v):
        """验证验证码格式是否正确"""
        if not v or not isinstance(v, str):
            raise ValueError("验证码不能为空")
        if not re.match(r'^\d{6}$', v):
            raise ValueError("验证码必须是6位数字")
        return v

class AutoLoginRequest(BaseModel):
    """自动登录请求模型"""
    token: str
    
    @validator('token')
    def validate_token(cls, v):
        """验证令牌是否为空"""
        if not v or not isinstance(v, str):
            raise ValueError("令牌不能为空")
        return v

class LogoutRequest(BaseModel):
    """登出请求模型"""
    token: str
    
    @validator('token')
    def validate_token(cls, v):
        """验证令牌是否为空"""
        if not v or not isinstance(v, str):
            raise ValueError("令牌不能为空")
        return v

class UserResponse(BaseModel):
    """用户响应模型"""
    user_id: str
    username: str
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    token: Optional[str] = None
    encrypted_user_data: Optional[str] = None
    expire_time: Optional[str] = None

class UserInfoRequest(BaseModel):
    """用户信息请求模型"""
    user_id: str
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """验证用户ID不能为空"""
        if not v or not isinstance(v, str):
            raise ValueError("用户ID不能为空")
        return v