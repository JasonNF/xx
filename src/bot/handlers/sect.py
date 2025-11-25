"""宗门系统handlers - 凡人修仙传版本"""
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from bot.models.database import AsyncSessionLocal
from bot.models import Player, RealmType
from bot.models.sect import Sect, SectApplication, SectShopItem
from bot.services.sect_service import SectService
from sqlalchemy import select, func


async def sect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看宗门信息 - /宗门"""
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

        # 检查是否已加入宗门
        if player.sect_id:
            # 获取宗门信息
            result = await session.execute(
                select(Sect).where(Sect.id == player.sect_id)
            )
            sect = result.scalar_one_or_none()

            if not sect:
                await update.message.reply_text("❌ 宗门数据错误")
                return

            # 获取成员数量
            result = await session.execute(
                select(func.count(Player.id)).where(Player.sect_id == sect.id)
            )
            member_count = result.scalar()

            # 构建消息
            msg = f"🏯 【{sect.name}】\n\n"
            msg += f"{sect.description}\n\n"

            msg += f"📊 宗门信息\n"
            msg += f"阵营：{sect.faction.value}\n"
            msg += f"等级：{sect.level}级\n"
            msg += f"声望：{sect.reputation}\n"
            msg += f"成员：{member_count}/{sect.max_members}\n\n"

            msg += f"🏛️ 建筑等级\n"
            msg += f"大殿：Lv.{sect.hall_level}\n"
            msg += f"藏经阁：Lv.{sect.library_level}\n"
            msg += f"炼丹房：Lv.{sect.alchemy_level}\n"
            msg += f"炼器阁：Lv.{sect.refinery_level}\n\n"

            # 获取当前职位信息
            current_position = SectService.get_position_by_reputation(player.contribution)
            next_position = SectService.get_next_position(player.contribution)

            msg += f"👤 你的身份\n"
            msg += f"职位：{player.sect_position or current_position['name']}\n"
            msg += f"声望：{player.contribution}"

            if next_position:
                msg += f" (距离{next_position['name']}还需{next_position['reputation_required'] - player.contribution}声望)"
            msg += "\n\n"

            if sect.announcement:
                msg += f"📢 公告\n{sect.announcement}\n\n"

            msg += "━━━━━━━━━━━━━━\n"
            msg += "💡 命令：\n"
            msg += "• /贡献 <灵石数量> - 捐献灵石获得声望\n"
            msg += "• /兑换 - 宗门商店\n"
            msg += "• /宗门成员 - 查看成员列表\n"
            msg += "• /挑战掌门 - 挑战掌门(长老以上)\n"
            msg += "• /退出 - 退出宗门"

        else:
            # 显示可加入的宗门列表
            result = await session.execute(
                select(Sect).where(Sect.is_npc_sect == True).order_by(Sect.name)
            )
            sects = result.scalars().all()

            msg = "🏯 【宗门列表】\n\n"
            msg += f"道友：{player.nickname}\n"
            msg += f"境界：{player.full_realm_name}\n"
            msg += "━━━━━━━━━━━━━━\n\n"

            if not sects:
                msg += "暂无可加入的宗门\n"
            else:
                for sect in sects:
                    result = await session.execute(
                        select(func.count(Player.id)).where(Player.sect_id == sect.id)
                    )
                    member_count = result.scalar()

                    faction_icon = {
                        "正道": "☀️",
                        "魔道": "🌙",
                        "中立": "⚖️",
                        "联盟": "🤝"
                    }.get(sect.faction.value, "🏯")

                    msg += f"{faction_icon} **{sect.name}**\n"
                    msg += f"    {sect.description[:50]}...\n"
                    msg += f"    成员：{member_count}/{sect.max_members}\n"
                    if sect.min_realm_requirement:
                        msg += f"    要求：{sect.min_realm_requirement}\n"
                    msg += "\n"

            msg += "━━━━━━━━━━━━━━\n"
            msg += "💡 使用 /入门 <宗门名> 申请加入"

        await update.message.reply_text(msg, parse_mode="Markdown")


async def join_sect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """申请加入宗门 - /入门 <宗门名>"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ 请指定宗门名称\n"
            "用法：/入门 <宗门名称>\n"
            "例如：/入门 黄枫谷"
        )
        return

    sect_name = " ".join(context.args)

    async with AsyncSessionLocal() as session:
        # 获取玩家
        result = await session.execute(
            select(Player).where(Player.telegram_id == user.id)
        )
        player = result.scalar_one_or_none()

        if not player:
            await update.message.reply_text("❌ 请先使用 /灵根 开始游戏")
            return

        # 检查是否已有宗门
        if player.sect_id:
            await update.message.reply_text(
                "❌ 你已经加入宗门了\n"
                "使用 /退出 离开当前宗门"
            )
            return

        # 获取宗门
        result = await session.execute(
            select(Sect).where(Sect.name == sect_name)
        )
        sect = result.scalar_one_or_none()

        if not sect:
            await update.message.reply_text(
                f"❌ 未找到宗门：{sect_name}\n"
                "使用 /宗门 查看可加入的宗门"
            )
            return

        # 检查成员数量
        result = await session.execute(
            select(func.count(Player.id)).where(Player.sect_id == sect.id)
        )
        member_count = result.scalar()

        if member_count >= sect.max_members:
            await update.message.reply_text(f"❌ {sect.name} 已满员")
            return

        # 检查境界要求
        if sect.min_realm_requirement:
            realm_order = {
                RealmType.MORTAL: 0,
                RealmType.QI_REFINING: 1,
                RealmType.FOUNDATION: 2,
                RealmType.CORE_FORMATION: 3,
                RealmType.NASCENT_SOUL: 4,
                RealmType.DEITY_TRANSFORMATION: 5,
            }

            req_realm = None
            for r in RealmType:
                if r.value == sect.min_realm_requirement:
                    req_realm = r
                    break

            if req_realm and realm_order.get(player.realm, 0) < realm_order.get(req_realm, 0):
                await update.message.reply_text(
                    f"❌ 境界不足\n"
                    f"需要：{sect.min_realm_requirement}\n"
                    f"当前：{player.full_realm_name}"
                )
                return

        # NPC宗门自动接受
        if sect.is_npc_sect or sect.auto_accept:
            player.sect_id = sect.id
            player.sect_position = "外门弟子"
            await session.commit()

            msg = f"🎉 成功加入 {sect.name}！\n\n"
            msg += f"你被授予「外门弟子」身份\n"
            msg += f"初始贡献：0\n\n"
            msg += "💡 使用 /宗门 查看宗门信息"
        else:
            # 创建申请
            application = SectApplication(
                sect_id=sect.id,
                player_id=player.id,
                status="pending"
            )
            session.add(application)
            await session.commit()

            msg = f"📝 已提交加入 {sect.name} 的申请\n\n"
            msg += "请等待宗门管理员审核"

        await update.message.reply_text(msg)


