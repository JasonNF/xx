"""门派相关数据模型 - 凡人修仙传版本"""
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class SectFaction(enum.Enum):
    """门派阵营"""
    RIGHTEOUS = "正道"  # 正道
    DEMONIC = "魔道"  # 魔道
    NEUTRAL = "中立"  # 中立势力
    ALLIANCE = "联盟"  # 修士联盟


class SectRegion(enum.Enum):
    """门派所在区域"""
    TIANNAN = "天南"  # 天南地区
    LUANXINGHAI = "乱星海"  # 乱星海
    DAJIN = "大晋"  # 大晋
    MULAN = "慕兰草原"  # 慕兰草原


class Sect(Base):
    """门派表 - 天南七派、魔道六宗"""
    __tablename__ = "sects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    announcement: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 门派属性
    faction: Mapped[SectFaction] = mapped_column(Enum(SectFaction), default=SectFaction.NEUTRAL, nullable=False)
    region: Mapped[SectRegion] = mapped_column(Enum(SectRegion), default=SectRegion.TIANNAN, nullable=False)

    # 是否NPC门派（如黄枫谷、鬼灵门）
    is_npc_sect: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 宗主信息
    master_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("players.id"), nullable=True)

    # 门派等级
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    reputation: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)  # 声望

    # 门派资源
    treasury: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    max_members: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    # 门派建筑等级
    hall_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 大殿
    library_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 藏经阁
    alchemy_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 炼丹房
    refinery_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 炼器阁

    # 门派设置
    auto_accept: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    min_realm_requirement: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )

    # 关系
    members: Mapped[list["Player"]] = relationship(
        "Player", back_populates="sect", foreign_keys="[Player.sect_id]"
    )
    shop_items: Mapped[list["SectShopItem"]] = relationship("SectShopItem", back_populates="sect")
    applications: Mapped[list["SectApplication"]] = relationship("SectApplication", back_populates="sect")


class SectApplication(Base):
    """宗门申请表"""
    __tablename__ = "sect_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sect_id: Mapped[int] = mapped_column(Integer, ForeignKey("sects.id"), nullable=False, index=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 申请留言
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)  # pending/approved/rejected

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    processed_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("players.id"), nullable=True)

    # 关系
    sect: Mapped["Sect"] = relationship("Sect", back_populates="applications")


class SectShopItem(Base):
    """宗门商店物品"""
    __tablename__ = "sect_shop_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sect_id: Mapped[int] = mapped_column(Integer, ForeignKey("sects.id"), nullable=False, index=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)

    # 兑换条件
    contribution_cost: Mapped[int] = mapped_column(Integer, nullable=False)  # 贡献度消耗
    stock: Mapped[int] = mapped_column(Integer, default=-1, nullable=False)  # 库存，-1表示无限
    required_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 需要宗门等级

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 关系
    sect: Mapped["Sect"] = relationship("Sect", back_populates="shop_items")
    item: Mapped["Item"] = relationship("Item")


class SectContribution(Base):
    """宗门贡献记录"""
    __tablename__ = "sect_contributions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sect_id: Mapped[int] = mapped_column(Integer, ForeignKey("sects.id"), nullable=False, index=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)

    contribution_type: Mapped[str] = mapped_column(String(50), nullable=False)  # donate/task/battle
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # 贡献值
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class SectWarStatus(enum.Enum):
    """宗门战状态"""
    DECLARED = "declared"  # 已宣战(等待开始)
    ONGOING = "ongoing"  # 进行中
    FINISHED = "finished"  # 已结束


class SectWar(Base):
    """宗门战记录"""
    __tablename__ = "sect_wars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    attacker_sect_id: Mapped[int] = mapped_column(Integer, ForeignKey("sects.id"), nullable=False, index=True)
    defender_sect_id: Mapped[int] = mapped_column(Integer, ForeignKey("sects.id"), nullable=False, index=True)

    status: Mapped[str] = mapped_column(Enum(SectWarStatus), default=SectWarStatus.DECLARED, nullable=False)
    winner_sect_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sects.id"), nullable=True)

    # 战况统计
    attacker_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    defender_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    attacker_kills: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    defender_kills: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 战利品
    reward_treasury: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reward_reputation: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 宣战人
    declared_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("players.id"), nullable=True)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 关系
    attacker_sect: Mapped["Sect"] = relationship("Sect", foreign_keys=[attacker_sect_id])
    defender_sect: Mapped["Sect"] = relationship("Sect", foreign_keys=[defender_sect_id])


class SectWarParticipation(Base):
    """宗门战参战记录"""
    __tablename__ = "sect_war_participations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    war_id: Mapped[int] = mapped_column(Integer, ForeignKey("sect_wars.id"), nullable=False, index=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    sect_id: Mapped[int] = mapped_column(Integer, ForeignKey("sects.id"), nullable=False)

    # 个人战况
    kills: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    deaths: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    contribution_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 贡献点数

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
