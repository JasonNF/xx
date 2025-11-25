"""洞府系统数据模型"""
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class CaveDwellingGrade(str, Enum):
    """洞府品级"""
    ORDINARY = "普通"  # 无加成
    FINE = "精品"  # 小幅加成
    SUPERIOR = "上品"  # 中幅加成
    TREASURE = "宝地"  # 大幅加成
    HOLY = "圣地"  # 极大加成


class CaveRoomType(str, Enum):
    """洞府房间类型"""
    CULTIVATION = "修炼室"  # 提升修炼速度
    ALCHEMY = "炼丹房"  # 提升炼丹成功率
    REFINERY = "炼器房"  # 提升炼器成功率
    SPIRIT_FIELD = "灵田"  # 种植灵药
    SPIRIT_POOL = "灵池"  # 恢复灵力
    STORAGE = "储物间"  # 扩展背包
    BEAST_ROOM = "灵兽房"  # 灵兽修养
    TALISMAN_ROOM = "制符室"  # 提升制符成功率


class CaveDwelling(Base):
    """玩家洞府"""
    __tablename__ = "cave_dwellings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, unique=True, index=True)

    # 洞府基本信息
    name: Mapped[str] = mapped_column(String(100), nullable=False, default="无名洞府")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location: Mapped[str] = mapped_column(String(100), nullable=False, default="未知之地")

    # 洞府品级和等级
    grade: Mapped[str] = mapped_column(String(20), nullable=False, default=CaveDwellingGrade.ORDINARY.value)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1-10级

    # 灵气浓度（影响修炼速度）
    spiritual_density: Mapped[int] = mapped_column(Integer, default=100, nullable=False)  # 100-1000

    # 房间数量限制
    max_rooms: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    current_rooms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 防御值（防止他人入侵）
    defense: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    # 维护
    maintenance_cost: Mapped[int] = mapped_column(Integer, default=100, nullable=False)  # 每天灵石消耗
    last_maintenance: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 升级花费
    next_level_cost: Mapped[int] = mapped_column(Integer, default=10000, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    upgraded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 关系
    player: Mapped["Player"] = relationship("Player", foreign_keys=[player_id])


class CaveRoom(Base):
    """洞府房间"""
    __tablename__ = "cave_rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cave_id: Mapped[int] = mapped_column(Integer, ForeignKey("cave_dwellings.id"), nullable=False, index=True)

    # 房间信息
    room_type: Mapped[str] = mapped_column(String(20), nullable=False)
    room_name: Mapped[str] = mapped_column(String(100), nullable=False)
    room_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1-5级

    # 房间效果
    effect_bonus: Mapped[int] = mapped_column(Integer, default=10, nullable=False)  # 加成百分比
    effect_description: Mapped[str] = mapped_column(Text, nullable=False)

    # 建造和升级
    build_cost: Mapped[int] = mapped_column(Integer, default=5000, nullable=False)
    upgrade_cost: Mapped[int] = mapped_column(Integer, default=10000, nullable=False)

    # 使用状态（针对灵田等特殊房间）
    is_occupied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    occupied_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    upgraded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # 关系
    cave: Mapped["CaveDwelling"] = relationship("CaveDwelling")


class SpiritField(Base):
    """灵田种植记录"""
    __tablename__ = "spirit_fields"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("cave_rooms.id"), nullable=False, index=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)

    # 种植信息
    plant_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)  # 种植的种子
    harvest_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)  # 收获的灵药

    # 种植数量
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # 时间
    planted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    harvest_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)  # 可收获时间

    # 收获倍率（受房间等级影响）
    harvest_multiplier: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    # 状态
    is_harvested: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class CaveUpgradeRecord(Base):
    """洞府升级记录"""
    __tablename__ = "cave_upgrade_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    cave_id: Mapped[int] = mapped_column(Integer, ForeignKey("cave_dwellings.id"), nullable=False)

    # 升级类型
    upgrade_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 洞府升级/房间建造/房间升级

    # 升级前后
    from_level: Mapped[int] = mapped_column(Integer, nullable=False)
    to_level: Mapped[int] = mapped_column(Integer, nullable=False)

    # 消耗
    cost: Mapped[int] = mapped_column(Integer, nullable=False)

    upgraded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class CaveVisitRecord(Base):
    """洞府访问记录"""
    __tablename__ = "cave_visit_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    visitor_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    cave_id: Mapped[int] = mapped_column(Integer, ForeignKey("cave_dwellings.id"), nullable=False, index=True)

    # 访问目的
    visit_purpose: Mapped[str] = mapped_column(String(50), nullable=False)  # 参观/挑战等

    # 访问结果（如挑战）
    is_success: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    reward_gained: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    visited_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
