"""阵法服务"""
import random
from datetime import datetime, timedelta
from typing import Tuple, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Player
from bot.models.formation import (
    FormationTemplate, PlayerFormation, ActiveFormation,
    FormationBreakRecord
)


class FormationService:
    """阵法服务类"""

    @staticmethod
    async def learn_formation(
        db: AsyncSession,
        player: Player,
        template_id: int
    ) -> Tuple[bool, str]:
        """学习阵法"""
        # 获取模板
        result = await db.execute(
            select(FormationTemplate).where(FormationTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()

        if not template:
            return False, "阵法不存在"

        # 检查是否已学习
        result = await db.execute(
            select(PlayerFormation).where(
                PlayerFormation.player_id == player.id,
                PlayerFormation.template_id == template_id
            )
        )
        if result.scalar_one_or_none():
            return False, "已经学会这个阵法"

        # 检查境界
        if player.realm != template.required_realm:
            if not FormationService._check_realm_requirement(player.realm, template.required_realm):
                return False, f"需要{template.required_realm}才能学习"

        # 检查灵石
        if player.spirit_stones < template.learning_cost:
            return False, f"灵石不足，需要{template.learning_cost}灵石"

        # 扣除灵石
        player.spirit_stones -= template.learning_cost

        # 学习阵法
        formation = PlayerFormation(
            player_id=player.id,
            template_id=template_id,
            proficiency=0,
            proficiency_level=1
        )
        db.add(formation)

        await db.commit()

        return True, f"成功学会{template.name}"

    @staticmethod
    async def deploy_formation(
        db: AsyncSession,
        player: Player,
        formation_id: int,
        location: str,
        duration_hours: int = 24
    ) -> Tuple[bool, str]:
        """布置阵法"""
        # 获取阵法
        result = await db.execute(
            select(PlayerFormation).where(
                PlayerFormation.id == formation_id,
                PlayerFormation.player_id == player.id
            )
        )
        formation = result.scalar_one_or_none()

        if not formation:
            return False, "未找到该阵法"

        # 获取模板
        result = await db.execute(
            select(FormationTemplate).where(FormationTemplate.id == formation.template_id)
        )
        template = result.scalar_one_or_none()

        if not template:
            return False, "阵法模板错误"

        # 检查资源
        total_spirit_cost = template.spirit_stone_cost
        if player.spirit_stones < total_spirit_cost:
            return False, f"灵石不足，需要{total_spirit_cost}灵石"

        if player.spiritual_power < template.spiritual_power_cost:
            return False, f"灵力不足，需要{template.spiritual_power_cost}灵力"

        # 检查是否已有激活的阵法
        result = await db.execute(
            select(ActiveFormation).where(
                ActiveFormation.player_id == player.id,
                ActiveFormation.is_active == True
            )
        )
        if result.scalar_one_or_none():
            return False, "已有激活的阵法，请先撤除"

        # 扣除资源
        player.spirit_stones -= total_spirit_cost
        player.spiritual_power -= template.spiritual_power_cost

        # 计算实际效果（受熟练度影响）
        proficiency_multiplier = 1.0 + (formation.proficiency / 100) * 0.5
        actual_defense = int(template.defense_bonus * proficiency_multiplier)
        actual_attack = int(template.attack_bonus * proficiency_multiplier)

        # 激活阵法
        active = ActiveFormation(
            player_id=player.id,
            formation_id=formation_id,
            location=location,
            current_defense_bonus=actual_defense,
            current_attack_bonus=actual_attack,
            expires_at=datetime.now() + timedelta(hours=duration_hours)
        )
        db.add(active)

        # 应用加成
        player.defense += actual_defense
        player.attack += actual_attack

        await db.commit()

        return True, f"成功布置{template.name}，持续{duration_hours}小时"

    @staticmethod
    async def dismiss_formation(
        db: AsyncSession,
        player: Player
    ) -> Tuple[bool, str]:
        """撤除阵法"""
        # 获取激活的阵法
        result = await db.execute(
            select(ActiveFormation).where(
                ActiveFormation.player_id == player.id,
                ActiveFormation.is_active == True
            )
        )
        active = result.scalar_one_or_none()

        if not active:
            return False, "没有激活的阵法"

        # 移除加成
        player.defense -= active.current_defense_bonus
        player.attack -= active.current_attack_bonus

        # 撤除阵法
        active.is_active = False

        await db.commit()

        return True, "成功撤除阵法"

    @staticmethod
    async def break_formation(
        db: AsyncSession,
        breaker: Player,
        formation_id: int
    ) -> Tuple[bool, str, Dict]:
        """破阵"""
        # 获取激活的阵法
        result = await db.execute(
            select(ActiveFormation).where(
                ActiveFormation.id == formation_id,
                ActiveFormation.is_active == True
            )
        )
        active = result.scalar_one_or_none()

        if not active:
            return False, "阵法不存在或已失效", {}

        if active.player_id == breaker.id:
            return False, "不能破自己的阵", {}

        # 获取阵法信息
        result = await db.execute(
            select(PlayerFormation).where(PlayerFormation.id == active.formation_id)
        )
        formation = result.scalar_one_or_none()

        result = await db.execute(
            select(FormationTemplate).where(FormationTemplate.id == formation.template_id)
        )
        template = result.scalar_one_or_none()

        # 计算破阵成功率
        base_rate = 0.5
        level_bonus = (breaker.level if breaker.realm == "炼气期" else breaker.level + 13) * 0.02
        comprehension_bonus = breaker.comprehension * 0.01
        formation_penalty = formation.proficiency * 0.003

        success_rate = base_rate + level_bonus + comprehension_bonus - formation_penalty
        success_rate = max(0.1, min(0.9, success_rate))

        is_success = random.random() < success_rate

        # 受到的伤害
        damage = 0
        if not is_success:
            damage = template.defense_bonus + template.trap_power
            breaker.hp = max(1, breaker.hp - damage)

        result_data = {
            "is_success": is_success,
            "damage_taken": damage,
            "exp_gained": 0,
            "stones_gained": 0
        }

        if is_success:
            # 破阵成功
            # 获取阵主
            result = await db.execute(
                select(Player).where(Player.id == active.player_id)
            )
            owner = result.scalar_one_or_none()

            # 移除阵主的加成
            if owner:
                owner.defense -= active.current_defense_bonus
                owner.attack -= active.current_attack_bonus

            # 撤除阵法
            active.is_active = False

            # 奖励
            exp_gained = 200 + template.flag_count * 50
            stones_gained = template.spirit_stone_cost // 2

            result_data["exp_gained"] = exp_gained
            result_data["stones_gained"] = stones_gained

            breaker.spirit_stones += stones_gained

        # 记录
        record = FormationBreakRecord(
            breaker_id=breaker.id,
            formation_id=formation_id,
            owner_id=active.player_id,
            is_success=is_success,
            damage_taken=damage,
            exp_gained=result_data["exp_gained"],
            spirit_stones_gained=result_data["stones_gained"]
        )
        db.add(record)

        await db.commit()

        if is_success:
            return True, "破阵成功！", result_data
        else:
            return False, "破阵失败，受到阵法反噬", result_data

    @staticmethod
    def _check_realm_requirement(current_realm: str, required_realm: str) -> bool:
        """检查境界是否满足要求"""
        realm_order = ["凡人", "炼气期", "筑基期", "结丹期", "元婴期", "化神期"]
        try:
            current_idx = realm_order.index(current_realm)
            required_idx = realm_order.index(required_realm)
            return current_idx >= required_idx
        except ValueError:
            return False
