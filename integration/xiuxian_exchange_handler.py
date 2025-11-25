"""
修仙游戏积分兑换命令处理器
用于PMSManageBot集成
使用中文命令风格
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from .credits_bridge_service import CreditsBridgeService


# 配置
PMS_DB_PATH = "./data/data.db"  # PMSManageBot数据库路径
XIUXIAN_DB_PATH = "./data/data.db"  # 修仙游戏数据库路径（集成后使用同一数据库）
EXCHANGE_RATE = 0.1  # 兑换比例：1积分=0.1灵石
DAILY_LIMIT = 10000  # 每日兑换上限
MIN_EXCHANGE = 100  # 最小兑换数量

# 中文命令名称
CMD_EXCHANGE = "兑换灵石"

# 初始化桥接服务
bridge_service = CreditsBridgeService(PMS_DB_PATH)


async def exchange_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """积分兑换命令 /exchange"""
    user = update.effective_user

    # 获取当前积分
    credits = bridge_service.get_pms_credits(user.id)

    # 获取今日已兑换
    today_total = bridge_service.get_daily_exchange_total(user.id)
    remaining_daily = DAILY_LIMIT - today_total

    # 创建兑换菜单
    keyboard = [
        [
            InlineKeyboardButton("100积分→10灵石", callback_data="exchange_100"),
            InlineKeyboardButton("500积分→50灵石", callback_data="exchange_500"),
        ],
        [
            InlineKeyboardButton("1000积分→100灵石", callback_data="exchange_1000"),
            InlineKeyboardButton("5000积分→500灵石", callback_data="exchange_5000"),
        ],
        [
            InlineKeyboardButton("📊 兑换历史", callback_data="exchange_history"),
            InlineKeyboardButton("❌ 取消", callback_data="exchange_cancel"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"""
💱 **积分兑换中心**

📊 **当前PMS积分**: {credits}

💎 **兑换比例**: 10积分 = 1灵石

📅 **今日已兑换**: {today_total} / {DAILY_LIMIT} 积分
📅 **今日剩余**: {remaining_daily} 积分

💡 **最小兑换**: {MIN_EXCHANGE} 积分

请选择兑换数量：
"""

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )


async def exchange_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理兑换回调"""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data

    if data == "exchange_cancel":
        await query.edit_message_text("❌ 已取消兑换")
        return

    if data == "exchange_history":
        # 显示兑换历史
        await show_exchange_history(query, user.id)
        return

    if data.startswith("exchange_"):
        # 执行兑换
        try:
            credits_amount = int(data.split("_")[1])
            await process_exchange(query, user.id, credits_amount)
        except (ValueError, IndexError):
            await query.edit_message_text("❌ 无效的兑换数量")


