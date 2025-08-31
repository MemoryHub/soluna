#!/bin/bash

# Soluna项目一键部署脚本
# 作者: Soluna团队
# 版本: 1.0

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# 检查Docker和Docker Compose
check_docker() {
    log "检查Docker环境..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    log "Docker环境检查通过"
}

# 创建必要的目录
create_directories() {
    log "创建必要的目录..."
    
    mkdir -p logs/scheduler
    
    log "目录创建完成"
}

# 检查环境文件
check_env_files() {
    local env_type=$1
    local env_file=".env.${env_type}"
    
    log "检查${env_type}环境配置文件..."
    
    if [[ ! -f "$env_file" ]]; then
        error "${env_type}环境配置文件 ${env_file} 不存在，请创建该文件并填入实际配置"
        exit 1
    fi
    
    log "${env_type}环境配置文件检查完成"
}

# 检查网络配置
check_network() {
    local env_type=$1
    
    if [[ "$env_type" == "production" ]]; then
        log "使用HTTPS协议部署"
        DOMAIN="${DOMAIN}"
    else
        log "使用HTTP协议部署"
        DOMAIN="localhost"
    fi
    
    log "目标域名: $DOMAIN"
}

# 构建和启动服务
build_and_start() {
    local env_type=$1
    
    log "开始构建和启动${env_type}环境服务..."
    
    # 设置环境变量
    export $(grep -v "^#" .env.${env_type} | xargs)
    
    # 停止现有服务
    log "停止现有服务..."
    docker-compose down || true
    
    # 清理旧镜像
    log "清理旧镜像..."
    docker system prune -f
    
    # 构建新镜像
    log "构建Docker镜像..."
    docker-compose build --no-cache
    
    # 启动服务
    log "启动${env_type}环境服务..."
    docker-compose up -d
    
    log "${env_type}环境服务启动完成"
}

# 启动生产环境
start_production() {
    log "开始Soluna项目生产环境部署..."
    check_docker
    create_directories
    check_env_files "production"
    check_network "production"
    build_and_start "production"
    check_status "production"
    show_info "production"
}

# 启动开发环境
start_dev() {
    log "开始Soluna项目开发环境部署..."
    check_docker
    create_directories
    check_env_files "development"
    check_network "development"
    
    # 设置环境变量
    export $(grep -v "^#" .env.development | xargs)
    docker-compose -f docker-compose.dev.yml up -d --build
    
    log "开发环境启动完成！"
    check_status "development"
    show_info "development"
}

# 停止所有服务
stop_services() {
    log "正在停止所有Soluna服务..."
    
    # 停止所有容器
    docker-compose down 2>/dev/null || true
    docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
    
    # 可选：清理未使用的镜像和卷
    read -p "是否清理未使用的Docker镜像和卷？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "清理未使用的资源..."
        docker system prune -f
        docker volume prune -f
        log "资源清理完成"
    fi
    
    log "所有服务已停止"
}

# 重启服务
restart_services() {
    local env_type=${1:-production}
    
    log "正在重启${env_type}环境服务..."
    
    # 停止服务
    docker-compose down || true
    
    # 重新构建和启动
    build_and_start "$env_type"
    
    log "${env_type}环境服务重启完成"
}

# 检查服务状态
check_status() {
    local env_type=${1:-production}
    
    log "检查${env_type}环境服务状态..."
    
    # 等待服务启动
    sleep 5
    
    # 检查容器状态
    if [[ "$env_type" == "development" ]]; then
        docker-compose -f docker-compose.dev.yml ps
    else
        docker-compose ps
    fi
    
    # 检查健康状态
    log "检查健康状态..."
    for service in soluna-web soluna-api soluna-scheduler; do
        if [[ "$env_type" == "development" ]]; then
            status=$(docker-compose -f docker-compose.dev.yml ps | grep -q "$service.*Up" && echo "正常" || echo "异常")
        else
            status=$(docker-compose ps | grep -q "$service.*Up" && echo "正常" || echo "异常")
        fi
        
        if [[ "$status" == "正常" ]]; then
            log "$service 服务运行正常"
        else
            error "$service 服务未正常运行"
        fi
    done
}

# 显示访问信息
show_info() {
    local env_type=$1
    
    if [[ "$env_type" == "development" ]]; then
        DOMAIN="localhost"
        PROTOCOL="http"
        WEB_PORT=3001
        API_PORT=8001
    else
        DOMAIN="${DOMAIN}"
        PROTOCOL="https"
        WEB_PORT=443
        API_PORT=443
    fi
    
    echo ""
    echo "========================================"
    echo "Soluna项目部署信息"
    echo "========================================"
    echo "环境: $env_type"
    echo "域名: ${PROTOCOL}://${DOMAIN}"
    echo ""
    
    if [[ "$env_type" == "development" ]]; then
        echo "服务地址:"
        echo "- 前端: http://localhost:3001"
        echo "- API: http://localhost:8001"
    else
        echo "服务地址:"
        echo "- 前端: https://${DOMAIN}"
        echo "- API: https://${DOMAIN}/api"
    fi
    
    echo ""
    echo "Docker命令:"
    if [[ "$env_type" == "development" ]]; then
        echo "- 查看日志: docker-compose -f docker-compose.dev.yml logs -f [service]"
        echo "- 停止服务: docker-compose -f docker-compose.dev.yml down"
    else
        echo "- 查看日志: docker-compose logs -f [service]"
        echo "- 停止服务: ./deploy.sh stop"
    fi
    echo "========================================"
}

# 显示帮助信息
show_help() {
    echo "Soluna项目部署脚本"
    echo ""
    echo "使用方法:"
    echo "  ./deploy.sh [命令] [环境]"
    echo ""
    echo "命令:"
    echo "  start       启动服务 (默认命令)"
    echo "  stop        停止所有服务"
    echo "  restart     重启服务"
    echo "  status      查看服务状态"
    echo "  help        显示此帮助信息"
    echo ""
    echo "环境:"
    echo "  production  生产环境 (默认)"
    echo "  development 开发环境"
    echo ""
    echo "配置文件:"
    echo "  .env.production   - 生产环境配置"
    echo "  .env.development  - 开发环境配置"
    echo ""
    echo "示例:"
    echo "  ./deploy.sh start production"
    echo "  ./deploy.sh start development"
    echo "  ./deploy.sh stop"
    echo "  ./deploy.sh restart production"
    echo "  ./deploy.sh status"
}

# 主执行逻辑
main() {
    local command=${1:-start}
    local env_type=${2:-production}
    
    case "$command" in
        "start")
            if [[ "$env_type" == "development" ]]; then
                start_dev
            else
                start_production
            fi
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services "$env_type"
            ;;
        "status")
            check_status "$env_type"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            # 兼容旧用法
            if [[ "$command" == "production" || "$command" == "development" ]]; then
                if [[ "$command" == "development" ]]; then
                    start_dev
                else
                    start_production
                fi
            else
                error "未知命令: $command"
                show_help
                exit 1
            fi
            ;;
    esac
}

# 执行主函数
main "$@"