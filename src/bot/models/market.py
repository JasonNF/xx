"""市场交易相关数据模型"""
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Shop(Base):
    """商店表"""
    __tablename__ = "shops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False, index=True)

    # 价格
    price: Mapped[int] = mapped_column(Integer, nullable=False)

    # 库存
    stock: Mapped[int] = mapped_column(Integer, default=-1, nullable=False)  # -1表示无限
    sold_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 限购
    daily_limit: Mapped[int] = mapped_column(Integer, default=-1, nullable=False)  # -1表示不限购

    # 购买条件
    required_realm: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    required_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )


class PlayerPurchase(Base):
    """玩家购买记录"""
    __tablename__ = "player_purchases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    shop_id: Mapped[int] = mapped_column(Integer, ForeignKey("shops.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)

    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    total_price: Mapped[int] = mapped_column(Integer, nullable=False)

    purchased_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, index=True)


class Market(Base):
    """玩家交易市场"""
    __tablename__ = "markets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    seller_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    inventory_id: Mapped[int] = mapped_column(Integer, ForeignKey("player_inventory.id"), nullable=False)

    # 交易信息
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    price_per_unit: Mapped[int] = mapped_column(Integer, nullable=False)
    total_price: Mapped[int] = mapped_column(Integer, nullable=False)

    # 状态
    is_sold: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    buyer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("players.id"), nullable=True)

    # 时间
    listed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    sold_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)  # 上架过期时间


class TradeRecord(Base):
    """交易记录"""
    __tablename__ = "trade_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    market_id: Mapped[int] = mapped_column(Integer, ForeignKey("markets.id"), nullable=False)
    seller_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    buyer_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    total_price: Mapped[int] = mapped_column(Integer, nullable=False)
    tax: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 交易税

    traded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class Auction(Base):
    """拍卖行"""
    __tablename__ = "auctions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    seller_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    inventory_id: Mapped[int] = mapped_column(Integer, ForeignKey("player_inventory.id"), nullable=False)

    # 拍卖信息
    starting_price: Mapped[int] = mapped_column(Integer, nullable=False)  # 起拍价
    current_bid: Mapped[int] = mapped_column(Integer, nullable=False)  # 当前出价
    buyout_price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 一口价

    # 当前最高出价者
    highest_bidder_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("players.id"), nullable=True)

    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_sold: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 时间
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    sold_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class AuctionBid(Base):
    """拍卖出价记录"""
    __tablename__ = "auction_bids"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    auction_id: Mapped[int] = mapped_column(Integer, ForeignKey("auctions.id"), nullable=False, index=True)
    bidder_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)

    bid_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    is_auto_bid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 是否自动出价

    bid_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
