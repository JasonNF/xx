#!/bin/bash

#===============================================
# 检查已注册的命令
#===============================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  检查已注册的命令${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

HANDLERS_DIR="/opt/xiuxian-bot/src/bot/handlers"

echo -e "${YELLOW}1. 查找所有CommandHandler注册...${NC}"
echo ""

# 查找所有CommandHandler行（排除中文和chinese_commands.py）
echo "已注册的英文命令:"
grep -rh "CommandHandler(" "$HANDLERS_DIR" \
    --include="*.py" \
    --exclude="chinese_commands.py" \
    | grep -v "^#" \
    | grep -v "[\u4e00-\u9fff]" \
    | sed 's/.*CommandHandler("\([^"]*\)".*/  \1/' \
    | sort -u

echo ""
echo -e "${YELLOW}2. 检查中文命令模块...${NC}"

if [ -f "$HANDLERS_DIR/chinese_commands.py" ]; then
    echo -e "${GREEN}✓ 中文命令模块存在${NC}"

    # 统计中文命令数量
    cmd_count=$(grep -c '^\s*".' "$HANDLERS_DIR/chinese_commands.py" || echo 0)
    echo "  中文命令数量: $cmd_count"
else
    echo -e "${RED}✗ 中文命令模块不存在${NC}"
fi

echo ""
echo -e "${YELLOW}3. 检查main.py集成...${NC}"

if grep -q "from bot.handlers.chinese_commands import setup_chinese_commands" /opt/xiuxian-bot/src/bot/main.py; then
    echo -e "${GREEN}✓ 中文命令已集成到main.py${NC}"
else
    echo -e "${RED}✗ 中文命令未集成到main.py${NC}"
fi

echo ""
echo -e "${YELLOW}4. 查看最近日志...${NC}"
journalctl -u xiuxian-bot -n 30 --no-pager | grep -E "已加载|中文命令|CommandHandler|注册|ERROR" | tail -20

echo ""
