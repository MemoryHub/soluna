-- 创建soluna_user数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS soluna DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci;

-- 使用soluna_user数据库
USE soluna;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '用户ID，UUID格式',
    phone_number VARCHAR(20) NOT NULL UNIQUE COMMENT '手机号码',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    avatar_url VARCHAR(255) NULL COMMENT '头像URL',
    last_login DATETIME NULL COMMENT '最后登录时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '软删除标记'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 创建用户令牌表
CREATE TABLE IF NOT EXISTS user_tokens (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT '自增ID',
    user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
    token TEXT NOT NULL COMMENT 'JWT令牌',
    expire_time DATETIME NOT NULL COMMENT '过期时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '软删除标记',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户令牌表';

-- 创建索引以提高查询性能
CREATE INDEX idx_users_phone_number ON users(phone_number);
CREATE INDEX idx_user_tokens_user_id ON user_tokens(user_id);
CREATE INDEX idx_user_tokens_expire_time ON user_tokens(expire_time);

-- 提示信息
SELECT '用户表和用户令牌表创建成功！' AS message;
SELECT '使用以下命令可以执行此脚本：' AS hint;
SELECT 'mysql -h bj-cdb-40yvxqh6.sql.tencentcdb.com -P 59964 -u zhangbo -p"iDU6ny#@GtU" < create_user_tables.sql' AS command;