async def leave_sect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """退出宗门 - /退出"""
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

        if not player.sect_id:
            await update.message.reply_text("❌ 你还没有加入任何宗门")
            return

        # 获取宗门名称
        result = await session.execute(
            select(Sect).where(Sect.id == player.sect_id)
        )
        sect = result.scalar_one_or_none()
        sect_name = sect.name if sect else "未知宗门"

        # 使用Service退出宗门
        success, message = await SectService.leave_sect(session, player)

        if not success:
            await update.message.reply_text(f"❌ {message}")
            return

        await update.message.reply_text(f"👋 {message}")


async def donate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """向宗门捐献灵石 - /贡献 <数量>"""
    user = update.effective_user

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(
            "❌ 请指定灵石数量\n"
            "用法：/贡献 <灵石数量>\n"
            "例如：/贡献 1000"
        )
        return

    amount = int(context.args[0])
    if amount <= 0:
        await update.message.reply_text("❌ 数量必须大于0")
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

        # 使用Service处理捐献
        success, message, reputation_gain = await SectService.donate_to_sect(
            session, player, amount
        )

        if not success:
            await update.message.reply_text(f"❌ {message}")
            return

        # 检查是否晋升
        current_position = SectService.get_position_by_reputation(player.contribution)
        promotion_msg = ""
        if player.sect_position and player.sect_position != current_position["name"]:
            promotion_msg = f"\n\n🎊 恭喜晋升为 {current_position['name']}！"

        await update.message.reply_text(
            f"🎁 {message}！\n\n"
            f"💰 捐献：{amount} 灵石\n"
            f"📊 获得：{reputation_gain} 声望\n\n"
            f"💰 剩余灵石：{player.spirit_stones}\n"
            f"📊 总声望：{player.contribution}{promotion_msg}"
        )


