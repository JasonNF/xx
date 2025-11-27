"""洞府系统命令处理"""
import logging
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes, CommandHandler, Application
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Player, Item, PlayerInventory
from bot.models.cave_dwelling import (
    CaveDwelling, CaveRoom, SpiritField, CaveUpgradeRecord,
    CaveDwellingGrade, CaveRoomType
)
from bot.models.database import get_db
from bot.services.player_service import PlayerService
from bot.services.spirit_field_service import SpiritFieldService

logger = logging.getLogger(__name__)


async def cave_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看洞府信息"""
    user = update.effective_user
    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user.id)
        if not player:
            await update.message.reply_text("❌ 请先使用 /开始 创建角色")
            return

        # 获取洞府
        result = await db.execute(
            select(CaveDwelling).where(CaveDwelling.player_id == player.id)
        )
        cave = result.scalar_one_or_none()

        if not cave:
            text = "🏔️ 洞府系统\n\n"
            text += "你还没有洞府！\n\n"
            text += "📌 使用 /购买洞府 <位置> 购买洞府\n"
            text += "💰 基础洞府价格: 50,000 灵石"
            await update.message.reply_text(text)
            return

        # 获取房间列表
        result = await db.execute(
            select(CaveRoom).where(CaveRoom.cave_id == cave.id)
        )
        rooms = result.scalars().all()

        # 检查维护状态
        days_since_maintenance = (datetime.now() - cave.last_maintenance).days
        maintenance_due = days_since_maintenance * cave.maintenance_cost

        text = f"🏔️ 洞府：{cave.name}\n"
        text += f"📍 位置：{cave.location}\n"
        text += f"⭐ 品级：{cave.grade} | 等级：{cave.level}级\n"
        text += f"✨ 灵气浓度：{cave.spiritual_density}\n"
        text += f"🛡️ 防御值：{cave.defense}\n\n"

        text += f"🏠 房间：{cave.current_rooms}/{cave.max_rooms}\n"
        if rooms:
            for room in rooms:
                occupied_status = "【使用中】" if room.is_occupied else ""
                text += f"  • {room.room_name} Lv.{room.room_level} {occupied_status}\n"
                text += f"    效果：{room.effect_description}\n"
        else:
            text += "  暂无房间\n"

        text += f"\n💰 维护费用：{cave.maintenance_cost} 灵石/天\n"
        if days_since_maintenance > 0:
            text += f"⚠️ 欠缴维护费：{maintenance_due} 灵石（{days_since_maintenance}天）\n"

        text += f"\n⬆️ 升级到 {cave.level+1} 级需要：{cave.next_level_cost} 灵石\n"

        text += "\n📌 可用命令：\n"
        text += "/建造房间 <房间类型> - 建造新房间\n"
        text += "/房间列表 - 查看可建造的房间类型\n"
        text += "/升级洞府 - 升级洞府等级\n"
        text += "/维护洞府 - 支付维护费用\n"
        text += "/改名洞府 <新名称> - 修改洞府名称"

        await update.message.reply_text(text)


async def buy_cave_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """购买洞府"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text("❌ 用法: /购买洞府 <位置名称>")
        return

    location = " ".join(context.args)
    base_cost = 50000

    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user.id)
        if not player:
            await update.message.reply_text("❌ 请先使用 /开始 创建角色")
            return

        # 检查是否已有洞府
        result = await db.execute(
            select(CaveDwelling).where(CaveDwelling.player_id == player.id)
        )
        if result.scalar_one_or_none():
            await update.message.reply_text("❌ 你已经拥有洞府了")
            return

        # 检查境界要求
        if player.realm not in ["筑基期", "结丹期", "元婴期", "化神期"]:
            await update.message.reply_text("❌ 需要达到筑基期才能购买洞府")
            return

        # 检查灵石
        if player.spirit_stones < base_cost:
            await update.message.reply_text(f"❌ 灵石不足，需要 {base_cost} 灵石")
            return

        # 扣除灵石
        player.spirit_stones -= base_cost

        # 创建洞府
        cave = CaveDwelling(
            player_id=player.id,
            name=f"{player.nickname}的洞府",
            location=location,
            grade=CaveDwellingGrade.ORDINARY.value,
            level=1,
            spiritual_density=100,
            max_rooms=3,
            current_rooms=0,
            defense=100,
            maintenance_cost=100,
            next_level_cost=10000
        )
        db.add(cave)

        await db.commit()

        text = "🎉 成功购买洞府！\n\n"
        text += f"🏔️ 洞府名称：{cave.name}\n"
        text += f"📍 位置：{cave.location}\n"
        text += f"⭐ 品级：{cave.grade}\n"
        text += f"✨ 灵气浓度：{cave.spiritual_density}\n\n"
        text += "现在可以使用 /建造房间 建造功能房间了！"

        await update.message.reply_text(text)


