#!/bin/bash

#===============================================
# 禁用PostgreSQL SSL以避免证书权限问题
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  禁用PostgreSQL SSL${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

ENV_FILE="/opt/xiuxian-bot/.env"

echo -e "${YELLOW}1. 备份配置文件...${NC}"
cp "$ENV_FILE" "${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
echo -e "${GREEN}✓ 已备份${NC}"

echo ""
echo -e "${YELLOW}2. 修改DATABASE_URL...${NC}"

# 读取当前的DATABASE_URL
CURRENT_URL=$(grep "^DATABASE_URL=" "$ENV_FILE" | cut -d'=' -f2-)

echo "当前URL: $CURRENT_URL"

# 检查是否已经有sslmode参数
if echo "$CURRENT_URL" | grep -q "sslmode"; then
    echo "  URL中已有sslmode参数,替换为disable..."
    NEW_URL=$(echo "$CURRENT_URL" | sed 's/sslmode=[^&]*/sslmode=disable/')
else
    echo "  添加sslmode=disable参数..."
    # 检查URL中是否已有?参数
    if echo "$CURRENT_URL" | grep -q "?"; then
        # 已有参数,用&连接
        NEW_URL="${CURRENT_URL}&sslmode=disable"
    else
        # 没有参数,用?连接
        NEW_URL="${CURRENT_URL}?sslmode=disable"
    fi
fi

echo "新URL: $NEW_URL"

# 替换配置文件中的DATABASE_URL
sed -i "s|^DATABASE_URL=.*|DATABASE_URL=${NEW_URL}|" "$ENV_FILE"

echo -e "${GREEN}✓ DATABASE_URL已更新${NC}"

echo ""
echo -e "${YELLOW}3. 删除空的.postgresql目录...${NC}"
if [ -d "/home/xiuxian/.postgresql" ]; then
    # 检查目录是否为空
    if [ -z "$(ls -A /home/xiuxian/.postgresql)" ]; then
        rm -rf /home/xiuxian/.postgresql
        echo -e "${GREEN}✓ 已删除空目录${NC}"
    else
        echo -e "${YELLOW}⚠ 目录不为空,保留${NC}"
    fi
else
    echo -e "${GREEN}✓ 目录不存在,无需删除${NC}"
fi

echo ""
echo -e "${YELLOW}4. 验证配置...${NC}"
grep "^DATABASE_URL=" "$ENV_FILE"

echo ""
echo -e "${YELLOW}5. 重启服务...${NC}"

systemctl restart xiuxian-bot

sleep 5

if systemctl is-active --quiet xiuxian-bot; then
    echo -e "${GREEN}✓ 服务运行正常!${NC}"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  修复完成!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "✅ Bot成功启动!"
    echo ""
    echo "🎮 测试命令 (在Telegram中发送):"
    echo "  中文: .开始  .修炼  .战斗  .背包"
    echo "  英文: /start /cultivate /battle /bag"
    echo ""

    echo -e "${YELLOW}最近日志:${NC}"
    journalctl -u xiuxian-bot -n 20 --no-pager

else
    echo -e "${RED}✗ 服务启动失败${NC}"
    echo ""
    echo "详细日志:"
    journalctl -u xiuxian-bot -n 50 --no-pager
    exit 1
fi

echo ""
echo "📊 实时监控: journalctl -u xiuxian-bot -f"
echo ""
