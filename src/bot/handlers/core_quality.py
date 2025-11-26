"""金丹品质系统handlers"""
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.models.database import AsyncSessionLocal
from bot.models import Player
from bot.services.core_quality_service import CoreQualityService
from sqlalchemy import select


async def core_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看金丹信息 - /金丹"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        player_core = await CoreQualityService.get_player_core(session, player)

        if not player_core:
            msg = "💫 【金丹信息】\n\n"
            msg += "⚠️ 您还未结丹\n\n"
            from bot.models import RealmType
            if player.realm == RealmType.FOUNDATION and player.realm_level >= 2:
                msg += "✅ 您已达到筑基后期，可以尝试结丹\n"
                msg += "💡 使用 /结丹 尝试结丹"
            else:
                msg += f"📊 当前境界：{player.full_realm_name}\n"
                msg += "💡 需要达到筑基后期才能尝试结丹"
        else:
            msg = "💫 【金丹信息】\n\n"
            msg += f"✨ 品质：{player_core.quality}/100\n"
            msg += f"🏅 等级：{player_core.grade}\n\n"

            if player_core.has_dao_pattern:
                msg += f"🌟 道纹：{player_core.dao_pattern_count}道\n\n"

            msg += "【加成效果】\n"
            msg += f"⚡ 修炼速度：+{player_core.cultivation_speed_bonus*100:.1f}%\n"
            msg += f"⚔️ 攻击力：+{player_core.attack_bonus}\n"
            msg += f"🛡️ 防御力：+{player_core.defense_bonus}\n"
            msg += f"❤️ 生命值：+{player_core.hp_bonus}\n"
            msg += f"💧 灵力：+{player_core.spiritual_power_bonus}\n\n"

            msg += f"📅 结丹时间：{player_core.formed_at.strftime('%Y-%m-%d')}\n"
            msg += f"🔮 使用丹药品质：{player_core.pill_quality}\n\n"

            if player_core.quality < 100:
                msg += "━━━━━━━━━━━━━━\n"
                msg += "💡 使用 /祭炼金丹 <方法> [风险等级] 提升品质"

        await update.message.reply_text(msg)


async def core_formation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """尝试结丹 - /结丹 [丹药ID]"""
    user = update.effective_user

    pill_item_id = None
    if context.args:
        try:
            pill_item_id = int(context.args[0])
        except ValueError:
            pass

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        success, message, result_data = await CoreQualityService.attempt_core_formation(
            session, player, pill_item_id
        )

        if not success:
            await update.message.reply_text(f"❌ {message}")
            return

        msg = f"🎉 {message}\n\n"
        msg += f"✨ 金丹品质：{result_data['quality']}/100\n"
        msg += f"🏅 品质等级：{result_data['grade']}\n\n"

        if result_data.get("has_dao_pattern"):
            msg += f"🌟 恭喜！金丹凝聚出 {result_data['dao_pattern_count']} 道道纹！\n\n"

        bonuses = result_data["bonuses"]
        msg += "【获得加成】\n"
        msg += f"⚡ 修炼速度：+{bonuses['cultivation_speed_bonus']*100:.1f}%\n"
        msg += f"⚔️ 攻击力：+{bonuses['attack_bonus']}\n"
        msg += f"🛡️ 防御力：+{bonuses['defense_bonus']}\n"
        msg += f"❤️ 生命值：+{bonuses['hp_bonus']}\n"
        msg += f"💧 灵力：+{bonuses['spiritual_power_bonus']}\n\n"

        msg += f"🎊 您已突破到结丹期！"

        await update.message.reply_text(msg)


