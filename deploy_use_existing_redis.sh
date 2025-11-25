#!/bin/bash

#===============================================
# 使用现有Redis服务的部署脚本
# 适用于服务器已有Redis的情况
#===============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 变量定义
PROJECT_NAME="xiuxian-bot"
INSTALL_DIR="/opt/${PROJECT_NAME}"
SERVICE_USER="xiuxian"
DB_NAME="xiuxian_prod"
DB_USER="xiuxian"

print_header() {
    echo ""
    echo -e "${BLUE}=========================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}=========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "此脚本需要root权限运行"
        echo "请使用: sudo bash deploy_use_existing_redis.sh"
        exit 1
    fi
}

detect_redis() {
    print_header "检测Redis服务"

    # 检测Redis是否运行
    if pgrep -x "redis-server" > /dev/null; then
        print_success "检测到Redis服务正在运行"

        # 尝试不同的端口
        for port in 6379 6380 6381 6382; do
            if redis-cli -p $port ping &>/dev/null | grep -q "PONG"; then
                REDIS_PORT=$port
                print_success "Redis运行在端口: $REDIS_PORT"
                break
            fi
        done

        if [ -z "$REDIS_PORT" ]; then
            print_warning "无法连接到Redis,将使用无缓存模式"
            USE_REDIS="no"
        else
            USE_REDIS="yes"
        fi
    else
        print_warning "未检测到Redis服务,将使用无缓存模式"
        USE_REDIS="no"
    fi

    echo ""
    echo -e "${YELLOW}Redis配置:${NC}"
    if [ "$USE_REDIS" = "yes" ]; then
        echo "  - 使用现有Redis: 是"
        echo "  - Redis端口: $REDIS_PORT"
        echo "  - Redis数据库: 1 (避免冲突)"
    else
        echo "  - 使用Redis: 否 (不影响核心功能)"
    fi
    echo ""

    read -p "确认继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
}

install_system_dependencies() {
    print_header "1. 安装系统依赖"

    apt-get update -qq 2>&1 | grep -v "Policy will reject signature" | grep -v "does not have a Release file" || true
    print_success "更新软件源"

    apt-get install -y -qq \
        python3 \
        python3-pip \
        python3-venv \
        postgresql \
        postgresql-contrib \
        git \
        curl \
        build-essential \
        libpq-dev

    # 如果需要Redis但没安装redis-cli
    if [ "$USE_REDIS" = "yes" ]; then
        if ! command -v redis-cli &> /dev/null; then
            apt-get install -y -qq redis-tools
            print_success "已安装redis-tools"
        fi
    fi

    print_success "系统依赖安装完成"
}

create_service_user() {
    print_header "2. 创建服务用户"

    if id "$SERVICE_USER" &>/dev/null; then
        print_warning "用户 $SERVICE_USER 已存在"
    else
        useradd -r -m -s /bin/bash "$SERVICE_USER"
        print_success "创建用户: $SERVICE_USER"
    fi
}

setup_postgresql() {
    print_header "3. 配置PostgreSQL数据库"

    # 生成随机密码
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

    # 创建数据库和用户
    sudo -u postgres psql <<EOF
-- 删除已存在的数据库和用户(如果有)
DROP DATABASE IF EXISTS ${DB_NAME};
DROP USER IF EXISTS ${DB_USER};

-- 创建新的数据库用户
CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';

-- 创建数据库
CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};

-- 授权
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};

\q
EOF

    print_success "PostgreSQL数据库配置完成"
    print_success "数据库: ${DB_NAME}"
    print_success "用户: ${DB_USER}"

    # 保存数据库凭证
    echo "DB_PASSWORD=${DB_PASSWORD}" > /tmp/db_credentials.txt
    chmod 600 /tmp/db_credentials.txt
}

