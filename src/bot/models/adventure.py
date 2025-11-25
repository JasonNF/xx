"""奇遇系统数据模型"""
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class AdventureType(str, Enum):
    """奇遇类型"""
    TREASURE = "宝藏"  # 发现宝物
    INHERITANCE = "传承"  # 获得传承
    ENLIGHTENMENT = "顿悟"  # 修为突破
    ENCOUNTER = "邂逅"  # 遇到高人
    DANGER = "险境"  # 危险事件
    CHALLENGE = "试炼"  # 挑战关卡
    MYSTERY = "秘闻"  # 神秘事件


class AdventureRarity(str, Enum):
    """奇遇稀有度"""
    COMMON = "普通"  # 常见
    RARE = "稀有"  # 稀有
    EPIC = "史诗"  # 史诗
    LEGENDARY = "传说"  # 传说
    MYTHICAL = "神话"  # 神话


class AdventureTemplate(Base):
    """奇遇模板"""
    __tablename__ = "adventure_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # 奇遇属性
    adventure_type: Mapped[str] = mapped_column(String(20), nullable=False)
    rarity: Mapped[str] = mapped_column(String(20), nullable=False)

    # 触发条件
    required_realm: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    required_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    required_location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # 特定地点
    required_luck: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 所需运气值

    # 触发概率
    trigger_rate: Mapped[float] = mapped_column(Float, default=0.01, nullable=False)  # 基础触发率

    # 奖励（JSON格式）
    rewards: Mapped[str] = mapped_column(Text, nullable=False)  # {"type": "item/exp/stones", "value": xxx}

    # 选择项（JSON格式，某些奇遇有多个选择）
    choices: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # [{"text": "选项1", "result": {...}}]

    # 风险等级
    danger_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-10

    # 冷却时间（天）
    cooldown_days: Mapped[int] = mapped_column(Integer, default=7, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class PlayerAdventure(Base):
    """玩家奇遇记录"""
    __tablename__ = "player_adventures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    template_id: Mapped[int] = mapped_column(Integer, ForeignKey("adventure_templates.id"), nullable=False)

    # 触发信息
    triggered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, index=True)
    location: Mapped[str] = mapped_column(String(100), nullable=False)

    # 选择和结果
    choice_made: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 选择的选项索引
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_success: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # 奖励获得
    rewards_claimed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reward_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON存储实际获得的奖励

    # 经历描述（用于记录奇遇故事）
    story: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 关系
    player: Mapped["Player"] = relationship("Player", foreign_keys=[player_id])
    template: Mapped["AdventureTemplate"] = relationship("AdventureTemplate")


class AdventureExploration(Base):
    """奇遇探索记录（探索地图寻找奇遇）"""
    __tablename__ = "adventure_explorations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)

    # 探索地点
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    exploration_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 山脉/秘境/古迹等

    # 探索时间和消耗
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    duration_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    spiritual_power_cost: Mapped[int] = mapped_column(Integer, nullable=False)

    # 结果
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    found_adventure: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    adventure_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("player_adventures.id"), nullable=True)

    # 其他发现（未触发奇遇时的普通奖励）
    exp_gained: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_found: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON


class LuckEvent(Base):
    """运气事件（影响奇遇触发）"""
    __tablename__ = "luck_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)

    # 事件类型
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 祈福/厄运/天象等
    event_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # 运气影响
    luck_modifier: Mapped[int] = mapped_column(Integer, nullable=False)  # +/-运气值
    duration_hours: Mapped[int] = mapped_column(Integer, nullable=False)  # 持续时间

    # 时间
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class AdventureCooldown(Base):
    """奇遇冷却记录"""
    __tablename__ = "adventure_cooldowns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    template_id: Mapped[int] = mapped_column(Integer, ForeignKey("adventure_templates.id"), nullable=False)

    # 冷却时间
    last_triggered: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, index=True)
    cooldown_until: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
