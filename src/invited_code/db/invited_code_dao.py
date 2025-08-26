# 邀请码DAO层模块
from typing import List, Dict, Optional, Any
from datetime import datetime
from src.db.mysql_client import mysql_client

class InviteCodeDAO:
    """邀请码数据访问对象，负责所有数据库操作"""
    
    def __init__(self):
        self.mysql_client = mysql_client

    def save_invite_code(self, code_info: Dict[str, Any]) -> bool:
        """保存单个邀请码到数据库"""
        try:
            sql = """
            INSERT INTO invite_codes (code, project_name, created_at, created_by, expires_at)
            VALUES (%s, %s, %s, %s, %s)
            """
            row_count = self.mysql_client.execute_update(sql, (
                code_info['code'],
                code_info['project_name'],
                code_info['created_at'],
                code_info.get('created_by'),
                code_info.get('expires_at')
            ))
            return row_count > 0
        except Exception as e:
            print(f"保存邀请码失败: {str(e)}")
            return False
    
    def batch_save_invite_codes(self, codes_info: List[Dict[str, Any]]) -> bool:
        """批量保存邀请码到数据库"""
        try:
            # 逐条保存，因为mysql_client没有提供executemany方法
            success_count = 0
            sql = """
            INSERT INTO invite_codes (code, project_name, created_at, created_by, expires_at)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            for code_info in codes_info:
                try:
                    row_count = self.mysql_client.execute_update(sql, (
                        code_info['code'],
                        code_info['project_name'],
                        code_info['created_at'],
                        code_info.get('created_by'),
                        code_info.get('expires_at')
                    ))
                    if row_count > 0:
                        success_count += 1
                except Exception as e:
                    print(f"保存单个邀请码失败: {code_info['code']}, 错误: {str(e)}")
                    
            return success_count == len(codes_info)
        except Exception as e:
            print(f"批量保存邀请码失败: {str(e)}")
            return False
    
    def get_invite_code_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """通过邀请码获取邀请码信息"""
        try:
            sql = """
            SELECT * FROM invite_codes WHERE code = %s
            """
            results = self.mysql_client.execute_query(sql, (code,))
            return results[0] if results else None
        except Exception as e:
            print(f"获取邀请码信息失败: {str(e)}")
            return None
    
    def update_invite_code_used_status(self, code: str, user_id: str) -> bool:
        """更新邀请码为已使用状态"""
        try:
            sql = """
            UPDATE invite_codes 
            SET is_used = TRUE, used_by = %s, used_at = NOW() 
            WHERE code = %s AND is_used = FALSE
            """
            row_count = self.mysql_client.execute_update(sql, (user_id, code))
            return row_count > 0
        except Exception as e:
            print(f"更新邀请码使用状态失败: {str(e)}")
            return False
    
    def get_user_used_codes(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户已使用的邀请码"""
        try:
            sql = """
            SELECT code, project_name, used_at 
            FROM invite_codes 
            WHERE used_by = %s
            """
            return self.mysql_client.execute_query(sql, (user_id,))
        except Exception as e:
            print(f"获取用户使用的邀请码失败: {str(e)}")
            return []
    
    def get_project_codes(self, project_name: str, include_used: bool = False) -> List[Dict[str, Any]]:
        """获取指定项目的邀请码列表"""
        try:
            if include_used:
                sql = """
                SELECT * FROM invite_codes WHERE project_name = %s
                """
            else:
                sql = """
                SELECT * FROM invite_codes WHERE project_name = %s AND is_used = FALSE
                """
            
            return self.mysql_client.execute_query(sql, (project_name,))
        except Exception as e:
            print(f"获取项目邀请码失败: {str(e)}")
            return []

# 创建DAO实例
invited_code_dao = InviteCodeDAO()