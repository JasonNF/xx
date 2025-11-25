"""玩家相关数据模型"""
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class RealmType(enum.Enum):
    """境界类型枚举"""
    # 凡人阶段
    MORTAL = "凡人"

    # 修仙阶段
    QI_REFINING = "炼气期"  # 1-9层
    FOUNDATION = "筑基期"  # 1-9层
    GOLDEN_CORE = "金丹期"  # 1-9层
    NASCENT_SOUL = "元婴期"  # 1-9层
    SOUL_FORMATION = "化神期"  # 1-9层
    VOID_REFINEMENT = "炼虚期"  # 1-9层
    BODY_INTEGRATION = "合体期"  # 1-9层
    MAHAYANA = "大乘期"  # 1-9层
    TRIBULATION = "渡劫期"  # 1-9层

    # 仙人阶段
    TRUE_IMMORTAL = "真仙"
    GOLDEN_IMMORTAL = "金仙"
    SUPREME_GOLDEN_IMMORTAL = "太乙金仙"
    DALUO_GOLDEN_IMMORTAL = "大罗金仙"


class Player(Base):
    """玩家基础信息表"""
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[str] = mapped_column(String(100), nullable=False)  # 游戏昵称

    # 境界信息
    realm: Mapped[RealmType] = mapped_column(Enum(RealmType), default=RealmType.MORTAL, nullable=False)
    realm_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 境界层数(1-9)

    # 基础属性
    hp: Mapped[int] = mapped_column(Integer, default=100, nullable=False)  # 生命值
    max_hp: Mapped[int] = mapped_column(Integer, default=100, nullable=False)  # 最大生命值
    spiritual_power: Mapped[int] = mapped_column(Integer, default=100, nullable=False)  # 灵力
    max_spiritual_power: Mapped[int] = mapped_column(Integer, default=100, nullable=False)  # 最大灵力

    # 战斗属性
    attack: Mapped[int] = mapped_column(Integer, default=10, nullable=False)  # 攻击力
    defense: Mapped[int] = mapped_column(Integer, default=5, nullable=False)  # 防御力
    speed: Mapped[int] = mapped_column(Integer, default=10, nullable=False)  # 速度
    crit_rate: Mapped[float] = mapped_column(Float, default=0.05, nullable=False)  # 暴击率
    crit_damage: Mapped[float] = mapped_column(Float, default=1.5, nullable=False)  # 暴击伤害

    # 修炼属性
    cultivation_exp: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)  # 当前修为
    next_realm_exp: Mapped[int] = mapped_column(BigInteger, default=1000, nullable=False)  # 突破所需修为
    comprehension: Mapped[int] = mapped_column(Integer, default=10, nullable=False)  # 悟性(影响修炼速度)
    root_bone: Mapped[int] = mapped_column(Integer, default=10, nullable=False)  # 根骨(资质)

    # 经济系统
    spirit_stones: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)  # 灵石
    contribution: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 宗门贡献度

    # 宗门信息
    sect_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sects.id"), nullable=True)
    sect_position: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 宗门职位

    # 装备栏位
    weapon_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("items.id"), nullable=True)
    armor_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("items.id"), nullable=True)
    accessory_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("items.id"), nullable=True)

    # 当前功法
    cultivation_method_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("cultivation_methods.id"), nullable=True
    )

    # 状态
    is_cultivating: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 是否正在修炼
    cultivation_start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cultivation_end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    is_in_battle: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 是否在战斗中
    last_pve_battle: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_pvp_battle: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 签到
    last_sign_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    continuous_sign_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 统计数据
    total_battles: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_wins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_kills: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )

    # 关系
    sect: Mapped[Optional["Sect"]] = relationship("Sect", back_populates="members")
    inventory: Mapped[list["PlayerInventory"]] = relationship("PlayerInventory", back_populates="player")
    skills: Mapped[list["PlayerSkill"]] = relationship("PlayerSkill", back_populates="player")
    quests: Mapped[list["PlayerQuest"]] = relationship("PlayerQuest", back_populates="player")
    cultivation_method: Mapped[Optional["CultivationMethod"]] = relationship("CultivationMethod")

    @property
    def full_realm_name(self) -> str:
        """完整境界名称"""
        if self.realm == RealmType.MORTAL:
            return "凡人"
        if self.realm_level == 0:
            return f"{self.realm.value}初期"
        elif self.realm_level <= 3:
            return f"{self.realm.value}{self.realm_level}层"
        elif self.realm_level <= 6:
            return f"{self.realm.value}中期"
        else:
            return f"{self.realm.value}后期"

    @property
    def combat_power(self) -> int:
        """战力评估"""
        return int(
            self.attack * 2 +
            self.defense * 1.5 +
            self.max_hp * 0.5 +
            self.speed * 0.8 +
            self.crit_rate * 1000
        )


class CultivationMethod(Base):
    """功法表"""
    __tablename__ = "cultivation_methods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    grade: Mapped[str] = mapped_column(String(20), nullable=False)  # 天地玄黄

    # 功法效果
    cultivation_speed_bonus: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    attack_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    defense_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hp_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 学习条件
    required_realm: Mapped[RealmType] = mapped_column(Enum(RealmType), nullable=False)
    required_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    learning_cost: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 学习消耗灵石

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class PlayerSkill(Base):
    """玩家技能表"""
    __tablename__ = "player_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False)
    skill_id: Mapped[int] = mapped_column(Integer, ForeignKey("skills.id"), nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    exp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 关系
    player: Mapped["Player"] = relationship("Player", back_populates="skills")
    skill: Mapped["Skill"] = relationship("Skill")


class Skill(Base):
    """技能表"""
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    skill_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 攻击、防御、辅助

    # 技能效果
    damage_multiplier: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    spiritual_cost: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    cooldown: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 冷却回合

    # 学习条件
    required_realm: Mapped[RealmType] = mapped_column(Enum(RealmType), nullable=False)
    learning_cost: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
