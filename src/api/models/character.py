from pydantic import BaseModel, validator
from typing import Optional
import json
from src.character.model.character import Character
from src.utils.security import security_utils

class GenerateCharacterRequest(BaseModel):
    """生成角色"""
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    language: str = "Chinese"


class SaveCharacterRequest(BaseModel):
    """保存角色请求模型（加密版）"""
    encrypted_character: str
    
    @validator('encrypted_character')
    def validate_encrypted_character(cls, v):
        """验证加密字符数字段是否有效"""
        if not v or not isinstance(v, str):
            raise ValueError("加密字符数字段不能为空且必须为字符串")
        
        try:
            # 尝试解密以验证数据格式是否正确
            decrypted = security_utils.decrypt(v)
            
            # 预处理解密后的数据，去除可能的额外字符
            import re
            # 查找第一个{和最后一个}，提取有效的JSON部分
            match = re.search(r'\{.*\}', decrypted, re.DOTALL)
            if match:
                clean_json_str = match.group(0)
                try:
                    character_dict = json.loads(clean_json_str)
                except json.JSONDecodeError as e:
                    raise ValueError(f"加密字符数字段格式无效: JSON解析失败: {str(e)}")
            else:
                raise ValueError("加密字符数字段格式无效: 未找到有效的JSON对象")
            
            # 验证是否包含Character类所需的必要字段
            required_fields = ['name', 'age', 'gender', 'occupation']
            missing_fields = [field for field in required_fields if field not in character_dict]
            
            if missing_fields:
                raise ValueError(f"解密后的角色数据缺少必要字段: {missing_fields}")
            
        except json.JSONDecodeError as e:
            raise ValueError(f"加密字符数字段格式无效: JSON解析失败: {str(e)}")
        except Exception as e:
            raise ValueError(f"加密字符数字段格式无效: {str(e)}")
        
        return v
    
    def get_character(self) -> Character:
        """从加密数据中获取Character对象"""
        decrypted = security_utils.decrypt(self.encrypted_character)
        
        # 处理解密后可能包含额外数据的JSON字符串
        try:
            # 尝试直接解析
            character_dict = json.loads(decrypted)
            return Character(**character_dict)
        except json.JSONDecodeError:
            # 尝试使用正则表达式提取有效的JSON部分
            import re
            match = re.search(r'\{.*\}', decrypted, re.DOTALL)
            if match:
                clean_json_str = match.group(0)
                try:
                    character_dict = json.loads(clean_json_str)
                    return Character(**character_dict)
                except json.JSONDecodeError as e2:
                    raise ValueError(f"加密字符数字段格式无效: JSON解析失败: {str(e2)}")
            else:
                raise ValueError("加密字符数字段格式无效: 未找到有效的JSON对象")
    
    @classmethod
    def from_character(cls, character: Character) -> 'SaveCharacterRequest':
        """从Character对象创建SaveCharacterRequest实例"""
        # 将Character对象转换为字典
        character_dict = character.__dict__
        # 序列化为JSON字符串
        character_json = json.dumps(character_dict)
        # 加密
        encrypted = security_utils.encrypt(character_json)
        return cls(encrypted_character=encrypted)


class CharacterListRequest(BaseModel):
    """角色列表请求模型"""
    limit: int = 10
    offset: int = 0
    first_letter: str = "*"

