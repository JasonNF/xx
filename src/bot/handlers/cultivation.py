"""修炼相关命令处理器"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler

from bot.models import get_db
from bot.services.player_service import PlayerService
from bot.services.cultivation_service import CultivationService


async def cultivate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /cultivate 命令"""
    user = update.effective_user

    async with get_db() as db:
        player = await PlayerService.get_player(db, user.id)

        if not player:
            await update.message.reply_text("请先使用 /开始 开始游戏")
            return

        # 检查参数
        if not context.args:
            # 显示修炼菜单
            keyboard = [
                [
                    InlineKeyboardButton("1小时", callback_data="cultivate_1"),
                    InlineKeyboardButton("2小时", callback_data="cultivate_2"),
                    InlineKeyboardButton("4小时", callback_data="cultivate_4"),
                ],
                [
                    InlineKeyboardButton("8小时", callback_data="cultivate_8"),
                    InlineKeyboardButton("12小时", callback_data="cultivate_12"),
                    InlineKeyboardButton("24小时", callback_data="cultivate_24"),
                ],
                [
                    InlineKeyboardButton("完成修炼", callback_data="finish_cultivate"),
                    InlineKeyboardButton("取消修炼", callback_data="cancel_cultivate"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            status = await CultivationService.get_cultivation_status(player)
            exp_per_hour = await CultivationService.calculate_cultivation_exp(db, player, 1)
            text = f"""
🧘 **修炼系统**

当前状态：{status}

💡 选择修炼时长：
• 修炼时间越长，获得修为越多
• 悟性和根骨影响修炼效率
• 修炼中可能遇到随机事件

**当前修炼速度**: ~{exp_per_hour} 修为/小时
"""
            await update.message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            return

        # 解析修炼时长
        try:
            hours = float(context.args[0])
            success, message = await CultivationService.start_cultivation(db, player, hours)

            await update.message.reply_text(message)
        except ValueError:
            await update.message.reply_text("请输入有效的小时数，例如：/修炼 2")


async def finish_cultivation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /finish 命令 - 完成修炼"""
    user = update.effective_user

    async with get_db() as db:
        player = await PlayerService.get_player(db, user.id)

        if not player:
            await update.message.reply_text("请先使用 /开始 开始游戏")
            return

        success, message, exp_gained = await CultivationService.finish_cultivation(db, player)

        if success:
            # 检查是否可以突破
            can_break, _ = await PlayerService.can_breakthrough(player)
            if can_break:
                keyboard = [[InlineKeyboardButton("💫 突破境界", callback_data="breakthrough")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    f"{message}\n\n修为已满！可以尝试突破境界了！",
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(message)
        else:
            await update.message.reply_text(message)


async def cancel_cultivation_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /cancel 命令 - 取消修炼"""
    user = update.effective_user

    async with get_db() as db:
        player = await PlayerService.get_player(db, user.id)

        if not player:
            await update.message.reply_text("请先使用 /开始 开始游戏")
            return

        success, message = await CultivationService.cancel_cultivation(db, player)
        await update.message.reply_text(message)


async def breakthrough_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /breakthrough 命令 - 突破境界"""
    user = update.effective_user

    async with get_db() as db:
        player = await PlayerService.get_player(db, user.id)

        if not player:
            await update.message.reply_text("请先使用 /开始 开始游戏")
            return

        success, message = await PlayerService.breakthrough(db, player)

        if success:
            # 播放"动画"效果
            celebration = """
✨✨✨✨✨✨✨✨
🌟 境界突破成功！ 🌟
✨✨✨✨✨✨✨✨

{message}

💚 生命值：{player.max_hp}
💙 灵力值：{player.max_spiritual_power}
⚔️ 攻击力：{player.attack}
🛡️ 防御力：{player.defense}
""".format(message=message, player=player)
            await update.message.reply_text(celebration)
        else:
            await update.message.reply_text(f"❌ {message}")


# 回调查询处理
async def cultivation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理修炼相关的回调"""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data

    async with get_db() as db:
        player = await PlayerService.get_player(db, user.id)

        if not player:
            await query.edit_message_text("请先使用 /检测灵根 开始游戏")
            return

        if data.startswith("cultivate_"):
            # 开始修炼
            hours = int(data.split("_")[1])
            success, message = await CultivationService.start_cultivation(db, player, hours)
            await query.edit_message_text(f"🧘 {message}")

        elif data == "finish_cultivate":
            # 完成修炼
            success, message, exp_gained = await CultivationService.finish_cultivation(db, player)
            await query.edit_message_text(message)

        elif data == "cancel_cultivate":
            # 取消修炼
            success, message = await CultivationService.cancel_cultivation(db, player)
            await query.edit_message_text(message)

        elif data == "breakthrough":
            # 突破境界
            success, message = await PlayerService.breakthrough(db, player)
            if success:
                await query.edit_message_text(f"✨ {message}")
            else:
                await query.edit_message_text(f"❌ {message}")


# 注册处理器
def register_handlers(application):
    """注册修炼相关处理器"""
    application.add_handler(MessageHandler(filters.Regex(r"^\.修炼"), cultivate_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.结算"), finish_cultivation_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.取消"), cancel_cultivation_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.突破"), breakthrough_command))

    # 回调查询
    application.add_handler(CallbackQueryHandler(
        cultivation_callback,
        pattern="^(cultivate_|finish_cultivate|cancel_cultivate|breakthrough)"
    ))
