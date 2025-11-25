"""商店系统handlers - 凡人修仙传版本"""
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.models.database import AsyncSessionLocal
from bot.models import Player, Item, PlayerInventory, ItemType
from sqlalchemy import select


async def shop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看商店 - /商店 [类型]"""
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

        # 筛选类型
        filter_type = None
        if context.args:
            type_map = {
                "丹药": ItemType.PILL,
                "武器": ItemType.WEAPON,
                "护甲": ItemType.ARMOR,
                "饰品": ItemType.ACCESSORY,
                "材料": ItemType.MATERIAL
            }
            filter_type = type_map.get(context.args[0])

        # 获取商店物品
        query = select(Item).where(Item.buy_price > 0)
        if filter_type:
            query = query.where(Item.item_type == filter_type)
        query = query.order_by(Item.item_type, Item.buy_price)

        result = await session.execute(query)
        items = result.scalars().all()

        if not items:
            msg = "🏪 【坊市】\n\n"
            msg += "暂无商品出售"
            if filter_type:
                msg += f"\n\n💡 尝试查看其他类型：/商店"
            await update.message.reply_text(msg)
            return

        # 按类型分组
        items_by_type = {}
        for item in items:
            type_name = item.item_type.value
            if type_name not in items_by_type:
                items_by_type[type_name] = []
            items_by_type[type_name].append(item)

        # 构建消息
        msg = "🏪 【坊市】\n\n"
        msg += f"道友：{player.nickname}\n"
        msg += f"💰 灵石：{player.spirit_stones}\n"
        msg += "━━━━━━━━━━━━━━\n\n"

        for type_name, type_items in items_by_type.items():
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

            for item in type_items:
                can_buy = "✅" if player.spirit_stones >= item.buy_price else "🔒"
                msg += f"{can_buy} {item.name}\n"
                msg += f"    💰 {item.buy_price} 灵石\n"

                # 显示效果
                if item.item_type == ItemType.PILL:
                    effects = []
                    if item.hp_restore > 0:
                        effects.append(f"HP+{item.hp_restore}")
                    if item.spiritual_restore > 0:
                        effects.append(f"灵力+{item.spiritual_restore}")
                    if item.exp_bonus > 0:
                        effects.append(f"修为+{item.exp_bonus}")
                    if effects:
                        msg += f"    效果：{', '.join(effects)}\n"
                else:
                    bonuses = []
                    if item.attack_bonus > 0:
                        bonuses.append(f"攻+{item.attack_bonus}")
                    if item.defense_bonus > 0:
                        bonuses.append(f"防+{item.defense_bonus}")
                    if item.hp_bonus > 0:
                        bonuses.append(f"HP+{item.hp_bonus}")
                    if bonuses:
                        msg += f"    属性：{' '.join(bonuses)}\n"

            msg += "\n"

        msg += "━━━━━━━━━━━━━━\n"
        msg += "💡 命令：\n"
        msg += "• /购买 <物品名> [数量] - 购买物品\n"
        msg += "• /出售 <物品名> [数量] - 出售物品\n"
        msg += "• /商店 丹药 - 筛选类型"

        await update.message.reply_text(msg, parse_mode="Markdown")


async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """购买物品 - /购买 <物品名> [数量]"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定物品名称\n"
            "用法：/购买 <物品名称> [数量]\n"
            "例如：/购买 回气丹 5"
        )
        return

    # 解析参数
    args = context.args
    quantity = 1
    if len(args) >= 2 and args[-1].isdigit():
        quantity = int(args[-1])
        item_name = " ".join(args[:-1])
    else:
        item_name = " ".join(args)

    if quantity <= 0:
        await update.message.reply_text("❌ 数量必须大于0")
        return

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
            select(Item).where(Item.name == item_name, Item.buy_price > 0)
        )
        item = result.scalar_one_or_none()

        if not item:
            await update.message.reply_text(
                f"❌ 未找到商品：{item_name}\n"
                "使用 /商店 查看可购买的商品"
            )
            return

        # 计算总价
        total_cost = item.buy_price * quantity

        # 检查灵石
        if player.spirit_stones < total_cost:
            await update.message.reply_text(
                f"❌ 灵石不足\n\n"
                f"需要：{total_cost} 灵石\n"
                f"拥有：{player.spirit_stones} 灵石"
            )
            return

        # 扣除灵石
        player.spirit_stones -= total_cost

        # 添加到背包
        result = await session.execute(
            select(PlayerInventory).where(
                PlayerInventory.player_id == player.id,
                PlayerInventory.item_id == item.id,
                PlayerInventory.is_equipped == False
            )
        )
        existing = result.scalar_one_or_none()

        if existing and item.is_stackable:
            existing.quantity += quantity
        else:
            for _ in range(quantity):
                new_inv = PlayerInventory(
                    player_id=player.id,
                    item_id=item.id,
                    quantity=1
                )
                session.add(new_inv)

        await session.commit()

        # 构建消息
        msg = f"🛒 购买成功！\n\n"
        msg += f"📦 {item.name}"
        if quantity > 1:
            msg += f" x{quantity}"
        msg += "\n"
        msg += f"💰 花费：{total_cost} 灵石\n"
        msg += f"💰 剩余：{player.spirit_stones} 灵石"

        await update.message.reply_text(msg)


