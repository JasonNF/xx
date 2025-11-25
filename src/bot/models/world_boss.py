"""世界BOSS系统模型"""
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class WorldBossStatus(enum.Enum):
    """世界BOSS状态"""
    ACTIVE = "active"  # 活跃中(可挑战)
    DEFEATED = "defeated"  # 已击败
    ESCAPED = "escaped"  # 逃跑(超时未击败)


class WorldBoss(Base):
    """世界BOSS表"""
    __tablename__ = "world_bosses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="BOSS名称")
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="BOSS描述")

    # BOSS属性
    level: Mapped[int] = mapped_column(Integer, nullable=False, comment="等级")
    max_hp: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="最大血量")
    current_hp: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="当前血量")
    attack: Mapped[int] = mapped_column(Integer, nullable=False, comment="攻击力")
    defense: Mapped[int] = mapped_column(Integer, nullable=False, comment="防御力")

    # 状态
    status: Mapped[str] = mapped_column(SQLEnum(WorldBossStatus), default=WorldBossStatus.ACTIVE, nullable=False)

    # 奖励池
    total_reward_stones: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="总奖励灵石")
    total_reward_exp: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="总奖励经验")

    # 击杀者
    final_killer_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("players.id"), nullable=True, comment="最后一击玩家"
    )

    # 时间
    spawned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, comment="降临时间")
    defeated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="击败时间")
    despawn_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="消失时间(2小时后)")

    # 关系
    final_killer: Mapped[Optional["Player"]] = relationship("Player", foreign_keys=[final_killer_id])
    participants: Mapped[list["WorldBossParticipation"]] = relationship(
        "WorldBossParticipation", back_populates="boss"
    )


class WorldBossParticipation(Base):
    """世界BOSS参与记录"""
    __tablename__ = "world_boss_participations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    boss_id: Mapped[int] = mapped_column(Integer, ForeignKey("world_bosses.id"), nullable=False, index=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)

    # 战斗数据
    total_damage: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False, comment="总伤害")
    attack_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="攻击次数")

    # 奖励
    reward_stones: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="获得灵石")
    reward_exp: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="获得经验")
    reward_item_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("items.id"), nullable=True, comment="获得物品"
    )
    is_rewarded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否已领奖")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 关系
    boss: Mapped["WorldBoss"] = relationship("WorldBoss", back_populates="participants")
    player: Mapped["Player"] = relationship("Player", foreign_keys=[player_id])
    reward_item: Mapped[Optional["Item"]] = relationship("Item", foreign_keys=[reward_item_id])


class WorldBossTemplate(Base):
    """世界BOSS模板"""
    __tablename__ = "world_boss_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="BOSS名称")
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="BOSS描述")

    # 基础属性
    level: Mapped[int] = mapped_column(Integer, nullable=False, comment="等级")
    base_hp: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="基础血量")
    base_attack: Mapped[int] = mapped_column(Integer, nullable=False, comment="基础攻击")
    base_defense: Mapped[int] = mapped_column(Integer, nullable=False, comment="基础防御")

    # 奖励配置
    reward_stones_min: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    reward_stones_max: Mapped[int] = mapped_column(Integer, default=5000, nullable=False)
    reward_exp_min: Mapped[int] = mapped_column(Integer, default=5000, nullable=False)
    reward_exp_max: Mapped[int] = mapped_column(Integer, default=10000, nullable=False)

    # 特殊掉落(JSON: [{"item_id": 1, "chance": 0.1}])
    drop_table: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="掉落表JSON")

    # 权重(用于随机选择BOSS)
    spawn_weight: Mapped[int] = mapped_column(Integer, default=1, nullable=False, comment="刷新权重")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="是否启用")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
