"""寿元系统handlers - 凡人修仙传版本"""
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes, CommandHandler

from bot.models.database import AsyncSessionLocal
from bot.models import Player
from bot.services.lifespan_service import LifespanService
from sqlalchemy import select


async def lifespan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看寿元信息 - /寿元"""
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

        # 计算剩余寿元
        remaining_years = player.lifespan - player.age
        lifespan_ratio = remaining_years / player.lifespan

        # 寿元状态
        if lifespan_ratio > 0.5:
            status = "✅ 寿元充足"
            status_icon = "💚"
        elif lifespan_ratio > 0.2:
            status = "⚠️ 寿元正常"
            status_icon = "💛"
        elif lifespan_ratio > 0.1:
            status = "🔴 寿元不足"
            status_icon = "🧡"
        else:
            status = "💀 寿元危急"
            status_icon = "❤️"

        # 衰老惩罚
        penalty = LifespanService.get_age_penalty(player)
        penalty_text = ""
        if penalty < 1.0:
            penalty_pct = int((1.0 - penalty) * 100)
            penalty_text = f"\n⚠️ 衰老惩罚：战斗力 -{penalty_pct}%"

        # 境界寿元
        realm_lifespan = LifespanService.REALM_LIFESPAN.get(player.realm, 100)

        # 构建消息
        msg = f"⏳ 【寿元信息】\n\n"
        msg += f"{status_icon} 状态：{status}\n\n"
        msg += f"当前年龄：{player.age}岁\n"
        msg += f"寿元上限：{player.lifespan}岁\n"
        msg += f"剩余寿元：{remaining_years}岁 ({lifespan_ratio * 100:.1f}%)\n"
        msg += penalty_text
        msg += f"\n━━━━━━━━━━━━━━\n"
        msg += f"境界：{player.full_realm_name}\n"
        msg += f"基础寿元：{realm_lifespan}岁\n\n"

        # 提示信息
        if lifespan_ratio <= 0.2:
            msg += "💡 建议：\n"
            msg += "• 寻找延寿丹药\n"
            msg += "• 尽快突破提升境界\n"
            msg += "• 完成延寿相关任务\n\n"

        msg += "📊 寿元说明：\n"
        msg += "• 凡人：100岁\n"
        msg += "• 炼气期：150岁\n"
        msg += "• 筑基期：300岁\n"
        msg += "• 结丹期：500岁\n"
        msg += "• 元婴期：1000岁\n"
        msg += "• 化神期：2000岁"

        await update.message.reply_text(msg)


def register_handlers(application):
    """注册寿元相关处理器"""
    application.add_handler(MessageHandler(filters.Regex(r"^\.寿元"), lifespan_command))
