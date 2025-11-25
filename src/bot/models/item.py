"""物品、法宝、丹药相关数据模型 - 凡人修仙传版本"""
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class TreasureGrade(enum.Enum):
    """法宝等级"""
    TALISMAN = "符箓"  # 一次性
    MAGIC_TOOL_LOW = "下品法器"
    MAGIC_TOOL_MID = "中品法器"
    MAGIC_TOOL_HIGH = "上品法器"
    MAGIC_TREASURE = "法宝"
    ANCIENT_TREASURE = "古宝"
    HEAVEN_REACHING = "通天灵宝"


class ItemType(enum.Enum):
    """物品类型"""
    # 法宝装备
    WEAPON = "武器"
    ARMOR = "护甲"
    ACCESSORY = "饰品"

    # 丹药
    PILL = "丹药"

    # 材料
    HERB = "灵药"  # 炼丹材料
    ORE = "矿石"  # 炼器材料
    MATERIAL = "其他材料"

    # 其他
    CONSUMABLE = "消耗品"
    MISC = "杂物"


class EquipmentQuality(str, enum.Enum):
    """装备品质等级 - 与灵兽品质保持一致"""
    COMMON = "凡品"      # 基础倍率1.0x, 强化上限+10
    IMMORTAL = "仙品"    # 基础倍率1.5x, 强化上限+15
    DIVINE = "神品"      # 基础倍率2.0x, 强化上限+20


class EquipmentSlot(str, enum.Enum):
    """装备槽位类型"""
    WEAPON = "武器"
    OFF_HAND = "副手"
    HEAD = "头部"
    BODY = "身体"
    LEGS = "腿部"
    FEET = "脚部"
    ACCESSORY = "饰品"


class Item(Base):
    """物品/法宝/丹药基础表"""
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    item_type: Mapped[ItemType] = mapped_column(Enum(ItemType), nullable=False)

    # 法宝等级（仅法宝类）
    treasure_grade: Mapped[Optional[TreasureGrade]] = mapped_column(Enum(TreasureGrade), nullable=True)

    # 装备系统字段（向后兼容）
    quality: Mapped[Optional[EquipmentQuality]] = mapped_column(Enum(EquipmentQuality), nullable=True)
    set_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("equipment_sets.id"), nullable=True)
    equipment_slot: Mapped[Optional[EquipmentSlot]] = mapped_column(Enum(EquipmentSlot), nullable=True)

    # 基础属性
    is_tradable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_stackable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    max_stack: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # 价格（灵石）
    buy_price: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sell_price: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 使用条件
    required_realm: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    required_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # 法宝属性加成
    attack_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    defense_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hp_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    spiritual_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    speed_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 法宝特殊能力
    special_ability: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 丹药效果（仅丹药类）
    hp_restore: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    spiritual_restore: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    exp_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 突破丹药效果
    breakthrough_bonus: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 提升突破成功率

    # 灵药年份（仅灵药类）
    herb_age: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class PlayerInventory(Base):
    """玩家背包"""
    __tablename__ = "player_inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_equipped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 法宝炼化等级（0-12层）
    refining_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 是否本命法宝
    is_natal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 装备强化系统（向后兼容）
    enhancement_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    obtained_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 关系
    player: Mapped["Player"] = relationship("Player", back_populates="inventory")
    item: Mapped["Item"] = relationship("Item")


class EquipmentSet(Base):
    """套装定义表"""
    __tablename__ = "equipment_sets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    element: Mapped[str] = mapped_column(String(20), nullable=False)  # 青龙/朱雀/玄武/白虎
    set_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 攻击型/防御型/平衡型/爆发型
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class EquipmentSetBonus(Base):
    """套装效果表"""
    __tablename__ = "equipment_set_bonuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    set_id: Mapped[int] = mapped_column(Integer, ForeignKey("equipment_sets.id"), nullable=False)
    piece_count: Mapped[int] = mapped_column(Integer, nullable=False)  # 2/4/6件
    bonus_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # 类型: attack_percent, defense_percent, hp_percent, crit_rate, special_skill等
    bonus_value: Mapped[float] = mapped_column(Float, nullable=False)
    special_effect: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON格式特殊效果
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 关系
    equipment_set: Mapped["EquipmentSet"] = relationship("EquipmentSet")


class EnhancementRecord(Base):
    """强化记录表"""
    __tablename__ = "enhancement_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    inventory_id: Mapped[int] = mapped_column(Integer, ForeignKey("player_inventory.id"), nullable=False)
    from_level: Mapped[int] = mapped_column(Integer, nullable=False)
    to_level: Mapped[int] = mapped_column(Integer, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    cost: Mapped[int] = mapped_column(Integer, nullable=False)
    used_protection: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 关系
    player: Mapped["Player"] = relationship("Player")
