"""炼器服务"""
import json
import random
from datetime import datetime, timedelta
from typing import Tuple, List, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Player, Item, PlayerInventory
from bot.models.refinery import PlayerRefinery, RefineryRecipe, RefineryRecord, ItemEnhancement
from bot.services.cave_service import CaveService


class RefineryService:
    """炼器服务类"""

    @staticmethod
    async def get_or_create_refinery_data(
        db: AsyncSession,
        player: Player
    ) -> PlayerRefinery:
        """获取或创建玩家炼器数据"""
        result = await db.execute(
            select(PlayerRefinery).where(PlayerRefinery.player_id == player.id)
        )
        refinery = result.scalar_one_or_none()

        if not refinery:
            refinery = PlayerRefinery(player_id=player.id)
            db.add(refinery)
            await db.commit()
            await db.refresh(refinery)

        return refinery

    @staticmethod
    async def can_refine(
        player: Player,
        refinery: PlayerRefinery,
        recipe: RefineryRecipe
    ) -> Tuple[bool, str]:
        """检查是否可以炼器"""
        if refinery.is_refining:
            return False, "正在炼器中，请先完成当前炼制"

        if player.is_cultivating:
            return False, "修炼中无法炼器"

        if player.is_in_battle:
            return False, "战斗中无法炼器"

        if refinery.refinery_level < recipe.required_refinery_level:
            return False, f"炼器等级不足，需要Lv.{recipe.required_refinery_level}"

        if player.spiritual_power < recipe.spiritual_power_cost:
            return False, f"灵力不足，需要{recipe.spiritual_power_cost}"

        return True, ""

    @staticmethod
    async def check_materials(
        db: AsyncSession,
        player: Player,
        recipe: RefineryRecipe
    ) -> Tuple[bool, str, List[Dict]]:
        """检查材料是否充足"""
        materials = json.loads(recipe.materials)
        missing = []

        for material in materials:
            item_id = material["item_id"]
            required_qty = material["quantity"]

            result = await db.execute(
                select(PlayerInventory).where(
                    PlayerInventory.player_id == player.id,
                    PlayerInventory.item_id == item_id,
                    PlayerInventory.is_equipped == False
                )
            )
            inv_items = result.scalars().all()

            total_qty = sum(inv.quantity for inv in inv_items)

            if total_qty < required_qty:
                result = await db.execute(
                    select(Item).where(Item.id == item_id)
                )
                item = result.scalar_one_or_none()
                item_name = item.name if item else f"ID:{item_id}"
                missing.append(f"{item_name}(缺{required_qty - total_qty})")

        if missing:
            return False, f"材料不足：{', '.join(missing)}", materials

        return True, "", materials

    @staticmethod
    async def start_refining(
        db: AsyncSession,
        player: Player,
        refinery: PlayerRefinery,
        recipe: RefineryRecipe
    ) -> Tuple[bool, str]:
        """开始炼器"""
        can_refine, reason = await RefineryService.can_refine(player, refinery, recipe)
        if not can_refine:
            return False, reason

        has_materials, reason, materials = await RefineryService.check_materials(db, player, recipe)
        if not has_materials:
            return False, reason

        # 消耗材料
        for material in materials:
            item_id = material["item_id"]
            required_qty = material["quantity"]

            result = await db.execute(
                select(PlayerInventory).where(
                    PlayerInventory.player_id == player.id,
                    PlayerInventory.item_id == item_id,
                    PlayerInventory.is_equipped == False
                )
            )
            inv_items = result.scalars().all()

            remaining = required_qty
            for inv in inv_items:
                if remaining <= 0:
                    break

                if inv.quantity <= remaining:
                    remaining -= inv.quantity
                    await db.delete(inv)
                else:
                    inv.quantity -= remaining
                    remaining = 0

        # 消耗灵力
        player.spiritual_power -= recipe.spiritual_power_cost

        # 设置炼器状态
        refinery.is_refining = True
        refinery.refining_recipe_id = recipe.id
        refinery.refining_start_time = datetime.now()
        refinery.refining_end_time = datetime.now() + timedelta(hours=recipe.duration_hours)

        await db.commit()

        return True, f"开始炼制 {recipe.name}，预计{recipe.duration_hours}小时后完成"

    @staticmethod
    async def finish_refining(
        db: AsyncSession,
        player: Player,
        refinery: PlayerRefinery
    ) -> Tuple[bool, str, Dict]:
        """完成炼器"""
        if not refinery.is_refining:
            return False, "没有正在进行的炼器", {}

        if datetime.now() < refinery.refining_end_time:
            remaining = refinery.refining_end_time - datetime.now()
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            return False, f"炼器未完成，还需{hours}小时{minutes}分钟", {}

        # 获取配方
        result = await db.execute(
            select(RefineryRecipe).where(RefineryRecipe.id == refinery.refining_recipe_id)
        )
        recipe = result.scalar_one_or_none()

        if not recipe:
            refinery.is_refining = False
            await db.commit()
            return False, "配方数据错误", {}

        # 计算成功率
        success_rate = recipe.base_success_rate
        level_bonus = (refinery.refinery_level - recipe.required_refinery_level) * 0.05
        success_rate += level_bonus
        success_rate += player.comprehension * 0.01
        # 炼器房加成
        cave_refinery_bonus = await CaveService.get_refinery_success_bonus(db, player.id)
        success_rate += cave_refinery_bonus
        success_rate = max(0.1, min(0.95, success_rate))

        # 判定成功
        is_success = random.random() < success_rate

        result_data = {
            "success": is_success,
            "recipe_name": recipe.name,
            "item": None,
            "exp": 0
        }

        if is_success:
            # 获取物品
            result = await db.execute(
                select(Item).where(Item.id == recipe.result_item_id)
            )
            item = result.scalar_one_or_none()

            if item:
                # 添加到背包
                new_inv = PlayerInventory(
                    player_id=player.id,
                    item_id=recipe.result_item_id,
                    quantity=1
                )
                db.add(new_inv)
                await db.flush()

                # 品质加成
                quality = 50 + min(refinery.refinery_level * 5, 50)

                result_data["item"] = {
                    "name": item.name,
                    "quality": quality
                }

            refinery.success_count += 1
            exp_gain = 100 + recipe.required_refinery_level * 20
        else:
            exp_gain = 20

        # 更新经验
        refinery.refinery_exp += exp_gain
        result_data["exp"] = exp_gain

        while refinery.refinery_exp >= refinery.next_level_exp:
            refinery.refinery_exp -= refinery.next_level_exp
            refinery.refinery_level += 1
            refinery.next_level_exp = int(refinery.next_level_exp * 1.5)
            result_data["level_up"] = refinery.refinery_level

        refinery.total_refines += 1

        # 记录
        record = RefineryRecord(
            player_id=player.id,
            recipe_id=recipe.id,
            is_success=is_success,
            item_quality=quality if is_success else 0,
            exp_gained=exp_gain
        )
        db.add(record)

        # 重置状态
        refinery.is_refining = False
        refinery.refining_recipe_id = None
        refinery.refining_start_time = None
        refinery.refining_end_time = None

        await db.commit()

        return True, "炼器完成", result_data

    @staticmethod
    async def enhance_item(
        db: AsyncSession,
        player: Player,
        inventory_id: int,
        material_count: int
    ) -> Tuple[bool, str, Dict]:
        """强化物品（使用材料提升属性）

        Returns:
            (是否成功, 消息, 结果数据)
        """
        # 获取物品
        result = await db.execute(
            select(PlayerInventory).where(
                PlayerInventory.id == inventory_id,
                PlayerInventory.player_id == player.id
            )
        )
        inv = result.scalar_one_or_none()

        if not inv:
            return False, "未找到该物品", {}

        if inv.is_equipped:
            return False, "请先卸下装备再强化", {}

        # 获取或创建强化记录
        result = await db.execute(
            select(ItemEnhancement).where(ItemEnhancement.inventory_id == inventory_id)
        )
        enhancement = result.scalar_one_or_none()

        if not enhancement:
            enhancement = ItemEnhancement(inventory_id=inventory_id)
            db.add(enhancement)

        if enhancement.enhancement_level >= 12:
            return False, "已达到最高强化等级(+12)", {}

        # 计算成功率（等级越高越难）
        success_rate = 1.0 - (enhancement.enhancement_level * 0.05)
        is_success = random.random() < success_rate

        result_data = {
            "success": is_success,
            "level": enhancement.enhancement_level
        }

        if is_success:
            enhancement.enhancement_level += 1
            # 每级增加属性
            enhancement.bonus_attack += 5
            enhancement.bonus_defense += 3
            enhancement.bonus_hp += 10

            result_data["new_level"] = enhancement.enhancement_level
            result_data["bonuses"] = {
                "attack": enhancement.bonus_attack,
                "defense": enhancement.bonus_defense,
                "hp": enhancement.bonus_hp
            }

        await db.commit()

        return True, "强化完成" if is_success else "强化失败", result_data
