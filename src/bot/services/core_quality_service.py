"""金丹品质服务"""
import random
from datetime import datetime
from typing import Tuple, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Player, Item
from bot.models.core_quality import (
    PlayerCore, CoreFormationAttempt, CoreRefinementRecord,
    CoreQualityGrade
)


class CoreQualityService:
    """金丹品质服务类"""

    # 品质等级对应的阈值
    QUALITY_THRESHOLDS = {
        CoreQualityGrade.INFERIOR: (0, 20),
        CoreQualityGrade.LOW: (21, 40),
        CoreQualityGrade.MEDIUM: (41, 60),
        CoreQualityGrade.HIGH: (61, 80),
        CoreQualityGrade.SUPERIOR: (81, 90),
        CoreQualityGrade.PERFECT: (91, 100),
    }

    @staticmethod
    def get_quality_grade(quality: int) -> CoreQualityGrade:
        """根据品质值获取品质等级"""
        for grade, (min_q, max_q) in CoreQualityService.QUALITY_THRESHOLDS.items():
            if min_q <= quality <= max_q:
                return grade
        return CoreQualityGrade.INFERIOR

    @staticmethod
    def calculate_quality_bonuses(quality: int) -> Dict:
        """根据品质计算各项加成"""
        # 修炼速度加成: 每点品质 +0.5%
        cultivation_bonus = quality * 0.005

        # 属性加成: 随品质线性增长
        attack_bonus = quality * 2
        defense_bonus = quality * 2
        hp_bonus = quality * 10
        spiritual_power_bonus = quality * 5

        return {
            "cultivation_speed_bonus": cultivation_bonus,
            "attack_bonus": attack_bonus,
            "defense_bonus": defense_bonus,
            "hp_bonus": hp_bonus,
            "spiritual_power_bonus": spiritual_power_bonus
        }

    @staticmethod
    async def get_player_core(
        db: AsyncSession,
        player: Player
    ) -> Optional[PlayerCore]:
        """获取玩家金丹记录"""
        result = await db.execute(
            select(PlayerCore).where(PlayerCore.player_id == player.id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def attempt_core_formation(
        db: AsyncSession,
        player: Player,
        pill_item_id: Optional[int] = None
    ) -> Tuple[bool, str, Dict]:
        """尝试结丹

        Args:
            db: 数据库会话
            player: 玩家
            pill_item_id: 使用的结丹丹药ID（可选）

        Returns:
            (是否成功, 消息, 结果数据)
        """
        # 检查是否已经结丹
        existing_core = await CoreQualityService.get_player_core(db, player)
        if existing_core:
            return False, "您已经结丹成功", {}

        # 检查境界（必须是筑基期大圆满）
        from bot.models import RealmType
        if player.realm != RealmType.FOUNDATION or player.realm_level < 2:
            return False, "需要达到筑基后期才能尝试结丹", {}

        # 基础成功率 50%
        base_success_rate = 0.5

        # 修为影响（修为越高成功率越高，最多+20%）
        cultivation_bonus = min(player.cultivation / 1000000, 0.2)

        # 悟性影响（最多+15%）
        comprehension_bonus = player.comprehension * 0.0015

        # 灵根影响
        spirit_root_bonus = 0.0
        if player.spirit_root:
            spirit_root_bonus = player.spirit_root.cultivation_speed_bonus * 0.1

        # 丹药影响
        pill_quality = 0
        pill_bonus = 0.0
        if pill_item_id:
            # 这里假设使用了结丹丹药,可以提升成功率和品质
            # 实际应该从Item表中获取丹药信息
            pill_quality = 70  # 假设丹药品质
            pill_bonus = 0.15  # 丹药提升成功率15%

        # 总成功率
        success_rate = base_success_rate + cultivation_bonus + comprehension_bonus + spirit_root_bonus + pill_bonus
        success_rate = max(0.3, min(0.95, success_rate))  # 限制在30%-95%之间

        # 判定成功
        is_success = random.random() < success_rate

        # 记录尝试
        attempt = CoreFormationAttempt(
            player_id=player.id,
            cultivation_level=player.realm_level,
            pill_used_id=pill_item_id,
            pill_quality=pill_quality,
            is_success=is_success,
            failure_reason="心境不稳，冲击失败" if not is_success else None
        )
        db.add(attempt)

        result_data = {
            "success_rate": success_rate,
            "is_success": is_success
        }

        if is_success:
            # 计算金丹品质
            quality = await CoreQualityService.calculate_core_quality(
                player, pill_quality
            )

            attempt.core_quality = quality

            # 创建金丹记录
            bonuses = CoreQualityService.calculate_quality_bonuses(quality)
            grade = CoreQualityService.get_quality_grade(quality)

            # 检查是否形成道纹（完美金丹才有可能）
            has_dao_pattern = False
            dao_pattern_count = 0
            if grade == CoreQualityGrade.PERFECT:
                # 10%几率产生道纹
                if random.random() < 0.1:
                    has_dao_pattern = True
                    dao_pattern_count = random.randint(1, 3)  # 1-3道纹

            player_core = PlayerCore(
                player_id=player.id,
                quality=quality,
                grade=grade.value,
                formation_cultivation=player.cultivation,
                pill_quality=pill_quality,
                cultivation_speed_bonus=bonuses["cultivation_speed_bonus"],
                attack_bonus=bonuses["attack_bonus"],
                defense_bonus=bonuses["defense_bonus"],
                hp_bonus=bonuses["hp_bonus"],
                spiritual_power_bonus=bonuses["spiritual_power_bonus"],
                has_dao_pattern=has_dao_pattern,
                dao_pattern_count=dao_pattern_count
            )
            db.add(player_core)

            # 应用金丹加成
            player.attack += bonuses["attack_bonus"]
            player.defense += bonuses["defense_bonus"]
            player.max_hp += bonuses["hp_bonus"]
            player.hp = player.max_hp
            player.max_spiritual_power += bonuses["spiritual_power_bonus"]
            player.spiritual_power = player.max_spiritual_power

            # 突破到结丹期
            from bot.models import RealmType
            player.realm = RealmType.CORE_FORMATION
            player.realm_level = 0
            player.cultivation_exp = 0

            result_data.update({
                "quality": quality,
                "grade": grade.value,
                "has_dao_pattern": has_dao_pattern,
                "dao_pattern_count": dao_pattern_count,
                "bonuses": bonuses
            })

        await db.commit()

        if is_success:
            return True, "结丹成功！", result_data
        else:
            return False, "结丹失败，请调整状态后再次尝试", result_data

    @staticmethod
    async def calculate_core_quality(
        player: Player,
        pill_quality: int
    ) -> int:
        """计算金丹品质

        品质由以下因素决定:
        - 筑基期修为（0-30分）
        - 使用丹药品质（0-30分）
        - 悟性（0-20分）
        - 灵根（0-15分）
        - 随机波动（-5到+5分）
        """
        quality = 0

        # 1. 修为影响（最高30分）
        # 假设筑基期满修为是500万
        cultivation_score = min(player.cultivation / 5000000 * 30, 30)
        quality += int(cultivation_score)

        # 2. 丹药品质（最高30分）
        pill_score = pill_quality * 0.3
        quality += int(pill_score)

        # 3. 悟性（最高20分）
        comprehension_score = player.comprehension * 0.2
        quality += int(comprehension_score)

        # 4. 灵根（最高15分）
        if player.spirit_root:
            # 单灵根15分，双灵根12分，三灵根9分，以此类推
            root_count = len(player.spirit_root.roots.split(","))
            if root_count == 1:
                quality += 15
            elif root_count == 2:
                quality += 12
            elif root_count == 3:
                quality += 9
            elif root_count == 4:
                quality += 6
            else:
                quality += 3

        # 5. 随机波动
        quality += random.randint(-5, 5)

        # 确保品质在0-100范围内
        quality = max(0, min(100, quality))

        return quality

    @staticmethod
    async def refine_core(
        db: AsyncSession,
        player: Player,
        method: str,
        material_item_id: Optional[int] = None,
        risk_level: int = 1
    ) -> Tuple[bool, str, Dict]:
        """祭炼金丹提升品质

        Args:
            db: 数据库会话
            player: 玩家
            method: 祭炼方法
            material_item_id: 使用的材料ID
            risk_level: 风险等级（1-10，越高提升越大但失败概率也越大）

        Returns:
            (是否成功, 消息, 结果数据)
        """
        # 获取金丹记录
        player_core = await CoreQualityService.get_player_core(db, player)
        if not player_core:
            return False, "您还未结丹", {}

        # 检查是否已经完美
        if player_core.quality >= 100:
            return False, "金丹已达完美品质，无法继续提升", {}

        # 基础成功率：70% - (风险等级 * 5%)
        success_rate = 0.7 - (risk_level * 0.05)
        success_rate = max(0.1, success_rate)  # 最低10%

        # 判定成功
        is_success = random.random() < success_rate

        quality_before = player_core.quality

        if is_success:
            # 成功：品质提升 = 风险等级 * (1-3)
            quality_gain = risk_level * random.randint(1, 3)
            new_quality = min(100, quality_before + quality_gain)

            # 更新金丹品质
            player_core.quality = new_quality
            old_grade = player_core.grade
            new_grade = CoreQualityService.get_quality_grade(new_quality)
            player_core.grade = new_grade.value

            # 重新计算并应用加成
            old_bonuses = CoreQualityService.calculate_quality_bonuses(quality_before)
            new_bonuses = CoreQualityService.calculate_quality_bonuses(new_quality)

            # 差值加成
            player.attack += new_bonuses["attack_bonus"] - old_bonuses["attack_bonus"]
            player.defense += new_bonuses["defense_bonus"] - old_bonuses["defense_bonus"]
            player.max_hp += new_bonuses["hp_bonus"] - old_bonuses["hp_bonus"]
            player.max_spiritual_power += new_bonuses["spiritual_power_bonus"] - old_bonuses["spiritual_power_bonus"]

            # 更新金丹加成
            player_core.cultivation_speed_bonus = new_bonuses["cultivation_speed_bonus"]
            player_core.attack_bonus = new_bonuses["attack_bonus"]
            player_core.defense_bonus = new_bonuses["defense_bonus"]
            player_core.hp_bonus = new_bonuses["hp_bonus"]
            player_core.spiritual_power_bonus = new_bonuses["spiritual_power_bonus"]

            # 检查是否升品
            grade_up = old_grade != new_grade.value

            # 检查是否产生道纹
            dao_pattern_gained = False
            if new_grade == CoreQualityGrade.PERFECT and not player_core.has_dao_pattern:
                if random.random() < 0.15:  # 15%几率
                    player_core.has_dao_pattern = True
                    player_core.dao_pattern_count = random.randint(1, 3)
                    dao_pattern_gained = True

            result_data = {
                "is_success": True,
                "quality_before": quality_before,
                "quality_after": new_quality,
                "quality_gain": quality_gain,
                "grade_up": grade_up,
                "new_grade": new_grade.value,
                "dao_pattern_gained": dao_pattern_gained
            }

        else:
            # 失败：根据风险等级可能降低品质
            if risk_level >= 7:
                # 高风险可能导致品质下降
                quality_loss = risk_level * random.randint(1, 2)
                new_quality = max(0, quality_before - quality_loss)

                player_core.quality = new_quality
                new_grade = CoreQualityService.get_quality_grade(new_quality)
                player_core.grade = new_grade.value

                # 重新计算并应用加成
                old_bonuses = CoreQualityService.calculate_quality_bonuses(quality_before)
                new_bonuses = CoreQualityService.calculate_quality_bonuses(new_quality)

                # 差值加成（可能是负数）
                player.attack += new_bonuses["attack_bonus"] - old_bonuses["attack_bonus"]
                player.defense += new_bonuses["defense_bonus"] - old_bonuses["defense_bonus"]
                player.max_hp += new_bonuses["hp_bonus"] - old_bonuses["hp_bonus"]
                player.max_spiritual_power += new_bonuses["spiritual_power_bonus"] - old_bonuses["spiritual_power_bonus"]

                # 更新金丹加成
                player_core.cultivation_speed_bonus = new_bonuses["cultivation_speed_bonus"]
                player_core.attack_bonus = new_bonuses["attack_bonus"]
                player_core.defense_bonus = new_bonuses["defense_bonus"]
                player_core.hp_bonus = new_bonuses["hp_bonus"]
                player_core.spiritual_power_bonus = new_bonuses["spiritual_power_bonus"]

                quality_gain = -quality_loss
            else:
                new_quality = quality_before
                quality_gain = 0

            result_data = {
                "is_success": False,
                "quality_before": quality_before,
                "quality_after": new_quality,
                "quality_gain": quality_gain
            }

        # 记录祭炼
        record = CoreRefinementRecord(
            player_id=player.id,
            method=method,
            material_used_id=material_item_id,
            quality_before=quality_before,
            quality_after=result_data["quality_after"],
            quality_gain=result_data["quality_gain"],
            is_success=is_success,
            risk_level=risk_level
        )
        db.add(record)

        await db.commit()

        if is_success:
            return True, "祭炼成功！金丹品质提升", result_data
        else:
            if risk_level >= 7 and quality_gain < 0:
                return False, "祭炼失败，金丹品质下降！", result_data
            else:
                return False, "祭炼失败，金丹品质未变化", result_data
