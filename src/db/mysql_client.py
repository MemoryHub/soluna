import os
import pymysql
import time
import logging
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MySQLClient:
    _instance = None
    _max_reconnect_attempts = 3
    _reconnect_delay = 1  # 秒

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
        self._reconnect_count = 0
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
                autocommit=True,
                connect_timeout=30,
                read_timeout=30,
                write_timeout=30,
                max_allowed_packet=16777216,
                init_command="SET sql_mode=''"
            )
            self.cursor = self.connection.cursor()
            self._reconnect_count = 0  # 重置重连计数器
            logger.info("MySQL连接已建立")
        except Exception as e:
            logger.error(f"连接MySQL失败: {e}")
            raise

    def execute_query(self, query, params=None):
        """执行SQL查询并返回结果，包含重连机制"""
        return self._execute_with_retry(self.cursor.execute, query, params, fetch=True)

    def execute_update(self, query, params=None):
        """执行SQL更新操作，包含重连机制"""
        return self._execute_with_retry(self.cursor.execute, query, params, fetch=False)

    def _execute_with_retry(self, execute_func, query, params=None, fetch=True):
        """带重试机制的执行方法"""
        for attempt in range(self._max_reconnect_attempts):
            try:
                # 检查连接是否有效
                if not self._is_connection_valid():
                    logger.warning(f"连接无效，尝试重新连接... (第{attempt + 1}次)")
                    self.connect()
                
                # 执行查询
                result = execute_func(query, params or ())
                
                if fetch:
                    return self.cursor.fetchall()
                else:
                    self.connection.commit()
                    return result
                    
            except (pymysql.err.OperationalError, pymysql.err.InterfaceError) as e:
                error_code = e.args[0] if e.args else None
                
                # MySQL连接丢失错误码
                if error_code in (2006, 2013, 0):
                    logger.warning(f"MySQL连接丢失，尝试重连... (第{attempt + 1}次): {e}")
                    self._reconnect_count += 1
                    
                    if attempt < self._max_reconnect_attempts - 1:
                        time.sleep(self._reconnect_delay * (attempt + 1))  # 指数退避
                        continue
                    else:
                        logger.error("达到最大重连次数，放弃重连")
                        raise
                else:
                    # 其他错误直接抛出
                    logger.error(f"数据库操作失败: {e}")
                    if not fetch and self.connection:
                        self.connection.rollback()
                    raise
                    
            except Exception as e:
                logger.error(f"数据库操作失败: {e}")
                if not fetch and self.connection:
                    self.connection.rollback()
                raise

    def _is_connection_valid(self):
        """检查连接是否有效"""
        try:
            if not self.connection or not self.connection.open:
                return False
            
            # 发送ping命令检查连接
            self.connection.ping(reconnect=True)
            return True
            
        except Exception as e:
            logger.warning(f"连接检查失败: {e}")
            return False

    def ping(self):
        """手动检查连接健康状态"""
        return self._is_connection_valid()

    def get_reconnect_count(self):
        """获取重连次数统计"""
        return self._reconnect_count

    def close_connection(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.open:
            self.connection.close()
            logger.info("MySQL连接已关闭")

    def execute_batch_update(self, query: str, data: list) -> int:
        """
        批量执行更新操作
        
        Args:
            query: SQL更新语句，使用%s作为占位符
            data: 参数列表，每个元素是一个元组
            
        Returns:
            受影响的行数总和
        """
        if not data:
            return 0
            
        total_affected = 0
        try:
            # 检查连接是否有效
            if not self._is_connection_valid():
                logger.warning("连接无效，重新连接...")
                self.connect()
            
            # 使用executemany进行批量操作
            affected_rows = self.cursor.executemany(query, data)
            self.connection.commit()
            total_affected = affected_rows or 0
            
            logger.info(f"批量更新完成，影响行数: {total_affected}")
            return total_affected
            
        except Exception as e:
            logger.error(f"批量更新失败: {e}")
            if self.connection:
                self.connection.rollback()
            raise

    def execute_batch_insert(self, query: str, data: list) -> int:
        """
        批量执行插入操作
        
        Args:
            query: SQL插入语句，使用%s作为占位符
            data: 参数列表，每个元素是一个元组
            
        Returns:
            插入的行数
        """
        if not data:
            return 0
            
        try:
            # 检查连接是否有效
            if not self._is_connection_valid():
                logger.warning("连接无效，重新连接...")
                self.connect()
            
            # 使用executemany进行批量操作
            affected_rows = self.cursor.executemany(query, data)
            self.connection.commit()
            
            logger.info(f"批量插入完成，影响行数: {affected_rows}")
            return affected_rows or 0
            
        except Exception as e:
            logger.error(f"批量插入失败: {e}")
            if self.connection:
                self.connection.rollback()
            raise

# 创建单例实例
mysql_client = MySQLClient.get_instance()