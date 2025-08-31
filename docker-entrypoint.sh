#!/bin/sh

# Docker入口脚本
set -e

# 加载环境变量
if [ -f ".env.${ENVIRONMENT:-production}" ]; then
    echo "加载环境配置: .env.${ENVIRONMENT:-production}"
    export $(grep -v "^#" .env.${ENVIRONMENT:-production} | xargs)
fi

# 检查必要的环境变量
required_vars="MONGODB_HOST MONGODB_PORT MONGODB_DATABASE MYSQL_HOST MYSQL_PORT MYSQL_USERNAME MYSQL_PASSWORD MYSQL_DATABASE"

for var in $required_vars; do
    eval value=\$${var}
    if [ -z "$value" ]; then
        echo "错误: 缺少必要的环境变量 $var"
        exit 1
    fi
    echo "环境变量 $var: $value"
done

# 启动应用
echo "启动Soluna API服务..."
exec uvicorn src.api.main:app --host 0.0.0.0 --port 8000
