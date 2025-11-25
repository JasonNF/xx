#!/bin/bash

#===============================================
# 修复.env配置文件格式问题
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  修复配置文件${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}需要root权限${NC}"
    exit 1
fi

INSTALL_DIR="/opt/xiuxian-bot"
ENV_FILE="$INSTALL_DIR/.env"

# 1. 备份配置
echo -e "${YELLOW}1. 备份配置文件...${NC}"
cp "$ENV_FILE" "${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
echo -e "${GREEN}✓ 已备份${NC}"

# 2. 修复ADMIN_IDS格式
echo ""
echo -e "${YELLOW}2. 修复ADMIN_IDS格式...${NC}"

# 读取当前的ADMIN_IDS
CURRENT_ADMIN_IDS=$(grep "^ADMIN_IDS=" "$ENV_FILE" | cut -d'=' -f2)

echo "当前值: $CURRENT_ADMIN_IDS"

# 检查是否已经是列表格式
if [[ "$CURRENT_ADMIN_IDS" == "["* ]]; then
    echo -e "${GREEN}✓ ADMIN_IDS已经是列表格式${NC}"
else
    # 转换为列表格式
    # 如果有逗号,分割成多个元素
    if [[ "$CURRENT_ADMIN_IDS" == *","* ]]; then
        # 多个ID: 1234,5678 -> [1234,5678]
        NEW_ADMIN_IDS="[${CURRENT_ADMIN_IDS}]"
    else
        # 单个ID: 1234 -> [1234]
        NEW_ADMIN_IDS="[${CURRENT_ADMIN_IDS}]"
    fi

    echo "新值: $NEW_ADMIN_IDS"

    # 替换配置
    sed -i "s/^ADMIN_IDS=.*/ADMIN_IDS=${NEW_ADMIN_IDS}/" "$ENV_FILE"

    echo -e "${GREEN}✓ ADMIN_IDS格式已修复${NC}"
fi

# 3. 显示修复后的配置
echo ""
echo -e "${YELLOW}3. 验证配置...${NC}"
echo ""
echo "关键配置:"
grep "^BOT_TOKEN=" "$ENV_FILE" | head -c 50
echo "..."
grep "^DATABASE_URL=" "$ENV_FILE" | sed 's/:.*@/:***@/'
grep "^ADMIN_IDS=" "$ENV_FILE"
echo ""

# 4. 测试Python配置加载
echo -e "${YELLOW}4. 测试配置加载...${NC}"

cd "$INSTALL_DIR"
if sudo -u xiuxian PYTHONPATH="$INSTALL_DIR/src" "$INSTALL_DIR/venv/bin/python" -c "from bot.config import settings; print('Config loaded OK')" 2>&1; then
    echo -e "${GREEN}✓ 配置加载成功${NC}"
else
    echo -e "${RED}✗ 配置加载失败${NC}"
    echo ""
    echo "详细错误:"
    sudo -u xiuxian PYTHONPATH="$INSTALL_DIR/src" "$INSTALL_DIR/venv/bin/python" -c "from bot.config import settings" 2>&1 || true
    exit 1
fi

# 5. 重启服务
echo ""
echo -e "${YELLOW}5. 重启服务...${NC}"

systemctl restart xiuxian-bot

sleep 3

if systemctl is-active --quiet xiuxian-bot; then
    echo -e "${GREEN}✓ 服务运行正常!${NC}"
else
    echo -e "${RED}✗ 服务仍有问题${NC}"
    echo ""
    echo "查看日志:"
    journalctl -u xiuxian-bot -n 20 --no-pager
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  修复成功!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "服务状态:"
systemctl status xiuxian-bot --no-pager -l | head -10
echo ""
echo "实时日志:"
echo "  journalctl -u xiuxian-bot -f"
echo ""
