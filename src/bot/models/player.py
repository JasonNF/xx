"""玩家相关数据模型 - 凡人修仙传版本"""
import enum
import json
from datetime import datetime
from typing import Optional, List

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class RealmType(enum.Enum):
    """境界类型枚举 - 人界篇"""
    # 凡人阶段
    MORTAL = "凡人"

    # 人界五大境界
    QI_REFINING = "炼气期"  # 1-13层
    FOUNDATION = "筑基期"  # 初/中/后期
    CORE_FORMATION = "结丹期"  # 初/中/后期（改名避免混淆）
    NASCENT_SOUL = "元婴期"  # 初/中/后期
    DEITY_TRANSFORMATION = "化神期"  # 初/中/后期（人界巅峰）


class RealmStage(enum.Enum):
    """境界小阶段（筑基期及以上）"""
    EARLY = "初期"
    MIDDLE = "中期"
    LATE = "后期"


class SpiritRootElement(enum.Enum):
    """灵根元素类型"""
    # 五行灵根
    METAL = "金"
    WOOD = "木"
    WATER = "水"
    FIRE = "火"
    EARTH = "土"

    # 变异灵根
    WIND = "风"
    THUNDER = "雷"
    ICE = "冰"
    DARK = "暗"


class SpiritRoot(Base):
    """灵根表 - 核心资质系统"""
    __tablename__ = "spirit_roots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), unique=True, nullable=False)

    # 灵根属性（JSON存储：["金", "木", "水", "火"]）
    elements: Mapped[str] = mapped_column(Text, nullable=False)

    # 灵根纯度 0-100（影响修炼速度加成）
    purity: Mapped[int] = mapped_column(Integer, default=50, nullable=False)

    # 是否变异灵根
    is_mutant: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 关系
    player: Mapped["Player"] = relationship("Player", back_populates="spirit_root")

    @property
    def element_list(self) -> List[str]:
        """获取灵根属性列表"""
        return json.loads(self.elements)

    @property
    def element_count(self) -> int:
        """灵根属性数量"""
        return len(self.element_list)

    @property
    def root_type(self) -> str:
        """灵根类型名称"""
        count = self.element_count
        if count == 1:
            if self.is_mutant:
                return "异灵根"
            else:
                return "天灵根"
        elif count == 2:
            return "双灵根"
        elif count == 3:
            return "三灵根"
        elif count == 4:
            return "伪灵根"
        else:
            return "五行废灵根"

    @property
    def cultivation_speed_multiplier(self) -> float:
        """
        计算修炼速度倍率（已平衡优化）

        天灵根: 2.0 + 纯度/400 = 2.0-2.25x
        异灵根: 1.8 + 纯度/500 = 1.8-2.0x
        双灵根: 1.5 + 纯度/600 = 1.5-1.67x
        三灵根: 1.0 + 纯度/800 = 1.0-1.125x
        四灵根: 0.7 + 纯度/800 = 0.7-0.775x (韩立，已提升40%)
        五灵根: 0.5 + 纯度/1000 = 0.5-0.55x (已提升67%)
        """
        count = self.element_count
        if count == 1:
            if self.is_mutant:
                return 1.8 + (self.purity / 500.0)
            else:
                return 2.0 + (self.purity / 400.0)
        elif count == 2:
            return 1.5 + (self.purity / 600.0)
        elif count == 3:
            return 1.0 + (self.purity / 800.0)
        elif count == 4:
            # 提升伪灵根速度：0.5x → 0.7x（提升40%）
            # 韩立就是伪灵根，但通过努力也能成就大道
            return 0.7 + (self.purity / 800.0)
        else:
            # 提升杂灵根速度：0.3x → 0.5x（提升67%）
            return 0.5 + (self.purity / 1000.0)

    @property
    def breakthrough_bonus(self) -> float:
        """
        突破成功率加成（已平衡优化）

        天灵根: 20-25%
        异灵根: 15-20%
        双灵根: 10-16.7%
        三灵根: 5-12.5%
        伪灵根: 0-2.5%（已移除负面影响）
        杂灵根: 0%（已移除-5%惩罚）
        """
        count = self.element_count
        if count == 1:
            if self.is_mutant:
                return 0.15 + (self.purity / 500.0)  # 15-20%
            else:
                return 0.20 + (self.purity / 400.0)  # 20-25%
        elif count == 2:
            return 0.10 + (self.purity / 600.0)  # 10-16.7%
        elif count == 3:
            return 0.05 + (self.purity / 800.0)  # 5-12.5%
        elif count == 4:
            # 伪灵根：给予小幅加成（0-2.5%）而非0
            return self.purity / 2000.0  # 0-2.5%
        else:
            # 杂灵根：移除负面影响，改为0
            return 0.0  # 不再-5%

    def __repr__(self) -> str:
        elements_str = "、".join(self.element_list)
        return f"<SpiritRoot {self.root_type} [{elements_str}] 纯度:{self.purity}>"


