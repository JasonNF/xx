#!/bin/bash

#===============================================
# 最终修复：恢复英文CommandHandler
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  恢复英文CommandHandler${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

START_FILE="/opt/xiuxian-bot/src/bot/handlers/start.py"

echo -e "${YELLOW}1. 备份start.py...${NC}"
cp "$START_FILE" "${START_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
echo -e "${GREEN}✓ 已备份${NC}"

echo ""
echo -e "${YELLOW}2. 添加英文CommandHandler...${NC}"

sudo -u xiuxian /opt/xiuxian-bot/venv/bin/python3 << 'PYEOF'
start_file = '/opt/xiuxian-bot/src/bot/handlers/start.py'

with open(start_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
found_register = False

for i, line in enumerate(lines):
    new_lines.append(line)

    # 找到注册函数的文档字符串
    if found_register and '"""' in line and 'register_handlers' not in line:
        # 在文档字符串后添加英文handlers
        new_lines.append('    application.add_handler(CommandHandler("start", detect_spirit_root_command))\n')
        new_lines.append('    application.add_handler(CommandHandler("help", help_command))\n')
        new_lines.append('    application.add_handler(CommandHandler("info", status_command))\n')
        found_register = False
        continue

    if 'def register_handlers(application):' in line:
        found_register = True

with open(start_file, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('✓ 已添加以下英文CommandHandler:')
print('  - /start -> detect_spirit_root_command')
print('  - /help  -> help_command')
print('  - /info  -> status_command')
PYEOF

echo -e "${GREEN}✓ 修复完成${NC}"

echo ""
echo -e "${YELLOW}3. 验证修复结果...${NC}"
echo ""
grep -A 5 "def register_handlers" "$START_FILE"

echo ""
echo -e "${YELLOW}4. 重启服务...${NC}"

systemctl restart xiuxian-bot

sleep 5

if systemctl is-active --quiet xiuxian-bot; then
    echo -e "${GREEN}✓ 服务运行正常!${NC}"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  修复成功完成!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "🎮 现在可以测试命令了:"
    echo ""
    echo "  英文命令:"
    echo "    /start - 检测灵根"
    echo "    /help  - 查看帮助"
    echo "    /info  - 查看状态"
    echo ""
    echo "  中文命令:"
    echo "    .开始  - 检测灵根"
    echo "    .帮助  - 查看帮助"
    echo "    .状态  - 查看状态"
    echo ""

    echo "最近日志:"
    journalctl -u xiuxian-bot -n 15 --no-pager

else
    echo -e "${RED}✗ 服务启动失败${NC}"
    journalctl -u xiuxian-bot -n 30 --no-pager
    exit 1
fi

echo ""
echo "📊 实时监控: journalctl -u xiuxian-bot -f"
echo ""
