"""道号修改处理器"""
import re
from datetime import datetime
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes, CommandHandler

from bot.models import get_db
from bot.services.player_service import PlayerService


# 改名配置（已平衡优化）
RENAME_COST = 20000   # 改名消耗灵石：2万（原10万，降低80%）
MIN_NAME_LENGTH = 2   # 最小长度
MAX_NAME_LENGTH = 10  # 最大长度

# 禁用词列表（可根据需要扩展）
FORBIDDEN_WORDS = [
    "管理员", "GM", "系统", "官方", "客服",
    "fuck", "shit", "damn", "傻逼", "操你妈",
    # 可以添加更多禁用词
]


async def rename_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /改名 命令"""
    user = update.effective_user

    # 检查参数
    if not context.args or len(context.args) == 0:
        await update.message.reply_text(
            "❌ 用法错误\n\n"
            "正确用法: /改名 <新道号>\n\n"
            "📋 改名规则：\n"
            f"• 道号长度：{MIN_NAME_LENGTH}-{MAX_NAME_LENGTH}个字符\n"
            f"• 消耗灵石：{RENAME_COST:,}\n"
            "• 终生只能改名一次\n"
            "• 不可包含特殊字符或敏感词\n\n"
            "示例: /改名 逍遥散人"
        )
        return

    new_nickname = " ".join(context.args).strip()

    # 验证新道号
    is_valid, error_message = validate_nickname(new_nickname)
    if not is_valid:
        await update.message.reply_text(f"❌ {error_message}")
        return

    async with get_db() as db:
        player = await PlayerService.get_player(db, user.id)

        if not player:
            await update.message.reply_text("你还未踏入修仙之路，请先使用 /检测灵根 开始游戏")
            return

        # 检查是否已经改过名
        if player.has_renamed:
            rename_date = player.rename_time.strftime("%Y年%m月%d日") if player.rename_time else "未知"
            await update.message.reply_text(
                f"❌ 改名失败\n\n"
                f"道友已于 {rename_date} 改过道号\n"
                f"当前道号：{player.nickname}\n\n"
                f"⚠️ 每人终生只能改名一次，请珍惜机会！"
            )
            return

        # 检查灵石是否足够
        if player.spirit_stones < RENAME_COST:
            shortage = RENAME_COST - player.spirit_stones
            await update.message.reply_text(
                f"❌ 灵石不足\n\n"
                f"改名需要：{RENAME_COST:,} 灵石\n"
                f"当前拥有：{player.spirit_stones:,} 灵石\n"
                f"还需要：{shortage:,} 灵石"
            )
            return

        # 检查是否与当前道号相同
        if new_nickname == player.nickname:
            await update.message.reply_text(
                f"❌ 新道号不能与当前道号相同\n\n"
                f"当前道号：{player.nickname}"
            )
            return

        # 记录旧道号
        old_nickname = player.nickname

        # 执行改名
        player.nickname = new_nickname
        player.has_renamed = True
        player.rename_time = datetime.now()
        player.spirit_stones -= RENAME_COST

        await db.commit()

        # 改名成功消息
        success_message = f"""
✨ 改名成功！

━━━━━━━━━━━━━━━
📜 原道号：{old_nickname}
🌟 新道号：{new_nickname}
💎 消耗灵石：{RENAME_COST:,}
💰 剩余灵石：{player.spirit_stones:,}
━━━━━━━━━━━━━━━

⚠️ 此为终生唯一改名机会，已使用！

从今日起，修仙界将以 {new_nickname} 之名铭记道友！
"""

        await update.message.reply_text(success_message)


def validate_nickname(nickname: str) -> tuple[bool, str]:
    """验证道号合法性

    Returns:
        (is_valid, error_message)
    """
    # 长度检查
    if len(nickname) < MIN_NAME_LENGTH:
        return False, f"道号长度不能少于{MIN_NAME_LENGTH}个字符"

    if len(nickname) > MAX_NAME_LENGTH:
        return False, f"道号长度不能超过{MAX_NAME_LENGTH}个字符"

    # 空白字符检查
    if not nickname or nickname.isspace():
        return False, "道号不能为空或只包含空格"

    # 特殊字符检查（只允许中文、英文、数字、常见标点）
    if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9·•]+$', nickname):
        return False, "道号只能包含中文、英文、数字和·符号"

    # 禁用词检查
    nickname_lower = nickname.lower()
    for word in FORBIDDEN_WORDS:
        if word.lower() in nickname_lower:
            return False, f"道号包含禁用词：{word}"

    # 数字开头检查
    if nickname[0].isdigit():
        return False, "道号不能以数字开头"

    return True, ""


async def check_rename_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看改名状态 - /改名状态"""
    user = update.effective_user

    async with get_db() as db:
        player = await PlayerService.get_player(db, user.id)

        if not player:
            await update.message.reply_text("你还未踏入修仙之路，请先使用 /检测灵根 开始游戏")
            return

        if player.has_renamed:
            rename_date = player.rename_time.strftime("%Y年%m月%d日 %H:%M") if player.rename_time else "未知"
            status_message = f"""
📋 改名状态

━━━━━━━━━━━━━━━
🌟 当前道号：{player.nickname}
📅 改名时间：{rename_date}
🚫 改名次数：已使用（1/1）
━━━━━━━━━━━━━━━

⚠️ 终生改名机会已用完
"""
        else:
            status_message = f"""
📋 改名状态

━━━━━━━━━━━━━━━
🌟 当前道号：{player.nickname}
✅ 改名次数：可用（0/1）
💎 改名费用：{RENAME_COST:,} 灵石
💰 当前灵石：{player.spirit_stones:,} 灵石
━━━━━━━━━━━━━━━

💡 使用 /改名 <新道号> 修改道号
⚠️ 终生只能改名一次，请慎重考虑！
"""

        await update.message.reply_text(status_message)


def register_handlers(application):
    """注册改名相关处理器"""
    application.add_handler(MessageHandler(filters.Regex(r"^\.改名"), rename_command))
    application.add_handler(MessageHandler(filters.Regex(r"^\.改名状态"), check_rename_status_command))
