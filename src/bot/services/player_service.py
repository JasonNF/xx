"""玩家相关服务"""
import random
from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Player, RealmType, PlayerInventory, Item, SpiritRoot
from bot.config import settings


class PlayerService:
    """玩家服务类"""

    @staticmethod
    async def get_or_create_player(
        db: AsyncSession,
        telegram_id: int,
        username: Optional[str],
        first_name: str
    ) -> Tuple[Player, bool]:
        """获取或创建玩家

        Returns:
            (player, is_new): 玩家对象和是否新创建
        """
        # 查询玩家
        result = await db.execute(
            select(Player).where(Player.telegram_id == telegram_id)
        )
        player = result.scalar_one_or_none()

        if player:
            # 更新用户信息
            player.username = username
            player.first_name = first_name
            await db.commit()
            return player, False

        # 创建新玩家
        player = Player(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            nickname=first_name,  # 默认使用first_name
            realm=RealmType.MORTAL,
            realm_level=0,
            # 随机初始属性
            comprehension=random.randint(8, 15),
            spirit_stones=settings.NEWBIE_GIFT,
        )

        db.add(player)
        await db.commit()
        await db.refresh(player)

        # 自动生成灵根
        from bot.services.spirit_root_service import SpiritRootService
        spirit_root = await SpiritRootService.generate_spirit_root(db, player)

        # 重新刷新玩家对象以加载灵根关系
        await db.refresh(player)

        return player, True

    @staticmethod
    async def get_player(db: AsyncSession, telegram_id: int) -> Optional[Player]:
        """通过Telegram ID获取玩家"""
        result = await db.execute(
            select(Player).where(Player.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_player_attributes(db: AsyncSession, player: Player) -> None:
        """根据境界更新玩家属性"""
        # 使用累计总层数计算，确保突破后属性递增
        total_level = PlayerService._calculate_total_realm_level(player.realm, player.realm_level)

        # 基础属性计算（使用累计层数）
        base_multiplier = total_level

        # 更新最大HP和灵力
        player.max_hp = 100 + base_multiplier * 50
        player.max_spiritual_power = 100 + base_multiplier * 30

        # 更新攻防速度
        player.attack = 10 + base_multiplier * 5
        player.defense = 5 + base_multiplier * 3
        player.speed = 10 + base_multiplier * 2

        # 恢复HP和灵力
        player.hp = player.max_hp
        player.spiritual_power = player.max_spiritual_power

        # 计算下一境界所需修为
        from bot.config.realm_config import RealmConfig
        player.next_realm_exp = RealmConfig.get_next_realm_exp(player.realm, player.realm_level)

        await db.commit()

    @staticmethod
    def _calculate_total_realm_level(realm: RealmType, realm_level: int) -> int:
        """计算从凡人到当前境界的累计总层数

        确保突破后属性持续递增，不会出现倒退

        Args:
            realm: 当前大境界
            realm_level: 当前小境界等级

        Returns:
            累计总层数

        Examples:
            凡人: 0
            炼气1层: 1
            炼气13层: 13
            筑基初期: 16 (13 + 3)
            筑基中期: 19 (13 + 6)
            筑基后期: 22 (13 + 9)
            结丹初期: 27 (22 + 5)
            ...
        """
        if realm == RealmType.MORTAL:
            return 0
        elif realm == RealmType.QI_REFINING:
            return realm_level  # 1-13
        elif realm == RealmType.FOUNDATION:
            return 13 + (realm_level + 1) * 3  # 16/19/22
        elif realm == RealmType.CORE_FORMATION:
            return 22 + (realm_level + 1) * 5  # 27/32/37
        elif realm == RealmType.NASCENT_SOUL:
            return 37 + (realm_level + 1) * 7  # 44/51/58
        elif realm == RealmType.DEITY_TRANSFORMATION:
            return 58 + (realm_level + 1) * 10  # 68/78/88
        else:
            return 0

    @staticmethod
    async def can_breakthrough(player: Player) -> Tuple[bool, str]:
        """检查是否可以突破

        Returns:
            (can_breakthrough, reason)
        """
        if player.cultivation_exp < player.next_realm_exp:
            return False, f"修为不足，还需要 {player.next_realm_exp - player.cultivation_exp} 修为"

        if player.is_cultivating:
            return False, "正在修炼中，无法突破"

        if player.is_in_battle:
            return False, "战斗中无法突破"

        return True, ""

    @staticmethod
    async def breakthrough(db: AsyncSession, player: Player) -> Tuple[bool, str]:
        """突破境界

        Returns:
            (success, message)
        """
        from bot.config.realm_config import RealmConfig

        can_break, reason = await PlayerService.can_breakthrough(player)
        if not can_break:
            return False, reason

        # 检查是否已达到最高境界
        if player.realm == RealmType.DEITY_TRANSFORMATION and player.realm_level >= 2:
            return False, "已达化神后期圆满，无法继续突破（需飞升）"

        # 获取基础成功率（根据境界难度）
        base_success_rate = RealmConfig.get_breakthrough_base_chance(player.realm, player.realm_level)

        # 计算最终突破成功率
        success_rate = base_success_rate

        # 悟性影响成功率（每点+1%）
        success_rate += player.comprehension * 0.01

        # 灵根影响成功率
        if player.spirit_root:
            success_rate += player.spirit_root.breakthrough_bonus

        # 限制范围
        success_rate = max(0.05, min(0.95, success_rate))

        # 记录突破前信息
        old_realm_name = player.full_realm_name

        # 判定突破
        if random.random() < success_rate:
            # 突破成功！
            next_realm, next_level = RealmConfig.get_next_realm_info(player.realm, player.realm_level)

            # 更新境界
            player.realm = next_realm
            player.realm_level = next_level

            # 消耗修为
            player.cultivation_exp -= player.next_realm_exp

            # 更新下一境界所需修为
            player.next_realm_exp = RealmConfig.get_next_realm_exp(player.realm, player.realm_level)

            # 更新属性
            await PlayerService.update_player_attributes(db, player)

            # 突破大境界时的特殊奖励
            breakthrough_bonus = ""
            if player.realm != next_realm:
                # 大境界突破
                if player.realm == RealmType.FOUNDATION:
                    # 筑基期觉醒神识
                    player.divine_sense = 100
                    player.max_divine_sense = 100
                    breakthrough_bonus = "\n✨ 觉醒神识！"
                elif player.realm == RealmType.CORE_FORMATION:
                    # 结丹期寿元大增
                    player.lifespan += 300
                    breakthrough_bonus = "\n🎂 寿元增加300年！"
                elif player.realm == RealmType.NASCENT_SOUL:
                    # 元婴期寿元大增
                    player.lifespan += 500
                    breakthrough_bonus = "\n🎂 寿元增加500年！"
                elif player.realm == RealmType.DEITY_TRANSFORMATION:
                    # 化神期寿元大增
                    player.lifespan += 1000
                    breakthrough_bonus = "\n🎂 寿元增加1000年！\n🌟 人界巅峰！"

            await db.commit()

            success_message = f"""🎉 突破成功！

{old_realm_name} → {player.full_realm_name}
战力提升至: {player.combat_power}
下一境界需: {player.next_realm_exp:,} 修为{breakthrough_bonus}"""

            return True, success_message
        else:
            # 突破失败
            # 失败惩罚：损失10-30%修为，境界越高损失越多
            loss_ratio = 0.1 + (list(RealmType).index(player.realm) * 0.03)
            loss_ratio = min(0.3, loss_ratio)
            loss = int(player.next_realm_exp * loss_ratio)

            player.cultivation_exp = max(0, player.cultivation_exp - loss)

            # 大境界突破失败可能受伤
            damage_message = ""
            if player.realm_level >= 2 or player.realm in [
                RealmType.CORE_FORMATION,
                RealmType.NASCENT_SOUL,
                RealmType.DEITY_TRANSFORMATION
            ]:
                # 高级突破失败，受到反噬
                damage = int(player.max_hp * 0.2)
                player.hp = max(1, player.hp - damage)
                damage_message = f"\n💔 遭受反噬，损失 {damage} 生命值"

            await db.commit()

            fail_message = f"""💥 突破失败！

损失修为: {loss:,} (-{loss_ratio*100:.0f}%){damage_message}

💡 提示: 提升悟性和灵根品质可增加突破成功率"""

            return False, fail_message

    @staticmethod
    async def daily_sign(db: AsyncSession, player: Player) -> Tuple[bool, str, int]:
        """每日签到

        Returns:
            (success, message, reward)
        """
        today = datetime.now().date()

        # 检查是否已签到
        if player.last_sign_date and player.last_sign_date.date() == today:
            return False, "今天已经签到过了", 0

        # 检查连续签到
        if player.last_sign_date:
            yesterday = today - timedelta(days=1)
            if player.last_sign_date.date() == yesterday:
                player.continuous_sign_days += 1
            else:
                player.continuous_sign_days = 1
        else:
            player.continuous_sign_days = 1

        # 计算奖励（连续签到奖励递增）
        base_reward = settings.DAILY_SIGN_REWARD
        bonus = min(player.continuous_sign_days - 1, 7) * 100
        total_reward = base_reward + bonus

        # 积分奖励（已平衡优化：10 → 50积分/天）
        daily_credits = 50
        credit_bonus = min(player.continuous_sign_days - 1, 7) * 5  # 连续签到额外积分
        total_credits = daily_credits + credit_bonus

        # 发放奖励
        player.spirit_stones += total_reward
        player.credits += total_credits  # 同时发放积分
        player.last_sign_date = datetime.now()

        await db.commit()

        return True, f"签到成功！连续签到 {player.continuous_sign_days} 天\n获得 {total_credits} 积分", total_reward
