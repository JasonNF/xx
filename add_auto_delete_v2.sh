#!/bin/bash

#===============================================
# 添加消息自动删除功能V2（修复导入路径）
#===============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  添加消息自动删除功能 V2${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo -e "${YELLOW}1. 创建message_utils.py工具模块...${NC}"

# 创建utils目录
sudo -u xiuxian mkdir -p /opt/xiuxian-bot/src/bot/utils

# 创建message_utils.py
sudo -u xiuxian cat > /opt/xiuxian-bot/src/bot/utils/message_utils.py << 'PYEOF'
"""
消息工具模块 - 处理消息自动删除等功能
"""
import asyncio
import logging
from typing import Optional
from telegram import Message

logger = logging.getLogger(__name__)

AUTO_DELETE_SECONDS = 15  # 消息自动删除时间（秒）


async def send_and_delete(message: Message, text: str, delete_after: int = AUTO_DELETE_SECONDS, **kwargs) -> Optional[Message]:
    """
    发送消息并在指定时间后自动删除

    Args:
        message: 用户的原始消息对象
        text: 要发送的回复文本
        delete_after: 多少秒后删除消息（默认15秒）
        **kwargs: 传递给reply_text的其他参数（如parse_mode等）

    Returns:
        发送的消息对象，如果发送失败则返回None
    """
    try:
        # 发送回复消息
        bot_message = await message.reply_text(text, **kwargs)

        # 创建异步任务来删除消息
        asyncio.create_task(_delete_messages_after_delay(
            user_message=message,
            bot_message=bot_message,
            delay=delete_after
        ))

        return bot_message

    except Exception as e:
        logger.error(f"发送消息失败: {e}", exc_info=True)
        return None


async def _delete_messages_after_delay(user_message: Message, bot_message: Message, delay: int):
    """
    延迟删除用户消息和bot消息

    Args:
        user_message: 用户的消息
        bot_message: bot的回复消息
        delay: 延迟时间（秒）
    """
    try:
        # 等待指定时间
        await asyncio.sleep(delay)

        # 删除bot的回复
        try:
            await bot_message.delete()
            logger.debug(f"已删除bot消息 {bot_message.message_id}")
        except Exception as e:
            logger.warning(f"删除bot消息失败 {bot_message.message_id}: {e}")

        # 删除用户的命令消息
        try:
            await user_message.delete()
            logger.debug(f"已删除用户消息 {user_message.message_id}")
        except Exception as e:
            logger.warning(f"删除用户消息失败 {user_message.message_id}: {e}")

    except Exception as e:
        logger.error(f"消息自动删除任务失败: {e}", exc_info=True)


async def delete_message_after(message: Message, delay: int = AUTO_DELETE_SECONDS):
    """
    单独删除某条消息

    Args:
        message: 要删除的消息
        delay: 延迟时间（秒）
    """
    try:
        await asyncio.sleep(delay)
        await message.delete()
        logger.debug(f"已删除消息 {message.message_id}")
    except Exception as e:
        logger.warning(f"删除消息失败 {message.message_id}: {e}")
PYEOF

# 创建__init__.py
sudo -u xiuxian cat > /opt/xiuxian-bot/src/bot/utils/__init__.py << 'PYEOF'
"""Bot工具模块"""
from .message_utils import send_and_delete, delete_message_after, AUTO_DELETE_SECONDS

__all__ = ['send_and_delete', 'delete_message_after', 'AUTO_DELETE_SECONDS']
PYEOF

echo -e "${GREEN}✓ message_utils.py已创建${NC}"

echo ""
echo -e "${YELLOW}2. 修改start.py启用自动删除...${NC}"

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

使用 /help 查看所有命令
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
            await send_and_delete(
                update.message,
                "❌ 你还没有开始修仙之旅\\n请先使用 /start 命令检测灵根"
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

print('✓ 已启用自动删除功能')
PYEOF

echo -e "${GREEN}✓ start.py已更新${NC}"

echo ""
echo -e "${YELLOW}3. 验证语法...${NC}"
sudo -u xiuxian /opt/xiuxian-bot/venv/bin/python3 -m py_compile /opt/xiuxian-bot/src/bot/handlers/start.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 语法检查通过${NC}"
else
    echo -e "${RED}✗ 语法检查失败${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}4. 重启服务...${NC}"
systemctl restart xiuxian-bot

sleep 6

if systemctl is-active --quiet xiuxian-bot; then
    echo -e "${GREEN}✓ 服务运行正常！${NC}"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  自动删除功能添加成功！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "✨ 功能特性:"
    echo "  • 用户命令消息：15秒后自动删除"
    echo "  • Bot回复消息：15秒后自动删除"
    echo "  • 保持群组/频道整洁"
    echo ""
    echo "🎮 测试命令:"
    echo "  /start 或 .开始 - 观察15秒后消息自动消失"
    echo "  /info 或 .状态 - 观察15秒后消息自动消失"
    echo ""
    echo "⚙️  修改删除时间:"
    echo "  编辑 /opt/xiuxian-bot/src/bot/utils/message_utils.py"
    echo "  修改 AUTO_DELETE_SECONDS = 15"
    echo ""

    echo "最近日志:"
    journalctl -u xiuxian-bot -n 15 --no-pager

else
    echo -e "${RED}✗ 服务启动失败${NC}"
    journalctl -u xiuxian-bot -n 50 --no-pager
    exit 1
fi

echo ""
echo "📊 实时监控: journalctl -u xiuxian-bot -f"
echo ""
