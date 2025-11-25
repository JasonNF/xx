"""技能系统handlers - 凡人修仙传版本"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from bot.models.database import AsyncSessionLocal
from bot.models import Player, Skill, PlayerSkill
from bot.services import SkillService
from sqlalchemy import select


async def skills_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看已学技能 - /skills"""
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

        # 获取玩家技能
        skills = await SkillService.get_player_skills(session, player)

        if not skills:
            await update.message.reply_text(
                "📚 你还没有学会任何技能\n\n"
                "💡 使用 /学习 学习新技能"
            )
            return

        # 构建消息
        msg = "⚔️ 【已学技能】\n\n"
        msg += f"道友境界：{player.full_realm_name}\n"
        msg += f"💧 灵力：{player.spiritual_power}/{player.max_spiritual_power}\n"
        msg += "━━━━━━━━━━━━━━\n\n"

        for skill in skills:
            status = "✅" if skill["is_ready"] else "⏳"
            msg += f"{status} **{skill['name']}** (Lv.{skill['level']})\n"
            msg += f"   {skill['description']}\n"

            # 技能属性
            if skill['element']:
                element_icon = {
                    "金": "⚔️", "木": "🌲", "水": "💧",
                    "火": "🔥", "土": "🪨"
                }.get(skill['element'], "✨")
                msg += f"   {element_icon} {skill['element']}系 | "
            else:
                msg += f"   "

            msg += f"威力：{skill['base_power']} | "
            msg += f"消耗：{skill['spiritual_cost']}灵力\n"

            # 冷却状态
            if not skill['is_ready']:
                msg += f"   ⏳ 冷却中：{skill['cooldown_remaining']}秒\n"
            else:
                msg += f"   ⚡ 冷却：{skill['cooldown_rounds']}回合\n"

            # 熟练度
            msg += f"   📊 熟练度：{skill['proficiency']}/{(skill['level'] + 1) * 100}\n"
            msg += "\n"

        msg += "━━━━━━━━━━━━━━\n"
        msg += "💡 提示：\n"
        msg += "• 战斗中使用技能增加熟练度\n"
        msg += "• 熟练度满可升级技能（/升级）"

        await update.message.reply_text(msg, parse_mode="Markdown")


async def learn_skill_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """学习技能 - /learn_skill [技能名称]"""
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

        # 如果没有提供技能名称，显示可学习的技能列表
        if not context.args:
            # 获取所有技能
            result = await session.execute(select(Skill).order_by(Skill.learning_cost))
            all_skills = result.scalars().all()

            # 获取已学技能ID
            result = await session.execute(
                select(PlayerSkill.skill_id).where(PlayerSkill.player_id == player.id)
            )
            learned_skill_ids = {row[0] for row in result}

            # 可学习的技能
            available_skills = [s for s in all_skills if s.id not in learned_skill_ids]

            if not available_skills:
                await update.message.reply_text("🎉 恭喜！你已经学会所有可用技能")
                return

            msg = "📚 【可学习技能】\n\n"
            msg += f"道友境界：{player.full_realm_name}\n"
            msg += f"💰 灵石：{player.spirit_stones}\n"
            msg += "━━━━━━━━━━━━━━\n\n"

            for skill in available_skills:
                # 检查是否满足要求
                can_learn = True
                reason = ""

                # 检查境界要求
                if skill.required_realm:
                    from bot.models.player import RealmType
                    realm_order = {
                        RealmType.MORTAL: 0,
                        RealmType.QI_REFINING: 1,
                        RealmType.FOUNDATION: 2,
                        RealmType.CORE_FORMATION: 3,
                        RealmType.NASCENT_SOUL: 4,
                        RealmType.DEITY_TRANSFORMATION: 5,
                    }
                    if realm_order.get(player.realm, 0) < realm_order.get(skill.required_realm, 0):
                        can_learn = False
                        reason = f"需要{skill.required_realm.value}境界"

                # 检查灵根要求
                if can_learn and skill.required_spirit_root and player.spirit_root:
                    if skill.required_spirit_root not in player.spirit_root.element_list:
                        can_learn = False
                        reason = f"需要{skill.required_spirit_root}灵根"

                # 检查灵石
                if can_learn and player.spirit_stones < skill.learning_cost:
                    can_learn = False
                    reason = "灵石不足"

                status_icon = "✅" if can_learn else "🔒"
                element_icon = {
                    "金": "⚔️", "木": "🌲", "水": "💧",
                    "火": "🔥", "土": "🪨"
                }.get(skill.element, "✨") if skill.element else "✨"

                msg += f"{status_icon} **{skill.name}**\n"
                msg += f"   {skill.description}\n"
                msg += f"   {element_icon} 属性：{skill.element or '无'} | "
                msg += f"威力：{skill.base_power} | "
                msg += f"消耗：{skill.spiritual_cost}灵力\n"
                msg += f"   💰 学习费用：{skill.learning_cost} 灵石\n"

                if skill.required_realm:
                    msg += f"   📖 要求：{skill.required_realm.value}"
                    if skill.required_spirit_root:
                        msg += f" + {skill.required_spirit_root}灵根"
                    msg += "\n"

                if not can_learn:
                    msg += f"   ⚠️ {reason}\n"

                msg += "\n"

            msg += "━━━━━━━━━━━━━━\n"
            msg += "💡 使用方法：/学习 <技能名称>\n"
            msg += "例如：/学习 火球术"

            await update.message.reply_text(msg, parse_mode="Markdown")
            return

        # 学习指定技能
        skill_name = " ".join(context.args)

        # 获取技能
        result = await session.execute(
            select(Skill).where(Skill.name == skill_name)
        )
        skill = result.scalar_one_or_none()

        if not skill:
            await update.message.reply_text(
                f"❌ 未找到技能：{skill_name}\n"
                "使用 /学习 查看可学习技能"
            )
            return

        # 尝试学习
        success, message = await SkillService.learn_skill(session, player, skill)

        if success:
            element_icon = {
                "金": "⚔️", "木": "🌲", "水": "💧",
                "火": "🔥", "土": "🪨"
            }.get(skill.element, "✨") if skill.element else "✨"

            msg = f"🎉 {message}\n\n"
            msg += f"{element_icon} **{skill.name}**\n"
            msg += f"{skill.description}\n\n"
            msg += f"威力：{skill.base_power} | 消耗：{skill.spiritual_cost}灵力\n"
            msg += f"💰 花费：{skill.learning_cost} 灵石\n"
            msg += f"💰 剩余灵石：{player.spirit_stones}\n\n"
            msg += "💡 在战斗中使用此技能可增加熟练度"

            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ {message}")


