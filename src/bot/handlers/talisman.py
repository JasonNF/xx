"""符箓系统handlers"""
import json
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from datetime import datetime, timedelta
import random

from bot.models.database import AsyncSessionLocal
from bot.models import Player, Item, PlayerInventory
from bot.models.talisman import (
    TalismanRecipe, PlayerTalismanSkill, PlayerTalisman,
    TalismanCraftRecord
)
from bot.services.cave_service import CaveService
from sqlalchemy import select


async def talisman_skill_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看制符技能 - /制符"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 获取或创建制符技能
        result = await session.execute(
            select(PlayerTalismanSkill).where(PlayerTalismanSkill.player_id == player.id)
        )
        skill = result.scalar_one_or_none()

        if not skill:
            skill = PlayerTalismanSkill(player_id=player.id)
            session.add(skill)
            await session.commit()
            await session.refresh(skill)

        msg = "📜 【制符技能】\n\n"
        msg += f"等级：Lv.{skill.skill_level}\n"
        msg += f"经验：{skill.skill_exp}/{skill.next_level_exp}\n"
        msg += f"成功率：{skill.success_count}/{skill.total_crafts} " if skill.total_crafts > 0 else "成功率：暂无记录\n"

        if skill.total_crafts > 0:
            success_rate = (skill.success_count / skill.total_crafts) * 100
            msg += f"({success_rate:.1f}%)\n"

        msg += "\n"

        if skill.is_crafting:
            result = await session.execute(
                select(TalismanRecipe).where(TalismanRecipe.id == skill.crafting_recipe_id)
            )
            recipe = result.scalar_one_or_none()

            if recipe:
                remaining = skill.crafting_end_time - datetime.now()
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)

                msg += "🔥 正在制作中\n"
                msg += f"符箓：{recipe.name}\n"
                msg += f"剩余时间：{hours}小时{minutes}分钟\n\n"
                msg += "💡 使用 /制符结算 完成制作\n"
                msg += "💡 使用 /制符取消 取消制作"
        else:
            msg += "💡 使用 /符箓图鉴 查看可制作符箓\n"
            msg += "💡 使用 /制作符箓 <符箓名> 开始制作"

        await update.message.reply_text(msg)


