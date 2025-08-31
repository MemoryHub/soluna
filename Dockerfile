# 使用Python 3.11作为基础镜像
FROM python:3.11-alpine

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 设置pip使用国内镜像源和超时设置
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn
ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_NO_CACHE_DIR=1

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories \
    && apk update \
    && apk add --no-cache --virtual .build-deps \
        bash \
        build-base \
        linux-headers \
    && apk add --no-cache curl

# 复制依赖文件
COPY requirements.txt .

# 使用国内镜像源安装依赖，增加重试次数和超时时间
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    --timeout=100 \
    --retries=10 \
    --prefer-binary \
    --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    --extra-index-url https://mirrors.aliyun.com/pypi/simple/ \
    -r requirements.txt && \
    apk del .build-deps && \
    rm -rf /var/cache/apk/*

# 在COPY之前确保创建目录
RUN mkdir -p /app

# 设置工作目录
WORKDIR /app

# 复制启动脚本
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh && ls -la /app/docker-entrypoint.sh

# 复制应用代码
COPY . /app

# 暴露端口
EXPOSE 8000

# 启动应用
ENTRYPOINT ["/app/docker-entrypoint.sh"]