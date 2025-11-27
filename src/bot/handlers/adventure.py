"""奇遇系统命令处理"""
import logging
import random
import json
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes, CommandHandler, Application
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Player, Item, PlayerInventory
from bot.models.adventure import (
    AdventureTemplate, PlayerAdventure, AdventureExploration,
    LuckEvent, AdventureCooldown, AdventureType, AdventureRarity
)
from bot.models.database import get_db
from bot.services.player_service import PlayerService

logger = logging.getLogger(__name__)


async def adventure_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看奇遇系统说明"""
    text = "🌟 奇遇系统\n\n"
    text += "在修仙之路上，机缘巧合下可能遇到各种奇遇！\n\n"

    text += "📚 奇遇类型：\n"
    text += "  • 宝藏 - 发现珍贵宝物\n"
    text += "  • 传承 - 获得前辈传承\n"
    text += "  • 顿悟 - 修为突破\n"
    text += "  • 邂逅 - 遇到高人指点\n"
    text += "  • 险境 - 危险但有高收益\n"
    text += "  • 试炼 - 挑战关卡\n"
    text += "  • 秘闻 - 神秘事件\n\n"

    text += "🎯 如何触发奇遇：\n"
    text += "  1. 使用 /探索奇遇 <地点> 主动探索\n"
    text += "  2. 修炼、战斗、探险时随机触发\n"
    text += "  3. 提升运气值增加触发概率\n\n"

    text += "🍀 运气系统：\n"
    text += "  • /祈福 - 消耗灵石增加运气\n"
    text += "  • /运气 - 查看当前运气状态\n"
    text += "  • 部分事件会降低运气\n\n"

    text += "📌 可用命令：\n"
    text += "/探索奇遇 <地点> <时长> - 探索寻找奇遇\n"
    text += "/奇遇列表 - 查看已触发的奇遇\n"
    text += "/奇遇图鉴 - 查看奇遇图鉴\n"
    text += "/完成奇遇 <ID> - 完成奇遇挑战\n"
    text += "/祈福 - 祈福增加运气\n"
    text += "/运气 - 查看运气状态"

    await update.message.reply_text(text)


async def explore_adventure_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """探索奇遇"""
    user = update.effective_user

    if len(context.args) < 1:
        await update.message.reply_text("❌ 用法: /探索奇遇 <地点> [时长]\n例如: /探索奇遇 天渊山脉 4\n可选时长: 1, 2, 4, 8小时")
        return

    location = context.args[0]
    duration_hours = int(context.args[1]) if len(context.args) > 1 else 2

    if duration_hours not in [1, 2, 4, 8]:
        await update.message.reply_text("❌ 时长只能是 1, 2, 4, 8 小时")
        return

    spiritual_cost = duration_hours * 50

    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user.id)
        if not player:
            await update.message.reply_text("❌ 请先使用 /开始 创建角色")
            return

        # 检查是否正在探索
        result = await db.execute(
            select(AdventureExploration).where(
                AdventureExploration.player_id == player.id,
                AdventureExploration.is_completed == False
            )
        )
        if result.scalar_one_or_none():
            await update.message.reply_text("❌ 你正在探索中，无法开始新的探索")
            return

        # 检查灵力
        if player.spiritual_power < spiritual_cost:
            await update.message.reply_text(f"❌ 灵力不足，需要 {spiritual_cost} 点灵力")
            return

        # 扣除灵力
        player.spiritual_power -= spiritual_cost

        # 创建探索记录
        exploration = AdventureExploration(
            player_id=player.id,
            location=location,
            exploration_type="探索",
            duration_hours=duration_hours,
            end_time=datetime.now() + timedelta(hours=duration_hours),
            spiritual_power_cost=spiritual_cost
        )
        db.add(exploration)

        await db.commit()

        text = f"🗺️ 开始探索 {location}！\n\n"
        text += f"⏱️ 探索时长：{duration_hours}小时\n"
        text += f"💫 消耗灵力：{spiritual_cost}\n\n"
        text += f"探索完成后使用 /探索结算 查看结果"

        await update.message.reply_text(text)


async def finish_exploration_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """完成探索"""
    user = update.effective_user

    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user.id)
        if not player:
            await update.message.reply_text("❌ 请先使用 /开始 创建角色")
            return

        # 获取探索记录
        result = await db.execute(
            select(AdventureExploration).where(
                AdventureExploration.player_id == player.id,
                AdventureExploration.is_completed == False
            )
        )
        exploration = result.scalar_one_or_none()

        if not exploration:
            await update.message.reply_text("❌ 没有进行中的探索")
            return

        # 检查时间
        if datetime.now() < exploration.end_time:
            remaining = exploration.end_time - datetime.now()
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            await update.message.reply_text(f"⏰ 探索尚未完成，还需 {hours}小时{minutes}分钟")
            return

        # 计算奇遇触发
        # 获取玩家运气值
        result = await db.execute(
            select(LuckEvent).where(
                LuckEvent.player_id == player.id,
                LuckEvent.is_active == True,
                LuckEvent.end_time > datetime.now()
            )
        )
        luck_events = result.scalars().all()
        total_luck = sum(event.luck_modifier for event in luck_events)

        # 基础触发率
        base_rate = 0.15  # 15%基础概率
        luck_bonus = total_luck * 0.01  # 每点运气+1%
        duration_bonus = exploration.duration_hours * 0.05  # 每小时+5%

        trigger_rate = base_rate + luck_bonus + duration_bonus
        trigger_rate = min(0.8, trigger_rate)  # 最高80%

        found_adventure = random.random() < trigger_rate

        exploration.is_completed = True
        exploration.found_adventure = found_adventure

        text = f"🗺️ 探索完成！\n\n"
        text += f"📍 地点：{exploration.location}\n"
        text += f"⏱️ 时长：{exploration.duration_hours}小时\n"

        if found_adventure:
            # 触发奇遇！随机选择一个适合的奇遇
            # 根据总层数计算适合的奇遇等级
            from bot.services.player_service import PlayerService
            total_level = PlayerService._calculate_total_realm_level(player.realm, player.realm_level)
            result = await db.execute(
                select(AdventureTemplate).where(
                    AdventureTemplate.required_level <= total_level
                )
            )
            templates = result.scalars().all()

            if not templates:
                found_adventure = False
            else:
                # 根据稀有度加权随机
                weights = []
                for t in templates:
                    if t.rarity == AdventureRarity.COMMON.value:
                        weights.append(50)
                    elif t.rarity == AdventureRarity.RARE.value:
                        weights.append(30)
                    elif t.rarity == AdventureRarity.EPIC.value:
                        weights.append(15)
                    elif t.rarity == AdventureRarity.LEGENDARY.value:
                        weights.append(4)
                    else:  # MYTHICAL
                        weights.append(1)

                chosen_template = random.choices(templates, weights=weights)[0]

                # 创建玩家奇遇
                adventure = PlayerAdventure(
                    player_id=player.id,
                    template_id=chosen_template.id,
                    location=exploration.location,
                    story=f"在{exploration.location}探索时，{chosen_template.description}"
                )
                db.add(adventure)
                await db.flush()

                exploration.adventure_id = adventure.id

                text += f"\n🌟 发现奇遇：【{chosen_template.name}】\n"
                text += f"⭐ 稀有度：{chosen_template.rarity}\n"
                text += f"📖 {chosen_template.description}\n\n"
                text += f"使用 /完成奇遇 {adventure.id} 开始挑战！"
        else:
            # 未触发奇遇，给予普通奖励
            base_exp = exploration.duration_hours * 100
            exploration.exp_gained = base_exp
            player.cultivation_exp += base_exp

            text += f"\n未发现特殊奇遇\n"
            text += f"📚 获得修为：{base_exp}"

        await db.commit()

        await update.message.reply_text(text)


async def list_adventures_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看奇遇列表"""
    user = update.effective_user

    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user.id)
        if not player:
            await update.message.reply_text("❌ 请先使用 /开始 创建角色")
            return

        # 获取未完成的奇遇
        result = await db.execute(
            select(PlayerAdventure, AdventureTemplate).join(
                AdventureTemplate
            ).where(
                PlayerAdventure.player_id == player.id,
                PlayerAdventure.is_completed == False
            ).order_by(PlayerAdventure.triggered_at.desc())
        )
        adventures = result.all()

        if not adventures:
            await update.message.reply_text("🌟 暂无待完成的奇遇")
            return

        text = "🌟 当前奇遇列表\n\n"

        for adv, template in adventures:
            time_str = adv.triggered_at.strftime("%m-%d %H:%M")
            text += f"【{template.name}】(ID: {adv.id})\n"
            text += f"⭐ 稀有度：{template.rarity}\n"
            text += f"📍 地点：{adv.location}\n"
            text += f"⏰ 触发时间：{time_str}\n"
            text += f"📖 {template.description[:50]}...\n\n"

        text += "使用 /完成奇遇 <ID> 开始挑战"

        await update.message.reply_text(text)


