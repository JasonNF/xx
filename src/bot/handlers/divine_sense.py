"""神识系统handlers - 凡人修仙传版本"""
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes, CommandHandler

from bot.models.database import AsyncSessionLocal
from bot.models import Player
from sqlalchemy import select


async def divine_sense_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看神识信息 - /神识"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        msg = "🔮 【神识信息】\n\n"

        # 判断是否觉醒神识
        from bot.models import RealmType
        if player.realm in [RealmType.MORTAL, RealmType.QI_REFINING]:
            msg += "⚠️ 神识未觉醒\n\n"
            msg += "💡 筑基后方能觉醒神识\n"
            msg += f"📊 当前境界：{player.full_realm_name}"
            await update.message.reply_text(msg)
            return

        # 已觉醒神识
        msg += f"✨ 神识强度：{player.divine_sense}/{player.max_divine_sense}\n\n"

        # 根据神识强度计算能力范围
        sense_range = player.divine_sense // 10  # 每10点神识1米感知范围
        control_weight = player.divine_sense // 5  # 每5点神识可御物1斤

        msg += "【神识能力】\n"
        msg += f"👁️ 感知范围：{sense_range}米\n"
        msg += f"🪶 御物重量：{control_weight}斤\n"
        msg += f"⚔️ 战斗加成：+{player.divine_sense//20}%\n\n"

        # 神识等级
        sense_level = "微弱"
        if player.divine_sense >= 1000:
            sense_level = "强大"
        elif player.divine_sense >= 500:
            sense_level = "充裕"
        elif player.divine_sense >= 200:
            sense_level = "尚可"

        msg += f"🏅 神识等级：{sense_level}\n\n"

        msg += "━━━━━━━━━━━━━━\n"
        msg += "💡 使用 /修炼神识 提升神识强度\n"
        msg += "💡 使用 /探查 <玩家> 探查对方信息"

        await update.message.reply_text(msg)


