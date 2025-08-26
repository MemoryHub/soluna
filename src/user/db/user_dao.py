from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from src.db.mysql_client import mysql_client

class UserDAO:
    """用户数据访问对象，处理用户表的CRUD操作"""
    
    def __init__(self):
        self.db = mysql_client
    
    def get_user_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """根据手机号获取用户信息"""
        query = """SELECT * FROM users WHERE phone_number = %s AND deleted = FALSE"""
        result = self.db.execute_query(query, (phone_number,))
        return result[0] if result else None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """根据用户ID获取用户信息"""
        query = """SELECT * FROM users WHERE user_id = %s AND deleted = FALSE"""
        result = self.db.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def create_user(self, user_data: Dict[str, Any]) -> bool:
        """创建新用户"""
        query = """
            INSERT INTO users (user_id, phone_number, username, avatar_url, last_login)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            user_data.get('user_id'),
            user_data.get('phone_number'),
            user_data.get('username'),
            user_data.get('avatar_url'),
            user_data.get('last_login')
        )
        try:
            self.db.execute_update(query, params)
            return True
        except Exception as e:
            print(f"创建用户失败: {e}")
            return False
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """更新用户信息"""
        # 构建动态更新语句
        set_clauses = []
        params = []
        
        for key, value in user_data.items():
            if key != 'user_id' and key != 'created_at':
                set_clauses.append(f"{key} = %s")
                params.append(value)
        
        # 添加更新时间
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        params.append(user_id)
        
        query = f"""UPDATE users SET {', '.join(set_clauses)} WHERE user_id = %s"""
        
        try:
            self.db.execute_update(query, params)
            return True
        except Exception as e:
            print(f"更新用户失败: {e}")
            return False
    
    def update_last_login(self, user_id: str) -> bool:
        """更新用户最后登录时间"""
        query = """UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = %s"""
        try:
            self.db.execute_update(query, (user_id,))
            return True
        except Exception as e:
            print(f"更新最后登录时间失败: {e}")
            return False

class TokenDAO:
    """令牌数据访问对象，处理令牌表的CRUD操作"""
    
    def __init__(self):
        self.db = mysql_client
    
    def save_token(self, user_id: str, token: str, expire_time: datetime) -> bool:
        """保存用户令牌"""
        # 先删除该用户之前的令牌
        self.delete_token_by_user_id(user_id)
        
        query = """
            INSERT INTO user_tokens (user_id, token, expire_time)
            VALUES (%s, %s, %s)
        """
        params = (user_id, token, expire_time)
        
        try:
            self.db.execute_update(query, params)
            return True
        except Exception as e:
            print(f"保存令牌失败: {e}")
            return False
    
    def get_token_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """根据用户ID获取令牌"""
        query = """SELECT * FROM user_tokens WHERE user_id = %s"""
        result = self.db.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def get_user_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """根据令牌获取用户信息"""
        query = """
            SELECT u.* FROM users u 
            JOIN user_tokens t ON u.user_id = t.user_id 
            WHERE t.token = %s AND u.deleted = FALSE
        """
        result = self.db.execute_query(query, (token,))
        return result[0] if result else None
    
    def delete_token(self, token: str) -> bool:
        """删除指定令牌"""
        query = """DELETE FROM user_tokens WHERE token = %s"""
        try:
            self.db.execute_update(query, (token,))
            return True
        except Exception as e:
            print(f"删除令牌失败: {e}")
            return False
    
    def delete_token_by_user_id(self, user_id: str) -> bool:
        """删除指定用户的所有令牌"""
        query = """DELETE FROM user_tokens WHERE user_id = %s"""
        try:
            self.db.execute_update(query, (user_id,))
            return True
        except Exception as e:
            print(f"删除用户令牌失败: {e}")
            return False
    
    def validate_token(self, token: str) -> bool:
        """验证令牌是否有效"""
        query = """
            SELECT COUNT(*) as count FROM user_tokens 
            WHERE token = %s AND expire_time > CURRENT_TIMESTAMP
        """
        result = self.db.execute_query(query, (token,))
        return result[0]['count'] > 0 if result else False

# 创建单例实例
user_dao = UserDAO()
token_dao = TokenDAO()