async def sell_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """出售物品 - /出售 <物品名> [数量]"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定物品名称\n"
            "用法：/出售 <物品名称> [数量]\n"
            "例如：/出售 野猪皮 10"
        )
        return

    # 解析参数
    args = context.args
    quantity = 1
    if len(args) >= 2 and args[-1].isdigit():
        quantity = int(args[-1])
        item_name = " ".join(args[:-1])
    else:
        item_name = " ".join(args)

    if quantity <= 0:
        await update.message.reply_text("❌ 数量必须大于0")
        return

    async with AsyncSessionLocal() as session:
        # 获取玩家
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 获取玩家背包中的物品
        result = await session.execute(
            select(PlayerInventory, Item)
            .join(Item, PlayerInventory.item_id == Item.id)
            .where(
                PlayerInventory.player_id == player.id,
                Item.name == item_name,
                PlayerInventory.is_equipped == False
            )
        )
        inv_items = result.all()

        if not inv_items:
            await update.message.reply_text(
                f"❌ 未找到可出售的物品：{item_name}\n"
                "• 已装备的物品需要先卸下\n"
                "使用 /背包 查看拥有的物品"
            )
            return

        # 计算总数量
        total_quantity = sum(inv.quantity for inv, _ in inv_items)
        if total_quantity < quantity:
            await update.message.reply_text(
                f"❌ 数量不足\n\n"
                f"需要：{quantity}\n"
                f"拥有：{total_quantity}"
            )
            return

        # 获取售价
        item = inv_items[0][1]
        if item.sell_price <= 0:
            await update.message.reply_text(f"❌ {item.name} 无法出售")
            return

        # 计算收入
        total_income = item.sell_price * quantity

        # 从背包移除
        remaining = quantity
        for inv, _ in inv_items:
            if remaining <= 0:
                break

            if inv.quantity <= remaining:
                remaining -= inv.quantity
                await session.delete(inv)
            else:
                inv.quantity -= remaining
                remaining = 0

        # 增加灵石
        player.spirit_stones += total_income

        await session.commit()

        # 构建消息
        msg = f"💰 出售成功！\n\n"
        msg += f"📦 {item.name}"
        if quantity > 1:
            msg += f" x{quantity}"
        msg += "\n"
        msg += f"💰 获得：{total_income} 灵石\n"
        msg += f"💰 现有：{player.spirit_stones} 灵石"

        await update.message.reply_text(msg)


def register_handlers(application):
    """注册商店相关处理器"""
    application.add_handler(CommandHandler("商店", shop_command))
    application.add_handler(CommandHandler("购买", buy_command))
    application.add_handler(CommandHandler("出售", sell_command))
