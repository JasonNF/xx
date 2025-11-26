"""积分商城处理器"""
import json
from datetime import datetime, timedelta
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import (
    get_db,
    Player,
    CreditShopItem,
    CreditShopCategory,
    CreditShopPurchase,
    PlayerCreditShopLimit,
    CreditType,
    PlayerInventory,
)
from bot.services.player_service import PlayerService
from bot.services.credit_service import CreditService


async def credit_shop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """积分商城主菜单 - /积分商城 或 /商城"""
    user_id = update.effective_user.id

    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user_id)
        if not player:
            await update.message.reply_text("❌ 请先使用 /检测灵根 开始修仙之旅")
            return

        # 创建分类按钮
        keyboard = [
            [
                InlineKeyboardButton("📖 功法", callback_data="shop_category_CULTIVATION_METHOD"),
                InlineKeyboardButton("⚔️ 法宝", callback_data="shop_category_TREASURE"),
            ],
            [
                InlineKeyboardButton("💊 丹药", callback_data="shop_category_PILL"),
                InlineKeyboardButton("✨ 特殊物品", callback_data="shop_category_SPECIAL"),
            ],
            [
                InlineKeyboardButton("🌟 精选商品", callback_data="shop_featured"),
                InlineKeyboardButton("📊 我的积分", callback_data="shop_my_credits"),
            ],
            [
                InlineKeyboardButton("💎 积分兑换灵石", callback_data="shop_exchange_spirit_stones"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = f"""
🏪 ═══════ 积分商城 ═══════

👤 道号：{player.nickname}
💰 当前积分：{player.credits:,}
💎 当前灵石：{player.spirit_stones:,}
🌟 境界：{player.full_realm_name}

━━━━━━━━━━━━━━━
📦 商品分类

📖 功法：极品功法，提升修炼速度
⚔️ 法宝：神器法宝，战力飙升
💊 丹药：突破丹药，成功率提升
✨ 特殊物品：稀有道具，奇珍异宝

━━━━━━━━━━━━━━━
💎 积分兑换

• 兑换比例：1积分 = 10灵石
• 无手续费，即时到账
• 随时可兑换

━━━━━━━━━━━━━━━
💡 提示：
• 点击分类查看商品
• 部分商品有境界要求
• 限量商品先到先得
━━━━━━━━━━━━━━━
"""

        await update.message.reply_text(text, reply_markup=reply_markup)


async def shop_category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理分类选择回调"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    callback_data = query.data

    if callback_data == "shop_featured":
        # 显示精选商品
        await show_featured_items(query, user_id)
    elif callback_data == "shop_my_credits":
        # 显示我的积分
        await show_my_credits(query, user_id)
    elif callback_data == "shop_exchange_spirit_stones":
        # 兑换灵石
        await show_exchange_spirit_stones(query, user_id)
    elif callback_data.startswith("shop_exchange_confirm_"):
        # 确认兑换
        amount = int(callback_data.replace("shop_exchange_confirm_", ""))
        await confirm_exchange_spirit_stones(query, user_id, amount)
    elif callback_data.startswith("shop_category_"):
        # 显示分类商品
        category_name = callback_data.replace("shop_category_", "")
        await show_category_items(query, user_id, category_name)
    elif callback_data.startswith("shop_item_"):
        # 显示商品详情
        item_id = int(callback_data.replace("shop_item_", ""))
        await show_item_detail(query, user_id, item_id)
    elif callback_data.startswith("shop_buy_"):
        # 购买商品
        item_id = int(callback_data.replace("shop_buy_", ""))
        await purchase_item(query, user_id, item_id)
    elif callback_data == "shop_back":
        # 返回主菜单
        await credit_shop_command(update, context)


async def show_category_items(query, user_id: int, category_name: str):
    """显示分类商品列表"""
    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user_id)
        if not player:
            await query.edit_message_text("❌ 玩家不存在")
            return

        # 查询分类商品
        category = CreditShopCategory[category_name]
        result = await db.execute(
            select(CreditShopItem)
            .where(
                and_(
                    CreditShopItem.category == category,
                    CreditShopItem.is_active == True,
                    # 检查时间限制
                    (CreditShopItem.available_from == None) | (CreditShopItem.available_from <= datetime.now()),
                    (CreditShopItem.available_until == None) | (CreditShopItem.available_until >= datetime.now()),
                )
            )
            .order_by(CreditShopItem.sort_order, CreditShopItem.credit_price.desc())
        )
        items = result.scalars().all()

        if not items:
            await query.edit_message_text(f"❌ {category.value} 分类暂无商品")
            return

        # 构建商品列表
        text = f"🏪 {category.value} 分类\n\n"
        text += f"💰 你的积分：{player.credits:,}\n\n"
        text += "━━━━━━━━━━━━━━━\n"

        keyboard = []
        for item in items[:10]:  # 限制显示10个
            # 检查库存
            stock_text = ""
            if item.total_stock != -1:
                if item.remaining_stock <= 0:
                    stock_text = " [已售罄]"
                elif item.remaining_stock <= 5:
                    stock_text = f" [仅剩{item.remaining_stock}]"

            # 检查购买限制
            limit_text = ""
            if item.purchase_limit_per_player != -1:
                limit_text = f" [限购{item.purchase_limit_per_player}]"

            # 显示折扣
            price_text = f"{item.credit_price:,}"
            if item.discount_rate < 1.0:
                discount_percent = int((1 - item.discount_rate) * 100)
                actual_price = int(item.credit_price * item.discount_rate)
                price_text = f"~~{item.credit_price:,}~~ {actual_price:,} ({discount_percent}%OFF)"

            item_text = f"{item.icon or '📦'} {item.name}\n"
            item_text += f"   💎 {price_text} 积分{stock_text}{limit_text}\n"

            # 显示需求
            if item.required_realm:
                item_text += f"   🔒 需求：{item.required_realm}"
                if item.required_level > 1:
                    item_text += f" {item.required_level}层"
                item_text += "\n"

            text += item_text + "\n"

            # 添加按钮
            button_text = f"{item.icon or '📦'} {item.name}"
            if item.remaining_stock == 0:
                button_text += " [售罄]"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"shop_item_{item.id}")])

        keyboard.append([InlineKeyboardButton("« 返回主菜单", callback_data="shop_back")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup)


async def show_featured_items(query, user_id: int):
    """显示精选商品"""
    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user_id)
        if not player:
            await query.edit_message_text("❌ 玩家不存在")
            return

        # 查询精选商品
        result = await db.execute(
            select(CreditShopItem)
            .where(
                and_(
                    CreditShopItem.is_featured == True,
                    CreditShopItem.is_active == True,
                    (CreditShopItem.available_from == None) | (CreditShopItem.available_from <= datetime.now()),
                    (CreditShopItem.available_until == None) | (CreditShopItem.available_until >= datetime.now()),
                )
            )
            .order_by(CreditShopItem.sort_order)
        )
        items = result.scalars().all()

        if not items:
            await query.edit_message_text("❌ 暂无精选商品")
            return

        text = "🌟 ═══ 精选商品 ═══ 🌟\n\n"
        text += f"💰 你的积分：{player.credits:,}\n\n"
        text += "━━━━━━━━━━━━━━━\n"

        keyboard = []
        for item in items:
            stock_text = ""
            if item.total_stock != -1 and item.remaining_stock <= 5:
                stock_text = f" [仅剩{item.remaining_stock}]"

            item_text = f"{item.icon or '📦'} {item.name}\n"
            item_text += f"   {item.description[:50]}...\n"
            item_text += f"   💎 {item.credit_price:,} 积分{stock_text}\n\n"

            text += item_text

            button_text = f"{item.icon or '📦'} {item.name}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"shop_item_{item.id}")])

        keyboard.append([InlineKeyboardButton("« 返回主菜单", callback_data="shop_back")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup)


async def show_item_detail(query, user_id: int, item_id: int):
    """显示商品详情"""
    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user_id)
        if not player:
            await query.edit_message_text("❌ 玩家不存在")
            return

        # 查询商品
        item = await db.get(CreditShopItem, item_id)
        if not item or not item.is_active:
            await query.edit_message_text("❌ 商品不存在或已下架")
            return

        # 检查购买限制
        limit_info = await get_purchase_limit_info(db, player.id, item_id)

        # 计算实际价格
        actual_price = int(item.credit_price * item.discount_rate)

        # 构建详情文本
        text = f"{item.icon or '📦'} {item.name}\n\n"
        text += f"📝 描述：{item.description}\n\n"
        text += f"🏷️ 分类：{item.category.value}\n"
        text += f"💎 价格：{actual_price:,} 积分"

        if item.discount_rate < 1.0:
            discount_percent = int((1 - item.discount_rate) * 100)
            text += f" (原价 {item.credit_price:,}, {discount_percent}%OFF)"
        text += "\n"

        # 库存信息
        if item.total_stock != -1:
            text += f"📦 库存：{item.remaining_stock}/{item.total_stock}\n"
        else:
            text += "📦 库存：无限\n"

        # 限购信息
        if item.purchase_limit_per_player != -1:
            text += f"🔢 限购：每人限购 {item.purchase_limit_per_player} 次"
            if limit_info:
                text += f"（已购 {limit_info.total_purchased} 次）"
            text += "\n"

        if item.daily_purchase_limit != -1:
            text += f"📅 每日限购：{item.daily_purchase_limit} 次"
            if limit_info:
                text += f"（今日已购 {limit_info.daily_purchased} 次）"
            text += "\n"

        # 需求信息
        if item.required_realm:
            text += f"🔒 境界要求：{item.required_realm}"
            if item.required_level > 1:
                text += f" {item.required_level}层"
            text += "\n"

        if item.required_vip_level > 0:
            text += f"👑 VIP要求：VIP{item.required_vip_level}\n"

        # 标签
        if item.tags:
            text += f"🏷️ 标签：{item.tags}\n"

        text += "\n━━━━━━━━━━━━━━━\n"
        text += f"💰 你的积分：{player.credits:,}\n"

        # 检查是否可以购买
        can_buy, reason = await can_purchase_item(db, player, item, limit_info)

        keyboard = []
        if can_buy:
            keyboard.append([InlineKeyboardButton("✅ 立即兑换", callback_data=f"shop_buy_{item.id}")])
        else:
            text += f"\n❌ 无法购买：{reason}\n"

        keyboard.append([InlineKeyboardButton("« 返回分类", callback_data=f"shop_category_{item.category.name}")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup)


async def purchase_item(query, user_id: int, item_id: int):
    """购买商品"""
    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user_id)
        if not player:
            await query.answer("❌ 玩家不存在", show_alert=True)
            return

        # 查询商品
        item = await db.get(CreditShopItem, item_id)
        if not item or not item.is_active:
            await query.answer("❌ 商品不存在或已下架", show_alert=True)
            return

        # 检查购买限制
        limit_info = await get_purchase_limit_info(db, player.id, item_id)
        can_buy, reason = await can_purchase_item(db, player, item, limit_info)

        if not can_buy:
            await query.answer(f"❌ {reason}", show_alert=True)
            return

        # 计算实际价格
        actual_price = int(item.credit_price * item.discount_rate)

        # 扣除积分
        success, message = await CreditService.deduct_credits(
            db, player, actual_price, CreditType.EXCHANGE_DEDUCT,
            f"兑换：{item.name}", item.id
        )

        if not success:
            await query.answer(f"❌ {message}", show_alert=True)
            return

        # 减少库存
        if item.total_stock != -1:
            item.remaining_stock -= 1
            item.sold_count += 1

        # 创建购买记录
        purchase = CreditShopPurchase(
            player_id=player.id,
            shop_item_id=item.id,
            item_name=item.name,
            quantity=1,
            credit_cost=actual_price,
            original_price=item.credit_price,
            player_realm=player.realm.value,
            player_level=player.realm_level,
        )
        db.add(purchase)

        # 更新限购记录
        if not limit_info:
            limit_info = PlayerCreditShopLimit(
                player_id=player.id,
                shop_item_id=item.id,
                total_purchased=0,
                daily_purchased=0,
            )
            db.add(limit_info)

        limit_info.total_purchased += 1
        limit_info.last_purchase_date = datetime.now()

        # 检查是否需要重置每日限购
        if limit_info.daily_reset_date:
            if (datetime.now() - limit_info.daily_reset_date).days >= 1:
                limit_info.daily_purchased = 1
                limit_info.daily_reset_date = datetime.now()
            else:
                limit_info.daily_purchased += 1
        else:
            limit_info.daily_purchased = 1
            limit_info.daily_reset_date = datetime.now()

        await db.commit()
        await db.refresh(player)

        # 发放物品到玩家背包
        delivery_success = False
        delivery_message = ""

        if item.item_id:
            # 商品关联了具体物品，添加到背包
            result = await db.execute(
                select(PlayerInventory).where(
                    and_(
                        PlayerInventory.player_id == player.id,
                        PlayerInventory.item_id == item.item_id
                    )
                )
            )
            existing_inv = result.scalar_one_or_none()

            if existing_inv:
                existing_inv.quantity += 1
            else:
                new_inv = PlayerInventory(
                    player_id=player.id,
                    item_id=item.item_id,
                    quantity=1
                )
                db.add(new_inv)

            await db.commit()
            delivery_success = True
            delivery_message = "💼 物品已发放到背包"
        elif item.special_effects:
            # 特殊效果商品，解析并应用效果
            try:
                effects = json.loads(item.special_effects)
                effect_messages = []

                for effect in effects if isinstance(effects, list) else [effects]:
                    effect_type = effect.get("type")
                    value = effect.get("value", 0)

                    if effect_type == "spirit_stones":
                        player.spirit_stones += value
                        effect_messages.append(f"💰 灵石 +{value:,}")
                    elif effect_type == "exp":
                        player.cultivation_exp += value
                        effect_messages.append(f"⭐ 修为 +{value:,}")
                    elif effect_type == "spiritual_power":
                        player.spiritual_power = min(
                            player.max_spiritual_power,
                            player.spiritual_power + value
                        )
                        effect_messages.append(f"💧 灵力 +{value}")
                    elif effect_type == "hp_recovery":
                        player.hp = min(player.max_hp, player.hp + value)
                        effect_messages.append(f"❤️ 生命恢复 +{value}")
                    elif effect_type == "comprehension":
                        player.comprehension += value
                        effect_messages.append(f"🧠 悟性 +{value}")
                    elif effect_type == "contribution":
                        player.contribution += value
                        effect_messages.append(f"🏛️ 门派贡献 +{value}")

                await db.commit()
                delivery_success = True
                delivery_message = "✨ 效果已生效：\n" + "\n".join(effect_messages)
            except (json.JSONDecodeError, TypeError):
                delivery_message = "⚠️ 特殊效果应用失败，请联系管理员"
        else:
            # 无具体物品也无特殊效果，可能是虚拟商品
            delivery_success = True
            delivery_message = "📜 兑换凭证已记录"

        success_text = f"""
✅ 兑换成功！

{item.icon or '📦'} {item.name}

━━━━━━━━━━━━━━━
💸 消耗积分：{actual_price:,}
💰 剩余积分：{player.credits:,}
━━━━━━━━━━━━━━━

{item.description}

{delivery_message}
"""

        await query.answer("✅ 兑换成功！", show_alert=False)
        await query.edit_message_text(success_text)


