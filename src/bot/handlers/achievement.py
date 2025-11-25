"""成就系统handler"""
import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, Application

from bot.models import get_db, Player, AchievementCategory
from bot.services.achievement_service import AchievementService

logger = logging.getLogger(__name__)


async def achievement_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看成就列表 - /成就 [分类]"""
    user_id = update.effective_user.id

    # 获取分类参数
    category_str = context.args[0] if context.args else None

    async with get_db() as db:
        # 获取玩家
        from sqlalchemy import select
        result = await db.execute(select(Player).where(Player.telegram_id == user_id))
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("你还未踏入修仙之路，请先使用 /检测灵根 开始游戏")
            return

        # 解析分类
        category = None
        if category_str:
            category_map = {
                "修炼": AchievementCategory.CULTIVATION,
                "战斗": AchievementCategory.COMBAT,
                "收集": AchievementCategory.COLLECTION,
                "制作": AchievementCategory.CRAFTING,
                "探索": AchievementCategory.EXPLORATION,
                "社交": AchievementCategory.SOCIAL,
                "财富": AchievementCategory.WEALTH,
                "特殊": AchievementCategory.SPECIAL
            }
            category = category_map.get(category_str)

            if not category:
                await update.message.reply_text(
                    "❌ 未知分类\n\n"
                    "可用分类: 修炼 战斗 收集 制作 探索 社交 财富 特殊"
                )
                return

        # 获取成就列表
        achievements = await AchievementService.get_player_achievements(
            db, player.id, category
        )

        if not achievements:
            await update.message.reply_text("该分类下暂无成就")
            return

        # 按分类分组
        from collections import defaultdict
        by_category = defaultdict(list)
        for ach in achievements:
            by_category[ach["category"]].append(ach)

        # 构建消息
        category_names = {
            "cultivation": "📚 修炼",
            "combat": "⚔️ 战斗",
            "collection": "📦 收集",
            "crafting": "🔨 制作",
            "exploration": "🗺️ 探索",
            "social": "👥 社交",
            "wealth": "💰 财富",
            "special": "✨ 特殊"
        }

        message_parts = []

        for cat, achs in by_category.items():
            message_parts.append(f"\n{category_names.get(cat, cat)}")
            for ach in achs:
                status = ""
                if ach["is_claimed"]:
                    status = "✅"
                elif ach["is_completed"]:
                    status = "🎁"  # 可领取
                else:
                    status = "🔒"

                progress_text = f"{ach['current_progress']}/{ach['condition_value']}"
                message_parts.append(
                    f"{status} {ach['icon']} {ach['name']} ({progress_text})\n"
                    f"   {ach['description']} | {ach['points']}点"
                )

        message = "🏆 成就系统\n" + "\n".join(message_parts)
        message += "\n\n💡 使用 /领取成就 <ID> 领取奖励"

        await update.message.reply_text(message)


async def claim_achievement_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """领取成就奖励 - /领取成就 <成就ID>"""
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text("❌ 请指定成就ID\n用法: /领取成就 <成就ID>")
        return

    try:
        achievement_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ 成就ID必须是数字")
        return

    async with get_db() as db:
        # 获取玩家
        from sqlalchemy import select
        result = await db.execute(select(Player).where(Player.telegram_id == user_id))
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("你还未踏入修仙之路，请先使用 /检测灵根 开始游戏")
            return

        # 领取成就
        success, message, rewards = await AchievementService.claim_achievement(
            db, player, achievement_id
        )

        if not success:
            await update.message.reply_text(f"❌ {message}")
            return

        # 构建奖励消息
        reward_parts = ["🎉 成就奖励领取成功！\n"]

        if rewards.get("exp", 0) > 0:
            reward_parts.append(f"📖 修为 +{rewards['exp']}")

        if rewards.get("spirit_stones", 0) > 0:
            reward_parts.append(f"💎 灵石 +{rewards['spirit_stones']}")

        if rewards.get("points", 0) > 0:
            reward_parts.append(f"⭐ 成就点数 +{rewards['points']}")

        if rewards.get("item"):
            item = rewards["item"]
            reward_parts.append(f"📦 {item['name']} x{item['quantity']}")

        if rewards.get("title"):
            reward_parts.append(f"🏅 称号: {rewards['title']}")

        await update.message.reply_text("\n".join(reward_parts))


async def achievement_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看成就统计 - /成就统计"""
    user_id = update.effective_user.id

    async with get_db() as db:
        # 获取玩家
        from sqlalchemy import select
        result = await db.execute(select(Player).where(Player.telegram_id == user_id))
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("你还未踏入修仙之路,请先使用 /检测灵根 开始游戏")
            return

        # 获取统计数据
        summary = await AchievementService.get_achievement_summary(db, player.id)

        # 构建消息
        category_names = {
            "cultivation": "📚 修炼",
            "combat": "⚔️ 战斗",
            "collection": "📦 收集",
            "crafting": "🔨 制作",
            "exploration": "🗺️ 探索",
            "social": "👥 社交",
            "wealth": "💰 财富",
            "special": "✨ 特殊"
        }

        message = f"""📊 成就统计

✅ 已完成: {summary['completed_achievements']}/{summary['total_achievements']}
📈 完成度: {summary['completion_rate']*100:.1f}%
⭐ 总点数: {summary['total_points']}
🎁 可领取: {summary['claimable_count']}

分类统计:
"""
        for cat, count in summary['category_stats'].items():
            if count > 0:
                message += f"{category_names.get(cat, cat)}: {count}\n"

        if summary['last_achievement_time']:
            from datetime import datetime
            last_time = summary['last_achievement_time'].strftime("%Y-%m-%d %H:%M")
            message += f"\n🕐 最近完成: {last_time}"

        await update.message.reply_text(message)


