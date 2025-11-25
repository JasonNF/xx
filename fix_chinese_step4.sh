#!/bin/bash

#===============================================
# 快速修复: 直接删除所有中文CommandHandler
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  快速修复中文CommandHandler${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

INSTALL_DIR="/opt/xiuxian-bot"
HANDLERS_DIR="$INSTALL_DIR/src/bot/handlers"

echo -e "${YELLOW}1. 查找包含中文CommandHandler的文件...${NC}"

# 查找所有包含中文CommandHandler的文件
FILES=$(find "$HANDLERS_DIR" -name "*.py" -not -name "chinese_commands.py" -type f 2>/dev/null)

echo "找到以下文件:"
echo "$FILES"
echo ""

echo -e "${YELLOW}2. 删除中文CommandHandler行...${NC}"

# 使用更简单的方法: 直接用sed删除包含中文字符的CommandHandler行
for file in $FILES; do
    if [ -f "$file" ]; then
        echo "  处理: $(basename $file)"

        # 删除所有包含中文的CommandHandler行
        # 使用更可靠的模式匹配
        sed -i '/CommandHandler.*[\u4e00-\u9fff]/d' "$file" 2>/dev/null || \
        sed -i '/CommandHandler("检测灵根/d; /CommandHandler("帮助/d; /CommandHandler("状态/d; /CommandHandler("修炼/d; /CommandHandler("收功/d; /CommandHandler("突破/d; /CommandHandler("战斗/d; /CommandHandler("背包/d; /CommandHandler("商店/d; /CommandHandler("宗门/d; /CommandHandler("排行榜/d; /CommandHandler("签到/d' "$file" 2>/dev/null || true
    fi
done

echo -e "${GREEN}✓ 已处理所有文件${NC}"

echo ""
echo -e "${YELLOW}3. 修正权限...${NC}"
chown -R xiuxian:xiuxian "$HANDLERS_DIR"
chown -R xiuxian:xiuxian "$INSTALL_DIR/src/bot/"
echo -e "${GREEN}✓ 权限已修正${NC}"

echo ""
echo -e "${YELLOW}4. 重启服务...${NC}"

systemctl restart xiuxian-bot

sleep 5

if systemctl is-active --quiet xiuxian-bot; then
    echo -e "${GREEN}✓ 服务运行正常!${NC}"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  修复完成!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "✅ Bot现在支持中文命令了!"
    echo ""
    echo "🎮 测试命令 (在Telegram中发送):"
    echo "  .开始"
    echo "  .帮助"
    echo "  .状态"
    echo ""
    echo "💡 英文命令仍然可用: /start /help /info"
    echo ""

    echo -e "${YELLOW}查看最近日志:${NC}"
    journalctl -u xiuxian-bot -n 15 --no-pager

else
    echo -e "${RED}✗ 服务启动失败${NC}"
    echo ""
    echo "详细日志:"
    journalctl -u xiuxian-bot -n 30 --no-pager
    exit 1
fi

echo ""
echo "📊 实时监控:"
echo "  journalctl -u xiuxian-bot -f"
echo ""
