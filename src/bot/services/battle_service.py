"""战斗系统服务"""
import random
from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Player, Monster, BattleRecord, BattleType, BattleResult, PlayerSkill, Skill
from bot.config import settings
from bot.services.skill_service import SkillService
from bot.services.battle_strategy import BattleAI, BattleStrategy


class BattleService:
    """战斗服务类"""

    @staticmethod
    async def _get_player_available_skills(
        db: AsyncSession,
        player: Player,
        current_sp: int
    ) -> List[Tuple[PlayerSkill, Skill]]:
        """获取玩家可用技能列表（灵力足够）

        Returns:
            List of (PlayerSkill, Skill) tuples
        """
        result = await db.execute(
            select(PlayerSkill, Skill)
            .join(Skill, PlayerSkill.skill_id == Skill.id)
            .where(PlayerSkill.player_id == player.id)
            .where(Skill.spiritual_cost <= current_sp)  # 只返回灵力足够的技能
        )

        skills = []
        for player_skill, skill in result:
            skills.append((player_skill, skill))

        return skills

    @staticmethod
    async def can_battle_pve(player: Player) -> Tuple[bool, str]:
        """检查是否可以进行PVE战斗"""
        if player.is_cultivating:
            return False, "修炼中无法战斗"

        if player.is_in_battle:
            return False, "已在战斗中"

        if player.hp <= 0:
            return False, "生命值不足，请先恢复"

        # 检查冷却时间
        if player.last_pve_battle:
            cooldown = settings.PVE_COOLDOWN
            time_passed = (datetime.now() - player.last_pve_battle).total_seconds()
            if time_passed < cooldown:
                remaining = int(cooldown - time_passed)
                return False, f"冷却中，还需等待 {remaining} 秒"

        return True, ""

    @staticmethod
    async def can_battle_pvp(player: Player) -> Tuple[bool, str]:
        """检查是否可以进行PVP战斗"""
        if player.is_cultivating:
            return False, "修炼中无法战斗"

        if player.is_in_battle:
            return False, "已在战斗中"

        if player.hp <= player.max_hp * 0.3:
            return False, "生命值低于30%，无法进行PVP"

        # 检查冷却时间
        if player.last_pvp_battle:
            cooldown = settings.PVP_COOLDOWN
            time_passed = (datetime.now() - player.last_pvp_battle).total_seconds()
            if time_passed < cooldown:
                remaining = int(cooldown - time_passed)
                return False, f"冷却中，还需等待 {remaining} 秒"

        return True, ""

    @staticmethod
    async def battle_pve(
        db: AsyncSession,
        player: Player,
        monster: Monster
    ) -> Tuple[BattleResult, List[str], Dict]:
        """PVE战斗

        Returns:
            (result, battle_log, rewards)
        """
        # 设置战斗状态
        player.is_in_battle = True
        await db.commit()

        try:
            # 复制属性用于战斗
            player_hp = player.hp
            player_sp = player.spiritual_power
            monster_hp = monster.hp

            battle_log = []
            battle_log.append(f"⚔️ {player.nickname} VS {monster.name}")
            battle_log.append(f"💚 {player.nickname}: {player_hp}/{player.max_hp} | 💙灵力: {player_sp}/{player.max_spiritual_power}")
            battle_log.append(f"💔 {monster.name}: {monster_hp}/{monster.hp}")
            battle_log.append(f"📋 战斗策略: {BattleStrategy(player.battle_strategy).name}")
            battle_log.append("---")

            # 解析玩家战斗策略
            try:
                strategy = BattleStrategy(player.battle_strategy)
            except:
                strategy = BattleStrategy.BALANCED

            # 战斗回合
            round_num = 0
            max_rounds = settings.MAX_BATTLE_ROUNDS

            while player_hp > 0 and monster_hp > 0 and round_num < max_rounds:
                round_num += 1
                battle_log.append(f"\n第 {round_num} 回合：")

                # 根据速度决定谁先攻击
                player_first = player.speed >= monster.speed

                if player_first:
                    # 玩家先攻击 - 使用AI选择技能或普通攻击
                    available_skills = await BattleService._get_player_available_skills(db, player, player_sp)
                    action_type, skill_tuple, reason = BattleAI.select_action(
                        player=player,
                        available_skills=available_skills,
                        strategy=strategy,
                        current_hp=player_hp,
                        current_sp=player_sp,
                        opponent_hp=monster_hp,
                        opponent_max_hp=monster.hp,
                        round_num=round_num
                    )

                    if action_type == "skill" and skill_tuple:
                        player_skill, skill = skill_tuple
                        # 使用技能
                        damage, is_crit, effect_desc = await SkillService.calculate_skill_damage(
                            caster=player,
                            skill=skill,
                            target_defense=monster.defense,
                            skill_level=player_skill.skill_level
                        )
                        player_sp -= skill.spiritual_cost
                        monster_hp -= damage
                        crit_text = "💥暴击！" if is_crit else ""
                        battle_log.append(f"  ✨ {player.nickname} 施放 [{skill.name}] 造成 {damage} 伤害 {crit_text}")
                        if effect_desc:
                            battle_log.append(f"     {effect_desc}")
                    else:
                        # 普通攻击
                        damage, is_crit = BattleService._calculate_damage(
                            player.attack, monster.defense, player.crit_rate, player.crit_damage
                        )
                        monster_hp -= damage
                        crit_text = "💥暴击！" if is_crit else ""
                        battle_log.append(f"  🗡️ {player.nickname} 普通攻击造成 {damage} 伤害 {crit_text}")

                    if monster_hp <= 0:
                        break

                    # 怪物反击
                    damage, is_crit = BattleService._calculate_damage(
                        monster.attack, player.defense, 0.05, 1.5
                    )
                    player_hp -= damage
                    crit_text = "💥暴击！" if is_crit else ""
                    battle_log.append(f"  👹 {monster.name} 攻击造成 {damage} 伤害 {crit_text}")
                else:
                    # 怪物先攻击
                    damage, is_crit = BattleService._calculate_damage(
                        monster.attack, player.defense, 0.05, 1.5
                    )
                    player_hp -= damage
                    crit_text = "💥暴击！" if is_crit else ""
                    battle_log.append(f"  👹 {monster.name} 攻击造成 {damage} 伤害 {crit_text}")

                    if player_hp <= 0:
                        break

                    # 玩家反击 - 使用AI选择技能或普通攻击
                    available_skills = await BattleService._get_player_available_skills(db, player, player_sp)
                    action_type, skill_tuple, reason = BattleAI.select_action(
                        player=player,
                        available_skills=available_skills,
                        strategy=strategy,
                        current_hp=player_hp,
                        current_sp=player_sp,
                        opponent_hp=monster_hp,
                        opponent_max_hp=monster.hp,
                        round_num=round_num
                    )

                    if action_type == "skill" and skill_tuple:
                        player_skill, skill = skill_tuple
                        # 使用技能
                        damage, is_crit, effect_desc = await SkillService.calculate_skill_damage(
                            caster=player,
                            skill=skill,
                            target_defense=monster.defense,
                            skill_level=player_skill.skill_level
                        )
                        player_sp -= skill.spiritual_cost
                        monster_hp -= damage
                        crit_text = "💥暴击！" if is_crit else ""
                        battle_log.append(f"  ✨ {player.nickname} 施放 [{skill.name}] 造成 {damage} 伤害 {crit_text}")
                        if effect_desc:
                            battle_log.append(f"     {effect_desc}")
                    else:
                        # 普通攻击
                        damage, is_crit = BattleService._calculate_damage(
                            player.attack, monster.defense, player.crit_rate, player.crit_damage
                        )
                        monster_hp -= damage
                        crit_text = "💥暴击！" if is_crit else ""
                        battle_log.append(f"  🗡️ {player.nickname} 普通攻击造成 {damage} 伤害 {crit_text}")

            # 判定结果
            if player_hp > 0 and monster_hp <= 0:
                result = BattleResult.WIN
                battle_log.append("\n---")
                battle_log.append("🎉 胜利！")
            elif player_hp <= 0:
                result = BattleResult.LOSE
                battle_log.append("\n---")
                battle_log.append("💀 战败...")
            else:
                result = BattleResult.DRAW
                battle_log.append("\n---")
                battle_log.append("⏱️ 平局（达到最大回合数）")

            # 更新玩家状态
            player.hp = max(0, player_hp)
            player.spiritual_power = max(0, player_sp)
            player.last_pve_battle = datetime.now()

            # 计算奖励
            rewards = {}
            if result == BattleResult.WIN:
                # 修为奖励
                exp_reward = monster.exp_reward
                rewards["exp"] = exp_reward
                player.cultivation_exp += exp_reward

                # 灵石奖励
                spirit_stones = random.randint(monster.spirit_stones_min, monster.spirit_stones_max)
                rewards["spirit_stones"] = spirit_stones
                player.spirit_stones += spirit_stones

                # 更新统计
                player.total_battles += 1
                player.total_wins += 1
                player.total_kills += 1

                battle_log.append(f"获得 {exp_reward} 修为，{spirit_stones} 灵石")
            else:
                player.total_battles += 1

            # 记录战斗
            battle_record = BattleRecord(
                battle_type=BattleType.PVE,
                player_id=player.id,
                monster_id=monster.id,
                player_hp_before=player.hp,
                player_hp_after=max(0, player_hp),
                opponent_hp_before=monster.hp,
                opponent_hp_after=max(0, monster_hp),
                rounds=round_num,
                result=result,
                exp_gained=rewards.get("exp", 0),
                spirit_stones_gained=rewards.get("spirit_stones", 0),
            )
            db.add(battle_record)

            await db.commit()

            return result, battle_log, rewards

        finally:
            # 清除战斗状态
            player.is_in_battle = False
            await db.commit()

    @staticmethod
    async def battle_pvp(
        db: AsyncSession,
        attacker: Player,
        defender: Player
    ) -> Tuple[BattleResult, List[str], Dict]:
        """PVP战斗

        Returns:
            (result, battle_log, rewards)
        """
        # 设置战斗状态
        attacker.is_in_battle = True
        defender.is_in_battle = True
        await db.commit()

        try:
            # 复制属性用于战斗
            attacker_hp = attacker.hp
            attacker_sp = attacker.spiritual_power
            defender_hp = defender.hp
            defender_sp = defender.spiritual_power

            battle_log = []
            battle_log.append(f"⚔️ {attacker.nickname} VS {defender.nickname}")
            battle_log.append(f"💚 {attacker.nickname}: {attacker_hp}/{attacker.max_hp} | 💙灵力: {attacker_sp}/{attacker.max_spiritual_power}")
            battle_log.append(f"💚 {defender.nickname}: {defender_hp}/{defender.max_hp} | 💙灵力: {defender_sp}/{defender.max_spiritual_power}")
            battle_log.append(f"📋 {attacker.nickname} 策略: {BattleStrategy(attacker.battle_strategy).name}")
            battle_log.append(f"📋 {defender.nickname} 策略: {BattleStrategy(defender.battle_strategy).name}")
            battle_log.append("---")

            # 解析战斗策略
            try:
                attacker_strategy = BattleStrategy(attacker.battle_strategy)
            except:
                attacker_strategy = BattleStrategy.BALANCED

            try:
                defender_strategy = BattleStrategy(defender.battle_strategy)
            except:
                defender_strategy = BattleStrategy.BALANCED

            # 战斗回合
            round_num = 0
            max_rounds = settings.MAX_BATTLE_ROUNDS

            while attacker_hp > 0 and defender_hp > 0 and round_num < max_rounds:
                round_num += 1
                battle_log.append(f"\n第 {round_num} 回合：")

                # 根据速度决定谁先攻击
                attacker_first = attacker.speed >= defender.speed

                if attacker_first:
                    # 攻击方先攻击 - 使用AI选择
                    attacker_skills = await BattleService._get_player_available_skills(db, attacker, attacker_sp)
                    action_type, skill_tuple, reason = BattleAI.select_action(
                        player=attacker,
                        available_skills=attacker_skills,
                        strategy=attacker_strategy,
                        current_hp=attacker_hp,
                        current_sp=attacker_sp,
                        opponent_hp=defender_hp,
                        opponent_max_hp=defender.max_hp,
                        round_num=round_num
                    )

                    if action_type == "skill" and skill_tuple:
                        player_skill, skill = skill_tuple
                        damage, is_crit, effect_desc = await SkillService.calculate_skill_damage(
                            caster=attacker,
                            skill=skill,
                            target_defense=defender.defense,
                            skill_level=player_skill.skill_level
                        )
                        attacker_sp -= skill.spiritual_cost
                        defender_hp -= damage
                        crit_text = "💥暴击！" if is_crit else ""
                        battle_log.append(f"  ✨ {attacker.nickname} 施放 [{skill.name}] 造成 {damage} 伤害 {crit_text}")
                    else:
                        damage, is_crit = BattleService._calculate_damage(
                            attacker.attack, defender.defense, attacker.crit_rate, attacker.crit_damage
                        )
                        defender_hp -= damage
                        crit_text = "💥暴击！" if is_crit else ""
                        battle_log.append(f"  🗡️ {attacker.nickname} 普通攻击造成 {damage} 伤害 {crit_text}")

                    if defender_hp <= 0:
                        break

                    # 防守方反击 - 使用AI选择
                    defender_skills = await BattleService._get_player_available_skills(db, defender, defender_sp)
                    action_type, skill_tuple, reason = BattleAI.select_action(
                        player=defender,
                        available_skills=defender_skills,
                        strategy=defender_strategy,
                        current_hp=defender_hp,
                        current_sp=defender_sp,
                        opponent_hp=attacker_hp,
                        opponent_max_hp=attacker.max_hp,
                        round_num=round_num
                    )

                    if action_type == "skill" and skill_tuple:
                        player_skill, skill = skill_tuple
                        damage, is_crit, effect_desc = await SkillService.calculate_skill_damage(
                            caster=defender,
                            skill=skill,
                            target_defense=attacker.defense,
                            skill_level=player_skill.skill_level
                        )
                        defender_sp -= skill.spiritual_cost
                        attacker_hp -= damage
                        crit_text = "💥暴击！" if is_crit else ""
                        battle_log.append(f"  ✨ {defender.nickname} 施放 [{skill.name}] 造成 {damage} 伤害 {crit_text}")
                    else:
                        damage, is_crit = BattleService._calculate_damage(
                            defender.attack, attacker.defense, defender.crit_rate, defender.crit_damage
                        )
                        attacker_hp -= damage
                        crit_text = "💥暴击！" if is_crit else ""
                        battle_log.append(f"  🛡️ {defender.nickname} 反击造成 {damage} 伤害 {crit_text}")
                else:
                    # 防守方先攻击 - 使用AI选择
                    defender_skills = await BattleService._get_player_available_skills(db, defender, defender_sp)
                    action_type, skill_tuple, reason = BattleAI.select_action(
                        player=defender,
                        available_skills=defender_skills,
                        strategy=defender_strategy,
                        current_hp=defender_hp,
                        current_sp=defender_sp,
                        opponent_hp=attacker_hp,
                        opponent_max_hp=attacker.max_hp,
                        round_num=round_num
                    )

                    if action_type == "skill" and skill_tuple:
                        player_skill, skill = skill_tuple
                        damage, is_crit, effect_desc = await SkillService.calculate_skill_damage(
                            caster=defender,
                            skill=skill,
                            target_defense=attacker.defense,
                            skill_level=player_skill.skill_level
                        )
                        defender_sp -= skill.spiritual_cost
                        attacker_hp -= damage
                        crit_text = "💥暴击！" if is_crit else ""
                        battle_log.append(f"  ✨ {defender.nickname} 施放 [{skill.name}] 造成 {damage} 伤害 {crit_text}")
                    else:
                        damage, is_crit = BattleService._calculate_damage(
                            defender.attack, attacker.defense, defender.crit_rate, defender.crit_damage
                        )
                        attacker_hp -= damage
                        crit_text = "💥暴击！" if is_crit else ""
                        battle_log.append(f"  🛡️ {defender.nickname} 攻击造成 {damage} 伤害 {crit_text}")

                    if attacker_hp <= 0:
                        break

                    # 攻击方反击 - 使用AI选择
                    attacker_skills = await BattleService._get_player_available_skills(db, attacker, attacker_sp)
                    action_type, skill_tuple, reason = BattleAI.select_action(
                        player=attacker,
                        available_skills=attacker_skills,
                        strategy=attacker_strategy,
                        current_hp=attacker_hp,
                        current_sp=attacker_sp,
                        opponent_hp=defender_hp,
                        opponent_max_hp=defender.max_hp,
                        round_num=round_num
                    )

                    if action_type == "skill" and skill_tuple:
                        player_skill, skill = skill_tuple
                        damage, is_crit, effect_desc = await SkillService.calculate_skill_damage(
                            caster=attacker,
                            skill=skill,
                            target_defense=defender.defense,
                            skill_level=player_skill.skill_level
                        )
                        attacker_sp -= skill.spiritual_cost
                        defender_hp -= damage
                        crit_text = "💥暴击！" if is_crit else ""
                        battle_log.append(f"  ✨ {attacker.nickname} 施放 [{skill.name}] 造成 {damage} 伤害 {crit_text}")
                    else:
                        damage, is_crit = BattleService._calculate_damage(
                            attacker.attack, defender.defense, attacker.crit_rate, attacker.crit_damage
                        )
                        defender_hp -= damage
                        crit_text = "💥暴击！" if is_crit else ""
                        battle_log.append(f"  🗡️ {attacker.nickname} 反击造成 {damage} 伤害 {crit_text}")

            # 判定结果
            if attacker_hp > 0 and defender_hp <= 0:
                result = BattleResult.WIN
                battle_log.append("\n---")
                battle_log.append(f"🎉 {attacker.nickname} 获胜！")
            elif attacker_hp <= 0:
                result = BattleResult.LOSE
                battle_log.append("\n---")
                battle_log.append(f"🎉 {defender.nickname} 获胜！")
            else:
                result = BattleResult.DRAW
                battle_log.append("\n---")
                battle_log.append("⏱️ 平局（达到最大回合数）")

            # 更新玩家状态
            attacker.hp = max(1, attacker_hp)  # PVP不会死亡，至少保留1HP
            attacker.spiritual_power = max(0, attacker_sp)
            defender.hp = max(1, defender_hp)
            defender.spiritual_power = max(0, defender_sp)
            attacker.last_pvp_battle = datetime.now()

            # 计算奖励（胜者获得）
            rewards = {}
            if result == BattleResult.WIN:
                # 修为奖励
                exp_reward = int(defender.cultivation_exp * 0.05)  # 获得对方5%修为
                rewards["exp"] = exp_reward
                attacker.cultivation_exp += exp_reward

                # 荣誉点数（可用于排行榜）
                rewards["honor"] = 10

                # 更新统计
                attacker.total_battles += 1
                attacker.total_wins += 1
                defender.total_battles += 1

                battle_log.append(f"{attacker.nickname} 获得 {exp_reward} 修为")
            elif result == BattleResult.LOSE:
                attacker.total_battles += 1
                defender.total_battles += 1
                defender.total_wins += 1
            else:
                attacker.total_battles += 1
                defender.total_battles += 1

            # 记录战斗
            battle_record = BattleRecord(
                battle_type=BattleType.PVP,
                player_id=attacker.id,
                opponent_id=defender.id,
                player_hp_before=attacker.hp,
                player_hp_after=max(1, attacker_hp),
                opponent_hp_before=defender.hp,
                opponent_hp_after=max(1, defender_hp),
                rounds=round_num,
                result=result,
                exp_gained=rewards.get("exp", 0),
            )
            db.add(battle_record)

            await db.commit()

            return result, battle_log, rewards

        finally:
            # 清除战斗状态
            attacker.is_in_battle = False
            defender.is_in_battle = False
            await db.commit()

    @staticmethod
    def _calculate_damage(
        attack: int,
        defense: int,
        crit_rate: float,
        crit_damage: float
    ) -> Tuple[int, bool]:
        """计算伤害

        Returns:
            (damage, is_crit)
        """
        # 基础伤害
        base_damage = max(1, attack - defense // 2)

        # 随机波动 ±20%
        damage = int(base_damage * random.uniform(0.8, 1.2))

        # 暴击判定
        is_crit = random.random() < crit_rate
        if is_crit:
            damage = int(damage * crit_damage)

        return damage, is_crit

    @staticmethod
    async def get_random_monsters(
        db: AsyncSession,
        player: Player,
        count: int = 5
    ) -> List[Monster]:
        """获取适合玩家等级的随机怪物"""
        # 根据玩家境界获取怪物
        result = await db.execute(
            select(Monster).where(
                Monster.realm == player.realm.value
            ).limit(count * 2)  # 多查询一些用于随机
        )
        all_monsters = result.scalars().all()

        if not all_monsters:
            return []

        # 随机选择
        selected = random.sample(all_monsters, min(count, len(all_monsters)))
        return selected
