"""
修仙游戏核心命令处理器
集成到PMSManageBot
使用中文命令风格
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from datetime import datetime, timedelta
import sqlite3
import json
import random
from typing import Tuple, Optional

# 配置
PMS_DB_PATH = "./data/data.db"  # PMSManageBot数据库路径
BATTLE_COOLDOWN_MINUTES = 5  # 战斗冷却时间

# ============================
# 命令名称定义（中文风格）
# ============================
# 基础命令
CMD_START = "灵根测试"        # 创建角色/开始游戏
CMD_STATUS = "状态"           # 查看角色状态
CMD_SIGN = "签到"             # 每日签到
CMD_HELP = "NPC"              # 帮助信息

# 修炼系统
CMD_CULTIVATE = "闭关"        # 开始修炼
CMD_FINISH = "出关"           # 完成修炼
CMD_BREAKTHROUGH = "渡劫"     # 境界突破

# 战斗系统
CMD_BATTLE = "历练"           # 挑战怪物
CMD_PVP = "切磋"              # 玩家对战

# 物品系统
CMD_BAG = "储物袋"            # 查看背包
CMD_USE = "使用"              # 使用物品

# 商店系统
CMD_SHOP = "坊市"             # 打开商店
CMD_BUY = "购买"              # 购买物品

# 积分兑换
CMD_EXCHANGE = "兑换灵石"     # 积分兑换

# ============================
# 数据库操作辅助函数
# ============================

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(PMS_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_player(telegram_id: int) -> Optional[dict]:
    """获取玩家信息"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM xiuxian_players WHERE telegram_id = ?", (telegram_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def create_player(telegram_id: int, name: str) -> dict:
    """创建新玩家"""
    conn = get_db_connection()
    cur = conn.cursor()

    # 随机生成根骨和悟性 (8-15)
    comprehension = random.randint(8, 15)
    root_bone = random.randint(8, 15)

    cur.execute("""
        INSERT INTO xiuxian_players (
            telegram_id, name, comprehension, root_bone, spirit_stones
        ) VALUES (?, ?, ?, ?, 1000)
    """, (telegram_id, name, comprehension, root_bone))

    conn.commit()
    conn.close()

    return get_player(telegram_id)


def update_player(telegram_id: int, **kwargs):
    """更新玩家属性"""
    if not kwargs:
        return

    conn = get_db_connection()
    cur = conn.cursor()

    set_clause = ", ".join(f"{k} = ?" for k in kwargs.keys())
    values = list(kwargs.values()) + [telegram_id]

    cur.execute(
        f"UPDATE xiuxian_players SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE telegram_id = ?",
        values
    )
    conn.commit()
    conn.close()


# ============================
# /灵根测试 - 开始修仙之旅
# ============================

async def xiuxian_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """开始修仙之旅 - 灵根测试"""
    user = update.effective_user
    player = get_player(user.id)

    if player:
        await update.message.reply_text(
            f"欢迎回来，{player['name']}道友！\n\n"
            f"当前境界：{player['realm']} {player['realm_level']}层\n"
            f"使用 /{CMD_STATUS} 查看详细信息"
        )
        return

    # 创建新角色
    player = create_player(user.id, user.first_name or "无名氏")

    keyboard = [
        [InlineKeyboardButton("📊 查看状态", callback_data="xiuxian_status")],
        [InlineKeyboardButton("💪 闭关修炼", callback_data="xiuxian_cultivate_menu")],
        [InlineKeyboardButton("⚔️ 外出历练", callback_data="xiuxian_battle_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"✨ **灵根测试完成！**\n\n"
        f"恭喜 {player['name']} 道友，你具备修仙资质！\n\n"
        f"🎲 **灵根检测结果**：\n"
        f"   • 悟性：{player['comprehension']} {'(天赋异禀)' if player['comprehension'] >= 13 else '(资质平平)' if player['comprehension'] <= 9 else ''}\n"
        f"   • 根骨：{player['root_bone']} {'(仙体之质)' if player['root_bone'] >= 13 else '(凡人之躯)' if player['root_bone'] <= 9 else ''}\n\n"
        f"💎 赠送初始灵石：1000\n\n"
        f"从此踏上仙途，愿道友仙路坦荡！\n\n"
        f"📖 使用 /{CMD_HELP} 查看所有命令",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


# ============================
# /个人状态 - 查看角色状态
# ============================

async def xiuxian_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看角色状态"""
    user = update.effective_user
    player = get_player(user.id)

    if not player:
        await update.message.reply_text(f"您还未踏入修仙之路，请先使用 /{CMD_START} 进行灵根测试")
        return

    # 计算突破进度
    progress = int((player['cultivation_exp'] / player['cultivation_exp_required']) * 100)
    progress_bar = "█" * (progress // 10) + "░" * (10 - progress // 10)

    status_text = f"""
📊 **{player['name']}的修仙面板**

🌟 **境界**: {player['realm']} {player['realm_level']}层
💫 **修为**: {player['cultivation_exp']:,} / {player['cultivation_exp_required']:,}
{progress_bar} {progress}%

⚔️ **战力属性**:
   • 气血: {player['hp']}/{player['max_hp']}
   • 灵力: {player['spiritual_power']}/{player['max_spiritual_power']}
   • 攻击: {player['attack']}
   • 防御: {player['defense']}
   • 身法: {player['speed']}

🎯 **修炼资质**:
   • 悟性: {player['comprehension']}
   • 根骨: {player['root_bone']}

💎 **灵石**: {player['spirit_stones']:,}

📈 **战绩**: {player['battles_won']}胜 / {player['battles_lost']}负

{'🧘 正在闭关修炼中...' if player['is_cultivating'] else ''}
"""

    keyboard = [
        [
            InlineKeyboardButton("🧘 闭关", callback_data="xiuxian_cultivate_menu"),
            InlineKeyboardButton("⚔️ 历练", callback_data="xiuxian_battle_menu"),
        ],
        [
            InlineKeyboardButton("🎒 储物袋", callback_data="xiuxian_inventory"),
            InlineKeyboardButton("🏪 坊市", callback_data="xiuxian_shop"),
        ],
        [
            InlineKeyboardButton("⬆️ 渡劫突破", callback_data="xiuxian_breakthrough"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            status_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            status_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )


# ============================
# /闭关修炼 - 修炼系统
# ============================

async def cultivate_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """修炼菜单"""
    query = update.callback_query
    if query:
        await query.answer()
        user = query.from_user
    else:
        user = update.effective_user

    player = get_player(user.id)

    if not player:
        text = f"请先使用 /{CMD_START} 进行灵根测试"
        if query:
            await query.edit_message_text(text)
        else:
            await update.message.reply_text(text)
        return

    if player['is_cultivating']:
        # 正在修炼中，显示完成选项
        start_time = datetime.fromisoformat(player['cultivation_start_time'])
        duration = timedelta(hours=player['cultivation_duration_hours'])
        end_time = start_time + duration
        now = datetime.now()

        if now >= end_time:
            # 修炼完成
            keyboard = [[InlineKeyboardButton("✅ 出关收取修为", callback_data="xiuxian_finish_cultivate")]]
            text = "✨ 闭关时间已到！点击出关收取修为。"
        else:
            remaining = end_time - now
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            text = f"🧘 闭关修炼中...\n\n距离出关还需: {hours}时辰{minutes}刻"
            keyboard = [[InlineKeyboardButton("« 返回", callback_data="xiuxian_status")]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        if query:
            await query.edit_message_text(text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(text, reply_markup=reply_markup)
        return

    # 显示修炼选项
    keyboard = [
        [
            InlineKeyboardButton("2时辰", callback_data="xiuxian_cultivate_2"),
            InlineKeyboardButton("4时辰", callback_data="xiuxian_cultivate_4"),
        ],
        [
            InlineKeyboardButton("8时辰", callback_data="xiuxian_cultivate_8"),
            InlineKeyboardButton("12时辰", callback_data="xiuxian_cultivate_12"),
        ],
        [InlineKeyboardButton("« 返回", callback_data="xiuxian_status")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "🧘 **选择闭关时长**\n\n"
        "闭关期间可以离开，时间到后回来出关即可。\n\n"
        f"当前悟性：{player['comprehension']}\n"
        f"当前根骨：{player['root_bone']}"
    )

    if query:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def start_cultivate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """开始修炼"""
    query = update.callback_query
    await query.answer()

    # 解析时长
    hours = int(query.data.split("_")[-1])
    user = query.from_user

    # 更新数据库
    update_player(
        user.id,
        is_cultivating=True,
        cultivation_start_time=datetime.now().isoformat(),
        cultivation_duration_hours=hours
    )

    await query.edit_message_text(
        f"✅ 开始闭关修炼！\n\n"
        f"闭关时长：{hours}时辰\n"
        f"预计出关时间：{(datetime.now() + timedelta(hours=hours)).strftime('%H:%M')}\n\n"
        f"闭关期间您可以离开，时间到后使用 /{CMD_FINISH} 出关"
    )


async def finish_cultivate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """完成修炼 - 出关"""
    query = update.callback_query if update.callback_query else None
    if query:
        await query.answer()

    user = update.effective_user
    player = get_player(user.id)

    if not player:
        text = f"请先使用 /{CMD_START} 进行灵根测试"
        if query:
            await query.edit_message_text(text)
        else:
            await update.message.reply_text(text)
        return

    if not player['is_cultivating']:
        text = "您当前没有在闭关修炼中"
        if query:
            await query.edit_message_text(text)
        else:
            await update.message.reply_text(text)
        return

    # 计算修为收益
    start_time = datetime.fromisoformat(player['cultivation_start_time'])
    planned_hours = player['cultivation_duration_hours']

    # 基础速率
    base_rate = 100  # 每小时100修为
    comprehension_bonus = 1 + (player['comprehension'] - 10) * 0.05
    root_bone_bonus = 1 + (player['root_bone'] - 10) * 0.03

    exp_gained = int(base_rate * planned_hours * comprehension_bonus * root_bone_bonus)

    # 随机事件
    event_text = ""
    if random.random() < 0.1:  # 10%顿悟
        bonus = int(exp_gained * 0.5)
        exp_gained += bonus
        event_text = f"\n\n🌟 闭关时福至心灵，顿悟天道！额外获得{bonus}修为"
    elif random.random() < 0.05:  # 5%走火入魔
        loss = int(exp_gained * 0.3)
        exp_gained -= loss
        event_text = f"\n\n⚠️ 心魔入侵，险些走火入魔！损失{loss}修为"

    # 更新玩家
    new_exp = player['cultivation_exp'] + exp_gained
    update_player(
        user.id,
        is_cultivating=False,
        cultivation_start_time=None,
        cultivation_duration_hours=None,
        cultivation_exp=new_exp
    )

    text = f"""
✨ **出关！**

⏱️ 闭关时长: {planned_hours}时辰
💫 获得修为: {exp_gained:,}
📊 当前修为: {new_exp:,} / {player['cultivation_exp_required']:,}
{event_text}

{'🎉 修为圆满，可以尝试渡劫突破了！使用 /' + CMD_BREAKTHROUGH if new_exp >= player['cultivation_exp_required'] else ''}
"""

    if query:
        await query.edit_message_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, parse_mode="Markdown")


# ============================
# /渡劫突破 - 境界突破
# ============================

async def breakthrough(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """境界突破 - 渡劫"""
    query = update.callback_query if update.callback_query else None
    if query:
        await query.answer()

    user = update.effective_user
    player = get_player(user.id)

    if not player:
        text = f"请先使用 /{CMD_START} 进行灵根测试"
        if query:
            await query.edit_message_text(text)
        else:
            await update.message.reply_text(text)
        return

    # 检查修为是否足够
    if player['cultivation_exp'] < player['cultivation_exp_required']:
        text = f"修为不足！还需要{player['cultivation_exp_required'] - player['cultivation_exp']}修为才能渡劫"
        if query:
            await query.edit_message_text(text)
        else:
            await update.message.reply_text(text)
        return

    # 计算成功率
    base_chance = 0.70
    comprehension_bonus = player['comprehension'] * 0.01
    root_bone_bonus = player['root_bone'] * 0.005
    realm_penalty = player['realm_level'] * 0.05

    success_rate = min(0.95, max(0.30, base_chance + comprehension_bonus + root_bone_bonus - realm_penalty))

    # 突破尝试
    success = random.random() < success_rate

    if success:
        # 突破成功
        new_level = player['realm_level'] + 1
        new_exp_required = int(player['cultivation_exp_required'] * 1.5)

        # 属性提升
        hp_gain = 50
        sp_gain = 20
        atk_gain = 5
        def_gain = 3
        spd_gain = 2

        update_player(
            user.id,
            realm_level=new_level,
            cultivation_exp=0,
            cultivation_exp_required=new_exp_required,
            max_hp=player['max_hp'] + hp_gain,
            hp=player['max_hp'] + hp_gain,
            max_spiritual_power=player['max_spiritual_power'] + sp_gain,
            spiritual_power=player['max_spiritual_power'] + sp_gain,
            attack=player['attack'] + atk_gain,
            defense=player['defense'] + def_gain,
            speed=player['speed'] + spd_gain
        )

        text = f"""
🎉 **渡劫成功！**

⚡ 天劫降临，道友安然渡过！

🌟 {player['realm']} {player['realm_level']}层 → {new_level}层

📈 **属性提升**:
   • 气血 +{hp_gain}
   • 灵力 +{sp_gain}
   • 攻击 +{atk_gain}
   • 防御 +{def_gain}
   • 身法 +{spd_gain}

💫 下次渡劫需要: {new_exp_required:,} 修为
"""
    else:
        # 突破失败
        exp_loss = int(player['cultivation_exp'] * 0.1)
        new_exp = max(0, player['cultivation_exp'] - exp_loss)

        update_player(user.id, cultivation_exp=new_exp)

        text = f"""
💔 **渡劫失败...**

⚡ 天劫之下，道心受损！

修为倒退: -{exp_loss:,}
剩余修为: {new_exp:,}

渡劫成功率: {int(success_rate * 100)}%

继续修炼，待时机成熟再试！
"""

    if query:
        await query.edit_message_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, parse_mode="Markdown")


# ============================
# /历练 - 战斗系统
# ============================

async def battle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """战斗菜单"""
    query = update.callback_query
    if query:
        await query.answer()

    keyboard = [
        [InlineKeyboardButton("🐺 野外历练", callback_data="xiuxian_battle_wild")],
        [InlineKeyboardButton("😈 挑战妖王", callback_data="xiuxian_battle_boss")],
        [InlineKeyboardButton("« 返回", callback_data="xiuxian_status")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "⚔️ **选择历练方式**\n\n"
        "🐺 野外历练：斩妖除魔，获得修为和灵石\n"
        "😈 挑战妖王：危险重重，奖励丰厚"
    )

    if query:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def battle_wild(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """野外战斗"""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    player = get_player(user.id)

    # 检查冷却
    if player['last_battle_time']:
        last_battle = datetime.fromisoformat(player['last_battle_time'])
        cooldown = timedelta(minutes=BATTLE_COOLDOWN_MINUTES)
        if datetime.now() - last_battle < cooldown:
            remaining = cooldown - (datetime.now() - last_battle)
            await query.edit_message_text(
                f"⏳ 需要恢复真元，还需{int(remaining.total_seconds() // 60)}刻钟"
            )
            return

    # 随机选择怪物
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM xiuxian_monsters WHERE realm = ? AND is_boss = 0 ORDER BY RANDOM() LIMIT 1",
        (player['realm'],)
    )
    monster = cur.fetchone()
    conn.close()

    if not monster:
        await query.edit_message_text("此地已无妖魔，换个地方历练吧")
        return

    # 战斗计算（简化版）
    player_power = player['attack'] + player['defense'] + player['speed']
    monster_power = monster['attack'] + monster['defense'] + monster['speed']

    win_chance = player_power / (player_power + monster_power)
    win = random.random() < win_chance

    if win:
        exp_reward = monster['exp_reward']
        stones_reward = monster['spirit_stones_reward']

        update_player(
            user.id,
            cultivation_exp=player['cultivation_exp'] + exp_reward,
            spirit_stones=player['spirit_stones'] + stones_reward,
            total_battles=player['total_battles'] + 1,
            battles_won=player['battles_won'] + 1,
            last_battle_time=datetime.now().isoformat()
        )

        text = f"""
⚔️ **斩妖成功！**

击败了 {monster['name']}

💫 获得修为: {exp_reward}
💎 获得灵石: {stones_reward}
"""
    else:
        hp_loss = int(player['max_hp'] * 0.2)
        new_hp = max(0, player['hp'] - hp_loss)

        update_player(
            user.id,
            hp=new_hp,
            total_battles=player['total_battles'] + 1,
            battles_lost=player['battles_lost'] + 1,
            last_battle_time=datetime.now().isoformat()
        )

        text = f"""
💔 **历练失败...**

被 {monster['name']} 击伤

❤️ 损失气血: {hp_loss}
剩余气血: {new_hp}/{player['max_hp']}
"""

    await query.edit_message_text(text, parse_mode="Markdown")


# ============================
# /每日签到 - 签到系统
# ============================

async def daily_sign(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """每日签到"""
    user = update.effective_user
    player = get_player(user.id)

    if not player:
        await update.message.reply_text(f"请先使用 /{CMD_START} 进行灵根测试")
        return

    today = datetime.now().date()
    last_sign = datetime.fromisoformat(player['last_sign_in_date']).date() if player['last_sign_in_date'] else None

    if last_sign == today:
        await update.message.reply_text("今日已在宗门签到过了！")
        return

    # 计算连续签到
    if last_sign == today - timedelta(days=1):
        new_streak = player['sign_in_streak'] + 1
    else:
        new_streak = 1

    # 签到奖励
    base_reward = 1000
    streak_bonus = min(new_streak * 100, 1000)
    total_reward = base_reward + streak_bonus

    update_player(
        user.id,
        spirit_stones=player['spirit_stones'] + total_reward,
        last_sign_in_date=today.isoformat(),
        sign_in_streak=new_streak
    )

    await update.message.reply_text(
        f"✅ **签到成功！**\n\n"
        f"💎 获得灵石: {total_reward}\n"
        f"   • 基础俸禄: {base_reward}\n"
        f"   • 连续{new_streak}日: +{streak_bonus}\n\n"
        f"当前灵石: {player['spirit_stones'] + total_reward:,}",
        parse_mode="Markdown"
    )


# ============================
# /修仙帮助 - 帮助信息
# ============================

async def xiuxian_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """帮助信息"""
    help_text = f"""
🎮 **修仙世界 - 命令帮助**

📋 **基础命令**:
/{CMD_START} - 灵根测试（创建角色）
/{CMD_STATUS} - 查看个人状态
/{CMD_SIGN} - 每日签到
/{CMD_HELP} - 修仙帮助

🧘 **修炼系统**:
/{CMD_CULTIVATE} - 闭关修炼
/{CMD_FINISH} - 出关
/{CMD_BREAKTHROUGH} - 渡劫突破

⚔️ **战斗系统**:
/{CMD_BATTLE} - 外出历练
/{CMD_PVP} @道友 - 切磋比试

🎒 **物品系统**:
/{CMD_BAG} - 查看储物袋
/{CMD_USE} [物品] - 使用物品

🏪 **坊市系统**:
/{CMD_SHOP} - 进入坊市
/{CMD_BUY} [物品] - 购买物品

💱 **积分兑换**:
/{CMD_EXCHANGE} - PMS积分兑换灵石

💡 **提示**: 点击菜单按钮也可快速操作！
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")


# ============================
# 回调查询路由
# ============================

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """回调查询路由"""
    query = update.callback_query
    data = query.data

    handlers = {
        "xiuxian_status": xiuxian_status,
        "xiuxian_cultivate_menu": cultivate_menu,
        "xiuxian_cultivate_2": start_cultivate,
        "xiuxian_cultivate_4": start_cultivate,
        "xiuxian_cultivate_8": start_cultivate,
        "xiuxian_cultivate_12": start_cultivate,
        "xiuxian_finish_cultivate": finish_cultivate,
        "xiuxian_breakthrough": breakthrough,
        "xiuxian_battle_menu": battle_menu,
        "xiuxian_battle_wild": battle_wild,
    }

    handler = handlers.get(data)
    if handler:
        await handler(update, context)
    else:
        await query.answer("功能开发中...")


# ============================
# Handler注册（用于main.py）
# 使用中文命令
# ============================

# 基础命令
xiuxian_start_handler = CommandHandler(CMD_START, xiuxian_start)
xiuxian_status_handler = CommandHandler(CMD_STATUS, xiuxian_status)
xiuxian_sign_handler = CommandHandler(CMD_SIGN, daily_sign)
xiuxian_help_handler = CommandHandler(CMD_HELP, xiuxian_help)

# 修炼命令
xiuxian_cultivate_handler = CommandHandler(CMD_CULTIVATE, cultivate_menu)
xiuxian_finish_handler = CommandHandler(CMD_FINISH, finish_cultivate)
xiuxian_breakthrough_handler = CommandHandler(CMD_BREAKTHROUGH, breakthrough)

# 战斗命令
xiuxian_battle_handler = CommandHandler(CMD_BATTLE, battle_menu)

# 回调查询handler
xiuxian_callback_handler = CallbackQueryHandler(callback_router, pattern="^xiuxian_")


# ============================
# 命令列表导出（方便其他模块使用）
# ============================
XIUXIAN_COMMANDS = {
    "基础": [
        (CMD_START, "灵根测试（创建角色）"),
        (CMD_STATUS, "查看个人状态"),
        (CMD_SIGN, "每日签到"),
        (CMD_HELP, "修仙帮助"),
    ],
    "修炼": [
        (CMD_CULTIVATE, "闭关修炼"),
        (CMD_FINISH, "出关"),
        (CMD_BREAKTHROUGH, "渡劫突破"),
    ],
    "战斗": [
        (CMD_BATTLE, "外出历练"),
        (CMD_PVP, "切磋比试"),
    ],
    "物品": [
        (CMD_BAG, "查看储物袋"),
        (CMD_USE, "使用物品"),
    ],
    "坊市": [
        (CMD_SHOP, "进入坊市"),
        (CMD_BUY, "购买物品"),
    ],
    "兑换": [
        (CMD_EXCHANGE, "PMS积分兑换灵石"),
    ],
}