async def titles_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看称号列表 - /称号"""
    user_id = update.effective_user.id

    async with get_db() as db:
        # 获取玩家
        from sqlalchemy import select
        result = await db.execute(select(Player).where(Player.telegram_id == user_id))
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("你还未踏入修仙之路，请先使用 /检测灵根 开始游戏")
            return

        # 获取称号列表
        titles = await AchievementService.get_player_titles(db, player.id)

        if not titles:
            await update.message.reply_text("你还没有任何称号\n完成成就可以获得称号!")
            return

        # 构建消息
        message_parts = ["🏅 我的称号\n"]

        for title in titles:
            status = "【使用中】" if title.is_active else ""
            source = f"(来自: {title.source})" if title.source else ""
            obtained = title.obtained_at.strftime("%Y-%m-%d")
            message_parts.append(
                f"{status}「{title.title}」 {source}\n"
                f"   获得时间: {obtained} | ID: {title.id}"
            )

        message = "\n".join(message_parts)
        message += "\n\n💡 使用 /装备称号 <ID> 装备称号\n💡 使用 /卸下称号 卸下当前称号"

        await update.message.reply_text(message)


async def equip_title_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """装备称号 - /装备称号 <称号ID>"""
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text("❌ 请指定称号ID\n用法: /装备称号 <称号ID>")
        return

    try:
        title_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ 称号ID必须是数字")
        return

    async with get_db() as db:
        # 获取玩家
        from sqlalchemy import select
        result = await db.execute(select(Player).where(Player.telegram_id == user_id))
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("你还未踏入修仙之路，请先使用 /检测灵根 开始游戏")
            return

        # 装备称号
        success, message = await AchievementService.set_active_title(
            db, player.id, title_id
        )

        if success:
            await update.message.reply_text(f"✅ {message}")
        else:
            await update.message.reply_text(f"❌ {message}")


async def unequip_title_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """卸下称号 - /卸下称号"""
    user_id = update.effective_user.id

    async with get_db() as db:
        # 获取玩家
        from sqlalchemy import select
        result = await db.execute(select(Player).where(Player.telegram_id == user_id))
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("你还未踏入修仙之路，请先使用 /检测灵根 开始游戏")
            return

        # 卸下称号
        success, message = await AchievementService.set_active_title(
            db, player.id, None
        )

        if success:
            await update.message.reply_text(f"✅ {message}")
        else:
            await update.message.reply_text(f"❌ {message}")


def register_handlers(application: Application):
    """注册所有handler"""
    application.add_handler(CommandHandler("成就", achievement_command))
    application.add_handler(CommandHandler("领取成就", claim_achievement_command))
    application.add_handler(CommandHandler("成就统计", achievement_stats_command))
    application.add_handler(CommandHandler("称号", titles_command))
    application.add_handler(CommandHandler("装备称号", equip_title_command))
    application.add_handler(CommandHandler("卸下称号", unequip_title_command))

    logger.info("成就系统handlers已注册")