async def list_room_types_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看可建造的房间类型"""
    text = "🏠 可建造房间类型\n\n"

    room_info = {
        CaveRoomType.CULTIVATION: ("修炼室", "提升修炼速度 +20%", 5000),
        CaveRoomType.ALCHEMY: ("炼丹房", "提升炼丹成功率 +15%", 8000),
        CaveRoomType.REFINERY: ("炼器房", "提升炼器成功率 +15%", 8000),
        CaveRoomType.SPIRIT_FIELD: ("灵田", "种植灵药，收获倍率 +50%", 10000),
        CaveRoomType.SPIRIT_POOL: ("灵池", "每天恢复灵力上限的30%", 6000),
        CaveRoomType.STORAGE: ("储物间", "扩展背包容量 +20格", 4000),
        CaveRoomType.BEAST_ROOM: ("灵兽房", "灵兽修养，提升成长速度 +25%", 7000),
        CaveRoomType.TALISMAN_ROOM: ("制符室", "提升制符成功率 +15%", 8000),
    }

    for room_type, (name, effect, cost) in room_info.items():
        text += f"【{name}】\n"
        text += f"  效果：{effect}\n"
        text += f"  建造费用：{cost} 灵石\n\n"

    text += "使用 /建造房间 <房间类型> 建造房间"

    await update.message.reply_text(text)


async def build_room_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """建造房间"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text("❌ 用法: /建造房间 <房间类型>\n例如: /建造房间 修炼室")
        return

    room_name = " ".join(context.args)

    # 房间类型映射
    room_map = {
        "修炼室": (CaveRoomType.CULTIVATION, "修炼速度 +20%", 5000, 10),
        "炼丹房": (CaveRoomType.ALCHEMY, "炼丹成功率 +15%", 8000, 15),
        "炼器房": (CaveRoomType.REFINERY, "炼器成功率 +15%", 8000, 15),
        "灵田": (CaveRoomType.SPIRIT_FIELD, "种植收获 +50%", 10000, 50),
        "灵池": (CaveRoomType.SPIRIT_POOL, "每天恢复30%灵力", 6000, 30),
        "储物间": (CaveRoomType.STORAGE, "背包 +20格", 4000, 20),
        "灵兽房": (CaveRoomType.BEAST_ROOM, "灵兽成长 +25%", 7000, 25),
        "制符室": (CaveRoomType.TALISMAN_ROOM, "制符成功率 +15%", 8000, 15),
    }

    if room_name not in room_map:
        await update.message.reply_text("❌ 未知的房间类型，使用 /房间列表 查看可建造的房间")
        return

    room_type, effect_desc, cost, bonus = room_map[room_name]

    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user.id)
        if not player:
            await update.message.reply_text("❌ 请先使用 /开始 创建角色")
            return

        # 获取洞府
        result = await db.execute(
            select(CaveDwelling).where(CaveDwelling.player_id == player.id)
        )
        cave = result.scalar_one_or_none()

        if not cave:
            await update.message.reply_text("❌ 你还没有洞府，使用 /购买洞府 购买")
            return

        # 检查房间数量限制
        if cave.current_rooms >= cave.max_rooms:
            await update.message.reply_text(f"❌ 房间已满（{cave.current_rooms}/{cave.max_rooms}），请先升级洞府")
            return

        # 检查灵石
        if player.spirit_stones < cost:
            await update.message.reply_text(f"❌ 灵石不足，需要 {cost} 灵石")
            return

        # 检查是否已有相同类型房间
        result = await db.execute(
            select(CaveRoom).where(
                CaveRoom.cave_id == cave.id,
                CaveRoom.room_type == room_type.value
            )
        )
        if result.scalar_one_or_none():
            await update.message.reply_text(f"❌ 已经建造了{room_name}，不能重复建造")
            return

        # 扣除灵石
        player.spirit_stones -= cost

        # 建造房间
        room = CaveRoom(
            cave_id=cave.id,
            room_type=room_type.value,
            room_name=room_name,
            room_level=1,
            effect_bonus=bonus,
            effect_description=effect_desc,
            build_cost=cost,
            upgrade_cost=cost * 2
        )
        db.add(room)

        cave.current_rooms += 1

        # 记录
        record = CaveUpgradeRecord(
            player_id=player.id,
            cave_id=cave.id,
            upgrade_type=f"建造{room_name}",
            from_level=0,
            to_level=1,
            cost=cost
        )
        db.add(record)

        await db.commit()

        text = f"🎉 成功建造{room_name}！\n\n"
        text += f"🏠 房间：{room_name} Lv.1\n"
        text += f"✨ 效果：{effect_desc}\n"
        text += f"⬆️ 升级费用：{room.upgrade_cost} 灵石"

        await update.message.reply_text(text)


