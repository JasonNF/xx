"""开始命令与基础信息处理器"""
import logging
from textwrap import dedent
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bot.config import settings
from bot.models import get_db
from bot.models.player import Player
from bot.services.player_service import PlayerService
from bot.services.spirit_root_service import SpiritRootService
from bot.utils.message_utils import send_and_delete

logger = logging.getLogger(__name__)


def _build_quick_actions() -> InlineKeyboardMarkup:
    """生成常用操作快捷菜单"""
    keyboard = [
        [
            InlineKeyboardButton("📊 角色状态", callback_data="status"),
            InlineKeyboardButton("🧘 开始修炼", callback_data="cultivate"),
        ],
        [
            InlineKeyboardButton("⚔️ 战斗", callback_data="battle"),
            InlineKeyboardButton("🏪 商店", callback_data="shop"),
        ],
        [
            InlineKeyboardButton("🏛️ 宗门", callback_data="sect"),
            InlineKeyboardButton("📖 帮助", callback_data="help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


async def detect_spirit_root_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 或 /检测灵根 命令"""
    user = update.effective_user
    logger.info("用户 %s (%s) 触发 /start", user.id, user.username)

    async with get_db() as db:
        result = await db.execute(
            select(Player)
            .where(Player.telegram_id == user.id)
            .options(selectinload(Player.spirit_root))
        )
        player = result.scalar_one_or_none()

        if player:
            spirit_root_text = ""
            if player.spirit_root:
                spirit_root_text = SpiritRootService.format_spirit_root_info(
                    player.spirit_root,
                    show_comment=False
                )

            message = dedent(f"""
            🎴 欢迎回来，{player.nickname}！

            {spirit_root_text}

            ━━━━━━━━━━━━━━━
            🌟 当前境界：{player.full_realm_name}
            ⚔️ 战力：{player.combat_power:,}
            💎 灵石：{player.spirit_stones:,}
            ━━━━━━━━━━━━━━━

            📖 使用 .帮助 查看所有命令
            📊 使用 .状态 查看详细属性
            """).strip()

            await send_and_delete(update.message, message, reply_markup=_build_quick_actions())
            return

        # 创建新玩家并生成灵根
        player, _ = await PlayerService.get_or_create_player(
            db,
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name or "无名小修"
        )
        await db.commit()

        # 重新加载以便获取灵根信息
        result = await db.execute(
            select(Player)
            .where(Player.telegram_id == user.id)
            .options(selectinload(Player.spirit_root))
        )
        player = result.scalar_one()

        spirit_root_text = ""
        if player.spirit_root:
            spirit_root_text = SpiritRootService.format_spirit_root_info(
                player.spirit_root,
                show_comment=True
            )

        message = dedent(f"""
        🎴 灵根检测完成

        恭喜道友，成功觉醒灵根！

        {spirit_root_text}

        你现在是 {player.full_realm_name}

        🎁 新手福利已发送：
        • 初始灵石：{settings.NEWBIE_GIFT:,}
        • 初始修炼速度：{settings.BASE_CULTIVATION_RATE} 修为/小时

        💡 快速上手：
        • .修炼 2  —— 修炼 2 小时
        • .状态      —— 查看角色状态
        • .帮助      —— 查看所有命令
        """).strip()

        await send_and_delete(update.message, message, reply_markup=_build_quick_actions())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /help 或 .帮助 命令"""
    help_text = dedent(f"""
    📖 **{settings.GAME_NAME} - 快速指引**

    **🎮 基础命令**
    .检测灵根 —— 开始游戏 / 查看角色
    .状态 —— 查看角色状态
    .改名 <新道号> —— 修改道号（终生一次，2万灵石）
    .改名状态 —— 查看改名次数和时间
    .帮助 —— 显示本指南

    **🧘 修炼系统**
    .修炼 <小时> —— 开始修炼
    .结算 —— 完成修炼收取修为
    .取消 —— 取消当前修炼
    .突破 —— 尝试突破境界

    **⚔️ 战斗系统**
    .战斗 <怪物名> —— PVE 挑战
    .切磋 —— PVP 决斗
    .技能 —— 查看已学技能
    .学习 <技能名> —— 学习技能
    .升级 <技能名> —— 升级技能

    **📋 任务与秘境**
    .任务 —— 查看任务列表
    .接取 <任务ID> —— 接任务
    .完成 <任务ID> —— 交任务
    .秘境 —— 查看秘境
    .探索 <秘境名> —— 进入秘境

    **💰 经济系统**
    .签到 —— 每日签到
    .积分商城 —— 浏览积分商品
    .我的积分 —— 查看积分记录
    .市场 —— 玩家交易行

    💡 提示：修炼获取修为，任务与秘境提供稀有资源，宗门/宗门战玩法在中后期开放。
    """).strip()

    await send_and_delete(update.message, help_text, parse_mode="Markdown")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看角色状态"""
    user = update.effective_user

    async with get_db() as db:
        result = await db.execute(
            select(Player)
            .where(Player.telegram_id == user.id)
            .options(selectinload(Player.spirit_root))
        )
        player = result.scalar_one_or_none()

        if not player:
            await send_and_delete(update.message, "❌ 你还未踏入修仙之路，请先使用 .检测灵根")
            return

        status_text = dedent(f"""
        👤 **{player.nickname}**

        🌟 **境界**：{player.full_realm_name}
        📊 **修为**：{player.cultivation_exp:,}/{player.next_realm_exp:,}
        ⚔️ **战力**：{player.combat_power:,}

        💚 **生命**：{player.hp}/{player.max_hp}
        💙 **灵力**：{player.spiritual_power}/{player.max_spiritual_power}
        ⚡ **速度**：{player.speed}
        💥 **暴击率**：{player.crit_rate * 100:.1f}%

        🧠 **悟性**：{player.comprehension}
        🔮 **神识**：{player.divine_sense}/{player.max_divine_sense}
        💎 **灵石**：{player.spirit_stones:,}
        🏆 **贡献**：{player.contribution:,}
        """).strip()

        if player.spirit_root:
            root_desc = SpiritRootService.get_root_description(player.spirit_root)
            status_text += f"\n🌈 **灵根**：{root_desc}（纯度 {player.spirit_root.purity}%）"

        await send_and_delete(update.message, status_text, parse_mode="Markdown")


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理主菜单按钮回调"""
    query = update.callback_query
    await query.answer()

    action = query.data

    # 根据回调数据调用对应的命令
    if action == "status":
        # 直接发送状态信息
        user = update.effective_user
        async with get_db() as db:
            result = await db.execute(
                select(Player)
                .where(Player.telegram_id == user.id)
                .options(selectinload(Player.spirit_root))
            )
            player = result.scalar_one_or_none()

            if not player:
                await query.edit_message_text("❌ 你还未踏入修仙之路，请先使用 .检测灵根")
                return

            status_text = dedent(f"""
            👤 **{player.nickname}**

            🌟 **境界**：{player.full_realm_name}
            📊 **修为**：{player.cultivation_exp:,}/{player.next_realm_exp:,}
            ⚔️ **战力**：{player.combat_power:,}

            💚 **生命**：{player.hp}/{player.max_hp}
            💙 **灵力**：{player.spiritual_power}/{player.max_spiritual_power}
            ⚡ **速度**：{player.speed}
            💥 **暴击率**：{player.crit_rate * 100:.1f}%

            🧠 **悟性**：{player.comprehension}
            🔮 **神识**：{player.divine_sense}/{player.max_divine_sense}
            💎 **灵石**：{player.spirit_stones:,}
            🏆 **贡献**：{player.contribution:,}
            """).strip()

            if player.spirit_root:
                root_desc = SpiritRootService.get_root_description(player.spirit_root)
                status_text += f"\n🌈 **灵根**：{root_desc}（纯度 {player.spirit_root.purity}%）"

            await query.edit_message_text(status_text, parse_mode="Markdown", reply_markup=_build_quick_actions())

    elif action == "cultivate":
        from bot.handlers.cultivation import cultivate_command
        # 创建一个假的消息上下文来调用命令
        await query.edit_message_text("🧘 请使用 `.修炼 <小时>` 命令开始修炼\n\n例如：`.修炼 2` 修炼2小时", parse_mode="Markdown", reply_markup=_build_quick_actions())

    elif action == "battle":
        await query.edit_message_text("⚔️ 战斗系统\n\n• `.战斗 <怪物名>` - PVE挑战\n• `.切磋` - PVP决斗\n• `.技能` - 查看技能", parse_mode="Markdown", reply_markup=_build_quick_actions())

    elif action == "shop":
        await query.edit_message_text("🏪 商店系统\n\n• `.商店` - 查看物品商店\n• `.积分商城` - 积分兑换商品\n• `.市场` - 玩家交易行", parse_mode="Markdown", reply_markup=_build_quick_actions())

    elif action == "sect":
        await query.edit_message_text("🏛️ 宗门系统\n\n• `.宗门` - 查看宗门信息\n• `.宗门任务` - 领取宗门任务\n• `.宗门贡献` - 查看贡献排名", parse_mode="Markdown", reply_markup=_build_quick_actions())

    elif action == "help":
        help_text = dedent(f"""
        📖 **{settings.GAME_NAME} - 快速指引**

        **🎮 基础命令**
        .检测灵根 / .状态 / .帮助

        **🧘 修炼系统**
        .修炼 <小时> / .结算 / .突破

        **⚔️ 战斗系统**
        .战斗 <怪物> / .切磋 / .技能

        **💰 经济系统**
        .签到 / .商店 / .积分商城
        """).strip()
        await query.edit_message_text(help_text, parse_mode="Markdown", reply_markup=_build_quick_actions())


def register_handlers(application):
    """注册基础命令处理器"""
    logger.info("注册 start/help/info 命令处理器")
    application.add_handler(CommandHandler("start", detect_spirit_root_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.检测灵根"), detect_spirit_root_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.帮助"), help_command))
    application.add_handler(CommandHandler("info", status_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.状态"), status_command))
    application.add_handler(CallbackQueryHandler(menu_callback, pattern="^(status|cultivate|battle|shop|sect|help)$"))
