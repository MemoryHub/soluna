import os
import pymongo
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class MongoDBClient:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        # 从环境变量获取MongoDB配置
        self.host = os.getenv('MONGODB_HOST', 'localhost')
        self.port = int(os.getenv('MONGODB_PORT', '27017'))
        self.username = os.getenv('MONGODB_USERNAME', '')
        self.password = os.getenv('MONGODB_PASSWORD', '')
        self.database_name = os.getenv('MONGODB_DATABASE', 'soluna')

        # 构建连接字符串
        if self.username and self.password:
            self.mongo_uri = f'mongodb://{self.username}:{self.password}@{self.host}:{self.port}/'
        else:
            self.mongo_uri = f'mongodb://{self.host}:{self.port}/'

        # 建立连接
        try:
            self.client = pymongo.MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000, directConnection=True)
            # 测试连接
            # 测试连接
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
        except Exception as e:
            print(f"连接MongoDB失败: {e}")
            raise

    def get_database(self):
        return self.db

    def close_connection(self):
        if self.client:
            self.client.close()
            print("MongoDB连接已关闭")

# 创建单例实例
mongo_client = MongoDBClient.get_instance()