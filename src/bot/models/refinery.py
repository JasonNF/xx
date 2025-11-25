"""炼器系统数据模型 - 凡人修仙传版本"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class RefineryRecipe(Base):
    """炼器配方表"""
    __tablename__ = "refinery_recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # 产出物品
    result_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)

    # 炼制要求
    required_refinery_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    base_success_rate: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)

    # 材料配方（JSON格式）
    materials: Mapped[str] = mapped_column(Text, nullable=False)

    # 炼制消耗
    spiritual_power_cost: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    duration_hours: Mapped[int] = mapped_column(Integer, default=2, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class PlayerRefinery(Base):
    """玩家炼器记录"""
    __tablename__ = "player_refinery"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)

    # 炼器等级和经验
    refinery_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    refinery_exp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    next_level_exp: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)

    # 当前炼器状态
    is_refining: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    refining_recipe_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("refinery_recipes.id"), nullable=True)
    refining_start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    refining_end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 统计
    total_refines: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 关系
    player: Mapped["Player"] = relationship("Player", foreign_keys=[player_id])


class RefineryRecord(Base):
    """炼器历史记录"""
    __tablename__ = "refinery_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("refinery_recipes.id"), nullable=False)

    # 结果
    is_success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    item_quality: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-100

    # 获得经验
    exp_gained: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, index=True)


class ItemEnhancement(Base):
    """物品强化/祭炼记录"""
    __tablename__ = "item_enhancements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inventory_id: Mapped[int] = mapped_column(Integer, ForeignKey("player_inventory.id"), nullable=False, unique=True)

    # 强化等级（0-12）
    enhancement_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 祭炼进度（0-100）
    refining_progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 附加属性加成
    bonus_attack: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bonus_defense: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bonus_hp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )
