"""签到系统handlers - 凡人修仙传版本"""
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes, CommandHandler

from bot.models.database import AsyncSessionLocal
from bot.models import Player
from bot.services import PlayerService
from sqlalchemy import select


async def signin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """每日签到 - /签到"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        # 获取玩家
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 执行签到
        success, message, reward = await PlayerService.daily_sign(session, player)

        if success:
            msg = f"📅 {message}\n\n"
            msg += f"🎁 奖励：{reward} 灵石\n\n"

            # 连续签到奖励说明
            days = player.continuous_sign_days
            if days < 7:
                next_bonus = (days) * 100
                msg += f"💡 明天连续签到奖励：{100 + next_bonus} 灵石\n"
            else:
                msg += f"🌟 已达成7天连续签到最高奖励！\n"

            msg += f"\n💰 当前灵石：{player.spirit_stones}"
        else:
            msg = f"❌ {message}\n\n"
            msg += "明天再来吧~"

        await update.message.reply_text(msg)


def register_handlers(application):
    """注册签到相关处理器"""
    application.add_handler(MessageHandler(filters.Regex(r"^\.签到"), signin_command))
