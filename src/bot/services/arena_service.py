"""竞技场服务"""
import random
from datetime import datetime, date
from typing import Tuple, List, Dict, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Player, Arena, BattleRecord, BattleType, BattleResult


class ArenaService:
    """竞技场服务类"""

    # 竞技场配置
    BASE_POINTS = 1000  # 初始积分
    WIN_POINTS = 20  # 胜利获得积分
    LOSS_POINTS = 10  # 失败扣除积分
    MAX_DAILY_CHALLENGES = 5  # 每日挑战上限
    RANK_REWARD_INTERVAL = 100  # 排名奖励间隔

    @staticmethod
    async def get_or_create_arena(db: AsyncSession, player: Player) -> Arena:
        """获取或创建竞技场数据"""
        result = await db.execute(
            select(Arena).where(Arena.player_id == player.id)
        )
        arena = result.scalar_one_or_none()

        if not arena:
            # 获取当前最大排名
            result = await db.execute(select(func.max(Arena.rank)))
            max_rank = result.scalar() or 0

            arena = Arena(
                player_id=player.id,
                rank=max_rank + 1,
                highest_rank=max_rank + 1,
                points=ArenaService.BASE_POINTS
            )
            db.add(arena)
            await db.commit()
            await db.refresh(arena)

        return arena

    @staticmethod
    async def check_daily_limit(arena: Arena) -> Tuple[bool, int]:
        """检查每日挑战次数

        Returns:
            (是否可挑战, 剩余次数)
        """
        today = date.today()

        # 如果是新的一天,重置次数
        if not arena.last_challenge_date or arena.last_challenge_date.date() < today:
            remaining = arena.max_daily_challenges
            return True, remaining

        remaining = arena.max_daily_challenges - arena.daily_challenges
        can_challenge = remaining > 0

        return can_challenge, remaining

    @staticmethod
    async def get_challenge_targets(
        db: AsyncSession,
        player: Player,
        arena: Arena,
        count: int = 3
    ) -> List[Dict]:
        """获取可挑战的目标

        返回排名在玩家附近的其他玩家
        """
        # 查找排名在当前玩家前后的玩家
        rank_min = max(1, arena.rank - 50)
        rank_max = arena.rank + 10

        result = await db.execute(
            select(Player, Arena).join(
                Arena, Arena.player_id == Player.id
            ).where(
                and_(
                    Arena.rank >= rank_min,
                    Arena.rank < arena.rank,  # 只能挑战排名高于自己的
                    Player.id != player.id
                )
            ).order_by(Arena.rank.desc()).limit(count)
        )
        targets = result.all()

        target_list = []
        for target_player, target_arena in targets:
            target_list.append({
                "player_id": target_player.id,
                "nickname": target_player.nickname,
                "realm": target_player.full_realm_name,
                "rank": target_arena.rank,
                "points": target_arena.points,
                "combat_power": target_player.combat_power
            })

        return target_list

    @staticmethod
    async def challenge(
        db: AsyncSession,
        challenger: Player,
        target_id: int
    ) -> Tuple[bool, str, Optional[Dict]]:
        """发起竞技场挑战"""
        # 获取挑战者竞技场数据
        challenger_arena = await ArenaService.get_or_create_arena(db, challenger)

        # 检查每日次数
        can_challenge, remaining = await ArenaService.check_daily_limit(challenger_arena)
        if not can_challenge:
            return False, "今日挑战次数已用完", None

        # 获取目标玩家
        result = await db.execute(select(Player).where(Player.id == target_id))
        target = result.scalar_one_or_none()

        if not target:
            return False, "目标玩家不存在", None

        # 获取目标竞技场数据
        target_arena = await ArenaService.get_or_create_arena(db, target)

        # 检查排名限制
        if target_arena.rank >= challenger_arena.rank:
            return False, "只能挑战排名高于自己的玩家", None

        # 模拟战斗(简化版)
        challenger_power = challenger.combat_power
        target_power = target.combat_power

        # 计算胜率(基于战力差异)
        power_ratio = challenger_power / target_power if target_power > 0 else 2.0
        base_win_rate = 0.5
        if power_ratio > 1:
            win_rate = min(0.85, base_win_rate + (power_ratio - 1) * 0.2)
        else:
            win_rate = max(0.15, base_win_rate - (1 - power_ratio) * 0.2)

        # 判定结果
        is_win = random.random() < win_rate

        # 更新挑战次数
        today = date.today()
        if not challenger_arena.last_challenge_date or challenger_arena.last_challenge_date.date() < today:
            challenger_arena.daily_challenges = 1
            challenger_arena.last_challenge_date = datetime.now()
        else:
            challenger_arena.daily_challenges += 1
            challenger_arena.last_challenge_date = datetime.now()

        challenger_arena.total_challenges += 1

        # 更新战果
        if is_win:
            # 胜利
            challenger_arena.total_wins += 1
            challenger_arena.win_streak += 1
            if challenger_arena.win_streak > challenger_arena.highest_win_streak:
                challenger_arena.highest_win_streak = challenger_arena.win_streak

            # 积分变化
            challenger_arena.points += ArenaService.WIN_POINTS
            target_arena.points = max(0, target_arena.points - ArenaService.WIN_POINTS // 2)

            # 排名交换
            old_challenger_rank = challenger_arena.rank
            old_target_rank = target_arena.rank
            challenger_arena.rank = old_target_rank
            target_arena.rank = old_challenger_rank

            if challenger_arena.rank < challenger_arena.highest_rank:
                challenger_arena.highest_rank = challenger_arena.rank

            result_msg = f"🎉 挑战成功！\n排名: {old_challenger_rank} → {challenger_arena.rank}"
            battle_result = BattleResult.WIN
        else:
            # 失败
            challenger_arena.win_streak = 0
            challenger_arena.points = max(0, challenger_arena.points - ArenaService.LOSS_POINTS)

            result_msg = f"💔 挑战失败\n排名未变: {challenger_arena.rank}"
            battle_result = BattleResult.LOSE

        # 记录战斗
        battle_record = BattleRecord(
            player_id=challenger.id,
            opponent_id=target.id,
            battle_type=BattleType.ARENA,
            result=battle_result,
            exp_gained=0,
            spirit_stones_gained=0
        )
        db.add(battle_record)

        await db.commit()

        # 构建结果数据
        result_data = {
            "is_win": is_win,
            "challenger_rank": challenger_arena.rank,
            "target_rank": target_arena.rank,
            "points_change": ArenaService.WIN_POINTS if is_win else -ArenaService.LOSS_POINTS,
            "win_streak": challenger_arena.win_streak,
            "remaining_challenges": challenger_arena.max_daily_challenges - challenger_arena.daily_challenges
        }

        return True, result_msg, result_data

    @staticmethod
    async def get_rankings(
        db: AsyncSession,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """获取竞技场排行榜"""
        result = await db.execute(
            select(Player, Arena).join(
                Arena, Arena.player_id == Player.id
            ).order_by(Arena.rank).limit(limit).offset(offset)
        )
        rankings = result.all()

        rankings_list = []
        for player, arena in rankings:
            rankings_list.append({
                "rank": arena.rank,
                "player_id": player.id,
                "nickname": player.nickname,
                "realm": player.full_realm_name,
                "points": arena.points,
                "combat_power": player.combat_power,
                "win_rate": arena.total_wins / arena.total_challenges if arena.total_challenges > 0 else 0,
                "win_streak": arena.win_streak
            })

        return rankings_list

    @staticmethod
    async def get_player_arena_info(db: AsyncSession, player: Player) -> Dict:
        """获取玩家竞技场信息"""
        arena = await ArenaService.get_or_create_arena(db, player)
        can_challenge, remaining = await ArenaService.check_daily_limit(arena)

        return {
            "rank": arena.rank,
            "highest_rank": arena.highest_rank,
            "points": arena.points,
            "total_challenges": arena.total_challenges,
            "total_wins": arena.total_wins,
            "win_rate": arena.total_wins / arena.total_challenges if arena.total_challenges > 0 else 0,
            "win_streak": arena.win_streak,
            "highest_win_streak": arena.highest_win_streak,
            "daily_challenges": arena.daily_challenges,
            "remaining_challenges": remaining,
            "can_challenge": can_challenge
        }
