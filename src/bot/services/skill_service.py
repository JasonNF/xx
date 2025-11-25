"""技能系统服务 - 凡人修仙传版本

包括:
- 五行法术施放
- 青元剑诀等功法专属技能
- 技能冷却管理
- 技能效果计算
"""
import random
from typing import Tuple, Dict, Optional, List
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Player, Skill, PlayerSkill


class SkillService:
    """技能系统服务"""

    @staticmethod
    async def can_use_skill(
        player: Player,
        skill: Skill,
        player_skill: Optional[PlayerSkill] = None
    ) -> Tuple[bool, str]:
        """检查是否可以使用技能"""

        # 检查灵力是否足够
        if player.spiritual_power < skill.spiritual_cost:
            return False, f"灵力不足({player.spiritual_power}/{skill.spiritual_cost})"

        # 检查境界要求
        if skill.required_realm:
            from bot.models.player import RealmType
            realm_order = {
                RealmType.MORTAL: 0,
                RealmType.QI_REFINING: 1,
                RealmType.FOUNDATION: 2,
                RealmType.CORE_FORMATION: 3,
                RealmType.NASCENT_SOUL: 4,
                RealmType.DEITY_TRANSFORMATION: 5,
            }
            if realm_order.get(player.realm, 0) < realm_order.get(skill.required_realm, 0):
                return False, f"需要{skill.required_realm.value}境界"

        # 检查灵根要求
        if skill.required_spirit_root and player.spirit_root:
            if skill.required_spirit_root not in player.spirit_root.element_list:
                return False, f"需要{skill.required_spirit_root}灵根"

        # 检查冷却时间
        if player_skill and player_skill.last_used:
            cooldown_seconds = skill.cooldown_rounds * 3  # 假设每回合3秒
            time_passed = (datetime.now() - player_skill.last_used).total_seconds()
            if time_passed < cooldown_seconds:
                remaining = int(cooldown_seconds - time_passed)
                return False, f"冷却中，还需{remaining}秒"

        return True, ""

    @staticmethod
    async def calculate_skill_damage(
        caster: Player,
        skill: Skill,
        target_defense: int,
        skill_level: int = 1
    ) -> Tuple[int, bool, str]:
        """计算技能伤害

        Returns:
            (damage, is_critical, effect_description)
        """
        # 基础伤害 = 技能基础威力 + 施法者攻击力
        base_damage = skill.base_power + int(caster.attack * 0.5)

        # 技能等级加成 (每级+10%)
        level_bonus = 1.0 + (skill_level - 1) * 0.1

        # 灵根元素匹配加成
        element_bonus = 1.0
        if skill.element and caster.spirit_root:
            if skill.element in caster.spirit_root.element_list:
                element_count = caster.spirit_root.element_count
                # 单灵根对应元素伤害+50%, 双灵根+30%, 以此类推
                if element_count == 1:
                    element_bonus = 1.5
                elif element_count == 2:
                    element_bonus = 1.3
                elif element_count == 3:
                    element_bonus = 1.15
                elif element_count == 4:
                    element_bonus = 1.05

        # 技能伤害倍率
        damage_multiplier = skill.damage_multiplier

        # 计算最终伤害
        total_damage = int(
            base_damage * level_bonus * element_bonus * damage_multiplier
        )

        # 减去防御
        final_damage = max(1, total_damage - target_defense)

        # 暴击判定
        is_crit = random.random() < caster.crit_rate
        if is_crit:
            final_damage = int(final_damage * caster.crit_damage)

        # 生成效果描述
        effect_desc = ""
        if skill.special_effects:
            import json
            try:
                effects = json.loads(skill.special_effects)
                if effects:
                    effect_desc = f"附加效果: {', '.join(effects)}"
            except:
                pass

        return final_damage, is_crit, effect_desc

    @staticmethod
    async def use_skill(
        db: AsyncSession,
        player: Player,
        skill: Skill,
        player_skill: Optional[PlayerSkill] = None
    ) -> Tuple[bool, str]:
        """使用技能（消耗灵力，记录冷却）

        Returns:
            (success, message)
        """
        # 检查是否可以使用
        can_use, msg = await SkillService.can_use_skill(player, skill, player_skill)
        if not can_use:
            return False, msg

        # 消耗灵力
        player.spiritual_power -= skill.spiritual_cost

        # 更新冷却时间
        if player_skill:
            player_skill.last_used = datetime.now()

        await db.commit()
        return True, f"施放 {skill.name}"

    @staticmethod
    async def learn_skill(
        db: AsyncSession,
        player: Player,
        skill: Skill
    ) -> Tuple[bool, str]:
        """学习技能

        Returns:
            (success, message)
        """
        # 检查是否已学习
        result = await db.execute(
            select(PlayerSkill).where(
                PlayerSkill.player_id == player.id,
                PlayerSkill.skill_id == skill.id
            )
        )
        if result.scalar_one_or_none():
            return False, "已经学会此技能"

        # 检查灵石是否足够
        if player.spirit_stones < skill.learning_cost:
            return False, f"灵石不足({player.spirit_stones}/{skill.learning_cost})"

        # 检查境界要求
        if skill.required_realm:
            from bot.models.player import RealmType
            realm_order = {
                RealmType.MORTAL: 0,
                RealmType.QI_REFINING: 1,
                RealmType.FOUNDATION: 2,
                RealmType.CORE_FORMATION: 3,
                RealmType.NASCENT_SOUL: 4,
                RealmType.DEITY_TRANSFORMATION: 5,
            }
            if realm_order.get(player.realm, 0) < realm_order.get(skill.required_realm, 0):
                return False, f"需要{skill.required_realm.value}境界"

        # 检查灵根要求
        if skill.required_spirit_root and player.spirit_root:
            if skill.required_spirit_root not in player.spirit_root.element_list:
                return False, f"需要{skill.required_spirit_root}灵根才能学习"

        # 扣除灵石
        player.spirit_stones -= skill.learning_cost

        # 创建玩家技能记录
        player_skill = PlayerSkill(
            player_id=player.id,
            skill_id=skill.id,
            skill_level=1,
            proficiency=0
        )
        db.add(player_skill)

        await db.commit()
        return True, f"成功学会 {skill.name}！"

    @staticmethod
    async def upgrade_skill(
        db: AsyncSession,
        player: Player,
        skill: Skill,
        player_skill: PlayerSkill
    ) -> Tuple[bool, str]:
        """升级技能

        Returns:
            (success, message)
        """
        # 检查等级上限 (最高10级)
        if player_skill.skill_level >= 10:
            return False, "技能已达最高等级"

        # 计算升级所需熟练度和灵石
        next_level = player_skill.skill_level + 1
        required_proficiency = next_level * 100
        required_stones = skill.learning_cost * next_level

        if player_skill.proficiency < required_proficiency:
            return False, f"熟练度不足({player_skill.proficiency}/{required_proficiency})"

        if player.spirit_stones < required_stones:
            return False, f"灵石不足({player.spirit_stones}/{required_stones})"

        # 扣除资源
        player.spirit_stones -= required_stones
        player_skill.proficiency -= required_proficiency
        player_skill.skill_level += 1

        await db.commit()
        return True, f"{skill.name} 升至 {player_skill.skill_level}级！"

    @staticmethod
    async def get_player_skills(
        db: AsyncSession,
        player: Player
    ) -> List[Dict]:
        """获取玩家所有技能及详情"""
        result = await db.execute(
            select(PlayerSkill, Skill)
            .join(Skill, PlayerSkill.skill_id == Skill.id)
            .where(PlayerSkill.player_id == player.id)
            .order_by(PlayerSkill.skill_level.desc())
        )

        skills_data = []
        for player_skill, skill in result:
            # 检查冷却状态
            is_ready = True
            cooldown_remaining = 0
            if player_skill.last_used:
                cooldown_seconds = skill.cooldown_rounds * 3
                time_passed = (datetime.now() - player_skill.last_used).total_seconds()
                if time_passed < cooldown_seconds:
                    is_ready = False
                    cooldown_remaining = int(cooldown_seconds - time_passed)

            skills_data.append({
                "id": skill.id,
                "name": skill.name,
                "description": skill.description,
                "level": player_skill.skill_level,
                "proficiency": player_skill.proficiency,
                "element": skill.element,
                "base_power": skill.base_power,
                "spiritual_cost": skill.spiritual_cost,
                "cooldown_rounds": skill.cooldown_rounds,
                "is_ready": is_ready,
                "cooldown_remaining": cooldown_remaining,
            })

        return skills_data

    @staticmethod
    def get_skill_element_bonus(skill_element: str, spirit_root_elements: List[str]) -> float:
        """获取技能元素与灵根的匹配加成"""
        if not skill_element or not spirit_root_elements:
            return 1.0

        if skill_element in spirit_root_elements:
            element_count = len(spirit_root_elements)
            if element_count == 1:
                return 1.5  # 天灵根，完美匹配
            elif element_count == 2:
                return 1.3  # 双灵根
            elif element_count == 3:
                return 1.15  # 三灵根
            elif element_count == 4:
                return 1.05  # 伪灵根

        return 1.0  # 无加成