async def upgrade_skill_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """升级技能 - /upgrade_skill [技能名称]"""
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

        # 如果没有提供技能名称，显示可升级的技能
        if not context.args:
            # 获取玩家所有技能
            result = await session.execute(
                select(PlayerSkill, Skill)
                .join(Skill, PlayerSkill.skill_id == Skill.id)
                .where(PlayerSkill.player_id == player.id)
                .order_by(PlayerSkill.skill_level.desc())
            )
            player_skills = result.all()

            if not player_skills:
                await update.message.reply_text(
                    "📚 你还没有学会任何技能\n\n"
                    "💡 使用 /学习 学习新技能"
                )
                return

            msg = "⬆️ 【技能升级】\n\n"
            msg += f"💰 灵石：{player.spirit_stones}\n"
            msg += "━━━━━━━━━━━━━━\n\n"

            upgradeable_count = 0
            for player_skill, skill in player_skills:
                next_level = player_skill.skill_level + 1
                required_proficiency = next_level * 100
                required_stones = skill.learning_cost * next_level

                can_upgrade = (
                    player_skill.skill_level < 10 and
                    player_skill.proficiency >= required_proficiency and
                    player.spirit_stones >= required_stones
                )

                if player_skill.skill_level >= 10:
                    status_icon = "⭐"
                    status = "已满级"
                elif can_upgrade:
                    status_icon = "✅"
                    status = "可升级"
                    upgradeable_count += 1
                else:
                    status_icon = "📊"
                    status = "修炼中"

                msg += f"{status_icon} **{skill.name}** (Lv.{player_skill.skill_level}) - {status}\n"

                if player_skill.skill_level < 10:
                    msg += f"   📊 熟练度：{player_skill.proficiency}/{required_proficiency}\n"
                    msg += f"   💰 升级费用：{required_stones} 灵石\n"

                    if not can_upgrade:
                        missing = []
                        if player_skill.proficiency < required_proficiency:
                            missing.append(f"熟练度差{required_proficiency - player_skill.proficiency}")
                        if player.spirit_stones < required_stones:
                            missing.append(f"灵石差{required_stones - player.spirit_stones}")
                        if missing:
                            msg += f"   ⚠️ {', '.join(missing)}\n"

                msg += "\n"

            msg += "━━━━━━━━━━━━━━\n"
            if upgradeable_count > 0:
                msg += f"💡 使用方法：/升级 <技能名称>\n"
                msg += "例如：/升级 火球术"
            else:
                msg += "💡 通过战斗使用技能来提升熟练度"

            await update.message.reply_text(msg, parse_mode="Markdown")
            return

        # 升级指定技能
        skill_name = " ".join(context.args)

        # 获取技能和玩家技能记录
        result = await session.execute(
            select(Skill).where(Skill.name == skill_name)
        )
        skill = result.scalar_one_or_none()

        if not skill:
            await update.message.reply_text(
                f"❌ 未找到技能：{skill_name}\n"
                "使用 /升级 查看可升级技能"
            )
            return

        result = await session.execute(
            select(PlayerSkill).where(
                PlayerSkill.player_id == player.id,
                PlayerSkill.skill_id == skill.id
            )
        )
        player_skill = result.scalar_one_or_none()

        if not player_skill:
            await update.message.reply_text(f"❌ 你还没有学会 {skill_name}")
            return

        # 尝试升级
        old_level = player_skill.skill_level
        success, message = await SkillService.upgrade_skill(
            session, player, skill, player_skill
        )

        if success:
            msg = f"⬆️ {message}\n\n"
            msg += f"**{skill.name}**\n"
            msg += f"等级：Lv.{old_level} → Lv.{player_skill.skill_level}\n"
            msg += f"威力提升：{int(skill.base_power * (1 + (old_level - 1) * 0.1))} → "
            msg += f"{int(skill.base_power * (1 + (player_skill.skill_level - 1) * 0.1))}\n\n"
            msg += f"💰 剩余灵石：{player.spirit_stones}\n"
            msg += f"📊 剩余熟练度：{player_skill.proficiency}"

            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ {message}")


def register_handlers(application):
    """注册技能相关处理器"""
    application.add_handler(CommandHandler("技能", skills_command))
    application.add_handler(CommandHandler("学习", learn_skill_command))
    application.add_handler(CommandHandler("升级", upgrade_skill_command))
