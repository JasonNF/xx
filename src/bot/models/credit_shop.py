"""积分商城数据模型"""
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Integer, String, Text, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class CreditType(enum.Enum):
    """积分类型"""
    SIGN_IN = "签到积分"           # 每日签到
    TASK_COMPLETION = "任务完成"   # 完成任务
    PVP_WIN = "竞技场胜利"         # PVP胜利
    WORLD_BOSS = "世界BOSS"        # 击杀世界BOSS
    SECT_CONTRIBUTION = "宗门贡献" # 宗门活动
    BREAKTHROUGH = "境界突破"      # 突破境界
    ACHIEVEMENT = "成就奖励"       # 完成成就
    ACTIVITY_REWARD = "活动奖励"   # 参与活动
    ADMIN_GRANT = "管理员赠送"     # 管理员手动发放
    EXCHANGE_DEDUCT = "商城兑换"   # 商城兑换扣除
    EXCHANGE_SPIRIT_STONES = "兑换灵石"  # 积分兑换灵石


class CreditShopCategory(enum.Enum):
    """商城分类"""
    CULTIVATION_METHOD = "功法"
    TREASURE = "法宝"
    PILL = "丹药"
    SPECIAL = "特殊物品"


class CreditShopItem(Base):
    """积分商城商品表"""
    __tablename__ = "credit_shop_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[CreditShopCategory] = mapped_column(Enum(CreditShopCategory), nullable=False, index=True)

    # 关联物品ID（如果是已存在的物品）
    item_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("items.id"), nullable=True)

    # 价格（积分）
    credit_price: Mapped[int] = mapped_column(Integer, nullable=False)

    # 库存控制
    total_stock: Mapped[int] = mapped_column(Integer, default=-1, nullable=False)  # -1=无限
    remaining_stock: Mapped[int] = mapped_column(Integer, default=-1, nullable=False)  # -1=无限
    sold_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 限购
    purchase_limit_per_player: Mapped[int] = mapped_column(Integer, default=-1, nullable=False)  # -1=不限购
    daily_purchase_limit: Mapped[int] = mapped_column(Integer, default=-1, nullable=False)  # 每日限购

    # 购买条件
    required_realm: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    required_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    required_vip_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # VIP等级要求

    # 折扣
    discount_rate: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)  # 折扣率 0.8=8折

    # 特殊效果（JSON格式存储）
    special_effects: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 商品图标/标签
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # emoji或图标
    tags: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # 标签：热门,限时,稀有

    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 是否精选
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 排序

    # 时间限制
    available_from: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # 上架时间
    available_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # 下架时间

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )


class PlayerCreditRecord(Base):
    """玩家积分记录"""
    __tablename__ = "player_credit_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)

    # 积分变动
    credit_change: Mapped[int] = mapped_column(Integer, nullable=False)  # 正数=获得，负数=消耗
    credit_before: Mapped[int] = mapped_column(Integer, nullable=False)  # 变动前积分
    credit_after: Mapped[int] = mapped_column(Integer, nullable=False)   # 变动后积分

    # 来源/原因
    credit_type: Mapped[CreditType] = mapped_column(Enum(CreditType), nullable=False, index=True)
    reason: Mapped[str] = mapped_column(String(200), nullable=False)
    reference_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 关联ID（如商品ID、任务ID等）

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, index=True)


class CreditShopPurchase(Base):
    """积分商城购买记录"""
    __tablename__ = "credit_shop_purchases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    shop_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("credit_shop_items.id"), nullable=False, index=True)

    # 购买信息
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    credit_cost: Mapped[int] = mapped_column(Integer, nullable=False)  # 实际花费积分
    original_price: Mapped[int] = mapped_column(Integer, nullable=False)  # 原价

    # 购买时玩家信息（快照）
    player_realm: Mapped[str] = mapped_column(String(50), nullable=False)
    player_level: Mapped[int] = mapped_column(Integer, nullable=False)

    purchased_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, index=True)


class PlayerCreditShopLimit(Base):
    """玩家商城限购记录"""
    __tablename__ = "player_credit_shop_limits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    shop_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("credit_shop_items.id"), nullable=False, index=True)

    # 购买统计
    total_purchased: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 总购买次数
    last_purchase_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # 最后购买时间
    daily_purchased: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 今日购买次数
    daily_reset_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # 每日重置日期

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )
