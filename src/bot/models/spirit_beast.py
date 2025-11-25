"""灵兽系统数据模型"""
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Float, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class BeastType(str, Enum):
    """灵兽类型"""
    ATTACK = "攻击型"
    DEFENSE = "防御型"
    SUPPORT = "辅助型"
    SPECIAL = "特殊型"


class BeastGrade(str, Enum):
    """灵兽品阶"""
    LOW = "低阶"  # 1-3阶
    MID = "中阶"  # 4-6阶
    HIGH = "高阶"  # 7-9阶
    SPIRIT = "灵兽"  # 10-12阶
    ANCIENT = "古兽"  # 13阶+


class BeastQuality(str, Enum):
    """灵兽品质等级"""
    COMMON = "凡品"    # 🟦 1-5星稀有度，适合炼气期至筑基期
    IMMORTAL = "仙品"  # 🟪 6-8星稀有度，适合结丹期至元婴期
    DIVINE = "神品"    # 🟨 9-10星稀有度，适合化神期及以上


class BeastTalent(str, Enum):
    """灵兽天赋类型"""
    # 攻击系天赋
    CRITICAL_STRIKE = "暴击"      # 增加暴击率和暴击伤害
    ARMOR_PIERCE = "破甲"         # 无视部分防御
    COMBO_ATTACK = "连击"         # 有概率连续攻击
    LIFE_STEAL = "吸血"           # 攻击回复生命值
    FURY = "狂怒"                 # 生命值越低攻击越高

    # 防御系天赋
    BLOCK = "格挡"                # 减少受到的伤害
    COUNTER = "反伤"              # 反弹部分伤害
    SHIELD = "护盾"               # 受到致命伤害时触发护盾
    REGENERATION = "回复"         # 持续恢复生命值
    IRON_SKIN = "铁皮"            # 提升防御力

    # 速度系天赋
    FIRST_STRIKE = "先攻"         # 提升先手概率
    DODGE = "闪避"                # 有概率闪避攻击
    PURSUIT = "追击"              # 击败敌人后可追击
    SWIFT = "迅捷"                # 大幅提升速度

    # 特殊系天赋
    SPIRIT_RESONANCE = "灵气共鸣"  # 提升主人修炼速度
    ELEMENT_MASTERY = "元素精通"   # 元素伤害提升
    BATTLE_SPIRIT = "战意"         # 战斗次数越多越强
    FORTUNE = "幸运"              # 提升掉落和捕捉概率
    WISDOM = "睿智"               # 提升经验获取


class TalentRarity(str, Enum):
    """天赋稀有度"""
    COMMON = "普通"      # 白色
    RARE = "稀有"        # 蓝色
    EPIC = "史诗"        # 紫色
    LEGENDARY = "传说"   # 金色


class SpiritBeastTemplate(Base):
    """灵兽模板（种类）"""
    __tablename__ = "spirit_beast_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # 灵兽属性
    beast_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 类型
    quality: Mapped[str] = mapped_column(String(20), default=BeastQuality.COMMON.value, nullable=False)  # 品质等级
    element: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 属性（金木水火土等）

    # 基础属性
    base_attack: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    base_defense: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    base_hp: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    base_speed: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    # 成长率（每级提升）
    growth_attack: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    growth_defense: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    growth_hp: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    # 特殊能力
    special_ability: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 稀有度（1-10，影响捕捉难度）
    rarity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class PlayerSpiritBeast(Base):
    """玩家灵兽"""
    __tablename__ = "player_spirit_beasts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    template_id: Mapped[int] = mapped_column(Integer, ForeignKey("spirit_beast_templates.id"), nullable=False)

    # 灵兽信息
    nickname: Mapped[str] = mapped_column(String(100), nullable=False)  # 昵称
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 等级（1-12阶）
    grade: Mapped[str] = mapped_column(String(20), default=BeastGrade.LOW.value, nullable=False)
    exp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    next_level_exp: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)

    # 当前属性（含加成）
    attack: Mapped[int] = mapped_column(Integer, nullable=False)
    defense: Mapped[int] = mapped_column(Integer, nullable=False)
    hp: Mapped[int] = mapped_column(Integer, nullable=False)
    max_hp: Mapped[int] = mapped_column(Integer, nullable=False)
    speed: Mapped[int] = mapped_column(Integer, nullable=False)

    # 亲密度（0-100）
    intimacy: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 天赋系统
    talents: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON格式存储天赋列表

    # 进化系统
    evolution_stage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 进化阶段（0-3）

    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 是否出战
    is_training: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 是否训练中
    training_end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 战斗统计
    total_battles: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_wins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_kills: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    captured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )

    # 关系
    player: Mapped["Player"] = relationship("Player", foreign_keys=[player_id])
    template: Mapped["SpiritBeastTemplate"] = relationship("SpiritBeastTemplate")


