"""战斗系统handlers - 整合技能系统"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from bot.models.database import AsyncSessionLocal
from bot.models import Player, Monster, PlayerSkill, Skill
from bot.services import BattleService, SkillService
from bot.services.battle_strategy import BattleAI, BattleStrategy
from sqlalchemy import select
import random


async def battle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """开始PVE战斗 - /battle [怪物名称]"""
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

        # 如果没有指定怪物,显示可战斗的怪物列表
        if not context.args:
            can_battle, reason = await BattleService.can_battle_pve(player)
            if not can_battle:
                await update.message.reply_text(f"❌ {reason}")
                return

            # 获取适合的怪物
            monsters = await BattleService.get_random_monsters(session, player, 5)

            if not monsters:
                await update.message.reply_text("🏜️ 当前没有适合你的对手")
                return

            msg = "⚔️ 【可挑战的对手】\n\n"
            msg += f"道友境界：{player.full_realm_name}\n"
            msg += f"❤️ 生命：{player.hp}/{player.max_hp}\n"
            msg += f"⚡ 战力：{player.combat_power}\n"
            msg += "━━━━━━━━━━━━━━\n\n"

            for monster in monsters:
                monster_power = monster.attack * 10 + monster.hp
                power_ratio = player.combat_power / monster_power if monster_power > 0 else 1.0

                if power_ratio >= 1.2:
                    difficulty = "😊 简单"
                elif power_ratio >= 0.9:
                    difficulty = "😐 普通"
                elif power_ratio >= 0.7:
                    difficulty = "😰 困难"
                else:
                    difficulty = "💀 极难"

                msg += f"👹 **{monster.name}** ({monster.level}级)\n"
                msg += f"   {monster.description}\n"
                msg += f"   ❤️ 生命：{monster.hp} | ⚔️ 攻击：{monster.attack}\n"
                msg += f"   🛡️ 防御：{monster.defense} | ⚡ 速度：{monster.speed}\n"
                msg += f"   难度：{difficulty}\n"
                msg += f"   🎁 奖励：{monster.exp_reward}修为 + {monster.spirit_stones_min}-{monster.spirit_stones_max}灵石\n"
                msg += f"   💡 /战斗 {monster.name}\n\n"

            msg += "━━━━━━━━━━━━━━\n"
            msg += "💡 选择对手开始战斗"

            await update.message.reply_text(msg, parse_mode="Markdown")
            return

        # 挑战指定怪物
        monster_name = " ".join(context.args)

        # 检查是否可以战斗
        can_battle, reason = await BattleService.can_battle_pve(player)
        if not can_battle:
            await update.message.reply_text(f"❌ {reason}")
            return

        # 获取怪物
        result = await session.execute(
            select(Monster).where(Monster.name == monster_name)
        )
        monster = result.scalar_one_or_none()

        if not monster:
            await update.message.reply_text(
                f"❌ 未找到怪物：{monster_name}\n"
                "使用 /战斗 查看可挑战对手"
            )
            return

        # 发送战斗开始消息
        msg = f"⚔️ 战斗开始！\n\n"
        msg += f"💚 {player.nickname} ({player.full_realm_name})\n"
        msg += f"   ❤️ {player.hp}/{player.max_hp} | ⚡ {player.combat_power}\n\n"
        msg += f"💔 {monster.name} ({monster.level}级)\n"
        msg += f"   ❤️ {monster.hp} | ⚔️ {monster.attack} | 🛡️ {monster.defense}\n\n"
        msg += "⏳ 战斗进行中..."

        await update.message.reply_text(msg)

        # 执行战斗
        result, battle_log, rewards = await BattleService.battle_pve(
            session, player, monster
        )

        # 发送战斗日志
        log_msg = "```\n" + "\n".join(battle_log) + "\n```"
        await update.message.reply_text(log_msg, parse_mode="Markdown")

        # 发送结果摘要
        if "exp" in rewards:
            summary = f"🎉 战斗胜利！\n\n"
            summary += f"⭐ 修为：+{rewards['exp']}\n"
            summary += f"💰 灵石：+{rewards['spirit_stones']}\n\n"
            summary += f"当前修为：{player.cultivation_exp}/{player.next_realm_exp}\n"
            summary += f"❤️ 剩余生命：{player.hp}/{player.max_hp}"
        else:
            summary = f"💀 战斗失败\n\n"
            summary += f"❤️ 剩余生命：{player.hp}/{player.max_hp}\n"
            summary += "建议恢复后再次挑战"

        await update.message.reply_text(summary)


async def battle_pvp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """PVP战斗 - /pvp [@username 或 回复消息]"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        # 获取攻击方
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        attacker = result.scalar_one_or_none()

        if not attacker:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 检查是否可以PVP
        can_battle, reason = await BattleService.can_battle_pvp(attacker)
        if not can_battle:
            await update.message.reply_text(f"❌ {reason}")
            return

        # 获取防守方
        defender_id = None
        if update.message.reply_to_message:
            defender_id = update.message.reply_to_message.from_user.id
        elif context.args:
            await update.message.reply_text(
                "❌ 请使用回复功能挑战对手\n"
                "在对方消息上点击回复，然后输入 /切磋"
            )
            return
        else:
            await update.message.reply_text(
                "❌ 请指定对手\n"
                "在对方消息上点击回复，然后输入 /切磋"
            )
            return

        # 不能挑战自己
        if defender_id == user.id:
            await update.message.reply_text("❌ 不能挑战自己")
            return

        # 获取防守方玩家
        result = await session.execute(
            select(Player).where(Player.telegram_id == defender_id)
        )
        defender = result.scalar_one_or_none()

        if not defender:
            await update.message.reply_text("❌ 对方还未开始游戏")
            return

        # 检查防守方是否可以被挑战
        if defender.is_in_battle:
            await update.message.reply_text("❌ 对方正在战斗中")
            return

        if defender.is_cultivating:
            await update.message.reply_text("❌ 对方正在修炼中")
            return

        if defender.hp <= defender.max_hp * 0.3:
            await update.message.reply_text("❌ 对方生命值过低，无法挑战")
            return

        # 发送战斗开始消息
        msg = f"⚔️ 【论道切磋】\n\n"
        msg += f"💚 {attacker.nickname} ({attacker.full_realm_name})\n"
        msg += f"   ❤️ {attacker.hp}/{attacker.max_hp} | ⚡ {attacker.combat_power}\n\n"
        msg += f"💙 {defender.nickname} ({defender.full_realm_name})\n"
        msg += f"   ❤️ {defender.hp}/{defender.max_hp} | ⚡ {defender.combat_power}\n\n"
        msg += "⏳ 战斗进行中..."

        await update.message.reply_text(msg)

        # 执行战斗
        result, battle_log, rewards = await BattleService.battle_pvp(
            session, attacker, defender
        )

        # 发送战斗日志
        log_msg = "```\n" + "\n".join(battle_log) + "\n```"
        await update.message.reply_text(log_msg, parse_mode="Markdown")

        # 发送结果
        from bot.models import BattleResult
        if result == BattleResult.WIN:
            summary = f"🎉 {attacker.nickname} 获胜！\n\n"
            summary += f"⭐ 修为：+{rewards.get('exp', 0)}\n"
            summary += f"🏆 荣誉：+{rewards.get('honor', 0)}\n\n"
            summary += f"💚 {attacker.nickname}：{attacker.hp}/{attacker.max_hp}\n"
            summary += f"💙 {defender.nickname}：{defender.hp}/{defender.max_hp}"
        elif result == BattleResult.LOSE:
            summary = f"🎉 {defender.nickname} 获胜！\n\n"
            summary += f"💚 {attacker.nickname}：{attacker.hp}/{attacker.max_hp}\n"
            summary += f"💙 {defender.nickname}：{defender.hp}/{defender.max_hp}"
        else:
            summary = f"⏱️ 平局！\n\n"
            summary += "双方势均力敌，难分胜负"

        await update.message.reply_text(summary)