class Player(Base):
    """玩家基础信息表"""
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[str] = mapped_column(String(100), nullable=False)  # 道号
    has_renamed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 是否已改过名
    rename_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # 改名时间

    # 境界信息
    realm: Mapped[RealmType] = mapped_column(Enum(RealmType), default=RealmType.MORTAL, nullable=False)
    realm_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # 炼气期: 1-13层
    # 筑基期及以上: 0=初期, 1=中期, 2=后期

    # 基础属性
    hp: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    max_hp: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    spiritual_power: Mapped[int] = mapped_column(Integer, default=100, nullable=False)  # 灵力
    max_spiritual_power: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    # 战斗属性
    attack: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    defense: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    speed: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    crit_rate: Mapped[float] = mapped_column(Float, default=0.05, nullable=False)
    crit_damage: Mapped[float] = mapped_column(Float, default=1.5, nullable=False)

    # 修炼属性
    cultivation_exp: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)  # 当前修为
    next_realm_exp: Mapped[int] = mapped_column(BigInteger, default=10000, nullable=False)  # 突破所需修为
    comprehension: Mapped[int] = mapped_column(Integer, default=10, nullable=False)  # 悟性（8-15）

    # 神识（筑基后觉醒）
    divine_sense: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_divine_sense: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 寿元系统
    age: Mapped[int] = mapped_column(Integer, default=16, nullable=False)  # 当前年龄
    lifespan: Mapped[int] = mapped_column(Integer, default=100, nullable=False)  # 最大寿元

    # 金丹品质（结丹期专用：1-9品，9品最好）
    golden_core_quality: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 经济系统
    spirit_stones: Mapped[int] = mapped_column(BigInteger, default=1000, nullable=False)  # 灵石
    contribution: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 门派贡献
    credits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 积分（用于积分商城）

    # 门派信息
    sect_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sects.id"), nullable=True)
    sect_position: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # 装备栏位
    weapon_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("items.id"), nullable=True)
    armor_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("items.id"), nullable=True)
    accessory_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("items.id"), nullable=True)

    # 当前功法
    cultivation_method_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("cultivation_methods.id"), nullable=True
    )

    # 状态
    is_cultivating: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cultivation_start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cultivation_end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    is_in_battle: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_pve_battle: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_pvp_battle: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 战斗策略（AI行为偏好）
    battle_strategy: Mapped[str] = mapped_column(String(20), default="balanced", nullable=False)

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
    spirit_root: Mapped[Optional["SpiritRoot"]] = relationship(
        "SpiritRoot", back_populates="player", uselist=False
    )
    sect: Mapped[Optional["Sect"]] = relationship(
        "Sect", back_populates="members", foreign_keys=[sect_id]
    )
    inventory: Mapped[list["PlayerInventory"]] = relationship("PlayerInventory", back_populates="player")
    skills: Mapped[list["PlayerSkill"]] = relationship("PlayerSkill", back_populates="player")
    quests: Mapped[list["PlayerQuest"]] = relationship("PlayerQuest", back_populates="player")
    cultivation_method: Mapped[Optional["CultivationMethod"]] = relationship("CultivationMethod")
    core: Mapped[Optional["PlayerCore"]] = relationship(
        "PlayerCore", back_populates="player", uselist=False
    )

    @property
    def full_realm_name(self) -> str:
        """完整境界名称"""
        if self.realm == RealmType.MORTAL:
            return "凡人"

        if self.realm == RealmType.QI_REFINING:
            return f"炼气期{self.realm_level}层"

        # 筑基期及以上
        stage_names = {0: "初期", 1: "中期", 2: "后期"}
        stage = stage_names.get(self.realm_level, "初期")
        return f"{self.realm.value}{stage}"

    @property
    def combat_power(self) -> int:
        """战力评估"""
        # 基础属性
        base_power = int(
            self.attack * 3 +
            self.defense * 2 +
            self.max_hp * 0.5 +
            self.speed * 0.8 +
            self.crit_rate * 1000
        )

        # 境界倍率
        realm_multiplier = {
            RealmType.MORTAL: 1.0,
            RealmType.QI_REFINING: 1.0 + (self.realm_level * 0.1),  # 1.0-2.3x
            RealmType.FOUNDATION: 5.0 + (self.realm_level * 2.0),  # 5-11x
            RealmType.CORE_FORMATION: 25.0 + (self.realm_level * 10.0),  # 25-45x
            RealmType.NASCENT_SOUL: 125.0 + (self.realm_level * 50.0),  # 125-225x
            RealmType.DEITY_TRANSFORMATION: 625.0 + (self.realm_level * 250.0),  # 625-1125x
        }.get(self.realm, 1.0)

        return int(base_power * realm_multiplier)

    @property
    def cultivation_speed(self) -> float:
        """当前修炼速度（每小时获得的修为）"""
        base_speed = 100.0

        # 灵根加成
        spirit_root_multi = self.spirit_root.cultivation_speed_multiplier if self.spirit_root else 1.0

        # 功法加成
        method_bonus = self.cultivation_method.cultivation_speed_bonus if self.cultivation_method else 1.0

        # 悟性加成（每点悟性+5%）
        comprehension_bonus = 1.0 + (self.comprehension * 0.05)

        # 境界惩罚（越高越慢）
        realm_penalty = 1.0 / (1.0 + self.realm_level * 0.1)

        return base_speed * spirit_root_multi * method_bonus * comprehension_bonus * realm_penalty


