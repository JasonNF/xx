"""阵法系统handlers"""
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.models.database import AsyncSessionLocal
from bot.models import Player
from bot.models.formation import FormationTemplate, PlayerFormation, ActiveFormation
from bot.services.formation_service import FormationService
from sqlalchemy import select
from datetime import datetime


async def formation_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看阵法列表 - /阵法"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        result = await session.execute(
            select(PlayerFormation).where(PlayerFormation.player_id == player.id)
        )
        formations = result.scalars().all()

        if not formations:
            msg = "⚡ 【阵法】\n\n"
            msg += "📦 您还没有学会任何阵法\n\n"
            msg += "💡 使用 /阵法图谱 查看可学习的阵法\n"
            msg += "💡 使用 /学习阵法 <阵法名> 学习阵法"
            await update.message.reply_text(msg)
            return

        msg = "⚡ 【已学阵法】\n\n"

        for formation in formations:
            result = await session.execute(
                select(FormationTemplate).where(FormationTemplate.id == formation.template_id)
            )
            template = result.scalar_one_or_none()

            if not template:
                continue

            msg += f"**{template.name}**\n"
            msg += f"    类型：{template.formation_type} | 品阶：{template.grade}\n"
            msg += f"    等级：Lv.{formation.proficiency_level} | 熟练度：{formation.proficiency}/100\n"
            msg += f"    🛡️+{template.defense_bonus} ⚔️+{template.attack_bonus}\n\n"

        msg += "━━━━━━━━━━━━━━\n"
        msg += "💡 使用 /布阵 <阵法名> 布置阵法\n"
        msg += "💡 使用 /撤阵 撤除当前阵法\n"
        msg += "💡 使用 /当前阵法 查看当前布置的阵法"

        await update.message.reply_text(msg, parse_mode="Markdown")


async def formation_codex_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """阵法图谱 - /阵法图谱"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        result = await session.execute(
            select(FormationTemplate).order_by(FormationTemplate.grade.asc())
        )
        templates = result.scalars().all()

        if not templates:
            await update.message.reply_text("📖 阵法图谱为空")
            return

        msg = "📖 【阵法图谱】\n\n"

        for template in templates:
            # 检查是否已学习
            result = await session.execute(
                select(PlayerFormation).where(
                    PlayerFormation.player_id == player.id,
                    PlayerFormation.template_id == template.id
                )
            )
            learned = result.scalar_one_or_none()
            status = "✅" if learned else "🔒"

            msg += f"{status} **{template.name}**\n"
            msg += f"    {template.description[:50]}...\n"
            msg += f"    类型：{template.formation_type} | 品阶：{template.grade}\n"
            msg += f"    要求：{template.required_realm} {template.required_level}层\n"
            msg += f"    效果：🛡️+{template.defense_bonus} ⚔️+{template.attack_bonus}\n"
            msg += f"    学习：{template.learning_cost}灵石\n"
            msg += f"    布阵：{template.spirit_stone_cost}灵石 + {template.spiritual_power_cost}灵力\n\n"

        msg += "━━━━━━━━━━━━━━\n"
        msg += "💡 使用 /学习阵法 <阵法名> 学习阵法"

        await update.message.reply_text(msg, parse_mode="Markdown")


async def learn_formation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """学习阵法 - /学习阵法 <阵法名>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定阵法名称\n"
            "用法：/学习阵法 <阵法名>\n"
            "例如：/学习阵法 五行困灵阵"
        )
        return

    formation_name = " ".join(context.args)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        result = await session.execute(
            select(FormationTemplate).where(FormationTemplate.name == formation_name)
        )
        template = result.scalar_one_or_none()

        if not template:
            await update.message.reply_text(f"❌ 未找到名为 {formation_name} 的阵法")
            return

        success, message = await FormationService.learn_formation(session, player, template.id)

        if success:
            msg = f"🎉 {message}\n\n"
            msg += f"📖 阵法：{template.name}\n"
            msg += f"🏷️ 类型：{template.formation_type}\n"
            msg += f"⭐ 品阶：{template.grade}\n\n"
            msg += f"【效果】\n"
            msg += f"🛡️ 防御：+{template.defense_bonus}\n"
            msg += f"⚔️ 攻击：+{template.attack_bonus}\n"
            if template.trap_power > 0:
                msg += f"🕸️ 困敌：{template.trap_power}\n"
            if template.illusion_power > 0:
                msg += f"✨ 幻术：{template.illusion_power}\n"
            msg += f"\n💰 消耗：{template.learning_cost}灵石"
        else:
            msg = f"❌ {message}"

        await update.message.reply_text(msg)


async def deploy_formation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """布阵 - /布阵 <阵法名> [时长]"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定阵法名称\n"
            "用法：/布阵 <阵法名> [时长]\n"
            "时长默认24小时\n"
            "例如：/布阵 五行困灵阵 48"
        )
        return

    formation_name = context.args[0]
    duration_hours = 24

    if len(context.args) > 1:
        try:
            duration_hours = int(context.args[1])
            if duration_hours < 1 or duration_hours > 168:
                await update.message.reply_text("❌ 时长必须在1-168小时之间")
                return
        except ValueError:
            await update.message.reply_text("❌ 时长必须是数字")
            return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 查找阵法
        result = await session.execute(
            select(PlayerFormation).join(FormationTemplate).where(
                PlayerFormation.player_id == player.id,
                FormationTemplate.name == formation_name
            )
        )
        formation = result.scalar_one_or_none()

        if not formation:
            await update.message.reply_text(f"❌ 您还未学会 {formation_name}")
            return

        # 布阵
        location = f"{player.nickname}的洞府"
        success, message = await FormationService.deploy_formation(
            session, player, formation.id, location, duration_hours
        )

        if success:
            result = await session.execute(
                select(FormationTemplate).where(FormationTemplate.id == formation.template_id)
            )
            template = result.scalar_one_or_none()

            msg = f"⚡ {message}\n\n"
            msg += f"📍 地点：{location}\n"
            msg += f"⏰ 持续：{duration_hours}小时\n\n"
            msg += f"【当前效果】\n"
            msg += f"🛡️ 防御：+{template.defense_bonus * (1 + formation.proficiency/200):.0f}\n"
            msg += f"⚔️ 攻击：+{template.attack_bonus * (1 + formation.proficiency/200):.0f}\n\n"
            msg += f"💰 消耗：{template.spirit_stone_cost}灵石 + {template.spiritual_power_cost}灵力"
        else:
            msg = f"❌ {message}"

        await update.message.reply_text(msg)


async def dismiss_formation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """撤阵 - /撤阵"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        success, message = await FormationService.dismiss_formation(session, player)

        if success:
            msg = f"✅ {message}"
        else:
            msg = f"❌ {message}"

        await update.message.reply_text(msg)