async def exchange_credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """兑换积分为灵石 - /兑换灵石 [积分数量]"""
    user_id = update.effective_user.id

    # 检查参数
    if not context.args or len(context.args) == 0:
        await update.message.reply_text(
            "❌ 用法错误\n\n"
            "正确用法: /兑换灵石 <积分数量>\n\n"
            "💎 兑换比例: 1积分 = 10灵石\n\n"
            "示例:\n"
            "• /兑换灵石 100  (兑换1,000灵石)\n"
            "• /兑换灵石 1000 (兑换10,000灵石)\n\n"
            "💡 也可以通过 /积分商城 使用快捷兑换"
        )
        return

    try:
        credit_amount = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ 请输入有效的积分数量")
        return

    if credit_amount <= 0:
        await update.message.reply_text("❌ 兑换数量必须大于0")
        return

    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user_id)
        if not player:
            await update.message.reply_text("❌ 请先使用 /检测灵根 开始修仙之旅")
            return

        # 执行兑换
        success, message = await CreditService.exchange_credits_to_spirit_stones(
            db, player, credit_amount
        )

        await update.message.reply_text(message if success else f"❌ {message}")


async def my_credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看我的积分 - /我的积分"""
    user_id = update.effective_user.id

    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user_id)
        if not player:
            await update.message.reply_text("❌ 请先使用 /检测灵根 开始修仙之旅")
            return

        # 获取积分统计
        summary = await CreditService.get_credit_summary(db, player.id)

        # 获取最近记录
        records = await CreditService.get_credit_records(db, player.id, limit=10)

        text = f"""
