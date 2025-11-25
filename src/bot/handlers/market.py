"""市场交易和拍卖系统handlers"""
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.models.database import AsyncSessionLocal
from bot.models import Player, Item, PlayerInventory
from bot.services.market_service import MarketService, AuctionService
from sqlalchemy import select


async def market_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看市场 - /市场 [物品名] [最高价]"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 解析参数
        item_name = None
        max_price = None

        if context.args:
            # 第一个参数可能是物品名
            item_name = context.args[0]
            # 第二个参数可能是最高价
            if len(context.args) > 1:
                try:
                    max_price = int(context.args[1])
                except ValueError:
                    pass

        # 搜索市场
        from sqlalchemy import func
        items, total = await MarketService.search_market(
            session, item_name, max_price, page=1, page_size=10
        )

        if not items:
            msg = "🏪 【市场】\n\n"
            msg += "📦 暂无商品在售\n\n"
            msg += "💡 使用 /上架 <背包ID> <数量> <单价> 上架物品"
            await update.message.reply_text(msg)
            return

        msg = "🏪 【市场】\n\n"
        if item_name:
            msg += f"🔍 搜索: {item_name}\n"
        if max_price:
            msg += f"💰 最高价: {max_price}\n"
        msg += f"📊 共找到 {total} 件商品\n"
        msg += "━━━━━━━━━━━━━━\n\n"

        for item in items:
            msg += f"🆔 订单ID: {item['id']}\n"
            msg += f"📦 {item['item_name']} x{item['quantity']}\n"
            msg += f"💰 单价: {item['price_per_unit']} | 总价: {item['total_price']}\n"
            msg += f"👤 卖家: {item['seller_name']}\n"
            msg += f"⏰ 到期: {item['expires_at'].strftime('%m-%d %H:%M')}\n\n"

        msg += "━━━━━━━━━━━━━━\n"
        msg += "💡 使用 /购买 <订单ID> 购买物品\n"
        msg += "💡 使用 /我的上架 查看自己的上架物品"

        await update.message.reply_text(msg)


async def list_item_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """上架物品 - /上架 <背包ID> <数量> <单价>"""
    user = update.effective_user

    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "❌ 参数错误\n"
            "用法: /上架 <背包ID> <数量> <单价>\n"
            "例如: /上架 123 5 1000"
        )
        return

    try:
        inventory_id = int(context.args[0])
        quantity = int(context.args[1])
        price_per_unit = int(context.args[2])
    except ValueError:
        await update.message.reply_text("❌ 参数必须是数字")
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        success, message = await MarketService.list_item_on_market(
            session, player, inventory_id, quantity, price_per_unit
        )

        if success:
            total_price = quantity * price_per_unit
            msg = f"✅ {message}\n\n"
            msg += f"📦 数量: {quantity}\n"
            msg += f"💰 单价: {price_per_unit} | 总价: {total_price}\n"
            msg += f"💡 提示: 成交后将收取 5% 的交易税"
        else:
            msg = f"❌ {message}"

        await update.message.reply_text(msg)


async def buy_from_market_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """购买物品 - /购买 <订单ID>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定订单ID\n"
            "用法: /购买 <订单ID>\n"
            "例如: /购买 123"
        )
        return

    try:
        market_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ 订单ID必须是数字")
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        success, message = await MarketService.buy_from_market(session, player, market_id)

        if success:
            msg = f"🎉 {message}"
        else:
            msg = f"❌ {message}"

        await update.message.reply_text(msg)


async def my_listings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看我的上架 - /我的上架"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        from bot.models.market import Market
        from datetime import datetime

        result = await session.execute(
            select(Market).where(
                Market.seller_id == player.id,
                Market.is_sold == False,
                Market.expires_at > datetime.now()
            ).order_by(Market.listed_at.desc())
        )
        listings = result.scalars().all()

        if not listings:
            await update.message.reply_text(
                "📦 您暂无上架的物品\n\n"
                "💡 使用 /上架 <背包ID> <数量> <单价> 上架物品"
            )
            return

        msg = "📦 【我的上架】\n\n"

        for listing in listings:
            result = await session.execute(
                select(Item).where(Item.id == listing.item_id)
            )
            item = result.scalar_one_or_none()
            item_name = item.name if item else "未知"

            msg += f"🆔 订单ID: {listing.id}\n"
            msg += f"📦 {item_name} x{listing.quantity}\n"
            msg += f"💰 单价: {listing.price_per_unit} | 总价: {listing.total_price}\n"
            msg += f"⏰ 到期: {listing.expires_at.strftime('%m-%d %H:%M')}\n\n"

        msg += "━━━━━━━━━━━━━━\n"
        msg += "💡 使用 /取消上架 <订单ID> 取消上架"

        await update.message.reply_text(msg)


async def cancel_listing_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """取消上架 - /取消上架 <订单ID>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定订单ID\n"
            "用法: /取消上架 <订单ID>\n"
            "例如: /取消上架 123"
        )
        return

    try:
        market_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ 订单ID必须是数字")
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        success, message = await MarketService.cancel_market_listing(session, player, market_id)

        if success:
            msg = f"✅ {message}"
        else:
            msg = f"❌ {message}"

        await update.message.reply_text(msg)


