"""炼器系统handlers - 凡人修仙传版本"""
import json
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.models.database import AsyncSessionLocal
from bot.models import Player, Item
from bot.models.refinery import RefineryRecipe, PlayerRefinery
from bot.services.refinery_service import RefineryService
from sqlalchemy import select


async def refinery_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看炼器信息 - /炼器"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        refinery = await RefineryService.get_or_create_refinery_data(session, player)

        msg = "🔨 【炼器信息】\n\n"
        msg += f"炼器等级：Lv.{refinery.refinery_level}\n"
        msg += f"炼器经验：{refinery.refinery_exp}/{refinery.next_level_exp}\n"
        msg += f"成功率：{refinery.success_count}/{refinery.total_refines} " if refinery.total_refines > 0 else "成功率：暂无记录\n"

        if refinery.total_refines > 0:
            success_rate = (refinery.success_count / refinery.total_refines) * 100
            msg += f"({success_rate:.1f}%)\n"

        msg += "\n"

        if refinery.is_refining:
            result = await session.execute(
                select(RefineryRecipe).where(RefineryRecipe.id == refinery.refining_recipe_id)
            )
            recipe = result.scalar_one_or_none()

            if recipe:
                from datetime import datetime
                remaining = refinery.refining_end_time - datetime.now()
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)

                msg += "🔥 正在炼制中\n"
                msg += f"法宝：{recipe.name}\n"
                msg += f"剩余时间：{hours}小时{minutes}分钟\n\n"
                msg += "💡 使用 /炼器结算 完成炼制\n"
                msg += "💡 使用 /炼器取消 取消炼制"
        else:
            msg += "💡 使用 /器方 查看可炼制法宝\n"
            msg += "💡 使用 /炼制法宝 <法宝名> 开始炼制"

        await update.message.reply_text(msg)


async def recipes_refinery_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看炼器配方 - /器方"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        refinery = await RefineryService.get_or_create_refinery_data(session, player)

        result = await session.execute(
            select(RefineryRecipe).order_by(RefineryRecipe.required_refinery_level, RefineryRecipe.name)
        )
        recipes = result.scalars().all()

        if not recipes:
            await update.message.reply_text("📜 暂无炼器配方")
            return

        msg = "📜 【炼器配方】\n\n"
        msg += f"炼器等级：Lv.{refinery.refinery_level}\n"
        msg += f"💧 灵力：{player.spiritual_power}/{player.max_spiritual_power}\n"
        msg += "━━━━━━━━━━━━━━\n\n"

        for recipe in recipes:
            can_refine = refinery.refinery_level >= recipe.required_refinery_level
            status_icon = "✅" if can_refine else "🔒"

            result = await session.execute(
                select(Item).where(Item.id == recipe.result_item_id)
            )
            item = result.scalar_one_or_none()
            item_name = item.name if item else "未知法宝"

            msg += f"{status_icon} **{recipe.name}**\n"
            msg += f"    {recipe.description[:40]}...\n"
            msg += f"    产出：{item_name}\n"
            msg += f"    成功率：{int(recipe.base_success_rate * 100)}%\n"
            msg += f"    消耗：{recipe.spiritual_power_cost}灵力 | 时长：{recipe.duration_hours}小时\n"

            materials = json.loads(recipe.materials)
            material_names = []
            for mat in materials:
                result = await session.execute(
                    select(Item).where(Item.id == mat["item_id"])
                )
                item = result.scalar_one_or_none()
                if item:
                    material_names.append(f"{item.name}x{mat['quantity']}")

            if material_names:
                msg += f"    材料：{', '.join(material_names)}\n"

            if not can_refine:
                msg += f"    ⚠️ 需要炼器Lv.{recipe.required_refinery_level}\n"

            msg += "\n"

        msg += "━━━━━━━━━━━━━━\n"
        msg += "💡 使用 /炼制法宝 <法宝名> 开始炼制"

        await update.message.reply_text(msg, parse_mode="Markdown")


async def refine_item_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """开始炼制法宝 - /炼制法宝 <法宝名>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定配方名称\n"
            "用法：/炼制法宝 <配方名称>\n"
            "例如：/炼制法宝 青钢剑"
        )
        return

    recipe_name = " ".join(context.args)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        refinery = await RefineryService.get_or_create_refinery_data(session, player)

        result = await session.execute(
            select(RefineryRecipe).where(RefineryRecipe.name == recipe_name)
        )
        recipe = result.scalar_one_or_none()

        if not recipe:
            await update.message.reply_text(
                f"❌ 未找到配方：{recipe_name}\n"
                "使用 /器方 查看可炼制法宝"
            )
            return

        success, message = await RefineryService.start_refining(session, player, refinery, recipe)

        if success:
            msg = f"🔨 {message}\n\n"
            msg += f"消耗：{recipe.spiritual_power_cost}灵力\n"
            msg += f"剩余灵力：{player.spiritual_power}/{player.max_spiritual_power}"
        else:
            msg = f"❌ {message}"

        await update.message.reply_text(msg)


async def finish_refinery_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """完成炼器 - /炼器结算"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        refinery = await RefineryService.get_or_create_refinery_data(session, player)

        success, message, result_data = await RefineryService.finish_refining(session, player, refinery)

        if not success:
            await update.message.reply_text(f"❌ {message}")
            return

        if result_data.get("success"):
            item = result_data.get("item")
            msg = f"🎉 炼制成功！\n\n"

            if item:
                msg += f"⚔️ 获得：{item['name']}\n"
                msg += f"✨ 品质：{item['quality']}/100\n\n"

            msg += f"⭐ 经验：+{result_data['exp']}\n"

            if result_data.get("level_up"):
                msg += f"\n🎊 炼器等级提升至 Lv.{result_data['level_up']}！"
        else:
            msg = f"💥 炼制失败...\n\n"
            msg += f"⭐ 经验：+{result_data['exp']}\n"
            msg += "\n再接再厉！"

        await update.message.reply_text(msg)


async def cancel_refinery_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """取消炼器 - /炼器取消"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        refinery = await RefineryService.get_or_create_refinery_data(session, player)

        if not refinery.is_refining:
            await update.message.reply_text("❌ 没有正在进行的炼器")
            return

        refinery.is_refining = False
        refinery.refining_recipe_id = None
        refinery.refining_start_time = None
        refinery.refining_end_time = None

        await session.commit()

        await update.message.reply_text("⚠️ 已取消炼器，材料已消耗无法返还")


def register_handlers(application):
    """注册炼器相关处理器"""
    application.add_handler(CommandHandler("炼器", refinery_info_command))
    application.add_handler(CommandHandler("器方", recipes_refinery_command))
    application.add_handler(CommandHandler("炼制法宝", refine_item_command))
    application.add_handler(CommandHandler("炼器结算", finish_refinery_command))
    application.add_handler(CommandHandler("炼器取消", cancel_refinery_command))