💰 ═══ 我的积分 ═══ 💰

👤 道号：{player.nickname}
💎 当前积分：{player.credits:,}

━━━━━━━━━━━━━━━
📊 积分统计

💰 累计获得：{summary['total_gained']:,}
💸 累计消耗：{summary['total_spent']:,}
📝 记录总数：{summary['total_records']}

━━━━━━━━━━━━━━━
📋 最近记录

"""

        if records:
            for record in records:
                text += CreditService.format_credit_record(record) + "\n"
        else:
            text += "暂无积分记录\n"

        text += "\n━━━━━━━━━━━━━━━\n"
        text += "💡 获取积分途径：\n"
        text += "• 每日签到\n"
        text += "• 完成任务\n"
        text += "• 竞技场胜利\n"
        text += "• 击杀世界BOSS\n"
        text += "• 境界突破\n"
        text += "• 完成成就\n\n"
        text += "━━━━━━━━━━━━━━━\n"
        text += "💎 积分用途：\n"
        text += "• 积分商城兑换物品\n"
        text += "• 兑换灵石 (1积分=10灵石)\n"
        text += "• 使用 /兑换灵石 <数量>\n"

        await update.message.reply_text(text)


async def show_my_credits(query, user_id: int):
    """显示我的积分（回调版本）"""
    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user_id)
        if not player:
            await query.edit_message_text("❌ 玩家不存在")
            return

        summary = await CreditService.get_credit_summary(db, player.id)
        records = await CreditService.get_credit_records(db, player.id, limit=10)

        text = f"""
