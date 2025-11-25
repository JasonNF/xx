"""寿元系统服务"""
from datetime import datetime, timedelta
from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Player, RealmType


class LifespanService:
    """寿元服务类"""

    # 各境界基础寿元
    REALM_LIFESPAN = {
        RealmType.MORTAL: 100,
        RealmType.QI_REFINING: 150,
        RealmType.FOUNDATION: 300,
        RealmType.CORE_FORMATION: 500,
        RealmType.NASCENT_SOUL: 1000,
        RealmType.DEITY_TRANSFORMATION: 2000,
    }

    @staticmethod
    async def update_lifespan_on_breakthrough(
        db: AsyncSession,
        player: Player
    ) -> None:
        """突破时更新寿元上限"""
        new_lifespan = LifespanService.REALM_LIFESPAN.get(player.realm, 100)

        # 如果新寿元更高，增加寿元
        if new_lifespan > player.lifespan:
            added_years = new_lifespan - player.lifespan
            player.lifespan = new_lifespan
            player.age += added_years // 10  # 突破消耗部分寿元

        await db.commit()

    @staticmethod
    async def age_player(
        db: AsyncSession,
        player: Player,
        years: int
    ) -> Tuple[bool, str]:
        """增加玩家年龄

        Returns:
            (是否还活着, 消息)
        """
        player.age += years

        if player.age >= player.lifespan:
            # 寿终正寝
            return False, f"道友寿元已尽，享年{player.age}岁..."

        remaining_years = player.lifespan - player.age

        if remaining_years <= 50:
            return True, f"⚠️ 剩余寿元不足{remaining_years}年，请尽快寻找延寿之法！"
        elif remaining_years <= 100:
            return True, f"💡 剩余寿元{remaining_years}年"

        await db.commit()
        return True, ""

    @staticmethod
    def get_age_penalty(player: Player) -> float:
        """获取年龄衰老惩罚

        寿元剩余不足20%时开始衰老
        """
        remaining_ratio = (player.lifespan - player.age) / player.lifespan

        if remaining_ratio > 0.2:
            return 1.0  # 无惩罚

        if remaining_ratio > 0.1:
            return 0.9  # -10%

        if remaining_ratio > 0.05:
            return 0.7  # -30%

        return 0.5  # -50%

    @staticmethod
    async def use_longevity_pill(
        db: AsyncSession,
        player: Player,
        years: int
    ) -> Tuple[bool, str]:
        """使用延寿丹药

        Returns:
            (是否成功, 消息)
        """
        # 延寿上限检查（不能超过境界寿元上限的1.5倍）
        max_lifespan = LifespanService.REALM_LIFESPAN.get(player.realm, 100) * 1.5

        if player.lifespan >= max_lifespan:
            return False, f"寿元已达境界上限({int(max_lifespan)}年)，无法继续延寿"

        # 增加寿元
        actual_add = min(years, int(max_lifespan - player.lifespan))
        player.lifespan += actual_add

        await db.commit()

        return True, f"寿元增加{actual_add}年，当前寿元上限：{player.lifespan}年"