async def sect_shop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """宗门商店 - /兑换"""
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

        if not player.sect_id:
            await update.message.reply_text("❌ 你还没有加入宗门")
            return

        # 获取宗门商店物品
        from bot.models import Item
        result = await session.execute(
            select(SectShopItem, Item)
            .join(Item, SectShopItem.item_id == Item.id)
            .where(SectShopItem.sect_id == player.sect_id)
            .order_by(SectShopItem.contribution_cost)
        )
        shop_items = result.all()

        if not shop_items:
            await update.message.reply_text(
                "🏪 【宗门商店】\n\n"
                "暂无可兑换物品"
            )
            return

        # 构建消息
        msg = "🏪 【宗门商店】\n\n"
        msg += f"📊 你的贡献：{player.contribution}\n"
        msg += "━━━━━━━━━━━━━━\n\n"

        for shop_item, item in shop_items:
            can_buy = "✅" if player.contribution >= shop_item.contribution_cost else "🔒"
            stock_text = f"库存：{shop_item.stock}" if shop_item.stock >= 0 else "不限"

            msg += f"{can_buy} **{item.name}**\n"
            msg += f"    {item.description[:30]}...\n"
            msg += f"    💰 {shop_item.contribution_cost} 贡献 | {stock_text}\n\n"

        msg += "━━━━━━━━━━━━━━\n"
        msg += "💡 使用 /兑换 <物品名> 兑换物品"

        await update.message.reply_text(msg, parse_mode="Markdown")


async def sect_members_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看宗门成员 - /宗门成员"""
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

        if not player.sect_id:
            await update.message.reply_text("❌ 你还没有加入宗门")
            return

        # 获取宗门信息
        sect_info = await SectService.get_sect_info(session, player.sect_id)
        if not sect_info:
            await update.message.reply_text("❌ 宗门数据错误")
            return

        sect = sect_info["sect"]

        # 获取成员列表
        members = await SectService.get_sect_members(session, player.sect_id, limit=20)

        msg = f"👥 【{sect.name} 成员榜】\n\n"
        msg += f"掌门：{sect_info['master_name']}\n"
        msg += f"总人数：{sect_info['member_count']}/{sect.max_members}\n"
        msg += "━━━━━━━━━━━━━━\n\n"

        for i, member in enumerate(members, 1):
            is_self = "👤 " if member["id"] == player.id else ""
            msg += f"{i}. {is_self}{member['nickname']}\n"
            msg += f"   {member['position']} | {member['realm']} | {member['reputation']}声望\n\n"

        await update.message.reply_text(msg)


async def challenge_master_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """挑战掌门 - /挑战掌门"""
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

        if not player.sect_id:
            await update.message.reply_text("❌ 你还没有加入宗门")
            return

        # 获取宗门
        result = await session.execute(
            select(Sect).where(Sect.id == player.sect_id)
        )
        sect = result.scalar_one_or_none()

        if not sect:
            await update.message.reply_text("❌ 宗门数据错误")
            return

        # 发起挑战
        success, message, master_id = await SectService.challenge_master(
            session, player, sect
        )

        if not success:
            await update.message.reply_text(f"❌ {message}")
            return

        if isinstance(master_id, int):
            # 需要战斗
            await update.message.reply_text(
                f"⚔️ {message}\n\n"
                f"战斗胜利后你将成为{sect.name}的新任掌门！\n"
                f"并获得大量声望和宗门资源！\n\n"
                f"💡 请使用战斗系统与掌门决斗"
            )
        else:
            # 直接晋升
            await update.message.reply_text(
                f"🎉 {message}\n\n"
                f"获得声望：{master_id or 0}"
            )


def register_handlers(application):
    """注册宗门相关处理器"""
    application.add_handler(CommandHandler("宗门", sect_command))
    application.add_handler(CommandHandler("入门", join_sect_command))
    application.add_handler(CommandHandler("退出", leave_sect_command))
    application.add_handler(CommandHandler("贡献", donate_command))
    application.add_handler(CommandHandler("兑换", sect_shop_command))
    application.add_handler(CommandHandler("宗门成员", sect_members_command))
    application.add_handler(CommandHandler("挑战掌门", challenge_master_command))