# ===== 拍卖系统 =====

async def auction_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看拍卖行 - /拍卖"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        from bot.models.market import Auction
        from datetime import datetime

        result = await session.execute(
            select(Auction).where(
                Auction.is_active == True,
                Auction.ends_at > datetime.now()
            ).order_by(Auction.ends_at.asc())
        )
        auctions = result.scalars().all()

        if not auctions:
            msg = "🔨 【拍卖行】\n\n"
            msg += "📦 暂无拍卖中的物品\n\n"
            msg += "💡 使用 /创建拍卖 <背包ID> <起拍价> [一口价] 创建拍卖"
            await update.message.reply_text(msg)
            return

        msg = "🔨 【拍卖行】\n\n"

        for auction in auctions:
            result = await session.execute(
                select(Item).where(Item.id == auction.item_id)
            )
            item = result.scalar_one_or_none()
            item_name = item.name if item else "未知"

            result = await session.execute(
                select(Player).where(Player.id == auction.seller_id)
            )
            seller = result.scalar_one_or_none()
            seller_name = seller.username if seller else "未知"

            msg += f"🆔 拍卖ID: {auction.id}\n"
            msg += f"📦 {item_name}\n"
            msg += f"💰 当前价: {auction.current_bid}\n"

            if auction.buyout_price:
                msg += f"💎 一口价: {auction.buyout_price}\n"

            if auction.highest_bidder_id:
                result = await session.execute(
                    select(Player).where(Player.id == auction.highest_bidder_id)
                )
                bidder = result.scalar_one_or_none()
                bidder_name = bidder.username if bidder else "未知"
                msg += f"👤 最高出价者: {bidder_name}\n"
            else:
                msg += f"👤 暂无出价\n"

            msg += f"👤 拍卖者: {seller_name}\n"
            msg += f"⏰ 结束: {auction.ends_at.strftime('%m-%d %H:%M')}\n\n"

        msg += "━━━━━━━━━━━━━━\n"
        msg += "💡 使用 /出价 <拍卖ID> <金额> 参与竞拍\n"
        msg += "💡 使用 /一口价 <拍卖ID> 直接购买"

        await update.message.reply_text(msg)


async def create_auction_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """创建拍卖 - /创建拍卖 <背包ID> <起拍价> [一口价]"""
    user = update.effective_user

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "❌ 参数错误\n"
            "用法: /创建拍卖 <背包ID> <起拍价> [一口价]\n"
            "例如: /创建拍卖 123 1000 5000"
        )
        return

    try:
        inventory_id = int(context.args[0])
        starting_price = int(context.args[1])
        buyout_price = int(context.args[2]) if len(context.args) > 2 else None
    except ValueError:
        await update.message.reply_text("❌ 参数必须是数字")
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        success, message = await AuctionService.create_auction(
            session, player, inventory_id, starting_price, buyout_price
        )

        if success:
            msg = f"🔨 {message}\n\n"
            msg += f"💰 起拍价: {starting_price}\n"
            if buyout_price:
                msg += f"💎 一口价: {buyout_price}\n"
            msg += f"💡 提示: 成交后将收取 5% 的拍卖税"
        else:
            msg = f"❌ {message}"

        await update.message.reply_text(msg)


