import os
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class MySQLClient:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        # 从环境变量获取MySQL配置
        self.host = os.getenv('MYSQL_HOST')
        self.port = os.getenv('MYSQL_PORT')
        self.username = os.getenv('MYSQL_USERNAME')
        self.password = os.getenv('MYSQL_PASSWORD')
        self.database_name = os.getenv('MYSQL_DATABASE')
        self.charset = 'utf8mb4'
        
        # 验证必要的配置是否存在
        self._validate_config()
        
        # 初始化连接
        self.connection = None
        self.cursor = None
        self.connect()
        
    def _validate_config(self):
        """验证必要的配置是否存在"""
        required_configs = {
            'MYSQL_HOST': self.host,
            'MYSQL_PORT': self.port,
            'MYSQL_USERNAME': self.username,
            'MYSQL_PASSWORD': self.password,
            'MYSQL_DATABASE': self.database_name
        }
        
        missing_configs = [key for key, value in required_configs.items() if value is None]
        if missing_configs:
            raise ValueError(f"缺少必要的MySQL配置: {', '.join(missing_configs)}. 请在.env文件中设置这些配置。")
        
        # 确保端口是整数
        try:
            self.port = int(self.port)
        except ValueError:
            raise ValueError(f"MYSQL_PORT必须是整数，当前值: {self.port}")

    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password,
                database=self.database_name,
                charset=self.charset,
                cursorclass=DictCursor,
                autocommit=True
            )
            self.cursor = self.connection.cursor()
        except Exception as e:
            print(f"连接MySQL失败: {e}")
            raise

    def execute_query(self, query, params=None):
        """执行SQL查询并返回结果"""
        try:
            if not self.connection or not self.connection.open:
                self.connect()
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Exception as e:
            print(f"执行查询失败: {e}")
            raise

    def execute_update(self, query, params=None):
        """执行SQL更新操作"""
        try:
            if not self.connection or not self.connection.open:
                self.connect()
            result = self.cursor.execute(query, params or ())
            self.connection.commit()
            return result
        except Exception as e:
            print(f"执行更新失败: {e}")
            if self.connection:
                self.connection.rollback()
            raise

    def close_connection(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.open:
            self.connection.close()
            print("MySQL连接已关闭")

# 创建单例实例
mysql_client = MySQLClient.get_instance()