"""任务系统handlers - 凡人修仙传版本"""
import json
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.models.database import AsyncSessionLocal
from bot.models import Player, Quest, PlayerQuest, QuestType, QuestStatus
from sqlalchemy import select, and_


async def quests_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看任务列表 - /quests [类型]"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        # 获取玩家
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 解析任务类型过滤
        quest_type_filter = None
        if context.args:
            type_map = {
                "主线": QuestType.MAIN,
                "每日": QuestType.DAILY,
                "每周": QuestType.WEEKLY,
                "宗门": QuestType.SECT,
            }
            quest_type_filter = type_map.get(context.args[0])

        # 获取所有任务
        query = select(Quest)
        if quest_type_filter:
            query = query.where(Quest.quest_type == quest_type_filter)
        result = await session.execute(query.order_by(Quest.id))
        all_quests = result.scalars().all()

        # 获取玩家任务进度
        result = await session.execute(
            select(PlayerQuest).where(PlayerQuest.player_id == player.id)
        )
        player_quests = {pq.quest_id: pq for pq in result.scalars().all()}

        # 分类任务
        available_quests = []  # 可接取
        in_progress_quests = []  # 进行中
        completed_quests = []  # 已完成

        for quest in all_quests:
            player_quest = player_quests.get(quest.id)

            # 检查是否满足接取条件
            can_accept = True
            reason = ""

            # 检查境界要求
            if quest.required_realm:
                if quest.required_realm not in player.full_realm_name:
                    can_accept = False
                    reason = f"需要{quest.required_realm}"

            # 检查等级要求
            if can_accept and player.realm_level < quest.required_level:
                can_accept = False
                reason = f"需要{quest.required_level}级"

            # 检查前置任务
            if can_accept and quest.prerequisite_quest_id:
                prereq_quest = player_quests.get(quest.prerequisite_quest_id)
                if not prereq_quest or prereq_quest.status != QuestStatus.CLAIMED:
                    can_accept = False
                    reason = "需要完成前置任务"

            # 检查冷却时间（可重复任务）
            if can_accept and player_quest and player_quest.next_available_at:
                if datetime.now() < player_quest.next_available_at:
                    can_accept = False
                    remaining = player_quest.next_available_at - datetime.now()
                    hours = int(remaining.total_seconds() // 3600)
                    reason = f"冷却中({hours}小时)"

            quest_info = {
                "quest": quest,
                "player_quest": player_quest,
                "can_accept": can_accept,
                "reason": reason,
            }

            if player_quest:
                if player_quest.status == QuestStatus.IN_PROGRESS:
                    in_progress_quests.append(quest_info)
                elif player_quest.status == QuestStatus.COMPLETED:
                    completed_quests.append(quest_info)
                elif player_quest.status == QuestStatus.CLAIMED and not quest.is_repeatable:
                    continue  # 已完成的不可重复任务不显示
                elif player_quest.status == QuestStatus.CLAIMED and quest.is_repeatable:
                    if can_accept:
                        available_quests.append(quest_info)
                else:
                    available_quests.append(quest_info)
            else:
                if can_accept:
                    available_quests.append(quest_info)

        # 构建消息
        msg = "📜 【任务列表】\n\n"
        msg += f"道友境界：{player.full_realm_name}\n"
        msg += "━━━━━━━━━━━━━━\n\n"

        # 进行中的任务
        if in_progress_quests:
            msg += "🔄 **进行中**\n\n"
            for info in in_progress_quests:
                quest = info["quest"]
                pq = info["player_quest"]
                progress_pct = int((pq.current_progress / quest.objective_count) * 100)

                type_icon = {"main": "📖", "daily": "⏰", "weekly": "📅", "sect": "🏛️"}.get(
                    quest.quest_type.value, "📜"
                )
                msg += f"{type_icon} **{quest.name}**\n"
                msg += f"   {quest.description}\n"
                msg += f"   📊 进度：{pq.current_progress}/{quest.objective_count} ({progress_pct}%)\n"

                if pq.current_progress >= quest.objective_count:
                    msg += f"   ✅ 可完成 - 使用 /完成 {quest.id}\n"

                msg += "\n"

            msg += "━━━━━━━━━━━━━━\n\n"

        # 可接取的任务
        if available_quests:
            msg += "✨ **可接取**\n\n"
            for info in available_quests[:5]:  # 只显示前5个
                quest = info["quest"]

                type_icon = {"main": "📖", "daily": "⏰", "weekly": "📅", "sect": "🏛️"}.get(
                    quest.quest_type.value, "📜"
                )
                msg += f"{type_icon} **{quest.name}**\n"
                msg += f"   {quest.description}\n"
                msg += f"   🎁 奖励：{quest.exp_reward}修为"
                if quest.spirit_stones_reward > 0:
                    msg += f" + {quest.spirit_stones_reward}灵石"
                msg += "\n"

                if quest.required_realm or quest.required_level > 1:
                    msg += f"   📖 要求："
                    if quest.required_realm:
                        msg += f"{quest.required_realm} "
                    if quest.required_level > 1:
                        msg += f"{quest.required_level}级"
                    msg += "\n"

                msg += f"   💡 /接取 {quest.id}\n"
                msg += "\n"

            if len(available_quests) > 5:
                msg += f"   ...还有{len(available_quests) - 5}个任务\n\n"

            msg += "━━━━━━━━━━━━━━\n\n"

        # 已完成待领取
        if completed_quests:
            msg += "🎉 **已完成**\n\n"
            for info in completed_quests:
                quest = info["quest"]
                msg += f"✅ **{quest.name}**\n"
                msg += f"   💡 /完成 {quest.id} 领取奖励\n\n"

            msg += "━━━━━━━━━━━━━━\n\n"

        if not in_progress_quests and not available_quests and not completed_quests:
            msg += "当前没有可用任务\n\n"

        msg += "💡 筛选：/任务 [主线|每日|每周|宗门]"

        await update.message.reply_text(msg, parse_mode="Markdown")


async def accept_quest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """接取任务 - /accept_quest <任务ID>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定任务ID\n"
            "用法：/接取 <任务ID>\n"
            "使用 /任务 查看可接取任务"
        )
        return

    try:
        quest_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ 任务ID必须是数字")
        return

    async with AsyncSessionLocal() as session:
        # 获取玩家
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 获取任务
        result = await session.execute(select(Quest).where(Quest.id == quest_id))
        quest = result.scalar_one_or_none()

        if not quest:
            await update.message.reply_text(f"❌ 未找到任务ID: {quest_id}")
            return

        # 检查是否已接取
        result = await session.execute(
            select(PlayerQuest).where(
                and_(
                    PlayerQuest.player_id == player.id,
                    PlayerQuest.quest_id == quest_id,
                )
            )
        )
        player_quest = result.scalar_one_or_none()

        if player_quest:
            if player_quest.status == QuestStatus.IN_PROGRESS:
                await update.message.reply_text("❌ 任务已在进行中")
                return
            elif player_quest.status == QuestStatus.COMPLETED:
                await update.message.reply_text("❌ 任务已完成，请先领取奖励")
                return
            elif player_quest.status == QuestStatus.CLAIMED and not quest.is_repeatable:
                await update.message.reply_text("❌ 此任务不可重复")
                return

        # 检查接取条件
        # 境界要求
        if quest.required_realm:
            if quest.required_realm not in player.full_realm_name:
                await update.message.reply_text(f"❌ 需要{quest.required_realm}境界")
                return

        # 等级要求
        if player.realm_level < quest.required_level:
            await update.message.reply_text(f"❌ 需要达到{quest.required_level}级")
            return

        # 前置任务
        if quest.prerequisite_quest_id:
            result = await session.execute(
                select(PlayerQuest).where(
                    and_(
                        PlayerQuest.player_id == player.id,
                        PlayerQuest.quest_id == quest.prerequisite_quest_id,
                    )
                )
            )
            prereq_quest = result.scalar_one_or_none()
            if not prereq_quest or prereq_quest.status != QuestStatus.CLAIMED:
                await update.message.reply_text("❌ 需要完成前置任务")
                return

        # 冷却时间
        if player_quest and player_quest.next_available_at:
            if datetime.now() < player_quest.next_available_at:
                remaining = player_quest.next_available_at - datetime.now()
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                await update.message.reply_text(f"❌ 任务冷却中，还需{hours}小时{minutes}分钟")
                return

        # 创建或更新任务记录
        if player_quest:
            player_quest.status = QuestStatus.IN_PROGRESS
            player_quest.current_progress = 0
            player_quest.accepted_at = datetime.now()
            player_quest.completed_at = None
            player_quest.claimed_at = None
            player_quest.next_available_at = None
        else:
            player_quest = PlayerQuest(
                player_id=player.id,
                quest_id=quest_id,
                status=QuestStatus.IN_PROGRESS,
                current_progress=0,
                accepted_at=datetime.now(),
            )
            session.add(player_quest)

        await session.commit()

        type_icon = {"main": "📖", "daily": "⏰", "weekly": "📅", "sect": "🏛️"}.get(
            quest.quest_type.value, "📜"
        )

        msg = f"✅ 接取任务成功！\n\n"
        msg += f"{type_icon} **{quest.name}**\n"
        msg += f"{quest.description}\n\n"
        msg += f"📊 目标：{quest.objective_type} {quest.objective_target or ''}\n"
        msg += f"   需要完成：{quest.objective_count}次\n\n"
        msg += f"🎁 奖励：\n"
        msg += f"   ⭐ 修为：{quest.exp_reward}\n"
        if quest.spirit_stones_reward > 0:
            msg += f"   💰 灵石：{quest.spirit_stones_reward}\n"
        if quest.contribution_reward > 0:
            msg += f"   🏛️ 宗门贡献：{quest.contribution_reward}\n"

        if quest.item_rewards:
            try:
                items = json.loads(quest.item_rewards)
                msg += "   🎁 物品：\n"
                for item in items:
                    msg += f"      • {item['item_name']} x{item['quantity']}\n"
            except:
                pass

        msg += "\n💡 完成后使用 /完成 领取奖励"

        await update.message.reply_text(msg, parse_mode="Markdown")


async def complete_quest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """完成任务并领取奖励 - /complete_quest <任务ID>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定任务ID\n"
            "用法：/完成 <任务ID>\n"
            "使用 /任务 查看任务列表"
        )
        return

    try:
        quest_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ 任务ID必须是数字")
        return

    async with AsyncSessionLocal() as session:
        # 获取玩家
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 获取任务和玩家任务记录
        result = await session.execute(select(Quest).where(Quest.id == quest_id))
        quest = result.scalar_one_or_none()

        if not quest:
            await update.message.reply_text(f"❌ 未找到任务ID: {quest_id}")
            return

        result = await session.execute(
            select(PlayerQuest).where(
                and_(
                    PlayerQuest.player_id == player.id,
                    PlayerQuest.quest_id == quest_id,
                )
            )
        )
        player_quest = result.scalar_one_or_none()

        if not player_quest:
            await update.message.reply_text("❌ 你还没有接取此任务")
            return

        if player_quest.status == QuestStatus.CLAIMED:
            await update.message.reply_text("❌ 任务奖励已领取")
            return

        # 检查任务进度
        if player_quest.current_progress < quest.objective_count:
            progress_pct = int((player_quest.current_progress / quest.objective_count) * 100)
            await update.message.reply_text(
                f"❌ 任务未完成\n"
                f"当前进度：{player_quest.current_progress}/{quest.objective_count} ({progress_pct}%)"
            )
            return

        # 发放奖励
        player.cultivation_exp += quest.exp_reward
        player.spirit_stones += quest.spirit_stones_reward
        if quest.contribution_reward > 0:
            player.contribution += quest.contribution_reward

        # TODO: 物品奖励 (需要背包系统)

        # 更新任务状态
        player_quest.status = QuestStatus.CLAIMED
        player_quest.completed_at = datetime.now()
        player_quest.claimed_at = datetime.now()

        # 设置冷却时间（可重复任务）
        if quest.is_repeatable and quest.cooldown_hours > 0:
            player_quest.next_available_at = datetime.now() + timedelta(hours=quest.cooldown_hours)

        await session.commit()

        type_icon = {"main": "📖", "daily": "⏰", "weekly": "📅", "sect": "🏛️"}.get(
            quest.quest_type.value, "📜"
        )

        msg = f"🎉 任务完成！\n\n"
        msg += f"{type_icon} **{quest.name}**\n\n"
        msg += "🎁 **获得奖励**\n"
        msg += f"⭐ 修为：+{quest.exp_reward}\n"

        if quest.spirit_stones_reward > 0:
            msg += f"💰 灵石：+{quest.spirit_stones_reward}\n"

        if quest.contribution_reward > 0:
            msg += f"🏛️ 宗门贡献：+{quest.contribution_reward}\n"

        if quest.item_rewards:
            try:
                items = json.loads(quest.item_rewards)
                msg += "🎁 物品：\n"
                for item in items:
                    msg += f"   • {item['item_name']} x{item['quantity']}\n"
            except:
                pass

        msg += "\n━━━━━━━━━━━━━━\n"
        msg += f"当前修为：{player.cultivation_exp}/{player.next_realm_exp}\n"
        msg += f"💰 灵石：{player.spirit_stones}"

        if quest.is_repeatable and quest.cooldown_hours > 0:
            msg += f"\n\n⏰ {quest.cooldown_hours}小时后可再次接取"

        await update.message.reply_text(msg, parse_mode="Markdown")


def register_handlers(application):
    """注册任务相关处理器"""
    application.add_handler(CommandHandler("任务", quests_command))
    application.add_handler(CommandHandler("接取", accept_quest_command))
    application.add_handler(CommandHandler("完成", complete_quest_command))