💰 ═══ 我的积分 ═══ 💰

👤 道号：{player.nickname}
💎 当前积分：{player.credits:,}

━━━━━━━━━━━━━━━
📊 积分统计

💰 累计获得：{summary['total_gained']:,}
💸 累计消耗：{summary['total_spent']:,}
📝 记录总数：{summary['total_records']}

━━━━━━━━━━━━━━━
📋 最近10条记录

"""

        if records:
            for record in records:
                text += CreditService.format_credit_record(record) + "\n"
        else:
            text += "暂无积分记录\n"

        keyboard = [[InlineKeyboardButton("« 返回主菜单", callback_data="shop_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup)


async def get_purchase_limit_info(
    db: AsyncSession, player_id: int, item_id: int
) -> Optional[PlayerCreditShopLimit]:
    """获取购买限制信息"""
    result = await db.execute(
        select(PlayerCreditShopLimit).where(
            and_(
                PlayerCreditShopLimit.player_id == player_id,
                PlayerCreditShopLimit.shop_item_id == item_id,
            )
        )
    )
    return result.scalar_one_or_none()


async def can_purchase_item(
    db: AsyncSession,
    player: Player,
    item: CreditShopItem,
    limit_info: Optional[PlayerCreditShopLimit],
) -> tuple[bool, str]:
    """检查是否可以购买商品"""
    # 检查库存
    if item.total_stock != -1 and item.remaining_stock <= 0:
        return False, "商品已售罄"

    # 检查积分
    actual_price = int(item.credit_price * item.discount_rate)
    if player.credits < actual_price:
        return False, f"积分不足（需要 {actual_price:,}，拥有 {player.credits:,}）"

    # 检查境界要求
    if item.required_realm:
        from bot.models import RealmType
        # 使用枚举的索引来比较境界高低
        realm_order = list(RealmType)
        try:
            required_realm = RealmType(item.required_realm)
            required_idx = realm_order.index(required_realm)
            player_idx = realm_order.index(player.realm)
            if player_idx < required_idx:
                return False, f"境界不足（需要 {item.required_realm}）"
            if player.realm == required_realm and player.realm_level < item.required_level:
                return False, f"境界等级不足（需要 {item.required_realm} {item.required_level}层）"
        except ValueError:
            pass  # 如果境界字符串无效，跳过检查

    # 检查VIP等级
    if item.required_vip_level > 0:
        # TODO: 实现VIP系统后添加检查
        pass

    # 检查总限购
    if item.purchase_limit_per_player != -1:
        if limit_info and limit_info.total_purchased >= item.purchase_limit_per_player:
            return False, f"已达购买上限（{item.purchase_limit_per_player}次）"

    # 检查每日限购
    if item.daily_purchase_limit != -1:
        if limit_info:
            # 检查是否需要重置
            if limit_info.daily_reset_date:
                days_passed = (datetime.now() - limit_info.daily_reset_date).days
                if days_passed >= 1:
                    # 需要重置，可以购买
                    pass
                elif limit_info.daily_purchased >= item.daily_purchase_limit:
                    return False, f"今日购买次数已用完（{item.daily_purchase_limit}次）"

    return True, ""


async def show_exchange_spirit_stones(query, user_id: int):
    """显示兑换灵石界面"""
    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user_id)
        if not player:
            await query.edit_message_text("❌ 玩家不存在")
            return

        # 兑换比例
        EXCHANGE_RATE = 10

        text = f"""
