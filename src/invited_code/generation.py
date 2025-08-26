# 邀请码生成模块
import random
import string
from datetime import datetime
import hashlib
import sys

class InviteCodeGenerator:
    """邀请码生成器类，用于生成基于项目的邀请码"""
    
    def __init__(self):
        # 字符集：排除易混淆的字符如O, 0, I, l
        self.characters = ''.join([c for c in string.ascii_uppercase + string.digits 
                                   if c not in 'O0Il'])
    
    def generate_code(self, length: int = 8) -> str:
        """生成指定长度的随机邀请码"""
        return ''.join(random.choice(self.characters) for _ in range(length))
    
    def generate_multiple_codes(self, count: int, project_name: str, length: int = 8) -> list[dict]:
        """生成多个邀请码，关联到指定项目"""
        codes = []
        for _ in range(count):
            code = self.generate_code(length)
            codes.append({
                'code': code,
                'project_name': project_name,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'is_used': False,
                'used_by': None,
                'used_at': None,
                'expires_at': None  # 可选的过期时间
            })
        return codes
    
    def verify_code_format(self, code: str) -> bool:
        """验证邀请码格式是否正确"""
        if len(code) != 8:
            return False
        for char in code:
            if char not in self.characters:
                return False
        return True

# 创建生成器实例
generator = InviteCodeGenerator()

# 主函数，用于直接运行生成邀请码（开发者使用）
def main():
    # 获取命令行参数
    count = 10
    project_name = "soluna"
    
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            pass
    
    if len(sys.argv) > 2:
        project_name = sys.argv[2]
    
    # 生成邀请码
    codes = generator.generate_multiple_codes(count, project_name)
    
    print(f"\n成功生成{len(codes)}个邀请码:\n")
    for i, code_info in enumerate(codes, 1):
        print(f"{i}. 邀请码: {code_info['code']}, 项目: {code_info['project_name']}")

if __name__ == "__main__":
    main()