#!/bin/bash

#===============================================
# 修复status_command中不存在的属性引用
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  修复status_command属性引用${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

START_FILE="/opt/xiuxian-bot/src/bot/handlers/start.py"

echo -e "${YELLOW}1. 备份start.py...${NC}"
cp "$START_FILE" "${START_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
echo -e "${GREEN}✓ 已备份${NC}"

echo ""
echo -e "${YELLOW}2. 修复status_command函数...${NC}"

sudo -u xiuxian /opt/xiuxian-bot/venv/bin/python3 << 'PYEOF'
import re

start_file = '/opt/xiuxian-bot/src/bot/handlers/start.py'

with open(start_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 新的status_command实现
new_status_command = '''async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /状态 命令 - 显示玩家当前状态"""
    user = update.effective_user

    async with get_db() as db:
        result = await db.execute(
            select(Player)
            .where(Player.telegram_id == user.id)
            .options(selectinload(Player.spirit_root))
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text(
                "❌ 你还没有开始修仙之旅\\n"
                "请先使用 /start 命令检测灵根"
            )
            return

        status_text = f"""
👤 **{player.nickname}**

🌟 **境界**: {player.full_realm_name}
📊 **修为**: {player.cultivation_exp:,}/{player.next_realm_exp:,}

💚 **生命**: {player.hp}/{player.max_hp}
💙 **灵力**: {player.spiritual_power}/{player.max_spiritual_power}

⚔️ **攻击**: {player.attack}
🛡️ **防御**: {player.defense}
⚡ **速度**: {player.speed}
💥 **暴击率**: {player.crit_rate * 100:.1f}%
💫 **暴击伤害**: {player.crit_damage * 100:.1f}%

🧠 **悟性**: {player.comprehension}
🔮 **神识**: {player.divine_sense}/{player.max_divine_sense}

💎 **灵石**: {player.spirit_stones:,}
🏆 **贡献**: {player.contribution:,}

⏳ **年龄/寿元**: {player.age}/{player.lifespan}
"""

        if player.spirit_root:
            status_text += f"\\n🌈 **灵根**: {player.spirit_root.display_name}"

        if player.golden_core_quality:
            status_text += f"\\n⚗️ **金丹品质**: {player.golden_core_quality}"

        await update.message.reply_text(status_text, parse_mode="Markdown")
'''

# 找到并替换status_command函数
pattern = r'async def status_command\(.*?\):.*?(?=\n(?:async )?def |$)'
content = re.sub(pattern, new_status_command, content, flags=re.DOTALL)

with open(start_file, 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ 已修复status_command函数')
print('  移除的不存在属性: root_bone, combat_power, total_battles, total_wins')
print('  添加了eager loading: selectinload(Player.spirit_root)')
PYEOF

echo -e "${GREEN}✓ 修复完成${NC}"

echo ""
echo -e "${YELLOW}3. 重启服务...${NC}"

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
    echo "  .状态 - 查看个人状态（现在应该正常工作）"
    echo "  /info - 查看个人状态（英文命令）"
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
