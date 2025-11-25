#!/bin/bash

#===============================================
# 调试命令处理器注册问题
#===============================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  调试命令处理器${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

HANDLERS_DIR="/opt/xiuxian-bot/src/bot/handlers"

echo -e "${YELLOW}1. 检查start.py中的命令注册...${NC}"
echo ""

if [ -f "$HANDLERS_DIR/start.py" ]; then
    echo "查找CommandHandler注册:"
    grep -n "CommandHandler" "$HANDLERS_DIR/start.py" | head -20
    echo ""

    echo "查找register_handlers函数:"
    grep -n "def register_handlers" "$HANDLERS_DIR/start.py"
    echo ""

    echo "查找函数定义:"
    grep -n "^def.*command" "$HANDLERS_DIR/start.py" | head -10
else
    echo -e "${RED}✗ start.py 不存在${NC}"
fi

echo ""
echo -e "${YELLOW}2. 检查main.py中的处理器注册...${NC}"
echo ""

MAIN_FILE="/opt/xiuxian-bot/src/bot/main.py"

if [ -f "$MAIN_FILE" ]; then
    echo "查找处理器注册调用:"
    grep -n "register_handlers" "$MAIN_FILE"
    echo ""

    echo "查找import语句:"
    grep -n "from bot.handlers" "$MAIN_FILE" | head -10
else
    echo -e "${RED}✗ main.py 不存在${NC}"
fi

echo ""
echo -e "${YELLOW}3. 查看所有handler文件...${NC}"
echo ""
ls -lh "$HANDLERS_DIR"/*.py

echo ""
echo -e "${YELLOW}4. 测试Python导入...${NC}"
echo ""

sudo -u xiuxian /opt/xiuxian-bot/venv/bin/python << 'PYEOF'
import sys
sys.path.insert(0, '/opt/xiuxian-bot/src')

try:
    from bot.handlers import start
    print("✓ start模块导入成功")

    # 检查是否有register_handlers函数
    if hasattr(start, 'register_handlers'):
        print("✓ register_handlers函数存在")
    else:
        print("✗ register_handlers函数不存在")
        print("可用函数:", [x for x in dir(start) if not x.startswith('_')])

except Exception as e:
    print(f"✗ 导入失败: {e}")
PYEOF

echo ""
echo -e "${YELLOW}5. 查看启动日志中的注册信息...${NC}"
echo ""
journalctl -u xiuxian-bot --since "5 minutes ago" | grep -E "注册|register|handler|Handler" | head -20

echo ""