async def talisman_recipes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """符箓图鉴 - /符箓图鉴"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        result = await session.execute(
            select(PlayerTalismanSkill).where(PlayerTalismanSkill.player_id == player.id)
        )
        skill = result.scalar_one_or_none()

        if not skill:
            skill = PlayerTalismanSkill(player_id=player.id)
            session.add(skill)
            await session.commit()

        result = await session.execute(
            select(TalismanRecipe).order_by(TalismanRecipe.required_talisman_skill, TalismanRecipe.name)
        )
        recipes = result.scalars().all()

        if not recipes:
            await update.message.reply_text("📜 暂无符箓配方")
            return

        msg = "📜 【符箓图鉴】\n\n"
        msg += f"制符等级：Lv.{skill.skill_level}\n"
        msg += f"💧 灵力：{player.spiritual_power}/{player.max_spiritual_power}\n"
        msg += "━━━━━━━━━━━━━━\n\n"

        for recipe in recipes:
            can_craft = skill.skill_level >= recipe.required_talisman_skill
            status_icon = "✅" if can_craft else "🔒"

            msg += f"{status_icon} **{recipe.name}**\n"
            msg += f"    {recipe.description[:40]}...\n"
            msg += f"    类型：{recipe.talisman_type} | 品阶：{recipe.grade}\n"
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

            if not can_craft:
                msg += f"    ⚠️ 需要制符Lv.{recipe.required_talisman_skill}\n"

            msg += "\n"

        msg += "━━━━━━━━━━━━━━\n"
        msg += "💡 使用 /制作符箓 <符箓名> 开始制作"

        await update.message.reply_text(msg, parse_mode="Markdown")


async def craft_talisman_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """制作符箓 - /制作符箓 <符箓名>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定符箓名称\n"
            "用法：/制作符箓 <符箓名>\n"
            "例如：/制作符箓 金刚符"
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

        # 获取制符技能
        result = await session.execute(
            select(PlayerTalismanSkill).where(PlayerTalismanSkill.player_id == player.id)
        )
        skill = result.scalar_one_or_none()

        if not skill:
            skill = PlayerTalismanSkill(player_id=player.id)
            session.add(skill)
            await session.commit()

        if skill.is_crafting:
            await update.message.reply_text("❌ 正在制作中，请先完成当前制作")
            return

        # 获取配方
        result = await session.execute(
            select(TalismanRecipe).where(TalismanRecipe.name == recipe_name)
        )
        recipe = result.scalar_one_or_none()

        if not recipe:
            await update.message.reply_text(f"❌ 未找到配方：{recipe_name}")
            return

        # 检查技能等级
        if skill.skill_level < recipe.required_talisman_skill:
            await update.message.reply_text(f"❌ 制符等级不足，需要Lv.{recipe.required_talisman_skill}")
            return

        # 检查灵力
        if player.spiritual_power < recipe.spiritual_power_cost:
            await update.message.reply_text(f"❌ 灵力不足，需要{recipe.spiritual_power_cost}灵力")
            return

        # 检查材料
        materials = json.loads(recipe.materials)
        missing = []

        for material in materials:
            item_id = material["item_id"]
            required_qty = material["quantity"]

            result = await session.execute(
                select(PlayerInventory).where(
                    PlayerInventory.player_id == player.id,
                    PlayerInventory.item_id == item_id,
                    PlayerInventory.is_equipped == False
                )
            )
            inv_items = result.scalars().all()

            total_qty = sum(inv.quantity for inv in inv_items)

            if total_qty < required_qty:
                result = await session.execute(
                    select(Item).where(Item.id == item_id)
                )
                item = result.scalar_one_or_none()
                item_name = item.name if item else f"ID:{item_id}"
                missing.append(f"{item_name}(缺{required_qty - total_qty})")

        if missing:
            await update.message.reply_text(f"❌ 材料不足：{', '.join(missing)}")
            return

        # 消耗材料
        for material in materials:
            item_id = material["item_id"]
            required_qty = material["quantity"]

            result = await session.execute(
                select(PlayerInventory).where(
                    PlayerInventory.player_id == player.id,
                    PlayerInventory.item_id == item_id,
                    PlayerInventory.is_equipped == False
                )
            )
            inv_items = result.scalars().all()

            remaining = required_qty
            for inv in inv_items:
                if remaining <= 0:
                    break

                if inv.quantity <= remaining:
                    remaining -= inv.quantity
                    await session.delete(inv)
                else:
                    inv.quantity -= remaining
                    remaining = 0

        # 消耗灵力
        player.spiritual_power -= recipe.spiritual_power_cost

        # 开始制作
        skill.is_crafting = True
        skill.crafting_recipe_id = recipe.id
        skill.crafting_start_time = datetime.now()
        skill.crafting_end_time = datetime.now() + timedelta(hours=recipe.duration_hours)

        await session.commit()

        msg = f"🔥 开始制作 {recipe.name}\n\n"
        msg += f"⏰ 预计{recipe.duration_hours}小时后完成\n"
        msg += f"💧 消耗灵力：{recipe.spiritual_power_cost}\n\n"
        msg += "💡 使用 /制符结算 完成制作"

        await update.message.reply_text(msg)


