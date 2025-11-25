#!/bin/bash

#===============================================
# 修复数据库eager loading问题
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  修复SQLAlchemy异步访问问题${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

PLAYER_SERVICE="/opt/xiuxian-bot/src/bot/services/player_service.py"

echo -e "${YELLOW}1. 添加eager loading到player查询...${NC}"

sudo -u xiuxian /opt/xiuxian-bot/venv/bin/python3 << 'PYEOF'
import re

player_service_file = '/opt/xiuxian-bot/src/bot/services/player_service.py'

with open(player_service_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 在import部分添加selectinload
if 'from sqlalchemy.orm import selectinload' not in content:
    content = re.sub(
        r'(from sqlalchemy\.ext\.asyncio import AsyncSession)',
        r'\1\nfrom sqlalchemy.orm import selectinload',
        content
    )

# 修改get_or_create_player中的查询，添加eager loading
old_query = r'result = await db\.execute\(\s*select\(Player\)\.where\(Player\.telegram_id == telegram_id\)\s*\)'

new_query = '''result = await db.execute(
            select(Player)
            .where(Player.telegram_id == telegram_id)
            .options(selectinload(Player.spirit_root))
        )'''

content = re.sub(old_query, new_query, content, flags=re.DOTALL)

with open(player_service_file, 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ 已添加 selectinload(Player.spirit_root)')
PYEOF

echo -e "${GREEN}✓ 修复完成${NC}"

echo ""
echo -e "${YELLOW}2. 重启服务...${NC}"

systemctl restart xiuxian-bot

sleep 5

if systemctl is-active --quiet xiuxian-bot; then
    echo -e "${GREEN}✓ 服务运行正常${NC}"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  修复成功！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "🎮 测试命令:"
    echo "  /start - 检测灵根（现在应该正常工作）"
    echo ""

else
    echo -e "${RED}✗ 服务启动失败${NC}"
    journalctl -u xiuxian-bot -n 30 --no-pager
    exit 1
fi

echo ""
