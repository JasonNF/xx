"""炼丹系统handlers - 凡人修仙传版本"""
import json
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.models.database import AsyncSessionLocal
from bot.models import Player, Item
from bot.models.alchemy import PillRecipe, PlayerAlchemy
from bot.services.alchemy_service import AlchemyService
from sqlalchemy import select


async def alchemy_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看炼丹信息 - /炼丹"""
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

        # 获取炼丹数据
        alchemy = await AlchemyService.get_or_create_alchemy_data(session, player)

        # 构建消息
        msg = "⚗️ 【炼丹信息】\n\n"
        msg += f"炼丹等级：Lv.{alchemy.alchemy_level}\n"
        msg += f"炼丹经验：{alchemy.alchemy_exp}/{alchemy.next_level_exp}\n"
        msg += f"成功率：{alchemy.success_count}/{alchemy.total_refines} " if alchemy.total_refines > 0 else "成功率：暂无记录\n"

        if alchemy.total_refines > 0:
            success_rate = (alchemy.success_count / alchemy.total_refines) * 100
            msg += f"({success_rate:.1f}%)\n"

        msg += "\n"

        # 当前炼丹状态
        if alchemy.is_refining:
            result = await session.execute(
                select(PillRecipe).where(PillRecipe.id == alchemy.refining_recipe_id)
            )
            recipe = result.scalar_one_or_none()

            if recipe:
                from datetime import datetime
                remaining = alchemy.refining_end_time - datetime.now()
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)

                msg += "🔥 正在炼制中\n"
                msg += f"丹药：{recipe.name}\n"
                msg += f"剩余时间：{hours}小时{minutes}分钟\n\n"
                msg += "💡 使用 /炼丹结算 完成炼制\n"
                msg += "💡 使用 /炼丹取消 取消炼制"
        else:
            msg += "💡 使用 /丹方 查看可炼制丹药\n"
            msg += "💡 使用 /炼制 <丹药名> 开始炼制"

        await update.message.reply_text(msg)


async def recipes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看丹方列表 - /丹方"""
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

        # 获取炼丹数据
        alchemy = await AlchemyService.get_or_create_alchemy_data(session, player)

        # 获取所有丹方
        result = await session.execute(
            select(PillRecipe).order_by(PillRecipe.required_alchemy_level, PillRecipe.name)
        )
        recipes = result.scalars().all()

        if not recipes:
            await update.message.reply_text("📜 暂无丹方")
            return

        # 构建消息
        msg = "📜 【丹方列表】\n\n"
        msg += f"炼丹等级：Lv.{alchemy.alchemy_level}\n"
        msg += f"💧 灵力：{player.spiritual_power}/{player.max_spiritual_power}\n"
        msg += "━━━━━━━━━━━━━━\n\n"

        for recipe in recipes:
            # 检查是否可炼制
            can_refine = alchemy.alchemy_level >= recipe.required_alchemy_level
            status_icon = "✅" if can_refine else "🔒"

            # 获取产出丹药信息
            result = await session.execute(
                select(Item).where(Item.id == recipe.result_pill_id)
            )
            pill = result.scalar_one_or_none()
            pill_name = pill.name if pill else "未知丹药"

            msg += f"{status_icon} **{recipe.name}**\n"
            msg += f"    {recipe.description[:40]}...\n"
            msg += f"    产出：{pill_name} x{recipe.result_quantity_min}-{recipe.result_quantity_max}\n"
            msg += f"    成功率：{int(recipe.base_success_rate * 100)}%\n"
            msg += f"    消耗：{recipe.spiritual_power_cost}灵力 | 时长：{recipe.duration_hours}小时\n"

            # 材料
            ingredients = json.loads(recipe.ingredients)
            ingredient_names = []
            for ing in ingredients:
                result = await session.execute(
                    select(Item).where(Item.id == ing["item_id"])
                )
                item = result.scalar_one_or_none()
                if item:
                    ingredient_names.append(f"{item.name}x{ing['quantity']}")

            if ingredient_names:
                msg += f"    材料：{', '.join(ingredient_names)}\n"

            if not can_refine:
                msg += f"    ⚠️ 需要炼丹Lv.{recipe.required_alchemy_level}\n"

            msg += "\n"

        msg += "━━━━━━━━━━━━━━\n"
        msg += "💡 使用 /炼制 <丹药名> 开始炼制"

        await update.message.reply_text(msg, parse_mode="Markdown")


async def refine_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """开始炼制 - /炼制 <丹药名>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定丹方名称\n"
            "用法：/炼制 <丹方名称>\n"
            "例如：/炼制 回气丹"
        )
        return

    recipe_name = " ".join(context.args)

    async with AsyncSessionLocal() as session:
        # 获取玩家
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 获取炼丹数据
        alchemy = await AlchemyService.get_or_create_alchemy_data(session, player)

        # 获取丹方
        result = await session.execute(
            select(PillRecipe).where(PillRecipe.name == recipe_name)
        )
        recipe = result.scalar_one_or_none()

        if not recipe:
            await update.message.reply_text(
                f"❌ 未找到丹方：{recipe_name}\n"
                "使用 /丹方 查看可炼制丹药"
            )
            return

        # 开始炼制
        success, message = await AlchemyService.start_refining(session, player, alchemy, recipe)

        if success:
            msg = f"⚗️ {message}\n\n"
            msg += f"消耗：{recipe.spiritual_power_cost}灵力\n"
            msg += f"剩余灵力：{player.spiritual_power}/{player.max_spiritual_power}"
        else:
            msg = f"❌ {message}"

        await update.message.reply_text(msg)


async def finish_refine_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """完成炼制 - /炼丹结算"""
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

        # 获取炼丹数据
        alchemy = await AlchemyService.get_or_create_alchemy_data(session, player)

        # 完成炼制
        success, message, result_data = await AlchemyService.finish_refining(session, player, alchemy)

        if not success:
            await update.message.reply_text(f"❌ {message}")
            return

        # 构建结果消息
        if result_data.get("success"):
            msg = f"🎉 炼制成功！\n\n"

            for pill in result_data.get("pills", []):
                msg += f"💊 获得：{pill['name']} x{pill['count']}\n"
                msg += f"✨ 品质：{pill['quality']}/100\n\n"

            msg += f"⭐ 经验：+{result_data['exp']}\n"

            if result_data.get("level_up"):
                msg += f"\n🎊 炼丹等级提升至 Lv.{result_data['level_up']}！"
        else:
            msg = f"💥 炼制失败...\n\n"
            msg += f"⭐ 经验：+{result_data['exp']}\n"
            msg += "\n再接再厉！"

        await update.message.reply_text(msg)


async def cancel_refine_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """取消炼制 - /炼丹取消"""
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

        # 获取炼丹数据
        alchemy = await AlchemyService.get_or_create_alchemy_data(session, player)

        # 取消炼制
        success, message = await AlchemyService.cancel_refining(session, alchemy)

        if success:
            msg = f"⚠️ {message}"
        else:
            msg = f"❌ {message}"

        await update.message.reply_text(msg)


def register_handlers(application):
    """注册炼丹相关处理器"""
    application.add_handler(CommandHandler("炼丹", alchemy_info_command))
    application.add_handler(CommandHandler("丹方", recipes_command))
    application.add_handler(CommandHandler("炼制", refine_command))
    application.add_handler(CommandHandler("炼丹结算", finish_refine_command))
    application.add_handler(CommandHandler("炼丹取消", cancel_refine_command))