async def train_divine_sense_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """修炼神识 - /修炼神识 [时长]"""
    user = update.effective_user

    if not context.args:
        duration_hours = 1
    else:
        try:
            duration_hours = int(context.args[0])
            if duration_hours not in [1, 2, 4, 8]:
                await update.message.reply_text("❌ 时长只能是 1、2、4、8 小时")
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

        # 检查境界
        from bot.models import RealmType
        if player.realm in [RealmType.MORTAL, RealmType.QI_REFINING]:
            await update.message.reply_text("❌ 筑基后方能修炼神识")
            return

        # 检查状态
        if player.is_cultivating:
            await update.message.reply_text("❌ 修炼中无法修炼神识")
            return

        if player.is_in_battle:
            await update.message.reply_text("❌ 战斗中无法修炼神识")
            return

        # 消耗灵力
        spirit_cost = duration_hours * 50
        if player.spiritual_power < spirit_cost:
            await update.message.reply_text(f"❌ 灵力不足，需要 {spirit_cost} 灵力")
            return

        player.spiritual_power -= spirit_cost

        # 基础增长：每小时 5-10 点
        base_gain = duration_hours * (5 + player.comprehension // 2)

        # 悟性加成
        comprehension_bonus = int(base_gain * (player.comprehension / 100))

        # 灵根加成
        spirit_root_bonus = 0
        if player.spirit_root:
            spirit_root_bonus = int(base_gain * player.spirit_root.cultivation_speed_bonus)

        total_gain = base_gain + comprehension_bonus + spirit_root_bonus

        # 增加神识
        player.divine_sense = min(player.divine_sense + total_gain, player.max_divine_sense)

        await session.commit()

        msg = f"🔮 修炼神识 {duration_hours} 小时\n\n"
        msg += f"✨ 神识增长：+{total_gain}\n"
        msg += f"💧 消耗灵力：{spirit_cost}\n\n"
        msg += f"📊 当前神识：{player.divine_sense}/{player.max_divine_sense}\n"
        msg += f"💧 剩余灵力：{player.spiritual_power}/{player.max_spiritual_power}"

        await update.message.reply_text(msg)


async def probe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """探查玩家 - /探查"""
    user = update.effective_user

    # 检查是否回复了某人的消息
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "❌ 请回复要探查的玩家消息\n"
            "用法：在对方消息上回复 /探查"
        )
        return

    target_user = update.message.reply_to_message.from_user

    async with AsyncSessionLocal() as session:
        # 获取探查者
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 检查神识
        if player.divine_sense < 50:
            await update.message.reply_text("❌ 神识不足，需要至少 50 点神识")
            return

        # 获取目标
        result = await session.execute(
            select(Player).where(Player.telegram_id == target_user.id)
        )
        target = result.scalar_one_or_none()

        if not target:
            await update.message.reply_text("❌ 对方还未开始游戏")
            return

        # 消耗神识
        sense_cost = 10
        player.divine_sense = max(0, player.divine_sense - sense_cost)

        await session.commit()

        # 判断能否探查成功
        # 如果目标神识高于探查者,可能失败
        success_rate = 0.8
        if target.divine_sense > player.divine_sense:
            diff = target.divine_sense - player.divine_sense
            success_rate = max(0.3, 0.8 - (diff / player.divine_sense))

        import random
        if random.random() > success_rate:
            msg = "💥 探查失败！\n\n"
            msg += "⚠️ 对方神识过于强大，反制了您的探查\n"
            msg += f"💫 消耗神识：{sense_cost}"
            await update.message.reply_text(msg)
            return

        # 探查成功
        msg = f"🔍 【探查结果】\n\n"
        msg += f"👤 道号：{target.nickname}\n"
        msg += f"🌟 境界：{target.realm}"
        if target.realm == "炼气期":
            msg += f" {target.level}层\n"
        else:
            msg += "\n"

        msg += f"⚔️ 攻击：{target.attack}\n"
        msg += f"🛡️ 防御：{target.defense}\n"
        msg += f"⚡ 速度：{target.speed}\n"

        if player.divine_sense >= target.divine_sense * 1.5:
            # 神识远超对方,能看到更多信息
            msg += f"\n❤️ 生命：{target.hp}/{target.max_hp}\n"
            msg += f"💧 灵力：{target.spiritual_power}/{target.max_spiritual_power}\n"

            if target.spirit_root:
                elements = target.spirit_root.roots
                msg += f"💎 灵根：{elements}\n"

        msg += f"\n💫 消耗神识：{sense_cost}"

        await update.message.reply_text(msg)


async def divine_sense_scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """神识扫描周围 - /神识扫描"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 检查神识
        if player.divine_sense < 100:
            await update.message.reply_text("❌ 神识不足，需要至少 100 点神识")
            return

        # 消耗神识
        sense_cost = 30
        player.divine_sense = max(0, player.divine_sense - sense_cost)

        # 扫描范围内的玩家（模拟）
        # 实际应该根据地理位置或房间系统
        result = await session.execute(
            select(Player).where(
                Player.id != player.id,
                Player.realm != "凡人"
            ).limit(5)
        )
        nearby_players = result.scalars().all()

        await session.commit()

        msg = "🔮 【神识扫描】\n\n"
        msg += f"📡 感知范围：{player.divine_sense//10}米\n\n"

        if not nearby_players:
            msg += "⚠️ 附近没有发现其他修士\n"
        else:
            msg += "发现以下修士：\n\n"
            for i, p in enumerate(nearby_players, 1):
                distance = (100 - i * 15)  # 模拟距离
                msg += f"{i}. {p.nickname}\n"
                msg += f"   境界：{p.realm}"
                if p.realm == "炼气期":
                    msg += f" {p.level}层"
                msg += f" | 距离：约{distance}米\n\n"

        msg += f"💫 消耗神识：{sense_cost}\n"
        msg += f"📊 剩余神识：{player.divine_sense}/{player.max_divine_sense}"

        await update.message.reply_text(msg)


def register_handlers(application):
    """注册神识相关处理器"""
    application.add_handler(MessageHandler(filters.Regex(r"^\.神识"), divine_sense_info_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.修炼神识"), train_divine_sense_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.探查"), probe_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.神识扫描"), divine_sense_scan_command))