async def finish_craft_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """制符结算 - /制符结算"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        result = await session.execute(
            select(PlayerTalismanSkill).where(PlayerTalismanSkill.player_id == player.id)
        )
        skill = result.scalar_one_or_none()

        if not skill or not skill.is_crafting:
            await update.message.reply_text("❌ 没有正在进行的制作")
            return

        if datetime.now() < skill.crafting_end_time:
            remaining = skill.crafting_end_time - datetime.now()
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            await update.message.reply_text(f"❌ 制作未完成，还需{hours}小时{minutes}分钟")
            return

        # 获取配方
        result = await session.execute(
            select(TalismanRecipe).where(TalismanRecipe.id == skill.crafting_recipe_id)
        )
        recipe = result.scalar_one_or_none()

        if not recipe:
            skill.is_crafting = False
            await session.commit()
            await update.message.reply_text("❌ 配方数据错误")
            return

        # 计算成功率
        success_rate = recipe.base_success_rate
        level_bonus = (skill.skill_level - recipe.required_talisman_skill) * 0.05
        success_rate += level_bonus
        success_rate += player.comprehension * 0.01
        # 制符室加成
        cave_talisman_bonus = await CaveService.get_talisman_success_bonus(session, player.id)
        success_rate += cave_talisman_bonus
        success_rate = max(0.1, min(0.95, success_rate))

        # 判定成功
        is_success = random.random() < success_rate

        result_data = {
            "success": is_success,
            "recipe_name": recipe.name,
            "quality": 0,
            "exp": 0
        }

        if is_success:
            # 计算品质
            quality = 50 + min(skill.skill_level * 5, 50)
            quality += random.randint(-10, 10)
            quality = max(0, min(100, quality))

            # 添加到符箓库存
            result = await session.execute(
                select(PlayerTalisman).where(
                    PlayerTalisman.player_id == player.id,
                    PlayerTalisman.recipe_id == recipe.id,
                    PlayerTalisman.quality == quality
                )
            )
            talisman = result.scalar_one_or_none()

            if talisman:
                talisman.quantity += 1
            else:
                talisman = PlayerTalisman(
                    player_id=player.id,
                    recipe_id=recipe.id,
                    quantity=1,
                    quality=quality
                )
                session.add(talisman)

            skill.success_count += 1
            exp_gain = 100 + recipe.required_talisman_skill * 20
            result_data["quality"] = quality
        else:
            exp_gain = 20

        # 更新经验
        skill.skill_exp += exp_gain
        result_data["exp"] = exp_gain

        while skill.skill_exp >= skill.next_level_exp:
            skill.skill_exp -= skill.next_level_exp
            skill.skill_level += 1
            skill.next_level_exp = int(skill.next_level_exp * 1.5)
            result_data["level_up"] = skill.skill_level

        skill.total_crafts += 1

        # 记录
        record = TalismanCraftRecord(
            player_id=player.id,
            recipe_id=recipe.id,
            is_success=is_success,
            talisman_quality=quality if is_success else 0,
            exp_gained=exp_gain
        )
        session.add(record)

        # 重置状态
        skill.is_crafting = False
        skill.crafting_recipe_id = None
        skill.crafting_start_time = None
        skill.crafting_end_time = None

        await session.commit()

        if is_success:
            msg = f"🎉 制作成功！\n\n"
            msg += f"📜 获得：{recipe.name}\n"
            msg += f"✨ 品质：{quality}/100\n\n"
            msg += f"⭐ 经验：+{exp_gain}\n"

            if result_data.get("level_up"):
                msg += f"\n🎊 制符等级提升至 Lv.{result_data['level_up']}！"
        else:
            msg = f"💥 制作失败...\n\n"
            msg += f"⭐ 经验：+{exp_gain}\n"
            msg += "\n再接再厉！"

        await update.message.reply_text(msg)


async def cancel_craft_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """制符取消 - /制符取消"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        result = await session.execute(
            select(PlayerTalismanSkill).where(PlayerTalismanSkill.player_id == player.id)
        )
        skill = result.scalar_one_or_none()

        if not skill or not skill.is_crafting:
            await update.message.reply_text("❌ 没有正在进行的制作")
            return

        skill.is_crafting = False
        skill.crafting_recipe_id = None
        skill.crafting_start_time = None
        skill.crafting_end_time = None

        await session.commit()

        await update.message.reply_text("⚠️ 已取消制作，材料已消耗无法返还")