async def use_skill_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """在战斗外使用技能(主要用于测试) - /use_skill <技能名>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定技能名称\n"
            "用法：/施法 <技能名称>\n"
            "使用 /技能 查看已学技能"
        )
        return

    skill_name = " ".join(context.args)

    async with AsyncSessionLocal() as session:
        # 获取玩家
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 获取技能
        result = await session.execute(
            select(Skill).where(Skill.name == skill_name)
        )
        skill = result.scalar_one_or_none()

        if not skill:
            await update.message.reply_text(
                f"❌ 未找到技能：{skill_name}\n"
                "使用 /技能 查看已学技能"
            )
            return

        # 获取玩家技能记录
        result = await session.execute(
            select(PlayerSkill).where(
                PlayerSkill.player_id == player.id,
                PlayerSkill.skill_id == skill.id
            )
        )
        player_skill = result.scalar_one_or_none()

        if not player_skill:
            await update.message.reply_text(
                f"❌ 你还没有学会 {skill_name}\n"
                "使用 /学习 学习技能"
            )
            return

        # 检查是否可以使用
        can_use, reason = await SkillService.can_use_skill(player, skill, player_skill)
        if not can_use:
            await update.message.reply_text(f"❌ {reason}")
            return

        # 使用技能
        success, message = await SkillService.use_skill(
            session, player, skill, player_skill
        )

        if not success:
            await update.message.reply_text(f"❌ {message}")
            return

        # 计算伤害(对假想敌)
        target_defense = 50  # 假想敌防御
        damage, is_crit, effect_desc = await SkillService.calculate_skill_damage(
            player, skill, target_defense, player_skill.skill_level
        )

        element_icon = {
            "金": "⚔️", "木": "🌲", "水": "💧",
            "火": "🔥", "土": "🪨"
        }.get(skill.element, "✨") if skill.element else "✨"

        msg = f"✨ {message}！\n\n"
        msg += f"{element_icon} **{skill.name}** (Lv.{player_skill.skill_level})\n"
        msg += f"{skill.description}\n\n"

        # 显示技能效果
        crit_text = "💥 暴击！" if is_crit else ""
        msg += f"💥 测试伤害：{damage} {crit_text}\n"

        if effect_desc:
            msg += f"✨ {effect_desc}\n"

        msg += f"\n💧 灵力消耗：{skill.spiritual_cost}\n"
        msg += f"💧 剩余灵力：{player.spiritual_power}/{player.max_spiritual_power}\n\n"

        # 灵根加成说明
        if skill.element and player.spirit_root:
            if skill.element in player.spirit_root.element_list:
                element_count = player.spirit_root.element_count
                bonus_pct = 0
                if element_count == 1:
                    bonus_pct = 50
                elif element_count == 2:
                    bonus_pct = 30
                elif element_count == 3:
                    bonus_pct = 15
                elif element_count == 4:
                    bonus_pct = 5

                if bonus_pct > 0:
                    msg += f"🌟 灵根匹配加成：+{bonus_pct}%伤害\n"

        msg += f"\n💡 技能在实战中可增加熟练度"

        await update.message.reply_text(msg, parse_mode="Markdown")


async def battle_strategy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """战斗策略管理 - /战略 [保守|平衡|激进]"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        # 获取玩家
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /start 开始游戏")
            return

        # 如果没有参数，显示当前策略和说明
        if not context.args:
            try:
                current_strategy = BattleStrategy(player.battle_strategy)
            except:
                current_strategy = BattleStrategy.BALANCED

            msg = "⚙️ 【战斗策略设置】\n\n"
            msg += f"当前策略: **{current_strategy.name}**\n\n"
            msg += BattleAI.get_strategy_description(current_strategy)
            msg += "\n\n━━━━━━━━━━━━━━\n\n"
            msg += "**可用策略**:\n\n"

            for strategy in BattleStrategy:
                strategy_desc = BattleAI.get_strategy_description(strategy)
                is_current = "✅ " if strategy == current_strategy else "   "
                msg += f"{is_current}**{strategy.value}** - {strategy.name}\n"

            msg += "\n━━━━━━━━━━━━━━\n"
            msg += "💡 使用方法: /战略 [保守|平衡|激进]\n"
            msg += "💡 策略影响战斗中的技能使用频率和灵力保留"

            await update.message.reply_text(msg, parse_mode="Markdown")
            return

        # 解析策略
        strategy_str = context.args[0]
        new_strategy = BattleAI.parse_strategy_from_string(strategy_str)

        if not new_strategy:
            await update.message.reply_text(
                f"❌ 无效的策略\n\n可用策略: 保守、平衡、激进"
            )
            return

        # 更新策略
        player.battle_strategy = new_strategy.value
        await session.commit()

        msg = f"✅ 战斗策略已切换为 **{new_strategy.name}**\n\n"
        msg += BattleAI.get_strategy_description(new_strategy)
        msg += "\n\n💡 策略将在下次战斗中生效"

        await update.message.reply_text(msg, parse_mode="Markdown")


def register_handlers(application):
    """注册战斗相关处理器"""
    application.add_handler(CommandHandler("战斗", battle_command))
    application.add_handler(CommandHandler("切磋", battle_pvp_command))
    application.add_handler(CommandHandler("施法", use_skill_command))
    application.add_handler(CommandHandler("战略", battle_strategy_command))
