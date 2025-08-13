#!/bin/bash

# 设置PYTHONPATH，确保能找到src目录
cd $(dirname $0)
export PYTHONPATH="$PYTHONPATH:$(pwd)/src"

# 激活虚拟环境（如果使用虚拟环境）
# source venv/bin/activate

# 启动FastAPI服务
cd src/api
uvicorn main:app --reload --host 0.0.0.0 --port 8000