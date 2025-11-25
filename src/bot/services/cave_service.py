"""洞府服务"""
from typing import Optional, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Player
from bot.models.cave_dwelling import CaveDwelling, CaveRoom, CaveRoomType


class CaveService:
    """洞府服务类"""

    @staticmethod
    async def get_player_cave(db: AsyncSession, player_id: int) -> Optional[CaveDwelling]:
        """获取玩家洞府"""
        result = await db.execute(
            select(CaveDwelling).where(CaveDwelling.player_id == player_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_room_bonus(db: AsyncSession, player_id: int, room_type: str) -> int:
        """获取特定房间类型的加成

        Args:
            db: 数据库会话
            player_id: 玩家ID
            room_type: 房间类型 (CaveRoomType的value)

        Returns:
            加成百分比 (例如 20 表示 20%)
        """
        # 获取玩家洞府
        result = await db.execute(
            select(CaveDwelling).where(CaveDwelling.player_id == player_id)
        )
        cave = result.scalar_one_or_none()

        if not cave:
            return 0

        # 获取指定类型的房间
        result = await db.execute(
            select(CaveRoom).where(
                CaveRoom.cave_id == cave.id,
                CaveRoom.room_type == room_type
            )
        )
        room = result.scalar_one_or_none()

        if not room:
            return 0

        # 房间等级影响加成 (每级+2%)
        level_multiplier = 1.0 + (room.room_level - 1) * 0.1
        return int(room.effect_bonus * level_multiplier)

    @staticmethod
    async def get_all_room_bonuses(db: AsyncSession, player_id: int) -> Dict[str, int]:
        """获取玩家所有房间加成

        Returns:
            字典: {房间类型: 加成百分比}
        """
        bonuses = {}

        # 获取玩家洞府
        result = await db.execute(
            select(CaveDwelling).where(CaveDwelling.player_id == player_id)
        )
        cave = result.scalar_one_or_none()

        if not cave:
            return bonuses

        # 获取所有房间
        result = await db.execute(
            select(CaveRoom).where(CaveRoom.cave_id == cave.id)
        )
        rooms = result.scalars().all()

        for room in rooms:
            level_multiplier = 1.0 + (room.room_level - 1) * 0.1
            bonus = int(room.effect_bonus * level_multiplier)
            bonuses[room.room_type] = bonus

        return bonuses

    @staticmethod
    async def get_cultivation_speed_bonus(db: AsyncSession, player_id: int) -> float:
        """获取修炼速度加成 (来自修炼室)

        Returns:
            加成倍率 (例如 1.2 表示提升20%)
        """
        bonus_percent = await CaveService.get_room_bonus(
            db, player_id, CaveRoomType.CULTIVATION.value
        )
        return 1.0 + (bonus_percent / 100.0)

    @staticmethod
    async def get_alchemy_success_bonus(db: AsyncSession, player_id: int) -> float:
        """获取炼丹成功率加成 (来自炼丹房)

        Returns:
            加成百分比 (例如 0.15 表示+15%)
        """
        bonus_percent = await CaveService.get_room_bonus(
            db, player_id, CaveRoomType.ALCHEMY.value
        )
        return bonus_percent / 100.0

    @staticmethod
    async def get_refinery_success_bonus(db: AsyncSession, player_id: int) -> float:
        """获取炼器成功率加成 (来自炼器房)

        Returns:
            加成百分比 (例如 0.15 表示+15%)
        """
        bonus_percent = await CaveService.get_room_bonus(
            db, player_id, CaveRoomType.REFINERY.value
        )
        return bonus_percent / 100.0

    @staticmethod
    async def get_talisman_success_bonus(db: AsyncSession, player_id: int) -> float:
        """获取制符成功率加成 (来自制符室)

        Returns:
            加成百分比 (例如 0.15 表示+15%)
        """
        bonus_percent = await CaveService.get_room_bonus(
            db, player_id, CaveRoomType.TALISMAN_ROOM.value
        )
        return bonus_percent / 100.0

    @staticmethod
    async def get_beast_growth_bonus(db: AsyncSession, player_id: int) -> float:
        """获取灵兽成长速度加成 (来自灵兽房)

        Returns:
            加成倍率 (例如 1.25 表示提升25%)
        """
        bonus_percent = await CaveService.get_room_bonus(
            db, player_id, CaveRoomType.BEAST_ROOM.value
        )
        return 1.0 + (bonus_percent / 100.0)

    @staticmethod
    async def get_storage_expansion(db: AsyncSession, player_id: int) -> int:
        """获取背包扩展格数 (来自储物间)

        Returns:
            扩展的格子数
        """
        return await CaveService.get_room_bonus(
            db, player_id, CaveRoomType.STORAGE.value
        )

    @staticmethod
    async def has_spirit_pool(db: AsyncSession, player_id: int) -> bool:
        """检查是否有灵池"""
        result = await db.execute(
            select(CaveDwelling).where(CaveDwelling.player_id == player_id)
        )
        cave = result.scalar_one_or_none()

        if not cave:
            return False

        result = await db.execute(
            select(CaveRoom).where(
                CaveRoom.cave_id == cave.id,
                CaveRoom.room_type == CaveRoomType.SPIRIT_POOL.value
            )
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def has_spirit_field(db: AsyncSession, player_id: int) -> bool:
        """检查是否有灵田"""
        result = await db.execute(
            select(CaveDwelling).where(CaveDwelling.player_id == player_id)
        )
        cave = result.scalar_one_or_none()

        if not cave:
            return False

        result = await db.execute(
            select(CaveRoom).where(
                CaveRoom.cave_id == cave.id,
                CaveRoom.room_type == CaveRoomType.SPIRIT_FIELD.value
            )
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def get_spiritual_density_bonus(db: AsyncSession, player_id: int) -> float:
        """获取洞府灵气浓度加成

        Returns:
            加成倍率 (基于灵气浓度，100=1.0, 200=1.2等)
        """
        result = await db.execute(
            select(CaveDwelling).where(CaveDwelling.player_id == player_id)
        )
        cave = result.scalar_one_or_none()

        if not cave:
            return 1.0

        # 灵气浓度每100点提供10%加成
        return 1.0 + ((cave.spiritual_density - 100) / 100) * 0.1
