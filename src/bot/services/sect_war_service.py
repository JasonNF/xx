"""宗门战争服务"""
import random
from datetime import datetime, timedelta
from typing import Tuple, Dict, List, Optional
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import (
    Player, Sect, SectWar, SectWarStatus, SectWarParticipation,
    BattleRecord, BattleType, BattleResult
)


class SectWarService:
    """宗门战争服务类"""

    # 宗门战争配置
    WAR_DURATION_HOURS = 24  # 战争持续时间(小时)
    MIN_PARTICIPANTS = 5  # 最少参战人数
    SCORE_PER_KILL = 100  # 每次击杀获得的分数
    TREASURY_REWARD_RATIO = 0.1  # 胜利方获得失败方国库的10%
    REPUTATION_REWARD = 1000  # 胜利方获得的声望

    @staticmethod
    async def can_declare_war(
        db: AsyncSession,
        attacker_sect: Sect,
        defender_sect_id: int
    ) -> Tuple[bool, str]:
        """检查是否可以宣战"""
        # 检查防御方门派是否存在
        result = await db.execute(
            select(Sect).where(Sect.id == defender_sect_id)
        )
        defender_sect = result.scalar_one_or_none()

        if not defender_sect:
            return False, "目标门派不存在"

        if attacker_sect.id == defender_sect.id:
            return False, "不能对自己的门派宣战"

        # 检查是否有正在进行或待开始的战争
        result = await db.execute(
            select(SectWar).where(
                or_(
                    and_(
                        SectWar.attacker_sect_id == attacker_sect.id,
                        SectWar.status != SectWarStatus.FINISHED
                    ),
                    and_(
                        SectWar.defender_sect_id == attacker_sect.id,
                        SectWar.status != SectWarStatus.FINISHED
                    ),
                    and_(
                        SectWar.attacker_sect_id == defender_sect.id,
                        SectWar.status != SectWarStatus.FINISHED
                    ),
                    and_(
                        SectWar.defender_sect_id == defender_sect.id,
                        SectWar.status != SectWarStatus.FINISHED
                    )
                )
            )
        )
        ongoing_war = result.scalar_one_or_none()

        if ongoing_war:
            return False, "双方门派有正在进行的战争"

        # 检查门派成员数量
        result = await db.execute(
            select(func.count(Player.id)).where(Player.sect_id == attacker_sect.id)
        )
        attacker_members = result.scalar()

        result = await db.execute(
            select(func.count(Player.id)).where(Player.sect_id == defender_sect.id)
        )
        defender_members = result.scalar()

        if attacker_members < SectWarService.MIN_PARTICIPANTS:
            return False, f"进攻方门派人数不足{SectWarService.MIN_PARTICIPANTS}人"

        if defender_members < SectWarService.MIN_PARTICIPANTS:
            return False, f"防守方门派人数不足{SectWarService.MIN_PARTICIPANTS}人"

        return True, ""

    @staticmethod
    async def declare_war(
        db: AsyncSession,
        attacker_sect: Sect,
        defender_sect_id: int,
        declarer_id: int
    ) -> Tuple[bool, str, Optional[SectWar]]:
        """宣战"""
        can_declare, reason = await SectWarService.can_declare_war(
            db, attacker_sect, defender_sect_id
        )

        if not can_declare:
            return False, reason, None

        # 创建宗门战记录
        war = SectWar(
            attacker_sect_id=attacker_sect.id,
            defender_sect_id=defender_sect_id,
            declared_by=declarer_id,
            status=SectWarStatus.DECLARED
        )
        db.add(war)
        await db.commit()
        await db.refresh(war)

        return True, f"宗门战已宣战，将在1小时后开始", war

    @staticmethod
    async def start_war(db: AsyncSession, war_id: int) -> Tuple[bool, str]:
        """开始宗门战"""
        result = await db.execute(
            select(SectWar).where(SectWar.id == war_id)
        )
        war = result.scalar_one_or_none()

        if not war:
            return False, "宗门战不存在"

        if war.status != SectWarStatus.DECLARED:
            return False, "宗门战状态不正确"

        war.status = SectWarStatus.ONGOING
        war.started_at = datetime.now()
        await db.commit()

        return True, "宗门战已开始"

    @staticmethod
    async def join_war(
        db: AsyncSession,
        player: Player,
        war_id: int
    ) -> Tuple[bool, str]:
        """参加宗门战"""
        # 获取战争信息
        result = await db.execute(
            select(SectWar).where(SectWar.id == war_id)
        )
        war = result.scalar_one_or_none()

        if not war:
            return False, "宗门战不存在"

        if war.status != SectWarStatus.ONGOING:
            return False, "宗门战未在进行中"

        # 检查是否属于参战门派
        if player.sect_id not in [war.attacker_sect_id, war.defender_sect_id]:
            return False, "你的门派未参与此战"

        # 检查是否已参战
        result = await db.execute(
            select(SectWarParticipation).where(
                SectWarParticipation.war_id == war_id,
                SectWarParticipation.player_id == player.id
            )
        )
        participation = result.scalar_one_or_none()

        if participation:
            return False, "你已参战"

        # 创建参战记录
        participation = SectWarParticipation(
            war_id=war_id,
            player_id=player.id,
            sect_id=player.sect_id
        )
        db.add(participation)
        await db.commit()

        return True, "已加入宗门战"

    @staticmethod
    async def record_battle_result(
        db: AsyncSession,
        war_id: int,
        winner: Player,
        loser: Player,
        battle_record: BattleRecord
    ) -> Tuple[bool, str]:
        """记录战斗结果"""
        # 获取战争信息
        result = await db.execute(
            select(SectWar).where(SectWar.id == war_id)
        )
        war = result.scalar_one_or_none()

        if not war:
            return False, "宗门战不存在"

        if war.status != SectWarStatus.ONGOING:
            return False, "宗门战未在进行中"

        # 获取参战记录
        result = await db.execute(
            select(SectWarParticipation).where(
                SectWarParticipation.war_id == war_id,
                SectWarParticipation.player_id == winner.id
            )
        )
        winner_participation = result.scalar_one_or_none()

        result = await db.execute(
            select(SectWarParticipation).where(
                SectWarParticipation.war_id == war_id,
                SectWarParticipation.player_id == loser.id
            )
        )
        loser_participation = result.scalar_one_or_none()

        # 如果没有参战记录,自动创建
        if not winner_participation:
            winner_participation = SectWarParticipation(
                war_id=war_id,
                player_id=winner.id,
                sect_id=winner.sect_id
            )
            db.add(winner_participation)

        if not loser_participation:
            loser_participation = SectWarParticipation(
                war_id=war_id,
                player_id=loser.id,
                sect_id=loser.sect_id
            )
            db.add(loser_participation)

        # 更新战况
        winner_participation.kills += 1
        winner_participation.contribution_points += SectWarService.SCORE_PER_KILL
        loser_participation.deaths += 1

        # 更新门派分数
        if winner.sect_id == war.attacker_sect_id:
            war.attacker_score += SectWarService.SCORE_PER_KILL
            war.attacker_kills += 1
        else:
            war.defender_score += SectWarService.SCORE_PER_KILL
            war.defender_kills += 1

        await db.commit()

        return True, f"战果已记录，{winner.nickname}击败{loser.nickname}"

    @staticmethod
    async def end_war(db: AsyncSession, war_id: int) -> Tuple[bool, str, Dict]:
        """结束宗门战"""
        result = await db.execute(
            select(SectWar).where(SectWar.id == war_id)
        )
        war = result.scalar_one_or_none()

        if not war:
            return False, "宗门战不存在", {}

        if war.status != SectWarStatus.ONGOING:
            return False, "宗门战未在进行中", {}

        # 判定胜负
        if war.attacker_score > war.defender_score:
            winner_sect_id = war.attacker_sect_id
            loser_sect_id = war.defender_sect_id
        elif war.defender_score > war.attacker_score:
            winner_sect_id = war.defender_sect_id
            loser_sect_id = war.attacker_sect_id
        else:
            # 平局,防守方获胜
            winner_sect_id = war.defender_sect_id
            loser_sect_id = war.attacker_sect_id

        war.winner_sect_id = winner_sect_id
        war.status = SectWarStatus.FINISHED
        war.ended_at = datetime.now()

        # 获取门派信息
        result = await db.execute(
            select(Sect).where(Sect.id.in_([winner_sect_id, loser_sect_id]))
        )
        sects = result.scalars().all()
        winner_sect = next((s for s in sects if s.id == winner_sect_id), None)
        loser_sect = next((s for s in sects if s.id == loser_sect_id), None)

        # 计算战利品
        treasury_reward = int(loser_sect.treasury * SectWarService.TREASURY_REWARD_RATIO)
        war.reward_treasury = treasury_reward
        war.reward_reputation = SectWarService.REPUTATION_REWARD

        # 转移资源
        loser_sect.treasury -= treasury_reward
        winner_sect.treasury += treasury_reward
        winner_sect.reputation += SectWarService.REPUTATION_REWARD

        await db.commit()

        result_data = {
            "winner_sect": winner_sect.name,
            "loser_sect": loser_sect.name,
            "winner_score": war.attacker_score if winner_sect_id == war.attacker_sect_id else war.defender_score,
            "loser_score": war.defender_score if winner_sect_id == war.attacker_sect_id else war.attacker_score,
            "treasury_reward": treasury_reward,
            "reputation_reward": SectWarService.REPUTATION_REWARD
        }

        return True, "宗门战已结束", result_data

    @staticmethod
    async def get_war_status(db: AsyncSession, war_id: int) -> Optional[Dict]:
        """获取宗门战状态"""
        result = await db.execute(
            select(SectWar, Sect).join(
                Sect, Sect.id == SectWar.attacker_sect_id
            ).where(SectWar.id == war_id)
        )
        data = result.one_or_none()

        if not data:
            return None

        war, attacker_sect = data

        result = await db.execute(
            select(Sect).where(Sect.id == war.defender_sect_id)
        )
        defender_sect = result.scalar_one()

        # 获取参战人数
        result = await db.execute(
            select(func.count(SectWarParticipation.id)).where(
                SectWarParticipation.war_id == war_id,
                SectWarParticipation.sect_id == war.attacker_sect_id
            )
        )
        attacker_participants = result.scalar()

        result = await db.execute(
            select(func.count(SectWarParticipation.id)).where(
                SectWarParticipation.war_id == war_id,
                SectWarParticipation.sect_id == war.defender_sect_id
            )
        )
        defender_participants = result.scalar()

        status_data = {
            "war_id": war.id,
            "status": war.status.value,
            "attacker_sect": attacker_sect.name,
            "defender_sect": defender_sect.name,
            "attacker_score": war.attacker_score,
            "defender_score": war.defender_score,
            "attacker_kills": war.attacker_kills,
            "defender_kills": war.defender_kills,
            "attacker_participants": attacker_participants,
            "defender_participants": defender_participants,
            "started_at": war.started_at,
            "ended_at": war.ended_at,
            "winner_sect_id": war.winner_sect_id
        }

        return status_data

    @staticmethod
    async def get_player_war_stats(
        db: AsyncSession,
        player_id: int,
        war_id: int
    ) -> Optional[Dict]:
        """获取玩家在特定宗门战的统计"""
        result = await db.execute(
            select(SectWarParticipation).where(
                SectWarParticipation.war_id == war_id,
                SectWarParticipation.player_id == player_id
            )
        )
        participation = result.scalar_one_or_none()

        if not participation:
            return None

        return {
            "kills": participation.kills,
            "deaths": participation.deaths,
            "contribution_points": participation.contribution_points,
            "kd_ratio": participation.kills / participation.deaths if participation.deaths > 0 else participation.kills
        }

    @staticmethod
    async def get_ongoing_wars(db: AsyncSession) -> List[Dict]:
        """获取所有进行中的宗门战"""
        result = await db.execute(
            select(SectWar).where(
                SectWar.status == SectWarStatus.ONGOING
            ).order_by(SectWar.started_at.desc())
        )
        wars = result.scalars().all()

        wars_list = []
        for war in wars:
            status = await SectWarService.get_war_status(db, war.id)
            if status:
                wars_list.append(status)

        return wars_list
