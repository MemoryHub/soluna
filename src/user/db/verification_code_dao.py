from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from src.db.mysql_client import mysql_client

class VerificationCodeDAO:
    """验证码数据访问对象，处理验证码的存储和验证"""
    
    def __init__(self):
        self.db = mysql_client
    
    def save_code(self, phone_number: str, code: str, expire_time: datetime, ip_address: str = "unknown") -> bool:
        """保存验证码到数据库"""
        query = """
            INSERT INTO verification_codes (phone_number, verification_code, expire_time, created_at, is_used, ip_address) 
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP, 0, %s)
        """
        params = (phone_number, code, expire_time, ip_address)
        
        try:
            self.db.execute_update(query, params)
            return True
        except Exception as e:
            print(f"保存验证码失败: {e}")
            return False
    
    def get_last_code_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """获取指定手机号的最后一条验证码记录"""
        query = """
            SELECT * FROM verification_codes 
            WHERE phone_number = %s 
            ORDER BY created_at DESC 
            LIMIT 1
        """
        result = self.db.execute_query(query, (phone_number,))
        return result[0] if result else None
    
    def verify_code(self, phone_number: str, code: str) -> bool:
        """验证验证码是否正确且未过期、未使用"""
        query = """
            SELECT * FROM verification_codes 
            WHERE phone_number = %s 
              AND verification_code = %s 
              AND expire_time > CURRENT_TIMESTAMP 
              AND is_used = 0
            ORDER BY created_at DESC 
            LIMIT 1
        """
        result = self.db.execute_query(query, (phone_number, code))
        
        # 如果找到有效的验证码，标记为已使用
        if result:
            self.mark_as_used(result[0]['id'])
            return True
        
        return False
    
    def mark_as_used(self, code_id: int) -> bool:
        """将验证码标记为已使用"""
        query = """
            UPDATE verification_codes 
            SET is_used = 1 
            WHERE id = %s
        """
        try:
            self.db.execute_update(query, (code_id,))
            return True
        except Exception as e:
            print(f"标记验证码为已使用失败: {e}")
            return False
    
    def get_phone_request_count(self, phone_number: str, minutes: int = 1) -> int:
        """获取指定手机号在指定分钟内的请求次数"""
        query = """
            SELECT COUNT(*) as count FROM verification_codes 
            WHERE phone_number = %s 
              AND created_at > DATE_SUB(CURRENT_TIMESTAMP, INTERVAL %s MINUTE)
        """
        result = self.db.execute_query(query, (phone_number, minutes))
        return result[0]['count'] if result else 0
    
    def get_ip_request_count(self, ip_address: str, hours: int = 24) -> int:
        """获取指定IP地址在指定小时内的请求次数"""
        query = """
            SELECT COUNT(*) as count FROM verification_codes 
            WHERE ip_address = %s 
              AND created_at > DATE_SUB(CURRENT_TIMESTAMP, INTERVAL %s HOUR)
        """
        result = self.db.execute_query(query, (ip_address, hours))
        return result[0]['count'] if result else 0
    
    def save_ip_request(self, phone_number: str, ip_address: str) -> bool:
        """保存IP请求记录"""
        # 这里我们直接在save_code方法中添加IP地址信息
        # 因为我们会修改save_code方法来接收IP地址参数
        # 所以这里暂时不需要单独的保存IP请求记录的方法
        return True

# 创建单例实例
verification_code_dao = VerificationCodeDAO()