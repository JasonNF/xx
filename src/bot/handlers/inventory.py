"""背包系统handlers - 凡人修仙传版本"""
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.models.database import AsyncSessionLocal
from bot.models import Player, Item, PlayerInventory, ItemType
from bot.models.item import EquipmentQuality, EquipmentSlot
from bot.services.equipment_service import EquipmentService
from sqlalchemy import select


async def inventory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看背包 - /背包"""
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

        # 获取背包物品
        result = await session.execute(
            select(PlayerInventory, Item)
            .join(Item, PlayerInventory.item_id == Item.id)
            .where(PlayerInventory.player_id == player.id)
            .order_by(Item.item_type, Item.name)
        )
        inventory_items = result.all()

        if not inventory_items:
            await update.message.reply_text(
                "🎒 【储物袋】\n\n"
                "背包空空如也...\n\n"
                "💡 通过战斗、探索或商店获得物品"
            )
            return

        # 按类型分组
        items_by_type = {}
        for inv, item in inventory_items:
            type_name = item.item_type.value
            if type_name not in items_by_type:
                items_by_type[type_name] = []
            items_by_type[type_name].append((inv, item))

        # 构建消息
        msg = "🎒 【储物袋】\n\n"
        msg += f"道友：{player.nickname}\n"
        msg += f"💰 灵石：{player.spirit_stones}\n"
        msg += "━━━━━━━━━━━━━━\n\n"

        for type_name, items in items_by_type.items():
            type_icon = {
                "武器": "⚔️",
                "护甲": "🛡️",
                "饰品": "💍",
                "丹药": "💊",
                "灵药": "🌿",
                "矿石": "💎",
                "消耗品": "📦",
                "杂物": "📿"
            }.get(type_name, "📦")

            msg += f"{type_icon} **{type_name}**\n"

            for inv, item in items:
                equipped = " [已装备]" if inv.is_equipped else ""
                quantity = f" x{inv.quantity}" if inv.quantity > 1 else ""

                # 装备品质和强化等级
                quality_display = ""
                if item.quality:
                    quality_display = f" {EquipmentService.format_quality_display(item.quality)}"

                enhancement_display = ""
                if inv.enhancement_level > 0:
                    enhancement_display = EquipmentService.format_enhancement_display(inv.enhancement_level)

                msg += f"  • {item.name}{quality_display}{enhancement_display}{quantity}{equipped}\n"

                # 显示装备属性（考虑强化加成）
                if item.equipment_slot:
                    attributes = await EquipmentService.calculate_equipment_attributes(session, inv, item)
                    bonuses = []
                    if attributes["attack"] > 0:
                        bonuses.append(f"攻+{attributes['attack']}")
                    if attributes["defense"] > 0:
                        bonuses.append(f"防+{attributes['defense']}")
                    if attributes["hp"] > 0:
                        bonuses.append(f"HP+{attributes['hp']}")
                    if attributes["speed"] > 0:
                        bonuses.append(f"速+{attributes['speed']}")
                    if bonuses:
                        msg += f"    {' '.join(bonuses)}\n"
                else:
                    # 非装备显示原属性
                    bonuses = []
                    if item.attack_bonus > 0:
                        bonuses.append(f"攻+{item.attack_bonus}")
                    if item.defense_bonus > 0:
                        bonuses.append(f"防+{item.defense_bonus}")
                    if item.hp_bonus > 0:
                        bonuses.append(f"HP+{item.hp_bonus}")
                    if item.speed_bonus > 0:
                        bonuses.append(f"速+{item.speed_bonus}")
                    if bonuses:
                        msg += f"    {' '.join(bonuses)}\n"

                # 丹药效果
                if item.item_type == ItemType.PILL:
                    effects = []
                    if item.hp_restore > 0:
                        effects.append(f"恢复{item.hp_restore}HP")
                    if item.spiritual_restore > 0:
                        effects.append(f"恢复{item.spiritual_restore}灵力")
                    if item.exp_bonus > 0:
                        effects.append(f"+{item.exp_bonus}修为")
                    if effects:
                        msg += f"    效果：{', '.join(effects)}\n"

            msg += "\n"

        msg += "━━━━━━━━━━━━━━\n"
        msg += "💡 命令：\n"
        msg += "• /使用 <物品名> - 使用物品\n"
        msg += "• /装备 <物品名> - 装备法宝\n"
        msg += "• /卸下 <物品名> - 卸下装备\n"
        msg += "• /强化 <物品名> - 强化装备\n"
        msg += "• /装备详情 <物品名> - 查看装备详细信息\n"
        msg += "• /套装效果 - 查看当前套装效果"

        await update.message.reply_text(msg, parse_mode="Markdown")


async def use_item_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """使用物品 - /使用 <物品名>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定物品名称\n"
            "用法：/使用 <物品名称>\n"
            "例如：/使用 回气丹"
        )
        return

    item_name = " ".join(context.args)

    async with AsyncSessionLocal() as session:
        # 获取玩家
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 获取物品
        result = await session.execute(
            select(PlayerInventory, Item)
            .join(Item, PlayerInventory.item_id == Item.id)
            .where(
                PlayerInventory.player_id == player.id,
                Item.name == item_name
            )
        )
        inv_item = result.first()

        if not inv_item:
            await update.message.reply_text(
                f"❌ 未找到物品：{item_name}\n"
                "使用 /背包 查看拥有的物品"
            )
            return

        inv, item = inv_item

        # 检查物品类型
        if item.item_type not in [ItemType.PILL, ItemType.CONSUMABLE]:
            await update.message.reply_text(
                f"❌ {item.name} 无法使用\n"
                "只能使用丹药和消耗品"
            )
            return

        # 使用物品
        effects = []

        # 恢复HP
        if item.hp_restore > 0:
            old_hp = player.hp
            player.hp = min(player.max_hp, player.hp + item.hp_restore)
            restored = player.hp - old_hp
            effects.append(f"❤️ 恢复 {restored} 生命值")

        # 恢复灵力
        if item.spiritual_restore > 0:
            old_sp = player.spiritual_power
            player.spiritual_power = min(
                player.max_spiritual_power,
                player.spiritual_power + item.spiritual_restore
            )
            restored = player.spiritual_power - old_sp
            effects.append(f"💧 恢复 {restored} 灵力")

        # 增加修为
        if item.exp_bonus > 0:
            player.cultivation_exp += item.exp_bonus
            effects.append(f"⭐ 获得 {item.exp_bonus} 修为")

        # 减少数量或删除
        if inv.quantity > 1:
            inv.quantity -= 1
        else:
            await session.delete(inv)

        await session.commit()

        # 构建消息
        msg = f"✨ 使用了 {item.name}！\n\n"
        if effects:
            msg += "\n".join(effects) + "\n\n"

        msg += f"❤️ 生命：{player.hp}/{player.max_hp}\n"
        msg += f"💧 灵力：{player.spiritual_power}/{player.max_spiritual_power}\n"

        if item.exp_bonus > 0:
            msg += f"⭐ 修为：{player.cultivation_exp}/{player.next_realm_exp}"

        await update.message.reply_text(msg)