deploy_application() {
    print_header "4. 部署应用程序"

    mkdir -p "$INSTALL_DIR"
    cp -r "$(pwd)"/* "$INSTALL_DIR/"
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"

    print_success "项目文件部署完成"
}

setup_python_environment() {
    print_header "5. 配置Python环境"

    cd "$INSTALL_DIR"

    sudo -u "$SERVICE_USER" python3 -m venv venv
    print_success "虚拟环境创建完成"

    print_warning "正在安装Python依赖..."
    sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install --upgrade pip -q
    sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install -r requirements.txt -q
    sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install psycopg2-binary -q

    print_success "Python依赖安装完成"
}

configure_environment() {
    print_header "6. 配置环境变量"

    DB_PASSWORD=$(grep DB_PASSWORD /tmp/db_credentials.txt | cut -d'=' -f2)

    echo ""
    echo -e "${YELLOW}请输入你的Telegram Bot Token:${NC}"
    read -p "Bot Token: " BOT_TOKEN

    echo ""
    echo -e "${YELLOW}请输入管理员Telegram ID (多个用逗号分隔):${NC}"
    read -p "Admin IDs: " ADMIN_IDS

    # 创建.env文件
    cat > "$INSTALL_DIR/.env" <<EOF
# Telegram Bot配置
BOT_TOKEN=${BOT_TOKEN}
BOT_USERNAME=your_bot_username

# 数据库配置
DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@localhost/${DB_NAME}

EOF

    # 根据是否使用Redis添加配置
    if [ "$USE_REDIS" = "yes" ]; then
        cat >> "$INSTALL_DIR/.env" <<EOF
# Redis配置 (使用现有服务)
REDIS_HOST=localhost
REDIS_PORT=${REDIS_PORT}
REDIS_DB=1
REDIS_PASSWORD=

EOF
    else
        cat >> "$INSTALL_DIR/.env" <<EOF
# Redis配置 (已禁用)
# REDIS_HOST=localhost
# REDIS_PORT=6379
# REDIS_DB=0
# REDIS_PASSWORD=

EOF
    fi

    cat >> "$INSTALL_DIR/.env" <<EOF
# 游戏配置
GAME_NAME=修仙世界
GAME_VERSION=1.0.0

# 修炼配置
BASE_CULTIVATION_RATE=100
BREAKTHROUGH_BASE_CHANCE=0.7

# 战斗配置
PVE_COOLDOWN=300
PVP_COOLDOWN=600

# 经济配置
DAILY_SIGN_REWARD=1000
NEWBIE_GIFT=5000

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=./data/logs/xiuxian.log

# 管理员Telegram ID
ADMIN_IDS=${ADMIN_IDS}
EOF

    chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/.env"
    chmod 600 "$INSTALL_DIR/.env"

    print_success "环境变量配置完成"
}

initialize_database() {
    print_header "7. 初始化数据库"

    cd "$INSTALL_DIR"
    sudo -u "$SERVICE_USER" mkdir -p data/logs

    print_success "数据库将在首次启动时自动初始化"
}

setup_systemd_service() {
    print_header "8. 配置systemd服务"

    cat > "/etc/systemd/system/${PROJECT_NAME}.service" <<EOF
[Unit]
Description=修仙世界 Telegram Bot
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=${SERVICE_USER}
Group=${SERVICE_USER}
WorkingDirectory=${INSTALL_DIR}
Environment="PATH=${INSTALL_DIR}/venv/bin"
ExecStart=${INSTALL_DIR}/venv/bin/python -m src.bot.main
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=${INSTALL_DIR}/data

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    print_success "systemd服务配置完成"
}

start_service() {
    print_header "9. 启动服务"

    systemctl start "$PROJECT_NAME"
    systemctl enable "$PROJECT_NAME"

    print_success "服务已启动并设置为开机自启"

    sleep 3

    if systemctl is-active --quiet "$PROJECT_NAME"; then
        print_success "服务运行正常"
    else
        print_error "服务启动失败,请检查日志"
        echo "查看日志: journalctl -u $PROJECT_NAME -f"
    fi
}

show_summary() {
    print_header "部署完成!"

    echo -e "${GREEN}✓ 部署成功!${NC}"
    echo ""
    echo "服务信息:"
    echo "  - 服务名称: $PROJECT_NAME"
    echo "  - 安装目录: $INSTALL_DIR"
    echo "  - 数据库: PostgreSQL ($DB_NAME)"

    if [ "$USE_REDIS" = "yes" ]; then
        echo "  - 缓存: Redis (端口 $REDIS_PORT, DB 1)"
    else
        echo "  - 缓存: 无 (不影响核心功能)"
    fi

    echo ""
    echo "常用命令:"
    echo "  - 查看状态: systemctl status $PROJECT_NAME"
    echo "  - 查看日志: journalctl -u $PROJECT_NAME -f"
    echo "  - 重启服务: systemctl restart $PROJECT_NAME"
    echo ""
    echo "数据库凭证: /tmp/db_credentials.txt (请删除)"
    echo ""
}

main() {
    clear
    print_header "修仙世界 Telegram Bot - 智能部署"

    check_root
    detect_redis
    install_system_dependencies
    create_service_user
    setup_postgresql
    deploy_application
    setup_python_environment
    configure_environment
    initialize_database
    setup_systemd_service
    start_service
    show_summary
}

main
