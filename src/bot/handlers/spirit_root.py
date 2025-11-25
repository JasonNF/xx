"""灵根检测 - 凡人修仙传核心机制"""
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.models.database import AsyncSessionLocal
from bot.models.player import Player
from bot.services.spirit_root_service import SpiritRootService
from sqlalchemy import select


async def test_root_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """测试灵根检测 - /test_root"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        # 检查玩家是否已存在
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if player and player.spirit_root:
            # 已有灵根，显示信息
            spirit_root = player.spirit_root
            msg = f"""
🔮 【灵根检测】

道友的灵根资质：
{SpiritRootService.format_spirit_root_info(spirit_root, show_comment=False)}
"""
            await update.message.reply_text(msg)
            return

        # 创建新玩家并随机生成灵根
        if not player:
            player = Player(
                telegram_id=user.id,
                username=user.username or f"user_{user.id}",
                name=user.first_name or f"修士{user.id}",
            )
            session.add(player)
            await session.flush()  # 获取player.id

        # 随机生成灵根
        spirit_root = await SpiritRootService.generate_spirit_root(session, player)

        # 显示检测结果
        msg = f"""
🔮 【灵根觉醒】

恭喜道友！成功检测到灵根！

{SpiritRootService.format_spirit_root_info(spirit_root, show_comment=True)}
"""
        await update.message.reply_text(msg)


def register_handlers(application):
    """注册灵根相关处理器"""
    application.add_handler(CommandHandler("灵根", test_root_command))