💎 ═══ 积分兑换灵石 ═══ 💎

👤 道号：{player.nickname}
💰 当前积分：{player.credits:,}
💎 当前灵石：{player.spirit_stones:,}

━━━━━━━━━━━━━━━
📋 兑换比例

1 积分 = {EXCHANGE_RATE} 灵石

━━━━━━━━━━━━━━━
💡 快捷兑换选项

"""

        # 快捷兑换选项
        exchange_options = [100, 500, 1000, 5000, 10000]

        keyboard = []
        for amount in exchange_options:
            if player.credits >= amount:
                spirit_stones = amount * EXCHANGE_RATE
                button_text = f"兑换 {amount:,} 积分 → {spirit_stones:,} 灵石"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"shop_exchange_confirm_{amount}")])
                text += f"• {amount:,} 积分 → {spirit_stones:,} 灵石\n"
            else:
                text += f"• {amount:,} 积分 → {amount * EXCHANGE_RATE:,} 灵石 [积分不足]\n"

        text += f"""
━━━━━━━━━━━━━━━
⚠️ 提示：
• 兑换后积分无法返还
• 即时到账，无手续费
• 可随时兑换
━━━━━━━━━━━━━━━
"""

        keyboard.append([InlineKeyboardButton("« 返回主菜单", callback_data="shop_back")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup)


async def confirm_exchange_spirit_stones(query, user_id: int, credit_amount: int):
    """确认兑换灵石"""
    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user_id)
        if not player:
            await query.answer("❌ 玩家不存在", show_alert=True)
            return

        # 执行兑换
        success, message = await CreditService.exchange_credits_to_spirit_stones(
            db, player, credit_amount
        )

        if not success:
            await query.answer(f"❌ {message}", show_alert=True)
            return

        await query.answer("✅ 兑换成功！", show_alert=False)

        # 显示兑换结果
        keyboard = [
            [InlineKeyboardButton("💎 继续兑换", callback_data="shop_exchange_spirit_stones")],
            [InlineKeyboardButton("« 返回主菜单", callback_data="shop_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(message, reply_markup=reply_markup)


# 注册处理器
def register_handlers(application):
    """注册积分商城处理器"""
    application.add_handler(CommandHandler(["积分商城", "商城"], credit_shop_command))
    application.add_handler(CommandHandler("我的积分", my_credits_command))
    application.add_handler(CommandHandler("兑换灵石", exchange_credits_command))
    application.add_handler(CallbackQueryHandler(shop_category_callback, pattern="^shop_"))
