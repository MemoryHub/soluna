# Soluna项目一键部署指南

## 🚀 快速开始（基于deploy.sh脚本）

本项目使用一键部署脚本，无需手动操作Docker命令！

## 📋 前置要求
- Docker & Docker Compose
- 服务器已配置好域名和SSL证书
- 足够的磁盘空间（建议10GB以上）

## 🔧 一键部署命令

### 1. 生产环境部署
```bash
# 一键部署生产环境
./deploy.sh start production
```

### 2. 开发环境部署
```bash
# 一键部署开发环境
./deploy.sh start development
```

### 3. 常用操作命令
```bash
# 停止所有服务
./deploy.sh stop

# 重启服务
./deploy.sh restart production

# 查看服务状态
./deploy.sh status

# 查看帮助
./deploy.sh help
```

## ⚠️ 关键权限设置（部署前必做）

### 文件权限调整
在首次部署前，必须确保以下文件有执行权限：

```bash
# 1. 设置soluna项目的docker-entrypoint.sh权限
cd /path/to/soluna
chmod +x docker-entrypoint.sh
ls -la docker-entrypoint.sh  # 确认权限为 -rwxr-xr-x

# 2. 设置soluna-scheduler项目的docker-entrypoint.sh权限
cd /path/to/soluna-scheduler
chmod +x docker-entrypoint.sh
ls -la docker-entrypoint.sh  # 确认权限为 -rwxr-xr-x
```

### 权限问题排查
如果一键部署失败，检查：
```bash
# 查看容器日志
./deploy.sh logs

# 检查权限错误
./deploy.sh status

# 手动修复权限
chmod +x docker-entrypoint.sh
```

## 🎯 一键部署流程

### 首次部署
```bash
# 1. 克隆代码
git clone <your-repo-url>
cd soluna

# 2. 设置权限（仅首次）
chmod +x deploy.sh
chmod +x docker-entrypoint.sh
chmod +x ../soluna-scheduler/docker-entrypoint.sh

# 4. 一键部署
./deploy.sh start production
```

### 更新部署
```bash
# 拉取最新代码
git pull origin main

# 一键重新部署
./deploy.sh restart production
```

### 5. 验证部署（一键检查）

#### 5.1 服务状态检查
```bash
# 一键查看所有服务状态
./deploy.sh status

# 预期输出示例：
# [2024-09-01 12:00:00] 检查生产环境服务状态...
# NAME              STATUS          PORTS
# soluna-web        Up 10 minutes   0.0.0.0:3000->3000/tcp
# soluna-api        Up 10 minutes   0.0.0.0:8000->8000/tcp
# soluna-scheduler  Up 10 minutes   
```

#### 5.2 健康检查
```bash
# 一键查看日志
./deploy.sh logs

# 或者查看特定服务的日志
./deploy.sh logs soluna-api
./deploy.sh logs soluna-scheduler
```

### 6. 一键部署高级用法

#### 6.1 完整命令列表
```bash
# 查看所有可用命令
./deploy.sh help

# 实际输出：
# Soluna项目部署脚本
# 
# 使用方法:
#   ./deploy.sh [命令] [环境]
# 
# 命令:
#   start       启动服务 (默认命令)
#   stop        停止所有服务
#   restart     重启服务
#   status      查看服务状态
#   help        显示此帮助信息
# 
# 环境:
#   production  生产环境 (默认)
#   development 开发环境
```

#### 6.2 开发环境一键部署
```bash
# 开发环境部署（端口3001/8001）
./deploy.sh start development

# 开发环境访问地址：
# - 前端: http://localhost:3001
# - API: http://localhost:8001
```

### 7. 一键维护操作

#### 7.1 日志管理（一键查看）
```bash
# 查看所有服务日志
./deploy.sh logs

# 查看特定服务日志
./deploy.sh logs soluna-api
./deploy.sh logs soluna-scheduler
./deploy.sh logs soluna-web
```

#### 7.2 服务管理
```bash
# 停止所有服务
./deploy.sh stop

# 重启生产环境
./deploy.sh restart production

# 重启开发环境
./deploy.sh restart development
```

### 8. 一键部署故障排查

#### 8.1 常见错误处理
```bash
# 如果部署失败，按顺序执行：

# 1. 检查权限
ls -la deploy.sh
ls -la docker-entrypoint.sh
ls -la ../soluna-scheduler/docker-entrypoint.sh

# 2. 检查环境文件
cat .env.production | head -10

# 3. 检查服务状态
./deploy.sh status

# 4. 查看详细日志
./deploy.sh logs
```

#### 8.2 一键修复权限
```bash
# 一键修复所有权限问题
chmod +x deploy.sh
chmod +x docker-entrypoint.sh
chmod +x ../soluna-scheduler/docker-entrypoint.sh

# 重新部署
./deploy.sh restart production
```

### 9. 生产环境配置（一键集成）

#### 9.1 一键部署脚本已自动处理
- ✅ 自动创建logs/scheduler目录
- ✅ 自动检查Docker环境
- ✅ 自动清理旧镜像
- ✅ 自动验证配置文件
- ✅ 自动检查网络配置

#### 9.2 手动配置（仅首次）
```bash
# 1. 设置权限（仅首次部署）
chmod +x deploy.sh
chmod +x docker-entrypoint.sh
chmod +x ../soluna-scheduler/docker-entrypoint.sh

# 3. 一键部署
./deploy.sh start production
```

## 🎯 部署验证清单（一键检查）

### 一键验证命令
```bash
# 执行完整验证
./deploy.sh status
```

### 手动验证步骤
- [ ] `chmod +x deploy.sh` 已执行
- [ ] `chmod +x docker-entrypoint.sh` 已执行（soluna项目）
- [ ] `chmod +x docker-entrypoint.sh` 已执行（soluna-scheduler项目）
- [ ] `.env.production` 文件已配置
- [ ] `./deploy.sh start production` 执行成功
- [ ] `./deploy.sh status` 显示所有服务"Up"
- [ ] 域名访问正常

## 🔧 一键部署脚本特性

### 自动化功能
- ✅ 自动检查Docker环境
- ✅ 自动创建必要目录
- ✅ 自动清理旧镜像
- ✅ 自动验证配置文件
- ✅ 自动显示部署信息
- ✅ 自动健康检查

### 错误处理
- ✅ 权限检查提示
- ✅ 配置文件验证
- ✅ 服务状态监控
- ✅ 详细错误日志