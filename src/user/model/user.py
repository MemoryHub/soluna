from datetime import datetime
from typing import Optional, Dict, Any

class User:
    """用户数据模型"""
    
    def __init__(self,
                 user_id: Optional[str] = None,
                 phone_number: str = "",
                 username: Optional[str] = None,
                 avatar_url: Optional[str] = None,
                 last_login: Optional[datetime] = None,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None,
                 deleted: bool = False):
        """初始化用户对象"""
        self.user_id = user_id
        self.phone_number = phone_number
        # 如果没有提供用户名，使用手机号作为用户名
        self.username = username or phone_number
        self.avatar_url = avatar_url
        self.last_login = last_login
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted = deleted
    
    def to_dict(self) -> Dict[str, Any]:
        """将用户对象转换为字典"""
        return {
            'user_id': self.user_id,
            'phone_number': self.phone_number,
            'username': self.username,
            'avatar_url': self.avatar_url,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted': self.deleted
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """从字典创建用户对象"""
        # 处理日期时间字段，确保值是字符串类型
        if 'last_login' in data and data['last_login'] and isinstance(data['last_login'], str):
            data['last_login'] = datetime.fromisoformat(data['last_login'])
        if 'created_at' in data and data['created_at'] and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and data['updated_at'] and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)