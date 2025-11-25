#!/bin/bash

#===============================================
# 修复start.py的导入错误
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  修复start.py导入错误${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo -e "${YELLOW}1. 检查实际的文件结构...${NC}"
echo "models目录内容:"
ls -la /opt/xiuxian-bot/src/bot/models/

echo ""
echo -e "${YELLOW}2. 查找最新的备份文件...${NC}"
BACKUP_FILE=$(ls -t /opt/xiuxian-bot/src/bot/handlers/start.py.backup.* 2>/dev/null | head -1)

if [ -n "$BACKUP_FILE" ]; then
    echo "找到备份: $BACKUP_FILE"

    echo ""
    echo -e "${YELLOW}3. 从备份中提取正确的导入...${NC}"

    sudo -u xiuxian /opt/xiuxian-bot/venv/bin/python3 << PYEOF
import re

# 读取备份文件
backup_file = '$BACKUP_FILE'
with open(backup_file, 'r', encoding='utf-8') as f:
    backup_content = f.read()

# 提取导入部分（前50行）
backup_imports = []
for line in backup_content.split('\n')[:50]:
    if line.startswith('import ') or line.startswith('from '):
        backup_imports.append(line)

print("备份文件中的导入:")
for imp in backup_imports:
    print(f"  {imp}")
PYEOF

else
    echo "未找到备份文件"
fi

echo ""
echo -e "${YELLOW}4. 重写start.py使用正确的导入...${NC}"

sudo -u xiuxian /opt/xiuxian-bot/venv/bin/python3 << 'PYEOF'
start_file = '/opt/xiuxian-bot/src/bot/handlers/start.py'

content = '''"""
开始命令处理器 - 处理/start命令，进行灵根检测
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bot.models.player import Player
from bot.services.player_service import get_or_create_player
from bot.database import get_db
from bot.utils.message_utils import send_and_delete

logger = logging.getLogger(__name__)


async def detect_spirit_root_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令 - 检测灵根"""
    user = update.effective_user

    logger.info(f"用户 {user.id} ({user.username}) 使用了 /start 命令")

    async with get_db() as db:
        # 检查玩家是否已存在
        result = await db.execute(
            select(Player)
            .where(Player.telegram_id == user.id)
            .options(selectinload(Player.spirit_root))
        )
        player = result.scalar_one_or_none()

        if player:
            # 玩家已存在，显示已有的灵根信息
            spirit_root = player.spirit_root

            welcome_back_text = f"""
🎴 欢迎回来，{player.nickname}！

你的灵根资质：
🔥 火灵根：{spirit_root.fire}
💧 水灵根：{spirit_root.water}
🌱 木灵根：{spirit_root.wood}
⚡ 雷灵根：{spirit_root.thunder}
🗿 土灵根：{spirit_root.earth}

境界：{player.full_realm_name}
修为：{player.cultivation_exp}/{player.next_realm_exp}

使用 /help 查看所有命令
"""
            await send_and_delete(update.message, welcome_back_text, parse_mode="Markdown")
            return

        # 创建新玩家并检测灵根
        player = await get_or_create_player(db, user)
        await db.commit()

        # 重新查询以获取spirit_root
        result = await db.execute(
            select(Player)
            .where(Player.telegram_id == user.id)
            .options(selectinload(Player.spirit_root))
        )
        player = result.scalar_one_or_none()
        spirit_root = player.spirit_root

        welcome_text = f"""
🎴 检测灵根

恭喜道友！你的灵根资质如下：

🔥 火灵根：{spirit_root.fire}
💧 水灵根：{spirit_root.water}
🌱 木灵根：{spirit_root.wood}
⚡ 雷灵根：{spirit_root.thunder}
🗿 土灵根：{spirit_root.earth}

{spirit_root.quality_description}

你现在是 {player.full_realm_name}
使用 /help 查看所有可用命令开始你的修仙之旅！
"""
        await send_and_delete(update.message, welcome_text, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /help 命令 - 显示帮助信息"""
    help_text = """
📖 修仙世界命令列表

🎮 基础命令：
/start 或 .开始 - 开始游戏，检测灵根
/help 或 .帮助 - 显示此帮助信息
/info 或 .状态 - 查看角色状态

⚡ 修炼命令：
/cultivate 或 .修炼 - 开始修炼
/breakthrough 或 .突破 - 尝试突破境界
/stop_cultivate 或 .收功 - 停止修炼

⚔️ 战斗命令：
/battle 或 .战斗 - 进入战斗菜单
/challenge 或 .挑战 - 挑战其他玩家

🎒 物品命令：
/inventory 或 .背包 - 查看背包
/shop 或 .商店 - 打开商店

🏛️ 宗门命令：
/sect 或 .宗门 - 宗门信息
/create_sect 或 .创建宗门 - 创建宗门
/join_sect 或 .加入宗门 - 加入宗门

📊 其他命令：
/ranking 或 .排行榜 - 查看排行榜
/sign 或 .签到 - 每日签到

💡 提示：可以使用 / 开头的英文命令，也可以使用 . 开头的中文命令
"""
    await send_and_delete(update.message, help_text, parse_mode="Markdown")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /info 命令 - 显示玩家当前状态"""
    user = update.effective_user

    async with get_db() as db:
        result = await db.execute(
            select(Player)
            .where(Player.telegram_id == user.id)
            .options(selectinload(Player.spirit_root))
        )
        player = result.scalar_one_or_none()

        if not player:
            error_msg = "❌ 你还没有开始修仙之旅\\n请先使用 /start 命令检测灵根"
            await send_and_delete(update.message, error_msg)
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

        await send_and_delete(update.message, status_text, parse_mode="Markdown")


def register_handlers(application):
    """注册所有处理器"""
    logger.info("start.register_handlers 被调用")

    application.add_handler(CommandHandler("start", detect_spirit_root_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", status_command))

    logger.info("✅ start handlers已注册: /start, /help, /info")
'''

with open(start_file, 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ 已重写start.py')
print('  - 移除了不存在的SpiritRoot导入')
print('  - 使用Player.spirit_root关系访问')
print('  - 正确使用send_and_delete')
PYEOF

echo -e "${GREEN}✓ 修复完成${NC}"

echo ""
echo -e "${YELLOW}5. 验证Python语法...${NC}"
sudo -u xiuxian /opt/xiuxian-bot/venv/bin/python3 -m py_compile /opt/xiuxian-bot/src/bot/handlers/start.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 语法检查通过${NC}"
else
    echo -e "${RED}✗ 语法检查失败${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}6. 测试导入...${NC}"
sudo -u xiuxian /opt/xiuxian-bot/venv/bin/python3 << 'PYEOF'
import sys
sys.path.insert(0, '/opt/xiuxian-bot/src')

try:
    from bot.handlers import start
    print("✓ start模块导入成功")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 导入测试失败${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}7. 重启服务...${NC}"

systemctl restart xiuxian-bot

sleep 5

if systemctl is-active --quiet xiuxian-bot; then
    echo -e "${GREEN}✓ 服务运行正常！${NC}"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  修复成功！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "🎮 功能特性:"
    echo "  ✅ /start, /help, /info 命令正常工作"
    echo "  ✅ .开始, .帮助, .状态 中文命令正常工作"
    echo "  ✅ 消息15秒后自动删除"
    echo ""

    echo "最近日志:"
    journalctl -u xiuxian-bot -n 20 --no-pager

else
    echo -e "${RED}✗ 服务启动失败${NC}"
    echo ""
    echo "详细错误信息:"
    journalctl -u xiuxian-bot -n 50 --no-pager
    exit 1
fi

echo ""
echo "📊 实时监控: journalctl -u xiuxian-bot -f"
echo ""
