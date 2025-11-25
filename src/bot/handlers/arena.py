"""竞技场handler"""
import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, Application
from sqlalchemy import select

from bot.models import get_db, Player
from bot.services.arena_service import ArenaService

logger = logging.getLogger(__name__)


async def arena_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看竞技场信息 - /竞技场"""
    user_id = update.effective_user.id

    async with get_db() as db:
        # 获取玩家
        result = await db.execute(select(Player).where(Player.telegram_id == user_id))
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("你还未踏入修仙之路，请先使用 /检测灵根 开始游戏")
            return

        # 获取竞技场信息
        info = await ArenaService.get_player_arena_info(db, player)

        message = f"""⚔️ 竞技场信息

🏆 当前排名: {info['rank']}
✨ 最高排名: {info['highest_rank']}
⭐ 积分: {info['points']}

📊 战绩统计:
总挑战: {info['total_challenges']}次
总胜利: {info['total_wins']}次
胜率: {info['win_rate']*100:.1f}%
连胜: {info['win_streak']}场
最高连胜: {info['highest_win_streak']}场

🎯 今日挑战:
已用: {info['daily_challenges']}/5
剩余: {info['remaining_challenges']}次
"""

        message += "\n💡 使用 /挑战目标 查看可挑战的对手"

        await update.message.reply_text(message)


async def challenge_targets_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看可挑战目标 - /挑战目标"""
    user_id = update.effective_user.id

    async with get_db() as db:
        # 获取玩家
        result = await db.execute(select(Player).where(Player.telegram_id == user_id))
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("你还未踏入修仙之路，请先使用 /检测灵根 开始游戏")
            return

        # 获取竞技场数据
        arena = await ArenaService.get_or_create_arena(db, player)

        # 检查挑战次数
        can_challenge, remaining = await ArenaService.check_daily_limit(arena)
        if not can_challenge:
            await update.message.reply_text("❌ 今日挑战次数已用完，请明天再来")
            return

        # 获取挑战目标
        targets = await ArenaService.get_challenge_targets(db, player, arena)

        if not targets:
            await update.message.reply_text("暂无可挑战的对手")
            return

        message_parts = [f"⚔️ 可挑战目标 (剩余{remaining}次)\n"]

        for target in targets:
            message_parts.append(
                f"\n排名 {target['rank']} - {target['nickname']}\n"
                f"境界: {target['realm']} | 战力: {target['combat_power']}\n"
                f"积分: {target['points']} | ID: {target['player_id']}"
            )

        message = "\n".join(message_parts)
        message += "\n\n💡 使用 /挑战 <ID> 发起挑战"

        await update.message.reply_text(message)


async def challenge_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """发起挑战 - /挑战 <玩家ID>"""
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text("❌ 请指定目标玩家ID\n用法: /挑战 <玩家ID>")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ 玩家ID必须是数字")
        return

    async with get_db() as db:
        # 获取玩家
        result = await db.execute(select(Player).where(Player.telegram_id == user_id))
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("你还未踏入修仙之路，请先使用 /检测灵根 开始游戏")
            return

        # 发起挑战
        success, message, result_data = await ArenaService.challenge(db, player, target_id)

        if not success:
            await update.message.reply_text(f"❌ {message}")
            return

        # 构建结果消息
        result_message = f"{message}\n\n"

        if result_data["is_win"]:
            result_message += f"✅ 胜利！\n"
        else:
            result_message += f"💔 失败\n"

        result_message += f"积分变化: {result_data['points_change']:+d}\n"

        if result_data["win_streak"] > 0:
            result_message += f"🔥 连胜: {result_data['win_streak']}场\n"

        result_message += f"\n剩余挑战次数: {result_data['remaining_challenges']}"

        await update.message.reply_text(result_message)


async def arena_rankings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看竞技场排行榜 - /竞技场排行"""
    async with get_db() as db:
        # 获取排行榜
        rankings = await ArenaService.get_rankings(db, limit=20)

        if not rankings:
            await update.message.reply_text("竞技场暂无数据")
            return

        message_parts = ["🏆 竞技场排行榜 (前20名)\n"]

        for rank_data in rankings:
            emoji = ""
            if rank_data["rank"] == 1:
                emoji = "🥇"
            elif rank_data["rank"] == 2:
                emoji = "🥈"
            elif rank_data["rank"] == 3:
                emoji = "🥉"

            message_parts.append(
                f"\n{emoji}#{rank_data['rank']} {rank_data['nickname']}\n"
                f"境界: {rank_data['realm']} | 战力: {rank_data['combat_power']}\n"
                f"积分: {rank_data['points']} | 胜率: {rank_data['win_rate']*100:.1f}%"
            )

        await update.message.reply_text("\n".join(message_parts))


def register_handlers(application: Application):
    """注册所有handler"""
    application.add_handler(CommandHandler("竞技场", arena_info_command))
    application.add_handler(CommandHandler("挑战目标", challenge_targets_command))
    application.add_handler(CommandHandler("挑战", challenge_command))
    application.add_handler(CommandHandler("竞技场排行", arena_rankings_command))

    logger.info("竞技场handlers已注册")
