# 邀请码API模型模块
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# 邀请码基础模型
class InviteCodeBase(BaseModel):
    code: str
    project_name: str

# 邀请码创建模型
class InviteCodeCreate(InviteCodeBase):
    created_by: Optional[int] = None
    expires_at: Optional[datetime] = None

# 邀请码更新模型
class InviteCodeUpdate(BaseModel):
    is_used: Optional[bool] = None
    used_by: Optional[int] = None
    used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

# 邀请码响应模型
class InviteCodeResponse(InviteCodeBase):
    id: int
    created_at: datetime
    is_used: bool
    used_by: Optional[int] = None
    used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_by: Optional[int] = None
    
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

# 邀请码验证请求
class VerifyInviteCodeRequest(BaseModel):
    code: str

# 邀请码验证响应
class VerifyInviteCodeResponse(BaseModel):
    is_valid: bool
    reason: Optional[str] = None
    code_info: Optional[Dict[str, Any]] = None

# 邀请码绑定请求
class BindInviteCodeRequest(BaseModel):
    code: str
    user_id: str

# 邀请码绑定响应
class BindInviteCodeResponse(BaseModel):
    success: bool
    message: str

# 用户邀请状态请求
class GetUserInviteStatusRequest(BaseModel):
    user_id: str

# 用户邀请状态响应
class UserInviteStatusResponse(BaseModel):
    has_used_codes: bool
    used_codes: List[Dict[str, Any]]

# 生成邀请码请求
class GenerateInviteCodesRequest(BaseModel):
    count: int = 10
    project_name: str
    created_by: Optional[int] = None
    expires_at: Optional[datetime] = None

# 生成邀请码响应
class GenerateInviteCodesResponse(BaseModel):
    codes: List[str]
    count: int

# 获取项目邀请码请求
class GetProjectInviteCodesRequest(BaseModel):
    project_name: str
    include_used: bool = False

# 获取项目邀请码响应
class GetProjectInviteCodesResponse(BaseModel):
    codes: List[InviteCodeResponse]
    total_count: int