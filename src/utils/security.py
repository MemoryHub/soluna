import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

class SecurityUtils:
    """安全工具类，提供加密和解密功能"""
    
    def __init__(self):
        # 从环境变量获取密钥，如果不存在则使用默认密钥
        # 注意：在生产环境中，应确保使用安全的密钥管理方式
        key = os.getenv('ENCRYPTION_KEY', 'soluna_encryption_key_32bytes!')
        # 确保密钥长度为32字节（256位）
        self.key = key.ljust(32)[:32].encode('utf-8')
        self.backend = default_backend()
    
    def encrypt(self, data: str) -> str:
        """加密数据"""
        
        # 生成随机IV
        iv = os.urandom(16)
        
        # 创建加密器
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        
        # 对数据进行填充
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data.encode('utf-8')) + padder.finalize()
        
        # 加密数据
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # 组合IV和加密数据并进行base64编码
        result = base64.b64encode(iv + encrypted_data).decode('utf-8')
        return result
    
    def decrypt(self, encrypted_data: str) -> str:
        try:
            # 解码base64数据
            raw_data = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # 提取IV和加密数据
            iv = raw_data[:16]
            ciphertext = raw_data[16:]
            
            # 创建解密器
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
            decryptor = cipher.decryptor()
            
            # 解密数据
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            # 移除填充
            unpadder = padding.PKCS7(128).unpadder()
            data = unpadder.update(padded_data) + unpadder.finalize()
            
            # 解码为字符串
            result = data.decode('utf-8')
            return result
        except Exception as e:
            raise ValueError(f"解密过程发生异常: {str(e)}")

# 创建单例实例
security_utils = SecurityUtils()