class CultivationMethod(Base):
    """功法表"""
    __tablename__ = "cultivation_methods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    grade: Mapped[str] = mapped_column(String(20), nullable=False)  # 天地玄黄、人级

    # 功法类型
    method_type: Mapped[str] = mapped_column(String(50), default="通用", nullable=False)  # 通用/剑修/体修/法修

    # 功法效果
    cultivation_speed_bonus: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    attack_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    defense_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hp_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 法力加成（高级功法增加法力上限）
    spiritual_power_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 学习条件
    required_realm: Mapped[RealmType] = mapped_column(Enum(RealmType), nullable=False)
    required_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    learning_cost: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 灵根要求（JSON: ["金", "木"]）
    required_spirit_root: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 宗门功法专属字段
    sect_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sects.id"), nullable=True)  # NULL=通用功法
    required_position_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 学习需要的职位等级(1-7)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class PlayerSkill(Base):
    """玩家技能表"""
    __tablename__ = "player_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    skill_id: Mapped[int] = mapped_column(Integer, ForeignKey("skills.id"), nullable=False)

    # 技能等级和熟练度
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    proficiency: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-10000

    # 当前冷却（战斗中使用）
    current_cooldown: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    learned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 关系
    player: Mapped["Player"] = relationship("Player", back_populates="skills")
    skill: Mapped["Skill"] = relationship("Skill")


class Skill(Base):
    """技能/法术表"""
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # 技能类型
    skill_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 攻击/防御/治疗/辅助/遁术

    # 元素属性
    element: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 金木水火土风雷冰暗

    # 技能效果
    base_power: Mapped[int] = mapped_column(Integer, default=100, nullable=False)  # 基础威力
    damage_multiplier: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    spiritual_cost: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    cooldown_rounds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 特殊效果（JSON: ["眩晕", "流血", "减速"]）
    special_effects: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 学习条件
    required_realm: Mapped[RealmType] = mapped_column(Enum(RealmType), nullable=False)
    required_spirit_root: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 需要特定灵根
    learning_cost: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
