"""修炼系统服务"""
import random
from datetime import datetime, timedelta
from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Player
from bot.config import settings
from bot.services.cave_service import CaveService


class CultivationService:
    """修炼服务类"""

    @staticmethod
    async def start_cultivation(
        db: AsyncSession,
        player: Player,
        duration_hours: float
    ) -> Tuple[bool, str]:
        """开始修炼

        Args:
            db: 数据库会话
            player: 玩家对象
            duration_hours: 修炼时长（小时）

        Returns:
            (success, message)
        """
        # 检查状态
        if player.is_cultivating:
            remaining = (player.cultivation_end_time - datetime.now()).total_seconds()
            return False, f"正在修炼中，剩余时间：{int(remaining / 60)} 分钟"

        if player.is_in_battle:
            return False, "战斗中无法修炼"

        # 检查时长限制
        duration_seconds = duration_hours * 3600
        if duration_seconds < settings.CULTIVATION_MIN_DURATION:
            return False, f"修炼时长不能少于 {settings.CULTIVATION_MIN_DURATION / 60} 分钟"

        if duration_seconds > settings.CULTIVATION_MAX_DURATION:
            return False, f"修炼时长不能超过 {settings.CULTIVATION_MAX_DURATION / 3600} 小时"

        # 开始修炼
        player.is_cultivating = True
        player.cultivation_start_time = datetime.now()
        player.cultivation_end_time = datetime.now() + timedelta(seconds=duration_seconds)

        await db.commit()

        return True, f"开始修炼，预计完成时间：{player.cultivation_end_time.strftime('%Y-%m-%d %H:%M:%S')}"

    @staticmethod
    async def finish_cultivation(
        db: AsyncSession,
        player: Player
    ) -> Tuple[bool, str, int]:
        """完成修炼

        Returns:
            (success, message, exp_gained)
        """
        if not player.is_cultivating:
            return False, "当前未在修炼中", 0

        now = datetime.now()

        # 检查是否到时间
        if now < player.cultivation_end_time:
            remaining = (player.cultivation_end_time - now).total_seconds()
            return False, f"修炼未完成，剩余时间：{int(remaining / 60)} 分钟", 0

        # 计算修炼时长
        duration_hours = (player.cultivation_end_time - player.cultivation_start_time).total_seconds() / 3600

        # 计算获得的修为
        exp_gained = await CultivationService.calculate_cultivation_exp(db, player, duration_hours)

        # 随机事件
        event_message = ""
        event = random.random()
        if event < 0.05:  # 5% 几率走火入魔
            exp_gained = int(exp_gained * 0.5)
            damage = int(player.max_hp * 0.3)
            player.hp = max(1, player.hp - damage)
            event_message = f"\n⚠️ 修炼时走火入魔！受到 {damage} 点伤害，修为减半！"
        elif event < 0.10:  # 5% 几率顿悟（已平衡优化：从10%降低）
            exp_gained = int(exp_gained * 1.5)  # +50%加成（已平衡优化：从+100%降低）
            event_message = "\n✨ 修炼时心有所悟！获得额外修为！"
        elif event < 0.25:  # 10% 几率得到宝物
            # TODO: 添加物品奖励
            event_message = "\n💎 修炼时意外发现一件宝物！"

        # 增加修为
        player.cultivation_exp += exp_gained

        # 重置修炼状态
        player.is_cultivating = False
        player.cultivation_start_time = None
        player.cultivation_end_time = None

        await db.commit()

        message = f"修炼完成！获得 {exp_gained} 修为{event_message}"
        return True, message, exp_gained

    @staticmethod
    async def cancel_cultivation(
        db: AsyncSession,
        player: Player
    ) -> Tuple[bool, str]:
        """取消修炼（提前结束，不获得修为）

        Returns:
            (success, message)
        """
        if not player.is_cultivating:
            return False, "当前未在修炼中"

        # 重置修炼状态
        player.is_cultivating = False
        player.cultivation_start_time = None
        player.cultivation_end_time = None

        await db.commit()

        return True, "已取消修炼"

    @staticmethod
    async def calculate_cultivation_exp(db: AsyncSession, player: Player, duration_hours: float) -> int:
        """计算修炼获得的修为

        Args:
            db: 数据库会话
            player: 玩家对象
            duration_hours: 修炼时长（小时）

        Returns:
            获得的修为
        """
        # 基础修炼速度
        base_rate = settings.BASE_CULTIVATION_RATE

        # 悟性加成
        comprehension_bonus = 1 + (player.comprehension - 10) * 0.05

        # 根骨加成
        # 根骨加成（使用悟性替代）
        root_bone_bonus = 1.0

        # 功法加成（如果有）
        method_bonus = 1.0
        if player.cultivation_method_id:
            # TODO: 从数据库获取功法加成
            method_bonus = 1.5

        # 境界系数（境界越高，修炼越慢）
        realm_index = list(player.realm.__class__).index(player.realm)
        realm_penalty = 1 / (1 + realm_index * 0.1)

        # 洞府修炼室加成
        cave_cultivation_bonus = await CaveService.get_cultivation_speed_bonus(db, player.id)

        # 洞府灵气浓度加成
        cave_spiritual_bonus = await CaveService.get_spiritual_density_bonus(db, player.id)

        # 计算最终修为
        exp = int(
            base_rate *
            duration_hours *
            comprehension_bonus *
            root_bone_bonus *
            method_bonus *
            realm_penalty *
            cave_cultivation_bonus *
            cave_spiritual_bonus
        )

        return exp

    @staticmethod
    async def get_cultivation_status(player: Player) -> str:
        """获取修炼状态描述"""
        if not player.is_cultivating:
            return "空闲中"

        now = datetime.now()
        if now >= player.cultivation_end_time:
            return "修炼完成，可以收取修为"

        remaining = (player.cultivation_end_time - now).total_seconds()
        hours = int(remaining / 3600)
        minutes = int((remaining % 3600) / 60)

        return f"修炼中，剩余时间：{hours}小时{minutes}分钟"