async def upgrade_cave_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """升级洞府"""
    user = update.effective_user

    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user.id)
        if not player:
            await update.message.reply_text("❌ 请先使用 /开始 创建角色")
            return

        # 获取洞府
        result = await db.execute(
            select(CaveDwelling).where(CaveDwelling.player_id == player.id)
        )
        cave = result.scalar_one_or_none()

        if not cave:
            await update.message.reply_text("❌ 你还没有洞府")
            return

        if cave.level >= 10:
            await update.message.reply_text("❌ 洞府已达最高等级")
            return

        # 检查灵石
        if player.spirit_stones < cave.next_level_cost:
            await update.message.reply_text(f"❌ 灵石不足，需要 {cave.next_level_cost} 灵石")
            return

        # 扣除灵石
        player.spirit_stones -= cave.next_level_cost

        old_level = cave.level
        cave.level += 1
        cave.max_rooms += 1  # 每级增加1个房间位
        cave.spiritual_density += 50  # 每级增加50灵气浓度
        cave.defense += 50  # 每级增加50防御

        old_cost = cave.next_level_cost
        cave.next_level_cost = int(cave.next_level_cost * 1.5)
        cave.upgraded_at = datetime.now()

        # 记录
        record = CaveUpgradeRecord(
            player_id=player.id,
            cave_id=cave.id,
            upgrade_type="洞府升级",
            from_level=old_level,
            to_level=cave.level,
            cost=old_cost
        )
        db.add(record)

        await db.commit()

        text = f"🎉 洞府升级成功！\n\n"
        text += f"🏔️ 等级：{old_level} → {cave.level}\n"
        text += f"🏠 房间上限：{cave.max_rooms}\n"
        text += f"✨ 灵气浓度：{cave.spiritual_density}\n"
        text += f"🛡️ 防御值：{cave.defense}\n"
        text += f"\n⬆️ 下次升级需要：{cave.next_level_cost} 灵石"

        await update.message.reply_text(text)


async def maintain_cave_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """维护洞府"""
    user = update.effective_user

    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user.id)
        if not player:
            await update.message.reply_text("❌ 请先使用 /开始 创建角色")
            return

        # 获取洞府
        result = await db.execute(
            select(CaveDwelling).where(CaveDwelling.player_id == player.id)
        )
        cave = result.scalar_one_or_none()

        if not cave:
            await update.message.reply_text("❌ 你还没有洞府")
            return

        # 计算欠费
        days_since_maintenance = (datetime.now() - cave.last_maintenance).days

        if days_since_maintenance == 0:
            await update.message.reply_text("✅ 洞府维护良好，暂不需要支付维护费")
            return

        total_cost = days_since_maintenance * cave.maintenance_cost

        # 检查灵石
        if player.spirit_stones < total_cost:
            await update.message.reply_text(f"❌ 灵石不足，需要 {total_cost} 灵石支付 {days_since_maintenance} 天的维护费")
            return

        # 扣除灵石
        player.spirit_stones -= total_cost
        cave.last_maintenance = datetime.now()

        await db.commit()

        text = f"✅ 洞府维护完成！\n\n"
        text += f"💰 支付维护费：{total_cost} 灵石（{days_since_maintenance}天）\n"
        text += f"📅 下次维护费用：{cave.maintenance_cost} 灵石/天"

        await update.message.reply_text(text)


async def rename_cave_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """修改洞府名称"""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text("❌ 用法: /改名洞府 <新名称>")
        return

    new_name = " ".join(context.args)

    if len(new_name) > 20:
        await update.message.reply_text("❌ 名称过长，最多20个字符")
        return

    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user.id)
        if not player:
            await update.message.reply_text("❌ 请先使用 /开始 创建角色")
            return

        # 获取洞府
        result = await db.execute(
            select(CaveDwelling).where(CaveDwelling.player_id == player.id)
        )
        cave = result.scalar_one_or_none()

        if not cave:
            await update.message.reply_text("❌ 你还没有洞府")
            return

        old_name = cave.name
        cave.name = new_name

        await db.commit()

        await update.message.reply_text(f"✅ 洞府名称已修改：{old_name} → {new_name}")


