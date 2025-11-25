"""秘境探索服务 - 凡人修仙传版本"""
import random
from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import (
    Player, SecretRealm, RealmExploration, ExplorationReward,
    RealmLootPool, RealmEvent, RealmStatus, Item, Monster
)


class RealmService:
    """秘境探索服务"""

    @staticmethod
    async def get_available_realms(db: AsyncSession, player: Player) -> List[Dict]:
        """获取玩家可进入的秘境列表"""
        result = await db.execute(
            select(SecretRealm).where(
                SecretRealm.status.in_([RealmStatus.OPEN, RealmStatus.PERMANENT])
            )
        )
        realms = result.scalars().all()

        available_realms = []
        for realm in realms:
            # 检查境界要求
            can_enter, reason = await RealmService.can_enter_realm(db, player, realm)

            available_realms.append({
                "id": realm.id,
                "name": realm.name,
                "description": realm.description,
                "difficulty": realm.difficulty.value,
                "realm_type": realm.realm_type.value,
                "min_realm_requirement": realm.min_realm_requirement,
                "entry_cost": realm.entry_cost,
                "duration_minutes": realm.duration_minutes,
                "danger_level": realm.danger_level,
                "can_enter": can_enter,
                "reason": reason if not can_enter else "",
                "current_players": realm.current_players,
                "max_players": realm.max_players,
            })

        return available_realms

    @staticmethod
    async def can_enter_realm(
        db: AsyncSession,
        player: Player,
        realm: SecretRealm
    ) -> Tuple[bool, str]:
        """检查是否可以进入秘境"""
        # 检查是否在修炼或战斗中
        if player.is_cultivating:
            return False, "修炼中无法探索秘境"
        if player.is_in_battle:
            return False, "战斗中无法探索秘境"

        # 检查境界要求
        if realm.min_realm_requirement:
            # 简化版：检查境界名称
            if realm.min_realm_requirement not in player.full_realm_name:
                # 更复杂的境界比较逻辑可以后续优化
                pass

        # 检查等级要求
        if player.realm_level < realm.min_level:
            return False, f"需要达到{realm.min_realm_requirement}"

        # 检查灵石是否足够
        if player.spirit_stones < realm.entry_cost:
            return False, f"灵石不足({player.spirit_stones}/{realm.entry_cost})"

        # 检查人数限制
        if realm.max_players > 0 and realm.current_players >= realm.max_players:
            return False, "秘境人数已满"

        # 检查冷却时间
        result = await db.execute(
            select(RealmExploration)
            .where(
                RealmExploration.player_id == player.id,
                RealmExploration.realm_id == realm.id,
                RealmExploration.status == "completed"
            )
            .order_by(RealmExploration.completed_at.desc())
            .limit(1)
        )
        last_exploration = result.scalar_one_or_none()

        if last_exploration and last_exploration.completed_at:
            cooldown = timedelta(hours=realm.cooldown_hours)
            time_passed = datetime.now() - last_exploration.completed_at
            if time_passed < cooldown:
                remaining = cooldown - time_passed
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                return False, f"冷却中，还需{hours}小时{minutes}分钟"

        # 检查生命值
        if player.hp < player.max_hp * 0.5:
            return False, "生命值不足50%，建议恢复后再进入"

        return True, ""

    @staticmethod
    async def start_exploration(
        db: AsyncSession,
        player: Player,
        realm: SecretRealm
    ) -> Tuple[bool, str, Optional[RealmExploration]]:
        """开始探索秘境

        Returns:
            (success, message, exploration)
        """
        # 检查是否可以进入
        can_enter, reason = await RealmService.can_enter_realm(db, player, realm)
        if not can_enter:
            return False, reason, None

        # 扣除灵石
        player.spirit_stones -= realm.entry_cost

        # 增加秘境当前人数
        if realm.max_players > 0:
            realm.current_players += 1

        # 创建探索记录
        exploration = RealmExploration(
            player_id=player.id,
            realm_id=realm.id,
            status="exploring",
            started_at=datetime.now(),
            hp_remaining=player.hp,
            spiritual_remaining=player.spiritual_power,
        )
        db.add(exploration)
        await db.commit()
        await db.refresh(exploration)

        return True, f"成功进入{realm.name}！探索时长：{realm.duration_minutes}分钟", exploration

    @staticmethod
    async def simulate_exploration(
        db: AsyncSession,
        player: Player,
        realm: SecretRealm,
        exploration: RealmExploration
    ) -> Dict:
        """模拟秘境探索过程 (简化版，一次性完成)

        Returns:
            exploration_result包含战斗记录、奖励等
        """
        # 初始化
        current_hp = player.hp
        current_spiritual = player.spiritual_power
        battle_log = []
        rewards_obtained = []

        # 模拟探索房间数 (3-8个房间)
        total_rooms = random.randint(3, 8)
        rooms_explored = 0
        battles_won = 0
        monsters_killed = 0

        battle_log.append(f"🏛️ 进入{realm.name}...")
        battle_log.append(f"📊 探索目标：{total_rooms}个区域\n")

        # 逐个房间探索
        for room_num in range(1, total_rooms + 1):
            if current_hp <= 0:
                battle_log.append("💀 生命值耗尽，探索失败！")
                break

            rooms_explored += 1
            battle_log.append(f"\n🚪 第{room_num}个区域：")

            # 随机事件 (60%遭遇战, 30%宝箱, 10%陷阱)
            event_roll = random.random()

            if event_roll < 0.6:  # 遭遇战
                # 随机选择怪物 (简化版)
                result = await db.execute(select(Monster).order_by(Monster.level))
                monsters = result.scalars().all()
                if monsters:
                    monster = random.choice(monsters)
                    battle_log.append(f"⚔️ 遭遇 {monster.name}！")

                    # 简化战斗 (基于战力差距)
                    player_power = player.combat_power
                    monster_power = monster.attack * 10 + monster.hp

                    if player_power > monster_power * 0.8:
                        # 战斗胜利
                        damage_taken = random.randint(10, 50)
                        current_hp -= damage_taken
                        battles_won += 1
                        monsters_killed += 1

                        # 获得奖励
                        stones_drop = random.randint(monster.spirit_stones_min, monster.spirit_stones_max)
                        exp_gain = monster.exp_reward

                        battle_log.append(f"  ✅ 胜利！损失{damage_taken}生命值")
                        battle_log.append(f"  💰 获得 {stones_drop} 灵石")
                        battle_log.append(f"  ⭐ 获得 {exp_gain} 修为")

                        rewards_obtained.append({
                            "type": "battle",
                            "spirit_stones": stones_drop,
                            "exp": exp_gain,
                        })
                    else:
                        # 战斗失败
                        damage_taken = random.randint(50, 150)
                        current_hp -= damage_taken
                        battle_log.append(f"  ❌ 战败！损失{damage_taken}生命值")

            elif event_roll < 0.9:  # 宝箱
                battle_log.append("📦 发现宝箱！")
                # 随机掉落秘境物品
                result = await db.execute(
                    select(RealmLootPool, Item)
                    .join(Item, RealmLootPool.item_id == Item.id)
                    .where(RealmLootPool.realm_id == realm.id)
                    .limit(3)
                )
                loot_items = result.all()

                if loot_items:
                    for loot_pool, item in loot_items:
                        if random.random() < loot_pool.drop_rate:
                            quantity = random.randint(loot_pool.min_quantity, loot_pool.max_quantity)
                            battle_log.append(f"  ✨ 获得 {item.name} x{quantity}")

                            # 记录奖励
                            reward = ExplorationReward(
                                exploration_id=exploration.id,
                                item_id=item.id,
                                quantity=quantity,
                                obtained_from="chest",
                                room_number=room_num,
                            )
                            db.add(reward)

            else:  # 陷阱
                damage = random.randint(20, 80)
                current_hp -= damage
                battle_log.append(f"⚠️ 触发陷阱！损失{damage}生命值")

        # 计算最终结果
        exploration.rooms_explored = rooms_explored
        exploration.battles_won = battles_won
        exploration.monsters_killed = monsters_killed
        exploration.hp_remaining = max(0, current_hp)
        exploration.spiritual_remaining = max(0, current_spiritual)

        # 计算奖励
        total_exp = sum(r.get("exp", 0) for r in rewards_obtained)
        total_stones = sum(r.get("spirit_stones", 0) for r in rewards_obtained)

        exploration.total_exp_gained = total_exp + realm.base_exp_reward
        exploration.total_spirit_stones = total_stones + realm.base_spirit_stones

        # 完成探索
        if current_hp > 0:
            exploration.status = "completed"
            exploration.completion_rating = RealmService._calculate_rating(
                rooms_explored, total_rooms, battles_won
            )
            battle_log.append(f"\n✅ 探索完成！评价：{exploration.completion_rating}")
        else:
            exploration.status = "failed"
            exploration.completion_rating = "F"
            battle_log.append(f"\n💀 探索失败！")

        exploration.completed_at = datetime.now()

        # 减少秘境人数
        if realm.max_players > 0:
            realm.current_players = max(0, realm.current_players - 1)

        await db.commit()

        return {
            "success": exploration.status == "completed",
            "battle_log": battle_log,
            "exploration": exploration,
            "rewards": {
                "exp": exploration.total_exp_gained,
                "spirit_stones": exploration.total_spirit_stones,
                "rating": exploration.completion_rating,
            }
        }

    @staticmethod
    def _calculate_rating(rooms_explored: int, total_rooms: int, battles_won: int) -> str:
        """计算探索评价"""
        completion_rate = rooms_explored / total_rooms if total_rooms > 0 else 0

        if completion_rate >= 1.0 and battles_won >= 4:
            return "S"
        elif completion_rate >= 0.8 and battles_won >= 3:
            return "A"
        elif completion_rate >= 0.6 and battles_won >= 2:
            return "B"
        elif completion_rate >= 0.4:
            return "C"
        else:
            return "D"
