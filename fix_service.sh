#!/bin/bash

#===============================================
# 修复xiuxian-bot服务的模块路径问题
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  修复服务配置${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}需要root权限${NC}"
    exit 1
fi

PROJECT_NAME="xiuxian-bot"
INSTALL_DIR="/opt/${PROJECT_NAME}"
SERVICE_USER="xiuxian"

# 1. 停止服务
echo -e "${YELLOW}1. 停止服务...${NC}"
systemctl stop "$PROJECT_NAME"
echo -e "${GREEN}✓ 已停止${NC}"

# 2. 更新systemd服务配置
echo ""
echo -e "${YELLOW}2. 更新systemd配置...${NC}"

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
Environment="PYTHONPATH=${INSTALL_DIR}/src"
ExecStart=${INSTALL_DIR}/venv/bin/python -m bot.main
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

echo -e "${GREEN}✓ 配置已更新${NC}"

# 3. 重新加载systemd
echo ""
echo -e "${YELLOW}3. 重新加载systemd...${NC}"
systemctl daemon-reload
echo -e "${GREEN}✓ 已重载${NC}"

# 4. 检查Python路径
echo ""
echo -e "${YELLOW}4. 验证Python模块...${NC}"

cd "$INSTALL_DIR"
if sudo -u "$SERVICE_USER" PYTHONPATH="$INSTALL_DIR/src" "$INSTALL_DIR/venv/bin/python" -c "from bot.config import settings" 2>/dev/null; then
    echo -e "${GREEN}✓ Python模块路径正确${NC}"
else
    echo -e "${RED}✗ Python模块导入失败${NC}"
    echo ""
    echo "尝试诊断:"
    sudo -u "$SERVICE_USER" PYTHONPATH="$INSTALL_DIR/src" "$INSTALL_DIR/venv/bin/python" -c "from bot.config import settings" 2>&1 || true
    echo ""
    echo "检查文件结构:"
    ls -la "$INSTALL_DIR/src/bot/" | head -10
fi

# 5. 启动服务
echo ""
echo -e "${YELLOW}5. 启动服务...${NC}"

if systemctl start "$PROJECT_NAME"; then
    echo -e "${GREEN}✓ 服务已启动${NC}"

    sleep 3

    if systemctl is-active --quiet "$PROJECT_NAME"; then
        echo -e "${GREEN}✓ 服务运行正常${NC}"
    else
        echo -e "${RED}✗ 服务启动失败${NC}"
    fi
else
    echo -e "${RED}✗ 启动失败${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  修复完成${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "查看服务状态:"
systemctl status "$PROJECT_NAME" --no-pager -l | head -15
echo ""
echo "查看实时日志:"
echo "  journalctl -u $PROJECT_NAME -f"
echo ""