async def spirit_field_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看灵田状态"""
    user = update.effective_user

    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user.id)
        if not player:
            await update.message.reply_text("❌ 请先使用 /开始 创建角色")
            return

        status = await SpiritFieldService.get_field_status(db, player.id)

        if not status:
            await update.message.reply_text("❌ 你还没有灵田，请先建造灵田房间")
            return

        if not status["occupied"]:
            text = "🌾 灵田状态\n\n"
            text += "灵田空闲中\n\n"
            text += "使用 /种植 <种子名> <数量> 开始种植"
            await update.message.reply_text(text)
            return

        text = "🌾 灵田状态\n\n"
        text += f"🌱 种植作物：{status['harvest_item_name']}\n"
        text += f"📊 数量：{status['quantity']}\n"
        text += f"⭐ 收获倍率：{status['harvest_multiplier']:.2f}x\n"
        text += f"⏰ {status['remaining_time']}\n\n"

        if status["is_ready"]:
            text += "✅ 已成熟，使用 /收获 收获作物"
        else:
            text += f"🕐 种植时间：{status['planted_at'].strftime('%m-%d %H:%M')}\n"
            text += f"🕐 成熟时间：{status['harvest_at'].strftime('%m-%d %H:%M')}"

        await update.message.reply_text(text)


async def plant_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """种植种子"""
    user = update.effective_user

    if len(context.args) < 1:
        await update.message.reply_text(
            "❌ 用法: /种植 <种子名> [数量] [生长小时]\n"
            "例如: /种植 灵草种子 10 24"
        )
        return

    seed_name = context.args[0]
    quantity = int(context.args[1]) if len(context.args) > 1 else 1
    growth_hours = int(context.args[2]) if len(context.args) > 2 else 24

    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user.id)
        if not player:
            await update.message.reply_text("❌ 请先使用 /开始 创建角色")
            return

        # 查找种子物品
        result = await db.execute(
            select(Item).where(Item.name.like(f"%{seed_name}%"))
        )
        seed_items = result.scalars().all()

        if not seed_items:
            await update.message.reply_text(f"❌ 未找到种子：{seed_name}")
            return

        if len(seed_items) > 1:
            text = "找到多个种子，请更精确地指定：\n"
            for item in seed_items:
                text += f"- {item.name}\n"
            await update.message.reply_text(text)
            return

        seed_item = seed_items[0]

        # TODO: 这里应该有个种子到产出物的映射表
        # 简化处理：假设种子名去掉"种子"就是产出物
        harvest_name = seed_item.name.replace("种子", "").replace("种", "")
        result = await db.execute(
            select(Item).where(Item.name == harvest_name)
        )
        harvest_item = result.scalar_one_or_none()

        if not harvest_item:
            await update.message.reply_text(f"❌ 找不到对应的收获物：{harvest_name}")
            return

        # 开始种植
        success, message = await SpiritFieldService.plant_seeds(
            db, player, seed_item.id, harvest_item.id, quantity, growth_hours
        )

        if success:
            text = f"🌾 {message}\n\n"
            text += f"🌱 种子：{seed_item.name} x{quantity}\n"
            text += f"📦 产出：{harvest_item.name}\n"
            text += f"⏰ 生长时间：{growth_hours}小时"
            await update.message.reply_text(text)
        else:
            await update.message.reply_text(f"❌ {message}")


async def harvest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """收获作物"""
    user = update.effective_user

    async with get_db() as db:
        player = await PlayerService.get_player_by_telegram_id(db, user.id)
        if not player:
            await update.message.reply_text("❌ 请先使用 /开始 创建角色")
            return

        success, message, result_data = await SpiritFieldService.harvest(db, player)

        if not success:
            await update.message.reply_text(f"❌ {message}")
            return

        text = f"🎉 收获成功！\n\n"
        text += f"📦 {result_data['item_name']} x{result_data['quantity']}\n"
        text += f"⭐ 收获倍率：{result_data['multiplier']:.2f}x\n\n"
        text += "灵田已空闲，可以继续种植"

        await update.message.reply_text(text)


def register_handlers(application: Application):
    """注册处理器"""
    application.add_handler(MessageHandler(filters.Regex(r"^\.洞府"), cave_info_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.购买洞府"), buy_cave_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.房间列表"), list_room_types_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.建造房间"), build_room_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.升级洞府"), upgrade_cave_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.维护洞府"), maintain_cave_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.改名洞府"), rename_cave_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.灵田"), spirit_field_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.种植"), plant_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.收获"), harvest_command))

    logger.info("洞府系统命令处理器注册完成")
