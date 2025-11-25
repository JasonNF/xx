"""功法系统handlers - 凡人修仙传版本"""
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.models.database import AsyncSessionLocal
from bot.models import Player, RealmType
from bot.models.player import CultivationMethod
from sqlalchemy import select


async def methods_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看可学功法 - /功法"""
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

        # 获取当前功法
        current_method = None
        if player.cultivation_method_id:
            result = await session.execute(
                select(CultivationMethod).where(CultivationMethod.id == player.cultivation_method_id)
            )
            current_method = result.scalar_one_or_none()

        # 获取所有功法
        result = await session.execute(
            select(CultivationMethod).order_by(CultivationMethod.required_realm, CultivationMethod.learning_cost)
        )
        methods = result.scalars().all()

        if not methods:
            await update.message.reply_text("📖 暂无可学功法")
            return

        # 构建消息
        msg = "📖 【功法列表】\n\n"
        msg += f"道友：{player.nickname}\n"
        msg += f"境界：{player.full_realm_name}\n"

        if current_method:
            msg += f"当前功法：{current_method.name} ({current_method.grade})\n"

        msg += f"💰 灵石：{player.spirit_stones}\n"
        msg += "━━━━━━━━━━━━━━\n\n"

        for method in methods:
            # 检查是否可学
            can_learn = True
            reason = ""

            # 境界要求
            realm_order = {
                RealmType.MORTAL: 0,
                RealmType.QI_REFINING: 1,
                RealmType.FOUNDATION: 2,
                RealmType.CORE_FORMATION: 3,
                RealmType.NASCENT_SOUL: 4,
                RealmType.DEITY_TRANSFORMATION: 5,
            }

            if realm_order.get(player.realm, 0) < realm_order.get(method.required_realm, 0):
                can_learn = False
                reason = f"需要{method.required_realm.value}"

            # 灵石要求
            if can_learn and player.spirit_stones < method.learning_cost:
                can_learn = False
                reason = "灵石不足"

            # 是否当前功法
            is_current = current_method and current_method.id == method.id

            status_icon = "⭐" if is_current else ("✅" if can_learn else "🔒")

            grade_icon = {
                "人级": "📘",
                "黄级": "📙",
                "玄级": "📗",
                "地级": "📕",
                "天级": "📔"
            }.get(method.grade, "📖")

            msg += f"{status_icon} {grade_icon} **{method.name}** ({method.grade})\n"
            msg += f"    {method.description[:40]}...\n"
            msg += f"    类型：{method.method_type}\n"

            # 效果
            effects = []
            if method.cultivation_speed_bonus > 1.0:
                bonus_pct = int((method.cultivation_speed_bonus - 1.0) * 100)
                effects.append(f"修炼+{bonus_pct}%")
            if method.attack_bonus > 0:
                effects.append(f"攻击+{method.attack_bonus}")
            if method.defense_bonus > 0:
                effects.append(f"防御+{method.defense_bonus}")
            if method.hp_bonus > 0:
                effects.append(f"生命+{method.hp_bonus}")

            if effects:
                msg += f"    效果：{', '.join(effects)}\n"

            msg += f"    💰 {method.learning_cost} 灵石\n"

            if not can_learn and not is_current:
                msg += f"    ⚠️ {reason}\n"

            msg += "\n"

        msg += "━━━━━━━━━━━━━━\n"
        msg += "💡 使用 /修炼功法 <功法名> 学习或切换功法"

        await update.message.reply_text(msg, parse_mode="Markdown")


async def learn_method_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """学习/切换功法 - /修炼功法 <功法名>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定功法名称\n"
            "用法：/修炼功法 <功法名称>\n"
            "例如：/修炼功法 长春功"
        )
        return

    method_name = " ".join(context.args)

    async with AsyncSessionLocal() as session:
        # 获取玩家
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 获取功法
        result = await session.execute(
            select(CultivationMethod).where(CultivationMethod.name == method_name)
        )
        method = result.scalar_one_or_none()

        if not method:
            await update.message.reply_text(
                f"❌ 未找到功法：{method_name}\n"
                "使用 /功法 查看可学功法"
            )
            return

        # 检查是否已学
        if player.cultivation_method_id == method.id:
            await update.message.reply_text(f"❌ 你已经在修炼 {method.name} 了")
            return

        # 检查境界要求
        realm_order = {
            RealmType.MORTAL: 0,
            RealmType.QI_REFINING: 1,
            RealmType.FOUNDATION: 2,
            RealmType.CORE_FORMATION: 3,
            RealmType.NASCENT_SOUL: 4,
            RealmType.DEITY_TRANSFORMATION: 5,
        }

        if realm_order.get(player.realm, 0) < realm_order.get(method.required_realm, 0):
            await update.message.reply_text(
                f"❌ 境界不足\n"
                f"需要：{method.required_realm.value}\n"
                f"当前：{player.full_realm_name}"
            )
            return

        # 检查灵石
        if player.spirit_stones < method.learning_cost:
            await update.message.reply_text(
                f"❌ 灵石不足\n\n"
                f"需要：{method.learning_cost}\n"
                f"拥有：{player.spirit_stones}"
            )
            return

        # 获取旧功法名
        old_method_name = "无"
        if player.cultivation_method_id:
            result = await session.execute(
                select(CultivationMethod).where(CultivationMethod.id == player.cultivation_method_id)
            )
            old_method = result.scalar_one_or_none()
            if old_method:
                old_method_name = old_method.name
                # 移除旧功法加成
                player.attack -= old_method.attack_bonus
                player.defense -= old_method.defense_bonus
                player.max_hp -= old_method.hp_bonus
                player.max_spiritual_power -= old_method.spiritual_power_bonus

        # 扣除灵石
        player.spirit_stones -= method.learning_cost

        # 学习新功法
        player.cultivation_method_id = method.id

        # 应用新功法加成
        player.attack += method.attack_bonus
        player.defense += method.defense_bonus
        player.max_hp += method.hp_bonus
        player.max_spiritual_power += method.spiritual_power_bonus

        # 恢复HP和灵力到新上限
        player.hp = min(player.hp, player.max_hp)
        player.spiritual_power = min(player.spiritual_power, player.max_spiritual_power)

        await session.commit()

        # 构建消息
        if old_method_name == "无":
            msg = f"📖 学习了 {method.name}！\n\n"
        else:
            msg = f"📖 从 {old_method_name} 转修 {method.name}！\n\n"

        msg += f"品级：{method.grade}\n"
        msg += f"类型：{method.method_type}\n\n"

        # 效果
        if method.cultivation_speed_bonus > 1.0:
            bonus_pct = int((method.cultivation_speed_bonus - 1.0) * 100)
            msg += f"⚡ 修炼速度 +{bonus_pct}%\n"

        if method.attack_bonus > 0:
            msg += f"⚔️ 攻击 +{method.attack_bonus}\n"
        if method.defense_bonus > 0:
            msg += f"🛡️ 防御 +{method.defense_bonus}\n"
        if method.hp_bonus > 0:
            msg += f"❤️ 生命上限 +{method.hp_bonus}\n"
        if method.spiritual_power_bonus > 0:
            msg += f"💧 灵力上限 +{method.spiritual_power_bonus}\n"

        msg += f"\n💰 花费：{method.learning_cost} 灵石\n"
        msg += f"💰 剩余：{player.spirit_stones} 灵石"

        await update.message.reply_text(msg)


def register_handlers(application):
    """注册功法相关处理器"""
    application.add_handler(CommandHandler("功法", methods_command))
    application.add_handler(CommandHandler("修炼功法", learn_method_command))
