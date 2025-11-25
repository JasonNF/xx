"""宗门排行榜系统"""
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.models.database import AsyncSessionLocal
from bot.models import Player, Sect
from bot.services.sect_service import SectService
from sqlalchemy import select, func, desc


async def sect_ranking_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """宗门排行榜 - /宗门排行 [类型]"""
    user = update.effective_user

    # 解析排行榜类型
    ranking_type = "reputation"  # 默认声望排行
    if context.args:
        type_map = {
            "声望": "reputation",
            "实力": "power",
            "成员": "members",
        }
        ranking_type = type_map.get(context.args[0], "reputation")

    async with AsyncSessionLocal() as session:
        # 获取玩家(可选)
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if ranking_type == "reputation":
            # 声望排行 - 按宗门成员总声望排序
            await show_sect_reputation_ranking(update, session, player)
        elif ranking_type == "power":
            # 实力排行 - 按宗门等级和声望排序
            await show_sect_power_ranking(update, session, player)
        elif ranking_type == "members":
            # 成员排行 - 按宗门成员数量排序
            await show_sect_members_ranking(update, session, player)


async def show_sect_reputation_ranking(update: Update, session, player: Player = None):
    """显示宗门声望排行"""
    # 获取所有宗门及其成员总声望
    query = (
        select(
            Sect.id,
            Sect.name,
            Sect.level,
            Sect.master_id,
            func.count(Player.id).label("member_count"),
            func.sum(Player.contribution).label("total_reputation")
        )
        .outerjoin(Player, Player.sect_id == Sect.id)
        .group_by(Sect.id)
        .order_by(desc("total_reputation"))
        .limit(10)
    )

    result = await session.execute(query)
    rankings = result.all()

    if not rankings:
        await update.message.reply_text("暂无宗门排行数据")
        return

    # 构建消息
    msg = "🏆 【宗门声望排行榜】\n\n"
    msg += "排名基于宗门成员累积总声望\n"
    msg += "━━━━━━━━━━━━━━\n\n"

    player_sect_rank = None
    for idx, (sect_id, sect_name, sect_level, master_id, member_count, total_rep) in enumerate(rankings, 1):
        # 获取掌门名称
        master_name = "虚位以待"
        if master_id:
            result2 = await session.execute(
                select(Player.nickname).where(Player.id == master_id)
            )
            master = result2.scalar_one_or_none()
            if master:
                master_name = master

        # 等级配置
        tier_config = SectService.SECT_TIERS.get(sect_level, SectService.SECT_TIERS[1])
        tier_name = tier_config["name"]

        # 排名图标
        rank_icon = {1: "🥇", 2: "🥈", 3: "🥉"}.get(idx, f"{idx}.")

        msg += f"{rank_icon} **{sect_name}** ({tier_name})\n"
        msg += f"   掌门: {master_name}\n"
        msg += f"   成员: {member_count}人\n"
        msg += f"   总声望: {total_rep or 0}\n"

        # 标记玩家所在宗门
        if player and player.sect_id == sect_id:
            msg += f"   👤 你的宗门\n"
            player_sect_rank = idx

        msg += "\n"

    msg += "━━━━━━━━━━━━━━\n"

    # 显示玩家宗门排名
    if player and player.sect_id:
        if player_sect_rank:
            msg += f"你的宗门排名: 第{player_sect_rank}名\n"
        else:
            msg += "你的宗门未进入前10名\n"

        msg += f"个人声望贡献: {player.contribution}\n"

    msg += "\n💡 类型: /宗门排行 [声望|实力|成员]"

    await update.message.reply_text(msg, parse_mode="Markdown")


async def show_sect_power_ranking(update: Update, session, player: Player = None):
    """显示宗门实力排行"""
    # 获取所有宗门,按等级和声望排序
    query = (
        select(
            Sect.id,
            Sect.name,
            Sect.level,
            Sect.reputation,
            Sect.master_id,
            func.count(Player.id).label("member_count")
        )
        .outerjoin(Player, Player.sect_id == Sect.id)
        .group_by(Sect.id)
        .order_by(desc(Sect.level), desc(Sect.reputation))
        .limit(10)
    )

    result = await session.execute(query)
    rankings = result.all()

    if not rankings:
        await update.message.reply_text("暂无宗门排行数据")
        return

    # 构建消息
    msg = "⚔️ 【宗门实力排行榜】\n\n"
    msg += "排名基于宗门等级和宗门声望\n"
    msg += "━━━━━━━━━━━━━━\n\n"

    player_sect_rank = None
    for idx, (sect_id, sect_name, sect_level, sect_rep, master_id, member_count) in enumerate(rankings, 1):
        # 获取掌门名称
        master_name = "虚位以待"
        if master_id:
            result2 = await session.execute(
                select(Player.nickname).where(Player.id == master_id)
            )
            master = result2.scalar_one_or_none()
            if master:
                master_name = master

        # 等级配置
        tier_config = SectService.SECT_TIERS.get(sect_level, SectService.SECT_TIERS[1])
        tier_name = tier_config["name"]

        # 排名图标
        rank_icon = {1: "🥇", 2: "🥈", 3: "🥉"}.get(idx, f"{idx}.")

        msg += f"{rank_icon} **{sect_name}** ({tier_name})\n"
        msg += f"   掌门: {master_name}\n"
        msg += f"   等级: Lv.{sect_level}\n"
        msg += f"   宗门声望: {sect_rep}\n"
        msg += f"   成员: {member_count}人\n"

        # 标记玩家所在宗门
        if player and player.sect_id == sect_id:
            msg += f"   👤 你的宗门\n"
            player_sect_rank = idx

        msg += "\n"

    msg += "━━━━━━━━━━━━━━\n"

    # 显示玩家宗门排名
    if player and player.sect_id:
        if player_sect_rank:
            msg += f"你的宗门排名: 第{player_sect_rank}名\n"
        else:
            msg += "你的宗门未进入前10名\n"

    msg += "\n💡 类型: /宗门排行 [声望|实力|成员]"

    await update.message.reply_text(msg, parse_mode="Markdown")


