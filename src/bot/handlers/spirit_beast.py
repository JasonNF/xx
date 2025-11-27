"""灵兽系统handlers"""
import json
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes, CommandHandler

from bot.models.database import AsyncSessionLocal
from bot.models import Player
from bot.models.spirit_beast import PlayerSpiritBeast, SpiritBeastTemplate
from bot.services.spirit_beast_service import SpiritBeastService
from sqlalchemy import select
from datetime import datetime, timedelta
import random


async def beast_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看灵兽列表 - /灵兽"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        result = await session.execute(
            select(PlayerSpiritBeast).where(
                PlayerSpiritBeast.player_id == player.id
            ).order_by(PlayerSpiritBeast.is_active.desc(), PlayerSpiritBeast.level.desc())
        )
        beasts = result.scalars().all()

        if not beasts:
            msg = "🐾 【灵兽】\n\n"
            msg += "📦 您还没有灵兽\n\n"
            msg += "💡 使用 /捕捉灵兽 尝试捕捉野生灵兽\n"
            msg += "💡 使用 /灵兽图鉴 查看可捕捉的灵兽"
            await update.message.reply_text(msg)
            return

        msg = "🐾 【我的灵兽】\n\n"

        for beast in beasts:
            result = await session.execute(
                select(SpiritBeastTemplate).where(SpiritBeastTemplate.id == beast.template_id)
            )
            template = result.scalar_one_or_none()

            status_icon = "⚔️" if beast.is_active else "💤"
            training_icon = "📚" if beast.is_training else ""
            evolution_icon = "⭐" * beast.evolution_stage if beast.evolution_stage > 0 else ""

            msg += f"{status_icon} **{beast.nickname}** {training_icon} {evolution_icon}\n"
            msg += f"    种类：{template.name if template else '未知'}\n"
            msg += f"    等级：Lv.{beast.level} | 品阶：{beast.grade}\n"
            msg += f"    ⚔️{beast.attack} 🛡️{beast.defense} ❤️{beast.hp}/{beast.max_hp}\n"
            msg += f"    💕 亲密度：{beast.intimacy}/100\n"

            # 显示天赋
            if beast.talents:
                talents_display = SpiritBeastService.format_talents_display(beast.talents)
                msg += f"    ✨ 天赋：{talents_display}\n"

            if beast.is_training and beast.training_end_time:
                remaining = beast.training_end_time - datetime.now()
                if remaining.total_seconds() > 0:
                    hours = int(remaining.total_seconds() // 3600)
                    minutes = int((remaining.total_seconds() % 3600) // 60)
                    msg += f"    ⏰ 训练剩余：{hours}h{minutes}m\n"

            msg += "\n"

        msg += "━━━━━━━━━━━━━━\n"
        msg += "💡 使用 /灵兽详情 <昵称> 查看详情\n"
        msg += "💡 使用 /出战灵兽 <昵称> 选择出战灵兽\n"
        msg += "💡 使用 /训练灵兽 <昵称> <时长> 训练灵兽"

        await update.message.reply_text(msg, parse_mode="Markdown")


async def beast_codex_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """灵兽图鉴 - /灵兽图鉴"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        result = await session.execute(
            select(SpiritBeastTemplate).order_by(SpiritBeastTemplate.rarity.asc())
        )
        templates = result.scalars().all()

        if not templates:
            await update.message.reply_text("📖 灵兽图鉴为空")
            return

        msg = "📖 【灵兽图鉴】\n\n"

        for template in templates:
            rarity_stars = "⭐" * min(template.rarity, 5)

            msg += f"**{template.name}** {rarity_stars}\n"
            msg += f"    {template.description[:40]}...\n"
            msg += f"    类型：{template.beast_type}\n"
            if template.element:
                msg += f"    属性：{template.element}\n"
            msg += f"    ⚔️{template.base_attack} 🛡️{template.base_defense} ❤️{template.base_hp}\n"
            if template.special_ability:
                msg += f"    💫 特殊：{template.special_ability[:30]}...\n"
            msg += "\n"

        msg += "━━━━━━━━━━━━━━\n"
        msg += "💡 使用 /捕捉灵兽 尝试捕捉野生灵兽"

        await update.message.reply_text(msg, parse_mode="Markdown")


async def capture_beast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """捕捉灵兽 - /捕捉灵兽"""
    user = update.effective_user

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 检查境界
        from bot.models import RealmType
        if player.realm == RealmType.QI_REFINING and player.realm_level < 7:
            await update.message.reply_text("❌ 需要达到炼气7层才能捕捉灵兽")
            return
        elif player.realm == RealmType.MORTAL:
            await update.message.reply_text("❌ 需要达到炼气7层才能捕捉灵兽")
            return

        # 检查灵兽数量
        result = await session.execute(
            select(PlayerSpiritBeast).where(PlayerSpiritBeast.player_id == player.id)
        )
        beast_count = len(result.scalars().all())

        max_beasts = 3
        if player.realm == RealmType.CORE_FORMATION:
            max_beasts = 5
        elif player.realm in [RealmType.NASCENT_SOUL, RealmType.DEITY_TRANSFORMATION]:
            max_beasts = 7

        if beast_count >= max_beasts:
            await update.message.reply_text(f"❌ 灵兽数量已达上限（{max_beasts}只）")
            return

        # 消耗灵石
        cost = 1000
        if player.spirit_stones < cost:
            await update.message.reply_text(f"❌ 灵石不足，需要 {cost} 灵石")
            return

        player.spirit_stones -= cost

        # 随机遇到灵兽
        result = await session.execute(
            select(SpiritBeastTemplate)
        )
        all_templates = result.scalars().all()

        if not all_templates:
            await update.message.reply_text("❌ 暂无可捕捉的灵兽")
            return

        # 根据稀有度加权随机
        weights = [10 / (template.rarity + 1) for template in all_templates]
        template = random.choices(all_templates, weights=weights, k=1)[0]

        # 捕捉成功率
        base_rate = 0.6
        # 根据总层数计算加成
        from bot.services.player_service import PlayerService
        total_level = PlayerService._calculate_total_realm_level(player.realm, player.realm_level)
        level_bonus = total_level * 0.02
        comprehension_bonus = player.comprehension * 0.01
        rarity_penalty = template.rarity * 0.05

        success_rate = base_rate + level_bonus + comprehension_bonus - rarity_penalty
        success_rate = max(0.1, min(0.9, success_rate))

        is_success = random.random() < success_rate

        if not is_success:
            await session.commit()
            msg = f"💥 捕捉失败！\n\n"
            msg += f"🐾 遇到了 {template.name}\n"
            msg += f"⭐ 稀有度：{template.rarity}/10\n"
            msg += f"📊 成功率：{success_rate*100:.1f}%\n\n"
            msg += f"💰 消耗：{cost}灵石\n"
            msg += "💡 再接再厉！"
            await update.message.reply_text(msg)
            return

        # 生成随机天赋
        talents = SpiritBeastService.generate_random_talents(template.quality)
        talents_json = json.dumps(talents, ensure_ascii=False) if talents else None

        # 捕捉成功，创建灵兽
        new_beast = PlayerSpiritBeast(
            player_id=player.id,
            template_id=template.id,
            nickname=template.name,
            level=1,
            attack=template.base_attack,
            defense=template.base_defense,
            hp=template.base_hp,
            max_hp=template.base_hp,
            speed=template.base_speed,
            intimacy=10,
            talents=talents_json
        )
        session.add(new_beast)

        await session.commit()

        msg = f"🎉 捕捉成功！\n\n"
        msg += f"🐾 获得灵兽：{template.name}\n"
        msg += f"⭐ 稀有度：{template.rarity}/10\n"
        msg += f"🏆 品质：{template.quality}\n"
        msg += f"🏷️ 类型：{template.beast_type}\n"
        if template.element:
            msg += f"⚡ 属性：{template.element}\n"

        # 显示天赋
        if talents:
            msg += f"\n✨ 【天赋】\n"
            for talent in talents:
                icon = talent.get("icon", "")
                name = talent["name"]
                description = talent["description"]
                rarity = talent.get("rarity", "普通")
                msg += f"{icon} {name} ({rarity})\n"
                msg += f"   {description}\n"

        msg += f"\n【初始属性】\n"
        msg += f"⚔️ 攻击：{template.base_attack}\n"
        msg += f"🛡️ 防御：{template.base_defense}\n"
        msg += f"❤️ 生命：{template.base_hp}\n"
        msg += f"⚡ 速度：{template.base_speed}\n\n"
        if template.special_ability:
            msg += f"💫 特殊能力：{template.special_ability}\n\n"
        msg += f"💰 消耗：{cost}灵石\n\n"
        msg += "💡 使用 /训练灵兽 提升灵兽等级\n"
        msg += "💡 使用 /灵兽详情 查看天赋详情"

        await update.message.reply_text(msg)


async def deploy_beast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """出战灵兽 - /出战灵兽 <昵称>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定灵兽昵称\n"
            "用法：/出战灵兽 <昵称>\n"
            "例如：/出战灵兽 啼魂兽"
        )
        return

    nickname = " ".join(context.args)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 取消当前出战灵兽
        result = await session.execute(
            select(PlayerSpiritBeast).where(
                PlayerSpiritBeast.player_id == player.id,
                PlayerSpiritBeast.is_active == True
            )
        )
        current_beast = result.scalar_one_or_none()
        if current_beast:
            current_beast.is_active = False

        # 选择新的出战灵兽
        result = await session.execute(
            select(PlayerSpiritBeast).where(
                PlayerSpiritBeast.player_id == player.id,
                PlayerSpiritBeast.nickname == nickname
            )
        )
        new_beast = result.scalar_one_or_none()

        if not new_beast:
            await update.message.reply_text(f"❌ 未找到名为 {nickname} 的灵兽")
            return

        if new_beast.is_training:
            await update.message.reply_text("❌ 灵兽训练中，无法出战")
            return

        new_beast.is_active = True

        await session.commit()

        msg = f"⚔️ {new_beast.nickname} 已出战！\n\n"
        msg += f"等级：Lv.{new_beast.level}\n"
        msg += f"⚔️ 攻击：{new_beast.attack}\n"
        msg += f"🛡️ 防御：{new_beast.defense}\n"
        msg += f"❤️ 生命：{new_beast.hp}/{new_beast.max_hp}\n"
        msg += f"💕 亲密度：{new_beast.intimacy}/100"

        await update.message.reply_text(msg)


async def train_beast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """训练灵兽 - /训练灵兽 <昵称> [时长]"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定灵兽昵称和训练时长\n"
            "用法：/训练灵兽 <昵称> [时长]\n"
            "时长：1、2、4、8小时（默认1小时）\n"
            "例如：/训练灵兽 啼魂兽 4"
        )
        return

    nickname = context.args[0]
    duration_hours = 1

    if len(context.args) > 1:
        try:
            duration_hours = int(context.args[1])
            if duration_hours not in [1, 2, 4, 8]:
                await update.message.reply_text("❌ 时长只能是 1、2、4、8 小时")
                return
        except ValueError:
            await update.message.reply_text("❌ 时长必须是数字")
            return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        result = await session.execute(
            select(PlayerSpiritBeast).where(
                PlayerSpiritBeast.player_id == player.id,
                PlayerSpiritBeast.nickname == nickname
            )
        )
        beast = result.scalar_one_or_none()

        if not beast:
            await update.message.reply_text(f"❌ 未找到名为 {nickname} 的灵兽")
            return

        if beast.is_training:
            await update.message.reply_text("❌ 灵兽已在训练中")
            return

        # 消耗灵石
        cost = duration_hours * 500
        if player.spirit_stones < cost:
            await update.message.reply_text(f"❌ 灵石不足，需要 {cost} 灵石")
            return

        player.spirit_stones -= cost

        # 开始训练
        beast.is_training = True
        beast.training_end_time = datetime.now() + timedelta(hours=duration_hours)

        await session.commit()

        msg = f"📚 {beast.nickname} 开始训练！\n\n"
        msg += f"⏰ 训练时长：{duration_hours}小时\n"
        msg += f"💰 消耗：{cost}灵石\n\n"
        msg += f"完成时间：{beast.training_end_time.strftime('%m-%d %H:%M')}\n\n"
        msg += "💡 使用 /训练结算 <昵称> 完成训练"

        await update.message.reply_text(msg)


async def finish_training_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """训练结算 - /训练结算 <昵称>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定灵兽昵称\n"
            "用法：/训练结算 <昵称>\n"
            "例如：/训练结算 啼魂兽"
        )
        return

    nickname = " ".join(context.args)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        result = await session.execute(
            select(PlayerSpiritBeast).where(
                PlayerSpiritBeast.player_id == player.id,
                PlayerSpiritBeast.nickname == nickname
            )
        )
        beast = result.scalar_one_or_none()

        if not beast:
            await update.message.reply_text(f"❌ 未找到名为 {nickname} 的灵兽")
            return

        if not beast.is_training:
            await update.message.reply_text("❌ 灵兽未在训练中")
            return

        if datetime.now() < beast.training_end_time:
            remaining = beast.training_end_time - datetime.now()
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            await update.message.reply_text(f"❌ 训练未完成，还需{hours}小时{minutes}分钟")
            return

        # 计算经验和亲密度
        exp_gain = random.randint(100, 200)
        intimacy_gain = random.randint(1, 3)

        beast.exp += exp_gain
        beast.intimacy = min(100, beast.intimacy + intimacy_gain)

        # 检查升级
        level_up = False
        new_level = beast.level

        while beast.exp >= beast.next_level_exp:
            beast.exp -= beast.next_level_exp
            beast.level += 1
            beast.next_level_exp = int(beast.next_level_exp * 1.5)
            level_up = True
            new_level = beast.level

            # 属性提升
            result = await session.execute(
                select(SpiritBeastTemplate).where(SpiritBeastTemplate.id == beast.template_id)
            )
            template = result.scalar_one_or_none()

            if template:
                beast.attack += template.growth_attack
                beast.defense += template.growth_defense
                beast.max_hp += template.growth_hp
                beast.hp = beast.max_hp

        # 重置训练状态
        beast.is_training = False
        beast.training_end_time = None

        await session.commit()

        msg = f"🎉 {beast.nickname} 训练完成！\n\n"
        msg += f"⭐ 经验：+{exp_gain}\n"
        msg += f"💕 亲密度：+{intimacy_gain}\n"

        if level_up:
            msg += f"\n🎊 等级提升至 Lv.{new_level}！\n"
            msg += f"⚔️ 攻击：{beast.attack}\n"
            msg += f"🛡️ 防御：{beast.defense}\n"
            msg += f"❤️ 生命：{beast.hp}/{beast.max_hp}"

        await update.message.reply_text(msg)


