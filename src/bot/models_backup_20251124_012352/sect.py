"""宗门相关数据模型"""
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Sect(Base):
    """宗门表"""
    __tablename__ = "sects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    announcement: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 宗门公告

    # 宗主信息
    master_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False)

    # 宗门等级
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    exp: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    next_level_exp: Mapped[int] = mapped_column(BigInteger, default=10000, nullable=False)

    # 宗门资源
    treasury: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)  # 宗门金库
    max_members: Mapped[int] = mapped_column(Integer, default=20, nullable=False)  # 最大成员数
    current_members: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 当前成员数

    # 宗门建筑等级
    hall_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 宗门大殿
    library_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 藏经阁
    workshop_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 炼器阁
    alchemy_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 炼丹房

    # 宗门设置
    auto_accept: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 自动接受申请
    min_realm_requirement: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 最低境界要求

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )

    # 关系
    members: Mapped[list["Player"]] = relationship("Player", back_populates="sect")
    applications: Mapped[list["SectApplication"]] = relationship("SectApplication", back_populates="sect")
    shop_items: Mapped[list["SectShopItem"]] = relationship("SectShopItem", back_populates="sect")


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


class SectWar(Base):
    """宗门战记录"""
    __tablename__ = "sect_wars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    attacker_sect_id: Mapped[int] = mapped_column(Integer, ForeignKey("sects.id"), nullable=False)
    defender_sect_id: Mapped[int] = mapped_column(Integer, ForeignKey("sects.id"), nullable=False)

    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)  # pending/ongoing/finished
    winner_sect_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sects.id"), nullable=True)

    attacker_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    defender_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 战利品
    reward_treasury: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
