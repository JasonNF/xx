"""金丹品质系统数据模型"""
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class CoreQualityGrade(str, Enum):
    """金丹品质等级"""
    INFERIOR = "下品"  # 品质 0-20
    LOW = "低品"  # 品质 21-40
    MEDIUM = "中品"  # 品质 41-60
    HIGH = "上品"  # 品质 61-80
    SUPERIOR = "极品"  # 品质 81-90
    PERFECT = "完美"  # 品质 91-100


class PlayerCore(Base):
    """玩家金丹记录"""
    __tablename__ = "player_cores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, unique=True, index=True)

    # 金丹品质 (0-100)
    quality: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    grade: Mapped[str] = mapped_column(String(10), default=CoreQualityGrade.MEDIUM.value, nullable=False)

    # 结丹时的状态
    formation_cultivation: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 结丹时的修为
    pill_quality: Mapped[int] = mapped_column(Integer, default=50, nullable=False)  # 使用的筑基丹品质

    # 品质加成效果
    cultivation_speed_bonus: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 修炼速度加成
    attack_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 攻击力加成
    defense_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 防御力加成
    hp_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 生命值加成
    spiritual_power_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 灵力加成

    # 特殊属性
    has_dao_pattern: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 是否有道纹(完美金丹)
    dao_pattern_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 道纹数量(1-9)

    formed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 关系
    player: Mapped["Player"] = relationship("Player", foreign_keys=[player_id], back_populates="core")


class CoreFormationAttempt(Base):
    """结丹尝试记录"""
    __tablename__ = "core_formation_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)

    # 结丹条件
    cultivation_level: Mapped[int] = mapped_column(Integer, nullable=False)  # 修为等级
    pill_used_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("items.id"), nullable=True)  # 使用的丹药
    pill_quality: Mapped[int] = mapped_column(Integer, default=50, nullable=False)  # 丹药品质

    # 结果
    is_success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    core_quality: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 结丹成功时的品质
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 失败原因

    attempted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, index=True)


class CoreRefinementRecord(Base):
    """金丹祭炼记录"""
    __tablename__ = "core_refinement_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)

    # 祭炼方式
    method: Mapped[str] = mapped_column(String(50), nullable=False)  # 天材地宝/灵兽精血/天雷淬炼等
    material_used_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("items.id"), nullable=True)

    # 祭炼效果
    quality_before: Mapped[int] = mapped_column(Integer, nullable=False)
    quality_after: Mapped[int] = mapped_column(Integer, nullable=False)
    quality_gain: Mapped[int] = mapped_column(Integer, nullable=False)

    is_success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    risk_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 风险等级 1-10

    refined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
