"""符箓系统数据模型"""
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class TalismanType(str, Enum):
    """符箓类型"""
    ATTACK = "攻击符"
    DEFENSE = "防御符"
    HEALING = "治疗符"
    ESCAPE = "遁符"
    SUMMONING = "召唤符"
    CURSE = "诅咒符"
    AUXILIARY = "辅助符"


class TalismanGrade(str, Enum):
    """符箓品阶"""
    LOW = "下品"
    MEDIUM = "中品"
    HIGH = "上品"
    SUPREME = "极品"


class TalismanRecipe(Base):
    """符箓配方"""
    __tablename__ = "talisman_recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # 符箓属性
    talisman_type: Mapped[str] = mapped_column(String(20), nullable=False)
    grade: Mapped[str] = mapped_column(String(20), nullable=False)

    # 制作要求
    required_realm: Mapped[str] = mapped_column(String(50), nullable=False)
    required_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    required_talisman_skill: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 制符技能等级

    # 材料（JSON格式：[{"item_id": 1, "quantity": 5}]）
    materials: Mapped[str] = mapped_column(Text, nullable=False)

    # 制作成功率和消耗
    base_success_rate: Mapped[float] = mapped_column(Float, default=0.6, nullable=False)
    spiritual_power_cost: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    duration_hours: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # 符箓效果
    effect_power: Mapped[int] = mapped_column(Integer, nullable=False)  # 威力
    effect_duration: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 持续时间(秒)
    cooldown: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 冷却时间(秒)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class PlayerTalismanSkill(Base):
    """玩家制符技能"""
    __tablename__ = "player_talisman_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, unique=True, index=True)

    # 制符等级
    skill_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    skill_exp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    next_level_exp: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)

    # 统计
    total_crafts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 当前制作状态
    is_crafting: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    crafting_recipe_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("talisman_recipes.id"), nullable=True)
    crafting_start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    crafting_end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 关系
    player: Mapped["Player"] = relationship("Player", foreign_keys=[player_id])


class PlayerTalisman(Base):
    """玩家符箓库存"""
    __tablename__ = "player_talismans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("talisman_recipes.id"), nullable=False)

    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    quality: Mapped[int] = mapped_column(Integer, default=50, nullable=False)  # 品质0-100

    acquired_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 关系
    player: Mapped["Player"] = relationship("Player", foreign_keys=[player_id])
    recipe: Mapped["TalismanRecipe"] = relationship("TalismanRecipe")


class TalismanCraftRecord(Base):
    """制符记录"""
    __tablename__ = "talisman_craft_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("talisman_recipes.id"), nullable=False)

    # 结果
    is_success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    talisman_quality: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    exp_gained: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    crafted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, index=True)


class TalismanUsageRecord(Base):
    """符箓使用记录"""
    __tablename__ = "talisman_usage_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("talisman_recipes.id"), nullable=False)

    # 使用场景
    usage_context: Mapped[str] = mapped_column(String(50), nullable=False)  # 战斗/探索/逃跑等
    target_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 目标ID（如有）

    # 效果
    effect_value: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_success: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    used_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