async def show_sect_members_ranking(update: Update, session, player: Player = None):
    """显示宗门成员排行"""
    # 获取所有宗门,按成员数量排序
    query = (
        select(
            Sect.id,
            Sect.name,
            Sect.level,
            Sect.master_id,
            Sect.max_members,
            func.count(Player.id).label("member_count")
        )
        .outerjoin(Player, Player.sect_id == Sect.id)
        .group_by(Sect.id)
        .order_by(desc("member_count"))
        .limit(10)
    )

    result = await session.execute(query)
    rankings = result.all()

    if not rankings:
        await update.message.reply_text("暂无宗门排行数据")
        return

    # 构建消息
    msg = "👥 【宗门成员排行榜】\n\n"
    msg += "排名基于宗门当前成员数量\n"
    msg += "━━━━━━━━━━━━━━\n\n"

    player_sect_rank = None
    for idx, (sect_id, sect_name, sect_level, master_id, max_members, member_count) in enumerate(rankings, 1):
        # 获取掌门名称
        master_name = "虚位以待"
        if master_id:
            result2 = await session.execute(
                select(Player.nickname).where(Player.id == master_id)
            )
            master = result2.scalar_one_or_none()
            if master:
                master_name = master

        # 等级配置
        tier_config = SectService.SECT_TIERS.get(sect_level, SectService.SECT_TIERS[1])
        tier_name = tier_config["name"]

        # 排名图标
        rank_icon = {1: "🥇", 2: "🥈", 3: "🥉"}.get(idx, f"{idx}.")

        # 计算满员百分比
        fill_pct = int((member_count / max_members) * 100) if max_members > 0 else 0

        msg += f"{rank_icon} **{sect_name}** ({tier_name})\n"
        msg += f"   掌门: {master_name}\n"
        msg += f"   成员: {member_count}/{max_members} ({fill_pct}%)\n"

        # 标记玩家所在宗门
        if player and player.sect_id == sect_id:
            msg += f"   👤 你的宗门\n"
            player_sect_rank = idx

        msg += "\n"

    msg += "━━━━━━━━━━━━━━\n"

    # 显示玩家宗门排名
    if player and player.sect_id:
        if player_sect_rank:
            msg += f"你的宗门排名: 第{player_sect_rank}名\n"
        else:
            msg += "你的宗门未进入前10名\n"

    msg += "\n💡 类型: /宗门排行 [声望|实力|成员]"

    await update.message.reply_text(msg, parse_mode="Markdown")


async def player_reputation_ranking_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """个人声望排行 - /声望排行"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        # 获取玩家
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        # 获取声望前10玩家
        result = await session.execute(
            select(Player)
            .order_by(desc(Player.contribution))
            .limit(20)
        )
        top_players = result.scalars().all()

        if not top_players:
            await update.message.reply_text("暂无排行数据")
            return

        # 构建消息
        msg = "🌟 【个人声望排行榜】\n\n"
        msg += "排名基于玩家累积总声望\n"
        msg += "━━━━━━━━━━━━━━\n\n"

        player_rank = None
        for idx, p in enumerate(top_players, 1):
            # 获取宗门名称
            sect_name = "无宗门"
            if p.sect_id:
                result2 = await session.execute(
                    select(Sect.name).where(Sect.id == p.sect_id)
                )
                sect = result2.scalar_one_or_none()
                if sect:
                    sect_name = sect

            # 获取职位
            position = SectService.get_position_by_reputation(p.contribution)
            position_name = p.sect_position or position["name"]

            # 排名图标
            rank_icon = {1: "🥇", 2: "🥈", 3: "🥉"}.get(idx, f"{idx}.")

            msg += f"{rank_icon} **{p.nickname}**\n"
            msg += f"   境界: {p.full_realm_name}\n"
            msg += f"   宗门: {sect_name}\n"
            msg += f"   职位: {position_name}\n"
            msg += f"   声望: {p.contribution}\n"

            # 标记玩家自己
            if player and p.id == player.id:
                msg += f"   👤 这是你\n"
                player_rank = idx

            msg += "\n"

        msg += "━━━━━━━━━━━━━━\n"

        # 显示玩家排名
        if player:
            if player_rank:
                msg += f"你的排名: 第{player_rank}名\n"
            else:
                msg += "你的排名未进入前20名\n"

            msg += f"你的声望: {player.contribution}"

        await update.message.reply_text(msg, parse_mode="Markdown")


def register_handlers(application):
    """注册排行榜相关处理器"""
    application.add_handler(CommandHandler("宗门排行", sect_ranking_command))
    application.add_handler(CommandHandler("声望排行", player_reputation_ranking_command))
