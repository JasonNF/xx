"""世界BOSS服务"""
import random
from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Player, WorldBoss, WorldBossParticipation, WorldBossTemplate, WorldBossStatus, Item


class WorldBossService:
    """世界BOSS服务类"""

    # BOSS配置
    BOSS_DURATION_HOURS = 2  # BOSS存在时长(2小时)
    MAX_ATTACKS_PER_PLAYER = 10  # 每个玩家最多攻击次数
    FINAL_KILLER_BONUS = 1.5  # 最后一击奖励倍数
    TOP_DAMAGER_BONUS = 1.3  # 伤害第一奖励倍数

    @staticmethod
    async def spawn_boss(db: AsyncSession) -> Tuple[bool, str, Optional[WorldBoss]]:
        """生成世界BOSS

        Returns:
            (是否成功, 消息, BOSS实例)
        """
        # 检查是否已有活跃的BOSS
        result = await db.execute(
            select(WorldBoss).where(WorldBoss.status == WorldBossStatus.ACTIVE)
        )
        existing_boss = result.scalar_one_or_none()

        if existing_boss:
            return False, "已有世界BOSS存在", existing_boss

        # 获取所有启用的模板
        result = await db.execute(
            select(WorldBossTemplate).where(WorldBossTemplate.is_active == True)
        )
        templates = result.scalars().all()

        if not templates:
            return False, "无可用的BOSS模板", None

        # 根据权重随机选择模板
        weights = [t.spawn_weight for t in templates]
        template = random.choices(templates, weights=weights, k=1)[0]

        # 生成BOSS
        now = datetime.now()
        despawn_time = now + timedelta(hours=WorldBossService.BOSS_DURATION_HOURS)

        # 随机生成奖励池
        reward_stones = random.randint(template.reward_stones_min, template.reward_stones_max)
        reward_exp = random.randint(template.reward_exp_min, template.reward_exp_max)

        boss = WorldBoss(
            name=template.name,
            description=template.description,
            level=template.level,
            max_hp=template.base_hp,
            current_hp=template.base_hp,
            attack=template.base_attack,
            defense=template.base_defense,
            status=WorldBossStatus.ACTIVE,
            total_reward_stones=reward_stones,
            total_reward_exp=reward_exp,
            spawned_at=now,
            despawn_at=despawn_time
        )

        db.add(boss)
        await db.commit()
        await db.refresh(boss)

        message = f"""🐉 世界BOSS降临！

名称: {boss.name}
等级: {boss.level}
血量: {boss.current_hp:,}
攻击: {boss.attack}
防御: {boss.defense}

奖励池:
💎 灵石: {boss.total_reward_stones:,}
✨ 经验: {boss.total_reward_exp:,}

⏰ 将在 {despawn_time.strftime('%H:%M')} 消失
💡 使用 /攻击BOSS 参与战斗！"""

        return True, message, boss

    @staticmethod
    async def attack_boss(
        db: AsyncSession,
        player: Player,
        boss_id: int
    ) -> Tuple[bool, str, Optional[Dict]]:
        """攻击世界BOSS

        Returns:
            (是否成功, 消息, 结果数据)
        """
        # 获取BOSS
        result = await db.execute(select(WorldBoss).where(WorldBoss.id == boss_id))
        boss = result.scalar_one_or_none()

        if not boss:
            return False, "BOSS不存在", None

        if boss.status != WorldBossStatus.ACTIVE:
            return False, f"BOSS已{boss.status.value}", None

        # 检查是否超时
        if datetime.now() > boss.despawn_at:
            boss.status = WorldBossStatus.ESCAPED
            await db.commit()
            return False, "BOSS已逃跑", None

        # 获取或创建参与记录
        result = await db.execute(
            select(WorldBossParticipation).where(
                and_(
                    WorldBossParticipation.boss_id == boss_id,
                    WorldBossParticipation.player_id == player.id
                )
            )
        )
        participation = result.scalar_one_or_none()

        if not participation:
            participation = WorldBossParticipation(
                boss_id=boss_id,
                player_id=player.id
            )
            db.add(participation)

        # 检查攻击次数限制
        if participation.attack_count >= WorldBossService.MAX_ATTACKS_PER_PLAYER:
            return False, f"今日攻击次数已用完({WorldBossService.MAX_ATTACKS_PER_PLAYER}次)", None

        # 计算伤害
        player_power = player.combat_power
        boss_defense = boss.defense

        # 基础伤害 = 玩家战力 * (1 - 防御减伤率)
        defense_reduction = min(0.8, boss_defense / (boss_defense + player_power))
        base_damage = int(player_power * (1 - defense_reduction))

        # 随机波动 ±20%
        damage = int(base_damage * random.uniform(0.8, 1.2))
        damage = max(1, damage)  # 至少造成1点伤害

        # 更新BOSS血量
        boss.current_hp = max(0, boss.current_hp - damage)

        # 更新参与记录
        participation.total_damage += damage
        participation.attack_count += 1

        # 判断是否击败BOSS
        is_defeated = boss.current_hp <= 0
        if is_defeated:
            boss.status = WorldBossStatus.DEFEATED
            boss.defeated_at = datetime.now()
            boss.final_killer_id = player.id

            # 分配奖励
            await WorldBossService._distribute_rewards(db, boss)

        await db.commit()

        # 构建结果消息
        result_data = {
            "damage": damage,
            "boss_current_hp": boss.current_hp,
            "boss_max_hp": boss.max_hp,
            "total_damage": participation.total_damage,
            "attack_count": participation.attack_count,
            "remaining_attacks": WorldBossService.MAX_ATTACKS_PER_PLAYER - participation.attack_count,
            "is_defeated": is_defeated
        }

        if is_defeated:
            message = f"⚔️ 造成伤害: {damage:,}\n\n🎉 BOSS已被击败！"
        else:
            hp_percent = (boss.current_hp / boss.max_hp) * 100
            message = f"""⚔️ 造成伤害: {damage:,}

BOSS状态:
❤️ 剩余血量: {boss.current_hp:,}/{boss.max_hp:,} ({hp_percent:.1f}%)

你的战绩:
总伤害: {participation.total_damage:,}
攻击次数: {participation.attack_count}/{WorldBossService.MAX_ATTACKS_PER_PLAYER}"""

        return True, message, result_data

    @staticmethod
    async def _distribute_rewards(db: AsyncSession, boss: WorldBoss):
        """分配奖励(内部方法)"""
        # 获取所有参与者,按伤害排序
        result = await db.execute(
            select(WorldBossParticipation).where(
                WorldBossParticipation.boss_id == boss.id
            ).order_by(WorldBossParticipation.total_damage.desc())
        )
        participants = result.scalars().all()

        if not participants:
            return

        # 计算总伤害
        total_damage = sum(p.total_damage for p in participants)
        if total_damage == 0:
            return

        # 获取最后一击玩家和伤害第一玩家
        final_killer_id = boss.final_killer_id
        top_damager_id = participants[0].player_id

        # 按伤害比例分配奖励
        for participation in participants:
            # 基础奖励(按伤害比例)
            damage_ratio = participation.total_damage / total_damage
            base_stones = int(boss.total_reward_stones * damage_ratio)
            base_exp = int(boss.total_reward_exp * damage_ratio)

            # 额外奖励
            bonus_multiplier = 1.0

            # 最后一击奖励
            if participation.player_id == final_killer_id:
                bonus_multiplier = WorldBossService.FINAL_KILLER_BONUS
            # 伤害第一奖励
            elif participation.player_id == top_damager_id:
                bonus_multiplier = WorldBossService.TOP_DAMAGER_BONUS

            # 计算最终奖励
            participation.reward_stones = int(base_stones * bonus_multiplier)
            participation.reward_exp = int(base_exp * bonus_multiplier)
            participation.is_rewarded = True

            # 发放奖励给玩家
            result = await db.execute(select(Player).where(Player.id == participation.player_id))
            player = result.scalar_one_or_none()
            if player:
                player.spirit_stones += participation.reward_stones
                player.cultivation_exp += participation.reward_exp

        await db.commit()

    @staticmethod
    async def get_boss_status(db: AsyncSession) -> Optional[Dict]:
        """获取当前活跃的BOSS状态"""
        result = await db.execute(
            select(WorldBoss).where(WorldBoss.status == WorldBossStatus.ACTIVE)
        )
        boss = result.scalar_one_or_none()

        if not boss:
            return None

        # 检查是否超时
        if datetime.now() > boss.despawn_at:
            boss.status = WorldBossStatus.ESCAPED
            await db.commit()
            return None

        # 获取参与人数
        result = await db.execute(
            select(func.count(WorldBossParticipation.id)).where(
                WorldBossParticipation.boss_id == boss.id
            )
        )
        participant_count = result.scalar() or 0

        # 计算剩余时间
        time_remaining = boss.despawn_at - datetime.now()
        minutes_remaining = int(time_remaining.total_seconds() / 60)

        hp_percent = (boss.current_hp / boss.max_hp) * 100

        return {
            "id": boss.id,
            "name": boss.name,
            "description": boss.description,
            "level": boss.level,
            "current_hp": boss.current_hp,
            "max_hp": boss.max_hp,
            "hp_percent": hp_percent,
            "attack": boss.attack,
            "defense": boss.defense,
            "participant_count": participant_count,
            "minutes_remaining": minutes_remaining,
            "total_reward_stones": boss.total_reward_stones,
            "total_reward_exp": boss.total_reward_exp,
            "spawned_at": boss.spawned_at
        }

    @staticmethod
    async def get_damage_rankings(
        db: AsyncSession,
        boss_id: int,
        limit: int = 20
    ) -> List[Dict]:
        """获取伤害排行榜"""
        result = await db.execute(
            select(WorldBossParticipation, Player).join(
                Player, Player.id == WorldBossParticipation.player_id
            ).where(
                WorldBossParticipation.boss_id == boss_id
            ).order_by(WorldBossParticipation.total_damage.desc()).limit(limit)
        )
        rankings = result.all()

        rankings_list = []
        for idx, (participation, player) in enumerate(rankings, 1):
            rankings_list.append({
                "rank": idx,
                "player_id": player.id,
                "nickname": player.nickname,
                "realm": player.full_realm_name,
                "total_damage": participation.total_damage,
                "attack_count": participation.attack_count,
                "reward_stones": participation.reward_stones if participation.is_rewarded else 0,
                "reward_exp": participation.reward_exp if participation.is_rewarded else 0,
                "is_rewarded": participation.is_rewarded
            })

        return rankings_list

    @staticmethod
    async def get_player_participation(
        db: AsyncSession,
        player_id: int,
        boss_id: int
    ) -> Optional[Dict]:
        """获取玩家参与情况"""
        result = await db.execute(
            select(WorldBossParticipation).where(
                and_(
                    WorldBossParticipation.boss_id == boss_id,
                    WorldBossParticipation.player_id == player_id
                )
            )
        )
        participation = result.scalar_one_or_none()

        if not participation:
            return None

        return {
            "total_damage": participation.total_damage,
            "attack_count": participation.attack_count,
            "remaining_attacks": WorldBossService.MAX_ATTACKS_PER_PLAYER - participation.attack_count,
            "reward_stones": participation.reward_stones,
            "reward_exp": participation.reward_exp,
            "is_rewarded": participation.is_rewarded
        }

    @staticmethod
    async def cleanup_old_bosses(db: AsyncSession):
        """清理过期的BOSS记录(调度任务)"""
        # 将超时的BOSS标记为逃跑
        result = await db.execute(
            select(WorldBoss).where(
                and_(
                    WorldBoss.status == WorldBossStatus.ACTIVE,
                    WorldBoss.despawn_at < datetime.now()
                )
            )
        )
        expired_bosses = result.scalars().all()

        for boss in expired_bosses:
            boss.status = WorldBossStatus.ESCAPED

        await db.commit()