async def complete_adventure_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """完成奇遇"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text("❌ 用法: /完成奇遇 <奇遇ID>")
        return

    try:
        adventure_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ 无效的奇遇ID")
        return

    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user.id)
        if not player:
            await update.message.reply_text("❌ 请先使用 /开始 创建角色")
            return

        # 获取奇遇
        result = await db.execute(
            select(PlayerAdventure, AdventureTemplate).join(
                AdventureTemplate
            ).where(
                PlayerAdventure.id == adventure_id,
                PlayerAdventure.player_id == player.id,
                PlayerAdventure.is_completed == False
            )
        )
        adventure_data = result.one_or_none()

        if not adventure_data:
            await update.message.reply_text("❌ 未找到该奇遇或已完成")
            return

        adventure, template = adventure_data

        # 计算成功率
        base_success_rate = 0.7
        # 使用总层数计算加成
        from bot.services.player_service import PlayerService
        total_level = PlayerService._calculate_total_realm_level(player.realm, player.realm_level)
        level_bonus = total_level * 0.02
        comprehension_bonus = player.comprehension * 0.01
        danger_penalty = template.danger_level * 0.05

        success_rate = base_success_rate + level_bonus + comprehension_bonus - danger_penalty
        success_rate = max(0.2, min(0.95, success_rate))

        is_success = random.random() < success_rate

        # 解析奖励
        rewards = json.loads(template.rewards)
        reward_texts = []

        if is_success:
            # 成功
            for reward in rewards:
                reward_type = reward.get("type")
                value = reward.get("value")

                if reward_type == "exp":
                    player.cultivation_exp += value
                    reward_texts.append(f"📚 修为 +{value}")
                elif reward_type == "stones":
                    player.spirit_stones += value
                    reward_texts.append(f"💎 灵石 +{value}")
                elif reward_type == "spiritual_power":
                    player.spiritual_power = min(
                        player.max_spiritual_power,
                        player.spiritual_power + value
                    )
                    reward_texts.append(f"💫 灵力 +{value}")
                elif reward_type == "comprehension":
                    player.comprehension += value
                    reward_texts.append(f"🧠 悟性 +{value}")

            adventure.is_success = True
            adventure.reward_details = json.dumps(rewards)

            text = f"🎉 奇遇挑战成功！\n\n"
            text += f"🌟 【{template.name}】\n"
            text += f"⭐ 稀有度：{template.rarity}\n\n"
            text += "获得奖励：\n"
            text += "\n".join(reward_texts)
        else:
            # 失败
            damage = template.danger_level * 50
            player.hp = max(1, player.hp - damage)

            adventure.is_success = False

            text = f"💔 奇遇挑战失败\n\n"
            text += f"🌟 【{template.name}】\n"
            text += f"⚠️ 受到伤害：{damage}\n"
            text += f"❤️ 当前生命：{player.hp}/{player.max_hp}"

        adventure.is_completed = True
        adventure.rewards_claimed = is_success
        adventure.completed_at = datetime.now()

        # 添加冷却
        cooldown = AdventureCooldown(
            player_id=player.id,
            template_id=template.id,
            cooldown_until=datetime.now() + timedelta(days=template.cooldown_days)
        )
        db.add(cooldown)

        await db.commit()

        await update.message.reply_text(text)


async def pray_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """祈福增加运气"""
    user = update.effective_user

    pray_cost = 5000
    luck_gain = 10
    duration_hours = 24

    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user.id)
        if not player:
            await update.message.reply_text("❌ 请先使用 /开始 创建角色")
            return

        # 检查灵石
        if player.spirit_stones < pray_cost:
            await update.message.reply_text(f"❌ 灵石不足，需要 {pray_cost} 灵石")
            return

        # 扣除灵石
        player.spirit_stones -= pray_cost

        # 创建运气事件
        luck_event = LuckEvent(
            player_id=player.id,
            event_type="祈福",
            event_name="祈福增运",
            luck_modifier=luck_gain,
            duration_hours=duration_hours,
            end_time=datetime.now() + timedelta(hours=duration_hours)
        )
        db.add(luck_event)

        await db.commit()

        text = f"🙏 祈福成功！\n\n"
        text += f"🍀 运气 +{luck_gain}\n"
        text += f"⏰ 持续时间：{duration_hours}小时\n"
        text += f"💰 消耗：{pray_cost} 灵石\n\n"
        text += "运气可以提升奇遇触发概率！"

        await update.message.reply_text(text)


async def luck_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看运气状态"""
    user = update.effective_user

    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user.id)
        if not player:
            await update.message.reply_text("❌ 请先使用 /开始 创建角色")
            return

        # 获取运气事件
        result = await db.execute(
            select(LuckEvent).where(
                LuckEvent.player_id == player.id,
                LuckEvent.is_active == True,
                LuckEvent.end_time > datetime.now()
            ).order_by(LuckEvent.end_time.desc())
        )
        luck_events = result.scalars().all()

        if not luck_events:
            await update.message.reply_text("🍀 当前没有运气加成效果")
            return

        total_luck = sum(event.luck_modifier for event in luck_events)

        text = f"🍀 当前运气状态\n\n"
        text += f"总运气值：{total_luck:+d}\n\n"

        for event in luck_events:
            remaining = event.end_time - datetime.now()
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)

            modifier_str = f"+{event.luck_modifier}" if event.luck_modifier > 0 else str(event.luck_modifier)
            text += f"【{event.event_name}】{modifier_str}\n"
            text += f"  剩余：{hours}小时{minutes}分钟\n\n"

        text += f"💡 运气影响奇遇触发率\n"
        text += f"当前加成：{total_luck}%"

        await update.message.reply_text(text)


def register_handlers(application: Application):
    """注册处理器"""
    application.add_handler(MessageHandler(filters.Regex(r"^\.奇遇"), adventure_info_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.探索奇遇"), explore_adventure_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.探索结算"), finish_exploration_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.奇遇列表"), list_adventures_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.完成奇遇"), complete_adventure_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.祈福"), pray_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.运气"), luck_status_command))

    logger.info("奇遇系统命令处理器注册完成")
