"""市场交易服务"""
from datetime import datetime, timedelta
from typing import Tuple, Dict, List, Optional

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Player, Item, PlayerInventory
from bot.models.market import Market, TradeRecord, Auction, AuctionBid


class MarketService:
    """市场交易服务类"""

    MARKET_TAX_RATE = 0.05  # 交易税率 5%
    MARKET_LISTING_DURATION = 7  # 上架天数
    MIN_BID_INCREMENT = 100  # 最小加价幅度

    @staticmethod
    async def list_item_on_market(
        db: AsyncSession,
        player: Player,
        inventory_id: int,
        quantity: int,
        price_per_unit: int
    ) -> Tuple[bool, str]:
        """上架物品到市场

        Args:
            db: 数据库会话
            player: 卖家
            inventory_id: 背包物品ID
            quantity: 数量
            price_per_unit: 单价

        Returns:
            (是否成功, 消息)
        """
        # 获取物品
        result = await db.execute(
            select(PlayerInventory).where(
                PlayerInventory.id == inventory_id,
                PlayerInventory.player_id == player.id
            )
        )
        inv = result.scalar_one_or_none()

        if not inv:
            return False, "未找到该物品"

        if inv.is_equipped:
            return False, "请先卸下装备再上架"

        if inv.quantity < quantity:
            return False, f"物品数量不足，当前拥有 {inv.quantity} 个"

        if price_per_unit < 1:
            return False, "价格必须大于0"

        # 检查是否已经上架
        result = await db.execute(
            select(Market).where(
                Market.inventory_id == inventory_id,
                Market.is_sold == False,
                Market.expires_at > datetime.now()
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return False, "该物品已在市场上架中"

        # 创建市场订单
        total_price = quantity * price_per_unit
        market_listing = Market(
            seller_id=player.id,
            item_id=inv.item_id,
            inventory_id=inventory_id,
            quantity=quantity,
            price_per_unit=price_per_unit,
            total_price=total_price,
            expires_at=datetime.now() + timedelta(days=MarketService.MARKET_LISTING_DURATION)
        )
        db.add(market_listing)

        # 从背包扣除数量
        inv.quantity -= quantity
        if inv.quantity == 0:
            await db.delete(inv)

        await db.commit()

        return True, f"成功上架物品，上架期限 {MarketService.MARKET_LISTING_DURATION} 天"

    @staticmethod
    async def buy_from_market(
        db: AsyncSession,
        buyer: Player,
        market_id: int
    ) -> Tuple[bool, str]:
        """从市场购买物品

        Args:
            db: 数据库会话
            buyer: 买家
            market_id: 市场订单ID

        Returns:
            (是否成功, 消息)
        """
        # 获取市场订单
        result = await db.execute(
            select(Market).where(Market.id == market_id)
        )
        listing = result.scalar_one_or_none()

        if not listing:
            return False, "未找到该订单"

        if listing.is_sold:
            return False, "该物品已售出"

        if listing.expires_at < datetime.now():
            return False, "该订单已过期"

        if listing.seller_id == buyer.id:
            return False, "不能购买自己的物品"

        # 检查买家金钱
        if buyer.spirit_stones < listing.total_price:
            return False, f"灵石不足，需要 {listing.total_price} 灵石"

        # 获取卖家
        result = await db.execute(
            select(Player).where(Player.id == listing.seller_id)
        )
        seller = result.scalar_one_or_none()

        if not seller:
            return False, "卖家不存在"

        # 计算税费
        tax = int(listing.total_price * MarketService.MARKET_TAX_RATE)
        seller_income = listing.total_price - tax

        # 转账
        buyer.spirit_stones -= listing.total_price
        seller.spirit_stones += seller_income

        # 添加物品到买家背包
        result = await db.execute(
            select(PlayerInventory).where(
                PlayerInventory.player_id == buyer.id,
                PlayerInventory.item_id == listing.item_id,
                PlayerInventory.is_equipped == False
            )
        )
        buyer_inv = result.scalar_one_or_none()

        if buyer_inv:
            buyer_inv.quantity += listing.quantity
        else:
            new_inv = PlayerInventory(
                player_id=buyer.id,
                item_id=listing.item_id,
                quantity=listing.quantity
            )
            db.add(new_inv)

        # 更新订单状态
        listing.is_sold = True
        listing.buyer_id = buyer.id
        listing.sold_at = datetime.now()

        # 记录交易
        trade_record = TradeRecord(
            market_id=market_id,
            seller_id=listing.seller_id,
            buyer_id=buyer.id,
            item_id=listing.item_id,
            quantity=listing.quantity,
            total_price=listing.total_price,
            tax=tax
        )
        db.add(trade_record)

        await db.commit()

        return True, f"购买成功！卖家收入 {seller_income} 灵石（税费 {tax}）"

    @staticmethod
    async def cancel_market_listing(
        db: AsyncSession,
        player: Player,
        market_id: int
    ) -> Tuple[bool, str]:
        """取消市场上架

        Args:
            db: 数据库会话
            player: 玩家
            market_id: 市场订单ID

        Returns:
            (是否成功, 消息)
        """
        # 获取订单
        result = await db.execute(
            select(Market).where(
                Market.id == market_id,
                Market.seller_id == player.id
            )
        )
        listing = result.scalar_one_or_none()

        if not listing:
            return False, "未找到该订单或无权操作"

        if listing.is_sold:
            return False, "该物品已售出，无法取消"

        # 返还物品到背包
        result = await db.execute(
            select(PlayerInventory).where(
                PlayerInventory.player_id == player.id,
                PlayerInventory.item_id == listing.item_id,
                PlayerInventory.is_equipped == False
            )
        )
        inv = result.scalar_one_or_none()

        if inv:
            inv.quantity += listing.quantity
        else:
            new_inv = PlayerInventory(
                player_id=player.id,
                item_id=listing.item_id,
                quantity=listing.quantity
            )
            db.add(new_inv)

        # 删除订单
        await db.delete(listing)
        await db.commit()

        return True, "成功取消上架，物品已返还"

    @staticmethod
    async def search_market(
        db: AsyncSession,
        item_name: Optional[str] = None,
        max_price: Optional[int] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Dict], int]:
        """搜索市场物品

        Args:
            db: 数据库会话
            item_name: 物品名称（可选）
            max_price: 最高价格（可选）
            page: 页码
            page_size: 每页数量

        Returns:
            (物品列表, 总数)
        """
        # 构建查询
        query = select(Market).where(
            Market.is_sold == False,
            Market.expires_at > datetime.now()
        )

        if item_name:
            # 需要join Item表
            query = query.join(Item).where(Item.name.contains(item_name))

        if max_price:
            query = query.where(Market.total_price <= max_price)

        # 按时间排序
        query = query.order_by(Market.listed_at.desc())

        # 总数
        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar()

        # 分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await db.execute(query)
        listings = result.scalars().all()

        # 转换为字典
        items = []
        for listing in listings:
            # 获取物品信息
            item_result = await db.execute(
                select(Item).where(Item.id == listing.item_id)
            )
            item = item_result.scalar_one_or_none()

            # 获取卖家信息
            seller_result = await db.execute(
                select(Player).where(Player.id == listing.seller_id)
            )
            seller = seller_result.scalar_one_or_none()

            items.append({
                "id": listing.id,
                "item_name": item.name if item else "未知",
                "quantity": listing.quantity,
                "price_per_unit": listing.price_per_unit,
                "total_price": listing.total_price,
                "seller_name": seller.username if seller else "未知",
                "listed_at": listing.listed_at,
                "expires_at": listing.expires_at
            })

        return items, total


class AuctionService:
    """拍卖服务类"""

    AUCTION_DURATION = 3  # 拍卖天数
    AUCTION_TAX_RATE = 0.05  # 拍卖税率 5%
    MIN_BID_INCREMENT = 100  # 最小加价幅度

    @staticmethod
    async def create_auction(
        db: AsyncSession,
        player: Player,
        inventory_id: int,
        starting_price: int,
        buyout_price: Optional[int] = None,
        duration_days: int = 3
    ) -> Tuple[bool, str]:
        """创建拍卖

        Args:
            db: 数据库会话
            player: 卖家
            inventory_id: 背包物品ID
            starting_price: 起拍价
            buyout_price: 一口价（可选）
            duration_days: 拍卖天数

        Returns:
            (是否成功, 消息)
        """
        # 获取物品
        result = await db.execute(
            select(PlayerInventory).where(
                PlayerInventory.id == inventory_id,
                PlayerInventory.player_id == player.id
            )
        )
        inv = result.scalar_one_or_none()

        if not inv:
            return False, "未找到该物品"

        if inv.is_equipped:
            return False, "请先卸下装备再拍卖"

        if inv.quantity != 1:
            return False, "拍卖仅支持单件物品"

        if starting_price < 1:
            return False, "起拍价必须大于0"

        if buyout_price and buyout_price <= starting_price:
            return False, "一口价必须高于起拍价"

        # 检查是否已在拍卖
        result = await db.execute(
            select(Auction).where(
                Auction.inventory_id == inventory_id,
                Auction.is_active == True,
                Auction.ends_at > datetime.now()
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return False, "该物品已在拍卖中"

        # 创建拍卖
        auction = Auction(
            seller_id=player.id,
            item_id=inv.item_id,
            inventory_id=inventory_id,
            starting_price=starting_price,
            current_bid=starting_price,
            buyout_price=buyout_price,
            ends_at=datetime.now() + timedelta(days=duration_days)
        )
        db.add(auction)

        # 从背包移除
        await db.delete(inv)

        await db.commit()
        await db.refresh(auction)

        return True, f"成功创建拍卖，拍卖期限 {duration_days} 天，拍卖ID: {auction.id}"

    @staticmethod
    async def place_bid(
        db: AsyncSession,
        player: Player,
        auction_id: int,
        bid_amount: int
    ) -> Tuple[bool, str]:
        """出价

        Args:
            db: 数据库会话
            player: 出价者
            auction_id: 拍卖ID
            bid_amount: 出价金额

        Returns:
            (是否成功, 消息)
        """
        # 获取拍卖
        result = await db.execute(
            select(Auction).where(Auction.id == auction_id)
        )
        auction = result.scalar_one_or_none()

        if not auction:
            return False, "未找到该拍卖"

        if not auction.is_active:
            return False, "该拍卖已结束"

        if auction.ends_at < datetime.now():
            return False, "该拍卖已过期"

        if auction.seller_id == player.id:
            return False, "不能对自己的拍卖出价"

        if bid_amount < auction.current_bid + AuctionService.MIN_BID_INCREMENT:
            return False, f"出价必须高于当前价 {auction.current_bid + AuctionService.MIN_BID_INCREMENT} 灵石"

        if player.spirit_stones < bid_amount:
            return False, f"灵石不足，需要 {bid_amount} 灵石"

        # 返还前一个出价者的押金
        if auction.highest_bidder_id:
            result = await db.execute(
                select(Player).where(Player.id == auction.highest_bidder_id)
            )
            previous_bidder = result.scalar_one_or_none()
            if previous_bidder:
                previous_bidder.spirit_stones += auction.current_bid

        # 扣除新出价者的灵石
        player.spirit_stones -= bid_amount

        # 更新拍卖
        auction.current_bid = bid_amount
        auction.highest_bidder_id = player.id

        # 记录出价
        bid_record = AuctionBid(
            auction_id=auction_id,
            bidder_id=player.id,
            bid_amount=bid_amount
        )
        db.add(bid_record)

        await db.commit()

        return True, f"出价成功！当前最高价: {bid_amount} 灵石"

    @staticmethod
    async def buyout_auction(
        db: AsyncSession,
        player: Player,
        auction_id: int
    ) -> Tuple[bool, str]:
        """一口价购买

        Args:
            db: 数据库会话
            player: 购买者
            auction_id: 拍卖ID

        Returns:
            (是否成功, 消息)
        """
        # 获取拍卖
        result = await db.execute(
            select(Auction).where(Auction.id == auction_id)
        )
        auction = result.scalar_one_or_none()

        if not auction:
            return False, "未找到该拍卖"

        if not auction.is_active:
            return False, "该拍卖已结束"

        if not auction.buyout_price:
            return False, "该拍卖没有设置一口价"

        if auction.seller_id == player.id:
            return False, "不能购买自己的拍卖"

        if player.spirit_stones < auction.buyout_price:
            return False, f"灵石不足，需要 {auction.buyout_price} 灵石"

        # 获取卖家
        result = await db.execute(
            select(Player).where(Player.id == auction.seller_id)
        )
        seller = result.scalar_one_or_none()

        if not seller:
            return False, "卖家不存在"

        # 返还前一个出价者的押金
        if auction.highest_bidder_id:
            result = await db.execute(
                select(Player).where(Player.id == auction.highest_bidder_id)
            )
            previous_bidder = result.scalar_one_or_none()
            if previous_bidder:
                previous_bidder.spirit_stones += auction.current_bid

        # 计算税费
        tax = int(auction.buyout_price * AuctionService.AUCTION_TAX_RATE)
        seller_income = auction.buyout_price - tax

        # 转账
        player.spirit_stones -= auction.buyout_price
        seller.spirit_stones += seller_income

        # 添加物品到买家背包
        new_inv = PlayerInventory(
            player_id=player.id,
            item_id=auction.item_id,
            quantity=1
        )
        db.add(new_inv)

        # 更新拍卖状态
        auction.is_active = False
        auction.is_sold = True
        auction.highest_bidder_id = player.id
        auction.current_bid = auction.buyout_price
        auction.sold_at = datetime.now()

        await db.commit()

        return True, f"一口价购买成功！卖家收入 {seller_income} 灵石（税费 {tax}）"

    @staticmethod
    async def cancel_auction(
        db: AsyncSession,
        player: Player,
        auction_id: int
    ) -> Tuple[bool, str]:
        """取消拍卖

        Args:
            db: 数据库会话
            player: 玩家
            auction_id: 拍卖ID

        Returns:
            (是否成功, 消息)
        """
        # 获取拍卖
        result = await db.execute(
            select(Auction).where(
                Auction.id == auction_id,
                Auction.seller_id == player.id
            )
        )
        auction = result.scalar_one_or_none()

        if not auction:
            return False, "未找到该拍卖或无权操作"

        if not auction.is_active:
            return False, "该拍卖已结束"

        if auction.highest_bidder_id:
            return False, "已有人出价，无法取消"

        # 返还物品到背包
        new_inv = PlayerInventory(
            player_id=player.id,
            item_id=auction.item_id,
            quantity=1
        )
        db.add(new_inv)

        # 更新拍卖状态
        auction.is_active = False
        await db.commit()

        return True, "成功取消拍卖，物品已返还"

    @staticmethod
    async def finalize_auction(
        db: AsyncSession,
        auction_id: int
    ) -> Tuple[bool, str]:
        """结算拍卖（定时任务调用）

        Args:
            db: 数据库会话
            auction_id: 拍卖ID

        Returns:
            (是否成功, 消息)
        """
        # 获取拍卖
        result = await db.execute(
            select(Auction).where(Auction.id == auction_id)
        )
        auction = result.scalar_one_or_none()

        if not auction:
            return False, "未找到该拍卖"

        if not auction.is_active:
            return False, "该拍卖已结束"

        if auction.ends_at > datetime.now():
            return False, "拍卖尚未结束"

        # 如果有人出价
        if auction.highest_bidder_id:
            # 获取卖家
            result = await db.execute(
                select(Player).where(Player.id == auction.seller_id)
            )
            seller = result.scalar_one_or_none()

            # 计算税费
            tax = int(auction.current_bid * AuctionService.AUCTION_TAX_RATE)
            seller_income = auction.current_bid - tax

            # 转账给卖家
            if seller:
                seller.spirit_stones += seller_income

            # 添加物品到买家背包
            new_inv = PlayerInventory(
                player_id=auction.highest_bidder_id,
                item_id=auction.item_id,
                quantity=1
            )
            db.add(new_inv)

            # 更新拍卖状态
            auction.is_active = False
            auction.is_sold = True
            auction.sold_at = datetime.now()

            await db.commit()

            return True, f"拍卖结算成功，成交价 {auction.current_bid} 灵石"

        else:
            # 无人出价，返还物品给卖家
            new_inv = PlayerInventory(
                player_id=auction.seller_id,
                item_id=auction.item_id,
                quantity=1
            )
            db.add(new_inv)

            # 更新拍卖状态
            auction.is_active = False
            await db.commit()

            return True, "拍卖流拍，物品已返还"
