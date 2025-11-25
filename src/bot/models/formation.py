"""阵法系统数据模型"""
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class FormationType(str, Enum):
    """阵法类型"""
    DEFENSIVE = "防御型"
    OFFENSIVE = "攻击型"
    ILLUSION = "幻术型"
    TRAPPING = "困敌型"
    SUPPORT = "辅助型"
    COMPOUND = "复合型"


class FormationGrade(str, Enum):
    """阵法品阶"""
    LOW = "低阶"  # 炼气期
    MID = "中阶"  # 筑基期
    HIGH = "高阶"  # 结丹期
    ANCIENT = "上古"  # 元婴期+


class FormationTemplate(Base):
    """阵法模板"""
    __tablename__ = "formation_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # 阵法属性
    formation_type: Mapped[str] = mapped_column(String(20), nullable=False)
    grade: Mapped[str] = mapped_column(String(20), nullable=False)

    # 学习要求
    required_realm: Mapped[str] = mapped_column(String(50), nullable=False)
    required_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    learning_cost: Mapped[int] = mapped_column(Integer, default=5000, nullable=False)  # 灵石

    # 阵法效果
    defense_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    attack_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    trap_power: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 困敌强度
    illusion_power: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 幻术强度

    # 布阵消耗
    spirit_stone_cost: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    spiritual_power_cost: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    # 维持消耗（每小时）
    maintenance_cost: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    # 所需阵旗数量
    flag_count: Mapped[int] = mapped_column(Integer, default=4, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class PlayerFormation(Base):
    """玩家阵法记录"""
    __tablename__ = "player_formations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    template_id: Mapped[int] = mapped_column(Integer, ForeignKey("formation_templates.id"), nullable=False)

    # 阵法熟练度
    proficiency: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-100
    proficiency_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1-10级

    # 学习时间
    learned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 关系
    player: Mapped["Player"] = relationship("Player", foreign_keys=[player_id])
    template: Mapped["FormationTemplate"] = relationship("FormationTemplate")


class ActiveFormation(Base):
    """激活的阵法"""
    __tablename__ = "active_formations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    formation_id: Mapped[int] = mapped_column(Integer, ForeignKey("player_formations.id"), nullable=False)

    # 阵法状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)  # 布阵地点

    # 当前效果（受熟练度影响）
    current_defense_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_attack_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 时间
    activated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # 关系
    player: Mapped["Player"] = relationship("Player", foreign_keys=[player_id])
    formation: Mapped["PlayerFormation"] = relationship("PlayerFormation")


class FormationBreakRecord(Base):
    """破阵记录"""
    __tablename__ = "formation_break_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    breaker_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    formation_id: Mapped[int] = mapped_column(Integer, ForeignKey("active_formations.id"), nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False)

    # 破阵结果
    is_success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    damage_taken: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 奖励
    exp_gained: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    spirit_stones_gained: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    broken_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class FormationTrainingRecord(Base):
    """阵法修炼记录"""
    __tablename__ = "formation_training_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    formation_id: Mapped[int] = mapped_column(Integer, ForeignKey("player_formations.id"), nullable=False)

    # 修炼方式
    training_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 布阵练习/实战/研究等

    # 修炼结果
    proficiency_gained: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    level_up: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    new_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    trained_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
