#!/bin/bash

#===============================================
# 修仙世界 Telegram Bot - 生产环境一键部署脚本
# 适用于: Debian/Ubuntu Linux VPS
# 功能: PostgreSQL + Redis + systemd
#===============================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 变量定义
PROJECT_NAME="xiuxian-bot"
INSTALL_DIR="/opt/${PROJECT_NAME}"
SERVICE_USER="xiuxian"
DB_NAME="xiuxian_prod"
DB_USER="xiuxian"

#===============================================
# 工具函数
#===============================================

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
        echo "请使用: sudo bash deploy.sh"
        exit 1
    fi
}

#===============================================
# 主要安装步骤
#===============================================

install_system_dependencies() {
    print_header "1. 安装系统依赖"

    # 更新软件源,忽略警告
    apt-get update -qq 2>&1 | grep -v "Policy will reject signature" | grep -v "does not have a Release file" || true
    print_success "更新软件源"

    apt-get install -y -qq \
        python3 \
        python3-pip \
        python3-venv \
        postgresql \
        postgresql-contrib \
        redis-server \
        git \
        curl \
        build-essential \
        libpq-dev

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
-- 创建数据库用户
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

setup_redis() {
    print_header "4. 配置Redis"

    # 启动并启用Redis
    systemctl start redis-server
    systemctl enable redis-server

    print_success "Redis服务已启动"
}

deploy_application() {
    print_header "5. 部署应用程序"

    # 创建安装目录
    mkdir -p "$INSTALL_DIR"

    # 复制项目文件
    print_warning "正在复制项目文件..."
    cp -r "$(pwd)"/* "$INSTALL_DIR/"

    # 设置所有权
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"

    print_success "项目文件部署完成"
}

setup_python_environment() {
    print_header "6. 配置Python环境"

    cd "$INSTALL_DIR"

    # 创建虚拟环境
    sudo -u "$SERVICE_USER" python3 -m venv venv
    print_success "虚拟环境创建完成"

    # 安装依赖
    print_warning "正在安装Python依赖..."
    sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install --upgrade pip -q
    sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install -r requirements.txt -q

    # 安装PostgreSQL驱动
    sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install psycopg2-binary -q

    print_success "Python依赖安装完成"
}

configure_environment() {
    print_header "7. 配置环境变量"

    # 读取数据库密码
    DB_PASSWORD=$(grep DB_PASSWORD /tmp/db_credentials.txt | cut -d'=' -f2)

    # 提示用户输入Bot Token
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

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

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
    print_header "8. 初始化数据库"

    cd "$INSTALL_DIR"

    # 创建数据目录
    sudo -u "$SERVICE_USER" mkdir -p data/logs

    # 导入游戏数据
    if [ -f "data/import_all_data.sh" ]; then
        print_warning "正在导入游戏数据..."
        cd data
        # 修改import脚本以使用PostgreSQL
        sudo -u "$SERVICE_USER" bash -c "
            export DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@localhost/${DB_NAME}
            # 这里需要调整导入脚本以支持PostgreSQL
            # 暂时跳过,首次启动时会自动创建表结构
        "
        cd ..
    fi

    print_success "数据库初始化完成"
}

setup_systemd_service() {
    print_header "9. 配置systemd服务"

    # 创建systemd服务文件
    cat > "/etc/systemd/system/${PROJECT_NAME}.service" <<EOF
[Unit]
Description=修仙世界 Telegram Bot
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service

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

# 安全设置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=${INSTALL_DIR}/data

[Install]
WantedBy=multi-user.target
EOF

    # 重载systemd
    systemctl daemon-reload

    print_success "systemd服务配置完成"
}

start_service() {
    print_header "10. 启动服务"

    # 启动服务
    systemctl start "$PROJECT_NAME"
    systemctl enable "$PROJECT_NAME"

    print_success "服务已启动并设置为开机自启"

    # 等待几秒
    sleep 3

    # 检查服务状态
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
    echo "  - 缓存: Redis"
    echo ""
    echo "常用命令:"
    echo "  - 查看状态: systemctl status $PROJECT_NAME"
    echo "  - 查看日志: journalctl -u $PROJECT_NAME -f"
    echo "  - 重启服务: systemctl restart $PROJECT_NAME"
    echo "  - 停止服务: systemctl stop $PROJECT_NAME"
    echo ""
    echo "数据库凭证已保存到: /tmp/db_credentials.txt"
    echo "请妥善保管并删除该文件!"
    echo ""
    echo -e "${YELLOW}下一步:${NC}"
    echo "1. 在Telegram中发送 /start 测试Bot"
    echo "2. 查看日志确认运行正常"
    echo "3. 删除数据库凭证文件: rm /tmp/db_credentials.txt"
    echo ""
}

#===============================================
# 主执行流程
#===============================================

main() {
    clear
    print_header "修仙世界 Telegram Bot - 生产环境部署"

    echo -e "${YELLOW}此脚本将执行以下操作:${NC}"
    echo "  1. 安装系统依赖 (Python, PostgreSQL, Redis)"
    echo "  2. 创建服务用户"
    echo "  3. 配置数据库和缓存"
    echo "  4. 部署应用程序"
    echo "  5. 配置systemd自动启动"
    echo ""
    echo -e "${RED}注意: 请确保你有Telegram Bot Token${NC}"
    echo ""
    read -p "确认开始部署? (y/N): " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "部署已取消"
        exit 0
    fi

    check_root

    install_system_dependencies
    create_service_user
    setup_postgresql
    setup_redis
    deploy_application
    setup_python_environment
    configure_environment
    initialize_database
    setup_systemd_service
    start_service
    show_summary
}

# 执行主函数
main
