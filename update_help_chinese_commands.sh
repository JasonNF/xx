#!/bin/bash

#===============================================
# 更新帮助文本为中文命令格式
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  更新帮助文本为中文命令格式${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo -e "${YELLOW}1. 更新start.py中的help_command...${NC}"

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
from bot.services.player_service import PlayerService
from bot.models.database import get_db
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

使用 .帮助 查看所有命令
"""
            await send_and_delete(update.message, welcome_back_text, parse_mode="Markdown")
            return

        # 创建新玩家并检测灵根
        player, is_new = await PlayerService.get_or_create_player(
            db, user.id, user.username, user.first_name
        )
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
使用 .帮助 查看所有可用命令开始你的修仙之旅！
"""
        await send_and_delete(update.message, welcome_text, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /help 命令 - 显示帮助信息"""
    help_text = """
📖 修仙世界 - 游戏指南

🎮 基础命令
.检测灵根 - 开始游戏/查看角色
.状态 - 查看详细角色状态
.改名 <新道号> - 修改道号（终生一次，10万灵石）
.改名状态 - 查看改名状态
.帮助 - 显示此帮助信息

🧘 修炼系统
.修炼 小时 - 开始修炼
.结算 - 完成修炼收取修为
.取消 - 取消当前修炼
.突破 - 尝试突破境界
.灵根 - 检测灵根

⚔️ 战斗系统
.战斗 怪物名 - 挑战怪物(PVE)
.切磋 - 挑战其他玩家(回复使用)
.技能 - 查看已学技能
.学习 技能名 - 学习新技能
.升级 技能名 - 升级技能
.施法 技能名 - 测试技能

🏛️ 秘境系统
.秘境 - 查看可用秘境
.探索 秘境名 - 进入秘境探索

📋 任务系统
.任务 类型 - 查看任务列表
.接取 任务ID - 接取任务
.完成 任务ID - 完成任务

💰 积分商城
.积分商城 或 .商城 - 浏览商城商品
.我的积分 - 查看积分余额和记录

💡 提示
• 修炼是获得修为的主要方式
• 探索秘境获得稀有物品
• 学习技能提升战斗力
• 战斗前请确保生命值充足
• 积分可通过签到、任务、PVP等途径获得
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
            await send_and_delete(
                update.message,
                "❌ 你还没有开始修仙之旅\\n请先使用 .检测灵根 命令"
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

print('✓ 已更新help命令，所有 / 改为 .')
PYEOF

echo -e "${GREEN}✓ 更新完成${NC}"

echo ""
echo -e "${YELLOW}2. 重启服务...${NC}"

systemctl restart xiuxian-bot

sleep 5

if systemctl is-active --quiet xiuxian-bot; then
    echo -e "${GREEN}✓ 服务运行正常！${NC}"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  帮助文本已更新为中文命令格式${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "📖 现在帮助文本显示的都是 . 开头的中文命令"
    echo ""
    echo "🎮 测试命令:"
    echo "  .帮助 - 查看更新后的帮助信息"
    echo ""

    echo "最近日志:"
    journalctl -u xiuxian-bot -n 10 --no-pager

else
    echo -e "${RED}✗ 服务启动失败${NC}"
    journalctl -u xiuxian-bot -n 30 --no-pager
    exit 1
fi

echo ""