async def equip_item_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """装备物品 - /装备 <物品名>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定物品名称\n"
            "用法：/装备 <物品名称>\n"
            "例如：/装备 青钢剑"
        )
        return

    item_name = " ".join(context.args)

    async with AsyncSessionLocal() as session:
        # 获取玩家
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 获取物品
        result = await session.execute(
            select(PlayerInventory, Item)
            .join(Item, PlayerInventory.item_id == Item.id)
            .where(
                PlayerInventory.player_id == player.id,
                Item.name == item_name
            )
        )
        inv_item = result.first()

        if not inv_item:
            await update.message.reply_text(
                f"❌ 未找到物品：{item_name}\n"
                "使用 /背包 查看拥有的物品"
            )
            return

        inv, item = inv_item

        # 使用服务层装备物品
        success, message = await EquipmentService.equip_item(session, player.id, inv, item)

        if not success:
            await update.message.reply_text(message)
            return

        # 计算装备属性
        attributes = await EquipmentService.calculate_equipment_attributes(session, inv, item)

        # 构建消息
        msg = f"⚔️ 装备了 {item.name}！\n\n"

        # 显示品质和强化等级
        if item.quality:
            msg += f"品质：{EquipmentService.format_quality_display(item.quality)}\n"

        if inv.enhancement_level > 0:
            msg += f"强化：{EquipmentService.format_enhancement_display(inv.enhancement_level)}\n"

        msg += "\n属性加成：\n"
        if attributes["attack"] > 0:
            msg += f"  • 攻击 +{attributes['attack']}\n"
        if attributes["defense"] > 0:
            msg += f"  • 防御 +{attributes['defense']}\n"
        if attributes["hp"] > 0:
            msg += f"  • 生命 +{attributes['hp']}\n"
        if attributes["spiritual"] > 0:
            msg += f"  • 灵力 +{attributes['spiritual']}\n"
        if attributes["speed"] > 0:
            msg += f"  • 速度 +{attributes['speed']}\n"

        await update.message.reply_text(msg)


async def unequip_item_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """卸下装备 - /卸下 <物品名>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定物品名称\n"
            "用法：/卸下 <物品名称>\n"
            "例如：/卸下 青钢剑"
        )
        return

    item_name = " ".join(context.args)

    async with AsyncSessionLocal() as session:
        # 获取玩家
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 获取物品
        result = await session.execute(
            select(PlayerInventory, Item)
            .join(Item, PlayerInventory.item_id == Item.id)
            .where(
                PlayerInventory.player_id == player.id,
                Item.name == item_name,
                PlayerInventory.is_equipped == True
            )
        )
        inv_item = result.first()

        if not inv_item:
            await update.message.reply_text(
                f"❌ 未装备：{item_name}\n"
                "使用 /背包 查看已装备的物品"
            )
            return

        inv, item = inv_item

        # 使用服务层卸下装备
        success, message = await EquipmentService.unequip_item(session, inv, item)

        await update.message.reply_text(message)