class BeastTrainingRecord(Base):
    """灵兽训练记录"""
    __tablename__ = "beast_training_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    beast_id: Mapped[int] = mapped_column(Integer, ForeignKey("player_spirit_beasts.id"), nullable=False)

    # 训练方式
    training_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 实战/灵材喂养/打坐等
    duration_hours: Mapped[int] = mapped_column(Integer, nullable=False)

    # 训练结果
    exp_gained: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    intimacy_gained: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 是否突破
    level_up: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    new_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    trained_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class BeastBattleRecord(Base):
    """灵兽战斗记录"""
    __tablename__ = "beast_battle_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    beast_id: Mapped[int] = mapped_column(Integer, ForeignKey("player_spirit_beasts.id"), nullable=False, index=True)

    # 战斗信息
    battle_type: Mapped[str] = mapped_column(String(50), nullable=False)  # PVE/PVP/灵兽对战
    opponent: Mapped[str] = mapped_column(String(100), nullable=False)  # 对手名称

    # 战斗结果
    is_win: Mapped[bool] = mapped_column(Boolean, nullable=False)
    exp_gained: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    damage_dealt: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    damage_taken: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    battled_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class BeastFusionRecord(Base):
    """灵兽融合记录"""
    __tablename__ = "beast_fusion_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)

    # 融合材料
    material_beast1_id: Mapped[int] = mapped_column(Integer, nullable=False)  # 材料灵兽1 ID
    material_beast1_name: Mapped[str] = mapped_column(String(100), nullable=False)  # 材料灵兽1 名称
    material_beast1_level: Mapped[int] = mapped_column(Integer, nullable=False)  # 材料灵兽1 等级

    material_beast2_id: Mapped[int] = mapped_column(Integer, nullable=False)  # 材料灵兽2 ID
    material_beast2_name: Mapped[str] = mapped_column(String(100), nullable=False)  # 材料灵兽2 名称
    material_beast2_level: Mapped[int] = mapped_column(Integer, nullable=False)  # 材料灵兽2 等级

    # 融合结果
    result_beast_id: Mapped[int] = mapped_column(Integer, ForeignKey("player_spirit_beasts.id"), nullable=False)
    result_beast_name: Mapped[str] = mapped_column(String(100), nullable=False)  # 结果灵兽名称
    inherited_talents: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 继承的天赋

    # 融合成本
    spirit_stones_cost: Mapped[int] = mapped_column(Integer, nullable=False)

    fused_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class BeastEvolutionRecord(Base):
    """灵兽进化记录"""
    __tablename__ = "beast_evolution_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    beast_id: Mapped[int] = mapped_column(Integer, ForeignKey("player_spirit_beasts.id"), nullable=False)

    # 进化信息
    from_stage: Mapped[int] = mapped_column(Integer, nullable=False)  # 进化前阶段
    to_stage: Mapped[int] = mapped_column(Integer, nullable=False)    # 进化后阶段
    beast_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # 属性提升
    attack_gain: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    defense_gain: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hp_gain: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 进化成本
    spirit_stones_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    evolution_item_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # 使用的进化道具

    evolved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