async def evolve_beast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """灵兽进化 - /灵兽进化 <昵称>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定灵兽昵称\n"
            "用法：/灵兽进化 <昵称>\n"
            "例如：/灵兽进化 青风狼"
        )
        return

    nickname = " ".join(context.args)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        result = await session.execute(
            select(PlayerSpiritBeast).where(
                PlayerSpiritBeast.player_id == player.id,
                PlayerSpiritBeast.nickname == nickname
            )
        )
        beast = result.scalar_one_or_none()

        if not beast:
            await update.message.reply_text(f"❌ 未找到名为 {nickname} 的灵兽")
            return

        result = await session.execute(
            select(SpiritBeastTemplate).where(SpiritBeastTemplate.id == beast.template_id)
        )
        template = result.scalar_one_or_none()

        if not template:
            await update.message.reply_text("❌ 灵兽模板数据异常")
            return

        # 尝试进化
        success, message, evolution_data = await SpiritBeastService.evolve_beast(
            session, player, beast, template
        )

        if not success:
            await update.message.reply_text(message)
            return

        # 进化成功
        msg = f"🎊 {beast.nickname} 进化成功！\n\n"
        msg += f"📈 进化阶段：{evolution_data['from_stage']} → {evolution_data['to_stage']}\n\n"
        msg += f"【属性提升】\n"
        msg += f"⚔️ 攻击：+{evolution_data['attack_gain']}\n"
        msg += f"🛡️ 防御：+{evolution_data['defense_gain']}\n"
        msg += f"❤️ 生命：+{evolution_data['hp_gain']}\n\n"

        if evolution_data.get('new_talent'):
            new_talent = evolution_data['new_talent']
            msg += f"✨ 获得新天赋：{new_talent['icon']}{new_talent['name']}\n"
            msg += f"   {new_talent['description']}\n\n"

        msg += f"【当前属性】\n"
        msg += f"⚔️ 攻击：{beast.attack}\n"
        msg += f"🛡️ 防御：{beast.defense}\n"
        msg += f"❤️ 生命：{beast.hp}/{beast.max_hp}\n\n"
        msg += f"💰 消耗：{evolution_data['cost']:,}灵石"

        await update.message.reply_text(msg)


async def fuse_beasts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """灵兽融合 - /灵兽融合 <灵兽1> <灵兽2>"""
    user = update.effective_user

    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ 请指定两只灵兽的昵称\n"
            "用法：/灵兽融合 <灵兽1> <灵兽2>\n"
            "例如：/灵兽融合 青风狼 烈焰鼠\n\n"
            "⚠️ 融合后两只灵兽将消失，生成新灵兽"
        )
        return

    nickname1 = context.args[0]
    nickname2 = context.args[1]

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 获取两只灵兽
        result = await session.execute(
            select(PlayerSpiritBeast).where(
                PlayerSpiritBeast.player_id == player.id,
                PlayerSpiritBeast.nickname == nickname1
            )
        )
        beast1 = result.scalar_one_or_none()

        result = await session.execute(
            select(PlayerSpiritBeast).where(
                PlayerSpiritBeast.player_id == player.id,
                PlayerSpiritBeast.nickname == nickname2
            )
        )
        beast2 = result.scalar_one_or_none()

        if not beast1:
            await update.message.reply_text(f"❌ 未找到名为 {nickname1} 的灵兽")
            return

        if not beast2:
            await update.message.reply_text(f"❌ 未找到名为 {nickname2} 的灵兽")
            return

        # 获取模板
        result = await session.execute(
            select(SpiritBeastTemplate).where(SpiritBeastTemplate.id == beast1.template_id)
        )
        template1 = result.scalar_one_or_none()

        result = await session.execute(
            select(SpiritBeastTemplate).where(SpiritBeastTemplate.id == beast2.template_id)
        )
        template2 = result.scalar_one_or_none()

        if not template1 or not template2:
            await update.message.reply_text("❌ 灵兽模板数据异常")
            return

        # 尝试融合
        success, message, new_beast = await SpiritBeastService.fuse_beasts(
            session, player, beast1, beast2, template1, template2
        )

        if not success:
            await update.message.reply_text(message)
            return

        # 融合成功
        result = await session.execute(
            select(SpiritBeastTemplate).where(SpiritBeastTemplate.id == new_beast.template_id)
        )
        new_template = result.scalar_one_or_none()

        msg = f"🎊 灵兽融合成功！\n\n"
        msg += f"💫 {beast1.nickname} + {beast2.nickname}\n"
        msg += f"   ↓\n"
        msg += f"🌟 {new_beast.nickname}\n\n"
        msg += f"【新灵兽属性】\n"
        msg += f"🏆 品质：{new_template.quality if new_template else '未知'}\n"
        msg += f"⚔️ 攻击：{new_beast.attack}\n"
        msg += f"🛡️ 防御：{new_beast.defense}\n"
        msg += f"❤️ 生命：{new_beast.hp}/{new_beast.max_hp}\n"
        msg += f"⚡ 速度：{new_beast.speed}\n"
        msg += f"📊 等级：Lv.{new_beast.level}\n\n"

        # 显示继承的天赋
        if new_beast.talents:
            talents_display = SpiritBeastService.format_talents_display(new_beast.talents)
            msg += f"✨ 继承天赋：{talents_display}\n\n"

        msg += f"💰 消耗：50,000灵石"

        await update.message.reply_text(msg)


def register_handlers(application):
    """注册灵兽相关处理器"""
    application.add_handler(MessageHandler(filters.Regex(r"^\.灵兽"), beast_list_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.灵兽图鉴"), beast_codex_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.捕捉灵兽"), capture_beast_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.出战灵兽"), deploy_beast_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.训练灵兽"), train_beast_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.训练结算"), finish_training_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.灵兽进化"), evolve_beast_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.灵兽融合"), fuse_beasts_command))
