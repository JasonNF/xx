"""灵田种植服务"""
from datetime import datetime, timedelta
from typing import Tuple, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Player, Item, PlayerInventory
from bot.models.cave_dwelling import CaveDwelling, CaveRoom, SpiritField, CaveRoomType


class SpiritFieldService:
    """灵田服务类"""

    @staticmethod
    async def get_spirit_field_room(db: AsyncSession, player_id: int) -> Optional[CaveRoom]:
        """获取玩家的灵田房间"""
        # 获取洞府
        result = await db.execute(
            select(CaveDwelling).where(CaveDwelling.player_id == player_id)
        )
        cave = result.scalar_one_or_none()

        if not cave:
            return None

        # 获取灵田房间
        result = await db.execute(
            select(CaveRoom).where(
                CaveRoom.cave_id == cave.id,
                CaveRoom.room_type == CaveRoomType.SPIRIT_FIELD.value
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def plant_seeds(
        db: AsyncSession,
        player: Player,
        seed_item_id: int,
        harvest_item_id: int,
        quantity: int,
        growth_hours: int
    ) -> Tuple[bool, str]:
        """种植灵药种子

        Args:
            db: 数据库会话
            player: 玩家对象
            seed_item_id: 种子物品ID
            harvest_item_id: 收获物品ID
            quantity: 种植数量
            growth_hours: 生长时间(小时)

        Returns:
            (success, message)
        """
        # 检查是否有灵田
        room = await SpiritFieldService.get_spirit_field_room(db, player.id)
        if not room:
            return False, "你还没有灵田，请先建造灵田房间"

        # 检查灵田是否已被使用
        if room.is_occupied:
            return False, "灵田正在使用中，请先收获"

        # 检查背包中的种子
        result = await db.execute(
            select(PlayerInventory).where(
                PlayerInventory.player_id == player.id,
                PlayerInventory.item_id == seed_item_id,
                PlayerInventory.is_equipped == False
            )
        )
        inv_items = result.scalars().all()
        total_seeds = sum(inv.quantity for inv in inv_items)

        if total_seeds < quantity:
            return False, f"种子不足，需要{quantity}个，只有{total_seeds}个"

        # 消耗种子
        remaining = quantity
        for inv in inv_items:
            if remaining <= 0:
                break

            if inv.quantity <= remaining:
                remaining -= inv.quantity
                await db.delete(inv)
            else:
                inv.quantity -= remaining
                remaining = 0

        # 计算收获倍率 (基于房间等级)
        level_multiplier = 1.0 + (room.room_level - 1) * 0.1
        base_multiplier = room.effect_bonus / 100.0  # 50% -> 0.5
        harvest_multiplier = 1.0 + base_multiplier * level_multiplier

        # 创建种植记录
        spirit_field = SpiritField(
            room_id=room.id,
            player_id=player.id,
            plant_item_id=seed_item_id,
            harvest_item_id=harvest_item_id,
            quantity=quantity,
            harvest_at=datetime.now() + timedelta(hours=growth_hours),
            harvest_multiplier=harvest_multiplier
        )
        db.add(spirit_field)

        # 设置房间占用状态
        room.is_occupied = True
        room.occupied_until = spirit_field.harvest_at

        await db.commit()

        return True, f"成功种植{quantity}个种子，预计{growth_hours}小时后可收获"

    @staticmethod
    async def harvest(
        db: AsyncSession,
        player: Player
    ) -> Tuple[bool, str, dict]:
        """收获灵药

        Returns:
            (success, message, result_data)
        """
        # 获取灵田
        room = await SpiritFieldService.get_spirit_field_room(db, player.id)
        if not room:
            return False, "你还没有灵田", {}

        if not room.is_occupied:
            return False, "灵田中没有种植物", {}

        # 获取种植记录
        result = await db.execute(
            select(SpiritField).where(
                SpiritField.player_id == player.id,
                SpiritField.room_id == room.id,
                SpiritField.is_harvested == False
            )
        )
        spirit_field = result.scalar_one_or_none()

        if not spirit_field:
            return False, "灵田中没有种植物", {}

        # 检查是否可以收获
        if datetime.now() < spirit_field.harvest_at:
            remaining = spirit_field.harvest_at - datetime.now()
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            return False, f"还未成熟，还需{hours}小时{minutes}分钟", {}

        # 计算收获数量
        base_harvest = spirit_field.quantity
        harvest_count = int(base_harvest * spirit_field.harvest_multiplier)

        # 获取收获物品信息
        result = await db.execute(
            select(Item).where(Item.id == spirit_field.harvest_item_id)
        )
        harvest_item = result.scalar_one_or_none()

        if not harvest_item:
            return False, "收获物品数据错误", {}

        # 添加到背包
        result = await db.execute(
            select(PlayerInventory).where(
                PlayerInventory.player_id == player.id,
                PlayerInventory.item_id == spirit_field.harvest_item_id,
                PlayerInventory.is_equipped == False
            )
        )
        existing = result.scalar_one_or_none()

        if existing and harvest_item.is_stackable:
            existing.quantity += harvest_count
        else:
            new_inv = PlayerInventory(
                player_id=player.id,
                item_id=spirit_field.harvest_item_id,
                quantity=harvest_count
            )
            db.add(new_inv)

        # 标记为已收获
        spirit_field.is_harvested = True

        # 释放灵田
        room.is_occupied = False
        room.occupied_until = None

        await db.commit()

        result_data = {
            "item_name": harvest_item.name,
            "quantity": harvest_count,
            "multiplier": spirit_field.harvest_multiplier
        }

        return True, f"成功收获{harvest_item.name} x{harvest_count}", result_data

    @staticmethod
    async def get_field_status(db: AsyncSession, player_id: int) -> Optional[dict]:
        """获取灵田状态

        Returns:
            None 或 状态字典
        """
        room = await SpiritFieldService.get_spirit_field_room(db, player_id)
        if not room:
            return None

        if not room.is_occupied:
            return {
                "occupied": False,
                "message": "灵田空闲中"
            }

        # 获取种植记录
        result = await db.execute(
            select(SpiritField, Item).join(
                Item, Item.id == SpiritField.harvest_item_id
            ).where(
                SpiritField.player_id == player_id,
                SpiritField.room_id == room.id,
                SpiritField.is_harvested == False
            )
        )
        data = result.one_or_none()

        if not data:
            return {
                "occupied": False,
                "message": "灵田空闲中"
            }

        spirit_field, harvest_item = data

        # 检查是否成熟
        is_ready = datetime.now() >= spirit_field.harvest_at

        status = {
            "occupied": True,
            "is_ready": is_ready,
            "harvest_item_name": harvest_item.name,
            "quantity": spirit_field.quantity,
            "harvest_multiplier": spirit_field.harvest_multiplier,
            "planted_at": spirit_field.planted_at,
            "harvest_at": spirit_field.harvest_at
        }

        if not is_ready:
            remaining = spirit_field.harvest_at - datetime.now()
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            status["remaining_time"] = f"{hours}小时{minutes}分钟"
        else:
            status["remaining_time"] = "已成熟，可收获"

        return status
