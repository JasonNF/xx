"""游戏调度器 - 定时任务系统"""
import logging
import asyncio
from datetime import datetime
from typing import Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select, and_

from bot.models.database import AsyncSessionLocal
from bot.models import Player
from bot.models.formation import ActiveFormation
from bot.models.adventure import LuckEvent
from bot.models.cave_dwelling import CaveDwelling

logger = logging.getLogger(__name__)


class GameScheduler:
    """游戏调度器"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._running = False

    def start(self):
        """启动调度器"""
        if self._running:
            logger.warning("调度器已在运行")
            return

        logger.info("正在启动游戏调度器...")

        # 注册定时任务
        self._register_jobs()

        # 启动调度器
        self.scheduler.start()
        self._running = True

        logger.info("游戏调度器已启动")

    def shutdown(self):
        """关闭调度器"""
        if not self._running:
            return

        logger.info("正在关闭游戏调度器...")
        self.scheduler.shutdown()
        self._running = False
        logger.info("游戏调度器已关闭")

    def _register_jobs(self):
        """注册所有定时任务"""
        # 每小时检查一次阵法过期
        self.scheduler.add_job(
            self._check_formations_expiry,
            trigger=IntervalTrigger(hours=1),
            id="check_formations",
            name="检查阵法过期",
            replace_existing=True
        )

        # 每小时检查一次运气事件过期
        self.scheduler.add_job(
            self._check_luck_events_expiry,
            trigger=IntervalTrigger(hours=1),
            id="check_luck_events",
            name="检查运气事件过期",
            replace_existing=True
        )

        # 每天凌晨检查洞府维护费用
        self.scheduler.add_job(
            self._check_cave_maintenance,
            trigger=CronTrigger(hour=0, minute=0),
            id="check_cave_maintenance",
            name="检查洞府维护",
            replace_existing=True
        )

        # 每天恢复灵池灵力
        self.scheduler.add_job(
            self._restore_spirit_pool,
            trigger=CronTrigger(hour=6, minute=0),
            id="restore_spirit_pool",
            name="灵池恢复灵力",
            replace_existing=True
        )

        # 每小时清理过期数据
        self.scheduler.add_job(
            self._cleanup_expired_data,
            trigger=IntervalTrigger(hours=6),
            id="cleanup_expired",
            name="清理过期数据",
            replace_existing=True
        )

        # 每天中午12点生成世界BOSS
        self.scheduler.add_job(
            self._spawn_world_boss,
            trigger=CronTrigger(hour=12, minute=0),
            id="spawn_world_boss",
            name="生成世界BOSS",
            replace_existing=True
        )

        # 每小时检查世界BOSS是否超时
        self.scheduler.add_job(
            self._cleanup_world_bosses,
            trigger=IntervalTrigger(hours=1),
            id="cleanup_world_bosses",
            name="清理超时BOSS",
            replace_existing=True
        )

        logger.info(f"已注册 {len(self.scheduler.get_jobs())} 个定时任务")

    async def _check_formations_expiry(self):
        """检查并处理过期的阵法"""
        try:
            logger.debug("开始检查阵法过期...")

            async with AsyncSessionLocal() as session:
                # 查找过期的激活阵法
                result = await session.execute(
                    select(ActiveFormation, Player).join(
                        Player, Player.id == ActiveFormation.player_id
                    ).where(
                        ActiveFormation.is_active == True,
                        ActiveFormation.expires_at <= datetime.now()
                    )
                )
                expired_formations = result.all()

                if not expired_formations:
                    logger.debug("没有过期的阵法")
                    return

                count = 0
                for formation, player in expired_formations:
                    # 移除玩家属性加成
                    player.defense -= formation.current_defense_bonus
                    player.attack -= formation.current_attack_bonus

                    # 撤除阵法
                    formation.is_active = False

                    count += 1

                await session.commit()
                logger.info(f"已处理 {count} 个过期阵法")

        except Exception as e:
            logger.error(f"检查阵法过期时出错: {e}", exc_info=True)

    async def _check_luck_events_expiry(self):
        """检查并处理过期的运气事件"""
        try:
            logger.debug("开始检查运气事件过期...")

            async with AsyncSessionLocal() as session:
                # 查找过期的运气事件
                result = await session.execute(
                    select(LuckEvent).where(
                        LuckEvent.is_active == True,
                        LuckEvent.end_time <= datetime.now()
                    )
                )
                expired_events = result.scalars().all()

                if not expired_events:
                    logger.debug("没有过期的运气事件")
                    return

                count = 0
                for event in expired_events:
                    event.is_active = False
                    count += 1

                await session.commit()
                logger.info(f"已处理 {count} 个过期运气事件")

        except Exception as e:
            logger.error(f"检查运气事件过期时出错: {e}", exc_info=True)

    async def _check_cave_maintenance(self):
        """检查洞府维护费用（每天执行）"""
        try:
            logger.info("开始检查洞府维护费用...")

            async with AsyncSessionLocal() as session:
                # 获取所有洞府
                result = await session.execute(
                    select(CaveDwelling, Player).join(
                        Player, Player.id == CaveDwelling.player_id
                    )
                )
                caves = result.all()

                if not caves:
                    logger.debug("没有洞府需要维护")
                    return

                total_collected = 0
                count = 0

                for cave, player in caves:
                    # 计算欠费天数
                    days_since = (datetime.now() - cave.last_maintenance).days

                    if days_since <= 0:
                        continue

                    # 如果超过30天未维护，降低灵气浓度
                    if days_since > 30:
                        penalty = min((days_since - 30) * 5, 50)  # 最多降低50
                        cave.spiritual_density = max(100, cave.spiritual_density - penalty)
                        logger.warning(
                            f"玩家 {player.name} 的洞府超过30天未维护，"
                            f"灵气浓度降低 {penalty} -> {cave.spiritual_density}"
                        )

                    count += 1

                await session.commit()
                logger.info(f"已检查 {count} 个洞府的维护状态")

        except Exception as e:
            logger.error(f"检查洞府维护时出错: {e}", exc_info=True)

    async def _restore_spirit_pool(self):
        """灵池恢复灵力（每天执行）"""
        try:
            logger.info("开始灵池恢复灵力...")

            async with AsyncSessionLocal() as session:
                from bot.services.cave_service import CaveService

                # 获取所有玩家
                result = await session.execute(select(Player))
                players = result.scalars().all()

                count = 0
                total_restored = 0

                for player in players:
                    # 检查是否有灵池
                    has_pool = await CaveService.has_spirit_pool(session, player.id)

                    if not has_pool:
                        continue

                    # 恢复30%灵力
                    restore_amount = int(player.max_spiritual_power * 0.3)
                    old_sp = player.spiritual_power
                    player.spiritual_power = min(
                        player.max_spiritual_power,
                        player.spiritual_power + restore_amount
                    )

                    actual_restored = player.spiritual_power - old_sp

                    if actual_restored > 0:
                        count += 1
                        total_restored += actual_restored

                await session.commit()
                logger.info(f"灵池为 {count} 名玩家恢复了 {total_restored} 点灵力")

        except Exception as e:
            logger.error(f"灵池恢复灵力时出错: {e}", exc_info=True)

    async def _cleanup_expired_data(self):
        """清理过期数据"""
        try:
            logger.info("开始清理过期数据...")

            async with AsyncSessionLocal() as session:
                # 这里可以添加其他清理逻辑
                # 例如：清理30天前的战斗记录、制作记录等

                # 清理已完成的奇遇记录（保留30天）
                from bot.models.adventure import PlayerAdventure
                from datetime import timedelta

                cutoff_date = datetime.now() - timedelta(days=30)

                result = await session.execute(
                    select(PlayerAdventure).where(
                        PlayerAdventure.is_completed == True,
                        PlayerAdventure.completed_at <= cutoff_date
                    )
                )
                old_adventures = result.scalars().all()

                for adventure in old_adventures:
                    await session.delete(adventure)

                await session.commit()
                logger.info(f"已清理 {len(old_adventures)} 条过期奇遇记录")

        except Exception as e:
            logger.error(f"清理过期数据时出错: {e}", exc_info=True)

    async def _spawn_world_boss(self):
        """生成世界BOSS（每天中午12点执行）"""
        try:
            logger.info("开始生成世界BOSS...")

            async with AsyncSessionLocal() as session:
                from bot.services.world_boss_service import WorldBossService

                success, message, boss = await WorldBossService.spawn_boss(session)

                if success:
                    logger.info(f"世界BOSS已生成: {boss.name} (ID: {boss.id})")
                else:
                    logger.warning(f"世界BOSS生成失败: {message}")

        except Exception as e:
            logger.error(f"生成世界BOSS时出错: {e}", exc_info=True)

    async def _cleanup_world_bosses(self):
        """清理超时的世界BOSS"""
        try:
            logger.debug("开始检查世界BOSS超时...")

            async with AsyncSessionLocal() as session:
                from bot.services.world_boss_service import WorldBossService

                await WorldBossService.cleanup_old_bosses(session)

        except Exception as e:
            logger.error(f"清理世界BOSS时出错: {e}", exc_info=True)


# 全局调度器实例
_scheduler_instance = None


def get_scheduler() -> GameScheduler:
    """获取调度器实例（单例模式）"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = GameScheduler()
    return _scheduler_instance


def start_scheduler():
    """启动调度器"""
    scheduler = get_scheduler()
    scheduler.start()


def stop_scheduler():
    """停止调度器"""
    scheduler = get_scheduler()
    scheduler.shutdown()