async def place_bid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """出价 - /出价 <拍卖ID> <金额>"""
    user = update.effective_user

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "❌ 参数错误\n"
            "用法: /出价 <拍卖ID> <金额>\n"
            "例如: /出价 123 2000"
        )
        return

    try:
        auction_id = int(context.args[0])
        bid_amount = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ 参数必须是数字")
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        success, message = await AuctionService.place_bid(session, player, auction_id, bid_amount)

        if success:
            msg = f"🎉 {message}"
        else:
            msg = f"❌ {message}"

        await update.message.reply_text(msg)


async def buyout_auction_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """一口价购买 - /一口价 <拍卖ID>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定拍卖ID\n"
            "用法: /一口价 <拍卖ID>\n"
            "例如: /一口价 123"
        )
        return

    try:
        auction_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ 拍卖ID必须是数字")
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        success, message = await AuctionService.buyout_auction(session, player, auction_id)

        if success:
            msg = f"🎉 {message}"
        else:
            msg = f"❌ {message}"

        await update.message.reply_text(msg)


async def my_auctions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看我的拍卖 - /我的拍卖"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        from bot.models.market import Auction
        from datetime import datetime

        result = await session.execute(
            select(Auction).where(
                Auction.seller_id == player.id,
                Auction.is_active == True,
                Auction.ends_at > datetime.now()
            ).order_by(Auction.started_at.desc())
        )
        auctions = result.scalars().all()

        if not auctions:
            await update.message.reply_text(
                "🔨 您暂无拍卖中的物品\n\n"
                "💡 使用 /创建拍卖 <背包ID> <起拍价> [一口价] 创建拍卖"
            )
            return

        msg = "🔨 【我的拍卖】\n\n"

        for auction in auctions:
            result = await session.execute(
                select(Item).where(Item.id == auction.item_id)
            )
            item = result.scalar_one_or_none()
            item_name = item.name if item else "未知"

            msg += f"🆔 拍卖ID: {auction.id}\n"
            msg += f"📦 {item_name}\n"
            msg += f"💰 当前价: {auction.current_bid}\n"

            if auction.buyout_price:
                msg += f"💎 一口价: {auction.buyout_price}\n"

            if auction.highest_bidder_id:
                result = await session.execute(
                    select(Player).where(Player.id == auction.highest_bidder_id)
                )
                bidder = result.scalar_one_or_none()
                bidder_name = bidder.username if bidder else "未知"
                msg += f"👤 最高出价者: {bidder_name}\n"
            else:
                msg += f"👤 暂无出价\n"

            msg += f"⏰ 结束: {auction.ends_at.strftime('%m-%d %H:%M')}\n\n"

        msg += "━━━━━━━━━━━━━━\n"
        msg += "💡 使用 /取消拍卖 <拍卖ID> 取消拍卖（需无人出价）"

        await update.message.reply_text(msg)


async def cancel_auction_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """取消拍卖 - /取消拍卖 <拍卖ID>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定拍卖ID\n"
            "用法: /取消拍卖 <拍卖ID>\n"
            "例如: /取消拍卖 123"
        )
        return

    try:
        auction_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ 拍卖ID必须是数字")
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        success, message = await AuctionService.cancel_auction(session, player, auction_id)

        if success:
            msg = f"✅ {message}"
        else:
            msg = f"❌ {message}"

        await update.message.reply_text(msg)


def register_handlers(application):
    """注册市场交易相关处理器"""
    # 市场交易
    application.add_handler(CommandHandler("市场", market_list_command))
    application.add_handler(CommandHandler("上架", list_item_command))
    application.add_handler(CommandHandler("购买", buy_from_market_command))
    application.add_handler(CommandHandler("我的上架", my_listings_command))
    application.add_handler(CommandHandler("取消上架", cancel_listing_command))

    # 拍卖行
    application.add_handler(CommandHandler("拍卖", auction_list_command))
    application.add_handler(CommandHandler("创建拍卖", create_auction_command))
    application.add_handler(CommandHandler("出价", place_bid_command))
    application.add_handler(CommandHandler("一口价", buyout_auction_command))
    application.add_handler(CommandHandler("我的拍卖", my_auctions_command))
    application.add_handler(CommandHandler("取消拍卖", cancel_auction_command))
