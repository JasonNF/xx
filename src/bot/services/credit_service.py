"""积分系统服务"""
from datetime import datetime
from typing import Optional, Tuple, List

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Player, PlayerCreditRecord, CreditType


class CreditService:
    """积分服务类"""

    @staticmethod
    async def add_credits(
        db: AsyncSession,
        player: Player,
        amount: int,
        credit_type: CreditType,
        reason: str,
        reference_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """增加玩家积分

        Args:
            db: 数据库会话
            player: 玩家对象
            amount: 增加的积分数量
            credit_type: 积分类型
            reason: 获得原因
            reference_id: 关联ID（可选）

        Returns:
            (success, message)
        """
        if amount <= 0:
            return False, "积分数量必须大于0"

        credit_before = player.credits
        player.credits += amount
        credit_after = player.credits

        # 记录积分变动
        record = PlayerCreditRecord(
            player_id=player.id,
            credit_change=amount,
            credit_before=credit_before,
            credit_after=credit_after,
            credit_type=credit_type,
            reason=reason,
            reference_id=reference_id
        )

        db.add(record)
        await db.commit()
        await db.refresh(player)

        return True, f"获得 {amount} 积分！{reason}"

    @staticmethod
    async def deduct_credits(
        db: AsyncSession,
        player: Player,
        amount: int,
        credit_type: CreditType,
        reason: str,
        reference_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """扣除玩家积分

        Args:
            db: 数据库会话
            player: 玩家对象
            amount: 扣除的积分数量
            credit_type: 积分类型
            reason: 扣除原因
            reference_id: 关联ID（可选）

        Returns:
            (success, message)
        """
        if amount <= 0:
            return False, "积分数量必须大于0"

        if player.credits < amount:
            return False, f"积分不足！需要 {amount} 积分，当前拥有 {player.credits} 积分"

        credit_before = player.credits
        player.credits -= amount
        credit_after = player.credits

        # 记录积分变动
        record = PlayerCreditRecord(
            player_id=player.id,
            credit_change=-amount,  # 负数表示扣除
            credit_before=credit_before,
            credit_after=credit_after,
            credit_type=credit_type,
            reason=reason,
            reference_id=reference_id
        )

        db.add(record)
        await db.commit()
        await db.refresh(player)

        return True, f"消耗 {amount} 积分。{reason}"

    @staticmethod
    async def get_credit_records(
        db: AsyncSession,
        player_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[PlayerCreditRecord]:
        """获取玩家积分记录

        Args:
            db: 数据库会话
            player_id: 玩家ID
            limit: 每页数量
            offset: 偏移量

        Returns:
            积分记录列表
        """
        result = await db.execute(
            select(PlayerCreditRecord)
            .where(PlayerCreditRecord.player_id == player_id)
            .order_by(PlayerCreditRecord.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_credit_summary(
        db: AsyncSession,
        player_id: int
    ) -> dict:
        """获取玩家积分统计

        Args:
            db: 数据库会话
            player_id: 玩家ID

        Returns:
            统计信息字典
        """
        # 总获得积分
        total_gained = await db.scalar(
            select(func.sum(PlayerCreditRecord.credit_change))
            .where(
                and_(
                    PlayerCreditRecord.player_id == player_id,
                    PlayerCreditRecord.credit_change > 0
                )
            )
        ) or 0

        # 总消耗积分
        total_spent = abs(await db.scalar(
            select(func.sum(PlayerCreditRecord.credit_change))
            .where(
                and_(
                    PlayerCreditRecord.player_id == player_id,
                    PlayerCreditRecord.credit_change < 0
                )
            )
        ) or 0)

        # 记录总数
        total_records = await db.scalar(
            select(func.count(PlayerCreditRecord.id))
            .where(PlayerCreditRecord.player_id == player_id)
        ) or 0

        return {
            "total_gained": total_gained,
            "total_spent": total_spent,
            "total_records": total_records
        }

    @staticmethod
    async def format_credit_record(record: PlayerCreditRecord) -> str:
        """格式化积分记录显示

        Args:
            record: 积分记录

        Returns:
            格式化字符串
        """
        change_str = f"+{record.credit_change}" if record.credit_change > 0 else str(record.credit_change)
        emoji = "💰" if record.credit_change > 0 else "💸"

        time_str = record.created_at.strftime("%m-%d %H:%M")

        return f"{emoji} {change_str} 积分 | {record.reason} ({time_str})"

    @staticmethod
    async def exchange_credits_to_spirit_stones(
        db: AsyncSession,
        player: Player,
        credit_amount: int
    ) -> Tuple[bool, str]:
        """积分兑换灵石

        兑换比例: 1积分 = 10灵石

        Args:
            db: 数据库会话
            player: 玩家对象
            credit_amount: 要兑换的积分数量

        Returns:
            (success, message)
        """
        if credit_amount <= 0:
            return False, "兑换积分必须大于0"

        if player.credits < credit_amount:
            return False, f"积分不足！需要 {credit_amount:,} 积分，当前拥有 {player.credits:,} 积分"

        # 兑换比例: 1积分 = 10灵石
        EXCHANGE_RATE = 10
        spirit_stones = credit_amount * EXCHANGE_RATE

        # 扣除积分
        credit_before = player.credits
        player.credits -= credit_amount
        credit_after = player.credits

        # 增加灵石
        player.spirit_stones += spirit_stones

        # 记录积分变动
        record = PlayerCreditRecord(
            player_id=player.id,
            credit_change=-credit_amount,
            credit_before=credit_before,
            credit_after=credit_after,
            credit_type=CreditType.EXCHANGE_SPIRIT_STONES,
            reason=f"兑换灵石 x{spirit_stones:,}",
            reference_id=None
        )

        db.add(record)
        await db.commit()
        await db.refresh(player)

        return True, f"""
✅ 兑换成功！

━━━━━━━━━━━━━━━
💎 消耗积分：{credit_amount:,}
💰 获得灵石：{spirit_stones:,}
━━━━━━━━━━━━━━━

剩余积分：{player.credits:,}
剩余灵石：{player.spirit_stones:,}
"""


# 积分获取规则（可配置）
class CreditRewards:
    """积分奖励配置"""

    # 每日签到
    DAILY_SIGN_BASE = 10  # 基础签到积分
    DAILY_SIGN_STREAK_BONUS = 5  # 连续签到每天额外积分

    # 任务完成
    TASK_EASY = 5
    TASK_NORMAL = 10
    TASK_HARD = 20
    TASK_LEGENDARY = 50

    # PVP
    PVP_WIN = 5
    PVP_STREAK_BONUS = 2  # 连胜额外奖励

    # 世界BOSS
    WORLD_BOSS_PARTICIPATION = 10  # 参与奖励
    WORLD_BOSS_TOP1 = 50  # 第一名
    WORLD_BOSS_TOP3 = 30  # 前三名
    WORLD_BOSS_TOP10 = 15  # 前十名

    # 境界突破
    BREAKTHROUGH_QI_REFINING = 5  # 炼气期突破
    BREAKTHROUGH_FOUNDATION = 20  # 筑基期突破
    BREAKTHROUGH_CORE_FORMATION = 50  # 结丹期突破
    BREAKTHROUGH_NASCENT_SOUL = 100  # 元婴期突破
    BREAKTHROUGH_DEITY_TRANSFORMATION = 200  # 化神期突破

    # 成就
    ACHIEVEMENT_BRONZE = 10
    ACHIEVEMENT_SILVER = 25
    ACHIEVEMENT_GOLD = 50
    ACHIEVEMENT_PLATINUM = 100

    @staticmethod
    def get_sign_reward(streak_days: int) -> int:
        """计算签到奖励

        Args:
            streak_days: 连续签到天数

        Returns:
            积分奖励
        """
        base = CreditRewards.DAILY_SIGN_BASE
        bonus = min(streak_days - 1, 7) * CreditRewards.DAILY_SIGN_STREAK_BONUS
        return base + bonus

    @staticmethod
    def get_breakthrough_reward(realm: str) -> int:
        """根据境界获取突破奖励

        Args:
            realm: 境界名称

        Returns:
            积分奖励
        """
        rewards = {
            "炼气期": CreditRewards.BREAKTHROUGH_QI_REFINING,
            "筑基期": CreditRewards.BREAKTHROUGH_FOUNDATION,
            "结丹期": CreditRewards.BREAKTHROUGH_CORE_FORMATION,
            "元婴期": CreditRewards.BREAKTHROUGH_NASCENT_SOUL,
            "化神期": CreditRewards.BREAKTHROUGH_DEITY_TRANSFORMATION,
        }
        return rewards.get(realm, 0)
