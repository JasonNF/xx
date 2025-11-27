"""宗门战争handler"""
import logging
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes, CommandHandler, Application
from sqlalchemy import select

from bot.models import get_db, Player, Sect, SectWar, SectWarStatus
from bot.services.sect_war_service import SectWarService

logger = logging.getLogger(__name__)


async def declare_war_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """宣战 - /宣战 <目标门派ID>"""
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text("❌ 请指定目标门派ID\n用法: /宣战 <门派ID>")
        return

    try:
        target_sect_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ 门派ID必须是数字")
        return

    async with get_db() as db:
        # 获取玩家
        result = await db.execute(select(Player).where(Player.telegram_id == user_id))
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("你还未踏入修仙之路，请先使用 /检测灵根 开始游戏")
            return

        if not player.sect_id:
            await update.message.reply_text("❌ 你还未加入门派")
            return

        # 获取玩家门派
        result = await db.execute(select(Sect).where(Sect.id == player.sect_id))
        sect = result.scalar_one_or_none()

        if not sect:
            await update.message.reply_text("❌ 门派不存在")
            return

        # 检查是否为宗主
        if sect.master_id != player.id:
            await update.message.reply_text("❌ 只有宗主可以宣战")
            return

        # 宣战
        success, message, war = await SectWarService.declare_war(
            db, sect, target_sect_id, player.id
        )

        if success:
            await update.message.reply_text(
                f"⚔️ 宣战成功！\n\n"
                f"宗门战将在1小时后开始\n"
                f"战争ID: {war.id}\n\n"
                f"💡 战争开始后使用 /参战 {war.id} 加入战斗"
            )
        else:
            await update.message.reply_text(f"❌ {message}")


async def join_war_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """参战 - /参战 <战争ID>"""
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text("❌ 请指定战争ID\n用法: /参战 <战争ID>")
        return

    try:
        war_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ 战争ID必须是数字")
        return

    async with get_db() as db:
        # 获取玩家
        result = await db.execute(select(Player).where(Player.telegram_id == user_id))
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("你还未踏入修仙之路，请先使用 /检测灵根 开始游戏")
            return

        if not player.sect_id:
            await update.message.reply_text("❌ 你还未加入门派")
            return

        # 参战
        success, message = await SectWarService.join_war(db, player, war_id)

        if success:
            await update.message.reply_text(
                f"⚔️ {message}\n\n"
                f"你已加入宗门战！\n"
                f"使用 /宗门战状态 {war_id} 查看战况"
            )
        else:
            await update.message.reply_text(f"❌ {message}")


async def war_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看宗门战状态 - /宗门战状态 <战争ID>"""
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text("❌ 请指定战争ID\n用法: /宗门战状态 <战争ID>")
        return

    try:
        war_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ 战争ID必须是数字")
        return

    async with get_db() as db:
        # 获取玩家
        result = await db.execute(select(Player).where(Player.telegram_id == user_id))
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("你还未踏入修仙之路，请先使用 /检测灵根 开始游戏")
            return

        # 获取战况
        status = await SectWarService.get_war_status(db, war_id)

        if not status:
            await update.message.reply_text("❌ 宗门战不存在")
            return

        # 状态显示
        status_text = {
            "declared": "准备中",
            "ongoing": "进行中",
            "finished": "已结束"
        }

        message = f"""⚔️ 宗门战状态

攻方: {status['attacker_sect']}
守方: {status['defender_sect']}

状态: {status_text.get(status['status'], status['status'])}

战况:
🔴 {status['attacker_sect']}: {status['attacker_score']}分 ({status['attacker_kills']}杀) | {status['attacker_participants']}人参战
🔵 {status['defender_sect']}: {status['defender_score']}分 ({status['defender_kills']}杀) | {status['defender_participants']}人参战
"""

        if status['started_at']:
            message += f"\n开始时间: {status['started_at'].strftime('%Y-%m-%d %H:%M')}"

        if status['ended_at']:
            message += f"\n结束时间: {status['ended_at'].strftime('%Y-%m-%d %H:%M')}"

        # 如果已结束,显示胜者
        if status['status'] == "finished" and status['winner_sect_id']:
            winner_name = status['attacker_sect'] if status['winner_sect_id'] == status.get('attacker_sect_id') else status['defender_sect']
            message += f"\n\n🏆 胜利: {winner_name}"

        # 显示玩家个人战绩
        if player.sect_id in [status.get('attacker_sect_id'), status.get('defender_sect_id')]:
            player_stats = await SectWarService.get_player_war_stats(db, player.id, war_id)
            if player_stats:
                message += f"\n\n你的战绩:\n"
                message += f"击杀: {player_stats['kills']} | 死亡: {player_stats['deaths']}\n"
                message += f"K/D: {player_stats['kd_ratio']:.2f} | 贡献: {player_stats['contribution_points']}"

        await update.message.reply_text(message)


async def ongoing_wars_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看进行中的宗门战 - /进行中的宗门战"""
    async with get_db() as db:
        wars = await SectWarService.get_ongoing_wars(db)

        if not wars:
            await update.message.reply_text("当前没有进行中的宗门战")
            return

        message_parts = ["⚔️ 进行中的宗门战\n"]

        for war in wars:
            message_parts.append(
                f"\n战争ID: {war['war_id']}\n"
                f"🔴 {war['attacker_sect']} ({war['attacker_score']}分)\n"
                f"  vs\n"
                f"🔵 {war['defender_sect']} ({war['defender_score']}分)\n"
                f"参战: {war['attacker_participants']}人 vs {war['defender_participants']}人"
            )

        message = "\n".join(message_parts)
        message += "\n\n💡 使用 /参战 <ID> 加入战斗\n💡 使用 /宗门战状态 <ID> 查看详情"

        await update.message.reply_text(message)


def register_handlers(application: Application):
    """注册所有handler"""
    application.add_handler(MessageHandler(filters.Regex(r"^\.宣战"), declare_war_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.参战"), join_war_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.宗门战状态"), war_status_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.进行中的宗门战"), ongoing_wars_command))

    logger.info("宗门战争handlers已注册")
