"""成就系统服务"""
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import (
    Player, Achievement, PlayerAchievement, PlayerTitle, AchievementStats,
    AchievementCategory, PlayerInventory, Item
)


class AchievementService:
    """成就服务类"""

    # 成就条件类型映射
    CONDITION_TYPES = {
        # 修炼相关
        "realm_reach": "达到特定境界",
        "cultivation_hours": "累计修炼时长",
        "breakthrough_count": "成功突破次数",

        # 战斗相关
        "battle_win": "战斗胜利次数",
        "battle_perfect": "完美战斗(无伤)次数",
        "kill_boss": "击败BOSS次数",
        "pvp_win": "PVP胜利次数",
        "consecutive_win": "连续胜利次数",

        # 收集相关
        "collect_item": "收集特定物品",
        "treasure_collect": "收集法宝数量",
        "spirit_beast_collect": "收集灵兽数量",

        # 制作相关
        "alchemy_success": "成功炼丹次数",
        "refinery_success": "成功炼器次数",
        "talisman_craft": "成功制符次数",
        "formation_master": "阵法掌握数量",

        # 探索相关
        "secret_realm_clear": "秘境通关次数",
        "adventure_complete": "奇遇完成次数",
        "cave_upgrade": "洞府升级次数",

        # 社交相关
        "sect_contribution": "宗门贡献值",
        "invite_friends": "邀请好友数量",

        # 财富相关
        "spirit_stones": "拥有灵石数量",
        "total_earnings": "累计赚取灵石",
        "market_trade": "市场交易次数",

        # 特殊相关
        "sign_days": "连续签到天数",
        "first_achievement": "第一次获得成就",
        "achievement_points": "成就点数达到"
    }

    @staticmethod
    async def get_or_create_stats(db: AsyncSession, player_id: int) -> AchievementStats:
        """获取或创建玩家成就统计"""
        result = await db.execute(
            select(AchievementStats).where(AchievementStats.player_id == player_id)
        )
        stats = result.scalar_one_or_none()

        if not stats:
            stats = AchievementStats(player_id=player_id)
            db.add(stats)
            await db.commit()
            await db.refresh(stats)

        return stats

    @staticmethod
    async def check_and_update_progress(
        db: AsyncSession,
        player: Player,
        condition_type: str,
        current_value: int
    ) -> List[Achievement]:
        """检查并更新成就进度

        Returns:
            新完成的成就列表
        """
        # 查找该类型的所有成就
        result = await db.execute(
            select(Achievement).where(Achievement.condition_type == condition_type)
        )
        achievements = result.scalars().all()

        newly_completed = []

        for achievement in achievements:
            # 查找玩家成就记录
            result = await db.execute(
                select(PlayerAchievement).where(
                    PlayerAchievement.player_id == player.id,
                    PlayerAchievement.achievement_id == achievement.id
                )
            )
            player_ach = result.scalar_one_or_none()

            # 如果没有记录,创建一个
            if not player_ach:
                player_ach = PlayerAchievement(
                    player_id=player.id,
                    achievement_id=achievement.id,
                    current_progress=0
                )
                db.add(player_ach)

            # 如果已完成,跳过
            if player_ach.is_completed:
                continue

            # 更新进度
            player_ach.current_progress = current_value

            # 检查是否完成
            if current_value >= achievement.condition_value:
                player_ach.is_completed = True
                player_ach.completed_at = datetime.now()
                newly_completed.append(achievement)

        if newly_completed:
            await db.commit()

        return newly_completed

    @staticmethod
    async def claim_achievement(
        db: AsyncSession,
        player: Player,
        achievement_id: int
    ) -> Tuple[bool, str, Dict]:
        """领取成就奖励

        Returns:
            (是否成功, 消息, 奖励数据)
        """
        # 获取成就
        result = await db.execute(
            select(Achievement).where(Achievement.id == achievement_id)
        )
        achievement = result.scalar_one_or_none()

        if not achievement:
            return False, "成就不存在", {}

        # 获取玩家成就记录
        result = await db.execute(
            select(PlayerAchievement).where(
                PlayerAchievement.player_id == player.id,
                PlayerAchievement.achievement_id == achievement_id
            )
        )
        player_ach = result.scalar_one_or_none()

        if not player_ach or not player_ach.is_completed:
            return False, "成就未完成", {}

        if player_ach.is_claimed:
            return False, "奖励已领取", {}

        # 发放奖励
        rewards = {
            "exp": achievement.exp_reward,
            "spirit_stones": achievement.spirit_stones_reward,
            "points": achievement.points,
            "item": None,
            "title": None
        }

        # 灵石奖励
        if achievement.spirit_stones_reward > 0:
            player.spirit_stones += achievement.spirit_stones_reward

        # 经验奖励
        if achievement.exp_reward > 0:
            player.cultivation_exp += achievement.exp_reward

        # 物品奖励
        if achievement.reward_item_id:
            result = await db.execute(
                select(Item).where(Item.id == achievement.reward_item_id)
            )
            item = result.scalar_one_or_none()
            if item:
                # 添加到背包
                result = await db.execute(
                    select(PlayerInventory).where(
                        PlayerInventory.player_id == player.id,
                        PlayerInventory.item_id == achievement.reward_item_id,
                        PlayerInventory.is_equipped == False
                    )
                )
                inv = result.scalar_one_or_none()

                if inv and item.is_stackable:
                    inv.quantity += achievement.reward_item_quantity
                else:
                    new_inv = PlayerInventory(
                        player_id=player.id,
                        item_id=achievement.reward_item_id,
                        quantity=achievement.reward_item_quantity
                    )
                    db.add(new_inv)

                rewards["item"] = {
                    "name": item.name,
                    "quantity": achievement.reward_item_quantity
                }

        # 称号奖励
        if achievement.title:
            # 检查是否已有该称号
            result = await db.execute(
                select(PlayerTitle).where(
                    PlayerTitle.player_id == player.id,
                    PlayerTitle.title == achievement.title
                )
            )
            existing_title = result.scalar_one_or_none()

            if not existing_title:
                new_title = PlayerTitle(
                    player_id=player.id,
                    title=achievement.title,
                    source=achievement.name
                )
                db.add(new_title)
                rewards["title"] = achievement.title

        # 更新统计
        stats = await AchievementService.get_or_create_stats(db, player.id)
        stats.completed_achievements += 1
        stats.total_points += achievement.points
        stats.last_achievement_time = datetime.now()

        # 更新分类统计
        category_field = f"{achievement.category.value}_count"
        if hasattr(stats, category_field):
            setattr(stats, category_field, getattr(stats, category_field) + 1)

        # 标记为已领取
        player_ach.is_claimed = True
        player_ach.claimed_at = datetime.now()

        await db.commit()

        return True, "领取成功", rewards

    @staticmethod
    async def get_player_achievements(
        db: AsyncSession,
        player_id: int,
        category: Optional[AchievementCategory] = None,
        completed_only: bool = False
    ) -> List[Dict]:
        """获取玩家成就列表"""
        # 构建查询
        query = select(Achievement, PlayerAchievement).outerjoin(
            PlayerAchievement,
            (PlayerAchievement.achievement_id == Achievement.id) &
            (PlayerAchievement.player_id == player_id)
        )

        # 分类过滤
        if category:
            query = query.where(Achievement.category == category.value)

        # 完成过滤
        if completed_only:
            query = query.where(PlayerAchievement.is_completed == True)

        # 排序
        query = query.order_by(Achievement.category, Achievement.id)

        result = await db.execute(query)
        items = result.all()

        achievements_list = []
        for achievement, player_ach in items:
            # 隐藏成就未完成时不显示
            if achievement.is_hidden and (not player_ach or not player_ach.is_completed):
                continue

            ach_data = {
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "icon": achievement.icon,
                "category": achievement.category,
                "condition_type": achievement.condition_type,
                "condition_value": achievement.condition_value,
                "points": achievement.points,
                "is_hidden": achievement.is_hidden,
                "current_progress": player_ach.current_progress if player_ach else 0,
                "is_completed": player_ach.is_completed if player_ach else False,
                "is_claimed": player_ach.is_claimed if player_ach else False,
                "completed_at": player_ach.completed_at if player_ach else None,
                "claimed_at": player_ach.claimed_at if player_ach else None
            }
            achievements_list.append(ach_data)

        return achievements_list

    @staticmethod
    async def get_achievement_summary(db: AsyncSession, player_id: int) -> Dict:
        """获取成就概览"""
        stats = await AchievementService.get_or_create_stats(db, player_id)

        # 获取总成就数
        result = await db.execute(select(func.count(Achievement.id)))
        total_count = result.scalar()

        # 获取可领取数量
        result = await db.execute(
            select(func.count(PlayerAchievement.id)).where(
                PlayerAchievement.player_id == player_id,
                PlayerAchievement.is_completed == True,
                PlayerAchievement.is_claimed == False
            )
        )
        claimable_count = result.scalar()

        return {
            "total_achievements": total_count,
            "completed_achievements": stats.completed_achievements,
            "completion_rate": stats.completed_achievements / total_count if total_count > 0 else 0,
            "total_points": stats.total_points,
            "claimable_count": claimable_count,
            "last_achievement_time": stats.last_achievement_time,
            "category_stats": {
                "cultivation": stats.cultivation_count,
                "combat": stats.combat_count,
                "collection": stats.collection_count,
                "crafting": stats.crafting_count,
                "exploration": stats.exploration_count,
                "social": stats.social_count,
                "wealth": stats.wealth_count,
                "special": stats.special_count
            }
        }

    @staticmethod
    async def get_player_titles(db: AsyncSession, player_id: int) -> List[PlayerTitle]:
        """获取玩家称号列表"""
        result = await db.execute(
            select(PlayerTitle).where(
                PlayerTitle.player_id == player_id
            ).order_by(PlayerTitle.obtained_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def set_active_title(
        db: AsyncSession,
        player_id: int,
        title_id: Optional[int]
    ) -> Tuple[bool, str]:
        """设置激活称号"""
        # 取消所有激活的称号
        result = await db.execute(
            select(PlayerTitle).where(
                PlayerTitle.player_id == player_id,
                PlayerTitle.is_active == True
            )
        )
        active_titles = result.scalars().all()
        for title in active_titles:
            title.is_active = False

        # 如果指定了新称号
        if title_id:
            result = await db.execute(
                select(PlayerTitle).where(
                    PlayerTitle.id == title_id,
                    PlayerTitle.player_id == player_id
                )
            )
            new_title = result.scalar_one_or_none()

            if not new_title:
                return False, "称号不存在"

            new_title.is_active = True
            await db.commit()
            return True, f"已装备称号: {new_title.title}"
        else:
            await db.commit()
            return True, "已卸下称号"
