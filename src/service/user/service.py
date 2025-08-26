import os
import uuid
import jwt
import time
import random
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from src.user.db.user_dao import user_dao, token_dao
from src.user.db.verification_code_dao import verification_code_dao
from src.user.model.user import User
from src.utils.security import security_utils
from src.service.invited_code.service import invite_code_service
from src.character.utils import convert_object_id

class UserService:
    """用户服务层，处理用户相关的业务逻辑"""
    
    def __init__(self):
        # 从环境变量获取JWT密钥和过期时间，如果不存在则使用默认值
        self.jwt_secret = os.getenv('JWT_SECRET', 'soluna_jwt_secret_key_32bytes!')
        self.jwt_expire_hours = int(os.getenv('JWT_EXPIRE_HOURS', '24'))
        # 频率限制配置
        self.phone_rate_limit_seconds = 60  # 手机号请求间隔限制（秒）
        self.ip_rate_limit_count = 10  # IP地址24小时内最大请求次数
        self.code_expire_minutes = 5  # 验证码有效期（分钟）
    
    def generate_user_id(self) -> str:
        """生成唯一的用户ID"""
        return str(uuid.uuid4())
    
    def send_verification_code(self, phone_number: str, ip_address: str = "unknown") -> Dict[str, Any]:
        """发送验证码，包含频率限制"""
        # 检查手机号频率限制（60秒内只能请求一次）
        last_code = verification_code_dao.get_last_code_by_phone(phone_number)
        if last_code:
            last_request_time = last_code['created_at']
            if isinstance(last_request_time, str):
                last_request_time = datetime.fromisoformat(last_request_time)
            time_diff = (datetime.now() - last_request_time).total_seconds()
            if time_diff < self.phone_rate_limit_seconds:
                wait_time = int(self.phone_rate_limit_seconds - time_diff)
                raise Exception(f"请求过于频繁，请{wait_time}秒后再试")
        
        # 检查IP地址频率限制（24小时内不超过10次）
        ip_request_count = verification_code_dao.get_ip_request_count(ip_address)
        if ip_request_count >= self.ip_rate_limit_count:
            raise Exception("今日验证码请求次数已达上限，请明天再试")
        
        # 生成随机验证码
        verification_code = ''.join(random.choices('0123456789', k=6))
        
        # 计算过期时间
        expire_time = datetime.now() + timedelta(minutes=self.code_expire_minutes)
        
        # 保存验证码到数据库
        if not verification_code_dao.save_code(phone_number, verification_code, expire_time, ip_address):
            raise Exception("保存验证码失败")
        
        # 在实际生产环境中，这里应该调用短信服务API发送验证码
        # 目前仅记录日志
        print(f"向手机号 {phone_number} 发送验证码: {verification_code}")
        
        # 返回验证码信息（不包含验证码本身）
        return {
            'phone_number': phone_number,
            'expire_time': expire_time.isoformat()
        }
    
    def verify_code(self, phone_number: str, code: str) -> bool:
        """验证验证码是否正确且未过期、未使用"""
        # 使用DAO层验证验证码，确保验证码只能使用一次
        return verification_code_dao.verify_code(phone_number, code)
    
    def generate_jwt_token(self, user_id: str) -> str:
        """生成JWT令牌"""
        # 设置过期时间
        expire_time = datetime.utcnow() + timedelta(hours=self.jwt_expire_hours)
        
        # 构建payload
        payload = {
            'user_id': user_id,
            'exp': expire_time,
            'iat': datetime.utcnow()
        }
        
        # 生成JWT令牌
        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        
        # 保存令牌到数据库
        token_dao.save_token(user_id, token, expire_time)
        
        return token
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证JWT令牌"""
        try:
            # 验证令牌是否存在且有效
            if not token_dao.validate_token(token):
                return None
            
            # 解码JWT令牌
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            # 检查令牌是否过期
            if payload.get('exp') < time.time():
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            # 令牌已过期
            token_dao.delete_token(token)
            return None
        except jwt.InvalidTokenError:
            # 令牌无效
            return None
    
    def generate_login_result(self, user: User) -> Dict[str, Any]:
        """生成登录结果数据 - 将所有信息都加密传输"""
        # 生成JWT令牌
        token = self.generate_jwt_token(user.user_id)
        expire_time = (datetime.now() + timedelta(hours=self.jwt_expire_hours)).isoformat()
        
        # 获取用户邀请状态
        try:
              user_invite_status = invite_code_service.get_user_invite_status(user.user_id)
              # 确保used_codes的格式为[{'code': 'code_value'}]
              has_used_codes = user_invite_status['has_used_codes']
              # 格式化used_codes列表
              formatted_used_codes = [{'code': code_info['code']} for code_info in user_invite_status['used_codes']]
              user_invite_status_data = {'has_used_codes': has_used_codes, 'used_codes': formatted_used_codes}
        except Exception as e:
            user_invite_status_data = {'has_used_codes': False, 'used_codes': []}
        
        processed_invite_status = convert_object_id(user_invite_status_data)
        
        user_data = {
            "user_id": user.user_id,
            "phone_number": user.phone_number,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "token": token,
            "expire_time": expire_time,
            "invite_status": processed_invite_status
        }

        # 使用convert_object_id函数确保所有数据可JSON序列化（包括datetime）
        serializable_data = convert_object_id(user_data)
        
        # 将数据转换为JSON字符串 - 添加ensure_ascii=False和indent参数以确保正确处理中文
        json_str = json.dumps(serializable_data, ensure_ascii=False, indent=2)
        
        # 加密JSON字符串
        encrypted_user_data = security_utils.encrypt(json_str)
        
        # 只返回encrypted_user_data字段
        return {
            'encrypted_user_data': encrypted_user_data
        }
    
    def login(self, phone_number: str, verification_code: str) -> Optional[Dict[str, Any]]:
        """用户登录"""
        # 验证验证码
        if not self.verify_code(phone_number, verification_code):
            return None
        
        # 检查用户是否存在
        existing_user = user_dao.get_user_by_phone(phone_number)
        
        if existing_user:
            # 用户已存在，更新最后登录时间
            user_id = existing_user['user_id']
            user_dao.update_last_login(user_id)
            
            # 转换为User对象
            user = User.from_dict(existing_user)
        else:
            # 用户不存在，创建新用户
            user_id = self.generate_user_id()
            
            # 创建用户对象
            user = User(
                user_id=user_id,
                phone_number=phone_number,
                username=phone_number,
                last_login=datetime.now()
            )
            
            # 保存到数据库
            if not user_dao.create_user(user.to_dict()):
                return None
        
        # 生成登录结果
        return self.generate_login_result(user)
    
    def auto_login(self, token: str) -> Optional[Dict[str, Any]]:
        """自动登录功能"""
        # 验证令牌
        payload = self.verify_jwt_token(token)
        
        if not payload or 'user_id' not in payload:
            return None
        
        # 获取用户信息
        user_id = payload['user_id']
        user_data = user_dao.get_user_by_id(user_id)
        
        if not user_data:
            return None
        
        # 更新最后登录时间
        user_dao.update_last_login(user_id)
        
        # 转换为User对象
        user = User.from_dict(user_data)
        
        # 使用generate_login_result方法生成加密的登录结果，与login接口保持一致
        return self.generate_login_result(user)
    
    def logout(self, token: str) -> bool:
        """用户登出"""
        # 先验证令牌是否有效
        if not token_dao.validate_token(token):
            return False
        # 再删除令牌
        return token_dao.delete_token(token)
    
    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        user_data = user_dao.get_user_by_id(user_id)
        
        if not user_data:
            return None
        
        # 从用户数据中移除敏感信息
        user_data.pop('phone_number', None)
        
        return user_data

# 创建单例实例
user_service = UserService()