async def enhance_equipment_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """强化装备 - /强化 <物品名>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定装备名称\n"
            "用法：/强化 <装备名称>\n"
            "例如：/强化 青龙战剑"
        )
        return

    item_name = " ".join(context.args)

    async with AsyncSessionLocal() as session:
        # 获取玩家
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 获取物品
        result = await session.execute(
            select(PlayerInventory, Item)
            .join(Item, PlayerInventory.item_id == Item.id)
            .where(
                PlayerInventory.player_id == player.id,
                Item.name == item_name
            )
        )
        inv_item = result.first()

        if not inv_item:
            await update.message.reply_text(
                f"❌ 未找到装备：{item_name}\n"
                "使用 /背包 查看拥有的装备"
            )
            return

        inv, item = inv_item

        # 显示强化信息
        from bot.config.equipment_config import (
            get_enhancement_success_rate,
            calculate_enhancement_cost,
            get_enhancement_penalty,
            ENHANCEMENT_MAX_LEVEL
        )

        max_level = ENHANCEMENT_MAX_LEVEL.get(item.quality.value if item.quality else "凡品", 10)
        current_level = inv.enhancement_level

        if current_level >= max_level:
            await update.message.reply_text(
                f"❌ {item.name} 已达最大强化等级 +{max_level}\n\n"
                f"品质：{EquipmentService.format_quality_display(item.quality)}"
            )
            return

        # 计算强化信息
        cost = calculate_enhancement_cost(current_level, item.quality.value if item.quality else "凡品")
        success_rate = get_enhancement_success_rate(current_level)
        penalty = get_enhancement_penalty(current_level)

        msg = f"⚒️ 【装备强化】\n\n"
        msg += f"装备：{item.name}\n"
        msg += f"品质：{EquipmentService.format_quality_display(item.quality)}\n"
        msg += f"当前强化：+{current_level}\n"
        msg += f"目标强化：+{current_level + 1}\n\n"

        msg += f"💰 消耗灵石：{cost:,}\n"
        msg += f"📊 成功率：{success_rate * 100:.0f}%\n"

        if penalty < 0:
            msg += f"⚠️ 失败惩罚：{penalty}\n"
        else:
            msg += f"✅ 失败不掉级\n"

        msg += f"\n拥有灵石：{player.spirit_stones:,}\n\n"
        msg += "━━━━━━━━━━━━━━\n"
        msg += "确认强化请回复：确认强化"

        await update.message.reply_text(msg)

        # 存储待强化的装备ID到用户数据
        context.user_data['pending_enhancement'] = {
            'inventory_id': inv.id,
            'item_name': item.name
        }


async def confirm_enhance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """确认强化 - 确认强化"""
    user = update.effective_user

    if 'pending_enhancement' not in context.user_data:
        await update.message.reply_text("❌ 没有待强化的装备")
        return

    pending_data = context.user_data['pending_enhancement']
    inventory_id = pending_data['inventory_id']

    async with AsyncSessionLocal() as session:
        # 获取玩家
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 获取装备
        result = await session.execute(
            select(PlayerInventory, Item)
            .join(Item, PlayerInventory.item_id == Item.id)
            .where(PlayerInventory.id == inventory_id)
        )
        inv_item = result.first()

        if not inv_item:
            await update.message.reply_text("❌ 装备不存在")
            del context.user_data['pending_enhancement']
            return

        inv, item = inv_item

        # 执行强化
        success, message, data = await EquipmentService.enhance_equipment(
            session, player, inv, item, use_protection=False
        )

        if not success or not data:
            await update.message.reply_text(message)
            del context.user_data['pending_enhancement']
            return

        # 构建详细消息
        msg = message + "\n\n"
        msg += f"━━━━━━━━━━━━━━\n"
        msg += f"💰 消耗灵石：{data['cost']:,}\n"
        msg += f"📊 成功率：{data['success_rate'] * 100:.0f}%\n"
        msg += f"💎 剩余灵石：{player.spirit_stones:,}\n\n"

        if data['success']:
            msg += f"✨ 装备属性提升了 5%！"
        else:
            msg += f"💪 不要灰心，下次一定成功！"

        await update.message.reply_text(msg)

        # 清除待强化数据
        del context.user_data['pending_enhancement']


async def equipment_detail_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """装备详情 - /装备详情 <物品名>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定装备名称\n"
            "用法：/装备详情 <装备名称>\n"
            "例如：/装备详情 青龙战剑"
        )
        return

    item_name = " ".join(context.args)

    async with AsyncSessionLocal() as session:
        # 获取玩家
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 获取物品
        result = await session.execute(
            select(PlayerInventory, Item)
            .join(Item, PlayerInventory.item_id == Item.id)
            .where(
                PlayerInventory.player_id == player.id,
                Item.name == item_name
            )
        )
        inv_item = result.first()

        if not inv_item:
            await update.message.reply_text(
                f"❌ 未找到装备：{item_name}\n"
                "使用 /背包 查看拥有的装备"
            )
            return

        inv, item = inv_item

        # 检查是否是装备
        if not item.equipment_slot:
            await update.message.reply_text(f"❌ {item.name} 不是装备")
            return

        # 计算装备属性
        attributes = await EquipmentService.calculate_equipment_attributes(session, inv, item)

        # 构建消息
        msg = f"⚔️ 【装备详情】\n\n"
        msg += f"名称：{item.name}\n"
        msg += f"品质：{EquipmentService.format_quality_display(item.quality) if item.quality else '未知'}\n"
        msg += f"槽位：{item.equipment_slot.value}\n"
        msg += f"强化：{EquipmentService.format_enhancement_display(inv.enhancement_level)}\n"
        msg += f"状态：{'[已装备]' if inv.is_equipped else '[未装备]'}\n\n"

        msg += f"━━━━━━━━━━━━━━\n"
        msg += f"📊 **当前属性**\n"
        if attributes["attack"] > 0:
            msg += f"  ⚔️ 攻击：{attributes['attack']}\n"
        if attributes["defense"] > 0:
            msg += f"  🛡️ 防御：{attributes['defense']}\n"
        if attributes["hp"] > 0:
            msg += f"  ❤️ 生命：{attributes['hp']}\n"
        if attributes["spiritual"] > 0:
            msg += f"  💧 灵力：{attributes['spiritual']}\n"
        if attributes["speed"] > 0:
            msg += f"  💨 速度：{attributes['speed']}\n"

        # 显示套装信息
        if item.set_id:
            from bot.models.item import EquipmentSet
            result = await session.execute(
                select(EquipmentSet).where(EquipmentSet.id == item.set_id)
            )
            equipment_set = result.scalar_one_or_none()
            if equipment_set:
                msg += f"\n━━━━━━━━━━━━━━\n"
                msg += f"🔮 **套装信息**\n"
                msg += f"  {equipment_set.name}\n"
                msg += f"  {equipment_set.description}\n"

        # 显示强化信息
        from bot.config.equipment_config import ENHANCEMENT_MAX_LEVEL
        max_level = ENHANCEMENT_MAX_LEVEL.get(item.quality.value if item.quality else "凡品", 10)

        msg += f"\n━━━━━━━━━━━━━━\n"
        msg += f"⚒️ **强化信息**\n"
        msg += f"  当前等级：+{inv.enhancement_level}\n"
        msg += f"  最大等级：+{max_level}\n"

        if inv.enhancement_level < max_level:
            msg += f"\n💡 使用 /强化 {item.name} 进行强化"

        await update.message.reply_text(msg, parse_mode="Markdown")


