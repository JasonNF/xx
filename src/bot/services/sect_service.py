"""宗门服务 - 核心业务逻辑"""
from datetime import datetime
from typing import Optional, Tuple, Dict, List
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Player, Sect, SectShopItem, SectContribution, Item, PlayerInventory
from bot.models.sect import SectApplication


class SectService:
    """宗门服务类"""

    # 职位系统 - 按声望晋升
    # contribution字段作为宗门声望使用
    SECT_POSITIONS = [
        {"name": "外门弟子", "reputation_required": 0, "level": 1},
        {"name": "内门弟子", "reputation_required": 1000, "level": 2},
        {"name": "真传弟子", "reputation_required": 5000, "level": 3},
        {"name": "执事", "reputation_required": 10000, "level": 4},
        {"name": "堂主", "reputation_required": 20000, "level": 5},
        {"name": "长老", "reputation_required": 50000, "level": 6},
        {"name": "掌门", "reputation_required": 100000, "level": 7},  # 通过挑战获得
    ]

    # 宗门等级配置(影响加入所需声望)
    SECT_TIERS = {
        1: {"name": "小型宗门", "join_reputation": 0, "challenge_reward": 5000},
        2: {"name": "中型宗门", "join_reputation": 500, "challenge_reward": 10000},
        3: {"name": "大型宗门", "join_reputation": 1000, "challenge_reward": 20000},
        4: {"name": "顶级宗门", "join_reputation": 3000, "challenge_reward": 50000},
        5: {"name": "圣地宗门", "join_reputation": 10000, "challenge_reward": 100000},
    }

    # 宗门任务奖励声望配置
    TASK_REPUTATION_REWARDS = {
        "daily": 50,      # 日常任务
        "weekly": 200,    # 周常任务
        "special": 500,   # 特殊任务
        "contribution": 1  # 捐献灵石也可获得少量声望
    }

    @staticmethod
    def get_position_by_reputation(reputation: int) -> Dict:
        """根据声望获取对应职位"""
        current_position = SectService.SECT_POSITIONS[0]
        for position in SectService.SECT_POSITIONS:
            if reputation >= position["reputation_required"]:
                current_position = position
            else:
                break
        return current_position

    @staticmethod
    def get_next_position(current_reputation: int) -> Optional[Dict]:
        """获取下一个职位所需声望"""
        for position in SectService.SECT_POSITIONS:
            if current_reputation < position["reputation_required"]:
                return position
        return None

    @staticmethod
    async def join_sect(
        db: AsyncSession,
        player: Player,
        sect: Sect
    ) -> Tuple[bool, str]:
        """加入宗门"""
        # 检查是否已在宗门
        if player.sect_id:
            return False, "你已经在宗门中，请先退出当前宗门"

        # 检查宗门等级要求
        tier_config = SectService.SECT_TIERS.get(sect.level, SectService.SECT_TIERS[1])
        required_reputation = tier_config["join_reputation"]

        # 注意: contribution字段现在作为总累积声望使用
        # 加入宗门会消耗声望,但玩家的总声望(contribution)不会减少
        # 我们需要新增一个字段来记录"可用声望"
        # 临时方案: 检查玩家的contribution是否足够
        if player.contribution < required_reputation:
            return False, f"加入该宗门需要{required_reputation}声望，你当前拥有{player.contribution}声望"

        # 检查成员数量
        result = await db.execute(
            select(func.count(Player.id)).where(Player.sect_id == sect.id)
        )
        member_count = result.scalar()

        if member_count >= sect.max_members:
            return False, "该宗门已满员"

        # 加入宗门 - 消耗声望但总声望保留
        player.sect_id = sect.id
        player.sect_position = "外门弟子"
        # contribution字段保持不变,作为总累积声望

        await db.commit()

        return True, f"成功加入 {sect.name}！当前职位：外门弟子"

    @staticmethod
    async def leave_sect(
        db: AsyncSession,
        player: Player
    ) -> Tuple[bool, str]:
        """退出宗门"""
        if not player.sect_id:
            return False, "你还没有加入宗门"

        # 获取宗门信息
        result = await db.execute(
            select(Sect).where(Sect.id == player.sect_id)
        )
        sect = result.scalar_one_or_none()

        if not sect:
            return False, "宗门不存在"

        # 检查是否为掌门
        if sect.master_id == player.id:
            return False, "掌门不能直接退出宗门，请先禅让掌门之位"

        sect_name = sect.name

        # 退出宗门 - 保留已学功法和总声望
        player.sect_id = None
        player.sect_position = None
        # contribution(总声望)保留

        await db.commit()

        return True, f"你已退出 {sect_name}，已学功法和总声望已保留"

    @staticmethod
    async def get_available_cultivation_methods(
        db: AsyncSession,
        player: Player
    ) -> List[Dict]:
        """获取玩家可学习的宗门功法列表"""
        if not player.sect_id:
            return []

        # 获取当前职位等级
        position = SectService.get_position_by_reputation(player.contribution)
        position_level = position["level"]

        # TODO: 根据职位等级返回可学习的功法
        # 需要配合功法系统,这里返回占位数据
        return []

    @staticmethod
    async def challenge_master(
        db: AsyncSession,
        challenger: Player,
        sect: Sect
    ) -> Tuple[bool, str, Optional[int]]:
        """挑战掌门"""
        if not challenger.sect_id or challenger.sect_id != sect.id:
            return False, "你必须是本宗门成员才能挑战掌门", None

        if sect.master_id == challenger.id:
            return False, "你已经是掌门了", None

        # 检查职位要求 - 至少要是长老
        position = SectService.get_position_by_reputation(challenger.contribution)
        if position["level"] < 6:  # 长老级别
            return False, f"只有长老及以上才能挑战掌门，当前职位：{position['name']}", None

        # 获取现任掌门
        if not sect.master_id:
            # 无掌门,直接晋升
            sect.master_id = challenger.id
            challenger.sect_position = "掌门"

            tier_config = SectService.SECT_TIERS.get(sect.level, SectService.SECT_TIERS[1])
            reputation_reward = tier_config["challenge_reward"]
            challenger.contribution += reputation_reward

            await db.commit()

            return True, "该宗门无掌门，你成功继任掌门之位！", reputation_reward

        # 有掌门,需要战斗
        result = await db.execute(
            select(Player).where(Player.id == sect.master_id)
        )
        current_master = result.scalar_one_or_none()

        if not current_master:
            # 掌门不存在,直接晋升
            sect.master_id = challenger.id
            challenger.sect_position = "掌门"

            tier_config = SectService.SECT_TIERS.get(sect.level, SectService.SECT_TIERS[1])
            reputation_reward = tier_config["challenge_reward"]
            challenger.contribution += reputation_reward

            await db.commit()

            return True, "原掌门已不在，你成功继任掌门之位！", reputation_reward

        # 返回掌门信息,由战斗系统处理实际战斗
        # 战斗胜利后需要调用complete_master_challenge
        return True, f"挑战掌门 {current_master.nickname}，请准备战斗！", current_master.id

    @staticmethod
    async def complete_master_challenge(
        db: AsyncSession,
        winner: Player,
        loser: Player,
        sect: Sect
    ) -> Tuple[bool, str]:
        """完成掌门挑战(战斗胜利后调用)"""
        # 更换掌门
        old_master_name = loser.nickname
        sect.master_id = winner.id

        # 更新职位
        winner.sect_position = "掌门"
        loser.sect_position = "长老"  # 原掌门降为长老

        # 获得声望奖励和宗门资源
        tier_config = SectService.SECT_TIERS.get(sect.level, SectService.SECT_TIERS[1])
        reputation_reward = tier_config["challenge_reward"]
        winner.contribution += reputation_reward

        # 获得部分宗门资源
        treasury_gain = sect.treasury // 10  # 获得10%宗门金库
        winner.spirit_stones += treasury_gain
        sect.treasury -= treasury_gain

        await db.commit()

        return True, f"挑战成功！你击败了 {old_master_name}，成为新任掌门！\n获得：{reputation_reward}声望，{treasury_gain}灵石"

    @staticmethod
    async def donate_to_sect(
        db: AsyncSession,
        player: Player,
        amount: int
    ) -> Tuple[bool, str, int]:
        """向宗门捐献灵石，获得声望"""
        if not player.sect_id:
            return False, "你还没有加入宗门", 0

        if amount <= 0:
            return False, "捐献数量必须大于0", 0

        if player.spirit_stones < amount:
            return False, f"灵石不足，需要{amount}，拥有{player.spirit_stones}", 0

        # 获取宗门
        result = await db.execute(
            select(Sect).where(Sect.id == player.sect_id)
        )
        sect = result.scalar_one_or_none()

        if not sect:
            return False, "宗门不存在", 0

        # 计算声望收益 - 捐献也可获得少量声望
        reputation_gain = amount // 100  # 100灵石 = 1声望

        # 扣除灵石，增加声望
        player.spirit_stones -= amount
        player.contribution += reputation_gain

        # 增加宗门金库
        sect.treasury += amount

        # 检查是否晋升职位
        new_position = SectService.get_position_by_reputation(player.contribution)
        old_position_name = player.sect_position or "外门弟子"

        # 如果不是掌门,自动晋升职位
        if new_position["name"] != old_position_name and sect.master_id != player.id:
            if new_position["name"] != "掌门":  # 掌门需要挑战获得
                player.sect_position = new_position["name"]

        # 记录贡献
        contribution_record = SectContribution(
            sect_id=sect.id,
            player_id=player.id,
            contribution_type="donate",
            amount=reputation_gain,
            description=f"捐献{amount}灵石"
        )
        db.add(contribution_record)

        await db.commit()

        return True, "捐献成功", reputation_gain

    @staticmethod
    async def complete_sect_task(
        db: AsyncSession,
        player: Player,
        task_type: str
    ) -> Tuple[bool, str, int]:
        """完成宗门任务，获得声望"""
        if not player.sect_id:
            return False, "你还没有加入宗门", 0

        reputation_reward = SectService.TASK_REPUTATION_REWARDS.get(task_type, 0)
        if reputation_reward == 0:
            return False, "无效的任务类型", 0

        # 增加声望
        player.contribution += reputation_reward

        # 检查是否晋升
        result = await db.execute(
            select(Sect).where(Sect.id == player.sect_id)
        )
        sect = result.scalar_one_or_none()

        if sect:
            new_position = SectService.get_position_by_reputation(player.contribution)
            old_position_name = player.sect_position or "外门弟子"

            if new_position["name"] != old_position_name and sect.master_id != player.id:
                if new_position["name"] != "掌门":
                    player.sect_position = new_position["name"]

        # 记录贡献
        contribution_record = SectContribution(
            sect_id=player.sect_id,
            player_id=player.id,
            contribution_type="task",
            amount=reputation_reward,
            description=f"完成{task_type}任务"
        )
        db.add(contribution_record)

        await db.commit()

        return True, f"任务完成，获得{reputation_reward}声望", reputation_reward

    @staticmethod
    async def get_sect_info(db: AsyncSession, sect_id: int) -> Optional[Dict]:
        """获取宗门详细信息"""
        result = await db.execute(
            select(Sect).where(Sect.id == sect_id)
        )
        sect = result.scalar_one_or_none()

        if not sect:
            return None

        # 获取成员数量
        result = await db.execute(
            select(func.count(Player.id)).where(Player.sect_id == sect.id)
        )
        member_count = result.scalar()

        # 获取掌门信息
        master_name = "虚位以待"
        if sect.master_id:
            result = await db.execute(
                select(Player).where(Player.id == sect.master_id)
            )
            master = result.scalar_one_or_none()
            if master:
                master_name = master.nickname

        # 获取宗门等级配置
        tier_config = SectService.SECT_TIERS.get(sect.level, SectService.SECT_TIERS[1])

        return {
            "sect": sect,
            "member_count": member_count,
            "master_name": master_name,
            "tier_name": tier_config["name"],
            "join_reputation": tier_config["join_reputation"]
        }

    @staticmethod
    async def get_sect_members(
        db: AsyncSession,
        sect_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """获取宗门成员列表(按声望排序)"""
        result = await db.execute(
            select(Player)
            .where(Player.sect_id == sect_id)
            .order_by(Player.contribution.desc())
            .limit(limit)
            .offset(offset)
        )
        members = result.scalars().all()

        member_list = []
        for member in members:
            position = SectService.get_position_by_reputation(member.contribution)
            member_list.append({
                "id": member.id,
                "nickname": member.nickname,
                "realm": member.full_realm_name,
                "level": member.level,
                "position": member.sect_position or position["name"],
                "reputation": member.contribution
            })

        return member_list

    @staticmethod
    def get_library_bonus(library_level: int) -> float:
        """获取藏经阁修炼加成"""
        return 1.0 + (library_level * 0.05)  # 每级+5%

    @staticmethod
    def get_alchemy_bonus(alchemy_level: int) -> float:
        """获取炼丹房成功率加成"""
        return alchemy_level * 0.03  # 每级+3%

    @staticmethod
    def get_refinery_bonus(refinery_level: int) -> float:
        """获取炼器阁成功率加成"""
        return refinery_level * 0.03  # 每级+3%
