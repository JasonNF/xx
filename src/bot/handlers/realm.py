"""秘境探索handlers - 凡人修仙传版本"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler

from bot.models.database import AsyncSessionLocal
from bot.models import Player, SecretRealm
from bot.services import RealmService
from sqlalchemy import select


async def realms_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看可用秘境列表 - /realms"""
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

        # 获取可用秘境
        realms = await RealmService.get_available_realms(session, player)

        if not realms:
            await update.message.reply_text("🏛️ 当前没有开放的秘境")
            return

        # 构建消息
        msg = "🏛️ 【秘境列表】\n\n"
        msg += f"道友境界：{player.full_realm_name}\n"
        msg += f"💰 灵石：{player.spirit_stones}\n"
        msg += "━━━━━━━━━━━━━━\n\n"

        for realm in realms:
            status_icon = "✅" if realm["can_enter"] else "🔒"
            msg += f"{status_icon} **{realm['name']}**\n"
            msg += f"   类型：{realm['realm_type']} | 难度：{realm['difficulty']}\n"
            msg += f"   要求：{realm['min_realm_requirement']}\n"
            msg += f"   入场费：{realm['entry_cost']} 灵石\n"
            msg += f"   时长：{realm['duration_minutes']}分钟 | 危险度：{realm['danger_level']}/10\n"

            if not realm["can_enter"]:
                msg += f"   ⚠️ {realm['reason']}\n"

            if realm["max_players"] > 0:
                msg += f"   👥 {realm['current_players']}/{realm['max_players']}人\n"

            msg += f"   📖 {realm['description']}\n\n"

        msg += "━━━━━━━━━━━━━━\n"
        msg += "💡 使用 /探索 <秘境名称> 进入探索"

        await update.message.reply_text(msg, parse_mode="Markdown")


async def explore_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """开始探索秘境 - /explore <秘境名称>"""
    user = update.effective_user

    # 检查参数
    if not context.args:
        await update.message.reply_text(
            "❌ 请指定秘境名称\n"
            "用法：/探索 <秘境名称>\n"
            "例如：/探索 血色禁地"
        )
        return

    realm_name = " ".join(context.args)

    async with AsyncSessionLocal() as session:
        # 获取玩家
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 获取秘境
        result = await session.execute(
            select(SecretRealm).where(SecretRealm.name == realm_name)
        )
        realm = result.scalar_one_or_none()

        if not realm:
            await update.message.reply_text(
                f"❌ 未找到秘境：{realm_name}\n"
                "使用 /秘境 查看可用秘境"
            )
            return

        # 检查是否可以进入
        can_enter, reason = await RealmService.can_enter_realm(session, player, realm)
        if not can_enter:
            await update.message.reply_text(f"❌ 无法进入：{reason}")
            return

        # 开始探索
        success, message, exploration = await RealmService.start_exploration(
            session, player, realm
        )

        if not success:
            await update.message.reply_text(f"❌ {message}")
            return

        # 发送开始消息
        start_msg = f"🏛️ 【{realm.name}】\n\n"
        start_msg += f"{message}\n\n"
        start_msg += f"💰 消耗：{realm.entry_cost} 灵石\n"
        start_msg += f"⏱️ 时长：{realm.duration_minutes}分钟\n"
        start_msg += f"⚠️ 危险度：{realm.danger_level}/10\n\n"
        start_msg += "🎲 开始探索...\n"

        await update.message.reply_text(start_msg)

        # 模拟探索 (简化版，立即完成)
        result = await RealmService.simulate_exploration(
            session, player, realm, exploration
        )

        # 发送探索日志
        battle_log = "\n".join(result["battle_log"])
        log_msg = f"```\n{battle_log}\n```"
        await update.message.reply_text(log_msg, parse_mode="Markdown")

        # 发送最终奖励
        rewards = result["rewards"]
        if result["success"]:
            # 应用奖励到玩家
            player.cultivation_exp += rewards["exp"]
            player.spirit_stones += rewards["spirit_stones"]
            player.hp = result["exploration"].hp_remaining
            await session.commit()

            reward_msg = f"🎉 【探索完成】\n\n"
            reward_msg += f"📊 评价：{rewards['rating']}\n"
            reward_msg += f"⭐ 修为：+{rewards['exp']}\n"
            reward_msg += f"💰 灵石：+{rewards['spirit_stones']}\n"
            reward_msg += f"❤️ 剩余生命：{result['exploration'].hp_remaining}/{player.max_hp}\n\n"
            reward_msg += f"当前修为：{player.cultivation_exp}/{player.next_realm_exp}"
        else:
            reward_msg = f"💀 【探索失败】\n\n"
            reward_msg += "建议恢复后再次尝试"

        await update.message.reply_text(reward_msg)


def register_handlers(application):
    """注册秘境相关处理器"""
    application.add_handler(MessageHandler(filters.Regex(r"^\.秘境"), realms_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.探索"), explore_command))