async def current_formation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看当前阵法 - /当前阵法"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        result = await session.execute(
            select(ActiveFormation).where(
                ActiveFormation.player_id == player.id,
                ActiveFormation.is_active == True
            )
        )
        active = result.scalar_one_or_none()

        if not active:
            await update.message.reply_text(
                "⚡ 当前没有激活的阵法\n\n"
                "💡 使用 /布阵 <阵法名> 布置阵法"
            )
            return

        result = await session.execute(
            select(PlayerFormation).where(PlayerFormation.id == active.formation_id)
        )
        formation = result.scalar_one_or_none()

        result = await session.execute(
            select(FormationTemplate).where(FormationTemplate.id == formation.template_id)
        )
        template = result.scalar_one_or_none()

        msg = "⚡ 【当前阵法】\n\n"
        msg += f"📖 {template.name}\n"
        msg += f"🏷️ {template.formation_type} | {template.grade}\n"
        msg += f"📍 地点：{active.location}\n\n"

        msg += "【当前效果】\n"
        msg += f"🛡️ 防御加成：+{active.current_defense_bonus}\n"
        msg += f"⚔️ 攻击加成：+{active.current_attack_bonus}\n\n"

        remaining = active.expires_at - datetime.now()
        if remaining.total_seconds() > 0:
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            msg += f"⏰ 剩余时间：{hours}小时{minutes}分钟\n"
        else:
            msg += "⚠️ 阵法已失效\n"

        msg += f"\n💡 使用 /撤阵 撤除阵法"

        await update.message.reply_text(msg)


async def break_formation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """破阵 - /破阵 <阵法ID>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定阵法ID\n"
            "用法：/破阵 <阵法ID>\n"
            "例如：/破阵 123"
        )
        return

    try:
        formation_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ 阵法ID必须是数字")
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        success, message, result_data = await FormationService.break_formation(
            session, player, formation_id
        )

        if success:
            msg = f"🎉 {message}\n\n"
            msg += f"⭐ 经验：+{result_data['exp_gained']}\n"
            msg += f"💰 灵石：+{result_data['stones_gained']}\n"
        else:
            msg = f"💥 {message}\n\n"
            if result_data.get("damage_taken"):
                msg += f"💔 受到伤害：{result_data['damage_taken']}\n"
                msg += f"❤️ 剩余生命：{player.hp}/{player.max_hp}"

        await update.message.reply_text(msg)


async def nearby_formations_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看附近阵法 - /附近阵法"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 获取所有激活的阵法（排除自己的）
        result = await session.execute(
            select(ActiveFormation).where(
                ActiveFormation.player_id != player.id,
                ActiveFormation.is_active == True,
                ActiveFormation.expires_at > datetime.now()
            ).limit(10)
        )
        formations = result.scalars().all()

        if not formations:
            await update.message.reply_text(
                "⚡ 附近没有发现阵法\n\n"
                "💡 使用 /布阵 <阵法名> 布置阵法"
            )
            return

        msg = "⚡ 【附近阵法】\n\n"

        for formation in formations:
            result = await session.execute(
                select(PlayerFormation).where(PlayerFormation.id == formation.formation_id)
            )
            player_formation = result.scalar_one_or_none()

            result = await session.execute(
                select(FormationTemplate).where(FormationTemplate.id == player_formation.template_id)
            )
            template = result.scalar_one_or_none()

            result = await session.execute(
                select(Player).where(Player.id == formation.player_id)
            )
            owner = result.scalar_one_or_none()

            msg += f"🆔 阵法ID: {formation.id}\n"
            msg += f"📖 {template.name} ({template.grade})\n"
            msg += f"👤 阵主：{owner.nickname if owner else '未知'}\n"
            msg += f"📍 {formation.location}\n"

            remaining = formation.expires_at - datetime.now()
            hours = int(remaining.total_seconds() // 3600)
            msg += f"⏰ 剩余：{hours}小时\n\n"

        msg += "━━━━━━━━━━━━━━\n"
        msg += "💡 使用 /破阵 <阵法ID> 尝试破阵"

        await update.message.reply_text(msg)


def register_handlers(application):
    """注册阵法相关处理器"""
    application.add_handler(CommandHandler("阵法", formation_list_command))
    application.add_handler(CommandHandler("阵法图谱", formation_codex_command))
    application.add_handler(CommandHandler("学习阵法", learn_formation_command))
    application.add_handler(CommandHandler("布阵", deploy_formation_command))
    application.add_handler(CommandHandler("撤阵", dismiss_formation_command))
    application.add_handler(CommandHandler("当前阵法", current_formation_command))
    application.add_handler(CommandHandler("破阵", break_formation_command))
    application.add_handler(CommandHandler("附近阵法", nearby_formations_command))
