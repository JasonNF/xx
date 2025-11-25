"""排行榜系统handlers - 凡人修仙传版本"""
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.models.database import AsyncSessionLocal
from bot.models import Player, RealmType
from sqlalchemy import select, desc


async def ranking_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看排行榜 - /排行 [类型]"""
    user = update.effective_user

    # 解析排行类型
    rank_type = "combat"  # 默认战力榜
    if context.args:
        type_map = {
            "战力": "combat",
            "境界": "realm",
            "灵石": "wealth",
            "击杀": "kills",
            "胜率": "winrate"
        }
        rank_type = type_map.get(context.args[0], "combat")

    async with AsyncSessionLocal() as session:
        # 获取玩家
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        current_player = result.scalar_one_or_none()

        if not current_player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 根据类型查询
        if rank_type == "combat":
            title = "⚔️ 战力榜"
            # 战力需要计算，使用近似排序
            result = await session.execute(
                select(Player)
                .order_by(
                    desc(Player.realm),
                    desc(Player.realm_level),
                    desc(Player.attack)
                )
                .limit(20)
            )
        elif rank_type == "realm":
            title = "🌟 境界榜"
            result = await session.execute(
                select(Player)
                .order_by(
                    desc(Player.realm),
                    desc(Player.realm_level),
                    desc(Player.cultivation_exp)
                )
                .limit(20)
            )
        elif rank_type == "wealth":
            title = "💰 财富榜"
            result = await session.execute(
                select(Player)
                .order_by(desc(Player.spirit_stones))
                .limit(20)
            )
        elif rank_type == "kills":
            title = "💀 击杀榜"
            result = await session.execute(
                select(Player)
                .order_by(desc(Player.total_kills))
                .limit(20)
            )
        else:  # winrate
            title = "🏆 胜率榜"
            result = await session.execute(
                select(Player)
                .where(Player.total_battles >= 10)  # 至少10场战斗
                .order_by(desc(Player.total_wins * 100 / Player.total_battles))
                .limit(20)
            )

        players = result.scalars().all()

        if not players:
            await update.message.reply_text("🏆 暂无排行数据")
            return

        # 构建消息
        msg = f"{title}\n"
        msg += "━━━━━━━━━━━━━━\n\n"

        for i, player in enumerate(players, 1):
            # 排名图标
            if i == 1:
                rank_icon = "🥇"
            elif i == 2:
                rank_icon = "🥈"
            elif i == 3:
                rank_icon = "🥉"
            else:
                rank_icon = f"{i}."

            # 是否是当前玩家
            is_me = " ⬅️" if player.id == current_player.id else ""

            # 根据类型显示不同数据
            if rank_type == "combat":
                value = f"⚡ {player.combat_power}"
            elif rank_type == "realm":
                value = player.full_realm_name
            elif rank_type == "wealth":
                value = f"💰 {player.spirit_stones}"
            elif rank_type == "kills":
                value = f"💀 {player.total_kills}"
            else:  # winrate
                if player.total_battles > 0:
                    winrate = player.total_wins * 100 / player.total_battles
                    value = f"🏆 {winrate:.1f}%"
                else:
                    value = "🏆 0%"

            msg += f"{rank_icon} **{player.nickname}** {value}{is_me}\n"

        # 查找当前玩家排名
        msg += "\n━━━━━━━━━━━━━━\n"

        # 简单获取当前玩家的排名（近似）
        if rank_type == "combat":
            result = await session.execute(
                select(Player)
                .where(Player.attack > current_player.attack)
            )
            my_rank = len(result.scalars().all()) + 1
            my_value = f"⚡ {current_player.combat_power}"
        elif rank_type == "realm":
            my_rank = "N/A"  # 境界排名较复杂
            my_value = current_player.full_realm_name
        elif rank_type == "wealth":
            result = await session.execute(
                select(Player)
                .where(Player.spirit_stones > current_player.spirit_stones)
            )
            my_rank = len(result.scalars().all()) + 1
            my_value = f"💰 {current_player.spirit_stones}"
        elif rank_type == "kills":
            result = await session.execute(
                select(Player)
                .where(Player.total_kills > current_player.total_kills)
            )
            my_rank = len(result.scalars().all()) + 1
            my_value = f"💀 {current_player.total_kills}"
        else:
            my_rank = "N/A"
            if current_player.total_battles > 0:
                winrate = current_player.total_wins * 100 / current_player.total_battles
                my_value = f"🏆 {winrate:.1f}%"
            else:
                my_value = "🏆 0%"

        msg += f"你的排名：第{my_rank}名\n"
        msg += f"你的数据：{my_value}\n\n"

        msg += "💡 查看其他榜单：\n"
        msg += "/排行 战力 | /排行 境界\n"
        msg += "/排行 灵石 | /排行 击杀"

        await update.message.reply_text(msg, parse_mode="Markdown")


def register_handlers(application):
    """注册排行榜相关处理器"""
    application.add_handler(CommandHandler("排行", ranking_command))