async def process_exchange(query, telegram_id: int, credits_amount: int):
    """处理兑换逻辑"""
    # 检查最小兑换数量
    if credits_amount < MIN_EXCHANGE:
        await query.edit_message_text(f"❌ 最小兑换数量为{MIN_EXCHANGE}积分")
        return

    # 检查每日限制
    can_exchange, limit_message = bridge_service.check_daily_limit(
        telegram_id,
        credits_amount,
        DAILY_LIMIT
    )
    if not can_exchange:
        await query.edit_message_text(f"❌ {limit_message}")
        return

    # 执行兑换
    success, message, spirit_stones = bridge_service.exchange_to_spirit_stones(
        telegram_id=telegram_id,
        credits_amount=credits_amount,
        exchange_rate=EXCHANGE_RATE,
        xiuxian_db_path=XIUXIAN_DB_PATH
    )

    if success:
        # 兑换成功
        credits_left = bridge_service.get_pms_credits(telegram_id)
        text = f"""
✅ **兑换成功！**

📉 消耗积分：{credits_amount}
💎 获得灵石：{spirit_stones}

📊 剩余积分：{credits_left}

💡 灵石已自动存入您的修仙账户
使用 /status 查看修仙角色状态
"""
        # 添加继续兑换按钮
        keyboard = [
            [
                InlineKeyboardButton("继续兑换", callback_data="continue_exchange"),
                InlineKeyboardButton("查看状态", callback_data="xiuxian_status"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        # 兑换失败
        await query.edit_message_text(f"❌ {message}")


async def show_exchange_history(query, telegram_id: int):
    """显示兑换历史"""
    history = bridge_service.get_exchange_history(telegram_id, limit=10)

    if not history:
        await query.edit_message_text("📋 暂无兑换记录")
        return

    text = "📋 **兑换历史**（最近10条）\n\n"

    for i, record in enumerate(history, 1):
        created_at = record['created_at']
        credits = record['credits_amount']
        stones = record['spirit_stones_gained']
        rate = record['exchange_rate']

        text += f"{i}. {created_at}\n"
        text += f"   {credits}积分 → {stones}灵石 (比例:{rate})\n\n"

    # 添加返回按钮
    keyboard = [[InlineKeyboardButton("« 返回", callback_data="continue_exchange")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def continue_exchange_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """继续兑换回调"""
    query = update.callback_query
    await query.answer()

    if query.data == "continue_exchange":
        # 返回兑换菜单
        await exchange_command(update, context)
    elif query.data == "xiuxian_status":
        # 跳转到修仙状态（需要导入修仙的status命令）
        await query.edit_message_text("请使用 /status 查看修仙角色状态")


async def quick_exchange_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """快速兑换命令 /exchange 1000"""
    user = update.effective_user

    if not context.args:
        # 没有参数，显示菜单
        await exchange_command(update, context)
        return

    try:
        credits_amount = int(context.args[0])
    except (ValueError, IndexError):
        await update.message.reply_text(
            "❌ 无效的数量\n\n使用方法：/exchange [积分数量]\n例如：/exchange 1000"
        )
        return

    # 检查最小兑换数量
    if credits_amount < MIN_EXCHANGE:
        await update.message.reply_text(f"❌ 最小兑换数量为{MIN_EXCHANGE}积分")
        return

    # 检查每日限制
    can_exchange, limit_message = bridge_service.check_daily_limit(
        user.id,
        credits_amount,
        DAILY_LIMIT
    )
    if not can_exchange:
        await update.message.reply_text(f"❌ {limit_message}")
        return

    # 执行兑换
    success, message, spirit_stones = bridge_service.exchange_to_spirit_stones(
        telegram_id=user.id,
        credits_amount=credits_amount,
        exchange_rate=EXCHANGE_RATE,
        xiuxian_db_path=XIUXIAN_DB_PATH
    )

    if success:
        credits_left = bridge_service.get_pms_credits(user.id)
        text = f"""
✅ **兑换成功！**

📉 消耗积分：{credits_amount}
💎 获得灵石：{spirit_stones}
📊 剩余积分：{credits_left}

💡 灵石已自动存入您的修仙账户
"""
        await update.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ {message}")


# 注册处理器的函数
def register_exchange_handlers(application):
    """注册兑换相关处理器到Bot应用"""
    # 命令处理器 - 使用中文命令
    application.add_handler(CommandHandler(CMD_EXCHANGE, quick_exchange_command))

    # 回调查询处理器
    application.add_handler(CallbackQueryHandler(
        exchange_callback,
        pattern="^exchange_"
    ))
    application.add_handler(CallbackQueryHandler(
        continue_exchange_callback,
        pattern="^(continue_exchange|xiuxian_status)"
    ))


# 使用示例（在PMSManageBot的main.py中）
"""
from app.xiuxian.integration import xiuxian_exchange_handler

def main():
    application = ApplicationBuilder().token(settings.BOT_TOKEN).build()

    # ... 现有handlers ...

    # 注册修仙兑换handlers
    xiuxian_exchange_handler.register_exchange_handlers(application)

    application.run_polling()
"""
