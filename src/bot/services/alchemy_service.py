"""炼丹服务"""
import json
import random
from datetime import datetime, timedelta
from typing import Optional, Tuple, List, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Player, Item, PlayerInventory
from bot.models.alchemy import PlayerAlchemy, PillRecipe, AlchemyRecord
from bot.services.cave_service import CaveService


class AlchemyService:
    """炼丹服务类"""

    @staticmethod
    async def get_or_create_alchemy_data(
        db: AsyncSession,
        player: Player
    ) -> PlayerAlchemy:
        """获取或创建玩家炼丹数据"""
        result = await db.execute(
            select(PlayerAlchemy).where(PlayerAlchemy.player_id == player.id)
        )
        alchemy = result.scalar_one_or_none()

        if not alchemy:
            alchemy = PlayerAlchemy(player_id=player.id)
            db.add(alchemy)
            await db.commit()
            await db.refresh(alchemy)

        return alchemy

    @staticmethod
    async def can_refine(
        player: Player,
        alchemy: PlayerAlchemy,
        recipe: PillRecipe
    ) -> Tuple[bool, str]:
        """检查是否可以炼丹"""
        if alchemy.is_refining:
            return False, "正在炼丹中，请先完成当前炼制"

        if player.is_cultivating:
            return False, "修炼中无法炼丹"

        if player.is_in_battle:
            return False, "战斗中无法炼丹"

        if alchemy.alchemy_level < recipe.required_alchemy_level:
            return False, f"炼丹等级不足，需要Lv.{recipe.required_alchemy_level}"

        if player.spiritual_power < recipe.spiritual_power_cost:
            return False, f"灵力不足，需要{recipe.spiritual_power_cost}"

        return True, ""

    @staticmethod
    async def check_ingredients(
        db: AsyncSession,
        player: Player,
        recipe: PillRecipe
    ) -> Tuple[bool, str, List[Dict]]:
        """检查材料是否充足

        Returns:
            (是否充足, 错误信息, 材料列表)
        """
        ingredients = json.loads(recipe.ingredients)
        missing = []

        for ingredient in ingredients:
            item_id = ingredient["item_id"]
            required_qty = ingredient["quantity"]

            # 查询玩家背包
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
                # 获取物品名称
                result = await db.execute(
                    select(Item).where(Item.id == item_id)
                )
                item = result.scalar_one_or_none()
                item_name = item.name if item else f"ID:{item_id}"
                missing.append(f"{item_name}(缺{required_qty - total_qty})")

        if missing:
            return False, f"材料不足：{', '.join(missing)}", ingredients

        return True, "", ingredients

    @staticmethod
    async def start_refining(
        db: AsyncSession,
        player: Player,
        alchemy: PlayerAlchemy,
        recipe: PillRecipe
    ) -> Tuple[bool, str]:
        """开始炼丹"""
        # 检查条件
        can_refine, reason = await AlchemyService.can_refine(player, alchemy, recipe)
        if not can_refine:
            return False, reason

        # 检查材料
        has_materials, reason, ingredients = await AlchemyService.check_ingredients(db, player, recipe)
        if not has_materials:
            return False, reason

        # 消耗材料
        for ingredient in ingredients:
            item_id = ingredient["item_id"]
            required_qty = ingredient["quantity"]

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

        # 设置炼丹状态
        alchemy.is_refining = True
        alchemy.refining_recipe_id = recipe.id
        alchemy.refining_start_time = datetime.now()
        alchemy.refining_end_time = datetime.now() + timedelta(hours=recipe.duration_hours)

        await db.commit()

        return True, f"开始炼制 {recipe.name}，预计{recipe.duration_hours}小时后完成"

    @staticmethod
    async def finish_refining(
        db: AsyncSession,
        player: Player,
        alchemy: PlayerAlchemy
    ) -> Tuple[bool, str, Dict]:
        """完成炼丹"""
        if not alchemy.is_refining:
            return False, "没有正在进行的炼丹", {}

        if datetime.now() < alchemy.refining_end_time:
            remaining = alchemy.refining_end_time - datetime.now()
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            return False, f"炼丹未完成，还需{hours}小时{minutes}分钟", {}

        # 获取丹方
        result = await db.execute(
            select(PillRecipe).where(PillRecipe.id == alchemy.refining_recipe_id)
        )
        recipe = result.scalar_one_or_none()

        if not recipe:
            alchemy.is_refining = False
            await db.commit()
            return False, "丹方数据错误", {}

        # 计算成功率
        success_rate = recipe.base_success_rate
        # 炼丹等级加成
        level_bonus = (alchemy.alchemy_level - recipe.required_alchemy_level) * 0.05
        success_rate += level_bonus
        # 悟性加成
        success_rate += player.comprehension * 0.01
        # 炼丹房加成
        cave_alchemy_bonus = await CaveService.get_alchemy_success_bonus(db, player.id)
        success_rate += cave_alchemy_bonus
        # 限制范围
        success_rate = max(0.1, min(0.95, success_rate))

        # 判定成功
        is_success = random.random() < success_rate

        result_data = {
            "success": is_success,
            "recipe_name": recipe.name,
            "pills": [],
            "exp": 0
        }

        if is_success:
            # 成功，计算产出数量
            pill_count = random.randint(recipe.result_quantity_min, recipe.result_quantity_max)

            # 品质加成（炼丹等级影响）
            quality_bonus = min(alchemy.alchemy_level * 5, 50)

            # 添加到背包
            result = await db.execute(
                select(Item).where(Item.id == recipe.result_pill_id)
            )
            pill_item = result.scalar_one_or_none()

            if pill_item:
                # 查找现有背包
                result = await db.execute(
                    select(PlayerInventory).where(
                        PlayerInventory.player_id == player.id,
                        PlayerInventory.item_id == recipe.result_pill_id,
                        PlayerInventory.is_equipped == False
                    )
                )
                existing = result.scalar_one_or_none()

                if existing and pill_item.is_stackable:
                    existing.quantity += pill_count
                else:
                    new_inv = PlayerInventory(
                        player_id=player.id,
                        item_id=recipe.result_pill_id,
                        quantity=pill_count
                    )
                    db.add(new_inv)

                result_data["pills"] = [{
                    "name": pill_item.name,
                    "count": pill_count,
                    "quality": 50 + quality_bonus
                }]

            # 增加统计
            alchemy.success_count += 1

            # 获得经验（基础50 + 丹方等级 * 10）
            exp_gain = 50 + recipe.required_alchemy_level * 10
        else:
            # 失败，少量经验
            exp_gain = 10

        # 更新经验
        alchemy.alchemy_exp += exp_gain
        result_data["exp"] = exp_gain

        # 检查升级
        while alchemy.alchemy_exp >= alchemy.next_level_exp:
            alchemy.alchemy_exp -= alchemy.next_level_exp
            alchemy.alchemy_level += 1
            alchemy.next_level_exp = int(alchemy.next_level_exp * 1.5)
            result_data["level_up"] = alchemy.alchemy_level

        # 增加总次数
        alchemy.total_refines += 1

        # 记录历史
        record = AlchemyRecord(
            player_id=player.id,
            recipe_id=recipe.id,
            is_success=is_success,
            pill_quantity=pill_count if is_success else 0,
            pill_quality=50 + quality_bonus if is_success else 0,
            exp_gained=exp_gain
        )
        db.add(record)

        # 重置状态
        alchemy.is_refining = False
        alchemy.refining_recipe_id = None
        alchemy.refining_start_time = None
        alchemy.refining_end_time = None

        await db.commit()

        return True, "炼丹完成", result_data

    @staticmethod
    async def cancel_refining(
        db: AsyncSession,
        alchemy: PlayerAlchemy
    ) -> Tuple[bool, str]:
        """取消炼丹（材料不返还）"""
        if not alchemy.is_refining:
            return False, "没有正在进行的炼丹"

        alchemy.is_refining = False
        alchemy.refining_recipe_id = None
        alchemy.refining_start_time = None
        alchemy.refining_end_time = None

        await db.commit()

        return True, "已取消炼丹，材料已消耗无法返还"