async def set_bonus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """套装效果 - /套装效果"""
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

        # 获取套装效果
        active_sets = await EquipmentService.check_set_bonus(session, player.id)

        if not active_sets:
            await update.message.reply_text(
                "🔮 【套装效果】\n\n"
                "当前没有激活的套装效果\n\n"
                "💡 装备同一套装的多件装备可激活套装效果"
            )
            return

        # 构建消息
        msg = f"🔮 【套装效果】\n\n"

        for set_name, bonuses_list in active_sets.items():
            msg += f"**{set_name}套装** ✨\n"

            for bonus_data in bonuses_list:
                piece_count = bonus_data["piece_count"]
                bonuses = bonus_data["bonuses"]

                msg += f"\n{piece_count}件套效果：\n"
                for bonus in bonuses:
                    desc = bonus.get("desc", "")
                    bonus_type = bonus.get("type", "")

                    # 特殊技能显示
                    if bonus_type == "special_skill":
                        skill_name = bonus.get("value", "")
                        msg += f"  ⚡ {skill_name}：{desc}\n"
                    else:
                        msg += f"  • {desc}\n"

            msg += "\n━━━━━━━━━━━━━━\n"

        msg += "\n💡 使用 /装备详情 查看装备所属套装"

        await update.message.reply_text(msg, parse_mode="Markdown")


def register_handlers(application):
    """注册背包相关处理器"""
    application.add_handler(CommandHandler("背包", inventory_command))
    application.add_handler(CommandHandler("使用", use_item_command))
    application.add_handler(CommandHandler("装备", equip_item_command))
    application.add_handler(CommandHandler("卸下", unequip_item_command))
    application.add_handler(CommandHandler("强化", enhance_equipment_command))
    application.add_handler(CommandHandler("确认强化", confirm_enhance_command))
    application.add_handler(CommandHandler("装备详情", equipment_detail_command))
    application.add_handler(CommandHandler("套装效果", set_bonus_command))
