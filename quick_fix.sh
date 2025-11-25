#!/bin/bash

#===============================================
# 快速修复: 安装依赖并启动
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}快速修复...${NC}"

INSTALL_DIR="/opt/xiuxian-bot"

# 安装缺失的依赖
echo -e "${YELLOW}安装依赖...${NC}"
sudo -u xiuxian "$INSTALL_DIR/venv/bin/pip" install apscheduler python-dotenv --quiet --no-warn-script-location

echo -e "${GREEN}✓ 依赖已安装${NC}"

# 重启服务
echo -e "${YELLOW}重启服务...${NC}"
systemctl restart xiuxian-bot

sleep 5

if systemctl is-active --quiet xiuxian-bot; then
    echo -e "${GREEN}✓ 服务运行正常!${NC}"
    echo ""
    echo "✅ Bot已启动!"
    echo ""
    echo "🎮 测试命令:"
    echo "  中文: .开始 .修炼 .战斗"
    echo "  英文: /start /cultivate /battle"
    echo ""
    journalctl -u xiuxian-bot -n 15 --no-pager
else
    echo -e "${RED}✗ 服务启动失败${NC}"
    journalctl -u xiuxian-bot -n 30 --no-pager
    exit 1
fi