async def refine_core_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """祭炼金丹 - /祭炼金丹 <方法> [风险等级]"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定祭炼方法\n\n"
            "用法：/祭炼金丹 <方法> [风险等级]\n\n"
            "方法选项：\n"
            "- 天材地宝\n"
            "- 灵兽精血\n"
            "- 天雷淬炼\n"
            "- 地火焚炼\n\n"
            "风险等级：1-10（默认为1）\n"
            "风险越高，提升越大，但失败概率也越高\n"
            "风险≥7时失败可能导致品质下降！\n\n"
            "例如：/祭炼金丹 天雷淬炼 5"
        )
        return

    method = context.args[0]
    risk_level = 1

    if len(context.args) > 1:
        try:
            risk_level = int(context.args[1])
            if risk_level < 1 or risk_level > 10:
                await update.message.reply_text("❌ 风险等级必须在1-10之间")
                return
        except ValueError:
            await update.message.reply_text("❌ 风险等级必须是数字")
            return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        success, message, result_data = await CoreQualityService.refine_core(
            session, player, method, None, risk_level
        )

        msg = ""
        if success:
            msg += f"🎉 {message}\n\n"
            msg += f"📊 品质变化：{result_data['quality_before']} → {result_data['quality_after']}\n"
            msg += f"📈 提升：+{result_data['quality_gain']}\n"

            if result_data.get("grade_up"):
                msg += f"\n🎊 品质升级！晋升为 {result_data['new_grade']}！\n"

            if result_data.get("dao_pattern_gained"):
                msg += f"\n🌟 恭喜！金丹凝聚出道纹！\n"
        else:
            msg += f"💥 {message}\n\n"
            msg += f"📊 品质变化：{result_data['quality_before']} → {result_data['quality_after']}\n"

            if result_data['quality_gain'] < 0:
                msg += f"📉 下降：{result_data['quality_gain']}\n"
                msg += f"\n⚠️ 高风险祭炼失败，金丹受损！"
            else:
                msg += f"💡 品质未变化，可以再次尝试\n"

        await update.message.reply_text(msg)


async def core_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看结丹记录 - /结丹记录"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        from bot.models.core_quality import CoreFormationAttempt

        result = await session.execute(
            select(CoreFormationAttempt).where(
                CoreFormationAttempt.player_id == player.id
            ).order_by(CoreFormationAttempt.attempted_at.desc()).limit(10)
        )
        attempts = result.scalars().all()

        if not attempts:
            await update.message.reply_text("📜 暂无结丹记录")
            return

        msg = "📜 【结丹记录】\n\n"

        for i, attempt in enumerate(attempts, 1):
            status = "✅ 成功" if attempt.is_success else "❌ 失败"
            msg += f"{i}. {status}\n"
            msg += f"   境界：筑基 {attempt.cultivation_level}层\n"

            if attempt.is_success and attempt.core_quality:
                msg += f"   品质：{attempt.core_quality}/100\n"
            elif not attempt.is_success and attempt.failure_reason:
                msg += f"   原因：{attempt.failure_reason}\n"

            msg += f"   时间：{attempt.attempted_at.strftime('%Y-%m-%d %H:%M')}\n\n"

        await update.message.reply_text(msg)


async def refine_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看祭炼记录 - /祭炼记录"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        from bot.models.core_quality import CoreRefinementRecord

        result = await session.execute(
            select(CoreRefinementRecord).where(
                CoreRefinementRecord.player_id == player.id
            ).order_by(CoreRefinementRecord.refined_at.desc()).limit(10)
        )
        records = result.scalars().all()

        if not records:
            await update.message.reply_text("📜 暂无祭炼记录")
            return

        msg = "📜 【祭炼记录】\n\n"

        for i, record in enumerate(records, 1):
            status = "✅ 成功" if record.is_success else "❌ 失败"
            change_icon = "📈" if record.quality_gain > 0 else "📉" if record.quality_gain < 0 else "➖"

            msg += f"{i}. {status} - {record.method}\n"
            msg += f"   {record.quality_before} → {record.quality_after} ({change_icon}{record.quality_gain:+d})\n"
            msg += f"   风险等级：{record.risk_level}/10\n"
            msg += f"   时间：{record.refined_at.strftime('%Y-%m-%d %H:%M')}\n\n"

        await update.message.reply_text(msg)


def register_handlers(application):
    """注册金丹品质相关处理器"""
    application.add_handler(CommandHandler("金丹", core_info_command))
    application.add_handler(CommandHandler("结丹", core_formation_command))
    application.add_handler(CommandHandler("祭炼金丹", refine_core_command))
    application.add_handler(CommandHandler("结丹记录", core_history_command))
    application.add_handler(CommandHandler("祭炼记录", refine_history_command))
