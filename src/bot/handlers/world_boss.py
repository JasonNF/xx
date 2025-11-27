"""世界BOSS handler"""
import logging
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes, CommandHandler, Application
from sqlalchemy import select

from bot.models import get_db, Player
from bot.services.world_boss_service import WorldBossService

logger = logging.getLogger(__name__)


async def world_boss_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看世界BOSS状态 - /世界BOSS"""
    async with get_db() as db:
        # 获取当前活跃的BOSS
        boss_info = await WorldBossService.get_boss_status(db)

        if not boss_info:
            await update.message.reply_text(
                "🌙 当前无世界BOSS\n\n"
                "世界BOSS将在每天中午12:00降临,持续2小时\n"
                "💡 使用 /攻击BOSS 参与战斗"
            )
            return

        message = f"""🐉 世界BOSS: {boss_info['name']}

📖 {boss_info['description']}

⚔️ BOSS属性:
等级: Lv.{boss_info['level']}
血量: {boss_info['current_hp']:,}/{boss_info['max_hp']:,} ({boss_info['hp_percent']:.1f}%)
攻击: {boss_info['attack']}
防御: {boss_info['defense']}

🎁 奖励池:
💎 灵石: {boss_info['total_reward_stones']:,}
✨ 经验: {boss_info['total_reward_exp']:,}

👥 参与人数: {boss_info['participant_count']}
⏰ 剩余时间: {boss_info['minutes_remaining']}分钟

💡 使用 /攻击BOSS 参与战斗
💡 使用 /BOSS排行 查看伤害排行"""

        await update.message.reply_text(message)


async def attack_boss_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """攻击世界BOSS - /攻击BOSS"""
    user_id = update.effective_user.id

    async with get_db() as db:
        # 获取玩家
        result = await db.execute(select(Player).where(Player.telegram_id == user_id))
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("你还未踏入修仙之路,请先使用 /检测灵根 开始游戏")
            return

        # 获取当前BOSS
        boss_info = await WorldBossService.get_boss_status(db)
        if not boss_info:
            await update.message.reply_text("❌ 当前无世界BOSS")
            return

        # 攻击BOSS
        success, message, result_data = await WorldBossService.attack_boss(
            db, player, boss_info['id']
        )

        if not success:
            await update.message.reply_text(f"❌ {message}")
            return

        # 构建结果消息
        result_message = message

        # 如果BOSS被击败,显示奖励通知
        if result_data['is_defeated']:
            result_message += "\n\n💡 使用 /BOSS排行 查看奖励分配"

        await update.message.reply_text(result_message)


async def boss_rankings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看BOSS伤害排行 - /BOSS排行"""
    user_id = update.effective_user.id

    async with get_db() as db:
        # 获取玩家
        result = await db.execute(select(Player).where(Player.telegram_id == user_id))
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("你还未踏入修仙之路,请先使用 /检测灵根 开始游戏")
            return

        # 获取当前BOSS
        boss_info = await WorldBossService.get_boss_status(db)
        if not boss_info:
            await update.message.reply_text("❌ 当前无世界BOSS")
            return

        # 获取排行榜
        rankings = await WorldBossService.get_damage_rankings(db, boss_info['id'], limit=20)

        if not rankings:
            await update.message.reply_text("暂无参与数据")
            return

        # 获取玩家自己的参与情况
        player_participation = await WorldBossService.get_player_participation(
            db, player.id, boss_info['id']
        )

        message_parts = [f"🏆 世界BOSS伤害排行\n"]

        # 显示前20名
        for rank_data in rankings:
            emoji = ""
            if rank_data['rank'] == 1:
                emoji = "🥇"
            elif rank_data['rank'] == 2:
                emoji = "🥈"
            elif rank_data['rank'] == 3:
                emoji = "🥉"

            line = f"\n{emoji}#{rank_data['rank']} {rank_data['nickname']}\n"
            line += f"境界: {rank_data['realm']} | 伤害: {rank_data['total_damage']:,}\n"
            line += f"攻击: {rank_data['attack_count']}次"

            # 如果已分配奖励,显示奖励
            if rank_data['is_rewarded']:
                line += f"\n💰 奖励: 灵石{rank_data['reward_stones']:,} 经验{rank_data['reward_exp']:,}"

            message_parts.append(line)

        # 显示玩家自己的参与情况
        if player_participation:
            message_parts.append(f"\n\n━━━━━━━━━━━━━━━━")
            message_parts.append(f"\n你的战绩:")
            message_parts.append(f"总伤害: {player_participation['total_damage']:,}")
            message_parts.append(f"攻击次数: {player_participation['attack_count']}/10")

            if player_participation['is_rewarded']:
                message_parts.append(f"\n✅ 已获得奖励:")
                message_parts.append(f"💎 灵石: {player_participation['reward_stones']:,}")
                message_parts.append(f"✨ 经验: {player_participation['reward_exp']:,}")

        await update.message.reply_text("".join(message_parts))


async def my_boss_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看我的BOSS战绩 - /我的BOSS战绩"""
    user_id = update.effective_user.id

    async with get_db() as db:
        # 获取玩家
        result = await db.execute(select(Player).where(Player.telegram_id == user_id))
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("你还未踏入修仙之路,请先使用 /检测灵根 开始游戏")
            return

        # 获取当前BOSS
        boss_info = await WorldBossService.get_boss_status(db)
        if not boss_info:
            await update.message.reply_text("当前无世界BOSS")
            return

        # 获取玩家参与情况
        participation = await WorldBossService.get_player_participation(
            db, player.id, boss_info['id']
        )

        if not participation:
            await update.message.reply_text(
                "你尚未参与本次世界BOSS战斗\n\n"
                "💡 使用 /攻击BOSS 参与战斗"
            )
            return

        message = f"""⚔️ 我的世界BOSS战绩

🎯 战斗数据:
总伤害: {participation['total_damage']:,}
攻击次数: {participation['attack_count']}/10
剩余攻击: {participation['remaining_attacks']}次
"""

        if participation['is_rewarded']:
            message += f"""
🎁 已获得奖励:
💎 灵石: {participation['reward_stones']:,}
✨ 经验: {participation['reward_exp']:,}"""
        else:
            message += "\n📊 奖励将在BOSS被击败后分配"

        await update.message.reply_text(message)


def register_handlers(application: Application):
    """注册所有handler"""
    application.add_handler(MessageHandler(filters.Regex(r"^\.世界BOSS"), world_boss_status_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.攻击BOSS"), attack_boss_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.BOSS排行"), boss_rankings_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.我的BOSS战绩"), my_boss_stats_command))

    logger.info("世界BOSS handlers已注册")
