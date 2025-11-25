"""任务系统数据模型"""
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class QuestType(enum.Enum):
    """任务类型"""
    MAIN = "main"  # 主线任务
    DAILY = "daily"  # 每日任务
    WEEKLY = "weekly"  # 每周任务
    RANDOM = "random"  # 随机任务
    SECT = "sect"  # 宗门任务


class QuestStatus(enum.Enum):
    """任务状态"""
    AVAILABLE = "available"  # 可接取
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 已失败
    CLAIMED = "claimed"  # 已领取奖励


class Quest(Base):
    """任务表"""
    __tablename__ = "quests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    quest_type: Mapped[QuestType] = mapped_column(Enum(QuestType), nullable=False)

    # 任务目标
    objective_type: Mapped[str] = mapped_column(String(50), nullable=False)  # kill_monster/collect_item/cultivate等
    objective_target: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # 目标ID或名称
    objective_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 需要完成数量

    # 接取条件
    required_realm: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    required_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    prerequisite_quest_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("quests.id"), nullable=True)

    # 奖励
    exp_reward: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    spirit_stones_reward: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    contribution_reward: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 宗门贡献
    item_rewards: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON格式

    # 是否可重复
    is_repeatable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cooldown_hours: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 重置冷却时间

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class PlayerQuest(Base):
    """玩家任务进度表"""
    __tablename__ = "player_quests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    quest_id: Mapped[int] = mapped_column(Integer, ForeignKey("quests.id"), nullable=False, index=True)

    status: Mapped[QuestStatus] = mapped_column(Enum(QuestStatus), default=QuestStatus.AVAILABLE, nullable=False)

    # 进度
    current_progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 时间
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    claimed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_available_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # 可重复任务的下次可用时间

    # 关系
    player: Mapped["Player"] = relationship("Player", back_populates="quests")
    quest: Mapped["Quest"] = relationship("Quest")


class AchievementCategory(enum.Enum):
    """成就分类"""
    CULTIVATION = "cultivation"  # 修炼
    COMBAT = "combat"  # 战斗
    COLLECTION = "collection"  # 收集
    CRAFTING = "crafting"  # 制作
    EXPLORATION = "exploration"  # 探索
    SOCIAL = "social"  # 社交
    WEALTH = "wealth"  # 财富
    SPECIAL = "special"  # 特殊


class Achievement(Base):
    """成就表"""
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(String(10), default="🏆", nullable=False)

    # 成就分类
    category: Mapped[str] = mapped_column(Enum(AchievementCategory), default=AchievementCategory.SPECIAL, nullable=False)

    # 成就条件
    condition_type: Mapped[str] = mapped_column(String(50), nullable=False)  # realm_reach/battle_win/kill_boss等
    condition_value: Mapped[int] = mapped_column(Integer, nullable=False)

    # 奖励
    title: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 称号
    exp_reward: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    spirit_stones_reward: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reward_item_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("items.id"), nullable=True)
    reward_item_quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # 显示相关
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 是否隐藏成就
    points: Mapped[int] = mapped_column(Integer, default=10, nullable=False)  # 成就点数

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 关系
    reward_item: Mapped[Optional["Item"]] = relationship("Item", foreign_keys=[reward_item_id])


class PlayerAchievement(Base):
    """玩家成就表"""
    __tablename__ = "player_achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    achievement_id: Mapped[int] = mapped_column(Integer, ForeignKey("achievements.id"), nullable=False)

    # 进度追踪
    current_progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_claimed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    claimed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class PlayerTitle(Base):
    """玩家称号"""
    __tablename__ = "player_titles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # 来源(成就名称等)

    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 是否使用中
    obtained_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class AchievementStats(Base):
    """玩家成就统计"""
    __tablename__ = "achievement_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), unique=True, nullable=False, index=True)

    # 统计数据
    total_achievements: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_achievements: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 分类统计
    cultivation_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    combat_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    collection_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    crafting_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    exploration_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    social_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    wealth_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    special_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    last_achievement_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
