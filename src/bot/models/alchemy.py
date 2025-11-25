"""炼丹系统数据模型 - 凡人修仙传版本"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class PillRecipe(Base):
    """丹方表"""
    __tablename__ = "pill_recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # 产出丹药
    result_pill_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)
    result_quantity_min: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    result_quantity_max: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    # 炼制要求
    required_alchemy_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    base_success_rate: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)  # 基础成功率

    # 材料配方（JSON格式：[{"item_id": 1, "quantity": 3}, ...]）
    ingredients: Mapped[str] = mapped_column(Text, nullable=False)

    # 炼制消耗
    spiritual_power_cost: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    duration_hours: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 炼制时长

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class PlayerAlchemy(Base):
    """玩家炼丹记录"""
    __tablename__ = "player_alchemy"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)

    # 炼丹等级和经验
    alchemy_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    alchemy_exp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    next_level_exp: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)

    # 当前炼丹状态
    is_refining: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    refining_recipe_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("pill_recipes.id"), nullable=True)
    refining_start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    refining_end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 统计
    total_refines: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 关系
    player: Mapped["Player"] = relationship("Player", foreign_keys=[player_id])


class AlchemyRecord(Base):
    """炼丹历史记录"""
    __tablename__ = "alchemy_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("pill_recipes.id"), nullable=False)

    # 结果
    is_success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    pill_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pill_quality: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-100

    # 获得经验
    exp_gained: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, index=True)
