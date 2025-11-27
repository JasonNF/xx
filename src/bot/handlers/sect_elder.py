"""传功长老系统 - 宗门功法学习"""
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes, CommandHandler

from bot.models.database import AsyncSessionLocal
from bot.models import Player, Sect, RealmType
from bot.models.player import CultivationMethod
from bot.services.sect_service import SectService
from sqlalchemy import select, and_


async def sect_methods_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看宗门功法 - /宗门功法"""
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

        # 检查是否在宗门
        if not player.sect_id:
            await update.message.reply_text(
                "❌ 你还没有加入宗门\n"
                "使用 /入门 <宗门名> 加入宗门后可学习宗门功法"
            )
            return

        # 获取宗门信息
        result = await session.execute(
            select(Sect).where(Sect.id == player.sect_id)
        )
        sect = result.scalar_one_or_none()

        if not sect:
            await update.message.reply_text("❌ 宗门不存在")
            return

        # 获取当前职位和等级
        current_position = SectService.get_position_by_reputation(player.contribution)
        position_level = current_position["level"]

        # 获取当前功法
        current_method = None
        if player.cultivation_method_id:
            result = await session.execute(
                select(CultivationMethod).where(CultivationMethod.id == player.cultivation_method_id)
            )
            current_method = result.scalar_one_or_none()

        # 获取本宗门的功法
        result = await session.execute(
            select(CultivationMethod)
            .where(CultivationMethod.sect_id == sect.id)
            .order_by(CultivationMethod.required_position_level, CultivationMethod.learning_cost)
        )
        sect_methods = result.scalars().all()

        if not sect_methods:
            await update.message.reply_text(
                f"📖 【{sect.name} 传功阁】\n\n"
                "暂无宗门功法,请联系掌门配置功法"
            )
            return

        # 构建消息
        msg = f"📖 【{sect.name} 传功阁】\n\n"
        msg += f"传功长老: 欢迎{player.nickname}道友\n"
        msg += f"你的职位: {player.sect_position or current_position['name']}\n"
        msg += f"你的境界: {player.full_realm_name}\n"

        if current_method:
            msg += f"当前功法: {current_method.name} ({current_method.grade})\n"

        msg += f"💰 灵石: {player.spirit_stones}\n"
        msg += "━━━━━━━━━━━━━━\n\n"

        # 按职位等级分组显示
        methods_by_position = {}
        for method in sect_methods:
            pos_level = method.required_position_level or 1
            if pos_level not in methods_by_position:
                methods_by_position[pos_level] = []
            methods_by_position[pos_level].append(method)

        # 职位等级对应名称
        position_names = {
            1: "外门弟子", 2: "内门弟子", 3: "真传弟子",
            4: "执事", 5: "堂主", 6: "长老", 7: "掌门"
        }

        for pos_level in sorted(methods_by_position.keys()):
            pos_name = position_names.get(pos_level, f"Lv.{pos_level}")
            methods = methods_by_position[pos_level]

            msg += f"【{pos_name}功法】\n\n"

            for method in methods:
                # 检查是否可学
                can_learn = True
                reasons = []

                # 职位要求
                if position_level < pos_level:
                    can_learn = False
                    reasons.append(f"需要{pos_name}")

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
                    reasons.append(f"需要{method.required_realm.value}")

                # 灵石要求
                if player.spirit_stones < method.learning_cost:
                    can_learn = False
                    reasons.append("灵石不足")

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
                msg += f"   {method.description[:40]}...\n"
                msg += f"   类型: {method.method_type}\n"

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
                    msg += f"   效果: {', '.join(effects)}\n"

                msg += f"   💰 {method.learning_cost} 灵石\n"

                if not can_learn and not is_current:
                    msg += f"   ⚠️ {', '.join(reasons)}\n"

                msg += "\n"

            msg += "━━━━━━━━━━━━━━\n\n"

        msg += "💡 使用 /传功 <功法名> 学习宗门功法\n"
        msg += "💡 学习后即使退出宗门也保留功法"

        await update.message.reply_text(msg, parse_mode="Markdown")


async def learn_sect_method_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """学习宗门功法 - /传功 <功法名>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定功法名称\n"
            "用法: /传功 <功法名称>\n"
            "例如: /传功 青罡剑诀\n\n"
            "使用 /宗门功法 查看可学功法"
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

        # 检查是否在宗门
        if not player.sect_id:
            await update.message.reply_text("❌ 你还没有加入宗门")
            return

        # 获取功法
        result = await session.execute(
            select(CultivationMethod).where(
                and_(
                    CultivationMethod.name == method_name,
                    CultivationMethod.sect_id == player.sect_id
                )
            )
        )
        method = result.scalar_one_or_none()

        if not method:
            await update.message.reply_text(
                f"❌ 本宗门没有功法: {method_name}\n"
                "使用 /宗门功法 查看本宗门可学功法"
            )
            return

        # 检查是否已学
        if player.cultivation_method_id == method.id:
            await update.message.reply_text(f"❌ 你已经在修炼 {method.name} 了")
            return

        # 获取当前职位等级
        current_position = SectService.get_position_by_reputation(player.contribution)
        position_level = current_position["level"]

        # 检查职位要求
        required_pos_level = method.required_position_level or 1
        if position_level < required_pos_level:
            position_names = {
                1: "外门弟子", 2: "内门弟子", 3: "真传弟子",
                4: "执事", 5: "堂主", 6: "长老", 7: "掌门"
            }
            await update.message.reply_text(
                f"❌ 职位不足\n"
                f"需要: {position_names.get(required_pos_level, f'Lv.{required_pos_level}')}\n"
                f"当前: {player.sect_position or current_position['name']}"
            )
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
                f"需要: {method.required_realm.value}\n"
                f"当前: {player.full_realm_name}"
            )
            return

        # 检查灵石
        if player.spirit_stones < method.learning_cost:
            await update.message.reply_text(
                f"❌ 灵石不足\n\n"
                f"需要: {method.learning_cost}\n"
                f"拥有: {player.spirit_stones}"
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

        # 获取宗门信息
        result = await session.execute(
            select(Sect).where(Sect.id == player.sect_id)
        )
        sect = result.scalar_one_or_none()
        sect_name = sect.name if sect else "宗门"

        # 构建消息
        if old_method_name == "无":
            msg = f"🎉 在传功长老指导下,学会了{sect_name}功法!\n\n"
        else:
            msg = f"🎉 在传功长老指导下,从 {old_method_name} 转修宗门功法!\n\n"

        msg += f"📖 **{method.name}** ({method.grade})\n"
        msg += f"类型: {method.method_type}\n\n"

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

        msg += f"\n💰 花费: {method.learning_cost} 灵石\n"
        msg += f"💰 剩余: {player.spirit_stones} 灵石\n\n"
        msg += "✨ 功法已永久学会,退出宗门后依然可用"

        await update.message.reply_text(msg, parse_mode="Markdown")


def register_handlers(application):
    """注册传功长老相关处理器"""
    application.add_handler(MessageHandler(filters.Regex(r"^\.宗门功法"), sect_methods_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.传功"), learn_sect_method_command))
