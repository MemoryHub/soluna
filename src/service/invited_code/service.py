# 邀请码服务模块
from typing import List, Dict, Optional, Any
from datetime import datetime
from src.invited_code.generation import generator
from src.invited_code.db.invited_code_dao import invited_code_dao

class InviteCodeService:
    """邀请码服务类，提供邀请码的生成、验证、绑定等功能"""
    
    def __init__(self):
        self.dao = invited_code_dao
    
    def generate_and_save_codes(self, count: int, project_name: str, created_by: Optional[int] = None) -> List[Dict[str, Any]]:
        """生成并保存多个邀请码"""
        try:
            # 生成邀请码
            codes = generator.generate_multiple_codes(count, project_name)
            
            # 设置创建者信息
            for code in codes:
                code['created_by'] = created_by
            
            # 通过DAO层保存到数据库
            success = self.dao.batch_save_invite_codes(codes)
            
            if not success:
                raise Exception("保存邀请码失败")
            
            return codes
        except Exception as e:
            print(f"生成并保存邀请码失败: {str(e)}")
            raise
    
    def verify_invite_code(self, code: str) -> Dict[str, Any]:
        """验证邀请码是否有效"""
        try:
            # 通过DAO层获取邀请码信息
            result = self.dao.get_invite_code_by_code(code)
            
            if not result:
                return {
                    'is_valid': False,
                    'reason': '邀请码不存在'
                }
            
            # 检查邀请码格式
            if not generator.verify_code_format(code):
                return {
                    'is_valid': False,
                    'reason': '邀请码格式错误'
                }
            
            # 检查是否已使用
            if result['is_used']:
                return {
                    'is_valid': False,
                    'reason': '邀请码已使用',
                    'used_by': result['used_by'],
                    'used_at': result['used_at']
                }
            
            # 检查是否过期
            if result['expires_at'] and datetime.now() > result['expires_at']:
                return {
                    'is_valid': False,
                    'reason': '邀请码已过期'
                }
            
            return {
                'is_valid': True,
                'code_info': result
            }
        except Exception as e:
            print(f"验证邀请码失败: {str(e)}")
            raise
    
    def bind_invite_code(self, code: str, user_id: str) -> bool:
        """将邀请码绑定到用户"""
        try:
            # 先验证邀请码
            verify_result = self.verify_invite_code(code)
            
            if not verify_result['is_valid']:
                return False
            
            # 通过DAO层更新邀请码状态
            return self.dao.update_invite_code_used_status(code, user_id)
        except Exception as e:
            print(f"绑定邀请码失败: {str(e)}")
            raise
    
    def get_user_invite_status(self, user_id: str) -> Dict[str, Any]:
        """获取用户的邀请状态"""
        try:
            # 通过DAO层获取用户已使用的邀请码
            codes = self.dao.get_user_used_codes(user_id)
            
            return {
                'has_used_codes': len(codes) > 0,
                'used_codes': codes
            }
        except Exception as e:
            print(f"获取用户邀请状态失败: {str(e)}")
            raise
    
    def get_codes_by_project(self, project_name: str, include_used: bool = False) -> List[Dict[str, Any]]:
        """获取指定项目的邀请码列表"""
        try:
            # 通过DAO层获取项目邀请码
            return self.dao.get_project_codes(project_name, include_used)
        except Exception as e:
            print(f"获取项目邀请码失败: {str(e)}")
            raise

# 创建单例服务实例
invite_code_service = InviteCodeService()