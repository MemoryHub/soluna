from pydantic import BaseModel
from typing import Any, Optional

class ApiResponse(BaseModel):
    recode: int
    msg: str
    data: Optional[Any] = None

    def get(self, key: str, default: Any = None) -> Any:
        """安全地获取data字段中的值"""
        if self.data is None:
            return default
        if isinstance(self.data, dict):
            return self.data.get(key, default)
        if hasattr(self.data, key):
            return getattr(self.data, key)
        return default

    def to_dict(self) -> dict:
        """将ApiResponse对象转换为字典"""
        return self.dict()

    @staticmethod
    def success(data: Any = None, msg: str = "操作成功") -> 'ApiResponse':
        """创建成功响应"""
        return ApiResponse(recode=200, msg=msg, data=data)

    @staticmethod
    def error(recode: int = 500, msg: str = "操作失败") -> 'ApiResponse':
        """创建错误响应"""
        return ApiResponse(recode=recode, msg=msg)

    @staticmethod
    def not_found(msg: str = "资源未找到") -> 'ApiResponse':
        """创建未找到资源响应"""
        return ApiResponse(recode=404, msg=msg)

    @staticmethod
    def bad_request(msg: str = "请求参数错误") -> 'ApiResponse':
        """创建请求参数错误响应"""
        return ApiResponse(recode=400, msg=msg)