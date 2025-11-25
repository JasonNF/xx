"""物品、装备、丹药相关数据模型"""
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class ItemType(enum.Enum):
    """物品类型"""
    WEAPON = "weapon"  # 武器
    ARMOR = "armor"  # 护甲
    ACCESSORY = "accessory"  # 饰品
    PILL = "pill"  # 丹药
    MATERIAL = "material"  # 材料
    CONSUMABLE = "consumable"  # 消耗品
    MISC = "misc"  # 杂物


class ItemGrade(enum.Enum):
    """物品品质"""
    COMMON = "普通"
    UNCOMMON = "精良"
    RARE = "稀有"
    EPIC = "史诗"
    LEGENDARY = "传说"
    MYTHIC = "神话"


class Item(Base):
    """物品/装备/丹药基础表"""
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    item_type: Mapped[ItemType] = mapped_column(Enum(ItemType), nullable=False)
    grade: Mapped[ItemGrade] = mapped_column(Enum(ItemGrade), default=ItemGrade.COMMON, nullable=False)

    # 基础属性
    is_tradable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # 可交易
    is_stackable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 可堆叠
    max_stack: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 最大堆叠数

    # 价格
    buy_price: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 购买价格
    sell_price: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 出售价格

    # 使用条件
    required_realm: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    required_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # 装备属性加成（仅装备类）
    attack_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    defense_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hp_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    spiritual_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    speed_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    crit_rate_bonus: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # 丹药效果（仅丹药类）
    hp_restore: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    spiritual_restore: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    exp_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 修为增加

    # 特殊效果描述
    special_effect: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class PlayerInventory(Base):
    """玩家背包"""
    __tablename__ = "player_inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_equipped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 装备强化（仅装备）
    enhancement_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    obtained_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 关系
    player: Mapped["Player"] = relationship("Player", back_populates="inventory")
    item: Mapped["Item"] = relationship("Item")


class PillFormula(Base):
    """丹药配方表"""
    __tablename__ = "pill_formulas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pill_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # 炼制条件
    required_alchemy_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    success_rate: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)

    # 材料需求
    materials_required: Mapped[str] = mapped_column(Text, nullable=False)  # JSON格式存储

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 关系
    pill: Mapped["Item"] = relationship("Item")


class EnhancementRecord(Base):
    """装备强化记录"""
    __tablename__ = "enhancement_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    inventory_id: Mapped[int] = mapped_column(Integer, ForeignKey("player_inventory.id"), nullable=False)

    old_level: Mapped[int] = mapped_column(Integer, nullable=False)
    new_level: Mapped[int] = mapped_column(Integer, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    cost: Mapped[int] = mapped_column(Integer, nullable=False)  # 消耗灵石

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
