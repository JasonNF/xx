"""战斗相关数据模型"""
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Integer, String, Text, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class BattleType(enum.Enum):
    """战斗类型"""
    PVE = "pve"  # 打怪
    PVP = "pvp"  # 玩家对战
    BOSS = "boss"  # Boss战
    SECT_WAR = "sect_war"  # 宗门战


class BattleResult(enum.Enum):
    """战斗结果"""
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"


class Monster(Base):
    """怪物表"""
    __tablename__ = "monsters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    realm: Mapped[str] = mapped_column(String(50), nullable=False)  # 境界

    # 属性
    hp: Mapped[int] = mapped_column(Integer, nullable=False)
    attack: Mapped[int] = mapped_column(Integer, nullable=False)
    defense: Mapped[int] = mapped_column(Integer, nullable=False)
    speed: Mapped[int] = mapped_column(Integer, nullable=False)

    # 奖励
    exp_reward: Mapped[int] = mapped_column(Integer, nullable=False)  # 修为奖励
    spirit_stones_min: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    spirit_stones_max: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 掉落物品（JSON格式存储）
    drop_items: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    drop_rate: Mapped[float] = mapped_column(Float, default=0.1, nullable=False)

    is_boss: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class BattleRecord(Base):
    """战斗记录表"""
    __tablename__ = "battle_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    battle_type: Mapped[BattleType] = mapped_column(Enum(BattleType), nullable=False, index=True)

    # 参战方
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    opponent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("players.id"), nullable=True)  # PVP时
    monster_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("monsters.id"), nullable=True)  # PVE时

    # 战斗数据
    player_hp_before: Mapped[int] = mapped_column(Integer, nullable=False)
    player_hp_after: Mapped[int] = mapped_column(Integer, nullable=False)
    opponent_hp_before: Mapped[int] = mapped_column(Integer, nullable=False)
    opponent_hp_after: Mapped[int] = mapped_column(Integer, nullable=False)

    # 战斗回合数
    rounds: Mapped[int] = mapped_column(Integer, nullable=False)

    # 战斗结果
    result: Mapped[BattleResult] = mapped_column(Enum(BattleResult), nullable=False)

    # 奖励
    exp_gained: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    spirit_stones_gained: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_gained: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON格式

    # 战斗详情（JSON格式存储）
    battle_log: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class Arena(Base):
    """竞技场表"""
    __tablename__ = "arenas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), unique=True, nullable=False)

    # 排名
    rank: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    highest_rank: Mapped[int] = mapped_column(Integer, nullable=False)

    # 积分
    points: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)

    # 战斗统计
    total_challenges: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_wins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    win_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    highest_win_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 每日挑战次数
    daily_challenges: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_daily_challenges: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    last_challenge_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )
