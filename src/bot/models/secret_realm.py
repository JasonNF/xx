"""秘境探索系统 - 凡人修仙传版本

包括：
- 血色禁地（筑基丹主药产地）
- 虚天殿遗迹
- 古修士洞府
- 秘境探索记录
"""
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class SecretRealmType(enum.Enum):
    """秘境类型"""
    FORBIDDEN_LAND = "禁地"  # 血色禁地
    ANCIENT_RUIN = "古修士遗迹"  # 虚天殿等
    CAVE_MANSION = "洞府"  # 古修士洞府
    SECRET_REALM = "小型秘境"  # 其他秘境
    TRIAL_GROUND = "试炼之地"  # 宗门试炼


class RealmDifficulty(enum.Enum):
    """秘境难度"""
    EASY = "简单"
    NORMAL = "普通"
    HARD = "困难"
    HELL = "地狱"
    NIGHTMARE = "噩梦"


class RealmStatus(enum.Enum):
    """秘境状态"""
    UNOPENED = "未开启"
    OPEN = "开启中"
    CLOSED = "已关闭"
    PERMANENT = "永久开放"


class SecretRealm(Base):
    """秘境表 - 血色禁地、虚天殿等"""
    __tablename__ = "secret_realms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # 秘境属性
    realm_type: Mapped[SecretRealmType] = mapped_column(Enum(SecretRealmType), nullable=False)
    difficulty: Mapped[RealmDifficulty] = mapped_column(Enum(RealmDifficulty), default=RealmDifficulty.NORMAL)
    status: Mapped[RealmStatus] = mapped_column(Enum(RealmStatus), default=RealmStatus.UNOPENED)

    # 进入条件
    min_realm_requirement: Mapped[str] = mapped_column(String(50), nullable=False)  # 最低境界要求
    max_realm_limit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 最高境界限制
    min_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    entry_cost: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 入场灵石

    # 时间限制
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)  # 探索时长（分钟）
    cooldown_hours: Mapped[int] = mapped_column(Integer, default=24, nullable=False)  # 冷却时间（小时）

    # 开放时间（如果不是永久开放）
    open_start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    open_end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 奖励设置
    base_exp_reward: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    base_spirit_stones: Mapped[int] = mapped_column(Integer, default=500, nullable=False)

    # 危险度（影响遭遇战和陷阱概率）
    danger_level: Mapped[int] = mapped_column(Integer, default=5, nullable=False)  # 1-10

    # 是否为剧情关键秘境
    is_story_realm: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    story_chapter: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # 关联剧情章节

    # 最大同时在线人数（0=无限制）
    max_players: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_players: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )

    # 关系
    loot_pools: Mapped[list["RealmLootPool"]] = relationship("RealmLootPool", back_populates="realm")
    explorations: Mapped[list["RealmExploration"]] = relationship("RealmExploration", back_populates="realm")


class RealmLootPool(Base):
    """秘境掉落池 - 定义秘境内可掉落的物品"""
    __tablename__ = "realm_loot_pools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    realm_id: Mapped[int] = mapped_column(Integer, ForeignKey("secret_realms.id"), nullable=False, index=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)

    # 掉落概率
    drop_rate: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0-1.0
    min_quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    max_quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # 是否为保底奖励
    is_guaranteed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 仅特定境界可掉落
    realm_requirement: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 关系
    realm: Mapped["SecretRealm"] = relationship("SecretRealm", back_populates="loot_pools")
    item: Mapped["Item"] = relationship("Item")


class RealmExploration(Base):
    """玩家秘境探索记录"""
    __tablename__ = "realm_explorations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    realm_id: Mapped[int] = mapped_column(Integer, ForeignKey("secret_realms.id"), nullable=False, index=True)

    # 探索状态
    status: Mapped[str] = mapped_column(String(20), default="exploring", nullable=False)  # exploring/completed/failed/escaped

    # 时间记录
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 探索进度
    exploration_progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-100
    rooms_explored: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 探索的房间数

    # 战斗记录
    battles_won: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    battles_lost: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    monsters_killed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 生存状态
    hp_remaining: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    spiritual_remaining: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 收获统计
    total_exp_gained: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_spirit_stones: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_obtained: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 特殊事件
    rare_events_triggered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 稀有事件次数
    hidden_rooms_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 隐藏房间

    # 最终评价
    completion_rating: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # S/A/B/C/D

    # 关系
    player: Mapped["Player"] = relationship("Player")
    realm: Mapped["SecretRealm"] = relationship("SecretRealm", back_populates="explorations")
    rewards: Mapped[list["ExplorationReward"]] = relationship("ExplorationReward", back_populates="exploration")


class ExplorationReward(Base):
    """探索奖励详情 - 记录玩家在秘境中获得的具体奖励"""
    __tablename__ = "exploration_rewards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exploration_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("realm_explorations.id"), nullable=False, index=True
    )
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # 获得方式
    obtained_from: Mapped[str] = mapped_column(String(50), nullable=False)  # boss/chest/event/hidden
    room_number: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    obtained_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 关系
    exploration: Mapped["RealmExploration"] = relationship("RealmExploration", back_populates="rewards")
    item: Mapped["Item"] = relationship("Item")


class RealmEvent(Base):
    """秘境随机事件配置 - 定义秘境内可能发生的随机事件"""
    __tablename__ = "realm_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    realm_id: Mapped[int] = mapped_column(Integer, ForeignKey("secret_realms.id"), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # treasure/trap/npc/puzzle/battle

    # 触发概率
    trigger_chance: Mapped[float] = mapped_column(Float, default=0.1, nullable=False)  # 0.0-1.0

    # 奖励/惩罚
    exp_reward: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    spirit_stones_reward: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hp_change: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 正数=恢复，负数=伤害
    spiritual_change: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 是否为稀有事件
    is_rare: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 触发条件
    min_luck: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 最低幸运值要求
    required_item_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("items.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 关系
    realm: Mapped["SecretRealm"] = relationship("SecretRealm")
    required_item: Mapped[Optional["Item"]] = relationship("Item", foreign_keys=[required_item_id])