async def my_talismans_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看符箓 - /我的符箓"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        result = await session.execute(
            select(PlayerTalisman).where(PlayerTalisman.player_id == player.id)
        )
        talismans = result.scalars().all()

        if not talismans:
            await update.message.reply_text(
                "📜 您还没有符箓\n\n"
                "💡 使用 /制作符箓 <符箓名> 制作符箓"
            )
            return

        msg = "📜 【我的符箓】\n\n"

        for talisman in talismans:
            result = await session.execute(
                select(TalismanRecipe).where(TalismanRecipe.id == talisman.recipe_id)
            )
            recipe = result.scalar_one_or_none()

            if not recipe:
                continue

            msg += f"📜 **{recipe.name}** x{talisman.quantity}\n"
            msg += f"    类型：{recipe.talisman_type} | 品阶：{recipe.grade}\n"
            msg += f"    品质：{talisman.quality}/100\n"
            msg += f"    威力：{recipe.effect_power}\n"
            if recipe.effect_duration > 0:
                msg += f"    持续：{recipe.effect_duration}秒\n"
            msg += "\n"

        msg += "━━━━━━━━━━━━━━\n"
        msg += "💡 使用 /使用符箓 <符箓名> 使用符箓"

        await update.message.reply_text(msg, parse_mode="Markdown")


async def use_talisman_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """使用符箓 - /使用符箓 <符箓名>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定符箓名称\n"
            "用法：/使用符箓 <符箓名>\n"
            "例如：/使用符箓 金刚符"
        )
        return

    talisman_name = " ".join(context.args)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 查找符箓
        result = await session.execute(
            select(PlayerTalisman).join(TalismanRecipe).where(
                PlayerTalisman.player_id == player.id,
                TalismanRecipe.name == talisman_name
            )
        )
        talisman = result.scalar_one_or_none()

        if not talisman or talisman.quantity <= 0:
            await update.message.reply_text(f"❌ 没有 {talisman_name}")
            return

        result = await session.execute(
            select(TalismanRecipe).where(TalismanRecipe.id == talisman.recipe_id)
        )
        recipe = result.scalar_one_or_none()

        # 消耗符箓
        talisman.quantity -= 1
        if talisman.quantity == 0:
            await session.delete(talisman)

        # 应用效果
        effect_value = int(recipe.effect_power * (talisman.quality / 100))

        msg = f"✨ 使用 {recipe.name}\n\n"

        if recipe.talisman_type == "攻击符":
            player.attack += effect_value
            msg += f"⚔️ 攻击力提升 +{effect_value}\n"
            if recipe.effect_duration > 0:
                msg += f"⏰ 持续 {recipe.effect_duration}秒"
        elif recipe.talisman_type == "防御符":
            player.defense += effect_value
            msg += f"🛡️ 防御力提升 +{effect_value}\n"
            if recipe.effect_duration > 0:
                msg += f"⏰ 持续 {recipe.effect_duration}秒"
        elif recipe.talisman_type == "治疗符":
            player.hp = min(player.max_hp, player.hp + effect_value)
            msg += f"❤️ 恢复生命 +{effect_value}\n"
            msg += f"当前生命：{player.hp}/{player.max_hp}"
        elif recipe.talisman_type == "遁符":
            msg += f"💨 成功逃离！"
        else:
            msg += f"💫 产生神秘效果！"

        await session.commit()

        await update.message.reply_text(msg)


def register_handlers(application):
    """注册符箓相关处理器"""
    application.add_handler(CommandHandler("制符", talisman_skill_command))
    application.add_handler(CommandHandler("符箓图鉴", talisman_recipes_command))
    application.add_handler(CommandHandler("制作符箓", craft_talisman_command))
    application.add_handler(CommandHandler("制符结算", finish_craft_command))
    application.add_handler(CommandHandler("制符取消", cancel_craft_command))
    application.add_handler(CommandHandler("我的符箓", my_talismans_command))
    application.add_handler(CommandHandler("使用符箓", use_talisman_command))
